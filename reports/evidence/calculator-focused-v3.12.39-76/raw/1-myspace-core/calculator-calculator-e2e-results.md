# MySpace Calculator APK E2E QA Run

- **Generated (UTC):** 2026-10-27T13:38:46+00:00
- **APK:** `MySpace-v3.12.39-76-lite-dist.apk` (2,281,228 bytes)
- **Package:** `app.space.one`
- **SHA-256:** `7ae98fd05c25554c3b90c32fbc2aeda789c25d0551fab81d071e804106a2a2ad`
- **Device:** Android API 34 emulator, 320x640
- **UI inspection:** uiautomator-compressed
- **Scope:** Calculator feature only
- **Google reference:** NOT_INSTALLED — The official Google Calculator package was not present in the emulator image. No third-party APK mirror was used. Functional assertions therefore use the documented arithmetic expectations; this is not a live side-by-side Google comparison.

## Result summary

| Status | Count |
|---|---:|
| PASS | 6 |
| FAIL | 4 |
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
| TC-CALC-007 | History persists after activity restart and can restore an expression | **FAIL** | History shows 1+1 = 2 after restart | The expected entry was not found after restart. Before restart the display was ['CALCULATOR', '2']; visible history labels were ['History · 7', 'Clear', 'Close history', '= 3', '200+10%', '27th Oct, 13:36', '= 220', '0.1+0.2', '27th Oct, 13:35', '= 0.3', '(2+3)×4', '= 20', '2+3×4', '27th Oct, 13:34', '= 14'].
| TC-CALC-011 | Grouped history card restores and re-evaluates without Error | **FAIL** | History contains the 123456+1 calculation card | The calculation card was not found in the visible history labels.
| TC-CALC-008 | Chained calculations retain unrounded precision | **FAIL** | 1 | After 1 ÷ 3 =, the UI result was ['CALCULATOR', '0.3333333333']; multiplying by 3 did not return 1. This is consistent with the screen feeding its rounded display string back into the next expression.
| TC-CALC-009 | Scientific-notation result can be used in the next expression | **FAIL** | Continue from 1e+15 without Error | Initial 10^15 display was ['CALCULATOR', '1e+15']; adding +1 left an unchanged exponent result or produced Error. This is consistent with exponent-formatted display text not being accepted as a numeric literal by the expression validator/parser.
| TC-CALC-010 | Live comparison with official Google Calculator | **BLOCKED** | Same expressions run in com.google.android.calculator | The official Google Calculator package was not present in the emulator image. No third-party APK mirror was used. Functional assertions therefore use the documented arithmetic expectations; this is not a live side-by-side Google comparison.

Screenshots and UI hierarchy or OCR evidence are in the adjacent `evidence/` folder.
A BLOCKED Google comparison is not treated as a calculator functional pass.
