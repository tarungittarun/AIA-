# MySpace Calculator — Defect Tracker & E2E QA Report

**Report ID:** `CALC-QA-2026-10-26-01`
**Prepared:** 26 October 2026 (Asia/Kolkata)
**Status:** Active — runs 19 and 20 reached calculator E2E tests on Android 14 Google APIs ATD. Run 21's empty compressed hierarchy is now recovered by the standard UIAutomator retry: run 22 confirmed the fallback works, installed the exact APK, and exposed the `Process system isn't responding` dialog, but three “Wait” retries did not restore Calculator navigation. No run-22 calculator case or Google comparison executed; the emulator system ANR is now the primary blocker.
**Scope:** Calculator feature only. Other MySpace/TicTic features are explicitly out of scope.

## 1. Executive summary

The supplied APK is pinned by immutable Git blob and SHA-256. The linked TicTic source branch's latest Android CI run passed source-contract, Gradle unit-test/build, and lint checks, but did **not** exercise the release APK in an emulator. This QA branch has now made twenty-two Actions attempts: eight emulator setup/boot failures, five PackageManager/APK-install failures, one APK retrieval failure, one Monkey launch timeout, three API 34 pre-test UI failures, two Google APIs ATD runs that installed the exact APK and reached calculator tests, one ATD UI-inspection failure, and one ATD navigation failure after the new hierarchy retry worked. [Run 40252777933](https://github.com/tarungittarun/AIA-/actions/runs/40252777933), job `121348072380`, first reached the suite but left History open after a failed history assertion; this caused downstream keypad errors. [Run 40257359718](https://github.com/tarungittarun/AIA-/actions/runs/40257359718), job `121361967128`, completed UI cases in 35 minutes but exposed unverified zero/equals/continuation input; its artifact download failed with EOF. [Run 40268619689](https://github.com/tarungittarun/AIA-/actions/runs/40268619689), job `121396370520`, booted API 34 Google APIs ATD and installed the exact APK, but `uiautomator dump` returned malformed/empty XML and screenshot OCR found no text. Run 21 executed no calculator cases. Run 22, [Actions run `40270102374`](https://github.com/tarungittarun/AIA-/actions/runs/40270102374), proved the standard-dump retry recovers the UI hierarchy and installed the exact APK after an install retry, but the hierarchy showed `Process system isn't responding`; three “Wait” attempts did not restore Calculator navigation. No calculator test or Google-package scan ran. Its 34,624-byte artifact also failed to download with EOF. The six-test harness unit step passed in Actions.

Run 20 confirms the first four expected calculations in the visible History list: `2+3×4 → 14`, `(2+3)×4 → 20`, `0.1+0.2 → 0.3`, and `200+10% → 220`. TC-CALC-005 emitted a `PASS` notice for `√(9)` but displayed the expression together with `= 3`; because the calculation did not appear in History, equals commitment is not verified. TC-CALC-006 saw `sin(3)` instead of `sin(30)`, and TC-CALC-009 saw `1^15` instead of `10^15`, confirming zero-key delivery is still unreliable in scientific flows. TC-CALC-007 showed `1+1` and `= 2` before restart, but retained the expression in the editor—evidence that the equals key had not committed the calculation and History persistence was therefore **not tested**. TC-CALC-008 ended at `0.3333333333` without a visible `×3` continuation, so it does not yet establish a rounding defect. Do not attribute these to the app until the exact input and committed state are verified.

The committed harness checks that each non-placeholder zero tap changes the visible expression, resets keypad state, verifies equals commitment, and confirms continuation suffixes before chained assertions. The History test skips persistence checks unless `1+1 = 2` is visibly committed; Google package scanning is guarded and reports TC-CALC-010 errors. Run 21 exposed malformed/empty compressed UIAutomator output and no OCR-readable text. Run 22 verified the standard-hierarchy retry using a separate path; it successfully read the ANR dialog but could not recover the system process after three “Wait” attempts, so the input/commit checks did not run. Six regression tests (targeting, zero feedback, expression matching, History cleanup, package scanning, and standard-dump recovery) passed locally and in run 22 Actions. Two additional local tests cover the reboot recovery helper and its one-time use after three failed ANR “Wait” retries; all eight now pass locally, and the next Actions attempt will exercise this path.

