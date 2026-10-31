@PART: PART XII — EXECUTION APPENDICES
@PARTDESC: Step-level scripts the executor runs verbatim: Catalogue-0 case scripts, journey step tables, engine reference tables, 30-second feature demos, severity/SLA matrices, an Android glossary for the owner, the executor quick-start, and document control.

# Appendix Q — Catalogue-0 step scripts (executor-ready)

Environment stamp for every case: fresh install of the pinned APK, airplane mode ON (unless the case tests alarms), OCR reader enabled, screenshots at every assert. States: PASS / FAIL / BLOCKED per §20.1. Scripts use the harness verbs: `tap k`, `longpress region`, `ocr region`, `shot name`, `assert_ocr`, `adb cmd`, `install apk`, `start screen`, `reset state`.

| Case | Script |
|---|---|
| TC-ONE-C-001 | `tap 2 + 3 × 4 =` → `ocr display == "14"` · `AC` · `tap ( 2 + 3 ) × 4 =` → `== "20"` |
| TC-ONE-C-002 | `tap 2 ( 5 + 2 ) =` → `== "28"` · `( 2 )( 3 ) =` → `"6"` · `2 π =` → `"6.283185307"` |
| TC-ONE-C-003 | `200 + 10 % =` → `"220"` · `AC` · `200 × 10 % =` → `"20"` · `50 % =` → `"0.5"` |
| TC-ONE-C-004 | `10 +` → shot · `tap −` → `ocr expr == "10−"` · `AC 5 + =` → `"10"` · `=` again → `"15"` |
| TC-ONE-C-005 | `10 × − =` → `"-10"` · leading `− 5 =` → `"-5"` |
| TC-ONE-C-006 | `( 2 + 3 =` → `"25"` · smart-key: at start `(` inserts pair; after `+` inserts `)` when open |
| TC-ONE-C-007 | `123456` typed → `ocr expr == "1,23,456"` · select all, Copy → `adb clipboard == "123456"` |
| TC-ONE-C-008 | `0.1 + 0.2 =` → `"0.3"` · `1 ÷ 3 × 3 =` → `"1"` (exact-path proof in law logs) |
| TC-ONE-C-009 | `INV sin 0.5 ) =` (DEG) → `"30"` · `ln ( − 1 ) =` → error card text |
| TC-ONE-C-010 | type `2+3` → live `"5"` ≤ 1 frame · type `+` → live disappears (no stale) |
| TC-ONE-C-011 | `123456`, tap caret between 2 and 3 → type `9` → `"1293456"` grouped · `⌫` → `"123456"` |
| TC-ONE-C-012 | longpress `234` (300 ms) → highlight + `ocr pill == "Cut Copy MAdd MUse Paste"` |
| TC-ONE-C-013 | add 5 solves → `adb am force-stop` → relaunch → history count == 5, order exact |
| TC-ONE-C-014 | open history, tap card → expr painted pre-close (frame log) · double-tap → single paint |
| TC-ONE-C-015 | `3+4`, select `4`, memory has `123456` → `MUse` → `3+123456` · `=` → `"1,23,459"` |
| TC-ONE-C-016 | selection on → `AC` → selection gone, expr remains · `AC` → empty |
| TC-ONE-C-017 | selection on → tap elsewhere in expr → pill gone, caret at tap |
| TC-ONE-C-018 | select `456` in `123456` → Cut → shot gap · type `0` → `"1230"` · paste → `"1230456"` |
| TC-ONE-C-019 | clear expr → longpress empty → pill `MUse Paste` · MUse (mem `123456`) → `123456` |
| TC-ONE-C-020 | overflow → Memory → sheet rows + MUse/MAdd/MC + up/down moves persist |
| TC-ONE-C-021 | Settings → Key shape → each of 5 shapes → shot per shape → persists restart |
| TC-ONE-C-022 | overflow → `ocr menu == exactly 6 items in order` |
| TC-ONE-C-023 | shot pad before → Key theme → Rose → shot after → pixel-diff ≥ 10% · restart → Rose |
| TC-ONE-C-024 | Effects → pick Bubbles → `2+2 =` → animation frames captured · persists |
| TC-ONE-C-025 | focus expression, `adb shell ime list` untouched · typing via keys only, no IME window |
| TC-ONE-C-026 | light shot + dark shot → token asserts (expr ink, amber answer, caret color) |

