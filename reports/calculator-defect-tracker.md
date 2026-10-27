# MySpace Calculator — Defect Tracker & E2E QA Report

> **Current release addendum (27 October 2026):** The calculator-only direct APK QA for **MySpace 3.12.39 (76) / MyCalc 1.0.37 (38)** is recorded in [`calculator-defect-tracker-v3.12.39-76.md`](calculator-defect-tracker-v3.12.39-76.md), with screenshots and provenance in [`myspace-calculator-qa-v3.12.39-76.pdf`](myspace-calculator-qa-v3.12.39-76.pdf). The older report below is retained verbatim as historical context; its run numbers and version-specific claims are not superseded or rewritten.

**Report ID:** `CALC-QA-2026-10-26-01`
**Prepared:** 26 October 2026 (Asia/Kolkata)
**Status:** Active — runs 19, 20, and 23 reached calculator E2E tests on Android 14 Google APIs ATD. Run 23 validated both alternate recovery paths: standard UIAutomator recovered after malformed compressed output, and one bounded emulator reboot recovered navigation after a persistent system ANR. TC-CALC-001–004 passed again; TC-CALC-008 now confirms the chained-precision failure. TC-CALC-005/006/009 still show uncommitted or undelivered input, TC-CALC-007 and TC-CALC-010 have no visible annotations, and Google Calculator parity is not established.
**Scope:** Calculator feature only. Other MySpace/TicTic features are explicitly out of scope.

## 1. Executive summary

The supplied APK is pinned by immutable Git blob and SHA-256. The linked TicTic source branch's latest Android CI run passed source-contract, Gradle unit-test/build, and lint checks, but did **not** exercise the release APK in an emulator. This QA branch has now made twenty-three Actions attempts: eight emulator setup/boot failures, five PackageManager/APK-install failures, one APK retrieval failure, one Monkey launch timeout, three API 34 pre-test UI failures, three Google APIs ATD runs that reached calculator cases, one ATD hierarchy-inspection failure, and one ATD navigation failure. [Run 40252777933](https://github.com/tarungittarun/AIA-/actions/runs/40252777933), job `121348072380`, first reached the suite but left History open after a failed history assertion; [run 40257359718](https://github.com/tarungittarun/AIA-/actions/runs/40257359718), job `121361967128`, completed cases in 35 minutes but exposed unverified zero/equals/continuation input. [Run 40268619689](https://github.com/tarungittarun/AIA-/actions/runs/40268619689), job `121396370520`, installed the APK but UIAutomator returned malformed/empty XML and screenshot OCR found no text. Run 22, [Actions run `40270102374`](https://github.com/tarungittarun/AIA-/actions/runs/40270102374), verified standard-dump recovery but exposed a system-process ANR; three “Wait” attempts did not restore navigation. Run 23, [Actions run `40272601441`](https://github.com/tarungittarun/AIA-/actions/runs/40272601441), recovered through a single emulator reboot and ran calculator tests for 43m43s. Its eight-test Actions unit step passed. The 47,815-byte run-23 evidence artifact failed to download with EOF.

Run 23 independently confirmed TC-CALC-001–004 (`14`, `20`, `0.3`, `220`). TC-CALC-008 now **fails with valid input/continuation checks**: after `1 ÷ 3 =`, the visible value was `0.3333333333`, and continuing with `×3 =` did not return `1`; this confirms the chained-precision defect at runtime (exact final display text could not be recovered from the artifact). TC-CALC-005 still did not visibly commit `√(9) = 3`; TC-CALC-006 and TC-CALC-009 failed zero-key delivery before their intended calculations could be evaluated. Run 23 emitted no visible TC-CALC-007 or TC-CALC-010 annotation, and its report artifact could not be downloaded, so History persistence and Google Calculator availability/comparison remain unknown.

The committed harness now validates the expression before equals, rejects preview-only results, waits for zero-key UI feedback, checks continuation suffixes, retries standard UIAutomator after malformed compressed output, and performs one bounded reboot/relaunch after persistent system ANR. Eight emulator-free regression tests pass locally; run 23's eight-test Actions unit step passed. The APK was installed and tested without touching non-calculator features.

A live side-by-side comparison with official Google Calculator is **not confirmed**. Runs 20 and 23 emitted no visible TC-CALC-010 result; runs 21 and 22 failed before package scanning, and run-23 artifact retrieval failed with EOF. No third-party APK mirror is used, and the old AOSP calculator is not treated as equivalent. Expected-value results, including the confirmed chaining defect, are not proof of Google-app parity.

