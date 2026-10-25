# MySpace Calculator — Defect Tracker & E2E QA Report

**Report ID:** `CALC-QA-2026-10-25-01`
**Prepared:** 25 October 2026 (Asia/Kolkata)
**Status:** Preliminary — two Ubuntu emulator attempts failed before UI tests; Apple Silicon retry queued
**Scope:** Calculator feature only. Other MySpace/TicTic features are explicitly out of scope.

## 1. Executive summary

The supplied APK was identified and pinned by immutable Git blob and SHA-256. The linked TicTic source branch's latest Android CI run passed its source-contract, Gradle unit-test/build, and lint jobs. That run did **not** launch an emulator or exercise calculator UI flows. Two Actions attempts in this QA branch failed before the test script ran: [run 40204124011](https://github.com/tarungittarun/AIA-/actions/runs/40204124011) reported `Timeout waiting for emulator to boot`, while [run 40205135030](https://github.com/tarungittarun/AIA-/actions/runs/40205135030) ended inside emulator setup with shell exit code 2. No application-level pass/fail result is claimed. The workflow has been moved from the Ubuntu runner to an Apple Silicon macOS runner for the next attempt.

Static review of the calculator's result-to-expression path identified two reproducible-looking calculation risks: a rounded display result is reused during chained arithmetic, and a result rendered in scientific notation is not supported as a numeric literal by the input parser. These are **source-confirmed risks, not yet device-confirmed observations**. The workflow is configured to install the exact APK into a disposable Android emulator and exercise the calculator UI; neither attempt reached the Python UI harness, so no per-run test report or screenshot evidence has been generated.

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
| **Status** | Open / not assessed — emulator did not boot |
| **Product defect?** | No — this records a limitation of the comparison environment, not a MySpace app bug |

The official package `com.google.android.calculator` was not available in the local sandbox, and no official Google Calculator APK was obtained. The emulator workflow checks the exact package at runtime. If it is absent, it records the live comparison as `BLOCKED` while still running deterministic arithmetic/UI checks against expected values. The old AOSP calculator is not treated as equivalent to the current official Google Calculator.

**Comment log**

- **2026-10-25 — QA:** The official Play listing and product description were reviewed, but no live interaction was performed. Any future comparison must identify the actual reference package/version and distinguish it from mathematical expected-value checks.

### QA-002 — Upstream CI did not cover runtime calculator UI

| Field | Assessment |
|---|---|
| **Type** | Test coverage gap |
| **Status** | Mitigation added; two Ubuntu emulator setup failures; macOS retry pending |
| **Product defect?** | No — infrastructure finding |

The linked branch's latest CI run passed its build/test checks but does not install the release APK in an emulator or exercise the suite navigation and calculator UI. This branch adds a separate Android Emulator Actions workflow. It pins the supplied APK by blob and SHA-256, requests an API 34 Google Play emulator, tests calculator flows only, and uploads a Markdown/JSON run report plus screenshots/UI dumps for 30 days. Two Ubuntu attempts failed before the Python test harness ran; the first timed out waiting for emulator boot and the second ended with shell exit code 2 during emulator setup. The workflow now uses an Apple Silicon macOS runner with an arm64 Google Play image to avoid relying on Linux KVM.

### QA-003 — Android emulator setup failure in GitHub Actions