Module smoke scripts (one line each): note create→edit→search→restart; scan import→crop→export PDF; event+15-min alarm on test clock; backup→wipe→restore identity; music import→play 5 s→pause; record 10 s→flag→play; hub search hits 3 modules; mycalc parity C-001…008; flavor zero-permission manifest; airplane cold start all modules.

# Appendix R — Journey step tables (J-01…J-10)

| Journey | Step | Action | Assert |
|---|---|---|---|
| J-01 Scan to note | 1 | import fixture image | page appears in review |
|  | 2 | run OCR (pack on) | text card ≥ 92% accuracy |
|  | 3 | edit one line | text saved |
|  | 4 | → Notes | note created, body contains text |
|  | 5 | open Files → Scans | image present; note link visible in note metadata |
| J-02 Record to minutes | 1 | record 30 s | FGS notification ≤ 200 ms |
|  | 2 | flag at ~10 s | marker row exists |
|  | 3 | Done | file + row; playable |
|  | 4 | Transcribe | segments monotonic; text non-empty |
|  | 5 | → Notes | linked note with transcript + markers |
| J-03 Backup/wipe | 1 | create data (notes/events/recording) | counts baseline |
|  | 2 | backup (pass `test-1234`) | `.msone` in Backups; manifest hashes ok |
|  | 3 | `pm clear` | fresh state |
|  | 4 | restore from backup | counts match; hashes match; history restored |
|  | 5 | wrong passphrase attempt | clean failure, original data untouched |
| J-04 Calculator day | 1–12 | C-001…C-026 compressed set | all pass in one session |
| J-05 Airplane pass | 1 | airplane ON, cold start | hub interactive |
|  | 2 | one action per module | all succeed; logcat: zero net attempts |
| J-06 Death storm | 1 | draft note A, calc expr B, start recording C | states active |
|  | 2 | `am kill` ×3 | relaunch each time |
|  | 3 | reopen all three | A text, B expr+caret, C still recording (FGS) or finalized cleanly |
| J-07 Fresh low-end | 1 | E26C 2 GB + battery saver | smoke suite green |
|  | 2 | full J-04 subset | no ANR (watch checks) |
| J-08 TalkBack day | 1 | enable TalkBack | J-04 subset + note create completable |
|  | 2 | scan a11y tree | no unlabeled controls on visited screens |
| J-09 MyCalc parity | 1 | install flavor | home = calculator |
|  | 2 | C-001…008 | identical outcomes |
|  | 3 | dex scan | zero module classes; zero cross-module strings |
| J-10 Storage-full | 1 | fill storage < 50 MB | banner once |
|  | 2 | try record | graceful refusal, message |
|  | 3 | try scan | graceful refusal at shutter |
|  | 4 | verify existing data | no corruption (quick_check ok) |

# Appendix S — Engine reference tables

Operator precedence (high→low): `!` `%` (postfix) → unary `−` → `^` (right) → `× ÷` implicit → `+ −`. Parentheses override; functions bind like unary.

| Token class | Members | Lexer notes |
|---|---|---|
| NUM | `0-9 .` | one dot; `_` separators accepted in paste, stripped |
| OP | `+ − × ÷ ^` | unicode + ASCII aliases normalized |
| BRACKET | `( )` | depth cap 32 (TooDeep → syntax error) |
| CONST | `π e` | exact rationals? no — inexact path entry |
| FUNC | `sin cos tan asin acos atan ln log √` | open-bracket inserted |
| POSTFIX | `! %` | domain/context rules §17.1.5 |

Error cards (exact copy): `Cannot divide by zero` · `Outside domain (e.g., log of a negative number)` · `Can't calculate this yet — check the highlighted part` · `Expression is too long` · `Result is too large to display` · `Number too deep in brackets`.

Selection state machine: `IDLE →(long-press 300 ms) PILL_SHOW →(slide) RESIZING →(lift) PILL_SHOW →(tap inside) CARET_MOVE → IDLE`; `AC` from PILL_SHOW → CLEAR_SELECTION → IDLE; history replay/`=` → IDLE (selection cleared).