The source-derived risks (rounded chained arithmetic and scientific-notation continuation) remain **unconfirmed**; run 20 did not verify the continuation inputs. A live side-by-side comparison with official Google Calculator is also **not confirmed**. Run 20 emitted no TC-CALC-010/summary annotation; runs 21 and 22 failed before package scanning. Run 22's evidence artifact could not be downloaded. No third-party APK mirror is used, and the old AOSP calculator is not treated as equivalent. Expected arithmetic values remain functional oracles, not proof of Google-app parity.

**Release / parity recommendation:** Do not claim Google Calculator parity or close the source-derived findings yet. Re-run the hardened calculator-only suite. A direct comparison can be reported only if the exact official package `com.google.android.calculator` is detected and the TC-CALC-010 outcome is visible.

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
- **2026-10-26 — QA:** Run `40252777933` did not reach the arithmetic assertion: `TC-CALC-008` errored because the prior history test left the History panel open and the keypad was hidden.
- **2026-10-26 — QA:** Run `40257359718` reported `TC-CALC-008` FAIL, but the final display remained `0.3333333333` with no visible `×3` continuation. The test had not asserted that the continuation input registered, so this is not yet evidence of rounded-result propagation. The harness now verifies the `×3` suffix and equals commitment before classifying the arithmetic.

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
- **2026-10-26 — QA:** Run `40252777933` `TC-CALC-009` errored before evaluating scientific notation because the keypad was hidden behind History after TC-CALC-007 failed.
- **2026-10-26 — QA:** Run `40257359718` `TC-CALC-009` also did not reach the continuation check: the intended `10^15` input appeared as `1^15`. The new per-key zero feedback and basic/scientific panel isolation must make this expression exact before any parser finding is recorded.

### CALC-003 — History persistence not verified because equals did not commit

| Field | Assessment |
|---|---|
| **Type** | E2E test-validity observation / history persistence |
| **Severity / priority** | Unassigned — no product persistence defect is confirmed |
| **Status** | Inconclusive — run 20 showed the expression still in the editor with a preview, so the history write was not proven to have occurred |
| **Affected area** | Equals tap → SharedPreferences history write → app process restart → History panel |
| **First observed** | Run `40252777933`; diagnostic evidence clarified by run `40257359718`, 26 October 2026 |

**Steps attempted in run 20**

1. Verify the visible input is `1+1`, then tap `=`.
2. Wait 1.5 seconds, force-stop `app.space.one`, relaunch it, and open History.
3. Search for `1+1 = 2`.

**Expected:** A committed `1+1 = 2` calculation remains visible and selectable after process restart.
**Actual:** TC-CALC-007 reported no new entry; History still showed four earlier entries (`2+3×4 = 14`, `(2+3)×4 = 20`, `0.1+0.2 = 0.3`, and `200+10% = 220`). Crucially, immediately before restart the display still showed `1+1` and `= 2` rather than replacing the expression with `2`; this is consistent with the equals tap not committing and `= 2` being only a preview. The artifact could not be downloaded, but the check annotation contains these visible values.

**Triage / uncertainty:** Since the app's equals handler clears/replaces the expression only on commit, run 20 did not establish that a history write occurred. The missing history entry is therefore not evidence of persistence loss. The earlier run 19 also had incomplete input. Keep this record as an inconclusive test observation, not an app defect, until a completed equals flow is verified and a committed calculation still disappears after restart.

**Source review:** `CalculatorScreen.java` stores the expression/result through `AppPrefs.prefs(context).edit().putString(HISTORY_KEY, ...).apply()` when equals succeeds. This confirms the intended write path, not whether the equals tap committed in run 20.

**Next action:** The updated test rejects a pre-restart display that still contains `1+1`, records an `ERROR`, and skips the restart/persistence assertion. It also ensures the basic keypad is open and closes History in `finally` cleanup.

**Comment log**

- **2026-10-26 — QA:** Run `40252777933` initially reported the entry missing without verifying input/commit.
- **2026-10-26 — QA:** Run `40257359718` verified `1+1` and a `= 2` preview but not a committed result. Persistence remains untested; do not classify as a product defect.

## 4. QA / environment tracking (not product defects)

### QA-001 — Official Google Calculator live comparator availability

