# Standalone MyCalc Calculator APK E2E QA Run

- **Generated (UTC):** 2026-10-27T13:17:27+00:00
- **APK:** `MyCalc-v1.0.37-38.apk` (1,317,383 bytes)
- **Package:** `app.space.calc`
- **SHA-256:** `09b1dc8f91ac249643cb92aa74670fdd2db8430af6c0b8c7052d8e906efcf1d4`
- **Device:** Android API 34 emulator, 320x640
- **UI inspection:** uiautomator-compressed
- **Scope:** Calculator feature only
- **Google reference:** NOT_CHECKED — 

## Result summary

| Status | Count |
|---|---:|
| PASS | 6 |
| FAIL | 5 |
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
| TC-CALC-007 | History persists after activity restart and can restore an expression | **FAIL** | History shows 1+1 = 2 after restart | The expected entry was not found after restart. Before restart the display was ['MyCalc', 'STANDALONE', '2']; visible history labels were ['History · 7', 'Clear', 'Close history', '= 3', '200+10%', '27th Oct, 13:14', '= 220', '0.1+0.2', '= 0.3', '(2+3)×4', '= 20', '2+3×4', '27th Oct, 13:13', '= 14'].
| TC-CALC-011 | Grouped history card restores and re-evaluates without Error | **FAIL** | History contains the 123456+1 calculation card | The calculation card was not found in the visible history labels.
| TC-CALC-008 | Chained calculations retain unrounded precision | **FAIL** | 1 | After 1 ÷ 3 =, the UI result was ['MyCalc', 'STANDALONE', '0.3333333333']; multiplying by 3 did not return 1. This is consistent with the screen feeding its rounded display string back into the next expression.
| TC-CALC-009 | Scientific-notation result can be used in the next expression | **FAIL** | Continue from 1e+15 without Error | Initial 10^15 display was ['MyCalc', 'STANDALONE', '1e+15']; adding +1 left an unchanged exponent result or produced Error. This is consistent with exponent-formatted display text not being accepted as a numeric literal by the expression validator/parser.

Screenshots and UI hierarchy or OCR evidence are in the adjacent `evidence/` folder.
A BLOCKED Google comparison is not treated as a calculator functional pass.