Live-answer pipeline: keystroke → store update → engine job (cancel previous) ≤ 1 ms → render. Budget breach (> 1 ms measured over rolling 50 ops) → job hops to Default with 50 ms cap, result annotated in diagnostics only.

# Appendix T — Thirty-second demo script per feature (owner acceptance aid)

| Feature | How to see it in 30 seconds |
|---|---|
| F-001 precedence | `2+3×4=` → 14 |
| F-002 implicit | `2(5+2)=` → 28 |
| F-003 percent | `200+10%=` → 220 |
| F-004 pending op | `5+=` → 10, again → 15 |
| F-007 grouping | type `123456` → `1,23,456`; copy → bare |
| F-008 exactness | `1÷3×3=` → 1 |
| F-010 live answer | type `2+3` → amber 5 under field |
| F-012/13 selection | hold `123456`, slide to grow/shrink |
| F-019/20 memory | select number → MAdd → select in expr → MUse |
| F-021/22 history | three solves → history → tap top card |
| F-027 themes | ⋮ → Key theme → Rose |
| F-028 shapes | ⋮ → Key shape → Circle |
| F-031 effects | ⋮ → Effects → Bubbles → `2+2=` |
| F-035 dark mode | system dark toggle → amber answer, white caret |
| F-041 hub search | hub → "rent" → grouped hits |
| F-047 notes | new note → checklist → home → back |
| F-057 OCR | scan fixture page → text card |
| F-061 recurrence | event → Repeat → Monthly on 31st → Feb preview skips |
| F-062 alarm | event in 2 min, alert 1 min → heads-up |
| F-067 backup | backup → wipe → restore |
| F-070 playback | import folder → play → speed 1.5× |
| F-073 recorder | record → pause → resume → flag → done |
| F-076 transcribe | recording → Transcribe → segments |
| F-081 packs | Diagnostics → import dummy pack → verified chip |

# Appendix U — Severity, priority and SLA matrices

| Severity | Definition | Examples | Release rule | Fix SLA (agent-iterations) |
|---|---|---|---|---|
| S1 | Crash, data loss, security violation | restore wipes data; engine wrong on money math | blocks release, always | immediate |
| S2 | Core feature broken, no workaround | percent wrong; history lost on restart | blocks without waiver | ≤ 2 iterations |
| S3 | Feature degraded, workaround exists | theme not persisting on one OEM path | gate-report waiver | ≤ 5 |
| S4 | Polish | spacing, copy tweak | never blocks | backlog |

Priority (P0–P3 for defects) = severity × feature priority (§10) lookup table in `qa/severity.yaml`; disputes resolve toward the higher. Rejected defects require a reason class: `not-a-defect`, `as-designed` (ledger ref), `cannot-reproduce` (evidence attached), or `duplicate` (id).

# Appendix V — Android/compose glossary for the owner

| Term | Plain meaning |
|---|---|
| APK | the installable app file |
| AAB | Play-store format (not used here — sideloads need APK) |
| API level | Android version number (26 = Android 8, 33 = 13, 35 = 15) |
| Compose | the UI toolkit the app is built with |
| Room | the on-device database layer over SQLite |
| FTS | full-text search index inside that database |
| DataStore | small settings storage |
| FGS | foreground service — the persistent notification for recording/playback |
| SAF | the system file-picker permission model for folders |
| MediaStore | Android's shared media index (music import path) |
| TalkBack | Android's screen reader |
| Doze | the system's deep-sleep power state |
| R8 | the code shrinker/optimizer for release builds |
| Robolectric | JVM tests that fake Android |
| Espresso/UIAutomator | on-device UI test drivers |
| Roborazzi | screenshot test tool |
| adb | the device control bridge the QA harness uses |
| SHA-256 | the file fingerprint used for provenance |
| ANR | "application not responding" system dialog |

# Appendix W — Executor quick-start (first working session)

