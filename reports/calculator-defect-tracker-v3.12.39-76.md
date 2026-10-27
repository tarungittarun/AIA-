# MySpace v3.12.39-76 / MyCalc 1.0.37-38 — calculator defect tracker

**Report date:** 27 October 2026 (Asia/Kolkata)  
**Canonical direct-APK run:** [GitHub Actions run `40512838968`](https://github.com/tarungittarun/AIA-/actions/runs/40512838968)  
**Evidence-rich report:** [`myspace-calculator-qa-v3.12.39-76.pdf`](myspace-calculator-qa-v3.12.39-76.pdf) — 39 pages, 25 embedded emulator screenshots.  
**Raw proof bundle:** [`evidence/calculator-focused-v3.12.39-76/evidence-manifest.json`](evidence/calculator-focused-v3.12.39-76/evidence-manifest.json) — 240 SHA-256/size-verified JSON, PNG, XML, OCR and log files.  
**Overall result:** **FAIL** — direct APK failures remain on both distributions. Two of three APK shards failed; the memory/customization shard passed. The report-publisher job also succeeded, but that is not a passing QA result.  
**Scope:** Calculator UI only. Notes, Scanner, Calendar, Files, Music, Recorder, and other MySpace modules were not exercised or counted.

## Pinned inputs and guide alignment

| Input | Identity |
|---|---|
| MySpace distribution | `MySpace-v3.12.39-76-lite-dist.apk`, `app.space.one`, version `3.12.39` / code `76`, SHA-256 `7ae98fd05c25554c3b90c32fbc2aeda789c25d0551fab81d071e804106a2a2ad` |
| Standalone MyCalc | `MyCalc-v1.0.37-38.apk`, `app.space.calc`, version `1.0.37` / code `38`, SHA-256 `09b1dc8f91ac249643cb92aa74670fdd2db8430af6c0b8c7052d8e906efcf1d4` |
| Matching pinned guide | `TEST-GUIDE.md` at TicTic commit `a09e52f2c3f141bfc2d3a95f667a38fcac08b54a`, SHA-256 `a3d0b131c7beb99f8bc12712eebf8c01e5a8873de7996a23f943905768578fc4` |
| Device | Android 14 / API 34 x86_64 emulator, three shards, `max-parallel: 3` (within the 30-job / 3-runner ceiling) |

The guide copy pasted into chat is headed **MySpace 3.12.23 (60) / MyCalc 1.0.21 (22)** and is older than the supplied APK. To avoid testing one release against another release's claims, this run uses the matching guide checked into the same pinned source commit as the APKs: **MySpace 3.12.39 (76) / MyCalc 1.0.37 (38)**. Both APKs and the guide were SHA-256 verified in Actions before installation; APK ZIP integrity passed, and PackageManager reported the expected version names/codes.

## Direct result summary

| Shard | Calculator cases | Calculator-only user journeys |
|---|---|---|
| MySpace calculator and editing | `PASS 6 / FAIL 4 / BLOCKED 1` | `PASS 17 / FAIL 1 / BLOCKED 1` |
| MySpace memory/customization | `PASS 1` baseline sanity case | `PASS 4 / BLOCKED 1` |
| Standalone MyCalc | `PASS 6 / FAIL 5` | `PASS 21 / FAIL 1 / BLOCKED 3` |

Confirmed direct passes include expression entry/editing, selection toolbar, in-calculator copy/paste, cut-then-type, tap-to-release selection and caret insertion, mid-number insertion, AC clearing, the empty-box caret menu, no-device-keyboard check, D1/D2/D4/D6/D8 representative calculations, key-shape selection, key-theme selection, MAdd/MUse selected-operand replacement, memory-list display, effects selection, and MySpace Light/Dark theme visual change. On both apps, C11 exposed all eight named key themes through UI labels/OCR and accepted the Rose option with a measurable screen change (14.2% MySpace, 18.8% MyCalc); this is a picker/selection smoke pass, not a full palette/contrast certification.

## Open direct-APK findings

### CALC-001 — Chained precision still returns `0.9999999999`

| Field | Assessment |
|---|---|
| **Cases** | `TC-CALC-008` on both APKs |
| **Steps** | `1 ÷ 3 =`, then `× 3 =` |
| **Expected** | `1` |
| **Observed** | MySpace `CALCULATOR | 0.9999999999`; MyCalc `MyCalc | STANDALONE | 0.9999999999` |
| **Status** | Open — reproduced again in v3.12.39 / MyCalc 1.0.37 |
| **Severity / priority** | S2 / P1 — functional numerical accuracy |

**Investigation comment (27 Oct):** The first result is displayed as `0.3333333333`; the next multiplication does not return `1`. The evidence is consistent with the rounded display value being fed back into the next expression. This is the same defect family recorded in the preserved v3.12.21 regression history and remains open. No source-CI success is used to override this direct APK result.

### CALC-002 — Scientific-notation continuation still produces `Error`

| Field | Assessment |
|---|---|
| **Cases** | `TC-CALC-009` on both APKs |
| **Steps** | Produce `1e+15`, then append `+1` and evaluate |
| **Expected** | Continue from the displayed value without `Error` |
| **Observed** | Expression `1e+15+1` and result `Error` on both APKs |
| **Status** | Open — reproduced again in v3.12.39 / MyCalc 1.0.37 |
| **Severity / priority** | S2 / P1 — functional expression parsing / continuity |

**Investigation comment (27 Oct):** The exponent-formatted display text appears not to be accepted as a numeric literal by the expression validator/parser. This is also present in the preserved v3.12.21 regression history. The exact root cause remains a hypothesis; the direct user-visible failure is confirmed.

### CALC-003 — Trailing plus followed by equals remains `5`

| Field | Assessment |
|---|---|
| **Cases** | User journey `D3` on both APKs |
| **Steps** | Clear, type `5+`, tap `=` |
| **Expected** | `10` (the guide says Google doubles the operand) |
| **Observed** | MySpace `CALCULATOR | 5`; MyCalc `MyCalc | STANDALONE | 5` |
| **Status** | Open — direct APK failure |
| **Severity / priority** | S3 / P2 — Google-parity edge case |

**Investigation comment (27 Oct):** This behavior was already seen in the earlier v3.12.35 report and remains present in these newer APKs. It is a direct claim mismatch, not an emulator access problem. A live official Google Calculator comparison was still unavailable, so the expected value comes from the pinned guide rather than a side-by-side run.

### CALC-004 — History persistence / replay assertions fail on both APKs

| Field | Assessment |
|---|---|
| **Cases** | `TC-CALC-007` and `TC-CALC-011` on both APKs |
| **Expected** | History shows `1+1 = 2` after restart; the `123456+1` card restores and re-evaluates to `123457` |
| **Observed** | The expected entries/cards were not found in visible history labels, although several other history entries were visible |
| **Status** | Open as a direct APK assertion failure; exact cause not isolated |
| **Severity / priority** | S2 / P1 pending root-cause review |

**Investigation comment (27 Oct):** Both cases returned FAIL with history sheets populated by other calculations (`200+10%`, `0.1+0.2`, `(2+3)×4`, `2+3×4`, etc.). The screenshots show visible history, but the harness could not locate the specific expected expressions. This should be investigated as either a persistence/ordering/labeling issue or a harness-selection issue before declaring data loss. The report does not claim that all history is missing.

### CALC-005 — Standalone MyCalc requests a permission despite guide's zero-permission wording

| Field | Assessment |
|---|---|
| **Case** | `TC-CALC-012` on standalone MyCalc |
| **Expected** | No requested Android permissions |
| **Observed** | `app.space.calc.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION` |
| **Status** | Open — literal guide claim mismatch |
| **Severity / priority** | S4 / P3 — documentation / manifest audit |

**Investigation comment (27 Oct):** The PackageManager audit finds one requested permission. This is a framework-provided, signature-style protection commonly used for non-exported dynamic receivers; the test does **not** infer a dangerous runtime permission or an ad/network capability. The strict “zero requested permissions” wording in the guide is nevertheless inaccurate for this installed package.

## Blocked probes and bounded claims

| Probe | APK(s) | Why blocked | Interpretation |
|---|---|---|---|
| `B2` hold-then-drag selection | MySpace, MyCalc | `adb input swipe` cannot reproduce the app's stationary hold timer followed by a continuous character-by-character drag | No product failure inferred; selection binding remains untested by this emulator gesture |
| `B12-CARET` empty-caret MUse insertion | MySpace, MyCalc | After a screenshot showed the caret between `+` and `4`, the subsequent hold raised a text-selection toolbar (`Cut/Copy/MAdd/MUse/Paste`) rather than the smaller caret menu | The selected-operand MUse path passed, but MUse insertion at an empty mid-expression caret remains unproved |
| MyCalc `H1-H2` Light/Dark theme route | MyCalc | Settings/Theme was not exposed from the standalone calculator's home; only calculator overflow items were available | MySpace's Light/Dark change passed, but standalone theme switching remains untested |
| `TC-CALC-010` official Google Calculator comparison | MySpace | `com.google.android.calculator` was absent from the emulator image | No live comparison; AOSP Calculator was not substituted and no third-party APK mirror was used |

Additional boundaries: pixel-level caret blink, exact LED palettes, whole-line autoscroll, all eight key-theme palettes, frame-by-frame animation effects, memory reordering, external-app paste, handle dragging at all margins, and ad-related network/SDK behavior were not certified. The ad check only found no ad-like text in sampled calculator labels; it is not a whole-app or network ad-free certification.

## Environment, source CI, and historical records

- The canonical run used exactly three Android emulator jobs in parallel. Two shards are red because of direct `FAIL` results; the publisher job is green because it runs with `if: always()` and produces the PDF/evidence commit. Publisher success is not a QA pass.
- An earlier v3.12.39 run, [`40509840646`](https://github.com/tarungittarun/AIA-/actions/runs/40509840646), exposed harness navigation issues in memory-list, key-theme, and standalone theme probes. Those harness issues were corrected and the canonical run `40512838968` is the report of record.
- At the pinned source commit, upstream [`Tests` run `40504883690`](https://github.com/tarungittarun/TicTic/actions/runs/40504883690) had passing source-contract and JVM jobs but a failing UI emulator end-to-end job; [`Android CI` run `40504883668`](https://github.com/tarungittarun/TicTic/actions/runs/40504883668) succeeded for Python source contracts and a debug build. These are source-level results, not direct tests of the distributed APKs, and are not counted as APK passes or failures.
- Previous release reports remain preserved as historical records, including [`calculator-defect-tracker-v3.12.21-58.md`](calculator-defect-tracker-v3.12.21-58.md), [`calculator-defect-tracker-v3.12.24-61.html`](calculator-defect-tracker-v3.12.24-61.html), [`myspace-calculator-qa-v3.12.35-72.pdf`](myspace-calculator-qa-v3.12.35-72.pdf), and the older long-form [`calculator-defect-tracker.md`](calculator-defect-tracker.md). The v3.12.21 regression history for chained precision and exponent continuation is intentionally retained.
- The 240-file evidence bundle passed local SHA-256 and size verification against its manifest. The PDF was checked for 39 pages and 25 embedded screenshots. Original JSON, PNG, XML, OCR sidecars, hierarchy dumps, and crash-scan text remain in the sidecar folder for audit.

**Recommendation:** Do not present this release as calculator-complete or Google-parity certified. Prioritize CALC-001, CALC-002, and CALC-004; fix or clarify the `5+ =` expectation; update the standalone zero-permission wording; and rerun the blocked gesture/theme probes with an input method and reference-app image that can exercise them fairly.
