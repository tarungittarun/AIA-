# MySpace Calculator — Defect Tracker & E2E QA Report

**Report ID:** `CALC-QA-2026-10-26-01`
**Prepared:** 26 October 2026 (Asia/Kolkata)
**Status:** Active — run 19 reached calculator E2E tests on Android 14 Google APIs ATD; input/navigation and history findings need an isolated rerun. The full run artifact could not be downloaded, and live Google Calculator comparison remains unconfirmed.
**Scope:** Calculator feature only. Other MySpace/TicTic features are explicitly out of scope.

## 1. Executive summary

The supplied APK is pinned by immutable Git blob and SHA-256. The linked TicTic source branch's latest Android CI run passed source-contract, Gradle unit-test/build, and lint checks, but did **not** exercise the release APK in an emulator. This QA branch has now made nineteen Actions attempts: eight emulator setup/boot failures, five PackageManager/APK-install failures, one APK retrieval failure, one Monkey launch timeout, three API 34 pre-test UI failures, and one Google APIs ATD run that installed the exact APK and reached calculator tests. [Run 40252777933](https://github.com/tarungittarun/AIA-/actions/runs/40252777933), job `121348072380`, ran on API 34 Google APIs ATD; it recorded one recoverable ANR “Wait” action and reached the calculator suite. Check annotations report TC-CALC-006 and TC-CALC-007 failures, and TC-CALC-008/009 errors. The run artifact download failed with EOF, so the full JSON/Markdown summary and unannotated outcomes are unavailable. The annotations show the History panel was left open after the history assertion failed, preventing the next tests from finding `AC`.

Run 19 observed `sin(3) = 0.0523359562` instead of the requested `sin(30) = 0.5`. This may be a missed/timing-sensitive zero tap rather than an app calculation defect: the visible history also recorded `.1+0.2` rather than the requested `0.1+0.2`. TC-CALC-007 did not find the newly calculated `1+1 = 2` after a force-stop, but the old harness did not verify the typed expression before restarting and waited only 0.25 seconds before killing the process. Therefore history persistence remains an **investigating observation**, not a confirmed product defect. The report separates these application findings from the confirmed harness-isolation failure.

The harness has since been hardened: keypad taps are constrained to the keypad region (avoiding same-text display nodes), inter-tap settling increased, each ordinary test verifies the typed expression before evaluating it, the history flow verifies `1+1 = 2` before restart and allows the asynchronous preferences write to settle, and History is closed in a `finally` cleanup. Every test outcome is now emitted as a GitHub check annotation, so status remains available if artifacts fail to download. Three emulator-free regression tests validate key targeting, exact expression matching, and History cleanup. The rerun is pending these changes. The two source-derived risks (rounded chained arithmetic and scientific-notation continuation) are still **not device-confirmed** because the corresponding run-19 tests were blocked by the History panel state.

A live side-by-side comparison with the official Google Calculator is **not confirmed**. Run 19's artifact was unavailable, and the available annotations do not reveal the exact result of the package scan or comparator. No third-party APK mirror is used and the old AOSP calculator is not treated as equivalent. Expected arithmetic values remain functional oracles, not proof of Google-app parity.

**Release / parity recommendation:** Do not claim Google Calculator parity. Re-run the hardened calculator-only suite, then resolve the history and input findings. A direct comparison remains blocked until the exact official package `com.google.android.calculator` is available and the workflow emits a verifiable result.

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
- **2026-10-26 — QA:** Run `40252777933` did not reach the arithmetic assertion: `TC-CALC-008` errored because the prior history test left the History panel open and the keypad was hidden. Keep this finding open as source-derived; the harness now closes History in a `finally` block before retrying.

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
- **2026-10-26 — QA:** Run `40252777933` `TC-CALC-009` errored before evaluating scientific notation because the keypad was hidden behind History after TC-CALC-007 failed. No device result is available; retry after the harness cleanup fix.

### CALC-003 — Newly calculated history entry absent after process restart (unconfirmed)

