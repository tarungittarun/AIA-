# MySpace Calculator APK E2E QA Run

- **Generated (UTC):** 2026-10-27T08:46:10+00:00
- **APK:** `MySpace-v3.12.35-72-lite-dist.apk` (2,274,980 bytes)
- **Package:** `app.space.one`
- **SHA-256:** `f3257177dc098cf62f54a6f77df526195323d36b23ed5a69f9ff07ddf96b45fb`
- **Device:** Android API 34 emulator, 320x640
- **UI inspection:** uiautomator-compressed
- **Scope:** Calculator feature only
- **Google reference:** NOT_INSTALLED — The official Google Calculator package was not present in the emulator image. No third-party APK mirror was used. Functional assertions therefore use the documented arithmetic expectations; this is not a live side-by-side Google comparison.

## Result summary

| Status | Count |
|---|---:|
| PASS | 8 |
| FAIL | 2 |
| ERROR | 0 |
| BLOCKED | 1 |

## Test cases

| ID | Test | Status | Expected | Actual / comment |
|---|---|---|---|---|
| TC-CALC-001 | Operator precedence | **PASS** | 14 | Observed result matched the expected calculator value.
| TC-CALC-002 | Parentheses override precedence | **PASS** | 20 | Observed result matched the expected calculator value.
| TC-CALC-003 | Decimal addition | **PASS** | 0.3 | Observed result matched the expected calculator value.
| TC-CALC-004 | Contextual percentage | **PASS** | 220 | Observed result matched the expected calculator value.
| TC-CALC-005 | Square root in scientific panel | **PASS** | 3 | Observed result matched the expected calculator value.
| TC-CALC-006 | Sine in degree mode | **PASS** | 0.5 | Observed result matched the expected calculator value.
| TC-CALC-007 | History persists after activity restart and can restore an expression | **PASS** | History shows 1+1 = 2 and restores the expression | The history entry survived process restart and restored its expression.
| TC-CALC-011 | Grouped history card restores and re-evaluates without Error | **PASS** | History card re-evaluates to 123457 without Error | The grouped expression was restored and evaluated successfully; display commas did not contaminate the calculation.
| TC-CALC-008 | Chained calculations retain unrounded precision | **FAIL** | 1 | After 1 ÷ 3 =, the UI result was ['CALCULATOR', '0.3333333333']; multiplying by 3 did not return 1. This is consistent with the screen feeding its rounded display string back into the next expression.
| TC-CALC-009 | Scientific-notation result can be used in the next expression | **FAIL** | Continue from 1e+15 without Error | Initial 10^15 display was ['CALCULATOR', '1e+15']; adding +1 left an unchanged exponent result or produced Error. This is consistent with exponent-formatted display text not being accepted as a numeric literal by the expression validator/parser.
| TC-CALC-010 | Live comparison with official Google Calculator | **BLOCKED** | Same expressions run in com.google.android.calculator | The official Google Calculator package was not present in the emulator image. No third-party APK mirror was used. Functional assertions therefore use the documented arithmetic expectations; this is not a live side-by-side Google comparison.

Screenshots and UI hierarchy or OCR evidence are in the adjacent `evidence/` folder.
A BLOCKED Google comparison is not treated as a calculator functional pass.