```
1. Clone the repo; open docs/blueprint/myspace-one-development-blueprint.pdf
2. Read: §front, Ch 1, Ch 15, Ch 19  (30 min)
3. Initialize the task graph: docs/plan/task-graph.yaml with G1 slice (§19.6)
4. Bootstrap: `gradle wrapper && gradle assembleFullDebug assembleMycalcDebug`
5. Verify CI fast lane green on an empty-hub skeleton commit
6. Enter the G2 loop; per task: read binding §, write tests, implement, verify, commit with Refs
7. End of session: task graph statuses + session log (Appendix L template)
Cadence rules: never skip local verification; never commit red; evidence paths in every task row.
```

The build is designed so that *any* competent executor — human or AI — can resume from the task graph + ledger alone. That property (resumability without oral history) is itself a success criterion of the blueprint.

# Appendix X — Document control

| Field | Value |
|---|---|
| Title | MySpace One — Application Development Blueprint |
| Version | 1.1 |
| Status | Approved for build execution (G0 artifact) |
| Date | 31 October 2026 |
| Author | Prepared by the AI build agent program for the owner of tarungittarun/AIA- |
| Audience | Autonomous build agent (primary); product owner; future maintainers |
| Source files | `docs/blueprint/content/*.md` (this PDF is generated; regenerate, never hand-edit) |
| Build command | `.venv/bin/python tools/blueprint/build_pdf.py --content docs/blueprint/content --out docs/blueprint/myspace-one-development-blueprint.pdf` |
| Figures | `tools/blueprint/figures.py` (regenerate before build if diagrams change) |
| Revision policy | Every feature/spec change lands its doc delta in the same merge (docs-drift CI gate §24.4) |

Revision history:

| Ver | Date | Change |
|---|---|---|
| 1.0 | 31 Oct 2026 | Initial complete blueprint: Parts I–XII, 32 chapters + appendices A–X |
| 1.1 | 31 Oct 2026 | Line-by-line correction pass (all § refs resolved, draft-style notes removed, tables normalized); new UI design-language material §6.12–§6.19 incl. Figma workflow, screen/frame registry, redlines and design-QA gate; 20 figures; appendices regrouped (M–P joined E–P); screen inventory superseded by §6.14 |

End of document.

# Appendix Y — Owner's personal acceptance manual (module by module)

How the owner verifies each module by hand in ~15 minutes total. The automated suites say the same things; this appendix translates them into thumb-actions.

**Calculator (4 min).** Open the app. Type `2+3×4` — expect `14` live. `=` — history appears. Type `123456` — expect `1,23,456`. Copy it, paste into Notes — expect bare `123456`. Hold on part of the number — pill appears; slide to grow/shrink; MAdd. Type `3+4`, select `4`, MUse — expect `3+123456` → `1,23,459`. `5+` `=` — expect `10`. `1÷3×3=` — expect exactly `1`. Open ⋮ — six items exactly. Key theme → Rose — keys recolor instantly. Swipe down — history. Restart the app — history and theme survive.

**Notes (2 min).** New note → checklist "milk, rice, turmeric" → check two → list shows 2/3. Kill app mid-typing → reopen → text intact. Search "milk" → hit with highlight. Delete → Undo comes back. Trash shows it 30 days.

**Scanner (2 min).** Import an image (or shoot a page). Crop applies. OCR runs — text editable. → Notes creates the note. Without the Essentials pack: the button explains itself and capture/export still work.

**Calendar (2 min).** New event tomorrow 13:36, alert 15 min, repeat monthly on the 31st — preview shows Feb skipped. Notification appears at 13:21 (test with a 2-minute event). ICS export into Files, delete event, import back.

**Files (2 min).** Add a SAF folder. Rename/move a file. Analyzer shows the donut. Backup → wipe data → restore with passphrase — everything returns. Wrong passphrase — clean failure.

**Music (1.5 min).** Import folder → play → 1.5× speed → sleep timer 15 min → headset button next/prev. MiniPlayer persists while checking a note.

**Recorder (1.5 min).** Record 30 s → flag mid-way → done. Play, tap marker to seek. Transcribe (Speech pack) → segments with timestamps → → Notes.

**Diagnostics + About (1 min).** Run self-test — six greens. About shows the exact commit and APK SHA-256 printed in the release notes. Model packs panel shows what's installed with SHAs.

