# MySpace Calculator — Defect Tracker & E2E QA Report

**Report ID:** `CALC-QA-2026-10-26-01`
**Prepared:** 26 October 2026 (Asia/Kolkata)
**Status:** Preliminary — no calculator test cases executed; the latest Apple Silicon run failed before Android boot even with software acceleration; returning to the Linux x86_64 emulator path that previously installed the APK
**Scope:** Calculator feature only. Other MySpace/TicTic features are explicitly out of scope.

## 1. Executive summary

The supplied APK was identified and pinned by immutable Git blob and SHA-256. The linked TicTic source branch's latest Android CI run passed its source-contract, Gradle unit-test/build, and lint jobs. That run did **not** launch an emulator or exercise calculator UI flows. Fourteen Actions attempts in this QA branch have not executed calculator test cases. Earlier runs `40204124011`, `40205135030`, `40206626414`, `40208505722`, `40208720426`, and `40210565671` cover emulator boot/setup and one APK-retrieval failure. [Run 40211691552](https://github.com/tarungittarun/AIA-/actions/runs/40211691552) booted API 30 but PackageManager was unavailable at install time. [Run 40212729874](https://github.com/tarungittarun/AIA-/actions/runs/40212729874) timed out during streamed APK installation; [run 40214057816](https://github.com/tarungittarun/AIA-/actions/runs/40214057816) then failed with a PackageManager broken pipe. [Run 40215666672](https://github.com/tarungittarun/AIA-/actions/runs/40215666672) installed the exact APK but Monkey launch timed out under software acceleration. [Run 40217050828](https://github.com/tarungittarun/AIA-/actions/runs/40217050828) failed in Android 11's `StorageManagerService.allocateBytes`: `PackageManagerInternal.freeStorage(...)` was null during APK install. Three latest macOS runs, [40224996344](https://github.com/tarungittarun/AIA-/actions/runs/40224996344), [40225466586](https://github.com/tarungittarun/AIA-/actions/runs/40225466586), and [40225896707](https://github.com/tarungittarun/AIA-/actions/runs/40225896707), all failed before Android boot with `HVF error: HV_UNSUPPORTED`, including with `-accel auto` and `-accel off`. No calculator functional result or Google-app comparison is claimed. The next retry returns to the Ubuntu x86_64 software emulator, which at least booted and installed the APK in one prior run.

Static review of the calculator's result-to-expression path identified two reproducible-looking calculation risks: a rounded display result is reused during chained arithmetic, and a result rendered in scientific notation is not supported as a numeric literal by the input parser. These are **source-confirmed risks, not yet device-confirmed observations**. The workflow is configured to install the exact APK into a disposable Android emulator and exercise calculator flows only. The latest macOS attempt failed during emulator initialization, before APK installation or the Python harness. QEMU reported that Apple Hypervisor Framework acceleration was unsupported even when disabled explicitly. A prior Ubuntu x86_64 software-emulator run installed the APK but Monkey timed out; another hit a StorageManager/PackageManager NPE. No per-run calculator results or screenshots were generated. The next attempt returns to Ubuntu x86_64, which has progressed furthest in this workflow.

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
| **Status** | Open / not assessed — APK installation failed before the package scan |
| **Product defect?** | No — this records a limitation of the comparison environment, not a MySpace app bug |

The official package `com.google.android.calculator` was not available in the local sandbox, and no official Google Calculator APK was obtained. The emulator workflow checks the exact package at runtime. If it is absent, it records the live comparison as `BLOCKED` while still running deterministic arithmetic/UI checks against expected values. The old AOSP calculator is not treated as equivalent to the current official Google Calculator.

**Comment log**

- **2026-10-25 — QA:** The official Play listing and product description were reviewed, but no live interaction was performed. Any future comparison must identify the actual reference package/version and distinguish it from mathematical expected-value checks.

### QA-002 — Upstream CI did not cover runtime calculator UI

| Field | Assessment |
|---|---|
| **Type** | Test coverage gap |
| **Status** | Mitigation added; thirteen emulator attempts and one APK retrieval failure still have no calculator results; the latest Apple Silicon boot failed even with acceleration disabled; returning to Ubuntu x86_64 |
| **Product defect?** | No — infrastructure finding |

The linked branch's latest CI run passed its build/test checks but does not install the release APK in an emulator or exercise calculator UI. This branch adds a separate Android Emulator Actions workflow. It pins the supplied APK by blob and SHA-256, tests calculator flows only, and uploads a Markdown/JSON run report plus screenshots/UI dumps for 30 days. Eight emulator setup attempts failed before APK installation: two Ubuntu/API 34 attempts, five Apple Silicon attempts (API 34, API 30 action, and three manual HVF failures), and one Ubuntu/API 30 attempt that ended with ADB exit code 224. A separate APK retrieval attempt failed with curl exit code 56 before emulator startup. Four Ubuntu/software-emulator installs failed at PackageManager readiness, with a timeout, a `Broken pipe (32)`, or a `StorageManagerService` NPE; another installed the APK but Monkey timed out. The latest macOS runs failed before boot even when acceleration was disabled. The next run returns to `ubuntu-24.04` and the API 30 Google APIs x86_64 image that previously installed the APK; the bootstrap keeps its portable Python timeout wrapper and the harness retains install retry/logcat capture plus extended Monkey handling.

### QA-003 — Actions emulator boot, installation, and app-launch failures

| Field | Assessment |
|---|---|
| **Type** | Test infrastructure / emulator reliability |
| **Status** | Open — latest macOS run failed during HVF initialization even with acceleration off; retrying Ubuntu x86_64 |
| **Runs / jobs** | [40204124011](https://github.com/tarungittarun/AIA-/actions/runs/40204124011), job `121201302193`; [40205135030](https://github.com/tarungittarun/AIA-/actions/runs/40205135030), job `121204338761`; [40206626414](https://github.com/tarungittarun/AIA-/actions/runs/40206626414), job `121208834615`; [40208505722](https://github.com/tarungittarun/AIA-/actions/runs/40208505722), job `121214502041`; [40208720426](https://github.com/tarungittarun/AIA-/actions/runs/40208720426), job `121215155606`; [40210565671](https://github.com/tarungittarun/AIA-/actions/runs/40210565671), job `121220690836`; [40211691552](https://github.com/tarungittarun/AIA-/actions/runs/40211691552), job `121224080079`; [40212729874](https://github.com/tarungittarun/AIA-/actions/runs/40212729874), job `121227260260`; [40214057816](https://github.com/tarungittarun/AIA-/actions/runs/40214057816), job `121231253984`; [40215666672](https://github.com/tarungittarun/AIA-/actions/runs/40215666672), job `121236137329`; [40217050828](https://github.com/tarungittarun/AIA-/actions/runs/40217050828), job `121240351784`; [40224996344](https://github.com/tarungittarun/AIA-/actions/runs/40224996344), job `121264373229`; [40225466586](https://github.com/tarungittarun/AIA-/actions/runs/40225466586), job `121265778684`; [40225896707](https://github.com/tarungittarun/AIA-/actions/runs/40225896707), job `121267068146` |
| **Product defect?** | No — no calculator test case ran |

**Observed:** Five earlier emulator attempts failed before APK installation. The first Ubuntu/API 34 run and both Apple Silicon boot attempts (API 34 and API 30) timed out; the second Ubuntu/API 34 run ended with shell exit code 2; the Ubuntu/API 30 action run ended with ADB exit code 224. A separate attempt failed before emulator startup while retrieving the APK (`curl` exit code 56). Run `40211691552` booted API 30 but PackageManager was unavailable at install time. Run `40212729874` reported PackageManager readiness after 26 probes, but streamed install timed out after 180 seconds. Run `40214057816` pushed the APK but PackageManager returned `Broken pipe (32)`. Run `40215666672` installed the APK, but Monkey timed out after 30 seconds on an Ubuntu runner with KVM unavailable. Run `40217050828` failed both install attempts with a Java `NullPointerException` in `StorageManagerService.allocateBytes` while calling `PackageManagerInternal.freeStorage`. Runs `40224996344`, `40225466586`, and `40225896707` all failed before boot: QEMU reported `HVF error: HV_UNSUPPORTED` and exited with code 1, including with `-accel auto` and `-accel off`. Exact APK checkout and SHA-256 verification succeeded in all eight custom-emulator runs that reached artifact verification. No calculator screen or Google-package scan ran.

**Action:** The Ubuntu x86_64 software emulator reached APK installation in one run and app-launch submission in another, but also showed intermittent PackageManager and StorageManager failures. Manual macOS/ARM64 attempts cannot initialize because the hosted runner does not support HVF, even with acceleration disabled. The next run returns to `ubuntu-24.04` and API 30 `google_apis;x86_64`. The bootstrap retains its portable timeout wrapper; the harness retains PackageManager readiness, one install retry with diagnostics, and extended Monkey handling. Direct Google comparison remains blocked until the calculator UI is reached and test execution begins.

**Comment log**

- **2026-10-25 — QA:** Ten Actions attempts had produced no calculator test-case result; the latest at that point installed the APK but Monkey timed out before a calculator screen was confirmed.
- **2026-10-26 — QA:** Run `40217050828` failed before app launch with a StorageManager/PackageManager NPE. No app-level pass/fail should be inferred; the next attempt moved to macOS ARM64.
- **2026-10-26 — QA:** Runs `40224996344`, `40225466586`, and `40225896707` failed before Android boot because HVF returned `HV_UNSUPPORTED`, even with `-accel off`; the next attempt returns to Ubuntu x86_64.

## 5. Functional test matrix

The harness is `qa/calculator_e2e.py`. Each device test is written to the workflow's generated run report. No calculator test case ran in any of the fourteen completed attempts (`40204124011`, `40205135030`, `40206626414`, `40208505722`, `40208720426`, `40210565671`, `40211691552`, `40212729874`, `40214057816`, `40215666672`, `40217050828`, `40224996344`, `40225466586`, and `40225896707`). The latest Apple Silicon attempt failed before Android boot because HVF was unsupported, even with `-accel off`. The next run returns to Ubuntu x86_64, which reached APK installation in a prior run. A Google reference `BLOCKED` result is not counted as a MySpace functional pass.

| Test ID | Scenario | Expected result | Current status |
|---|---|---|---|
| TC-CALC-001 | Operator precedence: `2 + 3 × 4` | `14` | Not run — Android boot failed with `HV_UNSUPPORTED` in runs `40224996344`, `40225466586`, and `40225896707`; Ubuntu x86_64 retry pending (see QA-003) |
| TC-CALC-002 | Parentheses: `(2 + 3) × 4` | `20` | Not run — Android boot failed with `HV_UNSUPPORTED` in runs `40224996344`, `40225466586`, and `40225896707`; Ubuntu x86_64 retry pending (see QA-003) |
| TC-CALC-003 | Decimal addition: `0.1 + 0.2` | `0.3` | Not run — Android boot failed with `HV_UNSUPPORTED` in runs `40224996344`, `40225466586`, and `40225896707`; Ubuntu x86_64 retry pending (see QA-003) |
| TC-CALC-004 | Contextual percentage: `200 + 10%` | `220` | Not run — Android boot failed with `HV_UNSUPPORTED` in runs `40224996344`, `40225466586`, and `40225896707`; Ubuntu x86_64 retry pending (see QA-003) |
| TC-CALC-005 | Scientific square root: `√(9)` | `3` | Not run — Android boot failed with `HV_UNSUPPORTED` in runs `40224996344`, `40225466586`, and `40225896707`; Ubuntu x86_64 retry pending (see QA-003) |
| TC-CALC-006 | Degree-mode sine: `sin(30)` | `0.5` | Not run — Android boot failed with `HV_UNSUPPORTED` in runs `40224996344`, `40225466586`, and `40225896707`; Ubuntu x86_64 retry pending (see QA-003) |
| TC-CALC-007 | History persists after process restart and restores an entry | `1+1` and `2` visible/selectable | Not run — Android boot failed with `HV_UNSUPPORTED` in runs `40224996344`, `40225466586`, and `40225896707`; Ubuntu x86_64 retry pending (see QA-003) |
| TC-CALC-008 | Chaining: `1 ÷ 3 = × 3 =` | `1` | Not run — Android boot failed with `HV_UNSUPPORTED` in runs `40224996344`, `40225466586`, and `40225896707`; Ubuntu x86_64 retry pending (see QA-003); linked to CALC-001 |
| TC-CALC-009 | Scientific result continuation: `10^15 = + 1 =` | Continues without parser/validator error | Not run — Android boot failed with `HV_UNSUPPORTED` in runs `40224996344`, `40225466586`, and `40225896707`; Ubuntu x86_64 retry pending (see QA-003); linked to CALC-002 |
| TC-CALC-010 | Live official Google Calculator comparison | Common precedence case run in `com.google.android.calculator` | Not run — Android boot failed with `HV_UNSUPPORTED` in runs `40224996344`, `40225466586`, and `40225896707`; Ubuntu x86_64 retry pending (see QA-003); may be blocked |

The workflow also saves screenshots and UI hierarchy XML under the artifact's `evidence/` directory, including on failed cases. The workflow fails on MySpace functional `FAIL`/`ERROR` results; blocked Google-reference availability is separately reported.

## 6. CI evidence and limitations

- **Existing upstream result:** [TicTic Android CI run 40201068395](https://github.com/tarungittarun/TicTic/actions/runs/40201068395), commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`, concluded success. Its source-contract and Android build/unit-test steps are evidence of source-level CI health only, not APK runtime behavior.
- **New workflow:** `.github/workflows/calculator-apk-e2e.yml` checks out TicTic at pinned commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9` with a sparse checkout for the exact APK, verifies SHA-256 and ZIP integrity, then runs the calculator-only harness on a macOS 15 Apple Silicon runner with an API 30 `google_apis;arm64-v8a` emulator using QEMU software acceleration. Seven emulator setup attempts, four PackageManager/APK-install failures, one Monkey app-launch timeout, and one APK retrieval failure have prevented calculator test cases. No calculator test case has run yet.
- **Local execution limitation:** The review sandbox did not have Android SDK/ADB/emulator tooling or KVM, so no local device E2E was possible. GitHub Actions is the execution target.
- **Google comparator limitation:** An API 30 `google_apis` system image is requested (without the Play Store), so Google Calculator availability is not assumed. The workflow checks for the exact `com.google.android.calculator` package and will not silently substitute a non-Google app.
- **No false pass claim:** This report separates static analysis, expected-value assertions, actual emulator results, and live Google comparison. Only the latter two can establish runtime observations.

## 7. References

1. [Official Google Calculator Play listing](https://play.google.com/store/apps/details?id=com.google.android.calculator&hl=en) — feature reference only; not a live comparison in this report.
2. TicTic calculator implementation and tests at source commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`: `feature-calculator/src/main/java/app/space/feature/calculator/CalculatorRules.java`, `CalculatorScreen.java`, and `feature-calculator/src/test/java/app/space/feature/calculator/CalculatorRulesTest.java`.
3. TicTic app inventory note `APPS.md` — reports a prior v3.12.0 feature comparison; not independently reproduced here.
