# MySpace Calculator v3.12.18 (55) — Defect Tracker & E2E QA

**Report ID:** `CALC-QA-2026-10-26-02`  
**Prepared:** 26 October 2026 (Asia/Kolkata)  
**Status:** APK identity and local regression checks verified; ten calculator-only Actions jobs are queued to run in parallel. No runtime result or Google Calculator parity claim yet.  
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

The Actions workflow checks out the immutable source commit, verifies the exact APK SHA-256 and ZIP integrity, then installs that APK. The APK itself is not copied into this repository.

## 2. Parallel execution plan

The request allowed up to 40 jobs. The workflow uses **10 independent matrix jobs**, one for each calculator test ID, with `max-parallel: 10` and `fail-fast: false`. Each job gets its own fresh Android 14 Google APIs ATD emulator, installs the same hash-pinned APK, runs one test case, and uploads uniquely named evidence. This avoids cross-case History/keypad contamination and lets failures be collected independently. TC-CALC-010 also runs TC-CALC-001 as its MySpace baseline before attempting the exact Google Calculator package comparison.

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
| `TC-CALC-010` | Live comparison with `com.google.android.calculator` |

Jobs run with the same API 34 ATD setup and the bounded ANR reboot recovery validated on the previous APK. Each matrix job emits its own GitHub test annotations and artifact; artifact downloads have previously returned EOF in this environment, so the check annotations are also retained as test evidence.

## 3. Result tracker

| Test ID | Expected | Status | Evidence / comments |
|---|---|---|---|
| TC-CALC-001 | `14` | **PENDING** | Isolated matrix job. |
| TC-CALC-002 | `20` | **PENDING** | Isolated matrix job. |
| TC-CALC-003 | `0.3` | **PENDING** | Isolated matrix job; exact input is checked before equals. |
| TC-CALC-004 | `220` | **PENDING** | Isolated matrix job. |
| TC-CALC-005 | `3`, visibly committed | **PENDING** | Preview-only equals is not counted as a pass. |
| TC-CALC-006 | `0.5` | **PENDING** | Input guard must see the full `sin(30)` expression before evaluation. |
| TC-CALC-007 | Committed `1+1 = 2` persists and restores after process restart | **PENDING** | Persistence is skipped if equals does not visibly commit. |
| TC-CALC-008 | `1` | **PENDING** | The `×3` continuation and second equals must be visibly verified before classifying arithmetic. |
| TC-CALC-009 | Valid continuation from `1e+15` | **PENDING** | Zero-key and continuation checks gate the parser assertion. |
| TC-CALC-010 | Same precedence case agrees with official Google Calculator | **PENDING** | Requires exact package `com.google.android.calculator`; no AOSP substitute. |

## 4. Interpretation and defect-tracker notes

- The previous APK, v3.12.7-44, had a verified equals-continuation discrepancy on `(1 ÷ 3) × 3` after the `×3` input and second equals were confirmed. This is **historical evidence for v3.12.7 only**. It is not assumed to persist in v3.12.18-55; TC-CALC-008 retests it as a fresh release.
- Missed zero taps and `= result` previews were automation/input validity problems on earlier runs. The new isolated jobs enforce the visible expression and committed-result checks before reporting an app-level arithmetic outcome.
- The Google Calculator comparison remains separate from expected-value checks. A result against arithmetic expectations does not establish Google Calculator parity.
- No unrelated feature or advertisement flow is included in the requested test scope.

## 5. CI evidence and comments

**Workflow:** `.github/workflows/calculator-apk-e2e.yml` — 10-job matrix, API 34 `google_atd;x86_64`, exact-source sparse checkout, SHA-256/ZIP validation, isolated calculator cases, and per-job evidence artifacts.

**Local validation:** Nine emulator-free harness tests passed, including case sharding, Google-baseline selection, UIAutomator fallback, and bounded ANR recovery. Python compilation, shell syntax, and `git diff --check` passed. These checks validate the harness/configuration, not APK runtime behavior.

**Comment log**

- **2026-10-26 — QA:** New release target pinned to source commit `ca8ab165ef155a367b9959a3c9cd7f4be21f891a`. SHA-256 `cd56a2b654dbe7d3a54c4dd291a06e2ec9d7150b6c399a89f93591b167d6e4e8`; ZIP integrity passed.
- **2026-10-26 — QA:** Chose ten parallel jobs (one per TC-CALC ID), within the user's 40-job ceiling. The Google-comparison job also executes TC-CALC-001 as its MySpace baseline.
- **2026-10-26 — QA:** Waiting for the matrix run. Until a job supplies runtime evidence, every case remains pending and no parity or release-pass claim is made.
