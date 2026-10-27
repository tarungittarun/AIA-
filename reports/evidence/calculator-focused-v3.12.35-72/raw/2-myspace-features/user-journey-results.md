# MySpace calculator-only APK QA

- APK: `MySpace-v3.12.35-72-lite-dist.apk`
- Package/version: `app.space.one` · 3.12.35 (72)
- APK SHA-256: `f3257177dc098cf62f54a6f77df526195323d36b23ed5a69f9ff07ddf96b45fb`
- Guide SHA-256: `d494cf934f12f0c5b1e77da2254d026438d1c10d233c9b53e4620beb7014db92`
- Source commit: `0727a2e3b9974d6df70153d76dc8e629e0a0b839`
- Emulator: Android 14/API 34, 320x640
- Calculator counts: `{'PASS': 1}`
- User journey counts: `{'FAIL': 1, 'PASS': 2}`

| ID | Section | User action | Outcome | Observed | Comment |
|---|---|---|---|---|---|
| B12 | B12 | Store a number with MAdd and use it in an expression | FAIL | after MUse=CALCULATOR \| 3+41,23,456 \| = 41,23,459 | MUse did not replace only the held 4 with the previously stored 123456. |
| E3-MEMORY | E3 | Open the calculator memory list | PASS | Memory \| Close memory \| 1,23,456 \| Move up from place 1 \| Move down from place 1 \| 825 \| © \| v.46 \| a \| MySpace \| catcutaTor \| Memory \| R \| 1,23,456 \| 59 \| 45 \| e \| a0 \| a \| 80 \| Calculator \| Apps \| Clock | The calculator's memory list displayed the value saved through MAdd. |
| E4 | E4 | Choose a calculator keypress effect | PASS | choices=✓ Spring · bounce back with overshoot; Pulse · quick fade pulse; bounce; Pulse; fade; pulse; selected one option | The Effects picker exposed user-selectable calculator animation options. This smoke test confirms access and selection, not frame-by-frame animation timing. |

Screenshots and UI hierarchy XML are in `evidence/`; calculator case JSON is under `calculator/`.
