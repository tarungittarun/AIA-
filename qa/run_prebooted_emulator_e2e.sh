#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

APK_PATH="${APK_PATH:?APK_PATH must point to the verified MySpace APK}"
TARGET_PACKAGE="${TARGET_PACKAGE:-app.space.one}"
CALCULATOR_CASES="${CALCULATOR_CASES:-}"
SHARD="${SHARD:-local}"
REPORT_ROOT="${REPORT_ROOT:-reports/e2e/guide-shard-${SHARD}}"
SERIAL="${ANDROID_SERIAL:-emulator-5554}"

if [[ ! -f "$APK_PATH" ]]; then
  echo "MySpace APK not found: $APK_PATH" >&2
  exit 2
fi

export ANDROID_SERIAL="$SERIAL"
adb wait-for-device
for attempt in $(seq 1 180); do
  if [[ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" == "1" ]]; then
    break
  fi
  if [[ "$attempt" -eq 180 ]]; then
    echo "Emulator did not finish booting within 6 minutes" >&2
    exit 2
  fi
  sleep 2
done

run_suite() {
  local label="$1"
  local apk="$2"
  local package="$3"
  local cases="$4"
  local report_dir="$5"
  local -a args=(
    python3 -u qa/calculator_e2e.py
    --apk "$apk"
    --package "$package"
    --report-dir "$report_dir"
  )
  if [[ -n "$cases" ]]; then
    args+=(--cases "$cases")
  fi
  echo "=== Running $label ($package), cases: ${cases:-all} ==="
  printf '::notice title=%s test selection::package=%s; cases=%s\n' \
    "$label" "$package" "${cases:-all}"
  "${args[@]}"
}

mkdir -p "$REPORT_ROOT"
myspace_status=0
if run_suite "MySpace v3.12.24-61" "$APK_PATH" "$TARGET_PACKAGE" \
  "$CALCULATOR_CASES" "$REPORT_ROOT/myspace"; then
  myspace_status=0
else
  myspace_status=$?
fi

mycalc_status=0
if [[ -n "${EXTRA_CALCULATOR_CASES:-}" ]]; then
  EXTRA_PACKAGE="${EXTRA_PACKAGE:-app.space.calc}"
  EXTRA_APK_PATH="${EXTRA_APK_PATH:?EXTRA_APK_PATH must point to the standalone MyCalc APK}"
  if [[ ! -f "$EXTRA_APK_PATH" ]]; then
    echo "Standalone MyCalc APK not found: $EXTRA_APK_PATH" >&2
    mycalc_status=2
  else
    if run_suite "Standalone MyCalc" "$EXTRA_APK_PATH" "$EXTRA_PACKAGE" \
      "${EXTRA_CALCULATOR_CASES:-}" "$REPORT_ROOT/mycalc"; then
      mycalc_status=0
    else
      mycalc_status=$?
    fi
  fi
fi

printf 'MySpace suite exit: %s\nStandalone MyCalc suite exit: %s\n' \
  "$myspace_status" "$mycalc_status"
if (( myspace_status != 0 || mycalc_status != 0 )); then
  exit 1
fi
