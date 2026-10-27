# Standalone MyCalc calculator-only APK QA

- APK: `MyCalc-v1.0.37-38.apk`
- Package/version: `app.space.calc` · 1.0.37 (38)
- APK SHA-256: `09b1dc8f91ac249643cb92aa74670fdd2db8430af6c0b8c7052d8e906efcf1d4`
- Guide SHA-256: `a3d0b131c7beb99f8bc12712eebf8c01e5a8873de7996a23f943905768578fc4`
- Source commit: `a09e52f2c3f141bfc2d3a95f667a38fcac08b54a`
- Emulator: Android 14/API 34, 320x640
- Calculator counts: `{'FAIL': 5, 'PASS': 6}`
- User journey counts: `{'PASS': 19, 'FAIL': 1, 'BLOCKED': 5}`

| ID | Section | User action | Outcome | Observed | Comment |
|---|---|---|---|---|---|
| F-HEADER | F | Inspect standalone MyCalc identity | PASS | World time \| MyCalc \| STANDALONE \| History \| More options \| 1e+15+1 \| Error \| Toggle the scientific keys \| Close the extra keys \| √( \| π \| ^ \| ! \| Deg \| sin( \| cos( \| tan( \| Inv \| e \| ln( \| log( \| AC \| ( ) \| % \| ÷ \| 7 \| 8 \| 9 \| × \| 4 \| 5 \| 6 \| − \| 1 \| 2 \| 3 \| + \| 0 \| . \| ⌫ \| = | The installed standalone calculator identifies itself in the visible app header. |
| D1 | D1 | Evaluate implicit multiplication | PASS | input=MyCalc \| STANDALONE \| 2(5+2)2 \| = 28; result=MyCalc \| STANDALONE \| 28 | The user-entered 2(5+2)2 expression evaluated as implicit multiplication to 28. |
| D2 | D2 | Replace a pending operator | PASS | MyCalc \| STANDALONE \| 10− \| = 10 | The trailing plus was replaced by minus; no evaluation was required. |
| D3 | D3 | Evaluate with a trailing plus | FAIL | MyCalc \| STANDALONE \| 5 | Pressing equals after 5+ did not produce 10. |
| D4 | D4 | Check Indian digit grouping | PASS | MyCalc \| STANDALONE \| 1,23,456 \| = 1,23,456 | Indian digit grouping was visible while typing the six-digit number. |
| D6 | D6 | Evaluate inverse sine in degree mode | PASS | inverse key=sin⁻¹; display=MyCalc \| STANDALONE \| 30 | Inverse sine of 0.5 in degree mode returned 30. |
| D8 | D8 | Delete one character at the caret | PASS | MyCalc \| STANDALONE \| 12 \| = 12 | The caret was placed at the end and one Backspace removed exactly one character. |
| B1 | B1 | Hold number to select and show actions | PASS | OCR toolbar=Copy; Cut; MAdd; MUse; Paste; hierarchy=World time \| MyCalc \| STANDALONE \| History \| More options \| 1,23,456 \| = 1,23,456 \| Toggle the scientific keys \| Open the extra keys \| AC \| ( ) \| % \| ÷ \| 7 \| 8 \| 9 \| × \| 4 \| 5 \| 6 \| − \| 1 \| 2 \| 3 \| + \| 0 \| . \| ⌫ \| = | The screenshot visibly exposed the floating selection toolbar; OCR is used because Android omits this popup from UiAutomator. |
| B2 | B2 | Drag while holding to change the selected portion | BLOCKED | The emulator input API could not reproduce the app-specific stationary hold-then-drag gesture; no product failure is inferred from this attempt. | The user-facing control was not available to this emulator run. |
| B4 | B4 | Copy then paste within the calculator | PASS | MyCalc \| STANDALONE \| 1,23,456 \| = 1,23,456 | Copy then Paste restored the digits within the calculator app; external app handoff was intentionally not tested. |
| B5 | B5 | Cut a held number and type into the gap | PASS | MyCalc \| STANDALONE \| 7 \| = 7 | Cut removed the held number and the next keypad digit became the expression. |
| B6 | B6 | Tap the held expression to release selection and place the caret | PASS | after tapping selected text and typing 9: MyCalc \| STANDALONE \| 12,39,456 \| = 12,39,456 | The held selection released on an in-selection tap, and the next digit was inserted at an interior caret position. |
| B7 | B7 | Clear a held selection with AC | PASS | display=MyCalc \| STANDALONE \| 0; OCR after AC=122 © 746 3 FA MyCalc STANDALONE > p v AC 0 % | AC removed the held text and dismissed the floating selection toolbar. |
| B9 | B9 | Tap inside a number and insert a digit | PASS | MyCalc \| STANDALONE \| 12,39,456 \| = 12,39,456 | OCR located the expression and a tap 58% across its visible glyph bounds inserted 9 between existing digits. |
| B11 | B11 | Hold empty expression-box space for caret menu | PASS | OCR caret menu=MUse; Paste | The screenshot shows the empty-box caret menu; OCR is used because the Android floating menu is omitted from UiAutomator. |
| C9 | C9 | Verify tapping the expression does not open a device keyboard | PASS | input_method not shown | Android's input-method diagnostics did not report a visible software keyboard after tapping the expression. |
| E3 | E3 | Open the three-dot menu | PASS | Haptics: On \| Memory \| Show as fraction \| Key theme \| Key shape \| Effects \| 123 \| © \| eat \| ‘STANDALONE, \| MyCalc \| Haptics: \| On \| Memory \| Show \| as \| fraction \| Key \| theme \| Key \| shape \| Effects | The overflow menu exposed Effects plus calculator menu actions. This smoke check does not verify the exact item count or reorder behavior. |
| C10 | C10 | Open key-shape picker and select Circle | PASS | picker=Circle; Squircle; Pill; Rounded square; No shape; selected=Circle | The picker exposed at least four named key silhouettes and accepted a Circle selection. Persistence and pixel-perfect geometry are not inferred from this one view. |
| H1-H2 | H1/H2 | Apply Light and Dark calculator themes | BLOCKED | Settings was not exposed from the calculator's MySpace home: ['Haptics: On', 'Memory', 'Show as fraction', 'Key theme', 'Key shape', 'Effects'] | The user-facing control was not available to this emulator run. |
| ADS-CALC | Calculator | Scan visible calculator labels for ad indicators | PASS | Scanned 6 visible labels; no ad indicator | No ad-like text appeared on the sampled calculator screen; this does not certify the app's network or SDK behavior. |
| B12 | B12 | Store a number with MAdd and use it in an expression | PASS | after MUse=MyCalc \| STANDALONE \| 3+1,23,456 \| = 1,23,459; after equals=MyCalc \| STANDALONE \| 1,23,459 | MAdd stored 123456 and MUse replaced the selected operand in 3+4; the grouped result equals 123459. |
| B12-CARET | B12 | Insert a stored value at a mid-expression caret | BLOCKED | The hold produced a text-selection toolbar, so MUse insertion at an empty caret was not proven. | The user-facing control was not available to this emulator run. |
| E3-MEMORY | E3 | Open the calculator memory list | BLOCKED | Calculator overflow did not expose View memory: ['World time', 'MyCalc', 'STANDALONE', 'History', 'More options', '3+1,23,456', '= 1,23,459', 'Toggle the scientific keys', 'Open the extra keys', 'AC', '( )', '%', '÷', '7', '8', '9', '×', '4', '5', '6', '−', '1', '2', '3', '+', '0', '.', '⌫', '='] | The user-facing control was not available to this emulator run. |
| E4 | E4 | Choose a calculator keypress effect | PASS | choices=✓ Spring · bounce back with overshoot; Pulse · quick fade pulse; bounce; Pulse; fade; pulse; selected one option | The Effects picker exposed user-selectable calculator animation options. This smoke test confirms access and selection, not frame-by-frame animation timing. |
| C11 | C11 | Select a calculator key theme | BLOCKED | Could not return to calculator controls through MySpace's Apps route: ['Tue, Oct 27', 'Home', 'Phone', 'Messages', 'MyCalc', 'Predicted app: MyCalc', 'Chrome', 'Camera', 'Search', 'Google app', 'Voice search', 'Google Lens'] | The user-facing control was not available to this emulator run. |

Screenshots and UI hierarchy XML are in `evidence/`; calculator case JSON is under `calculator/`.
