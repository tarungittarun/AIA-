# MySpace calculator-only APK QA

- APK: `MySpace-v3.12.39-76-lite-dist.apk`
- Package/version: `app.space.one` · 3.12.39 (76)
- APK SHA-256: `7ae98fd05c25554c3b90c32fbc2aeda789c25d0551fab81d071e804106a2a2ad`
- Guide SHA-256: `a3d0b131c7beb99f8bc12712eebf8c01e5a8873de7996a23f943905768578fc4`
- Source commit: `a09e52f2c3f141bfc2d3a95f667a38fcac08b54a`
- Emulator: Android 14/API 34, 320x640
- Calculator counts: `{'PASS': 1}`
- User journey counts: `{'PASS': 4, 'BLOCKED': 1}`

| ID | Section | User action | Outcome | Observed | Comment |
|---|---|---|---|---|---|
| B12 | B12 | Store a number with MAdd and use it in an expression | PASS | after MUse=CALCULATOR \| 3+1,23,456 \| = 1,23,459; after equals=CALCULATOR \| 1,23,459 | MAdd stored 123456 and MUse replaced the selected operand in 3+4; the grouped result equals 123459. |
| B12-CARET | B12 | Insert a stored value at a mid-expression caret | BLOCKED | The hold produced a text-selection toolbar, so MUse insertion at an empty caret was not proven. | The user-facing control was not available to this emulator run. |
| E3-MEMORY | E3 | Open the calculator memory list | PASS | Memory \| Close memory \| 1,23,456 \| Move up from place 1 \| Move down from place 1 \| Move up from place 2 \| Move down from place 2 \| Clear memory \| 136 \| © \| v.46 \| CALCULATOR \| B \| MySpace \| Memory \| 1,23,456 \| 1,23,456 \| Clear \| memory \| - \| 5) \| e \| 80 \| a0 \| ® \| A \| © \| > \| Clock \| Calculator \| Apps | The calculator's memory list displayed the value saved through MAdd. |
| E4 | E4 | Choose a calculator keypress effect | PASS | choices=✓ Spring · bounce back with overshoot; Pulse · quick fade pulse; bounce; Pulse; fade; pulse; selected one option | The Effects picker exposed user-selectable calculator animation options. This smoke test confirms access and selection, not frame-by-frame animation timing. |
| C11 | C11 | Select a calculator key theme | PASS | OCR-visible themes=MySpace settings, Graphite, Ocean, Sunset, Mint, Rose, Lemon, Iris; Rose-to-default-keypad screen change=14.2%; restored MySpace settings=True | The key-theme picker exposed Rose, accepted its selection, and visibly changed the calculator screen; the MySpace settings theme was restored where accessible. The eight-theme catalogue was not exhaustively audited. |

Screenshots and UI hierarchy XML are in `evidence/`; calculator case JSON is under `calculator/`.