| Field | Assessment |
|---|---|
| **Type** | Test environment blocker |
| **Status** | Open / not confirmed — runs 19 and 20 reached calculator tests but their package-scan outcomes are unavailable; runs 21 and 22 failed before package scanning. No direct Google comparison is established |
| **Product defect?** | No — this records a limitation of the comparison environment, not a MySpace app bug |

The official package `com.google.android.calculator` was not available in the local sandbox, and no official Google Calculator APK was obtained. The emulator workflow checks the exact package at runtime. Runs 19 and 20 reached calculator tests, but both report-artifact downloads failed and run 20 emitted no TC-CALC-010/aggregate annotation; runs 21 and 22 failed before the package scan. The exact package-scan/comparator outcome is unknown; no direct comparison can be claimed. The updated harness reports a package-scan error instead of aborting if ADB is unresponsive. If the package is absent, the workflow records the live comparison as `BLOCKED` while still running deterministic arithmetic/UI checks against expected values. The old AOSP calculator is not treated as equivalent to the current official Google Calculator.

**Comment log**

- **2026-10-25 — QA:** The official Play listing and product description were reviewed, but no live interaction was performed. Any future comparison must identify the actual reference package/version and distinguish it from mathematical expected-value checks.

### QA-002 — Upstream CI did not cover runtime calculator UI

| Field | Assessment |
|---|---|
| **Type** | Test coverage gap |
| **Status** | Partial mitigation verified — runs 19 and 20 reached calculator UI tests; run 20 confirmed TC-CALC-001–004. Run 22 verified standard UIAutomator recovery but hit a persistent system-process ANR before Calculator navigation. Six tests passed in run 22 Actions; two additional regression tests cover one bounded reboot/relaunch recovery, pending run 23. No functional cases ran in runs 21–22 |
| **Product defect?** | No — infrastructure finding |

The linked branch's latest CI run passed its build/test checks but does not install the release APK in an emulator or exercise calculator UI. This branch adds a separate Android Emulator Actions workflow. It pins the supplied APK by blob and SHA-256, tests calculator flows only, and uploads a Markdown/JSON run report plus screenshots and hierarchy/OCR evidence for 30 days. Eight emulator setup attempts failed before APK installation; one APK retrieval attempt failed with curl exit code 56; five Android 11 PackageManager/APK installs failed; and one software-emulator app launch timed out. Runs `40227928023`, `40248461920`, and `40250523030` booted API 34 and installed the APK but did not reach calculator tests. Run `40252777933` reached tests but left History open after TC-CALC-007; its artifact failed to download. Run `40257359718` emitted result notices for TC-CALC-001–005 and exposed input/equals gaps, but no TC-CALC-010 or aggregate annotation; its artifact also failed to download. Run `40268619689` booted and installed the APK but failed before navigation because the compressed UIAutomator output was malformed/empty and OCR returned no text. Run `40270102374` verified the alternate standard-dump retry: it recovered a valid hierarchy after the compressed output failed, but that hierarchy showed a system-process ANR; three “Wait” retries did not permit Calculator navigation. No UI test or Google-package scan ran in runs 21–22. Six emulator-free regression tests passed in the run-22 Actions step; eight now pass locally after adding two bounded ANR reboot/relaunch recovery checks. Run 23 will exercise that recovery path. Scope remains calculator-only.

### QA-003 — Actions emulator boot, installation, and app-launch failures

