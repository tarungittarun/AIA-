# MySpace Calculator v3.12.19 (56) — Defect Tracker & E2E QA

**Report ID:** `CALC-QA-2026-10-26-03`  
**Prepared:** 26 October 2026 (Asia/Kolkata)  
**Status:** Target APK identity and local harness validation passed. A 20-job calculator-only Actions matrix is configured; runtime results and Google Calculator parity are pending.  
**Scope:** Calculator feature only. Other MySpace/TicTic features are out of scope.

## 1. Artifact and source pin

| Field | Value |
|---|---|
| Supplied APK | [`MySpace-v3.12.19-56-lite-dist.apk`](https://github.com/tarungittarun/TicTic/raw/arena/3caca636-tictic/artifacts/MySpace-v3.12.19-56-lite-dist.apk) |
| Source branch | `arena/3caca636-tictic` |
| Immutable source commit | `c083d6ff68572e6d3b9be854d5eb0d0c59e91e23` |
| APK size | 2,089,128 bytes |
| Git blob SHA-1 | `bf19ec94f11acd0b1b231c2e5702d7ec0d5e39c5` |
| APK SHA-256 | `bcdd1de4606348d1e318452002f9f9a4c28bc464af1fabeb9941ee22891da02a` |
| APK archive integrity | PASS — ZIP validation found no corrupt entry (196 entries checked) |
| Application ID | `app.space.one` (source Gradle configuration) |
| Version | `3.12.19` / version code `56` (source Gradle configuration) |

The Actions workflow checks out the immutable source commit, verifies this exact APK SHA-256 and ZIP integrity, then installs the APK. The APK itself is not copied into this repository.

## 2. Execution plan

The workflow uses **20 independent jobs**: two fresh-emulator replicas of each of the ten calculator test IDs. The matrix is `test_case × replica [1, 2]`, with `max-parallel: 20` and `fail-fast: false`. Each job installs the hash-pinned APK, runs only its selected calculator test, and uploads a uniquely named report/evidence artifact. Replica results will be reported separately; one replica's failure will not be hidden by the other.

TC-CALC-010 also runs TC-CALC-001 as the MySpace arithmetic baseline in each replica before checking for the exact official Google package `com.google.android.calculator`. An absent reference package means the live comparison is blocked, not passed; AOSP Calculator is not an equivalent substitute.

| Test ID | Test |
|---|---|
| TC-CALC-001 | Operator precedence: `2 + 3 × 4` → `14` |
| TC-CALC-002 | Parentheses: `(2 + 3) × 4` → `20` |
| TC-CALC-003 | Decimal addition: `0.1 + 0.2` → `0.3` |
| TC-CALC-004 | Contextual percentage: `200 + 10%` → `220` |
| TC-CALC-005 | Scientific square root: `√(9)` → `3` |
| TC-CALC-006 | Degree-mode sine: `sin(30)` → `0.5` |
| TC-CALC-007 | History survives process restart and restores a committed entry |
| TC-CALC-008 | Chaining: `1 ÷ 3 = × 3 =` → `1` |
| TC-CALC-009 | Continue from `10^15` with `+ 1` without parser/validator error |
| TC-CALC-010 | Live comparison with official `com.google.android.calculator` |

## 3. Replica result tracker

All cells remain pending until check-run annotations or uploaded artifacts provide runtime evidence.

| Test ID | Expected | Replica 1 | Replica 2 | Comments |
|---|---|---|---|---|
| TC-CALC-001 | `14` | **PENDING** | **PENDING** | Isolated precedence test. |
| TC-CALC-002 | `20` | **PENDING** | **PENDING** | Exact expression must be visible before equals. |
| TC-CALC-003 | `0.3` | **PENDING** | **PENDING** | Zero taps and full decimal input are checked. |
| TC-CALC-004 | `220` | **PENDING** | **PENDING** | Contextual percentage. |
| TC-CALC-005 | `3`, visibly committed | **PENDING** | **PENDING** | Preview-only equals is not counted as a pass. |
| TC-CALC-006 | `0.5` | **PENDING** | **PENDING** | Full `sin(30)` input is checked before evaluation. |
| TC-CALC-007 | Persisted `1+1 = 2` is visible and restores after restart | **PENDING** | **PENDING** | Harness matcher now accepts a rendered `= 2` row; restoration must still be observed. |
| TC-CALC-008 | `1` | **PENDING** | **PENDING** | Input, first commit, continuation, and second commit are validated before classifying arithmetic. |
| TC-CALC-009 | Valid continuation from `1e+15` | **PENDING** | **PENDING** | Zero-key/input and equals-commit gates apply. |
| TC-CALC-010 | Same expression agrees with official Google Calculator | **PENDING** | **PENDING** | Each replica runs the MySpace baseline and independently checks for `com.google.android.calculator`. |

## 4. Prior-release context and defect-tracker notes

- The v3.12.18-55 run recorded a validated TC-CALC-008 discrepancy: `1 ÷ 3 = × 3 =` displayed `0.9999999999` instead of `1`. That is prior-release evidence only. TC-CALC-008 retests v3.12.19-56 independently in both replicas; no outcome is assumed.
- The v3.12.18-55 TC-CALC-007 run showed a persisted `1+1` / `= 2` history entry, but the harness expected a separate exact `2` label and skipped the restore action. The matcher was corrected to accept an optional equals prefix and zero-only decimal suffix; local unit coverage checks both accepted and rejected label forms. Runtime persistence/restoration remains pending.
- Earlier API 34 ATD jobs reported `KVM unavailable; using software acceleration` and some hit system-process ANRs. This 20-replica run records setup/navigation failures as blocked or inconclusive, never as functional app passes. A test that does not reach its validated assertion is not counted as a calculator result.
- No non-calculator feature or advertisement flow is included in this test scope.

## 5. Official Google Calculator comparison

The comparison target is the current official package `com.google.android.calculator`, not the old AOSP/system calculator. The emulator package scan and live comparison are pending in both TC-CALC-010 replicas. No parity claim will be made unless the exact official package is present and the same expression is exercised in both apps.

## 6. CI evidence and comments

**Workflow:** `.github/workflows/calculator-apk-e2e.yml` — immutable source checkout, exact APK SHA-256/ZIP verification, API 34 `google_atd;x86_64`, 20 isolated calculator jobs, and uniquely named per-replica evidence artifacts.

**Local validation:** Ten emulator-free harness tests passed, including the corrected history-result matcher. Python compilation, shell syntax validation, and `git diff --check` passed. These checks validate the harness/configuration, not APK runtime behavior.

**Comment log**

- **2026-10-26 — QA:** Pinned the supplied v3.12.19-56 APK to source commit `c083d6ff68572e6d3b9be854d5eb0d0c59e91e23`; verified SHA-256 `bcdd1de4606348d1e318452002f9f9a4c28bc464af1fabeb9941ee22891da02a` and ZIP integrity.
- **2026-10-26 — QA:** Configured two independent replicas for each of the ten calculator test IDs: 20 parallel jobs, within the requested job count.
- **2026-10-26 — QA:** Corrected the TC-CALC-007 history-result matcher following the prior release's visible `= 2` row; added emulator-free regression coverage. No runtime result is yet inferred from the harness fix.
- **2026-10-26 — QA:** Awaiting the v3.12.19-56 Actions matrix. All functional outcomes and official Google comparison status remain pending until job evidence is available.