| Field | Assessment |
|---|---|
| **Type** | Functional / history persistence |
| **Severity / priority** | Provisional S3 — Moderate / P2 — Normal; reassess after reproduction |
| **Status** | Investigating — one run-19 failure; input delivery and persistence timing were not validated |
| **Affected area** | Equals → SharedPreferences history write → app process restart → History panel |
| **First observed** | Run `40252777933`, 26 October 2026; exact APK, Android 14 Google APIs ATD |

**Steps attempted**

1. Clear the calculator, enter `1 + 1`, and tap `=`.
2. Wait 0.25 seconds, force-stop `app.space.one`, and relaunch it.
3. Open History and search for `1+1 = 2`.

**Expected:** The newly calculated `1+1 = 2` item remains visible and selectable after the process restart.
**Actual:** TC-CALC-007 reported the entry missing. The run's visible History list contained earlier entries such as `2+3×4 = 14`, `(2+3)×4 = 20`, `.1+0.2 = 0.3`, and `200+10% = 220`, but no `1+1`. The full test artifact was not retrievable.

**Triage / uncertainty:** Run 19's harness did not confirm that the complete expression `1+1` was displayed or that `2` appeared before force-stop. Run 19 also shows a missed `0` in a separate expression, and it killed the app only 0.25 seconds after `SharedPreferences.apply()`, whose disk write is asynchronous. The finding may therefore be caused by incomplete key delivery or an overly short persistence wait. Do not attribute it to the app until a rerun verifies both pre-restart input/result and post-restart absence.

**Source review:** `CalculatorScreen.java` stores the expression/result through `AppPrefs.prefs(context).edit().putString(HISTORY_KEY, ...).apply()` when equals succeeds. This confirms the intended write path, not successful persistence on this emulator.

**Next action:** The updated test asserts `1+1` is visible before equals, confirms `2` before process restart, waits 1.5 seconds for the asynchronous preference write, then checks and selects the restored history expression. It also closes History in a `finally` block so a failed persistence assertion cannot contaminate later tests.

**Comment log**

- **2026-10-26 — QA:** Run `40252777933` observed the item missing after restart. Classification remains provisional until the hardened test distinguishes input failure from a persistence defect.

## 4. QA / environment tracking (not product defects)

### QA-001 — Official Google Calculator live comparator availability

| Field | Assessment |
|---|---|
| **Type** | Test environment blocker |
| **Status** | Open / not confirmed — run 19 reached the calculator suite, but its full artifact (including package-scan/comparator status) could not be downloaded; no direct Google comparison is established |
| **Product defect?** | No — this records a limitation of the comparison environment, not a MySpace app bug |

The official package `com.google.android.calculator` was not available in the local sandbox, and no official Google Calculator APK was obtained. The emulator workflow checks the exact package at runtime. Run 19 reached the end of the calculator suite, but its report artifact failed to download and the available annotations do not identify the package-scan or comparator outcome. Thus no direct comparison can be claimed. If the package is absent, the workflow records the live comparison as `BLOCKED` while still running deterministic arithmetic/UI checks against expected values. The old AOSP calculator is not treated as equivalent to the current official Google Calculator.

**Comment log**

- **2026-10-25 — QA:** The official Play listing and product description were reviewed, but no live interaction was performed. Any future comparison must identify the actual reference package/version and distinguish it from mathematical expected-value checks.

### QA-002 — Upstream CI did not cover runtime calculator UI

| Field | Assessment |
|---|---|
| **Type** | Test coverage gap |
| **Status** | Partial mitigation verified — run 19 reached calculator UI tests on Android 14 Google APIs ATD, but run artifacts were unavailable and several cases failed/errored. Harness corrections and emulator-free regression tests are now added; rerun pending |
| **Product defect?** | No — infrastructure finding |