Run 20 confirmed the first four expected calculations in visible History: `2+3×4 → 14`, `(2+3)×4 → 20`, `0.1+0.2 → 0.3`, and `200+10% → 220`; run 23 independently reproduced those four values in the display. For TC-CALC-005, run 20 showed `√(9)` with `= 3` as a preview, and run 23 again found the expression still visible after equals, so a committed square-root calculation remains unverified. TC-CALC-006 and TC-CALC-009 exposed zero-key delivery failures (run 23 showed `sin(3` after the zero tap and `1` / `= 1` during the `10^15` sequence); the intended scientific expressions were not evaluated. Run 20's TC-CALC-007 showed `1+1` and `= 2` before restart but did not prove a commit; run 23 emitted no TC-CALC-007 annotation, so History persistence remains unknown. Unlike run 20, run 23 verified the `×3` continuation and second equals commitment in TC-CALC-008, yet the chained result did not equal `1`. This is now a runtime-confirmed arithmetic defect, not merely a missed input.

The committed harness verifies typed expressions before equals, rejects preview-only results, waits for zero-key feedback, and checks chained-input suffixes. It also recovers from malformed compressed hierarchy dumps and reboots once after a persistent system ANR. Run 22 verified hierarchy recovery; run 23 verified the reboot/relaunch path and proceeded to calculator tests. Eight emulator-free regression tests pass locally and in the run-23 Actions unit step. The history test skips persistence unless `1+1 = 2` is visibly committed; Google-package scanning remains guarded, but run 23 emitted no comparator result.

The rounded chained-arithmetic risk is **confirmed by run 23**; scientific-notation continuation remains untested because zero-key delivery stopped TC-CALC-009 before the intended expression. A live side-by-side comparison with official Google Calculator is **not confirmed**: runs 20 and 23 emitted no TC-CALC-010/summary annotation, and runs 21–22 failed before package scanning. The run-23 artifact failed to download. No third-party APK mirror is used, and the old AOSP calculator is not treated as equivalent. Matching expected values alone are not proof of Google-app parity.

**Release / parity recommendation:** Track CALC-001 as a confirmed chained-precision product defect and address it. Do not claim Google Calculator parity. Resolve the undelivered zero/equals inputs, obtain TC-CALC-007 and TC-CALC-010 evidence, and report a direct comparison only if the exact official package `com.google.android.calculator` is detected and its outcome is visible.

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

### CALC-001 — Chained calculation reuses rounded display value

