# Standalone MyCalc calculator-only APK QA

- APK: `MyCalc-v1.0.33-34.apk`
- Package/version: `app.space.calc` · 1.0.33 (34)
- APK SHA-256: `99c65435e455e241dd3eb65ea6494abcabf2099f5024f6a82c6cf8a621a6bf6b`
- Guide SHA-256: `d494cf934f12f0c5b1e77da2254d026438d1c10d233c9b53e4620beb7014db92`
- Source commit: `0727a2e3b9974d6df70153d76dc8e629e0a0b839`
- Emulator: Android 14/API 34, 320x640
- Calculator counts: `{'FAIL': 3, 'PASS': 8}`
- User journey counts: `{'PASS': 18, 'FAIL': 2, 'BLOCKED': 2}`

| ID | Section | User action | Outcome | Observed | Comment |
|---|---|---|---|---|---|
| F-HEADER | F | Inspect standalone MyCalc identity | PASS | World time \| MyCalc \| STANDALONE \| History \| More options \| 1e+15+1 \| Error \| Toggle the scientific keys \| Close the extra keys \| √( \| π \| ^ \| ! \| Deg \| sin( \| cos( \| tan( \| Inv \| e \| ln( \| log( \| AC \| ( ) \| % \| ÷ \| 7 \| 8 \| 9 \| × \| 4 \| 5 \| 6 \| − \| 1 \| 2 \| 3 \| + \| 0 \| . \| ⌫ \| = | The installed standalone calculator identifies itself in the visible app header. |
| D1 | D1 | Evaluate implicit multiplication | PASS | input=MyCalc \| STANDALONE \| 2(5+2)2 \| = 28; result=MyCalc \| STANDALONE \| 28 | The user-entered 2(5+2)2 expression evaluated as implicit multiplication to 28. |
| D2 | D2 | Replace a pending operator | PASS | MyCalc \| STANDALONE \| 10− \| = 10 | The trailing plus was replaced by minus; no evaluation was required. |
| D3 | D3 | Evaluate with a trailing plus | FAIL | MyCalc \| STANDALONE \| 5 | Pressing equals after 5+ did not produce 10. |
| D4 | D4 | Check Indian digit grouping | PASS | MyCalc \| STANDALONE \| 1,23,456 \| = 1,23,456 | Indian digit grouping was visible while typing the six-digit number. |
| D6 | D6 | Evaluate inverse sine in degree mode | PASS | inverse key=sin⁻¹; display=MyCalc \| STANDALONE \| 30 | Inverse sine of 0.5 in degree mode returned 30. |
| D8 | D8 | Delete one character at the caret | PASS | MyCalc \| STANDALONE \| 12 \| = 12 | The caret was placed at the end and one Backspace removed exactly one character. |
| B1 | B1 | Hold number to select and show actions | PASS | OCR toolbar=Copy; Cut; MAdd; MUse; hierarchy=World time \| MyCalc \| STANDALONE \| History \| More options \| 1,23,456 \| = 1,23,456 \| Toggle the scientific keys \| Open the extra keys \| AC \| ( ) \| % \| ÷ \| 7 \| 8 \| 9 \| × \| 4 \| 5 \| 6 \| − \| 1 \| 2 \| 3 \| + \| 0 \| . \| ⌫ \| = | The screenshot visibly exposed the floating selection toolbar; OCR is used because Android omits this popup from UiAutomator. |
| B2 | B2 | Drag while holding to change the selected portion | BLOCKED | The emulator input API could not reproduce the app-specific stationary hold-then-drag gesture; no product failure is inferred from this attempt. | The user-facing control was not available to this emulator run. |
| B4 | B4 | Copy then paste within the calculator | PASS | MyCalc \| STANDALONE \| 1,23,456 \| = 1,23,456 | Copy then Paste restored the digits within the calculator app; external app handoff was intentionally not tested. |
| B5 | B5 | Cut a held number and type into the gap | PASS | MyCalc \| STANDALONE \| 7 \| = 7 | Cut removed the held number and the next keypad digit became the expression. |
| B7 | B7 | Clear a held selection with AC | PASS | display=MyCalc \| STANDALONE \| 0; OCR after AC=850 © v.46 3 FA MyCalc STANDALONE > p v AC 0 % | AC removed the held text and dismissed the floating selection toolbar. |
| B9 | B9 | Tap inside a number and insert a digit | PASS | MyCalc \| STANDALONE \| 12,39,456 \| = 12,39,456 | OCR located the expression and a tap 58% across its visible glyph bounds inserted 9 between existing digits. |
| B11 | B11 | Hold empty expression-box space for caret menu | PASS | OCR caret menu=MUse; Paste; Select all | The screenshot shows the empty-box caret menu; OCR is used because the Android floating menu is omitted from UiAutomator. |
| C9 | C9 | Verify tapping the expression does not open a device keyboard | PASS | input_method not shown | Android's input-method diagnostics did not report a visible software keyboard after tapping the expression. |
| E3 | E3 | Open the three-dot menu | PASS | Haptics: On \| Clear memory \| View memory \| Show as fraction \| Key shape \| Effects \| 851 \| © \| wa \| Ey \| ‘STANDALONE, \| MyCalc \| Haptics: \| On \| Clear \| memory \| View \| memory \| Show \| as \| fraction \| Key \| shape \| Effects \| . \| 8 | The overflow menu exposed Effects plus calculator menu actions. This smoke check does not verify the exact item count or reorder behavior. |
| C10 | C10 | Open key-shape picker and select Circle | PASS | picker=Circle; Squircle; Pill; Rounded square; No shape; selected=Circle | The picker exposed at least four named key silhouettes and accepted a Circle selection. Persistence and pixel-perfect geometry are not inferred from this one view. |
| H1-H2 | H1/H2 | Switch calculator between Light and Dark themes | BLOCKED | Settings was not exposed from the calculator's MySpace home: ['Haptics: On', 'Clear memory', 'View memory', 'Show as fraction', 'Key shape', 'Effects'] | The user-facing control was not available to this emulator run. |
| ADS-CALC | Calculator | Scan visible calculator labels for ad indicators | PASS | Scanned 6 visible labels; no ad indicator | No ad-like text appeared on the sampled calculator screen; this does not certify the app's network or SDK behavior. |
| B12 | B12 | Store a number with MAdd and use it in an expression | FAIL | after MUse=MyCalc \| STANDALONE \| 3+1,23,456 \| = 1,23,459; after equals=MyCalc \| STANDALONE \| 1,23,459 | The stored value appeared in the expression but the calculator did not evaluate the expected sum 123459. |
| E3-MEMORY | E3 | Open the calculator memory list | PASS | Memory \| Close memory \| 1,23,456 \| Move up from place 1 \| Move down from place 1 \| 852 \| © \| v.46 \| 3 \| FA \| MyCalc \| ‘STANDALONE \| 159 \| Memory \| 1,23,456 \| 7 \| 8 \| 9 \| 4 \| ) \| 1 \| 2 | The calculator's memory list displayed the value saved through MAdd. |
| E4 | E4 | Choose a calculator keypress effect | PASS | choices=✓ Spring · bounce back with overshoot; Pulse · quick fade pulse; bounce; Pulse; fade; pulse; selected one option | The Effects picker exposed user-selectable calculator animation options. This smoke test confirms access and selection, not frame-by-frame animation timing. |

Screenshots and UI hierarchy XML are in `evidence/`; calculator case JSON is under `calculator/`.