The linked branch's latest CI run passed its build/test checks but does not install the release APK in an emulator or exercise calculator UI. This branch adds a separate Android Emulator Actions workflow. It pins the supplied APK by blob and SHA-256, tests calculator flows only, and uploads a Markdown/JSON run report plus screenshots and hierarchy/OCR evidence for 30 days. Eight emulator setup attempts failed before APK installation; one APK retrieval attempt failed with curl exit code 56; five Android 11 PackageManager/APK installs failed; and one software-emulator app launch timed out. Runs `40227928023`, `40248461920`, and `40250523030` booted API 34 and installed the APK but did not reach calculator tests. Run `40252777933` then booted API 34 Google APIs ATD, installed the exact APK, recovered once from an ANR “Wait” dialog, and ran the calculator suite. Its available annotations show TC-CALC-006/007 failures and TC-CALC-008/009 errors; the full report download failed with EOF. The harness now checks each test's typed expression, uses lower-region keypad targeting and longer tap settling, waits before the history force-stop, cleans up the History sheet, and emits each result as a GitHub check annotation. Three emulator-free tests cover these harness corrections. Rerun is pending; scope remains calculator-only.

### QA-003 — Actions emulator boot, installation, and app-launch failures

| Field | Assessment |
|---|---|
| **Type** | Test infrastructure / emulator reliability |
| **Status** | Partially mitigated — run 19 booted API 34 Google APIs ATD, installed the APK, and executed calculator cases; the ANR handler recovered once. Application-level failures and harness input/state-isolation issues now need the corrected rerun |
| **Runs / jobs** | [40204124011](https://github.com/tarungittarun/AIA-/actions/runs/40204124011), job `121201302193`; [40205135030](https://github.com/tarungittarun/AIA-/actions/runs/40205135030), job `121204338761`; [40206626414](https://github.com/tarungittarun/AIA-/actions/runs/40206626414), job `121208834615`; [40208505722](https://github.com/tarungittarun/AIA-/actions/runs/40208505722), job `121214502041`; [40208720426](https://github.com/tarungittarun/AIA-/actions/runs/40208720426), job `121215155606`; [40210565671](https://github.com/tarungittarun/AIA-/actions/runs/40210565671), job `121220690836`; [40211691552](https://github.com/tarungittarun/AIA-/actions/runs/40211691552), job `121224080079`; [40212729874](https://github.com/tarungittarun/AIA-/actions/runs/40212729874), job `121227260260`; [40214057816](https://github.com/tarungittarun/AIA-/actions/runs/40214057816), job `121231253984`; [40215666672](https://github.com/tarungittarun/AIA-/actions/runs/40215666672), job `121236137329`; [40217050828](https://github.com/tarungittarun/AIA-/actions/runs/40217050828), job `121240351784`; [40224996344](https://github.com/tarungittarun/AIA-/actions/runs/40224996344), job `121264373229`; [40225466586](https://github.com/tarungittarun/AIA-/actions/runs/40225466586), job `121265778684`; [40225896707](https://github.com/tarungittarun/AIA-/actions/runs/40225896707), job `121267068146`; [40226376668](https://github.com/tarungittarun/AIA-/actions/runs/40226376668), job `121268512489`; [40227928023](https://github.com/tarungittarun/AIA-/actions/runs/40227928023), job `121273214403`; [40248461920](https://github.com/tarungittarun/AIA-/actions/runs/40248461920), job `121334954755`; [40250523030](https://github.com/tarungittarun/AIA-/actions/runs/40250523030), job `121341188415`; [40252777933](https://github.com/tarungittarun/AIA-/actions/runs/40252777933), job `121348072380` |
| **Product defect?** | No — this tracker records emulator/workflow reliability. Run 19 did execute cases; individual functional and harness findings are tracked separately above and in QA-004. |

**Observed:** Eight emulator attempts failed before installation; one separate APK retrieval attempt failed with curl exit code 56. Five Android 11 runs failed at PackageManager/APK installation; one run installed but Monkey timed out. Three macOS/ARM64 attempts failed before boot with `HVF error: HV_UNSUPPORTED`. Run `40226376668` booted API 30 but both installs failed with `StorageManagerService.allocateBytes` / `PackageManagerInternal.freeStorage` null. Run `40227928023` booted API 34 x86_64 with software acceleration, received a PackageManager response after one readiness probe, and installed the exact APK; its UIAutomator dump exited 137. Runs `40248461920` and `40250523030` also installed on API 34 but stalled on system ANRs; the latter recovered by selecting “Wait” three times before an ADB input tap timed out. Run `40252777933` booted API 34 Google APIs ATD, installed the exact checksum-verified APK, recovered from one ANR “Wait” dialog, and reached test execution. Check-run annotations report TC-CALC-006/007 failures and TC-CALC-008/009 errors. The artifact download failed with EOF, so the complete summary, exact TC-CALC-010 status, and unannotated outcomes cannot be verified. The ANR cause remains unknown; the TC-CALC-008/009 errors were downstream of the History panel remaining open after TC-CALC-007 failed.

**Action:** Keep API 34 x86_64 and Google APIs ATD. The harness uses compressed/cached UIAutomator first, screenshot/Tesseract OCR with coordinate-derived keypad taps as fallback, and up to three “Wait” retries if an ANR dialog appears. On hierarchy failure it saves a screenshot, activity state, guest/system-server memory, and recent logcat. ATD may limit screenshots, so UIAutomator remains the primary path. Recent harness changes target taps only in the keypad region, add inter-tap settling and exact expression checks, wait 1.5 seconds before a history force-stop, and close History in cleanup. Every case now emits a check annotation. Rerun these changes before treating run-19 results as product defects. The Google comparator remains unconfirmed.

**Comment log**

- **2026-10-25 — QA:** Ten Actions attempts had produced no calculator test-case result; the latest at that point installed the APK but Monkey timed out before a calculator screen was confirmed.
- **2026-10-26 — QA:** Run `40217050828` failed before app launch with a StorageManager/PackageManager NPE. No app-level pass/fail should be inferred; the next attempt moved to macOS ARM64.
- **2026-10-26 — QA:** Runs `40224996344`, `40225466586`, and `40225896707` failed before Android boot because HVF returned `HV_UNSUPPORTED`, even with `-accel off`.
- **2026-10-26 — QA:** Run `40226376668` booted API 30; PackageManager answered after 27 probes, but installation failed twice with a `StorageManagerService.allocateBytes` null `PackageManagerInternal`. No calculator test case or Google comparison ran. The next run changes the emulator image to API 34.
- **2026-10-26 — QA:** Run `40227928023` booted API 34; PackageManager answered after one probe and the exact APK installed. The initial UIAutomator dump exited 137 before UI navigation. Cause is unconfirmed.
- **2026-10-26 — QA:** Run `40248461920` also booted API 34 and installed the APK. UIAutomator failed again; screenshot OCR then detected the Android system ANR dialog `Process system isn't responding` with `Wait` and `Close app`. The harness never reached the calculator.
- **2026-10-26 — QA:** Run `40250523030` installed the exact APK on API 34; compressed hierarchy failed and standard hierarchy succeeded, then OCR found the same system ANR. Three “Wait” attempts were followed by an ADB input tap timeout.
- **2026-10-26 — QA:** Run `40252777933` (job `121348072380`) booted API 34 Google APIs ATD, installed the exact APK, recovered once from an ANR dialog, and ran calculator tests. Check annotations identify TC-CALC-006/007 failures and TC-CALC-008/009 errors; artifact download failed with EOF. TC-CALC-008/009 were blocked by the History sheet left open after TC-CALC-007. The harness is being corrected and per-test GitHub annotations added for the rerun.

### QA-004 — Keypad targeting and History test isolation (harness defect)

| Field | Assessment |
|---|---|
| **Type** | E2E automation reliability / state isolation |
| **Status** | Corrected in the working tree; awaiting Actions verification |
| **Evidence** | Run `40252777933`: `sin(30)` arrived as `sin(3)`; decimal history recorded `.1+0.2`; History remained open after TC-CALC-007 and hid `AC` from TC-CALC-008/009 |
| **Product defect?** | No confirmed app defect. The observed symptoms can be explained by test-driver targeting/pacing and missing cleanup; verify with the updated test before reclassification. |

**Cause hypothesis:** The hierarchy tap resolver matched duplicate labels without restricting keypad controls to the keypad area, and keypad taps settled for only 0.18 seconds. A visible/editable display can contain the same text as a key (especially `0` after AC); the harness also lacked an assertion that the actual expression matched the intended key sequence. Separately, a failed History check did not close the sheet, leaving the keypad hidden for the next tests.

**Changes made:** Restrict keypad labels to nodes below 40% of screen height in both UIAutomator and OCR modes; increase tap settling to 0.35 seconds; assert each normal case's typed expression before evaluating; verify `1+1` and its `2` result before force-stop; wait 1.5 seconds before restart; and close History in `finally` cleanup. Added three emulator-free `unittest` checks for duplicate-zero targeting, exact expression matching, and History cleanup, and wired them into the Actions workflow before emulator setup. All three local tests pass. The next ATD run must confirm this improves real-device input; no claim is made yet.

**Comment log**

- **2026-10-26 — QA:** Run 19's sine and decimal evidence showed missing input digits, and the History sheet explained downstream TC-CALC-008/009 errors. Corrected the harness and added fast unit regression tests; awaiting real-emulator retest.

## 5. Functional test matrix

The harness is `qa/calculator_e2e.py`. Run 19, [Actions run `40252777933`](https://github.com/tarungittarun/AIA-/actions/runs/40252777933), is the first run to execute calculator UI cases: Android 14 Google APIs ATD booted, installed the exact APK, recovered once from an ANR “Wait” dialog, and reached the test suite. The full report artifact could not be downloaded (EOF); the check-run annotations are the available source of per-case failures/errors. They identify TC-CALC-006 and TC-CALC-007 as failures and TC-CALC-008 and TC-CALC-009 as errors. TC-CALC-008/009 errors arose because TC-CALC-007 left the History panel open, hiding the keypad. The unannotated cases are not treated as fully verified passes because the full artifact is missing; TC-CALC-003 also recorded `.1+0.2`, indicating an incomplete input sequence despite the `0.3` result. None of these results establishes Google Calculator parity. The harness now validates the input expression and emits an annotation for every test case so subsequent outcomes are visible even if the artifact download fails. A Google reference `BLOCKED` result is not counted as a MySpace functional pass.

| Test ID | Scenario | Expected result | Current status |
|---|---|---|---|
| TC-CALC-001 | Operator precedence: `2 + 3 × 4` | `14` | No failure annotation in run 19; history hierarchy showed `2+3×4 → 14`. Full artifact unavailable; per-test result will be explicit in the rerun. |
| TC-CALC-002 | Parentheses: `(2 + 3) × 4` | `20` | No failure annotation in run 19; history hierarchy showed `(2+3)×4 → 20`. Full artifact unavailable; per-test result will be explicit in the rerun. |
| TC-CALC-003 | Decimal addition: `0.1 + 0.2` | `0.3` | Inconclusive input: run-19 History showed `.1+0.2 → 0.3`; the result matched, but the leading `0` was not entered. Rerun after keypad-targeting fix; do not treat as a verified full-expression pass. |
| TC-CALC-004 | Contextual percentage: `200 + 10%` | `220` | No failure annotation in run 19; history hierarchy showed `200+10% → 220`. Full artifact unavailable; per-test result will be explicit in the rerun. |
| TC-CALC-005 | Scientific square root: `√(9)` | `3` | No failure annotation in run 19; the full artifact is unavailable, so retain as harness-reported only and verify explicitly on rerun. |
| TC-CALC-006 | Degree-mode sine: `sin(30)` | `0.5` | **FAIL (run 19, cause unconfirmed):** visible input/result was `sin(3) = 0.0523359562`; likely missed `0` tap or timing issue. Retest exact typed expression before diagnosing app math. |
| TC-CALC-007 | History persists after process restart and restores an entry | `1+1` and `2` visible/selectable | **FAIL (run 19, investigating):** the new entry was not found after process restart. The old harness did not verify the expression/result before force-stop and waited 0.25 s; see CALC-003. |
| TC-CALC-008 | Chaining: `1 ÷ 3 = × 3 =` | `1` | **ERROR / not evaluated (run 19):** TC-CALC-007 left History open, hiding `AC`; test isolation issue, not an app verdict. Linked to CALC-001. |
| TC-CALC-009 | Scientific result continuation: `10^15 = + 1 =` | Continues without parser/validator error | **ERROR / not evaluated (run 19):** History remained open after TC-CALC-007 and the keypad was hidden. Retry before drawing any parser conclusion; linked to CALC-002. |
| TC-CALC-010 | Live official Google Calculator comparison | Common precedence case run in `com.google.android.calculator` | **Unconfirmed in run 19:** exact package-scan/comparator outcome was in the unavailable artifact and no `TC-CALC-010` annotation was retrieved. No direct comparison or parity claim. |

The workflow saves screenshots plus UI hierarchy or synthetic OCR evidence under the artifact's `evidence/` directory. On a UIAutomator failure it also captures device activity, memory, and recent logcat diagnostics. The ATD image may limit screenshots; UIAutomator remains the primary evidence path. The workflow fails on MySpace functional `FAIL`/`ERROR` results; blocked Google-reference availability is separately reported.

## 6. CI evidence and limitations

- **Existing upstream result:** [TicTic Android CI run 40201068395](https://github.com/tarungittarun/TicTic/actions/runs/40201068395), commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`, concluded success. Its source-contract and Android build/unit-test steps are evidence of source-level CI health only, not APK runtime behavior.
- **New workflow:** `.github/workflows/calculator-apk-e2e.yml` checks out TicTic at pinned commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9` with a sparse checkout for the exact APK, verifies SHA-256 and ZIP integrity, unit-tests the QA harness, then runs calculator-only UI tests on `ubuntu-24.04` using an API 34 `google_atd;x86_64` emulator. Run `40252777933` booted, installed the APK, recovered once from a system ANR, and ran the suite. Four test cases received failure/error annotations; full artifact download failed with EOF. The updated harness now emits per-test annotations, targets keypad controls rather than same-text display labels, validates typed expressions, waits for the history preference write, and closes History after failure. The next Actions run will verify these corrections; artifact retrieval remains a limitation to watch.
- **Local execution limitation:** The review sandbox did not have Android SDK/ADB/emulator tooling or KVM, so no local device E2E was possible. GitHub Actions is the execution target.
- **Google comparator limitation:** The API 34 `google_atd` image provides Google APIs but not the Play Store; Google Calculator availability is not assumed. The workflow checks for the exact `com.google.android.calculator` package and will not silently substitute a non-Google app. Run 19's artifact did not reveal whether the package was installed, so no live comparison is claimed.
- **No false pass claim:** This report separates static analysis, expected-value assertions, actual emulator results, and live Google comparison. Only the latter two can establish runtime observations.

## 7. References

1. [Official Google Calculator Play listing](https://play.google.com/store/apps/details?id=com.google.android.calculator&hl=en) — feature reference only; not a live comparison in this report.
2. TicTic calculator implementation and tests at source commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`: `feature-calculator/src/main/java/app/space/feature/calculator/CalculatorRules.java`, `CalculatorScreen.java`, and `feature-calculator/src/test/java/app/space/feature/calculator/CalculatorRulesTest.java`.
3. TicTic app inventory note `APPS.md` — reports a prior v3.12.0 feature comparison; not independently reproduced here.
4. [Android Developers: scalable automated testing and ATD images](https://android-developers.googleblog.com/2021/10/whats-new-in-scalable-automated-testing.html) — describes ATD as a leaner system image that removes non-test apps/services and reduces CPU/memory load; screenshot behavior can be limited when hardware rendering is disabled.
