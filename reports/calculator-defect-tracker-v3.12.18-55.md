# MySpace Calculator v3.12.18 (55) — Defect Tracker & E2E QA

**Report ID:** `CALC-QA-2026-10-26-02`  
**Prepared:** 26 October 2026 (Asia/Kolkata)  
**Status:** **Partial; no release pass.** The ten-job Actions matrix completed with an overall failure. TC-CALC-001, 003, and 004 passed; TC-CALC-008 exposed a calculator result discrepancy; TC-CALC-002, 005, 006, and 009 were blocked by Android emulator/system-UI failures; TC-CALC-007 is inconclusive because the harness missed a visibly present history result; and the official Google Calculator comparison was blocked because its package was not installed. TC-CALC-010's MySpace baseline passed.

**Scope:** Calculator feature only. Other MySpace/TicTic features are out of scope.

## 1. Artifact and source pin

| Field | Value |
|---|---|
| Supplied APK | [`MySpace-v3.12.18-55-lite-dist.apk`](https://github.com/tarungittarun/TicTic/raw/arena/3caca636-tictic/artifacts/MySpace-v3.12.18-55-lite-dist.apk) |
| Source branch | `arena/3caca636-tictic` |
| Immutable source commit | `ca8ab165ef155a367b9959a3c9cd7f4be21f891a` |
| APK size | 2,088,900 bytes |
| Git blob SHA-1 | `856d79640fec2f12d4189177046cd81b2560e999` |
| APK SHA-256 | `cd56a2b654dbe7d3a54c4dd291a06e2ec9d7150b6c399a89f93591b167d6e4e8` |
| APK archive integrity | PASS — local ZIP test found no corrupt entry |
| Application ID | `app.space.one` (source Gradle configuration) |
| Version | `3.12.18` / version code `55` (source Gradle configuration) |

The Actions workflow checked out the immutable source commit, verified the exact APK SHA-256 and ZIP integrity, and attempted to install that APK in each emulator job. The APK itself is not copied into this repository.

## 2. Execution record

- **Workflow:** [Calculator APK v3.12.18 (55) E2E QA](https://github.com/tarungittarun/AIA-/actions/runs/40279185593)
- **Actions run ID / run number:** `40279185593` / `24`
- **Commit tested:** `f1b13c43425828f0f1ade660e23ab9103baf6b4f`
- **Conclusion:** `failure` — four jobs completed successfully and six ended unsuccessfully. Some failing jobs represent emulator setup/navigation failures, one is a harness assertion issue, and TC-CALC-008 is a calculator result failure; the run is not an overall calculator release pass.
- **Matrix:** 10 isolated Android 14 Google APIs ATD jobs, `max-parallel: 10`, `fail-fast: false`; TC-CALC-010 also ran TC-CALC-001 as the MySpace baseline.
- **Runner constraint:** The jobs reported `KVM unavailable; using software acceleration`. System-process ANRs and UI-hierarchy failures prevented several calculator cases from reaching their assertions.
- The local nine-test harness suite passed before the run and in each job. Harness/unit success is not APK functional success.

### Test plan

| Matrix job | Test |
|---|---|
| `TC-CALC-001` | Operator precedence: `2 + 3 × 4` → `14` |
| `TC-CALC-002` | Parentheses: `(2 + 3) × 4` → `20` |
| `TC-CALC-003` | Decimal addition: `0.1 + 0.2` → `0.3` |
| `TC-CALC-004` | Contextual percentage: `200 + 10%` → `220` |
| `TC-CALC-005` | Scientific square root: `√(9)` → `3` |
| `TC-CALC-006` | Degree-mode sine: `sin(30)` → `0.5` |
| `TC-CALC-007` | History survives process restart and restores a committed entry |
| `TC-CALC-008` | Chaining: `1 ÷ 3 = × 3 =` → `1` |
| `TC-CALC-009` | Continue from `10^15` with `+ 1` without parser/validator error |
| `TC-CALC-010` | Compare the same expression with official `com.google.android.calculator` |

## 3. Result tracker

| Test ID | Expected | Status | Evidence and QA comment |
|---|---|---|---|
| TC-CALC-001 | `14` | **PASS** | Observed `14`; GitHub annotation says the visible result matched. [Job](https://github.com/tarungittarun/AIA-/actions/runs/40279185593/job/121428450242) |
| TC-CALC-002 | `20` | **BLOCKED — emulator** | APK installation and API 34 boot succeeded, but Android became unresponsive. After Wait retries, Monkey failed with `Unable to connect to activity manager`; the parentheses calculation was not reached. [Job](https://github.com/tarungittarun/AIA-/actions/runs/40279185593/job/121428450256) |
| TC-CALC-003 | `0.3` | **PASS** | Observed `0.3`; GitHub annotation says the visible result matched. [Job](https://github.com/tarungittarun/AIA-/actions/runs/40279185593/job/121428450254) |
| TC-CALC-004 | `220` | **PASS** | Observed `220`; GitHub annotation says the visible result matched. [Job](https://github.com/tarungittarun/AIA-/actions/runs/40279185593/job/121428450170) |
| TC-CALC-005 | `3`, visibly committed | **BLOCKED — UI automation** | The emulator showed system-ANR symptoms; hierarchy dumps were malformed and screenshot OCR returned no visible text. No square-root assertion ran. [Job](https://github.com/tarungittarun/AIA-/actions/runs/40279185593/job/121428450483) |
| TC-CALC-006 | `0.5` | **BLOCKED — emulator** | The calculator screen was not reached. The final visible labels were `Process system isn't responding`, `Close app`, and `Wait`; no sine input or result assertion ran. [Job](https://github.com/tarungittarun/AIA-/actions/runs/40279185593/job/121428450307) |
| TC-CALC-007 | Persisted `1+1 = 2` is visible and restores after restart | **INCONCLUSIVE — harness assertion** | After process restart, History visibly contained `1+1` and `= 2`. The harness required a separate label exactly equal to `2`, so it incorrectly marked the entry absent; it never tapped the entry to verify restoration. This is not evidence of an app history defect. [Job](https://github.com/tarungittarun/AIA-/actions/runs/40279185593/job/121428450282) |
| TC-CALC-008 | `1` | **FAIL — calculator result discrepancy** | Preconditions passed: `1 ÷ 3` was committed and displayed as `0.3333333333`; `×3` was visibly entered and the second equals committed. The visible final result was `0.9999999999`, not `1`. The result is consistent with rounded display text being reused as the next operand, but that root cause is not confirmed. [Job](https://github.com/tarungittarun/AIA-/actions/runs/40279185593/job/121428449922) |
| TC-CALC-009 | Valid continuation from `1e+15` | **BLOCKED — UI automation** | After ANR recovery/reboot, repeated UIAutomator dumps were malformed and OCR returned no visible text. The exponent continuation assertion did not run. [Job](https://github.com/tarungittarun/AIA-/actions/runs/40279185593/job/121428450391) |
| TC-CALC-010 | Same expression agrees with official Google Calculator | **BLOCKED — reference not installed** | The MySpace baseline TC-CALC-001 passed with `14`. The emulator did not contain `com.google.android.calculator`, so no live official-app comparison was performed. No AOSP substitute or third-party APK mirror was used. [Job](https://github.com/tarungittarun/AIA-/actions/runs/40279185593/job/121428450283) |

## 4. Defect and follow-up records

### DEF-CALC-001 — Chained calculation loses precision after `1 ÷ 3`

- **Status:** Open — developer investigation required
- **Proposed severity / priority:** Major / High (core calculator result correctness)
- **Affected release:** MySpace Calculator `3.12.18`, version code `55`
- **Test:** TC-CALC-008, Actions run `40279185593`, job `121428449922`
- **Reproduction:** Enter `1 ÷ 3`, press equals, enter `× 3`, and press equals again.
- **Expected:** `1`
- **Observed:** First committed display `0.3333333333`; final committed display `0.9999999999`.
- **Validity checks:** The input expression, first committed result, `×3` continuation, and second committed result were checked by the harness before the failure was recorded.
- **Comment:** This is an observed arithmetic discrepancy. Reusing a rounded display string as an operand is a plausible explanation, not a verified root cause. Reproduce on a stable/KVM-capable device and inspect the calculator's internal value/formatting boundary.

### QA-HARNESS-001 — TC-CALC-007 history result-label matcher is too strict

- **Status:** Harness correction and retest required; not an application defect
- **Evidence:** After restart, the test saw `History · 1`, `1+1`, and `= 2`. The predicate searched for a label exactly equal to `2`, rejected the visible `= 2` form, and skipped the history-item restore check.
- **Comment:** Update the matcher to accept the rendered equals/result row, then rerun TC-CALC-007. The run provides evidence that the history entry persisted, but it does not prove that tapping the entry restores its expression.

### CI-ENV-001 — Emulator system ANR blocks calculator navigation/UI inspection

- **Status:** Environment limitation observed in this run; targeted rerun recommended
- **Evidence:** TC-CALC-002, 005, 006, and 009 could not reach their functional assertions. The jobs reported software acceleration because KVM was unavailable; failures included ActivityManager disconnection, persistent system ANR, malformed UIAutomator output, and empty OCR output.
- **Comment:** Rerun the blocked cases on a KVM-capable Android runner or with lower concurrent emulator load. Do not record these blocked cases as application passes or functional failures.

## 5. Official Google Calculator comparison

TC-CALC-010 attempted to locate the exact official package `com.google.android.calculator` in the emulator. The package was not installed, so the live comparison was blocked. The MySpace baseline expression still returned `14`. No AOSP `com.android.calculator2` app or third-party APK mirror was treated as equivalent to the current official Google Calculator. **Google parity remains unknown.**

## 6. CI evidence and comments

**Workflow:** `.github/workflows/calculator-apk-e2e.yml` — immutable source checkout, exact APK SHA-256/ZIP verification, API 34 `google_atd;x86_64`, ten isolated calculator matrix jobs, and per-job evidence upload.

**Actions evidence:** [Run 40279185593](https://github.com/tarungittarun/AIA-/actions/runs/40279185593). The test outcome notes above are from the individual GitHub check-run annotations. The artifact upload steps completed, but downloading the TC-CALC-002 artifact from this sandbox returned EOF; screenshots were therefore not reviewed locally and no evidence beyond the check annotations is claimed here.

**Local validation:** Nine emulator-free harness tests passed; Python compilation, shell syntax validation, and `git diff --check` passed. Those checks validate the harness/configuration, not APK runtime behavior.

**Comment log**

- **2026-10-26 — QA:** Pinned the supplied APK to source commit `ca8ab165ef155a367b9959a3c9cd7f4be21f891a`; verified SHA-256 `cd56a2b654dbe7d3a54c4dd291a06e2ec9d7150b6c399a89f93591b167d6e4e8` and ZIP integrity.
- **2026-10-26 — QA:** Pushed harness/workflow commit `f1b13c4`; Actions run `40279185593` executed all ten calculator test IDs in parallel, within the 40-job ceiling.
- **2026-10-26 — QA:** TC-CALC-001, 003, and 004 passed. The TC-CALC-010 MySpace baseline also returned `14`, but the official Google package was absent; no Google parity claim is made.
- **2026-10-26 — QA:** TC-CALC-008 recorded a validated chained result discrepancy (`0.9999999999` instead of `1`); opened report record `DEF-CALC-001` for investigation.
- **2026-10-26 — QA:** TC-CALC-002, 005, 006, and 009 were blocked by Android emulator/system-UI failures. TC-CALC-007's failure is an assertion mismatch because the persisted `= 2` row was visible; the restore action remains unverified.
- **2026-10-26 — QA:** Overall matrix conclusion is failure/partial. No release pass is claimed. Recommend retesting blocked cases on a stable runner and correcting the TC-CALC-007 matcher before that retest.
