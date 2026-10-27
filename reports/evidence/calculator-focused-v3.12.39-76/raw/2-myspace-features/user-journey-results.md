# MySpace calculator-only APK QA

- APK: `MySpace-v3.12.39-76-lite-dist.apk`
- Package/version: `app.space.one` · 3.12.39 (76)
- APK SHA-256: `7ae98fd05c25554c3b90c32fbc2aeda789c25d0551fab81d071e804106a2a2ad`
- Guide SHA-256: `a3d0b131c7beb99f8bc12712eebf8c01e5a8873de7996a23f943905768578fc4`
- Source commit: `a09e52f2c3f141bfc2d3a95f667a38fcac08b54a`
- Emulator: Android 14/API 34, 320x640
- Calculator counts: `{'PASS': 1}`
- User journey counts: `{'PASS': 2, 'BLOCKED': 3}`

| ID | Section | User action | Outcome | Observed | Comment |
|---|---|---|---|---|---|
| B12 | B12 | Store a number with MAdd and use it in an expression | PASS | after MUse=CALCULATOR \| 3+1,23,456 \| = 1,23,459; after equals=CALCULATOR \| 1,23,459 | MAdd stored 123456 and MUse replaced the selected operand in 3+4; the grouped result equals 123459. |
| B12-CARET | B12 | Insert a stored value at a mid-expression caret | BLOCKED | The hold produced a text-selection toolbar, so MUse insertion at an empty caret was not proven. | The user-facing control was not available to this emulator run. |
| E3-MEMORY | E3 | Open the calculator memory list | BLOCKED | Calculator overflow did not expose View memory: ['MySpace home', 'MySpace', 'CALCULATOR', 'History', 'World time', 'More options', '3+4', '= 7', 'Toggle the scientific keys', 'Open the extra keys', 'AC', '( )', '%', '÷', '7', '8', '9', '×', '4', '5', '6', '−', '1', '2', '3', '+', '0', '.', '⌫', '=', 'Apps', 'Clock', 'Calculator'] | The user-facing control was not available to this emulator run. |
| E4 | E4 | Choose a calculator keypress effect | PASS | choices=✓ Spring · bounce back with overshoot; Pulse · quick fade pulse; bounce; Pulse; fade; pulse; selected one option | The Effects picker exposed user-selectable calculator animation options. This smoke test confirms access and selection, not frame-by-frame animation timing. |
| C11 | C11 | Select a calculator key theme | BLOCKED | Could not return to calculator controls through MySpace's Apps route: ['Tue, Oct 27', 'Home', 'Phone', 'Messages', 'MySpace', 'Predicted app: MySpace', 'Chrome', 'Camera', 'Search', 'Google app', 'Voice search', 'Google Lens'] | The user-facing control was not available to this emulator run. |

Screenshots and UI hierarchy XML are in `evidence/`; calculator case JSON is under `calculator/`.