**Privacy spot-check (1 min).** Airplane mode ON. Everything above still works. App info → Permissions — the full app shows only the expected set; MyCalc shows none.

**Flavor (1 min).** Install MyCalc beside MySpace One — separate icon, calculator-first, zero module mentions, zero permissions.

# Appendix Z — Model cards (pack provenance summaries)

Shipped with each pack (full cards in pack LICENSE/cards.md; summaries normative here):

**Essentials (OCR + labels + embeddings).** Models: DBNet-lite (text detection), CRNN en (recognition), MobileNetV3 (labels), MiniLM-L6 int8 (embeddings). Intended use: printed/hand-printed Latin text in photos of pages, labels for photo organization, semantic search over the user's own notes. Out of scope: handwriting cursive, non-Latin scripts v1, tabular extraction. Eval: §16.8 thresholds (92% char acc, recall@10 0.8). Limitations: low-light/blurred images degrade; confidence badges surface doubt. Data: models are static weights; the app sends them nothing.

**Speech (whisper).** Model: whisper-tiny int8 (base optional Tier A). Intended use: transcribing the user's own recordings, en-first with autodetect within whisper's language set. Out of scope: real-time captioning v1, speaker diarization. Eval: ≤ 12% WER fixture set. Limitations: heavy accents/noise raise WER; timestamps monotonic but segment boundaries approximate.

**Assistant (small LLM).** Model: gemma-2B-it 4-bit (alt: Qwen2.5-1.5B-it 4-bit) via MediaPipe. Intended use: summarize/rewrite/checklist-ify the user's selected text; parse one event from a phrase. Out of scope: open-ended chat, factual QA (no knowledge source on device), generation without preview. Eval: rubric ≥ 4/5 on fixture notes; JSON schema discipline 100% after retry. Limitations: ~1.6 GB RAM class; Tier A only; outputs always previewed with undo; provenance recorded.

# Appendix AA — Program FAQ

**Q: Why 26 minimum when most phones are newer?** The owner distributes to real-world mixed hardware; Android 8 covers the tail cheaply (we avoid APIs that would force 30+).

**Q: Why Koin over Hilt?** Build speed and simpler kapt-free setup on the constrained CI (ADR-04); both would satisfy the architecture.

**Q: Why is `5+ = → 10` a release blocker?** It is the owner's named parity behavior (Google Calculator rule) and a historical pain point; F-004/TC-ONE-C-004 encode it.

**Q: What if the AI packs never ship?** The product ships and passes release without them; every AI affordance degrades per §16.7. Packs accelerate later, never gate now.

**Q: Why no WorkManager for reminders?** Exact alarms need AlarmManager anyway; one scheduling path beats two half-paths (ADR-10).

**Q: Can the agent add a module the owner didn't list?** No (§1.4). Proposals go to the ledger as decisions for the owner, not into the build.

**Q: Why FTS4 not FTS5?** API 26's SQLite ships FTS4 unconditionally (ADR-02); porting to FTS5 can be a v2 decision after floor-raising.

**Q: How big can my library/notes get?** Design targets: 50k tracks, 20k notes, 5k recordings stay within budgets (§23.6); beyond that, performance work is a ledger task, not a surprise.

**Q: What stops the agent from "green-washing" a failed run?** The report builder only reads manifest-verified artifacts; publisher success is structurally separate from case results (§22.5); the owner reads per-case tables, not job dots.

**Q: How do I (owner) request a change?** File it against the blueprint: a spec delta PR + traceability update; the agent implements in the normal loop. Changes to constraints (C1–C10) need an explicit owner decision entry.

# Appendix BB — Index of figures