| Field | Assessment |
|---|---|
| **Type** | Test infrastructure failure |
| **Status** | Open — runner changed; macOS retry pending |
| **Runs / jobs** | [40204124011](https://github.com/tarungittarun/AIA-/actions/runs/40204124011), job `121201302193`; [40205135030](https://github.com/tarungittarun/AIA-/actions/runs/40205135030), job `121204338761` |
| **Product defect?** | No — the test harness never reached app installation or UI execution |

**Observed:** Both Ubuntu-hosted `reactivecircus/android-emulator-runner` steps ended before the custom test script. The first reported `Timeout waiting for emulator to boot`; the second produced a shell exit-code-2 annotation. APK download and SHA-256 verification succeeded in both runs. The upload step found no report files, confirming that the Python UI harness did not run. Detailed runner logs were not retrievable in this environment, so the second failure's precise root cause is unknown.

**Action:** Increased the action boot wait to 1,200 seconds and removed the redundant `-wipe-data` option, but the second attempt still failed during setup. The workflow is now moved to the `macos-15` Apple Silicon runner with an `arm64-v8a` Google Play system image so it can use native macOS virtualization. If the retry also fails, investigate runner diagnostics and use a known-supported `google_apis` image for functional E2E while keeping official Google Calculator comparison blocked unless the exact package is present.

**Comment log**

- **2026-10-25 — QA:** Both failures are infrastructure/setup outcomes only. No calculator pass, failure, or Google-package availability should be inferred from either run.

## 5. Functional test matrix

The harness is `qa/calculator_e2e.py`. Each device test is written to the workflow's generated run report. No application test ran in either Ubuntu Actions attempt (`40204124011` and `40205135030`): both failed before the custom UI script. The macOS retry is pending. A Google reference `BLOCKED` result is not counted as a MySpace functional pass.

| Test ID | Scenario | Expected result | Current status |
|---|---|---|---|
| TC-CALC-001 | Operator precedence: `2 + 3 × 4` | `14` | Not run — emulator setup failed in runs `40204124011` and `40205135030`; macOS retry pending |
| TC-CALC-002 | Parentheses: `(2 + 3) × 4` | `20` | Not run — emulator setup failed in runs `40204124011` and `40205135030`; macOS retry pending |
| TC-CALC-003 | Decimal addition: `0.1 + 0.2` | `0.3` | Not run — emulator setup failed in runs `40204124011` and `40205135030`; macOS retry pending |
| TC-CALC-004 | Contextual percentage: `200 + 10%` | `220` | Not run — emulator setup failed in runs `40204124011` and `40205135030`; macOS retry pending |
| TC-CALC-005 | Scientific square root: `√(9)` | `3` | Not run — emulator setup failed in runs `40204124011` and `40205135030`; macOS retry pending |
| TC-CALC-006 | Degree-mode sine: `sin(30)` | `0.5` | Not run — emulator setup failed in runs `40204124011` and `40205135030`; macOS retry pending |
| TC-CALC-007 | History persists after process restart and restores an entry | `1+1` and `2` visible/selectable | Not run — emulator setup failed in runs `40204124011` and `40205135030`; macOS retry pending |
| TC-CALC-008 | Chaining: `1 ÷ 3 = × 3 =` | `1` | Not run — emulator setup failed in runs `40204124011` and `40205135030`; macOS retry pending; linked to CALC-001 |
| TC-CALC-009 | Scientific result continuation: `10^15 = + 1 =` | Continues without parser/validator error | Not run — emulator setup failed in runs `40204124011` and `40205135030`; macOS retry pending; linked to CALC-002 |
| TC-CALC-010 | Live official Google Calculator comparison | Common precedence case run in `com.google.android.calculator` | Not run — emulator setup failed in runs `40204124011` and `40205135030`; macOS retry pending; may be blocked |

The workflow also saves screenshots and UI hierarchy XML under the artifact's `evidence/` directory, including on failed cases. The workflow fails on MySpace functional `FAIL`/`ERROR` results; blocked Google-reference availability is separately reported.

## 6. CI evidence and limitations

- **Existing upstream result:** [TicTic Android CI run 40201068395](https://github.com/tarungittarun/TicTic/actions/runs/40201068395), commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`, concluded success. Its source-contract and Android build/unit-test steps are evidence of source-level CI health only, not APK runtime behavior.
- **New workflow:** `.github/workflows/calculator-apk-e2e.yml` downloads the exact Git blob and verifies SHA-256. Two Ubuntu emulator attempts failed before app installation; the current configuration retries on Apple Silicon macOS with an API 34 Google Play image. The UI harness has not yet run.
- **Local execution limitation:** The review sandbox did not have Android SDK/ADB/emulator tooling or KVM, so no local device E2E was possible. GitHub Actions is the execution target.
- **Google comparator limitation:** A Google Play emulator image is requested, but it is not assumed to contain Google Calculator. The workflow checks package availability and will not silently substitute a non-Google app.
- **No false pass claim:** This report separates static analysis, expected-value assertions, actual emulator results, and live Google comparison. Only the latter two can establish runtime observations.

## 7. References

1. [Official Google Calculator Play listing](https://play.google.com/store/apps/details?id=com.google.android.calculator&hl=en) — feature reference only; not a live comparison in this report.
2. TicTic calculator implementation and tests at source commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`: `feature-calculator/src/main/java/app/space/feature/calculator/CalculatorRules.java`, `CalculatorScreen.java`, and `feature-calculator/src/test/java/app/space/feature/calculator/CalculatorRulesTest.java`.
3. TicTic app inventory note `APPS.md` — reports a prior v3.12.0 feature comparison; not independently reproduced here.
