# Standalone MyCalc Calculator APK E2E QA Run

- **Generated (UTC):** 2026-10-27T09:02:06+00:00
- **APK:** `MyCalc-v1.0.33-34.apk` (1,311,395 bytes)
- **Package:** `app.space.calc`
- **SHA-256:** `99c65435e455e241dd3eb65ea6494abcabf2099f5024f6a82c6cf8a621a6bf6b`
- **Device:** Android API 34 emulator, 320x640
- **UI inspection:** uiautomator-compressed
- **Scope:** Calculator feature only
- **Google reference:** NOT_CHECKED — 

## Result summary

| Status | Count |
|---|---:|
| PASS | 8 |
| FAIL | 3 |
| ERROR | 0 |
| BLOCKED | 0 |

## Test cases

| ID | Test | Status | Expected | Actual / comment |
|---|---|---|---|---|
| TC-CALC-012 | Standalone MyCalc requests no Android permissions | **FAIL** | No requested Android permissions | The installed standalone package requests one or more Android permissions.
| TC-CALC-001 | Operator precedence | **PASS** | 14 | Observed result matched the expected calculator value.
| TC-CALC-002 | Parentheses override precedence | **PASS** | 20 | Observed result matched the expected calculator value.
| TC-CALC-003 | Decimal addition | **PASS** | 0.3 | Observed result matched the expected calculator value.
| TC-CALC-004 | Contextual percentage | **PASS** | 220 | Observed result matched the expected calculator value.
| TC-CALC-005 | Square root in scientific panel | **PASS** | 3 | Observed result matched the expected calculator value.
| TC-CALC-006 | Sine in degree mode | **PASS** | 0.5 | Observed result matched the expected calculator value.
| TC-CALC-007 | History persists after activity restart and can restore an expression | **PASS** | History shows 1+1 = 2 and restores the expression | The history entry survived process restart and restored its expression.
| TC-CALC-011 | Grouped history card restores and re-evaluates without Error | **PASS** | History card re-evaluates to 123457 without Error | The grouped expression was restored and evaluated successfully; display commas did not contaminate the calculation.
| TC-CALC-008 | Chained calculations retain unrounded precision | **FAIL** | 1 | After 1 ÷ 3 =, the UI result was ['MyCalc', 'STANDALONE', '0.3333333333']; multiplying by 3 did not return 1. This is consistent with the screen feeding its rounded display string back into the next expression.
| TC-CALC-009 | Scientific-notation result can be used in the next expression | **FAIL** | Continue from 1e+15 without Error | Initial 10^15 display was ['MyCalc', 'STANDALONE', '1e+15']; adding +1 left an unchanged exponent result or produced Error. This is consistent with exponent-formatted display text not being accepted as a numeric literal by the expression validator/parser.

Screenshots and UI hierarchy or OCR evidence are in the adjacent `evidence/` folder.
A BLOCKED Google comparison is not treated as a calculator functional pass.