| Field | Assessment |
|---|---|
| **Type** | Functional / numerical accuracy |
| **Severity / priority** | S2 — Major / P1 — High |
| **Status** | Confirmed on-device in run 23 — verified `1 ÷ 3 = × 3 =` continuation did not return `1`; source path predicts rounded-display propagation |
| **Affected area** | Equals → operator continuation |
| **First observed** | Static review of source commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`; runtime confirmed in Actions run `40272601441` (26 October 2026) |

**Steps to reproduce**

1. Open Calculator and clear the expression.
2. Enter `1 ÷ 3`, then tap `=`.
3. Tap `×`, `3`, then `=`.

**Expected:** `1` (within the calculator's display precision).
**Actual:** Run 23 confirmed that the tested chain did not return `1`. The first result was visibly `0.3333333333`. The exact final display string is unavailable because the Actions evidence artifact failed to download; source analysis predicts `0.9999999999` when the rounded first result is reused as the next operand. The harness verified the `1÷3` expression, visible `×3` continuation, and committed second equals before reporting the mismatch.

**Impact:** A normal equals-then-continue flow can propagate display rounding into subsequent calculations. This can produce visibly incorrect results in chained arithmetic, especially when users expect an exact integer or use the result as a later operand.

**Technical evidence:** `CalculatorRules.format()` rounds ordinary decimal output to ten places (`CalculatorRules.java`, lines 57–60). The equals handler formats the evaluated value, then sets `expression` to the formatted `result` (`CalculatorScreen.java`, lines 1228–1249). The `format()` comment says rounding is display-only, but the UI continuation path stores the formatted string back into `expression`; run 23's verified equals-then-operator result is consistent with that round trip.

**Suggested fix:** Keep the raw numeric result (or a suitable exact representation) separate from the formatted display string. On an operator after equals, seed the next expression from the raw value; continue using the formatted string only for display/history presentation. Add a regression test for `(1 ÷ 3) × 3` through the equals-continuation path, not only as one complete expression.

**Workaround:** Enter the complete expression `1 ÷ 3 × 3` before pressing equals; this avoids the intermediate display-format round trip.

**Comment log**

- **2026-10-25 — QA:** Static path review identifies the defect mechanism. The predicted output has not been observed on-device; the new emulator test `TC-CALC-008` is intended to confirm or reject it.
- **2026-10-26 — QA:** Run `40252777933` did not reach the arithmetic assertion: `TC-CALC-008` errored because the prior history test left the History panel open and the keypad was hidden.
- **2026-10-26 — QA:** Run `40257359718` reported `TC-CALC-008` FAIL, but the final display remained `0.3333333333` with no visible `×3` continuation. The test had not asserted that the continuation input registered, so this was not evidence of rounded-result propagation. The harness now verifies the `×3` suffix and equals commitment before classifying the arithmetic.
- **2026-10-26 — QA:** Run `40272601441` verified the complete `1÷3 = ×3 =` flow: input and continuation checks passed, the second equals committed, but the result did not equal `1` after the first displayed value `0.3333333333`. This confirms the runtime discrepancy; artifact download failed, so the precise final display string is not available.

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
- **2026-10-26 — QA:** Run `40257359718` `TC-CALC-009` did not reach the continuation check: the intended `10^15` input appeared as `1^15`.
- **2026-10-26 — QA:** Run `40272601441` failed `TC-CALC-009` at the zero-key feedback guard (`10^15` entry stayed at `1` / `= 1`). The scientific-notation parser/continuation path was still not exercised; do not classify CALC-002 as a confirmed runtime defect.

### CALC-003 — History persistence not verified because equals did not commit

| Field | Assessment |
|---|---|
| **Type** | E2E test-validity observation / history persistence |
| **Severity / priority** | Unassigned — no product persistence defect is confirmed |
| **Status** | Inconclusive — run 20 showed the expression still in the editor with a preview; run 23 emitted no visible TC-CALC-007 result. No history write/persistence outcome is established |
| **Affected area** | Equals tap → SharedPreferences history write → app process restart → History panel |
| **First observed** | Run `40252777933`; diagnostic evidence clarified by run `40257359718`, 26 October 2026 |

**Steps attempted in run 20**

1. Verify the visible input is `1+1`, then tap `=`.
2. Wait 1.5 seconds, force-stop `app.space.one`, relaunch it, and open History.
3. Search for `1+1 = 2`.

**Expected:** A committed `1+1 = 2` calculation remains visible and selectable after process restart.
**Actual:** TC-CALC-007 reported no new entry; History still showed four earlier entries (`2+3×4 = 14`, `(2+3)×4 = 20`, `0.1+0.2 = 0.3`, and `200+10% = 220`). Crucially, immediately before restart the display still showed `1+1` and `= 2` rather than replacing the expression with `2`; this is consistent with the equals tap not committing and `= 2` being only a preview. The run-20 artifact could not be downloaded, but its check annotation contains these visible values. Run 23 emitted no visible TC-CALC-007 annotation, so its persistence status remains unknown.

**Triage / uncertainty:** Since the app's equals handler clears/replaces the expression only on commit, run 20 did not establish that a history write occurred. The missing history entry is therefore not evidence of persistence loss. The earlier run 19 also had incomplete input. Keep this record as an inconclusive test observation, not an app defect, until a completed equals flow is verified and a committed calculation still disappears after restart.

**Source review:** `CalculatorScreen.java` stores the expression/result through `AppPrefs.prefs(context).edit().putString(HISTORY_KEY, ...).apply()` when equals succeeds. This confirms the intended write path, not whether the equals tap committed in run 20.

**Next action:** The updated test rejects a pre-restart display that still contains `1+1`, records an `ERROR`, and skips the restart/persistence assertion. It also ensures the basic keypad is open and closes History in `finally` cleanup.

**Comment log**

- **2026-10-26 — QA:** Run `40252777933` initially reported the entry missing without verifying input/commit.
- **2026-10-26 — QA:** Run `40257359718` verified `1+1` and a `= 2` preview but not a committed result. Persistence remains untested; do not classify as a product defect.
- **2026-10-26 — QA:** Run `40272601441` emitted no visible TC-CALC-007 annotation, and its evidence artifact failed to download. History persistence remains unknown.

## 4. QA / environment tracking (not product defects)

### QA-001 — Official Google Calculator live comparator availability

| Field | Assessment |
|---|---|
| **Type** | Test environment blocker |
| **Status** | Open / not confirmed — runs 19, 20, and 23 reached calculator cases, but no visible TC-CALC-010 result is available; runs 21–22 failed before package scanning. No direct Google comparison is established |
| **Product defect?** | No — this records a limitation of the comparison environment, not a MySpace app bug |

The official package `com.google.android.calculator` was not available in the local sandbox, and no official Google Calculator APK was obtained. The emulator workflow checks the exact package at runtime. Runs 19, 20, and 23 reached calculator tests, but no visible TC-CALC-010 or summary annotation is available; artifact downloads failed. Runs 21 and 22 did not reach package scanning. The exact package-scan/comparator outcome is unknown; no direct comparison can be claimed. The updated harness reports a package-scan error instead of aborting if ADB is unresponsive. If the package is absent, the workflow records the live comparison as `BLOCKED` while still running deterministic arithmetic/UI checks against expected values. The old AOSP calculator is not treated as equivalent to the current official Google Calculator.

**Comment log**

- **2026-10-25 — QA:** The official Play listing and product description were reviewed, but no live interaction was performed. Any future comparison must identify the actual reference package/version and distinguish it from mathematical expected-value checks.

### QA-002 — Upstream CI did not cover runtime calculator UI

| Field | Assessment |
|---|---|
| **Type** | Test coverage gap |
| **Status** | Partial mitigation verified — runs 19, 20, and 23 reached calculator tests. Run 23 verified the standard hierarchy fallback and one-time reboot recovery after a system ANR, then produced runtime results. Eight harness unit tests passed in run 23 Actions; no functional cases ran in runs 21–22 |
| **Product defect?** | No — infrastructure finding |

The linked branch's latest CI run passed its build/test checks but does not install the release APK in an emulator or exercise calculator UI. This branch adds a separate Android Emulator Actions workflow. It pins the supplied APK by blob and SHA-256, tests calculator flows only, and uploads a Markdown/JSON run report plus screenshots and hierarchy/OCR evidence for 30 days. Eight emulator setup attempts failed before APK installation; one APK retrieval attempt failed with curl exit code 56; five Android 11 PackageManager/APK installs failed; and one software-emulator app launch timed out. Runs `40227928023`, `40248461920`, and `40250523030` booted API 34 and installed the APK but did not reach calculator tests. Run `40252777933` reached tests but left History open after TC-CALC-007; its artifact failed to download. Run `40257359718` emitted result notices for TC-CALC-001–005 and exposed input/equals gaps, but no TC-CALC-010 or aggregate annotation; its artifact also failed to download. Run `40268619689` booted and installed the APK but failed before navigation because the compressed UIAutomator output was malformed/empty and OCR returned no text. Run `40270102374` verified standard-dump recovery but stopped at a system-process ANR after three “Wait” retries. Run `40272601441` exercised the added bounded reboot/relaunch recovery, reached Calculator, and ran functional cases; TC-CALC-001–004 passed and TC-CALC-008 confirmed the chaining discrepancy. TC-CALC-005/006/009 still exposed uncommitted or undelivered input. No functional UI case ran in runs 21–22; no TC-CALC-010 outcome is available. Eight harness tests passed in run-23 Actions; scope remains calculator-only.

### QA-003 — Actions emulator boot, installation, and app-launch failures

| Field | Assessment |
|---|---|
| **Type** | Test infrastructure / emulator reliability |
| **Status** | Partially mitigated — run 22's standard-dump retry recovered the hierarchy; run 23's bounded reboot/relaunch recovery restored navigation after a system ANR and allowed calculator cases to run. Software-emulator startup remains slow, but navigation is now demonstrated |
| **Runs / jobs** | [40204124011](https://github.com/tarungittarun/AIA-/actions/runs/40204124011), job `121201302193`; [40205135030](https://github.com/tarungittarun/AIA-/actions/runs/40205135030), job `121204338761`; [40206626414](https://github.com/tarungittarun/AIA-/actions/runs/40206626414), job `121208834615`; [40208505722](https://github.com/tarungittarun/AIA-/actions/runs/40208505722), job `121214502041`; [40208720426](https://github.com/tarungittarun/AIA-/actions/runs/40208720426), job `121215155606`; [40210565671](https://github.com/tarungittarun/AIA-/actions/runs/40210565671), job `121220690836`; [40211691552](https://github.com/tarungittarun/AIA-/actions/runs/40211691552), job `121224080079`; [40212729874](https://github.com/tarungittarun/AIA-/actions/runs/40212729874), job `121227260260`; [40214057816](https://github.com/tarungittarun/AIA-/actions/runs/40214057816), job `121231253984`; [40215666672](https://github.com/tarungittarun/AIA-/actions/runs/40215666672), job `121236137329`; [40217050828](https://github.com/tarungittarun/AIA-/actions/runs/40217050828), job `121240351784`; [40224996344](https://github.com/tarungittarun/AIA-/actions/runs/40224996344), job `121264373229`; [40225466586](https://github.com/tarungittarun/AIA-/actions/runs/40225466586), job `121265778684`; [40225896707](https://github.com/tarungittarun/AIA-/actions/runs/40225896707), job `121267068146`; [40226376668](https://github.com/tarungittarun/AIA-/actions/runs/40226376668), job `121268512489`; [40227928023](https://github.com/tarungittarun/AIA-/actions/runs/40227928023), job `121273214403`; [40248461920](https://github.com/tarungittarun/AIA-/actions/runs/40248461920), job `121334954755`; [40250523030](https://github.com/tarungittarun/AIA-/actions/runs/40250523030), job `121341188415`; [40252777933](https://github.com/tarungittarun/AIA-/actions/runs/40252777933), job `121348072380`; [40257359718](https://github.com/tarungittarun/AIA-/actions/runs/40257359718), job `121361967128`; [40268619689](https://github.com/tarungittarun/AIA-/actions/runs/40268619689), job `121396370520`; [40270102374](https://github.com/tarungittarun/AIA-/actions/runs/40270102374), job `121400854300`; [40272601441](https://github.com/tarungittarun/AIA-/actions/runs/40272601441), job `121408458329` |
| **Product defect?** | No — this tracker records emulator/workflow reliability. Runs 19, 20, and 23 executed cases; runs 21–22 did not. Functional and harness findings are tracked separately in CALC-001–003 and QA-004/005. |

**Observed:** Eight emulator attempts failed before installation; one separate APK retrieval attempt failed with curl exit code 56. Five Android 11 runs failed at PackageManager/APK installation; one run installed but Monkey timed out. Three macOS/ARM64 attempts failed before boot with `HVF error: HV_UNSUPPORTED`. Run `40226376668` booted API 30 but both installs failed with `StorageManagerService.allocateBytes` / `PackageManagerInternal.freeStorage` null. Run `40227928023` booted API 34 x86_64 with software acceleration, received a PackageManager response after one readiness probe, and installed the exact APK; its UIAutomator dump exited 137. Runs `40248461920` and `40250523030` also installed on API 34 but stalled on system ANRs; the latter recovered by selecting “Wait” three times before an ADB input tap timed out. Run `40252777933` booted API 34 Google APIs ATD, installed the exact APK, recovered from one ANR “Wait” dialog, and reached test execution; History remained open after TC-CALC-007. Run `40257359718` booted the same image, installed the exact APK, and completed the calculator step in 35 minutes. Its notices confirmed TC-CALC-001–005 visible results; TC-CALC-006 reported `sin(3)`, TC-CALC-007 showed `1+1` / `= 2` still in the editor before restart, TC-CALC-008 ended at the uncontinued `0.3333333333`, and TC-CALC-009 showed `1^15`. No TC-CALC-010 or aggregate-summary annotation was emitted. Run 20's artifact failed to download with EOF. Run `40268619689` (job `121396370520`) also booted API 34 ATD, installed the exact APK, then stopped before UI navigation: compressed UIAutomator output was malformed/empty (`syntax error: line 1, column 0`) and screenshot OCR found no visible text. Diagnostics were saved; no calculator test or Google-package scan ran. Its 27.8 KB evidence artifact also failed to download with EOF. Run `40270102374` (job `121400854300`) booted API 34 Google APIs ATD; PackageManager responded after one probe, install attempt 1 failed but retry installed the exact APK. The compressed hierarchy was unusable, then the new standard UIAutomator retry succeeded and exposed `Process system isn't responding`. Selecting “Wait” three times did not restore Calculator navigation; no functional case or Google-package scan ran. The 34,624-byte `calculator-e2e-evidence-22` artifact failed to download with EOF. Run `40272601441` (job `121408458329`) passed its eight-test harness step, booted API 34 ATD, installed the exact APK after an install retry, recovered the hierarchy with a standard dump, then rebooted once after three system-ANR “Wait” retries. It relaunched the package and reached calculator cases; TC-CALC-001–004 passed, TC-CALC-008 failed with a verified continuation, and TC-CALC-005/006/009 exposed input/commit errors. Run 23 emitted no visible TC-CALC-007/010 or aggregate-summary annotation. Its 47,815-byte evidence artifact failed to download with EOF. The run-19 History isolation issue is corrected; run 20's unresolved input findings remain inconclusive, runs 21–22 are environment failures, and run 23 confirms the TC-CALC-008 product discrepancy.

