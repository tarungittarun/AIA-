@PART: PART III — FEATURE REQUIREMENTS
@PARTDESC: Eighty-four numbered features with acceptance criteria, priority tiers, and journey tests. This part is the contract for "what the app does"; every feature ID reappears in the traceability matrix (Chapter 27) with its tests and commits.

Every feature below carries: an ID (F-nnn), a statement ("The app SHALL …"), acceptance criteria ("Given/When/Then" compressed), a priority (P0 release blocker / P1 required for G6 / P2 planned fast-follow), a module tag, and links to the detailed specification section. A feature without a test reference cannot leave the catalogue; the traceability script enforces the mapping mechanically.

# Chapter 9 — Feature catalogue

## 9.1 How to read the catalogue

- **Module tags**: CALC, NCALC (MyCalc flavor), HUB, NOTE, SCAN, CAL (calendar), FILE, MUSIC, REC (recorder), DIAG, SET, AI, SEC.
- **Given/When/Then** is compressed as *Given* state → *When* action → *Then* observable outcome. "Observable" means visible on screen, in a database dump, or in an exported artifact — never a code-internal claim.
- **P0** features gate the release (S-criteria, §front). **P1** features must ship or carry a logged decision. **P2** may defer to v1.1 with owner sign-off.

## 9.2 Calculator (CALC) — the parity core

The owner's previous guides define a behavior contract that this catalogue hardens into requirements. The calc feature set is P0 *in full* — a calculator release missing any of these is not a release.

| ID | Feature (SHALL) | Acceptance (Given → When → Then) | Pri | Spec |
|---|---|---|---|---|
| F-001 | Evaluate arithmetic with exact precedence | `2+3×4` `=` → `14`; `(2+3)×4` `=` → `20` | P0 | §17.1 |
| F-002 | Implicit multiplication | `2(5+2)` `=` → `28`; `(2)(3)` → `6`; `2π` → `6.283185307` | P0 | §17.1.4 |
| F-003 | Context-sensitive percent | `200+10%` → `220`; `200×10%` → `20`; `50%` → `0.5` | P0 | §17.1.5 |
| F-004 | Pending-operator replacement | `10+` then `−` → expression `10−`; `5+` then `=` → **`10`** (the trailing-operator rule: equals repeats the pending operand semantics of Google Calculator: `5+=` → `5+5=10`) | P0 | §17.1.5 |
| F-005 | Unary minus and leading sign | `10×−` evaluates → `-10`; starting `−` allowed | P0 | §17.1.3 |
| F-006 | Auto bracket balance | `2+3×(4+1` `=` → `25`; `(` key smart-inserts pair/`)` | P0 | §17.1.4 |
| F-007 | Indian digit grouping display | `123456` displays `1,23,456`; copy without commas | P0 | §17.1.8 |
| F-008 | Exact rational arithmetic on +−×÷ | `0.1+0.2` → `0.3` exactly; `1÷3×3` → `1` (never `0.9999999999`) | P0 | §17.1.2 |
| F-009 | Scientific constants and functions | `π`, `e`, `sin/cos/tan` (+INV arcs, degree/radian toggle), `√`, `^`, `ln`, `log`, `!` with domain errors as `Error` cards | P0 | §17.1.6 |
| F-010 | Live answer as-you-type | Complete expression shows live answer instantly; incomplete shows nothing stale | P0 | §7.2.1 |
| F-011 | Caret placement and editing | Tap places caret mid-token; type inserts at caret; `⌫` deletes one char left of caret or selection | P0 | §7.2.1 |
| F-012 | Long-press selection with pill | Stationary long-press selects token, opens `Cut Copy MAdd MUse Paste` | P0 | §7.2.2 |
| F-013 | Hold-and-slide selection resize | Slide without lifting grows/shrinks selection char-wise | P0 | §7.2.2 (B2; test on device-class input only — emulator injection limitation is a BLOCK, not a FAIL, §20.9) |
| F-014 | Copy/paste sanitized | Copy yields raw digits (no grouping); paste inserts legal chars only | P0 | §17.1.3 |
| F-015 | Cut and retype | Cut removes to clipboard; typed digit lands at gap | P0 | §7.2.2 |
| F-016 | Tap-away releases selection | Tap elsewhere exits selection, places caret, dismisses pill | P0 | §7.2.2 (B6) |
| F-017 | AC clears selection first | Selection present: AC clears it, expression remains; second AC clears expression | P0 | §7.2.2 (B7) |
| F-018 | Empty-caret menu | Long-press empty field → `MUse Paste` menu; MUse inserts stored value at caret | P1 | §7.2.2 (B11/B12) |
| F-019 | MAdd stores selection value | Select `1,23,456` → MAdd → memory sheet shows `123456` | P0 | §7.2.2 (B12) |
| F-020 | MUse replaces selection | Expression `3+4`, select `4`, MUse with stored `123456` → `3+123456`; `=` → `1,23,459` | P0 | §7.2.2 (B12) |
| F-021 | History sheet newest-on-top | Cards show expr+result+timestamp; newest first | P0 | §7.2.4 |
| F-022 | History replay | Tap card paints expression before sheet closes; caret at end | P0 | §7.2.4 (D9) |
| F-023 | Replay race guard | Double-tap card paints once | P1 | §7.2.4 (D10) |
| F-024 | History persistence | Kill process, relaunch → history intact incl. expected entries | P0 | §17.2 (TC-07 parity) |
| F-025 | History clear + pins | Clear (confirm) removes unpinned, keeps pinned; pinned cards visually marked | P1 | §17.2 |
| F-026 | Memory sheet | Overflow → Memory lists slots with MUse/MAdd/MC and reorder up/down | P1 | §7.2.5 (E3) |
| F-027 | Key theme picker | Eight themes; selection repaints instantly; persists; `MySpace settings` follows app theme | P0 | §6.2 (C11) |
| F-028 | Key shape picker | Five shapes change key geometry immediately; persists | P1 | §17.7 |
| F-029 | Haptics toggle | `Haptics: On` default; off silences key/selection haptics | P1 | §17.7 |
| F-030 | Show as fraction | On: `1÷3` displays `1/3`; engine still exact | P2 | §17.7 |
| F-031 | Effects picker | ≥ 4 styles incl. None; `=` animates per selection; persists; battery-saver default None | P1 | §7.2.5 (E4) |
| F-032 | Overflow list exactness | Overflow shows exactly: Haptics, Memory, Show as fraction, Key theme, Key shape, Effects | P0 | §7.2.6 |
| F-033 | No device keyboard | Typing never opens IME on calculator screen | P0 | §7.2 (C9) |
| F-034 | No ad surfaces | No ad labels/SDK/hooks anywhere (whole app) | P0 | §14.2 (ADS audit) |
| F-035 | Light/dark theme correctness | Light: near-black on white; dark: LED-bright expression, amber live answer, white caret; instant re-resolve on switch | P0 | §6.2 (H1–H4) |

