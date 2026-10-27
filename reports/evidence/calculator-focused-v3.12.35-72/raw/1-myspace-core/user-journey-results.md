# MySpace calculator-only APK QA

- APK: `MySpace-v3.12.35-72-lite-dist.apk`
- Package/version: `app.space.one` · 3.12.35 (72)
- APK SHA-256: `f3257177dc098cf62f54a6f77df526195323d36b23ed5a69f9ff07ddf96b45fb`
- Guide SHA-256: `d494cf934f12f0c5b1e77da2254d026438d1c10d233c9b53e4620beb7014db92`
- Source commit: `0727a2e3b9974d6df70153d76dc8e629e0a0b839`
- Emulator: Android 14/API 34, 320x640
- Calculator counts: `{'PASS': 8, 'FAIL': 2, 'BLOCKED': 1}`
- User journey counts: `{'PASS': 15, 'FAIL': 2, 'BLOCKED': 1}`

| ID | Section | User action | Outcome | Observed | Comment |
|---|---|---|---|---|---|
| D1 | D1 | Evaluate implicit multiplication | PASS | input=CALCULATOR \| 2(5+2)2 \| = 28; result=CALCULATOR \| 28 | The user-entered 2(5+2)2 expression evaluated as implicit multiplication to 28. |
| D2 | D2 | Replace a pending operator | PASS | CALCULATOR \| 10− \| = 10 | The trailing plus was replaced by minus; no evaluation was required. |
| D3 | D3 | Evaluate with a trailing plus | FAIL | CALCULATOR \| 5 | Pressing equals after 5+ did not produce 10. |
| D4 | D4 | Check Indian digit grouping | PASS | CALCULATOR \| 1,23,456 \| = 1,23,456 | Indian digit grouping was visible while typing the six-digit number. |
| D6 | D6 | Evaluate inverse sine in degree mode | PASS | inverse key=sin⁻¹; display=CALCULATOR \| 30 | Inverse sine of 0.5 in degree mode returned 30. |
| D8 | D8 | Delete one character at the caret | PASS | CALCULATOR \| 12 \| = 12 | The caret was placed at the end and one Backspace removed exactly one character. |
| B1 | B1 | Hold number to select and show actions | PASS | OCR toolbar=Copy; Cut; MAdd; MUse; hierarchy=MySpace home \| MySpace \| CALCULATOR \| History \| World time \| More options \| 1,23,456 \| = 1,23,456 \| Toggle the scientific keys \| Open the extra keys \| AC \| ( ) \| % \| ÷ \| 7 \| 8 \| 9 \| × \| 4 \| 5 \| 6 \| − \| 1 \| 2 \| 3 \| + \| 0 \| . \| ⌫ \| = \| Apps \| Clock \| Calculator | The screenshot visibly exposed the floating selection toolbar; OCR is used because Android omits this popup from UiAutomator. |
| B2 | B2 | Drag while holding to change the selected portion | BLOCKED | The emulator input API could not reproduce the app-specific stationary hold-then-drag gesture; no product failure is inferred from this attempt. | The user-facing control was not available to this emulator run. |
| B4 | B4 | Copy then paste within the calculator | PASS | CALCULATOR \| 1,23,456 \| = 1,23,456 | Copy then Paste restored the digits within the calculator app; external app handoff was intentionally not tested. |
| B5 | B5 | Cut a held number and type into the gap | PASS | CALCULATOR \| 7 \| = 7 | Cut removed the held number and the next keypad digit became the expression. |
| B7 | B7 | Clear a held selection with AC | PASS | display=CALCULATOR \| 0; OCR after AC=9:06 © van A MySpace eatcutaror 2) > p v AC % QO 80 a0 Calculator | AC removed the held text and dismissed the floating selection toolbar. |
| B9 | B9 | Tap inside a number and insert a digit | PASS | CALCULATOR \| 12,39,456 \| = 12,39,456 | OCR located the expression and a tap 58% across its visible glyph bounds inserted 9 between existing digits. |
| B11 | B11 | Hold empty expression-box space for caret menu | PASS | OCR caret menu=MUse; Paste; Select all | The screenshot shows the empty-box caret menu; OCR is used because the Android floating menu is omitted from UiAutomator. |
| C9 | C9 | Verify tapping the expression does not open a device keyboard | PASS | input_method not shown | Android's input-method diagnostics did not report a visible software keyboard after tapping the expression. |
| E3 | E3 | Open the three-dot menu | PASS | Haptics: On \| Clear memory \| View memory \| Show as fraction \| Key shape \| Effects \| 907 \| © \| 746 \| CALCULATOR \| B \| MySpace \| Haptics: \| On \| Clear \| memory \| View \| memory \| Show \| as \| fraction \| Key \| shape \| AC \| Effects \| fo) \| 5) \| 2 \| e \| a0 \| a \| 80 \| ® \| © \| g \| Calculator \| Clock \| Apps | The overflow menu exposed Effects plus calculator menu actions. This smoke check does not verify the exact item count or reorder behavior. |
| C10 | C10 | Open key-shape picker and select Circle | PASS | picker=Circle; Squircle; Pill; Rounded square; No shape; selected=Circle | The picker exposed at least four named key silhouettes and accepted a Circle selection. Persistence and pixel-perfect geometry are not inferred from this one view. |
| H1-H2 | H1/H2 | Switch calculator between Light and Dark themes | FAIL | expression after theme switch=CALCULATOR \| 0 | The entered expression did not remain visible after switching themes. |
| ADS-CALC | Calculator | Scan visible calculator labels for ad indicators | PASS | Scanned 31 visible labels; no ad indicator | No ad-like text appeared on the sampled calculator screen; this does not certify the app's network or SDK behavior. |

Screenshots and UI hierarchy XML are in `evidence/`; calculator case JSON is under `calculator/`.
