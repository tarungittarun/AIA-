# Appendix I — Case procedures (executor-ready one-liners)

Format per case: **Case** — *Given* state → *When* action(s) → *Then* assertion(s). The QA harness expands these into `qa/onedoc/procedures/<case>.json` (§24.5). One line each; the catalogue (Appendix C) remains the binding index.

## I.1 Laws

- **TC-LAW-001** — Given a doc with mixed marks typed 2 s ago → When autosave completes → Then `document.json` on disk parses to text+marks identical to on-screen.
- **TC-LAW-002** — Given any reachable model state → When `normalize()` runs twice → Then second run is a no-op and same-type marks never improperly overlap.
- **TC-LAW-003** — Given a fixed op list and seed → When applied on two clean instances → Then resulting documents and export bytes (minus timestamps) are identical.
- **TC-LAW-004** — Given an odoc containing a future-kind block → When opened → Then block preserved verbatim; conversion note lists it; saving keeps bytes.

## I.2 Library

- **TC-LIB-001** — Given home → When FAB tapped then a key typed → Then editor visible ≤ 2 s, doc exists with that char, no dialogs seen.
- **TC-LIB-002** — Given a doc titled only by first H1 → When renamed via long-press sheet → Then card title updates; untitled docs mirror first heading on edit.
- **TC-LIB-003** — Given 3 docs → When one starred → Then it pins to top of All; state survives relaunch.
- **TC-LIB-004** — Given a doc with an image asset → When duplicated → Then copy has new id, same content, independent asset refs.
- **TC-LIB-005** — Given a doc → When deleted → Then snackbar with undo 7 s; undo restores at same position in list.
- **TC-LIB-006** — Given a trashed doc aged 29 days → When library opened → Then remaining time shown; restore works; permanent delete asks confirm twice.
- **TC-LIB-007** — Given sort switched to title → When app relaunched → Then ordering persists.
- **TC-LIB-008** — Given empty library / empty trash / empty template-user-section → When each opened → Then single-line empty state with one CTA renders (no blank screens).
- **TC-LIB-009** — Given a 1,234-word doc with 2 images → When info sheet opened → Then words/chars/reading time/size/version count match computed truth.
- **TC-LIB-010** — Given 3 docs multi-selected → When export+delete applied → Then zip contains 3 exports; 3 cards vanish; undo restores them.

## I.3 Editor core

- **TC-EDIT-001** — Given cursor mid-paragraph → When typing fast (scripted 300 cps) → Then text lands at caret; neighbors unaffected; caret stays visual position.
- **TC-EDIT-002** — Given "aaa|bbb" in one block and marks spanning the middle → When Enter → Then two blocks with marks redistributed; Backspace merges back to the original spanned marks.
- **TC-EDIT-003** — Given type(10 chars)+paste+bold+type(5) → When undo×4/redo×4 → Then each step matches a previously rendered state; final = original start.
- **TC-EDIT-004** — Given a selection → When handles dragged, toolbar tapped, stylus/mouse used → Then actions apply to selection; toolbar never covers it; active states correct.
- **TC-EDIT-005** — Given text with nested same-type marks → When toggle bold on overlapping range → Then normalize yields single merged range; rendering matches.
- **TC-EDIT-006** — Given paragraph with bold middle → When switched H1→H2→para→list→para → Then bold survives every transition; outline updates.
- **TC-EDIT-007** — Given list item 3 of 5 → When Enter at end / at empty item / Tab / Shift+Tab → Then continue+renumber / exit-list / indent / outdent exactly as Docs.
- **TC-EDIT-008** — Given code block → When typing and toggling marks → Then code text takes no marks; quote allows them.
- **TC-EDIT-009** — Given paragraph → When each alignment set → Then rendering + persistence + export carry align.
- **TC-EDIT-010** — Given divider between paragraphs → When deleting adjacent empty para → Then divider remains single removable block.
- **TC-EDIT-011** — Given clipboard from Docs HTML (marks+list+table) → When pasted → Then subset converts per F2; scripts/styles dropped; clipboard unchanged on failure.
- **TC-EDIT-012** — Given 3-block selection → When cut then pasted elsewhere → Then target content byte-equal; source collapsed correctly; one undo reverts both.
- **TC-EDIT-013** — Given 7 matches of "q3" → When replace-all with "Q3" (case on) → Then confirm + pre-edit version created; one undo restores all 7.
- **TC-EDIT-014** — Given matches across pages → When next/prev in find bar → Then count updates, view scrolls, highlights non-destructive after close.
- **TC-EDIT-015** — Given live typing incl. emoji → When count chip read → Then words/chars match ICU grapheme truth.
- **TC-EDIT-016** — Given hardware keyboard → When Ctrl+B/Z/Y/F, arrows, Tab in list/table → Then behaviors per §15.4; undo parity with soft path.
- **TC-EDIT-017** — Given "a👨b" → When deleting between glyphs / splitting → Then surrogate pair moves/deletes atomically; offsets stay valid.