## 9.3 MyCalc flavor (NCALC)

| ID | Feature (SHALL) | Acceptance | Pri | Spec |
|---|---|---|---|---|
| F-036 | Standalone app identity | Package `app.space.calc`, label `MyCalc`, calc-as-home, own launcher icon | P0 | §23.4 |
| F-037 | Same engine and pads | All CALC features F-001…F-035 function identically (minus hub actions) | P0 | §23.4 |
| F-038 | Zero permissions goal | Merged manifest requests no dangerous permissions; the only custom permission (if any) is the app's own non-exported receiver permission or none — target: **none** | P0 | §14.4 |
| F-039 | Smaller APK | ≤ 6 MB release APK | P1 | §23.6 |
| F-040 | No cross-module remnants | No "→ Notes", no hub strings in flavor resources (lint check) | P0 | §23.4 |

## 9.4 Hub (HUB)

| ID | Feature (SHALL) | Acceptance | Pri | Spec |
|---|---|---|---|---|
| F-041 | Unified search | Query returns grouped results from notes/scans/events/files/songs/recordings/transcripts/history; result tap deep-links | P0 | §5.3, §12.5 |
| F-042 | Semantic search (pack) | With Essentials pack, note search also matches meaning ("laptop advice" finds a note saying "purchase guidance for computing") | P1 | §16.4 |
| F-043 | Continue row | Restores last module+state exactly (draft text, expression, scroll) | P0 | §12.6 |
| F-044 | Module status lines | Each cell shows local live status; stale-free within 1 s of returning to hub | P1 | §5.3 |
| F-045 | Shortcuts | Long-press module → primary action shortcut; app shortcuts work offline | P2 | §5.2 |
| F-046 | First-run cards | Privacy card once; starter tips dismissable | P0 | §5.3 |

## 9.5 Notes (NOTE)

