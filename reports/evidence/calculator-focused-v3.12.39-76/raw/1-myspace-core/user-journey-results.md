# MySpace calculator-only APK QA

- APK: `MySpace-v3.12.39-76-lite-dist.apk`
- Package/version: `app.space.one` · 3.12.39 (76)
- APK SHA-256: `7ae98fd05c25554c3b90c32fbc2aeda789c25d0551fab81d071e804106a2a2ad`
- Guide SHA-256: `a3d0b131c7beb99f8bc12712eebf8c01e5a8873de7996a23f943905768578fc4`
- Source commit: `a09e52f2c3f141bfc2d3a95f667a38fcac08b54a`
- Emulator: Android 14/API 34, 320x640
- Calculator counts: `{'PASS': 6, 'FAIL': 4, 'BLOCKED': 1}`
- User journey counts: `{'PASS': 17, 'FAIL': 1, 'BLOCKED': 1}`

| ID | Section | User action | Outcome | Observed | Comment |
|---|---|---|---|---|---|
| D1 | D1 | Evaluate implicit multiplication | PASS | input=CALCULATOR \| 2(5+2)2 \| = 28; result=CALCULATOR \| 28 | The user-entered 2(5+2)2 expression evaluated as implicit multiplication to 28. |
| D2 | D2 | Replace a pending operator | PASS | CALCULATOR \| 10− \| = 10 | The trailing plus was replaced by minus; no evaluation was required. |
| D3 | D3 | Evaluate with a trailing plus | FAIL | CALCULATOR \| 5 | Pressing equals after 5+ did not produce 10. |
| D4 | D4 | Check Indian digit grouping | PASS | CALCULATOR \| 1,23,456 \| = 1,23,456 | Indian digit grouping was visible while typing the six-digit number. |
| D6 | D6 | Evaluate inverse sine in degree mode | PASS | inverse key=sin⁻¹; display=CALCULATOR \| 30 | Inverse sine of 0.5 in degree mode returned 30. |
| D8 | D8 | Delete one character at the caret | PASS | CALCULATOR \| 12 \| = 12 | The caret was placed at the end and one Backspace removed exactly one character. |
| B1 | B1 | Hold number to select and show actions | PASS | OCR toolbar=Copy; Cut; MAdd; MUse; Paste; hierarchy=MySpace home \| MySpace \| CALCULATOR \| History \| World time \| More options \| 1,23,456 \| = 1,23,456 \| Toggle the scientific keys \| Open the extra keys \| AC \| ( ) \| % \| ÷ \| 7 \| 8 \| 9 \| × \| 4 \| 5 \| 6 \| − \| 1 \| 2 \| 3 \| + \| 0 \| . \| ⌫ \| = \| Apps \| Clock \| Calculator | The screenshot visibly exposed the floating selection toolbar; OCR is used because Android omits this popup from UiAutomator. |
| B2 | B2 | Drag while holding to change the selected portion | BLOCKED | The emulator input API could not reproduce the app-specific stationary hold-then-drag gesture; no product failure is inferred from this attempt. | The user-facing control was not available to this emulator run. |
| B4 | B4 | Copy then paste within the calculator | PASS | CALCULATOR \| 1,23,456 \| = 1,23,456 | Copy then Paste restored the digits within the calculator app; external app handoff was intentionally not tested. |
| B5 | B5 | Cut a held number and type into the gap | PASS | CALCULATOR \| 7 \| = 7 | Cut removed the held number and the next keypad digit became the expression. |
| B6 | B6 | Tap the held expression to release selection and place the caret | PASS | after tapping selected text and typing 9: CALCULATOR \| 12,39,456 \| = 12,39,456 | The held selection released on an in-selection tap, and the next digit was inserted at an interior caret position. |
| B7 | B7 | Clear a held selection with AC | PASS | display=CALCULATOR \| 0; OCR after AC=1:43 © w40 ~ MySpace eatcutaror p v AC % QO 80 a0 Calculator | AC removed the held text and dismissed the floating selection toolbar. |
| B9 | B9 | Tap inside a number and insert a digit | PASS | CALCULATOR \| 12,39,456 \| = 12,39,456 | OCR located the expression and a tap 58% across its visible glyph bounds inserted 9 between existing digits. |
| B11 | B11 | Hold empty expression-box space for caret menu | PASS | OCR caret menu=MUse; Paste | The screenshot shows the empty-box caret menu; OCR is used because the Android floating menu is omitted from UiAutomator. |
| C9 | C9 | Verify tapping the expression does not open a device keyboard | PASS | input_method not shown | Android's input-method diagnostics did not report a visible software keyboard after tapping the expression. |
| E3 | E3 | Open the three-dot menu | PASS | Haptics: On \| Memory \| Show as fraction \| Key theme \| Key shape \| Effects \| 144 \| © \| v.46 \| CALCULATOR \| B \| MySpace \| Haptics: \| On \| Memory \| Show \| as \| fraction \| Key \| theme \| Key \| shape \| AC \| Effects \| fo) \| 5) \| 2 \| e \| a0 \| a \| 80 \| ® \| © \| g \| Calculator \| Clock \| Apps | The overflow menu exposed Effects plus calculator menu actions. This smoke check does not verify the exact item count or reorder behavior. |
| C10 | C10 | Open key-shape picker and select Circle | PASS | picker=Circle; Squircle; Pill; Rounded square; No shape; selected=Circle | The picker exposed at least four named key silhouettes and accepted a Circle selection. Persistence and pixel-perfect geometry are not inferred from this one view. |
| H1-H2 | H1/H2 | Apply Light and Dark calculator themes | PASS | stable-screen pixel change=98.3%; Light SHA-256=47f3f2657a38700111d21ac8c0e91772521379127a57369d3acd6397247e0740; Dark SHA-256=03c2bfa1e77e8f65a6986cd3f596162581ec61f26457e0db304f3822753c4e51; expression=['CALCULATOR', '0'] | Both Light and Dark choices produced visibly different calculator screens. The displayed expression reset during the settings/home route, so expression persistence is not claimed. Exact palette/caret pixels are not asserted. |
| ADS-CALC | Calculator | Scan visible calculator labels for ad indicators | PASS | Scanned 31 visible labels; no ad indicator | No ad-like text appeared on the sampled calculator screen; this does not certify the app's network or SDK behavior. |

Screenshots and UI hierarchy XML are in `evidence/`; calculator case JSON is under `calculator/`.