**Action:** Keep API 34 x86_64 and Google APIs ATD for continuity. The harness tries compressed UIAutomator, standard UIAutomator, and a second standard dump using separate files with a short backoff; it validates nonempty XML and requires UI nodes. Run 22 confirmed the standard retry can recover the hierarchy after malformed compressed output. That hierarchy exposed a system-process ANR; three “Wait” retries did not restore the app screen. Run 23 verified one bounded emulator reboot/relaunch after three failed system-ANR “Wait” retries; the target package remained installed and calculator navigation succeeded. If ANRs persist on future runs, a runner with supported hardware acceleration is the next infrastructure fallback. OCR, device/memory/activity diagnostics, and logcat remain available. Eight emulator-free tests pass locally and in run-23 Actions. Runs 21–22 yielded no calculator cases; Google comparison remains unavailable.

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
- **2026-10-26 — QA:** Run `40270102374` (job `121400854300`) passed all six harness unit tests, booted API 34 ATD, and installed the exact APK after an installation retry. Standard UIAutomator recovered a valid hierarchy and exposed the system-process ANR. Three “Wait” attempts did not clear it, so no calculator case or Google package scan ran; artifact download failed with EOF.
- **2026-10-26 — QA:** Run `40272601441` (job `121408458329`) passed eight harness unit tests. The one-time reboot recovery restored navigation after a persistent system ANR, and calculator test cases ran. TC-CALC-001–004 passed; TC-CALC-008 failed after the verified `×3` continuation with a non-1 result. TC-CALC-005/006/009 had equals/zero-input errors. No visible TC-CALC-007/010 or aggregate summary was emitted, and the 47.8 KB evidence artifact failed to download.