## I.4 IME

- **TC-EDIT-IME-01** — Given glide-typed word with autocorrect full-replace → When composition finishes → Then single op; prior marks intact; no ghost text.
- **TC-EDIT-IME-02** — Given active composition → When two-finger scroll → Then composition cancels cleanly, text = last committed, no corruption.
- **TC-EDIT-IME-03** — Given Hindi transliteration of "namaste" → When composed → Then combining clusters never split across ops; rendering stable.
- **TC-EDIT-IME-04** — Given IME fuzzer with random valid sequences + ops → When run 10k steps → Then L2/L4/L5 hold after every step (seeds on failure).

## I.5 Properties, State, Tables/Images/Structure

- **TC-PROP-P01…P10** — Given generators per §16.3 → When 5k cases per property (PR) → Then all hold; failures shrink to minimal counterexamples with seeds.
- **TC-STATE-001** — Given edits 0.8 s old → When back/home → Then no dialog, state present on reopen (silent autosave).
- **TC-STATE-002** — Given mid-sentence caret + selection + IME composing → When rotate/split resize → Then caret, selection, composition state survive; scroll anchored.
- **TC-STATE-003** — Given 50 op batches in 2 min → When thresholds cross → Then auto snapshot lands exactly per policy table.
- **TC-STATE-004** — Given 5 versions on 50-page doc → When preview then restore → Then ≤ 30 s, pre_edit snapshot of current first, redo cleared, content equals chosen version.
- **TC-STATE-005** — Given typing loop → When `am kill` at 100 randomized instants → Then relaunch content always within 2 s of typing (observed: 0 loss).
- **TC-STATE-006** — Given doc with unused assets → When info/asset manager opened → Then accounting matches `du` truth; cleanup requires confirm and re-checks refs.
- **TC-STATE-007** — Given synthetic v1…vN-1 databases → When sequential migrations run → Then each up-test passes; chain lands on vN; dry-run corpus valid.
- **TC-STATE-008** — Given editor in split-screen → When focus lost to companion app → Then autosave fires; nothing lost on kill right after.
- **TC-STATE-009** — Given storage 99% full → When typing continues → Then editor keeps working in memory; warning chip; autosaves succeed after space freed (auto retry).
- **TC-TBL-001** — Given 3×3 table → When add/remove row/col, header toggle, bold inside cell → Then ops atomic in undo; marks render in cells; export keeps them.
- **TC-TBL-002** — Given table with long cell text → When rendered → Then columns wrap to presets; document never scrolls horizontally.
- **TC-IMG-001** — Given gallery/camera/scan inserts → When image added → Then EXIF GPS stripped, alt-text prompt focused, caption editable, viewer shows alt for TalkBack.
- **TC-IMG-002** — Given image → When S/M/L/full applied → Then measure-relative size persists; alt editor edits text read by reader.
- **TC-IMG-003** — Given doc with orphan asset after image delete → When asset manager opened → Then orphan listed; remove requires confirm; references double-checked.
- **TC-STRUCT-001** — Given doc with H1–H3 → When TOC block present and headings edited → Then entries update; tap scrolls to target with animation.
- **TC-STRUCT-002** — Given long doc scrolled → When map sheet opened → Then live position dot matches; tap navigates.
- **TC-STRUCT-003** — Given A4 normal vs Letter narrow → When switched → Then measure, guides, PDF pagination all change consistently.
- **TC-STRUCT-004** — Given 40-page doc → When guides compared to exported PDF breaks → Then within ±1 line on every page.
- **TC-STRUCT-005** — Given footnote → When exported → Then sup in body, note at page bottom in PDF; editor tap opens bottom sheet.
- **TC-STRUCT-006** — Given cover block filled → When exported md/html/pdf → Then styled per format capabilities; nothing lost silently.
- **TC-STRUCT-007** — Given 12 blocks → When drag-reordered (and via TalkBack actions) → Then order changes as one moveBlock op each; ids stable.
- **TC-STRUCT-008** — Given block menu → When duplicate/delete → Then new block copy with fresh ids / removal with single undo.
- **TC-STRUCT-009** — Given code block → When language label set to "kotlin" → Then label persists through all exports that support it, noted otherwise.