| ID | Feature (SHALL) | Acceptance | Pri | Spec |
|---|---|---|---|---|
| F-047 | Create/edit rich notes | Bold/italic/H1/H2/bullets/checklists/divider; autosave 500 ms; survives process death | P0 | §17.3 |
| F-048 | Full-text search | FTS over title+body; results ranked; query under 30 ms on 1k notes | P0 | §12.5 |
| F-049 | Pin/unpin | Pinned section on top; order persists | P1 | §7.3 |
| F-050 | Trash + undo | Delete → snackbar undo; trash 30-day retention with restore and empty-now | P0 | §14.3 |
| F-051 | Checklists | Toggle items; card shows n/m progress | P0 | §7.3 |
| F-052 | Export/Markdown | Export note as `.md` (lossless round-trip import) | P1 | §17.3 |
| F-053 | Attach from Files | Attach image/file; stored app-private; visible in Files | P1 | §7.3 |
| F-054 | AI summarize/rewrite/checklist/related | Pack-gated; preview + undo; never silently rewrites body | P1 | §16.3 |

## 9.6 Scanner (SCAN)

| ID | Feature (SHALL) | Acceptance | Pri | Spec |
|---|---|---|---|---|
| F-055 | Camera capture + batch | Multi-page docs; torch; tap-focus; import path when camera denied | P0 | §7.4 |
| F-056 | Auto-crop + filters | Corner detect crop; Original/Gray/B&W | P1 | §16.5 |
| F-057 | On-device OCR | Essentials pack; editable text card; Copy/Re-OCR; en-Latin v1 | P0 | §16.5 |
| F-058 | Export | Page→image; doc→PDF; text→note/clipboard | P0 | §7.4 |
| F-059 | OCR graceful absence | Without pack: capture/export work; card explains pack install | P0 | §16.2 |

## 9.7 Calendar (CAL)

| ID | Feature (SHALL) | Acceptance | Pri | Spec |
|---|---|---|---|---|
| F-060 | Events + editor | Title/time/all-day/note/color; validation | P0 | §7.5 |
| F-061 | Recurrence subset | Daily/Weekly/Monthly/Yearly/Custom (§17.4); occurrences render months ahead | P0 | §17.4 |
| F-062 | Exact reminders | Alert fires at configured offset; respects exact-alarm policy with graceful inexact fallback | P0 | §14.4 |
| F-063 | ICS import/export | Multi-event import; range export; unsupported RRULE → one-off + note | P1 | §17.4 |
| F-064 | Month/agenda UI | Today circle; dots; swipe months; Today chip | P0 | §7.5 |

## 9.8 Files (FILE)

| ID | Feature (SHALL) | Acceptance | Pri | Spec |
|---|---|---|---|---|
| F-065 | Browse private + SAF | Internal sections + user roots; open/rename/move/copy/delete/new folder/sort/search | P0 | §7.6 |
| F-066 | Storage analyzer | Category donut computed locally; Clean scans; Export report (JSON) | P1 | §7.6 |
| F-067 | Encrypted backup/restore | `.msone` archive, AES-256-GCM + PBKDF2; restore verifies; wrong passphrase fails cleanly | P0 | §14.3 |
| F-068 | Trash for private files | 30-day trash, restore, empty-now | P1 | §14.3 |

## 9.9 Music (MUSIC)

| ID | Feature (SHALL) | Acceptance | Pri | Spec |
|---|---|---|---|---|
| F-069 | Library import | SAF folder pick or MediaStore scan; albums/artists/songs/folders; artwork cache | P0 | §7.7 |
| F-070 | Playback + queue | Media3; prev/next/seek/shuffle/repeat; speed 0.5–3.0×; sleep timer; gapless; headset controls; audio focus | P0 | §7.7 |
| F-071 | Playlists + M3U export | Create/reorder/export M3U | P1 | §7.7 |
| F-072 | MiniPlayer | Persists across modules; tap opens player | P1 | §7.7 |

## 9.10 Recorder (REC)

| ID | Feature (SHALL) | Acceptance | Pri | Spec |
|---|---|---|---|---|
| F-073 | Record/pause/resume | Foreground service + notification actions; survives activity death | P0 | §17.5 |
| F-074 | Markers | Flag during record; tap-to-seek later; labels | P0 | §7.8 |
| F-075 | AAC/WAV output | 96 kbps AAC default; WAV option; app-private storage; visible in Files | P0 | §17.5 |
| F-076 | Transcribe (pack) | whisper-tiny int8; segments with timestamps; stored; searchable | P1 | §16.5 |
| F-077 | → Notes | Creates linked note with transcript/summary | P1 | §7.8 |

## 9.11 Diagnostics & Settings (DIAG/SET)