### QA-004 — Keypad targeting, equals commitment, and test isolation (harness defect)

| Field | Assessment |
|---|---|
| **Type** | E2E automation reliability / state isolation |
| **Status** | Eight harness checks passed in run 23 Actions, and the emulator reached test cases after ANR recovery. TC-CALC-008's verified continuation exposed the product issue tracked in CALC-001; zero-key/equals failures in TC-CALC-005/006/009 still block their intended assertions |
| **Evidence** | Runs `40252777933`/`40257359718`: `sin(30)` arrived as `sin(3)`, TC-CALC-007 lacked a verified commit, and run 20 TC-CALC-008 never showed `×3`. Run `40272601441`: TC-CALC-005 still showed an uncommitted expression, TC-CALC-006/009 zero taps did not register, while TC-CALC-008 verified the continuation and failed to return `1`. |
| **Product defect?** | TC-CALC-008 is now confirmed and tracked as CALC-001. TC-CALC-005/006/009 remain input/commit errors, not confirmed arithmetic defects; TC-CALC-007 persistence remains unknown. |

**Cause hypothesis:** Run 19's duplicate-label selection and 0.18-second tap settling likely contributed to missed zero taps; the keypad-region filter and longer delay corrected the decimal expression in run 20, but did not fully solve zero delivery on the scientific panel. The harness also lacked per-zero feedback, reset panel state between basic/scientific cases, and treated `= result` previews as committed results. The History cleanup bug in run 19 was independently confirmed and fixed.

