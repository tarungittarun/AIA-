#!/usr/bin/env bash
# Provision and boot a single Android emulator, then run the calculator-only UI suite.
# A custom launcher keeps boot diagnostics available even if Android never becomes ready.
set -Eeuo pipefail

ROOT="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/.." && pwd)}"
REPORT_DIR="$ROOT/reports/e2e"
mkdir -p "$REPORT_DIR/evidence"
: > "$REPORT_DIR/emulator.log"
: > "$REPORT_DIR/boot-status.log"

SDK_ROOT="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
if [[ -z "$SDK_ROOT" ]]; then
  echo "ANDROID_HOME/ANDROID_SDK_ROOT is not set" | tee -a "$REPORT_DIR/boot-status.log"
  exit 2
fi

AVD_NAME="calculator-qa"
SERIAL="emulator-5554"
IMAGE="system-images;android-30;google_apis;x86_64"
EMULATOR_LOG="$REPORT_DIR/emulator.log"
BOOT_LOG="$REPORT_DIR/boot-status.log"
APK_PATH="${APK_PATH:?APK_PATH was not exported by the verification step}"

fail_with_diagnostics() {
  local reason="$1"
  {
    echo "Failure: $reason"
    echo "Runner: $(uname -a)"
    echo "ANDROID_HOME=$SDK_ROOT"
    echo "KVM: $(if [[ -r /dev/kvm && -w /dev/kvm ]]; then echo available; else echo unavailable; fi)"
    echo "ADB devices:"
    adb devices -l 2>&1 || true
    echo "Emulator state:"
    adb -s "$SERIAL" get-state 2>&1 || true
    echo "sys.boot_completed:"
    timeout 15 adb -s "$SERIAL" shell getprop sys.boot_completed 2>&1 || true
    echo "init.svc.bootanim:"
    timeout 15 adb -s "$SERIAL" shell getprop init.svc.bootanim 2>&1 || true
    echo "Recent emulator output:"
    tail -n 60 "$EMULATOR_LOG" 2>/dev/null || true
    echo "Recent PackageManager probe:"
    tail -n 20 "$REPORT_DIR/package-manager-probe.log" 2>/dev/null || true
  } >> "$BOOT_LOG"
  local one_line
  one_line="$(tail -n 25 "$BOOT_LOG" | tr '\n' ' ' | sed 's/%/%25/g; s/\r/%0D/g; s/::/%3A%3A/g')"
  printf '::error title=Android emulator setup::%s\n' "$one_line"
  echo "Emulator setup failed; diagnostic files are under reports/e2e/."
  exit 1
}

# The setup action accepts SDK licenses and adds sdkmanager/avdmanager to PATH.
# Install only the API 30 image and emulator binary needed for this APK's minSdk 26.
{
  echo "Installing emulator and $IMAGE"
  sdkmanager --install emulator platform-tools platforms\;android-30 "$IMAGE"
} 2>&1 | tee "$REPORT_DIR/sdkmanager.log"

export ANDROID_AVD_HOME="${ANDROID_AVD_HOME:-$HOME/.android/avd}"
mkdir -p "$ANDROID_AVD_HOME"
printf 'no\n' | avdmanager create avd --force --name "$AVD_NAME" --package "$IMAGE" --device pixel_2 \
  2>&1 | tee "$REPORT_DIR/avdmanager.log"

EMULATOR_BIN="$SDK_ROOT/emulator/emulator"
if [[ ! -x "$EMULATOR_BIN" ]]; then
  echo "Emulator executable not found at $EMULATOR_BIN" | tee -a "$BOOT_LOG"
  exit 2
fi

emulator_args=(-avd "$AVD_NAME" -port 5554 -no-window -no-audio -no-boot-anim -no-snapshot -gpu swiftshader_indirect)
if [[ ! -r /dev/kvm || ! -w /dev/kvm ]]; then
  emulator_args+=(-accel off)
fi
printf 'Launching: %q ' "$EMULATOR_BIN" "${emulator_args[@]}" | tee -a "$BOOT_LOG"
echo | tee -a "$BOOT_LOG"
"$EMULATOR_BIN" "${emulator_args[@]}" >"$EMULATOR_LOG" 2>&1 &
EMULATOR_PID=$!
printf '%s\n' "$EMULATOR_PID" > "$REPORT_DIR/emulator.pid"