## I.6 Templates, IO, Search

- **TC-TPL-001…006** — Given gallery → When each of 12 templates instantiated, previewed, placeholder-filled, saved-as, deleted (user section) → Then behaviors per §17.5 with template files never mutating.
- **TC-IO-001** — Given 50-page doc → When PDF exported → Then fonts embedded (no fallback boxes), text selectable, breaks match §17.4, word count ±1%, < 10 s.
- **TC-IO-002** — Given doc with all 13 block kinds + image → When odoc export→import → Then F3-identical (bytes of document.json; asset SHAs equal).
- **TC-IO-003** — Given marks/tables/code docs → When md/txt/html exported → Then per §18.2 fidelity; unsupported constructs degrade with notes (never silent).
- **TC-IO-004** — Given styled doc → When docx exported then re-imported → Then headings/marks/lists/tables/images parity within F2; OOXML valid.
- **TC-IO-005** — Given md/html/docx/odoc fixtures → When imported → Then conversion notes state kept/dropped counts truthfully (UX-45).
- **TC-IO-006** — Given .exe/.pdf/random binary named .odoc → When import attempted → Then refusal with specific reason; no empty doc; clipboard intact.
- **TC-IO-007** — Given export → When share sheet invoked then cancelled → Then FileProvider URI grants scoped; temp cleaned in both paths.
- **TC-IO-008** — Given file-manager "open with" for each supported type → When tapped → Then import preview opens with correct sniffing.
- **TC-IO-009** — Given SAF locations (Downloads, custom folder) → When create/open through SAF → Then streams complete; sizes honored; caps warn at 50 MB.
- **TC-IO-010** — Given backup enabled + folder picked → When weekly trigger fires → Then encrypted zip lands with manifest SHAs; passphrase prompt is the only security dialog.
- **TC-IO-011** — Given export to SAF → When provider revoked mid-write → Then no partial file remains; reason shown; retry clean.
- **TC-IO-012** — Given share→receive→import→export loop per format → When completed → Then parity within declared fidelity each hop.
- **TC-IO-013** — Given backup → wipe app data → restore → Then library byte-identical at F3; report lists counts; conflicts import as versions.
- **TC-SRCH-001** — Given 200-doc corpus → When "warranty" typed (2 chars on) → Then results stream; snippet+count correct; < 300 ms end-to-end on API 33.
- **TC-SRCH-002** — Given a result → When tapped → Then editor opens at hit block, term highlighted, back returns to results.
- **TC-SRCH-003** — Given highlight in find bar → When search deep-link arrives → Then same highlight system serves both (no double-style).
- **TC-SRCH-004** — Given embed pack + query "what covers repairs" → When results merged → Then "related" section labeled; absent pack → section absent, no error.
- **TC-SRCH-005** — Given 10k-word doc saved → When index updated → Then < 150 ms on background executor; main thread untouched.

## I.7 Scan, AI, Packs, Read/A11y