| Fig | Title | Section |
|---|---|---|
| Cover | Honeycomb emblem (brand motif) | cover |
| 1 | Combined-app product map | §5.1 |
| 2 | Navigation graph | §5.2 |
| 3 | Figma workflow (design↔code loop, access policy) | §6.13 |
| 4 | Layered architecture | §11.1 |
| 5 | Calculator basic pad + scientific panel | §7.2 |
| 6 | History / memory / key-theme surfaces | §7.2.5 |
| 7 | Notes list + editor | §7.3 |
| 8 | Scanner viewfinder + OCR card | §7.4 |
| 9 | Calendar month+agenda + editor | §7.5 |
| 10 | Files browser + analyzer | §7.6 |
| 11 | Music library + player | §7.7 |
| 12 | Recorder capture + saved view | §7.8 |
| 13 | Diagnostics + model packs | §7.9 |
| 14 | Room schema ERD | §12.2 |
| 15 | Phase-gate lifecycle | §15.5 |
| 16 | AI stack (orchestrator, runtimes, tiers) | §16.4 |
| 17 | Device capability ladder | §16.8 |
| 18 | Test pyramid + CI pipeline | §20.1 |
| 19 | Defect lifecycle | §20.9 |

Tables are numbered by their section (e.g., "the §17.1.5 table"); the executive anchor tables are: constraints §1.3, promises §1.2, Catalogue-0 §20.6, settings registry §17.7/§17.12, budgets §23.6, risks Ch 30, screen registry §6.14, traceability §27.2.

# Appendix CC — Constraint → architecture traceability (why the structure is what it is)

| Constraint | Architectural embodiment | Fail-loud mechanism |
|---|---|---|
| C1 no internet permission | manifest allow-list; Konsist no-network rule; dex scan | CI gates (SC-01/03) |
| C2 no sign-in | no auth code path exists; About/identity only local | code review checklist §18.4 |
| C3 no ads | dependency deny-list audit | CI dependency-audit |
| C4 private data | ADR-09 storage policy; SAF only user-granted | TC-SEC-* suite |
| C5 packs never download | no download code; import+hash only | TC-PACK-sec-01 |
| C6 API 26 floor | compileSdk 36/minSdk 26; E26C in matrix | emulator matrix |
| C7 calculator parity | §17.1 normative engine; Catalogue-0 | release lane L5 red = stop |
| C8 ≤ 30 jobs / 3 runners | §24 sharding design; concurrency groups | job-count metric in metrics.json |
| C9 calculator-only flavor | Gradle flavor + dex scan (F-040) | CI mycalcNoCrossModule |
| C10 provenance everywhere | BuildConfig SHA; evidence manifests; About screen | S-criteria artifacts |
| P1 offline-first | airplane-mode CI cases; no network vocabulary in strings | J-05, UX-015 |
| P2 privacy structural | §14 threat model; §14.2 structural bans | SC checks 01–12 |
| P3 one home | design-system module; nav audit | TC-NAV-001, screenshots |
| P4 fast & gentle | §23.6 budgets as CI asserts | perf lanes |
| P5 verifiable | Chapters 20–22; §27 traceability | every gate |

# Appendix DD — Traceability CSV extended excerpt (format example)

