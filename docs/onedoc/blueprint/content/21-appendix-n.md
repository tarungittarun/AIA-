# Appendix N — Executor quick-start and runbooks

## N.1 Environment bootstrap (run verbatim)

```bash
# JDK
sudo apt-get update && sudo apt-get install -y openjdk-17-jdk
java -version   # expect 17.x

# Android SDK (cmdline-tools path)
mkdir -p $HOME/android-sdk/cmdline-tools
curl -o cmdtools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q cmdtools.zip -d $HOME/android-sdk/cmdline-tools && mv $HOME/android-sdk/cmdline-tools/cmdline-tools $HOME/android-sdk/cmdline-tools/latest
export ANDROID_HOME=$HOME/android-sdk && export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator

# Packages (pins per Appendix E)
yes | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-36" "build-tools;36.0.0" \
  "emulator" "system-images;android-26;google_apis;x86_64" \
  "system-images;android-33;google_apis;x86_64" \
  "system-images;android-35;google_apis;x86_64" \
  "system-images;android-36;google_apis;x86_64"
```

## N.2 AVD creation (§23.1, verbatim)

```bash
echo no | avdmanager create avd -n od-api26 -k "system-images;android-26;google_apis;x86_64" -d pixel_2 --force
echo no | avdmanager create avd -n od-api33 -k "system-images;android-33;google_apis;x86_64" -d pixel_4 --force
echo no | avdmanager create avd -n od-api35 -k "system-images;android-35;google_apis;x86_64" -d pixel_6 --force
echo no | avdmanager create avd -n od-api36 -k "system-images;android-36;google_apis;x86_64" -d pixel_8 --force
# RAM profiles per tier: edit config.ini (hw.ramSize=2048|3072|4096|8192)
```

## N.3 Emulator boot + clean state

```bash
emulator -avd od-api33 -no-window -no-audio -gpu swiftshader_indirect -no-snapshot-load -port 5554 &
adb wait-for-device
adb shell 'while [[ -z $(getprop sys.boot_completed) ]]; do sleep 1; done'
# golden boot snapshot (boot speed only; app data ALWAYS cleared per run):
adb -s od-api33 emu snapshot save golden-boot 2>/dev/null || true
```

Rule: every QA run starts `adb uninstall app.onedoc || true` — no run ever sees a previous run's data (§23.3).

## N.4 Build + install + drive (the direct-APK loop)

```bash
./gradlew :app:assembleFullRelease            # release APK (RC keystore per §26.1)
APK=app/build/outputs/apk/full/release/app-full-release.apk
sha256sum $APK | tee artifacts/apk-sha.txt
apkanalyzer manifest permissions $APK > artifacts/manifest-permissions.txt   # gate: == §20.5
adb install -r $APK
# drive via instrumentation QA apk (same run id, separate module :qa-driver):
adb shell am instrument -w -e case TC-J1,TC-J5,TC-STATE-005 \
  app.onedoc.test/androidx.test.runner.AndroidJUnitRunner | tee artifacts/instr.log
# artifacts: screenshots per case at /sdcard/onedoc-qa/<case>/ pulled to artifacts/
adb pull /sdcard/onedoc-qa artifacts/screens
```

## N.5 Release runbook (G8, ordered)

1. Verify G7 evidence is green for the EXACT release SHA (re-tag build if not).
2. `./gradlew :app:assembleFullRelease :app:bundleFullRelease` with release keystore (owner-provided) or RC keystore per §26.1.
3. Static gates: manifest, deny-list, size ≤ 25 MB, SBOM generation.
4. Direct-APK QA on the release build (full catalogue + journeys) → evidence PDF.
5. Defect tracker final pass; release notes per Appendix M; handoff note per §28.4.
6. `provenance.json` per §28.2; tag `v<X.Y.Z>`; GitHub Release with APK + PDF attached.
7. Re-sign runbook (if owner keystore arrives late): build RC-signed now; when keystore arrives, rebuild same commit with release key, re-run the static gates + smoke (not the full matrix — same bytes logic), update provenance; never patch a signed APK binary.

## N.6 The nightly all-green ritual

Nightly pipeline = full matrix + 50k-case properties + IME fuzzer + drift checks (Figma registry if token provided, tokens lint, dependency audit). Morning rule: a red nightly is the first task of the day — before any feature work (§29.4 blockage discipline). The ritual is the reason G7 surprises don't exist.
