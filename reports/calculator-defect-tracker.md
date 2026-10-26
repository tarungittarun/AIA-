# MySpace Calculator — Defect Tracker & E2E QA Report

**Report ID:** `CALC-QA-2026-10-26-01`
**Prepared:** 26 October 2026 (Asia/Kolkata)
**Status:** Preliminary — no calculator test cases executed; API 34 boot and exact-APK installation now succeed, but UIAutomator hierarchy acquisition was killed with exit 137 before navigation; memory, compressed-dump, and screenshot/OCR fallbacks are being added
**Scope:** Calculator feature only. Other MySpace/TicTic features are explicitly out of scope.

## 1. Executive summary

The supplied APK was identified and pinned by immutable Git blob and SHA-256. The linked TicTic source branch's latest Android CI run passed its source-contract, Gradle unit-test/build, and lint jobs, but did **not** launch an emulator or exercise calculator UI flows. Sixteen Actions attempts in this QA branch still have no calculator test result: eight emulator setup/boot failures, five PackageManager/APK-install failures, one APK retrieval failure, one Monkey launch timeout, and one UIAutomator failure. Earlier run details are listed under QA-003. Most recently, [run 40227928023](https://github.com/tarungittarun/AIA-/actions/runs/40227928023) booted an API 34 x86_64 emulator, PackageManager responded on the first probe, and the exact APK installed successfully. The next `uiautomator dump` process exited 137 before navigation or any test case; the cause is not confirmed. No calculator functional result or live Google-app comparison is claimed.

Static review of the calculator's result-to-expression path identified two source-confirmed risks: a rounded display result may be reused during chained arithmetic, and scientific-notation output may not be accepted as a subsequent operand. These are **not yet device-confirmed defects**. The workflow now gets past emulator boot and APK installation on API 34. The next attempt keeps that working setup, raises guest RAM to 3 GiB, reduces the display to 720×1280, requests compressed/cached hierarchy dumps, and installs a screenshot OCR fallback. If UIAutomator is killed again, the harness will gather activity/memory/logcat diagnostics and attempt visual OCR with coordinate-derived keypad taps. No calculator test or Google comparison has run yet.

A live side-by-side comparison with the official Google Calculator is **not yet established**. The public emulator image may not include `com.google.android.calculator`; the workflow checks for that exact package and records `BLOCKED` if it is absent. No third-party Google Calculator APK mirror is used. Expected arithmetic values are useful functional oracles, but they are not represented here as a live Google-app comparison.

**Release / parity recommendation:** Do not claim calculator E2E or Google Calculator parity until the emulator workflow has run and the reference-app status is resolved. Re-test both open findings on-device; fix or explicitly accept them before release.

## 2. Artifact and test basis