**Changes made:** Restrict keypad labels below 40% of screen height and prefer non-EditText/lower controls; increase tap settling to 0.35 seconds and require later zero taps to change the visible expression; explicitly close the scientific panel before basic flows; assert exact expression before evaluating; reject a result if the original expression remains visible after equals; and confirm `×3`/`+1` continuation text before arithmetic assertions. The history test verifies a committed `1+1 = 2` before force-stop and skips persistence if equals was not committed, while retaining a 1.5-second write-settle and `finally` cleanup. Google package scanning is guarded so failures still produce TC-CALC-010 and a report. Runs 21 and 22 failed before calculator navigation; run 23 reached the Calculator after reboot recovery and exercised the input/commit checks. The standard hierarchy retry and one-time reboot recovery both worked. Eight `unittest` checks covering targeting, zero feedback, expression matching, History cleanup, package scanning, hierarchy recovery, and ANR recovery passed locally and in run 23 Actions. TC-CALC-008 identified a product defect; the remaining zero/equals errors need focused input-delivery investigation.

**Comment log**

- **2026-10-26 — QA:** Run 19 exposed missed digits and the open-History isolation defect. The first fixes were committed and run 20 verified History cleanup, but scientific zero taps, equals commitment, and chained-input delivery remained uncertain. Runs 21–22 failed before Calculator UI cases; run 22 did verify standard-dump recovery.
- **2026-10-26 — QA:** Run 23's bounded reboot/relaunch recovered from the system ANR and executed UI cases. The regression checks caught uncommitted square root and missed scientific zero taps; the `×3` continuation and equals commitment were verified, revealing CALC-001's non-1 chained result. TC-CALC-007 and TC-CALC-010 annotations were not visible.

### QA-005 — Empty/malformed UI hierarchy with no OCR text on ATD

