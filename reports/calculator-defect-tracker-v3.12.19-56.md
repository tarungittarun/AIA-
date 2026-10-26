# MySpace Calculator v3.12.19 (56) — Defect Tracker & E2E QA

**Report ID:** `CALC-QA-2026-10-26-03`  
**Prepared:** 26 October 2026 (Asia/Kolkata)  
**Status:** **Matrix complete; no release pass.** All 20 jobs finished: 13 succeeded and 7 failed. TC-CALC-002, 003, 004, and 005 passed in both replicas. TC-CALC-008 failed with the same result discrepancy in both replicas. TC-CALC-001, 006, and 007 passed in one replica but were blocked by emulator/UI failures in the other; TC-CALC-009 was blocked in both. TC-CALC-010's MySpace baseline passed twice, but the official Google comparison was blocked because its package was not installed.

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

All 20 Actions jobs verified the exact SHA-256 and ZIP integrity before attempting installation. The APK itself is not copied into this repository.

## 2. Execution record

- **Workflow:** [Calculator APK v3.12.19 (56) E2E QA](https://github.com/tarungittarun/AIA-/actions/runs/40284113631)
- **Actions run ID / run number:** `40284113631` / `25`
- **Commit tested:** `6853af2331e3f18d4d5d08c361ba3bc816da94bd`
- **Conclusion:** `failure`; 13 job checks succeeded and 7 failed. The failures consist of two repeatable calculator result failures (TC-CALC-008) and five emulator/UI-automation blocks. A successful job can still contain a BLOCKED Google comparison; job success is not an overall release pass.
- **Matrix:** 20 independent jobs — ten calculator test IDs × two fresh-emulator replicas; `max-parallel: 20`, `fail-fast: false`.
- **Runner constraint:** All 20 jobs reported `KVM unavailable; using software acceleration`. System-process ANRs and UIAutomator/OCR failures blocked several replica assertions.
- **Harness validation:** The ten-test emulator-free harness suite passed in every job. This validates the harness, not the APK's functional behavior.

## 3. Replica result tracker

| Test ID | Expected | Replica 1 | Replica 2 | Evidence and comments |
|---|---|---|---|---|
| TC-CALC-001 | `14` | **BLOCKED** | **PASS** | Replica 1: malformed UIAutomator XML and OCR returned no visible text; no assertion ran. Replica 2: observed `14`. [R1](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672556) · [R2](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672775) |
| TC-CALC-002 | `20` | **PASS** | **PASS** | Both replicas observed `20`. [R1](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672697) · [R2](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672488) |
| TC-CALC-003 | `0.3` | **PASS** | **PASS** | Both replicas observed `0.3`. [R1](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672298) · [R2](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672613) |
| TC-CALC-004 | `220` | **PASS** | **PASS** | Both replicas observed `220`. [R1](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672603) · [R2](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672549) |
| TC-CALC-005 | `3`, visibly committed | **PASS** | **PASS** | Both replicas observed committed result `3`. [R1](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672661) · [R2](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672949) |
| TC-CALC-006 | `0.5` | **PASS** | **BLOCKED** | Replica 1 observed `0.5`. Replica 2's UIAutomator hierarchy was malformed and OCR returned no visible text; no sine assertion ran. [R1](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672739) · [R2](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672554) |
| TC-CALC-007 | Persisted `1+1 = 2` restores after restart | **PASS** | **BLOCKED** | Replica 1 displayed the persisted `1+1` / `= 2` entry after restart and restored `1+1` when selected. Replica 2 failed in UIAutomator/OCR before the assertion. The corrected history matcher worked in the passing replica. [R1](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672584) · [R2](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672659) |
| TC-CALC-008 | `1` | **FAIL** | **FAIL** | Both replicas validated `1 ÷ 3 =`, the visible `×3` continuation, and the second equals commit. Both showed first result `0.3333333333` and final result `0.9999999999`, not `1`. [R1](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672611) · [R2](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672531) |
| TC-CALC-009 | Valid continuation from `1e+15` | **BLOCKED** | **BLOCKED** | Both replicas remained on `Process system isn't responding` / `Close app` / `Wait`; calculator navigation and the exponent assertion were not reached. [R1](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672504) · [R2](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672815) |
| TC-CALC-010 | Live parity with official Google Calculator | **BLOCKED** | **BLOCKED** | In both replicas the MySpace TC-CALC-001 baseline observed `14`; `com.google.android.calculator` was absent, so no side-by-side official-app comparison ran. No AOSP substitute or third-party APK mirror was used. [R1](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672696) · [R2](https://github.com/tarungittarun/AIA-/actions/runs/40284113631/job/121443672548) |

## 4. Defect and follow-up records

### DEF-CALC-001 — Chained calculation loses precision after `1 ÷ 3`

- **Status:** Open — developer investigation required
- **Proposed severity / priority:** Major / High (core calculator result correctness)
- **Affected release:** MySpace Calculator `3.12.19`, version code `56`; the same discrepancy was observed on `3.12.18` / code `55`
- **Reproduction:** Enter `1 ÷ 3`, press equals, enter `× 3`, and press equals again.
- **Expected:** `1`
- **Observed:** Both independent replicas displayed first committed result `0.3333333333` and final committed result `0.9999999999`.
- **Validity checks:** The full input expression, first commit, `×3` continuation, and second commit were visibly checked before both failures were recorded.
- **Comment:** The v3.12.19-56 replicas reproduce the v3.12.18-55 discrepancy, supporting that it persists across these releases. Reusing rounded display text as the next operand is plausible but not a verified root cause. Inspect the internal numeric value/formatting boundary.

### CI-ENV-001 — Software-emulated Android system/UI failures

- **Status:** Environment limitation observed; five matrix jobs were blocked before functional assertions
- **Evidence:** TC-CALC-001 replica 1, TC-CALC-006 replica 2, and TC-CALC-007 replica 2 failed UIAutomator/OCR inspection; both TC-CALC-009 replicas remained on a system-process ANR screen. Every job reported KVM unavailable/software acceleration.
- **Comment:** These outcomes are blocked, not calculator functional failures. A stable or KVM-capable runner is recommended for rerunning these replicas.

### QA-HARNESS-001 — TC-CALC-007 history result-label matcher

- **Status:** Corrected and validated in one runtime replica; second replica blocked by the emulator
- **Evidence:** Replica 1 accepted the rendered `= 2` history row, selected the stored entry, and observed restored expression `1+1`. Emulator-free regression coverage verifies accepted and rejected result-label forms.
- **Comment:** The prior-release false-negative is fixed in the QA harness; it is not an application defect in this run.

## 5. Official Google Calculator comparison

Both TC-CALC-010 jobs checked for the exact official package `com.google.android.calculator`. It was not installed in either Android 14 ATD image, so the requested live comparison remains blocked. The MySpace baseline passed with `14` in both jobs. No AOSP `com.android.calculator2` app or third-party APK mirror was treated as equivalent to the current official app. **Google parity remains unknown.**

## 6. CI evidence and comments

**Workflow:** `.github/workflows/calculator-apk-e2e.yml` — exact source/APK pin, SHA-256 and ZIP verification, API 34 `google_atd;x86_64`, 20 independent jobs, and per-replica evidence artifacts.

**Actions evidence:** [Run 40284113631](https://github.com/tarungittarun/AIA-/actions/runs/40284113631). All 20 APK-verification steps and all 20 harness unit-test steps succeeded. Runtime findings above are based on individual GitHub check-run annotations; every job completed its artifact-upload step.

**Local validation:** Ten emulator-free harness tests passed, including the TC-CALC-007 matcher regression. Python compilation, shell syntax validation, and `git diff --check` passed. These checks validate the harness/configuration, not APK runtime behavior.

**Comment log**

- **2026-10-26 — QA:** Pinned v3.12.19-56 to upstream commit `c083d6ff68572e6d3b9be854d5eb0d0c59e91e23`; verified APK SHA-256 `bcdd1de4606348d1e318452002f9f9a4c28bc464af1fabeb9941ee22891da02a` and ZIP integrity.
- **2026-10-26 — QA:** Configured 20 jobs as two isolated replicas of each of the ten calculator cases; all 20 jobs completed and verified the pinned APK.
- **2026-10-26 — QA:** TC-CALC-002, 003, 004, and 005 passed in both replicas. TC-CALC-008 failed with the same validated result discrepancy in both replicas.
- **2026-10-26 — QA:** The corrected TC-CALC-007 test passed once, confirming visible history persistence and expression restoration. Its other replica was blocked by UI automation failure.
- **2026-10-26 — QA:** TC-CALC-001 and TC-CALC-006 each passed once and had one emulator-blocked replica; TC-CALC-009 was blocked in both replicas. Official Google comparison was attempted twice but the exact package was absent.
- **2026-10-26 — QA:** Overall Actions result is failure/partial. No release pass or Google Calculator parity claim is made.