```csv
feature,area,priority,spec,tests,latest_status,commits,notes
F-001,CALC,P0,§17.1,TC-ONE-C-001;TC-LAW-002,pass,ab12ef0,
F-002,CALC,P0,§17.1.4,TC-ONE-C-002;TC-LAW-005,pass,ab12ef0,
F-003,CALC,P0,§17.1.5,TC-ONE-C-003;TC-LAW-004,pass,cd23f41,
F-004,CALC,P0,§17.1.5,TC-ONE-C-004,pass,cd23f41,owner bug class closed
F-008,CALC,P0,§17.1.2,TC-ONE-C-008;TC-LAW-003,pass,ab12ef0,owner bug class closed
F-013,CALC,P0,§7.2.2,TC-ONE-C-B2,blocked,ef45a62,physical-device input required
F-019,CALC,P0,§7.2.2,TC-ONE-C-015,pass,ef45a62,
F-024,CALC,P0,§17.2,TC-ONE-C-013,pass,ff9012a,
F-027,CALC,P0,§6.2,TC-ONE-C-023,pass,112a3b4,
F-032,CALC,P0,§7.2.6,TC-ONE-C-022,pass,112a3b4,
F-036,NCALC,P0,§23.4,TC-SEC-perm-flavor;J-09,pass,22b4c5d,
F-038,NCALC,P0,§14.4,TC-SEC-perm-flavor,pass,22b4c5d,zero-permission verified
F-041,HUB,P0,§5.3,TC-HUB-001,pass,33c5d6e,
F-047,NOTE,P0,§17.3,TC-NOTE-rt;TC-NOTE-save-01,pass,44d6e7f,
F-050,NOTE,P0,§14.3,TC-NOTE-trash-01,pass,44d6e7f,
F-055,SCAN,P0,§7.4,TC-SCAN-cap-01;TC-SCAN-imp-01,pass,55e7f80,
F-057,SCAN,P0,§16.5,TC-SCAN-ocr-01,pass,55e7f80,pack-gated
F-059,SCAN,P0,§16.2,TC-SCAN-abs-01,pass,55e7f80,
F-060,CAL,P0,§7.5,TC-CAL-alarm-01,pass,66f8091,
F-061,CAL,P0,§17.4,TC-CAL-rr-01,pass,66f8091,200-rule corpus
F-062,CAL,P0,§14.4,TC-CAL-alarm-01;02,pass,66f8091,
F-065,FILE,P0,§7.6,TC-FILE-browse-01,pass,77091a2,
F-067,FILE,P0,§14.3,TC-SEC-backup-01..03,pass,77091a2,
F-069,MUSIC,P0,§7.7,TC-MUSIC-imp-01,pass,881a2b3,
F-070,MUSIC,P0,§7.7,TC-MUSIC-play-01,pass,881a2b3,
F-073,REC,P0,§17.5,TC-REC-svc-01,pass,992b3c4,
F-075,REC,P0,§17.5,TC-REC-fmt-01,pass,992b3c4,
F-081,DIAG,P0,§28.3,TC-DIAG-log-01,pass,aa3c4d5,
F-082,DIAG,P0,§16.8,TC-PACK-mgr-01;TC-PACK-sec-01,pass,aa3c4d5,
F-084,SET,P0,§7.10,TC-SET-about-01,pass,bb4d5e6,
UX-002,UX,P0,§8,TC-perf-coldstart,pass,perf-lane,
UX-015,UX,P0,§8,strings-audit,pass,ci-grep,
UX-019,UX,P0,§8,TC-flavor-strings,pass,ci,
(… full matrix generated per gate: reports/traceability.csv …)
```

# Appendix EE — "If something fails" (owner-facing, honors the old guide's contract)

The owner's original guides said: note the section code, use Settings → Diagnostics → Share log, attach a screenshot. The combined app keeps that contract, upgraded:

1. **In-app self-test first.** Diagnostics → Run self-test: six checks, one JSON card. Share it — it is the fastest triage artifact.
2. **Share the log (previewed).** Diagnostics → Logs → Share: you see the exact text before anything leaves via the share sheet. Section codes from the guides map to module tags in each log line (`[calc]`, `[scan]`, `…`).
3. **Screenshot the moment.** The failure state is designed to be self-describing (error card + one action), but your screenshot anchors it.
4. **What gets asked, and why.** Version + commit (About), device model, airplane-or-not, pack status if AI-related. With those four facts plus the JSON, nearly every defect reproduces from this blueprint's fixtures alone.
5. **What never happens.** No remote debugging, no account checks, no silent uploads — by architecture. Support is evidence you hand over, nothing more.

# Appendix FF — Extension guide (adding a module in v1.1+)

A worked recipe so future growth (Widgets, Voice search, non-Latin OCR…) follows the same laws:

1. **Spec first.** Add a Chapter-9-style feature table with IDs continuing the catalogue; write acceptance criteria before code; extend `qa/testcases.csv`.
2. **Module scaffold.** `feature/<name>/` + contracts in `core/domain`; register in DI + navigation + hub grid (one row in §5.6) + settings registry (§17.12 keys).
3. **Design-system compliance.** Screens use only tokens/components; empty/error/content states; screenshot goldens; a11y labels.
4. **Data rules.** New tables via numbered migration + fixture test; trash/backup coverage (backup `data.json` gains the table; older apps reject newer backups cleanly — already specified).
5. **AI hooks (optional).** New capability → orchestrator `Capability` + pack tier + fallback rung + eval fixtures; never a direct model call in the feature module.
6. **Quality gates.** Journeys, budgets (§23.6 rows for new screens), architecture tests pass; traceability rows complete; blueprint delta lands in the same merge.
7. **Release.** Feature flag via settings registry until Catalogue-0-class set is green; then promote to P0-class in the next minor.