| Field | Assessment |
|---|---|
| **Type** | Test infrastructure / Android UI inspection |
| **Status** | Mitigated in runs 22–23 — standard UIAutomator recovered valid hierarchy after malformed compressed output; the resulting system ANR is tracked separately in QA-003, where run-23 reboot recovery reached Calculator |
| **Evidence** | [Run `40268619689`](https://github.com/tarungittarun/AIA-/actions/runs/40268619689), job `121396370520`: API 34 Google APIs ATD booted, PackageManager responded, exact APK installed, then hierarchy parsing failed at line 1 column 0 and screenshot OCR returned no visible text |
| **Product defect?** | No — no calculator UI case ran; this is an emulator/UI-inspection infrastructure failure. |

**Observed:** The previous harness selected standard UIAutomator only when the compressed `uiautomator dump` command itself failed. In run 21 the compressed command returned without a command error, but the file read parsed as empty/malformed XML. OCR fallback then found no visible text. The emulator diagnostics were saved; the 27.8 KB evidence artifact failed to download with EOF. Root cause (temporary UIAutomator service failure, incomplete dump, or ATD screenshot behavior) remains unknown.

**Action:** The revised dumper tries compressed, standard, then a second standard dump using separate remote paths, with a short backoff between attempts so UiAutomation can recover. Each output must parse as XML and contain at least one UI node before it is accepted. If all attempts fail, the harness retains device/logcat diagnostics and attempts OCR. The emulator-free regression test simulates an empty compressed file followed by valid standard XML; it passed locally and in Actions. Runs 22 and 23 confirmed the standard retry on the actual emulator. Run 23's bounded reboot recovery then cleared the separate system ANR tracked in QA-003 and reached Calculator.

**Comment log**

- **2026-10-26 — QA:** Run 21 failed before Calculator navigation; no functional result or Google package scan is available. Standard-dump recovery was added for run 22.
- **2026-10-26 — QA:** Run 22's standard retry successfully recovered a valid hierarchy after the compressed dump failed validation. It exposed the ANR dialog instead of a blank screen; three “Wait” attempts did not recover the system.
- **2026-10-26 — QA:** Run 23 again recovered a valid hierarchy through the standard retry, then rebooted once and reached Calculator. The hierarchy-recovery finding is mitigated; see QA-003 for the system-ANR recovery.

## 5. Functional test matrix

The harness is `qa/calculator_e2e.py`. Runs 19, 20, and 23 reached calculator UI cases on Android 14 Google APIs ATD. Run 20's result notices showed TC-CALC-001–005, but TC-CALC-006 (`sin(3)`), TC-CALC-007's uncommitted `= 2` preview, TC-CALC-008 without a visible `×3`, and TC-CALC-009 (`1^15`) were inconclusive/input failures. Run 23 passed TC-CALC-001–004; TC-CALC-005/006/009 still hit equals/zero delivery guards; TC-CALC-008 failed after verified continuation and committed equals, confirming CALC-001. Run 23 emitted no visible TC-CALC-007, TC-CALC-010, or aggregate-summary annotation. Runs 21–22 did not reach calculator cases; run 22 verified hierarchy recovery, while run 23 recovered from the persistent system ANR through a bounded reboot. Evidence artifacts for runs 19–23 all failed to download with EOF. Eight harness regression tests passed locally and in run-23 Actions. No direct Google Calculator comparison is established.

| Test ID | Scenario | Expected result | Current status |
|---|---|---|---|
| TC-CALC-001 | Operator precedence: `2 + 3 × 4` | `14` | **PASS (runs 20, 23):** both runs displayed `14`; run 20 also recorded the result in History. |
| TC-CALC-002 | Parentheses: `(2 + 3) × 4` | `20` | **PASS (runs 20, 23):** both runs displayed `20`; run 20 also recorded the result in History. |
| TC-CALC-003 | Decimal addition: `0.1 + 0.2` | `0.3` | **PASS (runs 20, 23):** both runs displayed `0.3`; run 20 History recorded the exact input `0.1+0.2 → 0.3`. |
| TC-CALC-004 | Contextual percentage: `200 + 10%` | `220` | **PASS (runs 20, 23):** both runs displayed `220`; run 20 also recorded the result in History. |
| TC-CALC-005 | Scientific square root: `√(9)` | `3` | **ERROR (run 23):** after `=`, the expression remained visible, so the commit guard rejected the `√(9)` / `= 3` preview. Run 20 had the same provisional display. A completed square-root calculation is not verified; no arithmetic defect is claimed. |
| TC-CALC-006 | Degree-mode sine: `sin(30)` | `0.5` | **ERROR (run 23):** after the zero tap, the display remained `sin(3`; the intended `sin(30)` expression was not entered and no trig assertion ran. Input-delivery failure, not a confirmed sine defect. |
| TC-CALC-007 | History persists after process restart and restores an entry | Committed `1+1 = 2` visible/selectable after restart | **Inconclusive:** run 20 showed an uncommitted preview before restart; run 23 emitted no visible TC-CALC-007 annotation. Persistence is not established. See CALC-003. |
| TC-CALC-008 | Chaining: `1 ÷ 3 = × 3 =` | `1` | **FAIL (run 23):** the harness verified `1÷3`, committed the first result, saw the `×3` continuation, and committed the second equals, but the result was not `1`. The first displayed result was `0.3333333333`; exact final text unavailable because the artifact download failed. Confirmed in CALC-001. |
| TC-CALC-009 | Scientific result continuation: `10^15 = + 1 =` | Continues without parser/validator error | **ERROR (run 23):** zero-key feedback guard saw only `1` / `= 1`; `10^15` was not entered, so scientific-notation parsing/continuation was not tested. Linked to CALC-002; no runtime defect claim. |
| TC-CALC-010 | Live official Google Calculator comparison | Common precedence case run in `com.google.android.calculator` | **Unknown:** runs 20 and 23 emitted no visible TC-CALC-010 result; runs 21–22 failed before package scanning. Artifact downloads failed with EOF. No direct comparison or parity claim. |

The workflow saves screenshots plus UI hierarchy or synthetic OCR evidence under the artifact's `evidence/` directory. On a UIAutomator failure it also captures device activity, memory, and recent logcat diagnostics. The ATD image may limit screenshots; UIAutomator remains the primary evidence path. The workflow fails on MySpace functional `FAIL`/`ERROR` results; blocked Google-reference availability is separately reported.

## 6. CI evidence and limitations

- **Existing upstream result:** [TicTic Android CI run 40201068395](https://github.com/tarungittarun/TicTic/actions/runs/40201068395), commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`, concluded success. Its source-contract and Android build/unit-test steps are evidence of source-level CI health only, not APK runtime behavior.
- **New workflow:** `.github/workflows/calculator-apk-e2e.yml` checks out TicTic at pinned commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9` with a sparse checkout for the exact APK, verifies SHA-256 and ZIP integrity, unit-tests the QA harness, then runs calculator-only UI tests on `ubuntu-24.04` using an API 34 `google_atd;x86_64` emulator. Runs 19, 20, and 23 reached calculator cases; run 23 took 43m43s and passed the eight-test unit step. Run 21 failed on malformed/empty hierarchy plus no OCR text. Run 22 verified standard hierarchy recovery but hit a system-process ANR; run 23's bounded reboot recovered navigation. TC-CALC-001–004 passed again in run 23 and TC-CALC-008 confirmed the chained-precision defect; TC-CALC-005/006/009 remained input/commit errors. No visible TC-CALC-007/010 or aggregate summary was emitted. Evidence artifacts for runs 19–23 all failed to download with EOF. Runs 21–22 produced no functional calculator case.
- **Local execution limitation:** The review sandbox did not have Android SDK/ADB/emulator tooling or KVM, so no local device E2E was possible. GitHub Actions is the execution target.
- **Google comparator limitation:** The API 34 `google_atd` image provides Google APIs but not the Play Store; Google Calculator availability is not assumed. The workflow checks for the exact `com.google.android.calculator` package and will not silently substitute a non-Google app. Runs 20 and 23 emitted no visible TC-CALC-010/summary annotation; runs 21–22 failed before scanning, and the run-23 artifact failed to download. The package/comparator outcome remains unknown; no live comparison is claimed.
- **No false pass claim:** This report separates static analysis, expected-value assertions, actual emulator results, and live Google comparison. Only the latter two can establish runtime observations.

## 7. References

1. [Official Google Calculator Play listing](https://play.google.com/store/apps/details?id=com.google.android.calculator&hl=en) — feature reference only; not a live comparison in this report.
2. TicTic calculator implementation and tests at source commit `76f03909ea8bd11c9c4fed83c8e3d7279e3fc9c9`: `feature-calculator/src/main/java/app/space/feature/calculator/CalculatorRules.java`, `CalculatorScreen.java`, and `feature-calculator/src/test/java/app/space/feature/calculator/CalculatorRulesTest.java`.
3. TicTic app inventory note `APPS.md` — reports a prior v3.12.0 feature comparison; not independently reproduced here.
4. [Android Developers: scalable automated testing and ATD images](https://android-developers.googleblog.com/2021/10/whats-new-in-scalable-automated-testing.html) — describes ATD as a leaner system image that removes non-test apps/services and reduces CPU/memory load; screenshot behavior can be limited when hardware rendering is disabled.
