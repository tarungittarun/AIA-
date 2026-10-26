# MySpace v3.12.21-58 — Test Guide QA report & defect tracker

**Report date:** 2026-10-26

**Overall result:** **FAIL — two reproducible calculator defects; one Google parity comparison blocked.**

**Execution:** GitHub Actions, three Android 14 emulator shards, maximum three concurrent jobs.

## Executive summary

The exact MySpace distribution APK was checksum-verified, installed on Android 14 emulators, and exercised with the calculator E2E suite. The normal arithmetic, decimal, percent, scientific square-root/sine, and history checks passed. Two blind arithmetic probes failed in both MySpace and the separate MyCalc distribution: chained precision (`1 ÷ 3 = × 3 =`) ends at `0.9999999999`, and continuing from a displayed `10^15` result with `+1` yields `Error`. These are tracked below as open defects; the suspected causes are hypotheses, not confirmed root causes.

The plan below covers the guide's A–G claims, plus two blind probes. **The supplied MySpace APK runtime automation currently exercises the calculator only.** Claims outside that calculator path are reported as source-CI evidence or not directly tested—not as distribution-APK passes. Upstream CI for the exact source commit was green, but it builds/tests source and does not replace black-box testing of the supplied MySpace APK.

The official Google Calculator package was absent from the emulator image. TC-CALC-010 is therefore **BLOCKED**, not passed; AOSP Calculator was not substituted.

## Pinned inputs