| Field | Assessment |
|---|---|
| **Type** | Test infrastructure / emulator reliability |
| **Status** | Partially mitigated — runs 19 and 20 executed calculator cases. Run 22's standard-dump retry recovered the hierarchy but exposed a persistent system-process ANR after APK installation. A bounded reboot/relaunch recovery is added for run 23; functional navigation remains unverified |
| **Runs / jobs** | [40204124011](https://github.com/tarungittarun/AIA-/actions/runs/40204124011), job `121201302193`; [40205135030](https://github.com/tarungittarun/AIA-/actions/runs/40205135030), job `121204338761`; [40206626414](https://github.com/tarungittarun/AIA-/actions/runs/40206626414), job `121208834615`; [40208505722](https://github.com/tarungittarun/AIA-/actions/runs/40208505722), job `121214502041`; [40208720426](https://github.com/tarungittarun/AIA-/actions/runs/40208720426), job `121215155606`; [40210565671](https://github.com/tarungittarun/AIA-/actions/runs/40210565671), job `121220690836`; [40211691552](https://github.com/tarungittarun/AIA-/actions/runs/40211691552), job `121224080079`; [40212729874](https://github.com/tarungittarun/AIA-/actions/runs/40212729874), job `121227260260`; [40214057816](https://github.com/tarungittarun/AIA-/actions/runs/40214057816), job `121231253984`; [40215666672](https://github.com/tarungittarun/AIA-/actions/runs/40215666672), job `121236137329`; [40217050828](https://github.com/tarungittarun/AIA-/actions/runs/40217050828), job `121240351784`; [40224996344](https://github.com/tarungittarun/AIA-/actions/runs/40224996344), job `121264373229`; [40225466586](https://github.com/tarungittarun/AIA-/actions/runs/40225466586), job `121265778684`; [40225896707](https://github.com/tarungittarun/AIA-/actions/runs/40225896707), job `121267068146`; [40226376668](https://github.com/tarungittarun/AIA-/actions/runs/40226376668), job `121268512489`; [40227928023](https://github.com/tarungittarun/AIA-/actions/runs/40227928023), job `121273214403`; [40248461920](https://github.com/tarungittarun/AIA-/actions/runs/40248461920), job `121334954755`; [40250523030](https://github.com/tarungittarun/AIA-/actions/runs/40250523030), job `121341188415`; [40252777933](https://github.com/tarungittarun/AIA-/actions/runs/40252777933), job `121348072380`; [40257359718](https://github.com/tarungittarun/AIA-/actions/runs/40257359718), job `121361967128`; [40268619689](https://github.com/tarungittarun/AIA-/actions/runs/40268619689), job `121396370520`; [40270102374](https://github.com/tarungittarun/AIA-/actions/runs/40270102374), job `121400854300` |
| **Product defect?** | No — this tracker records emulator/workflow reliability. Runs 19–20 executed cases; runs 21–22 did not. Functional and harness findings are tracked separately in CALC-001–003 and QA-004/005. |

**Observed:** Eight emulator attempts failed before installation; one separate APK retrieval attempt failed with curl exit code 56. Five Android 11 runs failed at PackageManager/APK installation; one run installed but Monkey timed out. Three macOS/ARM64 attempts failed before boot with `HVF error: HV_UNSUPPORTED`. Run `40226376668` booted API 30 but both installs failed with `StorageManagerService.allocateBytes` / `PackageManagerInternal.freeStorage` null. Run `40227928023` booted API 34 x86_64 with software acceleration, received a PackageManager response after one readiness probe, and installed the exact APK; its UIAutomator dump exited 137. Runs `40248461920` and `40250523030` also installed on API 34 but stalled on system ANRs; the latter recovered by selecting “Wait” three times before an ADB input tap timed out. Run `40252777933` booted API 34 Google APIs ATD, installed the exact APK, recovered from one ANR “Wait” dialog, and reached test execution; History remained open after TC-CALC-007. Run `40257359718` booted the same image, installed the exact APK, and completed the calculator step in 35 minutes. Its notices confirmed TC-CALC-001–005 visible results; TC-CALC-006 reported `sin(3)`, TC-CALC-007 showed `1+1` / `= 2` still in the editor before restart, TC-CALC-008 ended at the uncontinued `0.3333333333`, and TC-CALC-009 showed `1^15`. No TC-CALC-010 or aggregate-summary annotation was emitted. Run 20's artifact failed to download with EOF. Run `40268619689` (job `121396370520`) also booted API 34 ATD, installed the exact APK, then stopped before UI navigation: compressed UIAutomator output was malformed/empty (`syntax error: line 1, column 0`) and screenshot OCR found no visible text. Diagnostics were saved; no calculator test or Google-package scan ran. Its 27.8 KB evidence artifact also failed to download with EOF. Run `40270102374` (job `121400854300`) booted API 34 Google APIs ATD; PackageManager responded after one probe, install attempt 1 failed but retry installed the exact APK. The compressed hierarchy was unusable, then the new standard UIAutomator retry succeeded and exposed `Process system isn't responding`. Selecting “Wait” three times did not restore Calculator navigation; no functional case or Google-package scan ran. The 34,624-byte `calculator-e2e-evidence-22` artifact failed to download with EOF. The run-19 History isolation issue is corrected; run 20's app findings remain inconclusive because input/equals state was unverified, and runs 21–22 are environment failures rather than app results.

**Action:** Keep API 34 x86_64 and Google APIs ATD for continuity. The harness tries compressed UIAutomator, standard UIAutomator, and a second standard dump using separate files with a short backoff; it validates nonempty XML and requires UI nodes. Run 22 confirmed the standard retry can recover the hierarchy after malformed compressed output. That hierarchy exposed a system-process ANR; three “Wait” retries did not restore the app screen. The next alternate attempt now adds one bounded emulator reboot/relaunch after three failed system-ANR “Wait” retries, rather than repeating unchanged UI dumps; run 23 will exercise it. If the ANR persists, a runner with supported hardware acceleration is the next infrastructure fallback. OCR, device/memory/activity diagnostics, and logcat are still retained. Eight emulator-free tests pass locally; the six-test run-22 Actions unit step passed. No run 21/22 calculator or Google comparison result is available.

**Comment log**

- **2026-10-25 — QA:** Ten Actions attempts had produced no calculator test-case result; the latest at that point installed the APK but Monkey timed out before a calculator screen was confirmed.
- **2026-10-26 — QA:** Run `40217050828` failed before app launch with a StorageManager/PackageManager NPE. No app-level pass/fail should be inferred; the next attempt moved to macOS ARM64.
- **2026-10-26 — QA:** Runs `40224996344`, `40225466586`, and `40225896707` failed before Android boot because HVF returned `HV_UNSUPPORTED`, even with `-accel off`.
- **2026-10-26 — QA:** Run `40226376668` booted API 30; PackageManager answered after 27 probes, but installation failed twice with a `StorageManagerService.allocateBytes` null `PackageManagerInternal`. No calculator test case or Google comparison ran. The next run changes the emulator image to API 34.
- **2026-10-26 — QA:** Run `40227928023` booted API 34; PackageManager answered after one probe and the exact APK installed. The initial UIAutomator dump exited 137 before UI navigation. Cause is unconfirmed.
- **2026-10-26 — QA:** Run `40248461920` also booted API 34 and installed the APK. UIAutomator failed again; screenshot OCR then detected the Android system ANR dialog `Process system isn't responding` with `Wait` and `Close app`. The harness never reached the calculator.
- **2026-10-26 — QA:** Run `40250523030` installed the exact APK on API 34; compressed hierarchy failed and standard hierarchy succeeded, then OCR found the same system ANR. Three “Wait” attempts were followed by an ADB input tap timeout.
- **2026-10-26 — QA:** Run `40252777933` (job `121348072380`) booted API 34 Google APIs ATD, installed the exact APK, recovered once from an ANR dialog, and ran calculator tests. Check annotations identify TC-CALC-006/007 failures and TC-CALC-008/009 errors; artifact download failed with EOF. TC-CALC-008/009 were blocked by the History sheet left open after TC-CALC-007. The harness cleanup was corrected before the next run.
- **2026-10-26 — QA:** Run `40257359718` (job `121361967128`) passed its harness unit-test step and executed calculator cases. TC-CALC-001–005 emitted PASS notices; TC-CALC-006 (`sin(3)`), TC-CALC-007 (still-visible `1+1`/`=2` preview), TC-CALC-008 (no visible `×3`), and TC-CALC-009 (`1^15`) need input/commit-aware retesting. No TC-CALC-010 or summary annotation was produced, and artifact download again failed with EOF. Zero-key feedback, equals commitment, panel reset, continuation checks, and package-scan handling were included in run 21.
- **2026-10-26 — QA:** Run `40268619689` (job `121396370520`) passed the five-test harness unit-test step from commit `68668e5`, booted Android 14 Google APIs ATD, and installed the exact APK. UIAutomator returned malformed/empty XML and screenshot OCR found no visible text; the suite did not navigate to Calculator or run any test cases. The artifact download failed with EOF.
- **2026-10-26 — QA:** Run `40270102374` (job `121400854300`) passed all six harness unit tests, booted API 34 ATD, and installed the exact APK after an installation retry. The compressed hierarchy failed validation, but standard UIAutomator recovered a valid hierarchy and exposed the system-process ANR. Three “Wait” attempts did not clear it, so no calculator case or Google package scan ran; artifact download failed with EOF.

### QA-004 — Keypad targeting, equals commitment, and test isolation (harness defect)

| Field | Assessment |
|---|---|
| **Type** | E2E automation reliability / state isolation |
| **Status** | Five input/commit/package-scan harness checks passed in run 21; six checks, including standard-dump recovery, passed in run 22. Two additional local checks cover bounded ANR reboot/relaunch recovery for run 23. The input/commit fixes remain unverified on-device |
| **Evidence** | Run `40252777933`: `sin(30)` arrived as `sin(3)`, decimal history recorded `.1+0.2`, and History hid the keypad after TC-CALC-007. Run `40257359718`: `0.1+0.2` was corrected, but scientific inputs still became `sin(3)` / `1^15`; TC-CALC-007 showed only a preview, and TC-CALC-008 showed no `×3` continuation. |
| **Product defect?** | No confirmed app defect from these cases. Run 20 shows the harness was accepting preview results and not confirming zero/continuation input; retest before reclassification. |

**Cause hypothesis:** Run 19's duplicate-label selection and 0.18-second tap settling likely contributed to missed zero taps; the keypad-region filter and longer delay corrected the decimal expression in run 20, but did not fully solve zero delivery on the scientific panel. The harness also lacked per-zero feedback, reset panel state between basic/scientific cases, and treated `= result` previews as committed results. The History cleanup bug in run 19 was independently confirmed and fixed.

**Changes made:** Restrict keypad labels below 40% of screen height and prefer non-EditText/lower controls; increase tap settling to 0.35 seconds and require later zero taps to change the visible expression; explicitly close the scientific panel before basic flows; assert exact expression before evaluating; reject a result if the original expression remains visible after equals; and confirm `×3`/`+1` continuation text before arithmetic assertions. The history test verifies a committed `1+1 = 2` before force-stop and skips persistence if equals was not committed, while retaining a 1.5-second write-settle and `finally` cleanup. Google package scanning is guarded so failures still produce TC-CALC-010 and a report. Runs 21 and 22 failed before calculator navigation, so the input/commit fixes were not exercised. Run 22 did verify that the standard UIAutomator retry recovers from malformed compressed XML. Six `unittest` checks covering targeting, zero feedback, expression matching, History cleanup, package scanning, and hierarchy recovery passed locally and in run 22 Actions. Two additional local regressions cover bounded reboot/relaunch after a persistent system ANR; run 23 will run them in Actions.

**Comment log**

- **2026-10-26 — QA:** Run 19 exposed missed digits and the open-History isolation defect. The first fixes were committed and run 20 verified History cleanup, but scientific zero taps, equals commitment, and chained-input delivery remained uncertain. Run 21 failed before UI navigation. Run 22 verified the standard-dump retry but then hit the persistent system-process ANR, so the functional input assertions remain unexercised.

### QA-005 — Empty/malformed UI hierarchy with no OCR text on ATD

| Field | Assessment |
|---|---|
| **Type** | Test infrastructure / Android UI inspection |
| **Status** | Mitigated in run 22 — the standard UIAutomator retry recovered a valid hierarchy after malformed compressed output. The hierarchy exposed a system-process ANR, tracked separately in QA-003 |
| **Evidence** | [Run `40268619689`](https://github.com/tarungittarun/AIA-/actions/runs/40268619689), job `121396370520`: API 34 Google APIs ATD booted, PackageManager responded, exact APK installed, then hierarchy parsing failed at line 1 column 0 and screenshot OCR returned no visible text |
| **Product defect?** | No — no calculator UI case ran; this is an emulator/UI-inspection infrastructure failure. |

**Observed:** The previous harness selected standard UIAutomator only when the compressed `uiautomator dump` command itself failed. In run 21 the compressed command returned without a command error, but the file read parsed as empty/malformed XML. OCR fallback then found no visible text. The emulator diagnostics were saved; the 27.8 KB evidence artifact failed to download with EOF. Root cause (temporary UIAutomator service failure, incomplete dump, or ATD screenshot behavior) remains unknown.

**Action:** The revised dumper tries compressed, standard, then a second standard dump using separate remote paths, with a short backoff between attempts so UiAutomation can recover. Each output must parse as XML and contain at least one UI node before it is accepted. If all attempts fail, the harness retains device/logcat diagnostics and attempts OCR. The emulator-free regression test simulates an empty compressed file followed by valid standard XML; it passes locally and in Actions. Run 22 confirmed the standard retry on the actual emulator; further UI navigation was blocked by the separate system ANR in QA-003.

**Comment log**

- **2026-10-26 — QA:** Run 21 failed before Calculator navigation; no functional result or Google package scan is available. Standard-dump recovery was added for run 22.
- **2026-10-26 — QA:** Run 22's standard retry successfully recovered a valid hierarchy after the compressed dump failed validation. It exposed the ANR dialog instead of a blank screen; three “Wait” attempts did not recover the system. The hierarchy-retry finding is mitigated; see QA-003 for the remaining emulator blocker.

## 5. Functional test matrix

The harness is `qa/calculator_e2e.py`. Run 19, [Actions run `40252777933`](https://github.com/tarungittarun/AIA-/actions/runs/40252777933), first reached calculator UI cases on Android 14 Google APIs ATD. Run 20, [Actions run `40257359718`](https://github.com/tarungittarun/AIA-/actions/runs/40257359718), ran for 35 minutes; annotations show TC-CALC-001–005 result notices, TC-CALC-006 input mismatch (`sin(3)`), TC-CALC-007's missing post-restart entry despite an uncommitted `= 2` preview, TC-CALC-008 with no visible `×3` continuation, and TC-CALC-009 input mismatch (`1^15`). Runs 19–22 evidence-artifact downloads failed with EOF. Run 20 emitted no TC-CALC-010 or aggregate-summary annotation; the official-package outcome remains unknown. Only TC-CALC-001–004 are currently verified by visible History entries; TC-CALC-005's PASS notice may reflect a preview rather than a committed calculation. Run 21, [Actions run `40268619689`](https://github.com/tarungittarun/AIA-/actions/runs/40268619689), booted and installed the APK but failed before UI navigation because UIAutomator XML was malformed/empty and OCR found no text. Run 22, [Actions run `40270102374`](https://github.com/tarungittarun/AIA-/actions/runs/40270102374), verified standard hierarchy recovery after the compressed dump failed, but the recovered tree showed a system-process ANR; three “Wait” attempts did not restore the calculator UI. Runs 21 and 22 executed no calculator case or package scan. Six harness tests passed locally and in the run-22 Actions unit step; eight now pass locally after adding two ANR reboot-recovery regressions for run 23. No outcome establishes Google Calculator parity.

| Test ID | Scenario | Expected result | Current status |
|---|---|---|---|
| TC-CALC-001 | Operator precedence: `2 + 3 × 4` | `14` | **PASS (run 20):** annotation and persisted History entry both show `2+3×4 → 14`. |
| TC-CALC-002 | Parentheses: `(2 + 3) × 4` | `20` | **PASS (run 20):** annotation and persisted History entry both show `(2+3)×4 → 20`. |
| TC-CALC-003 | Decimal addition: `0.1 + 0.2` | `0.3` | **PASS (run 20):** annotation shows `0.3`, and History records the exact input `0.1+0.2 → 0.3`; the leading-zero issue from run 19 was corrected. |
| TC-CALC-004 | Contextual percentage: `200 + 10%` | `220` | **PASS (run 20):** annotation and persisted History entry both show `200+10% → 220`. |
| TC-CALC-005 | Scientific square root: `√(9)` | `3` | **Provisional (run 20):** PASS notice showed `√(9)` and `= 3`, but History still contained only four earlier entries; the equals action may have left a preview. Rerun with the committed-result check; runs 21–22 did not reach this case. |
| TC-CALC-006 | Degree-mode sine: `sin(30)` | `0.5` | **ERROR (run 20):** expected-expression guard caught `sin(3)` instead of `sin(30)`; no sine assertion was run. Zero-key feedback checks are in the harness, but runs 21–22 failed before the case; retest remains pending. |
| TC-CALC-007 | History persists after process restart and restores an entry | Committed `1+1 = 2` visible/selectable after restart | **Inconclusive (run 20):** History lacked a new entry, but immediately before restart the editor still showed `1+1` with `= 2` preview, so equals was not verified as committed. See CALC-003; the harness now skips persistence assertions unless the editor changes to `2`. Runs 21–22 did not reach this case. |
| TC-CALC-008 | Chaining: `1 ÷ 3 = × 3 =` | `1` | **Inconclusive (run 20):** final display remained `0.3333333333`; the `×3` continuation was not visible/verified. No rounding defect established. The harness now verifies equals and the continuation suffix before comparing results; runs 21–22 did not reach this case. Linked to CALC-001. |
| TC-CALC-009 | Scientific result continuation: `10^15 = + 1 =` | Continues without parser/validator error | **ERROR (run 20):** typed expression was `1^15`, not `10^15`; no scientific-notation continuation was tested. Zero-key/panel-state checks are in the harness, but runs 21–22 failed before the case; retest remains pending. Linked to CALC-002. |
| TC-CALC-010 | Live official Google Calculator comparison | Common precedence case run in `com.google.android.calculator` | **Unknown (run 20):** no TC-CALC-010 or aggregate-summary annotation was emitted, and artifact download failed with EOF. The scan/comparator outcome is not assumed; runs 21–22 failed before package scanning. No direct comparison or parity claim. |

The workflow saves screenshots plus UI hierarchy or synthetic OCR evidence under the artifact's `evidence/` directory. On a UIAutomator failure it also captures device activity, memory, and recent logcat diagnostics. The ATD image may limit screenshots; UIAutomator remains the primary evidence path. The workflow fails on MySpace functional `FAIL`/`ERROR` results; blocked Google-reference availability is separately reported.

## 6. CI evidence and limitations

- **Existing upstream result:** [TicTic Android CI run 40201068395](https://github.com/tarungittarun/TicTic/actions/runs/40201068395), commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`, concluded success. Its source-contract and Android build/unit-test steps are evidence of source-level CI health only, not APK runtime behavior.
- **New workflow:** `.github/workflows/calculator-apk-e2e.yml` checks out TicTic at pinned commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9` with a sparse checkout for the exact APK, verifies SHA-256 and ZIP integrity, unit-tests the QA harness, then runs calculator-only UI tests on `ubuntu-24.04` using an API 34 `google_atd;x86_64` emulator. Runs `40252777933` and `40257359718` installed the APK and reached calculator tests; run 20 lasted 35 minutes. Run `40268619689` failed pre-navigation on malformed/empty hierarchy plus no OCR text. Run `40270102374` verified standard hierarchy recovery, but the recovered screen showed a system-process ANR that remained after three “Wait” attempts. Artifacts for runs 19–22 all failed to download with EOF. The workflow reports cases through check annotations; six harness unit tests passed in run 22 Actions, and eight pass locally with the reboot-recovery checks queued for run 23. No calculator test ran in runs 21–22.
- **Local execution limitation:** The review sandbox did not have Android SDK/ADB/emulator tooling or KVM, so no local device E2E was possible. GitHub Actions is the execution target.
- **Google comparator limitation:** The API 34 `google_atd` image provides Google APIs but not the Play Store; Google Calculator availability is not assumed. The workflow checks for the exact `com.google.android.calculator` package and will not silently substitute a non-Google app. Runs 19 and 20 did not expose the package-scan/comparator outcome because their artifacts failed to download and run 20 emitted no TC-CALC-010 annotation; runs 21 and 22 failed before scanning. No live comparison is claimed.
- **No false pass claim:** This report separates static analysis, expected-value assertions, actual emulator results, and live Google comparison. Only the latter two can establish runtime observations.

## 7. References

1. [Official Google Calculator Play listing](https://play.google.com/store/apps/details?id=com.google.android.calculator&hl=en) — feature reference only; not a live comparison in this report.
2. TicTic calculator implementation and tests at source commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`: `feature-calculator/src/main/java/app/space/feature/calculator/CalculatorRules.java`, `CalculatorScreen.java`, and `feature-calculator/src/test/java/app/space/feature/calculator/CalculatorRulesTest.java`.
3. TicTic app inventory note `APPS.md` — reports a prior v3.12.0 feature comparison; not independently reproduced here.
4. [Android Developers: scalable automated testing and ATD images](https://android-developers.googleblog.com/2021/10/whats-new-in-scalable-automated-testing.html) — describes ATD as a leaner system image that removes non-test apps/services and reduces CPU/memory load; screenshot behavior can be limited when hardware rendering is disabled.