cleanup() {
  local exit_code=$?
  set +e
  if adb -s "$SERIAL" get-state >/dev/null 2>&1; then
    adb -s "$SERIAL" emu kill >/dev/null 2>&1
  fi
  kill "$EMULATOR_PID" >/dev/null 2>&1
  wait "$EMULATOR_PID" >/dev/null 2>&1
  echo "Emulator cleanup completed (test-step exit=$exit_code)." >> "$BOOT_LOG"
  exit "$exit_code"
}
trap cleanup EXIT

adb start-server >> "$BOOT_LOG" 2>&1 || true
if ! timeout 180 adb -s "$SERIAL" wait-for-device >> "$BOOT_LOG" 2>&1; then
  fail_with_diagnostics "ADB did not see $SERIAL within 180 seconds"
fi

booted=false
for attempt in $(seq 1 300); do
  if ! kill -0 "$EMULATOR_PID" 2>/dev/null; then
    fail_with_diagnostics "Emulator process exited before Android boot completed"
  fi
  state="$(timeout 15 adb -s "$SERIAL" get-state 2>/dev/null || true)"
  boot="$(timeout 15 adb -s "$SERIAL" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)"
  printf '%s attempt=%s state=%s sys.boot_completed=%s\n' "$(date -u +%FT%TZ)" "$attempt" "$state" "$boot" >> "$BOOT_LOG"
  if [[ "$state" == "device" && "$boot" == "1" ]]; then
    booted=true
    break
  fi
  if (( attempt % 20 == 0 )); then
    echo "Still waiting for Android boot completion (attempt $attempt/300)."
  fi
  sleep 4
done

if [[ "$booted" != true ]]; then
  fail_with_diagnostics "Android API 30 did not finish booting within 20 minutes"
fi

# sys.boot_completed may be set before PackageManager publishes its binder service.
# Wait explicitly for it before adb install; this avoids the intermittent
# "cmd: Can't find service: package" failure seen on the first manual-boot run.
export ANDROID_SERIAL="$SERIAL"
package_manager_ready=false
for attempt in $(seq 1 90); do
  if timeout 8 adb -s "$SERIAL" shell cmd package list packages \
      > "$REPORT_DIR/package-manager-probe.log" 2>&1 \
      && ! grep -qi "can't find service: package" "$REPORT_DIR/package-manager-probe.log"; then
    package_manager_ready=true
    printf '%s package-manager-ready attempt=%s\n' "$(date -u +%FT%TZ)" "$attempt" >> "$BOOT_LOG"
    echo "::notice title=Android package manager ready::PackageManager responded after $attempt readiness probes."
    break
  fi
  printf '%s package-manager-not-ready attempt=%s\n' "$(date -u +%FT%TZ)" "$attempt" >> "$BOOT_LOG"
  sleep 5
done
if [[ "$package_manager_ready" != true ]]; then
  fail_with_diagnostics "Android booted but PackageManager did not become available within the readiness window"
fi

# Allow the framework and input service to settle after PackageManager is ready.
sleep 5
adb -s "$SERIAL" shell input keyevent 82 >> "$BOOT_LOG" 2>&1 || echo "Screen-unlock keyevent unavailable; continuing." >> "$BOOT_LOG"
adb -s "$SERIAL" shell settings put global window_animation_scale 0 >> "$BOOT_LOG" 2>&1 || true
adb -s "$SERIAL" shell settings put global transition_animation_scale 0 >> "$BOOT_LOG" 2>&1 || true
adb -s "$SERIAL" shell settings put global animator_duration_scale 0 >> "$BOOT_LOG" 2>&1 || true
printf '::notice title=Android emulator ready::API 30 x86_64 boot completed; running calculator-only UI tests.\n'

python3 -u "$ROOT/qa/calculator_e2e.py" \
  --apk "$APK_PATH" \
  --package app.space.one \
  --report-dir "$REPORT_DIR"