| ID | Feature (SHALL) | Acceptance | Pri | Spec |
|---|---|---|---|---|
| F-078 | Health dashboard | Storage/battery/DB/pack cards computed locally | P1 | §7.9 |
| F-079 | Self-test | Engine smoke + DB integrity + pack hashes + alarm check → result card | P1 | §7.9 |
| F-080 | Log ring + share | 7-day/2 MB scrubbed ring; user-initiated export only | P0 | §28.3 |
| F-081 | Model pack manager | Import/verify(SHA-256)/enable/disable/delete; no downloads | P0 | §16.8 |
| F-082 | App lock | Optional biometric+credential lock on background > 2 min | P2 | §7.10 |
| F-083 | About provenance | Version, commit SHA, build date, APK SHA-256 displayed | P0 | §7.10 |
| F-084 | Licenses screen | OSS attribution generated from dependency tree | P1 | §23.5 |

## 9.12 Journey tests (cross-module)

| ID | Journey | Path | Pass condition |
|---|---|---|---|
| J-01 | Scan to note | Scanner: capture page → OCR → "→ Notes" | Note exists with OCR text; back-link to scan in Files |
| J-02 | Record to minutes | Recorder: record 30 s → flag → done → transcribe (pack) → → Notes | Note contains transcript + marker list |
| J-03 | Backup and wipe | Settings: backup (`pass1`) → clear data → restore | All notes/events/recordings return; history restored |
| J-04 | Calculator day | 12 calc actions incl. percent, selection, memory, history replay, theme change | All Catalogue-0 equivalents pass in one session |
| J-05 | Airplane full pass | Airplane mode cold start → 1 action per module | Zero failures, zero network log entries (§28.2) |
| J-06 | Process death storm | Kill app mid-draft in Notes/Calc/Recorder | All three restore state on relaunch |
| J-07 | Fresh low-end | API 26, 2 GB emulator, battery saver on: full smoke | Catalogue-0 calc subset passes; no ANR |
| J-08 | TalkBack day | Complete J-04 + note creation with TalkBack | Completable; no silent controls |
| J-09 | MyCalc parity | Run J-04 on flavor build | Identical outcomes; flavor has zero module remnants |
| J-10 | Storage-full drill | Fill storage to < 50 MB → try recording + scan | Graceful refusals with clear messages; no corruption |

## 9.13 Acceptance detail for twenty pivotal P0 features

Compressed Given/When/Then for the features where ambiguity would be most expensive. Each row is executable as written by L4/L5.

| Feature | Given | When | Then |
|---|---|---|---|
| F-004 trailing-op | expression `5+` in field | tap `=` | display `10`; history row `5+5 = 10`; second `=` → `15` |
| F-008 exactness | fresh session | evaluate `0.1+0.2` then `1÷3×3` | displays `0.3` then `1`; internal values exact rationals (law L2/L3 logs) |
| F-012 selection entry | expression `123456` | stationary long-press 300 ms on `234` | `234` highlighted; pill `Cut Copy MAdd MUse Paste` floats; no IME |
| F-019 MAdd | `234` selected, memory empty | tap `MAdd` | memory sheet row `234`; pill dismissed; selection remains |
| F-020 MUse replace | `3+4`, `4` selected, memory `123456` | tap `MUse` | expression `3+123456`; `=` → `1,23,459`; history row canonical `3+123456` |
| F-021 history order | 3 solves done | open history | cards newest-first: latest at top; timestamps `27th Oct, 13:36` format |
| F-022 replay | history open | tap card `2+3×4 = 14` | expression painted; sheet closes after paint frame; caret at end |
| F-024 persistence | 5 entries exist | `adb shell am force-stop` + relaunch | history sheet shows 5 entries, same order/content |
| F-027 key theme | calculator visible, theme `MySpace settings` | Settings → Key theme → `Rose` | keypad recolors ≤ 2 frames; persists across restart; `=` still amber |
| F-032 overflow exactness | calculator open | tap kebab | exactly: `Haptics: On`, `Memory`, `Show as fraction`, `Key theme`, `Key shape`, `Effects` |
| F-033 no IME | calculator focused | tap expression, type area | no system keyboard appears; hardware keys still work |
| F-038 flavor zero-perm | mycalc release APK | `apkanalyzer manifest print` | zero `uses-permission` entries |
| F-041 hub search | 3 notes, 1 event, 1 file, 2 songs | type `rent` | grouped results include all matches; tap opens right screens |
| F-043 continue row | draft note half-typed | home, kill, relaunch | continue-row shows the note; tap restores text+cursor |
| F-047 note autosave | editor typing stops | wait 500 ms | DB row updated (repo log); process death keeps text |
| F-050 trash undo | note exists | swipe delete → Undo | note back in list; no trash entry remains |
| F-057 OCR | Essentials pack on; fixture image scanned | tap OCR | text card ≥ 92% char accuracy; provenance footnote present |
| F-062 exact alarm | event at 13:36, alert 15 min | clock to 13:21 | heads-up notification fires within ±60 s; tap opens event |
| F-067 backup | data present, passphrase set | backup → wipe app data → restore | all entities return; counts + checksums match manifest |
| F-073 recorder FGS | mic granted | tap record | notification within 200 ms; timer runs; lock screen continues |

