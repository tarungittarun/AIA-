# Standalone MyCalc user-facing APK QA

- APK: `MyCalc-v1.0.33-34.apk`
- Package/version: `app.space.calc` · 1.0.33 (34)
- APK SHA-256: `99c65435e455e241dd3eb65ea6494abcabf2099f5024f6a82c6cf8a621a6bf6b`
- Guide SHA-256: `d494cf934f12f0c5b1e77da2254d026438d1c10d233c9b53e4620beb7014db92`
- Source commit: `0727a2e3b9974d6df70153d76dc8e629e0a0b839`
- Emulator: Android 14/API 34, 320x640
- Calculator counts: `{'FAIL': 3, 'PASS': 8}`
- User journey counts: `{'PASS': 11, 'FAIL': 3, 'BLOCKED': 5}`

| ID | Section | User action | Outcome | Observed | Comment |
|---|---|---|---|---|---|
| F-HEADER | F | Inspect standalone MyCalc identity | PASS | World time \| MyCalc \| STANDALONE \| History \| More options \| 1e+15+1 \| Error \| Toggle the scientific keys \| Close the extra keys \| √( \| π \| ^ \| ! \| Deg \| sin( \| cos( \| tan( \| Inv \| e \| ln( \| log( \| AC \| ( ) \| % \| ÷ \| 7 \| 8 \| 9 \| × \| 4 \| 5 \| 6 \| − \| 1 \| 2 \| 3 \| + \| 0 \| . \| ⌫ \| = | The installed standalone calculator identifies itself in the visible app header. |
| F-ADS | F | Sample standalone calculator for ad indicators | PASS | Scanned 41 accessible labels; no ad indicator | No ad label was found on the sampled standalone calculator screen; not a full network/app-wide audit. |
| D1 | D1 | Evaluate implicit multiplication | PASS | input=MyCalc \| STANDALONE \| 2(5+2)2 \| = 28; result=MyCalc \| STANDALONE \| 28 | The user-entered 2(5+2)2 expression evaluated as implicit multiplication to 28. |
| D2 | D2 | Replace a pending operator | PASS | MyCalc \| STANDALONE \| 10− \| = 10 | The trailing plus was replaced by minus; no evaluation was required. |
| D3 | D3 | Evaluate with a trailing plus | FAIL | MyCalc \| STANDALONE \| 5 | Pressing equals after 5+ did not produce 10. |
| D4 | D4 | Check Indian digit grouping | PASS | MyCalc \| STANDALONE \| 1,23,456 \| = 1,23,456 | Indian digit grouping was visible while typing the six-digit number. |
| D6 | D6 | Evaluate inverse sine in degree mode | PASS | inverse key=sin⁻¹; display=MyCalc \| STANDALONE \| 30 | Inverse sine of 0.5 in degree mode returned 30. |
| D8 | D8 | Delete one character at the caret | PASS | MyCalc \| STANDALONE \| 12 \| = 12 | The caret was placed at the end and one Backspace removed exactly one character. |
| B1 | B1 | Hold number to select and show actions | FAIL | World time; MyCalc; STANDALONE; History; More options; 1,23,456; = 1,23,456; Toggle the scientific keys; Open the extra keys; AC; ( ); %; ÷; 7; 8; 9; ×; 4; 5; 6; −; 1; 2; 3; +; 0; .; ⌫; = | The expected selection action menu did not appear after a 650 ms hold on the typed number. |
| B2 | B2 | Drag while holding to change the selected portion | FAIL | World time; MyCalc; STANDALONE; History; More options; 1,23,456; = 1,23,456; Toggle the scientific keys; Open the extra keys; AC; ( ); %; ÷; 7; 8; 9; ×; 4; 5; 6; −; 1; 2; 3; +; 0; .; ⌫; = | No selection action UI was visible after the hold-then-drag gesture. |
| B4 | B4 | Copy then paste the selected digits | BLOCKED | Copy was not offered by the selection menu; clipboard round-trip was not attempted. | The user-facing control was not available to this emulator run. |
| B5 | B5 | Cut a held number and type into the gap | BLOCKED | Cut was not offered by the selection menu. | The user-facing control was not available to this emulator run. |
| B7 | B7 | Clear a held selection with AC | BLOCKED | No selection menu was exposed; AC-while-selected could not be attempted. | The user-facing control was not available to this emulator run. |
| B9 | B9 | Tap inside a number and insert a digit | PASS | MyCalc \| STANDALONE \| 12,39,456 \| = 12,39,456 | A tap within the visible number inserted 9 before the final character instead of appending at the end. |
| B11 | B11 | Hold empty expression-box space for caret menu | BLOCKED | Caret menu items were not exposed by UIAutomator/OCR: ['World time', 'MyCalc', 'STANDALONE', 'History', 'More options', '0', 'Toggle the scientific keys', 'Open the extra keys', 'AC', '( )', '%', '÷', '7', '8', '9', '×', '4', '5', '6', '−', '1', '2', '3', '+', '.', '⌫', '='] | The user-facing control was not available to this emulator run. |
| C9 | C9 | Verify tapping the expression does not open a device keyboard | PASS | input_method not shown | Android's input-method diagnostics did not report a visible software keyboard after tapping the expression. |
| E3 | E3 | Open the three-dot menu | PASS | Haptics: On \| Clear memory \| View memory \| Show as fraction \| Key shape \| Effects | The overflow menu opened and exposed Effects plus calculator menu actions. This smoke check does not verify the exact item count or reorder behavior. |
| C10 | C10 | Open key-shape picker and select Circle | PASS | picker=Circle; Squircle; Pill; Rounded square; No shape; selected=Circle | The new picker exposed at least four named key silhouettes and accepted a Circle selection. Persistence and pixel-perfect geometry are not inferred from this one view. |
| H1-H2 | H1/H2 | Switch between Light and Dark themes | BLOCKED | Settings entry was not visible: ['World time', 'MyCalc', 'STANDALONE', 'History', 'More options', '0', 'Toggle the scientific keys', 'Open the extra keys', 'AC', '( )', '%', '÷', '7', '8', '9', '×', '4', '5', '6', '−', '1', '2', '3', '+', '.', '⌫', '='] | The user-facing control was not available to this emulator run. |

Screenshots and UI hierarchy XML are in `evidence/`; calculator case JSON is under `calculator/`.