| Input | Identity |
|---|---|
| Test guide | [`TEST-GUIDE.md` at source commit](https://github.com/tarungittarun/TicTic/blob/e0bc02e191e6f793a40f23d0a07705a75396468e/TEST-GUIDE.md); SHA-256 `8ea903e7bca901acfe5151c6b665b84f066be7a7e340684f5afff001429943f4` |
| MySpace distribution | [`MySpace-v3.12.21-58-lite-dist.apk`](https://github.com/tarungittarun/TicTic/raw/e0bc02e191e6f793a40f23d0a07705a75396468e/artifacts/MySpace-v3.12.21-58-lite-dist.apk); package `app.space.one`; version `3.12.21` / code `58`; SHA-256 `629442fc1d54508690f8c75664ea8be7611fef14a74f4edcf6f2bd1cab40068d` |
| Standalone MyCalc | [`MyCalc-v1.0.19-20.apk`](https://github.com/tarungittarun/TicTic/raw/e0bc02e191e6f793a40f23d0a07705a75396468e/artifacts/MyCalc-v1.0.19-20.apk); package `app.space.calc`; version `1.0.19` / code `20`; SHA-256 `342f51bdbb12539f44971fc945d427714ac8cf74bf01a7fa8fccf02660e1f3fa` |
| Source commit | `e0bc02e191e6f793a40f23d0a07705a75396468e` |

Both APKs passed ZIP integrity and SHA-256 checks before installation.

## Runtime execution and evidence

- **Canonical run:** [GitHub Actions run 40299195327](https://github.com/tarungittarun/AIA-/actions/runs/40299195327) — three shards, one emulator boot per shard, max parallelism three. Shards 1 and 2 succeeded; shard 3 correctly failed on the two calculator defects. Screenshots, UI hierarchy captures, JSON, and Markdown run summaries are attached to the run's Artifacts section.
- **Earlier result run:** [40294118915](https://github.com/tarungittarun/AIA-/actions/runs/40294118915) — used to confirm standalone MyCalc cases 002 and 003; the final run reran the refined three-shard plan.
- **Harness tests:** 12/12 local unit tests passed; the unit-test step passed in all three canonical shards.
- **Pinned-source CI:** upstream [`Tests` run 40292039978](https://github.com/tarungittarun/TicTic/actions/runs/40292039978) and [`Android CI` run 40292039996](https://github.com/tarungittarun/TicTic/actions/runs/40292039996) both reported success on the pinned source commit. The guide states it has 386 Python contracts, 21 JVM suites, and 33 instrumented stories. These are useful source-level checks, but are not counted as direct runtime passes for the supplied distribution APK.
- **Emulator note:** transient Android system ANR dialogs required the harness's bounded Wait retries. The relevant jobs recovered and produced results; this is recorded as an emulator stability warning, not a confirmed app defect.

### Exact MySpace APK calculator results

Unique test IDs, deduplicating TC-CALC-001 because it was rerun as the TC-010 comparator baseline:

| ID | Scenario | Expected | Observed | Result |
|---|---|---|---|---|
| TC-CALC-001 | `2 + 3 × 4` | `14` | `14` | **PASS** |
| TC-CALC-002 | `(2 + 3) × 4` | `20` | `20` | **PASS** |
| TC-CALC-003 | `0.1 + 0.2` | `0.3` | `0.3` | **PASS** |
| TC-CALC-004 | `200 + 10%` | `220` | `220` | **PASS** |
| TC-CALC-005 | `√(9)` | `3` | `3` | **PASS** |
| TC-CALC-006 | `sin(30)` in degree mode | `0.5` | `0.5` | **PASS** |
| TC-CALC-007 | Persist and restore `1 + 1 = 2` via history | History survives activity restart and restores expression | Restored `1+1`; result `2` | **PASS** |
| TC-CALC-008 | `1 ÷ 3 =`, then `× 3 =` | `1` | `0.9999999999` | **FAIL — DEF-3219-01** |
| TC-CALC-009 | `10^15 =`, then `+ 1 =` | `1000000000000001` | Expression `1e+15+1`; result `Error` | **FAIL — DEF-3219-02** |
| TC-CALC-010 | Live parity check with official Google Calculator | Same `2 + 3 × 4 = 14` behavior in both apps | `com.google.android.calculator` absent | **BLOCKED** |

**MySpace unique-ID totals:** 7 PASS, 2 FAIL, 1 BLOCKED. TC-CALC-001 was additionally rerun as a baseline for TC-CALC-010.

### Standalone MyCalc distribution results

The standalone APK was checksum-verified and installed. Cases 001–009 were selected across the shards. Case-level evidence surfaced as follows; IDs 006 and 007 have no standalone per-case result in the published check annotations and are deliberately marked **unconfirmed**, not assumed to pass.

| ID | Observed standalone result | Result |
|---|---|---|
| TC-CALC-001 | `14` | **PASS** |
| TC-CALC-002 | `20` (run 40294118915) | **PASS** |
| TC-CALC-003 | `0.3` (run 40294118915) | **PASS** |
| TC-CALC-004 | `220` | **PASS** |
| TC-CALC-005 | `3` | **PASS** |
| TC-CALC-006 | No standalone per-case outcome surfaced | **UNCONFIRMED** |
| TC-CALC-007 | No standalone per-case outcome surfaced | **UNCONFIRMED** |
| TC-CALC-008 | `0.9999999999` | **FAIL — DEF-3219-01** |
| TC-CALC-009 | `1e+15+1` / `Error` | **FAIL — DEF-3219-02** |

This is not a complete direct verification of guide section F: the standalone icon and zero-permission claim were not inspected, and cases 006–007 remain unconfirmed on that APK.

## 30-case guide coverage plan

**Profiles:** N = normal; E = edge/negative/boundary; B = blind black-box probe. “Source CI green” refers to the aggregate upstream runs listed above, not to execution of that row against the supplied APK.

| # | Guide | Profile | Planned check | Exact distribution APK result |
|---:|---|:---:|---|---|
| 01 | A1–A2 | N | Honeycomb home-screen icon; header mark; tapping mark returns home | **Not directly run.** Guide/source CI only; launcher/header visual checks remain open. |
| 02 | B1–B3 | E | Long-press `123456`; verify stock selection pill/handles; drag both boundaries | **Not directly run.** Source instrumented suite reported green; no MySpace distribution gesture run. |
| 03 | B4 | E | Copy a selected substring and paste it elsewhere; ensure display commas are not copied | **Not directly run.** Source CI only. |
| 04 | B5 | E | Cut the held substring and type into the resulting gap | **Not directly run.** Source CI only. |
| 05 | B6–B7 | E | Tap outside to dismiss menu/selection; AC clears held text and menu | **Not directly run.** Source CI only. |
| 06 | B8 | E | Selection drag wins over horizontal scrolling; long expression scrolls when unselected | **Not directly run.** Source CI only. |
| 07 | C1–C2 | N | Long-expression layout, live-answer emphasis, expression gradient and key colors | **Not directly run.** Visual styling not validated on the supplied APK. |
| 08 | C3, C8 | E | Mid-number insertion and stable visible caret at next input location | **Not directly run.** Source UI suite aggregate green only. |
| 09 | C4 | E | Insert minus after multiplication without consuming `×` | **Not directly run.** Guide's named source UI test is covered by aggregate source CI; no distribution-APK run. |
| 10 | C5 | N | `200 + 10% = 220` | **PASS** on MySpace (TC-CALC-004) and MyCalc (TC-CALC-004). |
| 11 | C6 | N/E | Precedence plus bracket handling; include unclosed `(5+3 = 8` edge | **PARTIAL PASS.** MySpace precedence/parentheses passed (TC-CALC-001/002); unclosed-bracket auto-balance subcase not directly run. |
| 12 | C7 | E | Repeated `( )` key chooses the bracket that fits at the caret | **Not directly run.** Source CI only. |
| 13 | C9 | E | Confirm the device keyboard never appears | **Not directly run.** Source CI only. |
| 14 | D1 | E | `2 ( ) 5 + 2 ( ) 2 = 28` implicit multiplication | **Not directly run** on the distribution APK. |
| 15 | D2–D3 | E | Replace pending operator; verify `5 + = 10` behavior | **Not directly run** on the distribution APK. |
| 16 | D4 | N | `123456` displays `1,23,456`; grouping remains display-only | **Not directly run** on the distribution APK. |
| 17 | D5 | N | Expand/fold scientific panel and verify listed keys; calculate `√9 = 3` | **PARTIAL PASS.** Square-root calculation passed on both APKs (TC-CALC-005); panel visuals/toggle not directly tested. |
| 18 | D6 | E | `Inv` + `sin` inverse function; Deg/Rad toggle | **PARTIAL PASS.** `sin(30)=0.5` passed on MySpace (TC-CALC-006); inverse and Rad toggle not tested; standalone result unconfirmed. |
| 19 | D7–D8 | E | AC clears selection; backspace removes exactly one character at caret | **Not directly run.** Source CI only. |
| 20 | E1–E2 | N/E | History ordering, persistence/restore, and swipe-down entry | **PARTIAL PASS.** MySpace history persisted and restored (TC-CALC-007); swipe-down entry and all-history ordering not directly checked. |
| 21 | E3 | E | Exactly five menu items plus Effects; Memory popup can reorder/recall | **Not directly run** on the distribution APK. |
| 22 | E4 | N/E | Choose effects; at least four keypress animations; persistence | **Not directly run** on the distribution APK. |
| 23 | E5 | E | Page itself does not scroll; expression line/popups scroll internally | **Not directly run** on the distribution APK. |
| 24 | F | N/E | MyCalc identity, own icon, zero permissions, and B/C/D behavior | **PARTIAL.** APK identity verified; direct arithmetic outcomes are listed above. Icon/permission audit and standalone TC-CALC-006/007 remain unconfirmed. |
| 25 | G — Notes | N/E | Create note; pin, recolor, archive | **Not directly run.** Source CI only. |
| 26 | G — Calendar | N/E | Year picker; week/day views; save/trigger reminder and date boundary | **Not directly run.** Source CI only. |
| 27 | G — Music | E | Play library item; notification transport works after leaving screen | **Not directly run.** Source CI only. |
| 28 | G — Recorder | E | Save recording; self-test; permissions, cancel, and storage errors | **Not directly run.** Source CI only. |
| 29 | G — Scanner | E | Capture; move four crop handles; create PDF; rotate/cancel | **Not directly run.** Source CI only. |
| 30 | G — Files/Diagnostics | E | Edit/save/reopen text; diagnostics local save/share/cancel and privacy | **Not directly run.** Source CI only. |

### Additional blind black-box probes

These are deliberately outside the guide's stated examples and were chosen from user-visible arithmetic expectations before inspecting implementation details.

| Probe | Input and expected behavior | MySpace | MyCalc |
|---|---|---|---|
| BND-01 / TC-CALC-008 | `1 ÷ 3 = × 3 =` should return exactly `1` | **FAIL:** `0.9999999999` | **FAIL:** `0.9999999999` |
| BND-02 / TC-CALC-009 | `10^15 = + 1 =` should evaluate to `1000000000000001` | **FAIL:** expression ends in `Error` | **FAIL:** expression ends in `Error` |

## Defect tracker (with investigation comments)

### DEF-3219-01 — Chained calculation loses precision

- **Status:** Open; reproducible
- **Priority / severity:** P2 / Medium — incorrect numeric answer in a normal calculator continuation flow
- **Affected builds:** MySpace `3.12.21` code `58`; MyCalc `1.0.19` code `20`
- **Reproduction:** enter `1 ÷ 3`, press `=`, then `× 3`, then `=`.
- **Expected:** `1`
- **Actual:** `0.9999999999` in both APKs.
- **Comment — 2026-10-26:** Reproduced on the Android 14 emulator in both exact, checksum-pinned APKs. The same output was recorded for MySpace `3.12.19-56` in the earlier QA run (40284113631), so this is a recurring regression, not a one-off OCR mismatch. The intermediate UI showed `0.3333333333` before multiplication.
- **Root-cause note:** Reusing a rounded display value for the next calculation is plausible, but remains unconfirmed. Do not treat it as a proven diagnosis.
- **Suggested follow-up:** Preserve the unrounded numeric result internally across equals-then-operator input; add a regression asserting the final numeric value is exactly one (within the engine's defined precision contract).

### DEF-3219-02 — Scientific-notation result cannot be continued

- **Status:** Open; reproducible
- **Priority / severity:** P2 / Medium — large-value continuation produces an explicit calculation error
- **Affected builds:** MySpace `3.12.21` code `58`; MyCalc `1.0.19` code `20`
- **Reproduction:** enter `10 ^ 15`, press `=`, append `+ 1`, press `=`.
- **Expected:** `1000000000000001` (or an equivalent exact/scientific representation)
- **Actual:** displayed continuation `1e+15+1` is followed by `Error` in both APKs.
- **Comment — 2026-10-26:** Reproduced in the exact distribution APKs. This was an additional blind edge probe, not a failure of a specific guide example. The QA harness originally labelled the visible `Error` as an automation `ERROR`; it was corrected to classify the observed product output as a test **FAIL**, then the three-shard run was repeated.
- **Root-cause note:** The expression parser/validator may reject exponent-formatted result text, but this is a hypothesis pending source-level confirmation.
- **Suggested follow-up:** Keep the internal numeric value separate from its formatted display token, and add an end-to-end test for continuing from a scientific-notation result.

## Limits and interpretation

1. The 30-case plan intentionally covers guide sections A–G, but the current exact-APK E2E harness executes calculator scenarios only. Features outside that path are **not** claimed as verified on the supplied MySpace APK.
2. The pinned source's automated CI was green, and the guide describes broad automated coverage. Those checks are source-level evidence; they do not establish that every screen/gesture in the released APK behaves correctly.
3. Official Google Calculator was not installed in the Android 14 `google_apis` emulator image. No AOSP substitution or third-party APK mirror was used; live parity remains blocked.
4. MyCalc TC-CALC-006 and TC-CALC-007 were selected but lacked standalone per-case evidence in the final published check annotations; they remain unconfirmed in this tracker.
5. No physical handset run, ad inventory audit, or non-calculator MySpace distribution-APK exploratory pass was completed. No app feature or advertising code was changed by this QA work.

## Recommended next steps

1. Fix and regress DEF-3219-01 and DEF-3219-02 in the calculator engine; rerun the exact pinned distributions.
2. Add direct MySpace APK coverage for B/C/E and each G feature, and collect a standalone MyCalc result for cases 006–007.
3. Add the official Google Calculator to a suitable Play-enabled reference environment, if licensing and runner constraints permit, then rerun TC-CALC-010. Do not substitute AOSP Calculator.