# Appendix GG — Document generation pipeline (how this PDF is built)

```
docs/blueprint/
  content/*.md          # source chapters/appendices (single source of truth)
  figures/              # generated diagrams (tools/blueprint/figures.py)
  myspace-one-development-blueprint.pdf   # generated output
tools/blueprint/
  figures.py            # matplotlib generators → figures/*.png
  build_pdf.py          # markdown → typeset PDF (DejaVu fonts, TOC, bookmarks)
```

Regenerate: `python tools/blueprint/figures.py && python tools/blueprint/build_pdf.py --content docs/blueprint/content --out docs/blueprint/myspace-one-development-blueprint.pdf`. Rules: never hand-edit the PDF; content changes land with their feature changes (docs-drift gate); figures regenerate deterministically (seeded); the PDF asserts ≥ 200 pages at build time so trimming by accident fails loudly.

End of appendices.

# Appendix HH — Build files (bootstrap reference)

`settings.gradle.kts`:

```kotlin
pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement {
    repositories { google(); mavenCentral() }
}
rootProject.name = "myspace-one"
include(":app",
        ":feature:calculator", ":feature:notes", ":feature:scanner",
        ":feature:calendar", ":feature:files", ":feature:music",
        ":feature:recorder", ":feature:diagnostics", ":feature:hub",
        ":feature:settings",
        ":core:designsystem", ":core:domain", ":core:data",
        ":core:ai", ":core:common", ":core:testing")
```

Root `build.gradle.kts` (conventions excerpt):

```kotlin
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
    alias(libs.plugins.room) apply false
}
subprojects {
    // shared: kotlin jvm target 17, minSdk 26 via convention plugin
}
```

`app/build.gradle.kts` key block (flavors + provenance; see §23.7 for the full DSL):

```kotlin
android {
    namespace = "app.space.one"
    compileSdk = 36
    defaultConfig {
        minSdk = 26; targetSdk = 35
        versionCode = 31300; versionName = "3.13.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    // flavors per §23.7; signing per §25.2
}
```

Module convention (each `feature/*`):

```kotlin
plugins { id("myspace.android.feature") }   // convention plugin: compose + koin + lint
android { namespace = "app.space.one.feature.calculator" }
dependencies {
    implementation(project(":core:designsystem"))
    implementation(project(":core:domain"))
    implementation(project(":core:data"))
    testImplementation(project(":core:testing"))
}
```

`core/domain` stays a pure Kotlin (`java-library` + kotlinx-coroutines-core only) module — its `build.gradle.kts` must not contain `android.*` blocks at all, enforced by a CI check (the architecture test that keeps the engines JVM-testable).

# Appendix II — G1 day-by-day plan (first sprint, executor-ready)

| Day | Tasks (§19.6) | Definition of done for the day |
|---|---|---|
| 1 | T-BOOT-001 workspace | `gradle help` green; version catalog resolves; wrappers pinned |
| 2 | T-BOOT-002 flavors | both flavors assemble empty activities; namespaces correct |
| 3 | T-BOOT-003 CI fast lane | PR lane green on GitHub Actions runners ≤ 12 min |
| 4 | T-BOOT-004 empty hub | hub renders on E33B; screenshot test records golden |
| 5 | T-BOOT-005 provenance | BuildConfig SHA/time visible in a debug About row |
| 6 | T-BOOT-006 keystore | generated in secret store; owner backup receipt filed; rehearsal signed test APK |
| 7 | T-BOOT-007 screenshot harness | Roborazzi runs in lane; diff artifacts upload on failure |
| 8 | T-BOOT-008 G1 report | gate report committed with artifact paths; defects/ledger current |

Rules for the sprint: no task starts without its dependency closed; every day ends with a green tree (or a quarantined flake with an owner); the report is written by the evidence, never from memory. This sprint is the template for every later one — plan, execute, verify, record.