- **TC-SCAN-001** — Given fixture page → When capture→crop→OCR→review→fix→insert → Then ≤ 60 s/page on API 33; confidence marks on < 0.82 words; fixed word lands.
- **TC-SCAN-002** — Given 3 pages queued → When reordered then OCR batch → Then paragraphs in chosen order; page separators correct.
- **TC-AI-001** — Given 10-page OCR fixture set → When processed → Then accuracy ≥ 95%; marks use color+underline; export of scan-sourced doc flags unreviewed low-confidence words (UX-46).
- **TC-AI-002** — Given no OCR pack → When scan flow run → Then ends at save-image with one-line reason; no crash; retry offers pack manager.
- **TC-AI-003** — Given fixture audio injected → When dictation runs → Then first partial ≤ 1.5 s; stop → editable preview; insert = one grouped op.
- **TC-AI-004** — Given selections of varied size → When each verb run → Then labeled preview cards; Insert/Replace/Discard behave; nothing auto-applies.
- **TC-AI-005** — Given API 36 (Tier A) and API 33 (Tier B) → When Summarize → Then gemma rung on A; extractive rung on B; card labels match (UX-47).
- **TC-AI-006** — Given generation streaming → When cancel mid-stream / insert after completion → Then no residue on cancel; pre_edit snapshot before insert; single undo reverts.
- **TC-AI-007** — Given reader mode → When TTS play/pause/stop → Then sentence highlight follows; controls respond < 200 ms.
- **TC-AI-008** — Given cursor mid-doc → When read-from-cursor → Then range honored; system rate changes apply next utterance.
- **TC-AI-009** — Given tiers C/B/A and pack combos → When surfaces render → Then unavailable verbs hidden with long-press reason naming tier/pack/ram (never disabled buttons).
- **TC-AI-010** — Given prompt fixtures → When assistant runs twice per fixture → Then identical outputs (pinned seed); faithfulness rubric passes (no invented facts in 20 fixtures).
- **TC-AI-PACK-01** — Given valid .odpack via SAF → When install confirmed → Then SHA shown pre-confirm; verify passes; capability appears; delete frees space and capability disappears.
- **TC-AI-PACK-02** — Given pack with flipped byte in model file → When installed/loaded → Then refused with both SHAs; capability descends ladder; no crash/loop.
- **TC-READ-001** — Given reader mode with TTS → When font size changed and play pressed → Then render + speech continue from visible block.
- **TC-A11Y-001** — Given TalkBack on → When full letter flow (create→format→export) → Then completable sightless; traversal matches visual order; actions present in menu.
- **TC-A11Y-002** — Given all 8 themes → When contrast audited → Then body ≥ 4.5:1, large ≥ 3:1, HC themes ≥ 7:1 (snapshot gate fails otherwise).
- **TC-A11Y-003** — Given font scale 2.0 → When all screens walked → Then no clipped/truncated text; containers grow or scroll.

## I.8 Settings, Security, UX-platform, Perf/Env, Journeys

- **TC-SET-001…004, TC-DIAG-001** — Given settings surfaces → When themes/editor/files/about exercised per §8.6 → Then instant persistence; self-test ≤ 20 s offline; locales+RTL correct; diagnostics never leaves device.
- **TC-SEC-P-01** — Given release APK → When `apkanalyzer manifest` → Then permission set equals §20.5 exactly (CI gate fails on any delta).
- **TC-SEC-P-02** — Given full journey run → When notification shade inspected → Then only user-created/export-progress notifications ever appeared.
- **TC-SEC-P-03** — Given airplane-mode emulator + strace/logcat probes → When ALL flows incl. AI run on release APK → Then zero socket syscalls; zero resolver attempts; app fully functional.
- **TC-SEC-P-04** — Given clipboard seeded → When app foregrounded/idled 5 min → Then no clipboard reads outside explicit paste (Android 13 toast never appears).
- **TC-SEC-IO-01/02, TC-SEC-ST-01/02, TC-SEC-PK-01/02** — Given hostile fixtures (scripted HTML, zip-bomb, traversal pack, oversize DOCX) and storage probes → When processed → Then refusals with reasons; grants scoped; cache cleaned; encryption smoke passes; no path escapes.
- **TC-UX-001…011** — Given each criterion context (§5) → When measured on API 33 → Then all pass with numbers (taps, seconds, dp, %).
- **TC-PERF-001/002** — Given cold start / typing burst harness on API 33 → When run → Then < 1.2 s / P95 < 50 ms with frame stats attached.
- **TC-ENV-001…004** — Given each AVD and airplane mode → When P0 subset / Tier A / tablet-landscape / offline journeys run → Then green with evidence per environment.
- **TC-J1…TC-J5 (+variants)** — Given journey scripts §27.1–27.5 → When executed on release APK per matrix → Then all steps assert; screenshots + artifacts attached; variants (degraded/llm/semantic) follow their ladder rungs.