| Field | Value |
|---|---|
| APK | `MySpace-v3.12.7-44-lite-dist.apk` |
| Supplied location | `tarungittarun/TicTic` → `artifacts/MySpace-v3.12.7-44-lite-dist.apk` |
| Source branch / commit inspected | `arena/3caca636-tictic` / `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9` |
| APK size | 2,076,884 bytes |
| Git blob SHA-1 | `944ac047b622521a6d751db673bcd8cf74c6965f` |
| APK SHA-256 | `ff52331518b71a153abf6ef76c964538044121230e1ae87d2855e535a94e0a23` |
| Package / launcher | `app.space.one` / `app.tictic.clock.MainActivity` |
| Source version metadata | `3.12.7` / version code `44` (from the inspected source configuration) |
| Calculator module | `feature-calculator` |
| Existing upstream Actions run | [Run 40201068395](https://github.com/tarungittarun/TicTic/actions/runs/40201068395) — success for commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9` |
| Existing calculator JVM tests | 25 `@Test` methods found in `CalculatorRulesTest.java`; latest upstream CI reports the unit-test/build job as successful |
| New runtime test workflow | `.github/workflows/calculator-apk-e2e.yml` in this QA branch |

The linked repository's `APPS.md` says the calculator was compared feature-by-feature with Google Calculator in v3.12.0. This is a repository statement, not an independently reproduced comparison of this v3.12.7 APK.

## 3. Defect tracker

### CALC-001 — Chained calculation may reuse rounded display value

| Field | Assessment |
|---|---|
| **Type** | Functional / numerical accuracy |
| **Severity / priority** | S2 — Major / P1 — High |
| **Status** | Open — source path confirms the risk; runtime confirmation pending |
| **Affected area** | Equals → operator continuation |
| **First observed** | Static review of source commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9` |

**Steps to reproduce**

1. Open Calculator and clear the expression.
2. Enter `1 ÷ 3`, then tap `=`.
3. Tap `×`, `3`, then `=`.

**Expected:** `1` (within the calculator's display precision).
**Actual:** Not yet measured on an emulator. The source path predicts `0.9999999999`: `1 / 3` is formatted to ten decimal places as `0.3333333333`, then that display string is stored back as the expression used by the next operation.

**Impact:** A normal equals-then-continue flow can propagate display rounding into subsequent calculations. This can produce visibly incorrect results in chained arithmetic, especially when users expect an exact integer or use the result as a later operand.

**Technical evidence:** `CalculatorRules.format()` rounds ordinary decimal output to ten places (`CalculatorRules.java`, lines 57–60). The equals handler formats the evaluated value, then sets `expression` to the formatted `result` (`CalculatorScreen.java`, lines 1228–1249). The `format()` comment says rounding is display-only, but the UI continuation path appears to reuse the rounded string.

**Suggested fix:** Keep the raw numeric result (or a suitable exact representation) separate from the formatted display string. On an operator after equals, seed the next expression from the raw value; continue using the formatted string only for display/history presentation. Add a regression test for `(1 ÷ 3) × 3` through the equals-continuation path, not only as one complete expression.

**Workaround:** Enter the complete expression `1 ÷ 3 × 3` before pressing equals; this avoids the intermediate display-format round trip.

**Comment log**

- **2026-10-25 — QA:** Static path review identifies the defect mechanism. The predicted output has not been observed on-device; the new emulator test `TC-CALC-008` is intended to confirm or reject it.

### CALC-002 — Scientific-notation result may not be reusable as an operand

| Field | Assessment |
|---|---|
| **Type** | Functional / expression parsing |
| **Severity / priority** | S2 — Major / P2 — Normal |
| **Status** | Open — parser/input path confirms the risk; runtime confirmation pending |
| **Affected area** | Chaining after very large or very small results |
| **First observed** | Static review of source commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9` |

**Steps to reproduce**

1. Open the scientific keypad and enter `10 ^ 15`, then tap `=`. The formatter is expected to display `1e+15`.
2. Continue with `+ 1`, then tap `=`.

**Expected:** The displayed result remains a valid operand and the next expression evaluates.
**Actual:** Not yet measured on an emulator. Static review predicts the exponent-formatted expression is rejected, remains unchanged, or evaluates as `Error` when continued.

**Impact:** Users may be unable to continue calculations after a result crosses the formatter's scientific-notation threshold (absolute value ≥ `1e15` or < `1e-9`).

**Technical evidence:** `CalculatorRules.format()` emits `e` notation at those thresholds (`CalculatorRules.java`, lines 48–55). `parseNumber()` accepts digits and a decimal point only (`CalculatorRules.java`, lines 455–469); it does not parse exponent notation. The input validator's handling of `e` as Euler's constant does not make a formatted `1e+15` number literal valid.

**Suggested fix:** Prefer the raw-result continuation fix in CALC-001. If displayed scientific strings are intentionally parsed, implement a numeric exponent token such as `1e+15` without conflating it with the standalone Euler constant, and add parser, input-validation, and UI-chain regression tests for both exponent signs and small magnitudes.

**Workaround:** Re-enter the full expression without using the formatted result as an operand.

**Comment log**

- **2026-10-25 — QA:** Parser/formatter mismatch is visible in source. Device-level behavior remains unconfirmed; `TC-CALC-009` exercises the threshold and continuation.

## 4. QA / environment tracking (not product defects)

### QA-001 — Official Google Calculator live comparator availability

| Field | Assessment |
|---|---|
| **Type** | Test environment blocker |
| **Status** | Open / not assessed — API 34 APK installation succeeded, but UI inspection failed before the Google-package scan |
| **Product defect?** | No — this records a limitation of the comparison environment, not a MySpace app bug |

The official package `com.google.android.calculator` was not available in the local sandbox, and no official Google Calculator APK was obtained. The emulator workflow checks the exact package at runtime. If it is absent, it records the live comparison as `BLOCKED` while still running deterministic arithmetic/UI checks against expected values. The old AOSP calculator is not treated as equivalent to the current official Google Calculator.

**Comment log**

- **2026-10-25 — QA:** The official Play listing and product description were reviewed, but no live interaction was performed. Any future comparison must identify the actual reference package/version and distinguish it from mathematical expected-value checks.

### QA-002 — Upstream CI did not cover runtime calculator UI

| Field | Assessment |
|---|---|
| **Type** | Test coverage gap |
| **Status** | Mitigation added; sixteen Actions attempts still have no calculator results. Latest API 34 run booted and installed the APK, but UIAutomator exited 137 before tests; compressed/cached hierarchy and screenshot/OCR fallback are next |
| **Product defect?** | No — infrastructure finding |

The linked branch's latest CI run passed its build/test checks but does not install the release APK in an emulator or exercise calculator UI. This branch adds a separate Android Emulator Actions workflow. It pins the supplied APK by blob and SHA-256, tests calculator flows only, and uploads a Markdown/JSON run report plus screenshots and hierarchy/OCR evidence for 30 days. Eight emulator setup attempts failed before APK installation; one APK retrieval attempt failed with curl exit code 56; five Android 11 PackageManager/APK installs failed; and one software-emulator app launch timed out. Run `40227928023` is the first to boot API 34 and install the exact APK successfully, but its uncompressed UIAutomator dump exited 137. The current retry stays on Ubuntu/API 34 x86_64, increases emulator RAM, reduces display resolution, compresses/caches UI reads, and adds screenshot/OCR plus dumpsys/logcat fallback. The app scope remains calculator-only.

### QA-003 — Actions emulator boot, installation, and app-launch failures

| Field | Assessment |
|---|---|
| **Type** | Test infrastructure / emulator reliability |
| **Status** | Open — latest API 34 run booted and installed the exact APK; UIAutomator hierarchy dump exited 137 before navigation; alternate inspection retry queued |
| **Runs / jobs** | [40204124011](https://github.com/tarungittarun/AIA-/actions/runs/40204124011), job `121201302193`; [40205135030](https://github.com/tarungittarun/AIA-/actions/runs/40205135030), job `121204338761`; [40206626414](https://github.com/tarungittarun/AIA-/actions/runs/40206626414), job `121208834615`; [40208505722](https://github.com/tarungittarun/AIA-/actions/runs/40208505722), job `121214502041`; [40208720426](https://github.com/tarungittarun/AIA-/actions/runs/40208720426), job `121215155606`; [40210565671](https://github.com/tarungittarun/AIA-/actions/runs/40210565671), job `121220690836`; [40211691552](https://github.com/tarungittarun/AIA-/actions/runs/40211691552), job `121224080079`; [40212729874](https://github.com/tarungittarun/AIA-/actions/runs/40212729874), job `121227260260`; [40214057816](https://github.com/tarungittarun/AIA-/actions/runs/40214057816), job `121231253984`; [40215666672](https://github.com/tarungittarun/AIA-/actions/runs/40215666672), job `121236137329`; [40217050828](https://github.com/tarungittarun/AIA-/actions/runs/40217050828), job `121240351784`; [40224996344](https://github.com/tarungittarun/AIA-/actions/runs/40224996344), job `121264373229`; [40225466586](https://github.com/tarungittarun/AIA-/actions/runs/40225466586), job `121265778684`; [40225896707](https://github.com/tarungittarun/AIA-/actions/runs/40225896707), job `121267068146`; [40226376668](https://github.com/tarungittarun/AIA-/actions/runs/40226376668), job `121268512489`; [40227928023](https://github.com/tarungittarun/AIA-/actions/runs/40227928023), job `121273214403` |
| **Product defect?** | No — no calculator test case ran |

**Observed:** Eight emulator attempts failed before installation; one separate APK retrieval attempt failed with curl exit code 56. Five Android 11 runs failed at PackageManager/APK installation; one run installed but Monkey timed out. Three macOS/ARM64 attempts failed before boot with `HVF error: HV_UNSUPPORTED`. Run `40226376668` booted API 30 but both installs failed with `StorageManagerService.allocateBytes` / `PackageManagerInternal.freeStorage` null. Latest run `40227928023` booted API 34 x86_64 using software acceleration, received a PackageManager response after one readiness probe, and installed the exact checksum-verified APK. The first UI hierarchy request, `adb shell uiautomator dump /sdcard/window.xml`, exited 137. This confirms only that the process was killed; the cause is unknown (memory pressure is a hypothesis, not an established diagnosis). No app screen, calculator test case, or Google-package scan ran.

**Action:** Preserve the API 34 Ubuntu setup that successfully booted and installed the APK. The next attempt increases AVD RAM to 3 GiB, reduces the virtual display to 720×1280, uses `uiautomator dump --compressed`, caches each UI tree per screen state, and falls back to screenshot/Tesseract OCR with keypad-coordinate inference if both hierarchy methods fail. On UIAutomator failure it also saves a screenshot, activity state, guest/system-server memory details, and recent logcat. Direct Google comparison remains unassessed until UI navigation and test execution begin.

**Comment log**

- **2026-10-25 — QA:** Ten Actions attempts had produced no calculator test-case result; the latest at that point installed the APK but Monkey timed out before a calculator screen was confirmed.
- **2026-10-26 — QA:** Run `40217050828` failed before app launch with a StorageManager/PackageManager NPE. No app-level pass/fail should be inferred; the next attempt moved to macOS ARM64.
- **2026-10-26 — QA:** Runs `40224996344`, `40225466586`, and `40225896707` failed before Android boot because HVF returned `HV_UNSUPPORTED`, even with `-accel off`.
- **2026-10-26 — QA:** Run `40226376668` booted API 30; PackageManager answered after 27 probes, but installation failed twice with a `StorageManagerService.allocateBytes` null `PackageManagerInternal`. No calculator test case or Google comparison ran. The next run changes the emulator image to API 34.
- **2026-10-26 — QA:** Run `40227928023` booted API 34; PackageManager answered after one probe and the exact APK installed. The initial UIAutomator dump exited 137 before UI navigation. Cause is unconfirmed. Next attempt adds a 3 GiB guest, lower resolution, compressed/cached hierarchy, screenshot/dumpsys/logcat diagnostics, and a Tesseract OCR/coordinate fallback.

## 5. Functional test matrix

The harness is `qa/calculator_e2e.py`. Each device test is written to the workflow's generated run report. No calculator test case ran in any of the sixteen completed attempts (`40204124011`, `40205135030`, `40206626414`, `40208505722`, `40208720426`, `40210565671`, `40211691552`, `40212729874`, `40214057816`, `40215666672`, `40217050828`, `40224996344`, `40225466586`, `40225896707`, `40226376668`, and `40227928023`). The latest run booted API 34 and installed the APK, then stopped at UI hierarchy acquisition (exit 137), before the calculator screen or Google package scan. The next attempt includes compressed/cached UIAutomator and screenshot/OCR fallback. A Google reference `BLOCKED` result is not counted as a MySpace functional pass.

| Test ID | Scenario | Expected result | Current status |
|---|---|---|---|
| TC-CALC-001 | Operator precedence: `2 + 3 × 4` | `14` | Not run — run `40227928023` installed the APK on API 34 but its UIAutomator dump exited 137 before navigation; compressed/cached hierarchy and screenshot OCR fallback are next (see QA-003) |
| TC-CALC-002 | Parentheses: `(2 + 3) × 4` | `20` | Not run — run `40227928023` installed the APK on API 34 but its UIAutomator dump exited 137 before navigation; compressed/cached hierarchy and screenshot OCR fallback are next (see QA-003) |
| TC-CALC-003 | Decimal addition: `0.1 + 0.2` | `0.3` | Not run — run `40227928023` installed the APK on API 34 but its UIAutomator dump exited 137 before navigation; compressed/cached hierarchy and screenshot OCR fallback are next (see QA-003) |
| TC-CALC-004 | Contextual percentage: `200 + 10%` | `220` | Not run — run `40227928023` installed the APK on API 34 but its UIAutomator dump exited 137 before navigation; compressed/cached hierarchy and screenshot OCR fallback are next (see QA-003) |
| TC-CALC-005 | Scientific square root: `√(9)` | `3` | Not run — run `40227928023` installed the APK on API 34 but its UIAutomator dump exited 137 before navigation; compressed/cached hierarchy and screenshot OCR fallback are next (see QA-003) |
| TC-CALC-006 | Degree-mode sine: `sin(30)` | `0.5` | Not run — run `40227928023` installed the APK on API 34 but its UIAutomator dump exited 137 before navigation; compressed/cached hierarchy and screenshot OCR fallback are next (see QA-003) |
| TC-CALC-007 | History persists after process restart and restores an entry | `1+1` and `2` visible/selectable | Not run — run `40227928023` installed the APK on API 34 but its UIAutomator dump exited 137 before navigation; compressed/cached hierarchy and screenshot OCR fallback are next (see QA-003) |
| TC-CALC-008 | Chaining: `1 ÷ 3 = × 3 =` | `1` | Not run — run `40227928023` installed the APK on API 34 but its UIAutomator dump exited 137 before navigation; compressed/cached hierarchy and screenshot OCR fallback are next (see QA-003); linked to CALC-001 |
| TC-CALC-009 | Scientific result continuation: `10^15 = + 1 =` | Continues without parser/validator error | Not run — run `40227928023` installed the APK on API 34 but its UIAutomator dump exited 137 before navigation; compressed/cached hierarchy and screenshot OCR fallback are next (see QA-003); linked to CALC-002 |
| TC-CALC-010 | Live official Google Calculator comparison | Common precedence case run in `com.google.android.calculator` | Not run — run `40227928023` installed the APK on API 34 but its UIAutomator dump exited 137 before navigation; compressed/cached hierarchy and screenshot OCR fallback are next (see QA-003); may be blocked |

The workflow saves screenshots plus UI hierarchy or synthetic OCR evidence under the artifact's `evidence/` directory. On a UIAutomator failure it also captures device activity, memory, and recent logcat diagnostics. The workflow fails on MySpace functional `FAIL`/`ERROR` results; blocked Google-reference availability is separately reported.

## 6. CI evidence and limitations

- **Existing upstream result:** [TicTic Android CI run 40201068395](https://github.com/tarungittarun/TicTic/actions/runs/40201068395), commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`, concluded success. Its source-contract and Android build/unit-test steps are evidence of source-level CI health only, not APK runtime behavior.
- **New workflow:** `.github/workflows/calculator-apk-e2e.yml` checks out TicTic at pinned commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9` with a sparse checkout for the exact APK, verifies SHA-256 and ZIP integrity, then runs the calculator-only harness on `ubuntu-24.04` using an API 34 `google_apis;x86_64` emulator. Eight emulator setup attempts, five PackageManager/APK-install failures, one Monkey app-launch timeout, and one APK retrieval failure have been superseded by a run that boots API 34 and installs the APK. That run stopped at UIAutomator exit 137 before tests; a compressed/cached hierarchy and screenshot/OCR retry is now configured. No calculator test case has run yet.
- **Local execution limitation:** The review sandbox did not have Android SDK/ADB/emulator tooling or KVM, so no local device E2E was possible. GitHub Actions is the execution target.
- **Google comparator limitation:** An API 34 `google_apis` system image is requested (without the Play Store), so Google Calculator availability is not assumed. The workflow checks for the exact `com.google.android.calculator` package and will not silently substitute a non-Google app.
- **No false pass claim:** This report separates static analysis, expected-value assertions, actual emulator results, and live Google comparison. Only the latter two can establish runtime observations.

## 7. References

1. [Official Google Calculator Play listing](https://play.google.com/store/apps/details?id=com.google.android.calculator&hl=en) — feature reference only; not a live comparison in this report.
2. TicTic calculator implementation and tests at source commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`: `feature-calculator/src/main/java/app/space/feature/calculator/CalculatorRules.java`, `CalculatorScreen.java`, and `feature-calculator/src/test/java/app/space/feature/calculator/CalculatorRulesTest.java`.
3. TicTic app inventory note `APPS.md` — reports a prior v3.12.0 feature comparison; not independently reproduced here.