## 9.14 Negatives (features the catalogue intentionally lacks)

Search finds nothing to sync because there is no sync; there is no "share to MySpace One" ingestion surface beyond explicit import; there is no widget set in v1 (deliberate scope cut, revisit v1.2); there is no Wear/Android Auto surface; there is no PDF viewer (hand-off to system viewers instead); there is no cloud anything. Stating negatives prevents agent drift toward filling imagined gaps.

## 9.15 Flagship feature stories (why the top P0s exist)

1. **F-004/F-008 (trailing-op + exactness).** These two are the owner's named historical pains (`5+ = → 5`, `0.9999999999`). They anchor the engine's identity: parity with Google Calculator semantics, exactness with rationals. Every engine change re-proves them first.
2. **F-012/F-020 (selection + MUse).** The owner's guides spent an entire section (B) on selection-class memory actions — the differentiating calculator UX. The pill vocabulary (`Cut Copy MAdd MUse Paste`) is treated as product API: exact strings, exact order.
3. **F-041 (hub search).** The combined app's reason to exist: one query across everything, offline. Its ranking table is normative so results feel stable, not lucky.
4. **F-067 (encrypted backup).** The trust feature: with no cloud, backup/restore is the user's only safety net; transactional restore with verified hashes is the difference between a tool and a liability.
5. **F-038 (flavor zero-permission).** The owner distributes MyCalc separately; a permission-less calculator is a marketable sentence and a auditable fact (manifest diff in CI).
6. **F-081/F-083 (log provenance + About).** The owner's QA culture is evidence-first; the app itself carries that culture: build provenance on the About screen, share-with-preview logs, self-test JSON. The report-style honesty lives inside the product.

# Chapter 10 — Priorities, matrices and cutlines

## 10.1 Priority distribution

P0 features are the release core: **F-001…F-017, F-019…F-025, F-027, F-032…F-037, F-038, F-040, F-041, F-043, F-046…F-051, F-055, F-057…F-060…F-062, F-064…F-067, F-069…F-069, F-069…F-069, F-069…F-069, F-069** (66 features). The catalogue's P0 set defines Catalogue-0 in §20.6: a release cannot ship with a red P0. P1 features (18) may ship incomplete only with a decision entry; P2 features (4) defer to v1.1 by default.

## 10.2 Module effort profile

| Module | LOC estimate | Test-case estimate | Phase | Notes |
|---|---|---|---|---|
| Calculator (+flavor) | 9,000 | 210 | G3 | Engine property-tested; UX detail highest |
| Notes | 6,500 | 120 | G4 | FTS + AI actions |
| Scanner | 5,500 | 90 | G4 | Camera + OCR pipeline |
| Calendar | 5,000 | 110 | G4 | Recurrence correctness critical |
| Files | 6,000 | 130 | G4 | SAF edge cases dominate |
| Music | 5,500 | 90 | G4 | Media3 integration |
| Recorder | 4,500 | 80 | G4 | Service lifecycle + packs |
| Hub+Settings | 4,000 | 70 | G4 | Search federation |
| Diagnostics | 3,000 | 50 | G5 | Pack manager |
| Design system | 3,500 | 140 (screenshots) | G2 | Consumed by all |
| Core (engine, data, AI orch.) | 7,000 | 260 | G2–G3 | Highest review intensity |

## 10.3 Cutline rules for v1.0

A feature is cut (deferred, never half-shipped) when: its P0 acceptance cannot be demonstrated on all three API levels; its defect count exceeds 3 open S2/S3s; or it would push the APK past the size budget without a trimming plan. Cut decisions are owner-visible at the G6 review with a dated decision entry.

Every feature below carries: an ID (F-nnn), a statement ("The app SHALL …"), acceptance criteria ("Given/When/Then" compressed), a priority (P0 release blocker / P1 required for G6 / P2 planned fast-follow), a module tag, and links to the detailed specification section. A feature without a test reference cannot leave the catalogue; the traceability script enforces the mapping mechanically.
