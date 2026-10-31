@PART: PART II — REQUIREMENTS AND PRODUCT SHAPE
@PARTDESC: The complete feature catalogue F-001…F-090 with priorities and test bindings, the acceptance UX criteria, the navigation graph, and the screen inventory. If a behavior is not listed here or in Part V–VIII, it does not exist in v1.0.

# Chapter 3 — Product map and navigation

## 3.1 The product in one picture

![OneDoc product map: the home library at the center; editor, templates, scan, assistant, files, formats, search and reading around it — one offline process.](figures/fig-product-map.png)

OneDoc has exactly four top-level destinations — **Docs** (home), **Templates**, **Assistant** (pack manager), **Settings** — plus the editor, which opens full-screen over anything. Everything else is a state or a sheet inside those five surfaces. This flatness is deliberate: a writing app must never make the user navigate.

## 3.2 Navigation graph (normative)

![Normative navigation graph. Solid arrows are user taps; dashed arrows are system-driven (deep links from search results into editor selections).](figures/fig-navigation.png)

Navigation rules:

1. **N1.** Back from the editor always lands on the surface that launched it (home, search result, template picker, assistant preview).
2. **N2.** System back inside the editor: first dismiss selection/toolbar, then dismiss keyboard, then confirm-or-autosave exit (Law L7: exit never loses more than 2 s of typing — in practice zero).
3. **N3.** Every screen is reachable in ≤ 2 taps from home; no screen requires scroll-then-tap-then-scroll.
4. **N4.** The editor has no bottom navigation bar; it owns the whole screen except system insets.
5. **N5.** Search results deep-link into the editor with the hit block scrolled into view and the term highlighted.

## 3.3 Home screen (library)

![Documents library (OD-HOME-001): app bar with search, filter chips, document cards with title/meta/star, new-document FAB, bottom navigation.](figures/fig-home-wireframe.png)

The library is a single scrollable list of document cards (title, word count, relative edit time, starred pin, format badge for imported files), with filter chips All / Starred / Recent / Trash, a search entry in the app bar, and a FAB that creates a document **immediately** — no naming dialog first (UX-01). Sorting: recent edit descending; starred documents pin to the top section. Trash holds deletions for 30 days with a restore action and a permanent-delete with confirmation. Long-press enters multi-select with actions: star, rename, duplicate, export, delete.

## 3.4 Screen inventory

The complete normative registry — one row per screen, with Figma frame ids, entry/exit, and states — lives in **`docs/onedoc/blueprint/ui-screens.csv`** (generated with this blueprint; §7.5 explains its contract). Summary:

| Area | Screens | Registry prefix |
|---|---|---|
| Home / library | OD-HOME-001 library, OD-HOME-002 multi-select, OD-HOME-003 trash | OD-HOME |
| Editor | OD-EDIT-001 compose, OD-EDIT-002 selection state, OD-EDIT-003 insert sheet, OD-EDIT-004 find bar | OD-EDIT |
| Templates | OD-TPL-001 gallery, OD-TPL-002 preview | OD-TPL |
| Scan | OD-SCAN-001 camera, OD-SCAN-002 review/crop, OD-SCAN-003 OCR confirm | OD-SCAN |
| Assistant | OD-AI-001 pack manager, OD-AI-002 action sheet, OD-AI-003 generation preview | OD-AI |
| Files/data | OD-FILE-001 versions, OD-FILE-002 import, OD-FILE-003 export sheet | OD-FILE |
| Settings | OD-SET-001 root, OD-SET-002 editor, OD-SET-003 appearance, OD-SET-004 about/diagnostics | OD-SET |

# Chapter 4 — Feature catalogue (F-001 … F-090)

## 4.1 How to read the catalogue

Priority: **P0** = release-blocking (the product is broken without it), **P1** = must ship in v1.0, **P2** = committed stretch, may slip to v1.1 only with a logged decision. Every feature names its binding: the case ids (Chapter 5 and the catalogue in Appendix A) that prove it. The traceability tool (`tools/onedoc/traceability.py`) enforces the invariant **every F has ≥ 1 test binding**; `--check --strict` additionally fails if any P0 lacks a binding.

## 4.2 Documents and the library (F-001 … F-012)

| ID | Feature | Priority | Bound to |
|---|---|---|---|
| F-001 | Create blank document in one tap; opens editor with untitled doc; first character focuses body | P0 | TC-LIB-001 |
| F-002 | Rename inline from card long-press → rename sheet; title mirrors first heading when untitled | P0 | TC-LIB-002 |
| F-003 | Autosave: every edit persisted via journal + debounced model save (Law L3) | P0 | TC-STATE-001 |
| F-004 | Star/unstar; starred section pinned on All chip | P1 | TC-LIB-003 |
| F-005 | Duplicate document (full copy incl. assets, new id) | P1 | TC-LIB-004 |
| F-006 | Move to trash with undo snackbar (7 s window) | P0 | TC-LIB-005 |
| F-007 | Trash retention 30 days with per-item remaining time; restore; permanent delete with confirm | P1 | TC-LIB-006 |
| F-008 | Sort: recent (default), title A–Z, word count; persisted per device | P2 | TC-LIB-007 |
| F-009 | Empty states with one-action CTA (new doc / open templates) | P1 | TC-LIB-008 |
| F-010 | Document info sheet: created/modified, words, chars, reading time, size, version count | P2 | TC-LIB-009 |
| F-011 | Multi-select actions: star, duplicate, export, delete | P1 | TC-LIB-010 |
| F-012 | Cold start to first interaction < 1.2 s on Tier B emulator with 200 docs | P0 | TC-PERF-001 |

## 4.3 Editor core (F-013 … F-030)

| ID | Feature | Priority | Bound to |
|---|---|---|---|
| F-013 | Block text editing with per-block IME composition (no mid-composite breaks); Gboard, Samsung Keyboard, Swiftkey behaviors in scope | P0 | TC-EDIT-001, TC-EDIT-IME-01 |
| F-014 | Enter splits block; Backspace at start merges with previous; both preserve marks sanely | P0 | TC-EDIT-002 |
| F-015 | Undo/redo: single global stack, coalesced typing bursts (600 ms), grouped composite ops (paste, AI insert) | P0 | TC-EDIT-003, TC-PROP-P01 |
| F-016 | Selection: handles, floating toolbar (bold/italic/underline/strike, H1/H2/H3, list, quote, align, link) | P0 | TC-EDIT-004 |
| F-017 | Marks: bold, italic, underline, strike, code, highlight, link — non-overlapping per type (Law L2) | P0 | TC-EDIT-005 |
| F-018 | Heading levels H1–H3 applied per block; outline drives TOC and document map | P0 | TC-EDIT-006 |
| F-019 | Lists: bulleted, numbered (auto-continue, renumber on edit), checklists (tap box to check) | P0 | TC-EDIT-007 |
| F-020 | Blockquote and code block; code block uses monospace, disables inline marks | P1 | TC-EDIT-008 |
| F-021 | Alignment left/center/right/justify per block (non-heading) | P1 | TC-EDIT-009 |
| F-022 | Horizontal divider insert; deleting content around it behaves as one block | P2 | TC-EDIT-010 |
| F-023 | Paste: plain text, HTML subset (marks, lists, simple tables), image; clipboard sanitized | P0 | TC-EDIT-011 |
| F-024 | Cut/copy of selection including multi-block range; paste round-trips exactly | P0 | TC-EDIT-012 |
| F-025 | Find & replace: case toggle, whole-word, regex off by default; replace-all creates a pre-edit version first | P0 | TC-EDIT-013 |
| F-026 | Find bar shows match count and navigates hits; highlight non-destructive | P0 | TC-EDIT-014 |
| F-027 | Word/char count live in editor status chip; tap opens info sheet | P1 | TC-EDIT-015 |
| F-028 | Hardware keyboard: Ctrl+B/I/U, Ctrl+Z/Y, Ctrl+F, arrow-key block traversal, Tab in lists | P1 | TC-EDIT-016 |
| F-029 | Typing latency P95 < 50 ms at 10k words on Tier B emulator; frames never drop > 2 during IME burst | P0 | TC-PERF-002 |
| F-030 | Orientation change and process death restore full cursor, scroll and selection state | P0 | TC-STATE-002 |

## 4.4 Structure and objects (F-031 … F-044)

| ID | Feature | Priority | Bound to |
|---|---|---|---|
| F-031 | Tables: insert N×M, add/remove row/col, header row toggle, marks inside cells, swipe-safe cell editing | P0 | TC-TBL-001 |
| F-032 | Table column width presets (equal / content); long text wraps; no horizontal doc scrolling from tables | P0 | TC-TBL-002 |
| F-033 | Images: insert from gallery/camera; stored as assets; caption block; tap to view full-screen | P0 | TC-IMG-001 |
| F-034 | Image resize presets (S/M/L/full-width) and alt-text editor (a11y, §9) | P1 | TC-IMG-002 |
| F-035 | Table of contents block: generated from H1–H3, tap scrolls to target, refreshes on change | P1 | TC-STRUCT-001 |
| F-036 | Document map sheet: outline list, current position indicator | P2 | TC-STRUCT-002 |
| F-037 | Page setup: paper size (A4/Letter), margins (normal/narrow/wide), affecting PDF/print pagination | P1 | TC-STRUCT-003 |
| F-038 | Page-break guides in compose mode (dashed) matching PDF pagination within ±1 line | P1 | TC-STRUCT-004 |
| F-039 | Footnote blocks rendered at page bottom in PDF, inline sup markers in editor | P2 | TC-STRUCT-005 |
| F-040 | Cover block: title/subtitle/date styling for reports and letters | P2 | TC-STRUCT-006 |
| F-041 | Drag-to-reorder blocks via handle (with a11y equivalent: move up/down actions) | P1 | TC-STRUCT-007 |
| F-042 | Duplicate/delete block from handle menu | P1 | TC-STRUCT-008 |
| F-043 | Code block language label (stored, used for future highlighting; no execution ever) | P2 | TC-STRUCT-009 |
| F-044 | Asset manager: list of images in doc, remove unused (with confirm) | P2 | TC-IMG-003 |

## 4.5 Templates (F-045 … F-050)

| ID | Feature | Priority | Bound to |
|---|---|---|---|
| F-045 | 12 built-in templates: blank, letter, meeting notes, essay/report, invoice, resume, weekly plan, project brief, minutes, recipe, reading list, thesis outline | P0 | TC-TPL-001 |
| F-046 | Template preview (read-only render) before create | P1 | TC-TPL-002 |
| F-047 | Creating from template instantiates a **copy**; template never mutates | P0 | TC-TPL-003 |
| F-048 | Placeholders (Title, Date, [Your name]) tapped to fill; date placeholder auto-fills | P1 | TC-TPL-004 |
| F-049 | User templates: "Save as template" from any document | P1 | TC-TPL-005 |
| F-050 | Template gallery states: empty (never — built-ins), user section with delete | P2 | TC-TPL-006 |

## 4.6 Files, formats, sharing (F-051 … F-060)

| ID | Feature | Priority | Bound to |
|---|---|---|---|
| F-051 | Export PDF via Android Print framework; fonts embedded; selectable text; page setup honored | P0 | TC-IO-001 |
| F-052 | Export .odoc (native zip: document.json + assets + meta) — lossless F3 | P0 | TC-IO-002 |
| F-053 | Export Markdown F2; plain text F1; HTML F2 — per fidelity table §18.2 | P0 | TC-IO-003 |
| F-054 | Export .docx (OOXML subset writer): headings, paragraphs, marks, lists, tables, images | P1 | TC-IO-004 |
| F-055 | Import .odoc F3, .md/.txt F2/F1, .html F2, .docx best-effort F1 with conversion note | P0 | TC-IO-005 |
| F-056 | Import refuses unsupported formats with a specific reason (never a silent empty doc) | P0 | TC-IO-006 |
| F-057 | Share sheet integration: export-then-share; never a raw private-path share | P0 | TC-IO-007 |
| F-058 | Open-in from file managers for .odoc/.md/.txt/.html (intent filters, no internet mime traps) | P1 | TC-IO-008 |
| F-059 | SAF: user-readable locations honored for import; export via create-document dialog | P0 | TC-IO-009 |
| F-060 | Auto-backup: weekly zip of library (excluding trash) to user-chosen SAF folder; off by default | P2 | TC-IO-010 |

## 4.7 Versions and state (F-061 … F-066)

| ID | Feature | Priority | Bound to |
|---|---|---|---|
| F-061 | Versions screen: auto snapshots (every 5 min of activity or 50 ops), manual "Save version", pre-edit snapshots before replace-all / AI insert / import-merge | P0 | TC-STATE-003 |
| F-062 | Version preview read-only; Restore creates a pre-edit snapshot of current, then swaps — history never destroyed | P0 | TC-STATE-004 |
| F-063 | Journal durability: kill -9 within 2 s of last keystroke loses nothing (Law L3) | P0 | TC-STATE-005 |
| F-064 | Storage honest accounting: doc size + assets shown; unused assets cleaned on compaction | P2 | TC-STATE-006 |
| F-065 | Migration: schema version bump path tested v1→vN with synthetic old documents | P0 | TC-STATE-007 |
| F-066 | Multi-window/split-screen: editor remains single-instance, saves on focus loss | P1 | TC-STATE-008 |

## 4.8 Search (F-067 … F-070)

| ID | Feature | Priority | Bound to |
|---|---|---|---|
| F-067 | Library search: title + full text (FTS5), < 300 ms on 200 docs / 1 MB text, results with snippet + hit count | P0 | TC-SRCH-001 |
| F-068 | Result tap opens editor at hit block, term highlighted (N5) | P0 | TC-SRCH-002 |
| F-069 | Search within document via find bar (F-025) shares the same highlight system | P1 | TC-SRCH-003 |
| F-070 | Semantic search (MiniLM embeddings) when pack installed: "meaning" matches merged below FTS hits, labeled | P2 | TC-SRCH-004 |

## 4.9 On-device AI (F-071 … F-082)

| ID | Feature | Priority | Bound to |
|---|---|---|---|
| F-071 | Scan-to-doc: camera capture → perspective crop → OCR (DBNet-lite + CRNN) → editable paragraphs with confidence coloring | P0 | TC-SCAN-001, TC-AI-001 |
| F-072 | Multi-page scan: pages queue into one document, reorderable before insert | P1 | TC-SCAN-002 |
| F-073 | OCR on-device only; pack required (18 MB); without pack the camera flow ends at "save image asset" with reason | P0 | TC-AI-002 |
| F-074 | Dictation: whisper.cpp int8 streaming or system SpeechRecognizer per ladder §19.4; live partial results into a preview strip; Insert on stop | P0 | TC-AI-003 |
| F-075 | Assistant actions on selection or whole doc: Summarize, Rewrite (polish/formal/casual), Continue writing, Fix grammar — each produces a **preview card**, insertion is explicit | P0 | TC-AI-004 |
| F-076 | Assistant runtime: gemma-2B 4-bit, Tier A devices only; Tier B/C get extractive fallbacks per ladder | P0 | TC-AI-005 |
| F-077 | Generation is streamed, cancellable, and never edits the document silently; a pre-edit version is snapshotted before any insert | P0 | TC-AI-006 |
| F-078 | Pack manager: list packs (OCR/ASR/LLM/embeddings), size, license, install via SAF from side-loaded .odpack, SHA-256 verify at import and load; delete frees space | P0 | TC-AI-PACK-01 |
| F-079 | Corrupt/wrong-SHA pack: refused with reason; capability degrades per ladder; no crash, no retry loop | P0 | TC-AI-PACK-02 |
| F-080 | Read aloud: system TTS play/pause/stop from reader mode; sentence highlight follows speech | P1 | TC-AI-007 |
| F-081 | Read aloud honors document range (from cursor); voice/rate from system settings only | P2 | TC-AI-008 |
| F-082 | Every assistant control hides (not grays) when unavailable, with a one-line reason on long-press (tier/pack/ram) | P0 | TC-AI-009 |

## 4.10 Reading, a11y, settings, platform (F-083 … F-090)

| ID | Feature | Priority | Bound to |
|---|---|---|---|
| F-083 | Reader mode: distraction-free render (no toolbars), font size control, TTS entry | P1 | TC-READ-001 |
| F-084 | TalkBack: full traversal of editor by block; marks announced; actions (move block, format) via local context menu | P0 | TC-A11Y-001 |
| F-085 | Contrast ≥ 4.5:1 body text in all 8 themes incl. high-contrast black/white | P0 | TC-A11Y-002, DQ-4 |
| F-086 | Dynamic type: editor text scales to 200% system setting without clipping or truncation | P0 | TC-A11Y-003 |
| F-087 | Themes: light, dark, sepia, paper, high-contrast ×2, plus accent choices; "match system" default | P1 | TC-SET-001 |
| F-088 | Editor settings: default font (Inter/system/serif/mono), size 12–24 sp, autosave interval display, spell-check toggle (system service) | P1 | TC-SET-002 |
| F-089 | About + diagnostics screen: version, commit, storage usage, pack states, self-test button (runs integrity suite locally) | P1 | TC-SET-003 |
| F-090 | Locales: en (default), hi, mr string coverage; RTL layout mirroring correct | P2 | TC-SET-004 |

**Count check:** 90 features — P0 = 48, P1 = 28, P2 = 14 (machine-verified by `traceability.py --check --strict`, which additionally enforces a binding on every P0). The machine-readable list with bindings lives in Appendix A and is parsed by `tools/onedoc/traceability.py`.

## 4.11 Design notes behind the catalogue (library and editor)

**Library (F-001…012).** The library's only job is to get out of the way. Cards show title, meta, star — never previews: preview tiles cost scroll speed and leak content in public places (a deliberate privacy choice, consistent with §20). Rename is a sheet, not an inline text war with card layout. Trash uses a retention period rather than "are you sure" chains: recovery exists, so deletion can stay one tap. Sorting is persisted per device and never asked about — default recency matches how returning users actually work. Cold start (F-012) is a feature, not an implementation detail: the library renders from the Room index in the first frame, which is why documents store their index fields (title, wordCount, updatedAt) denormalized in Room despite document.json being authoritative (§11.2).

**Editor core (F-013…030).** The editor's design center is the **single op stream**: everything a user does becomes ops in one log, and every surface (undo, versions, search-highlight, autosave) is a consumer of that log. This is why undo covers AI inserts and replace-all with zero special cases (they are composite op groups, §17.10). Selection is a first-class state machine (§15.7) because selection bugs are the most user-visible editor bugs. Marks get one chapter-level rule set (§14.5) instead of per-feature ad hoc behavior — the "why does bold disappear here" bug class is engineered out, not patched. The typing budget (F-029) is stated in the catalogue rather than a perf chapter because it is a *requirement*: if a feature breaks it, the feature waits.

**Paste (F-023).** Paste is the highest-risk input path (untrusted content, arbitrary structure). Design: sanitize-to-model in one step (no intermediate HTML DOM retained), image sizes capped, HTML subset per §18.2 with everything else dropped *and counted* (the conversion note can say "paste dropped 3 unsupported constructs").

## 4.12 Design notes: structure, templates, files

**Tables (F-031/032).** Tables on touch fail when they try to be spreadsheet grids: free column drag, per-cell borders, horizontal scroll. OneDoc's preset-width, wrap-always, popup-cell-editor design trades spreadsheet feel for calm document behavior — and that trade is a feature, stated here so it survives implementation pressure.

**Images (F-033/034).** Presets beat free-resize on touch (fat-finger precision); captions are blocks (they export everywhere); alt text is prompted at insert because retrofitting alt text never happens. EXIF stripping is privacy, not housekeeping (§20.4).

**Templates (F-045…050).** Templates are data, deliberately dumb: no logic, no computed fields beyond date fill, no code execution (§1.4). Twelve built-ins cover the correspondent and compiler personas (§2.4); "save as template" is how the capturer persona freezes recurring structures (meeting notes with fixed headings).

**Files (F-051…060).** The fidelity ladder (§18.2) is the honesty contract: refuse > guess. PDF via the platform Print framework is a dependency decision: it guarantees printer-parity pagination and selectable text for free, at the cost of style control — acceptable for v1.0, revisit only if a golden diff demands it.

**Versions (F-061…066).** Version kinds are semantic (auto/manual/pre_edit) because restore UX depends on knowing *why* a snapshot exists ("Before change" reads as safety; "Auto" reads as background). Restore never destroys (F-062) — the version graph is append-only, which also makes the restore implementation trivially crash-safe (§12.3 rules apply to versions as to everything).

## 4.13 Design notes: search, AI, settings

**Search (F-067…070).** Search is split by job: "find the doc" (library FTS, title-weighted) vs "find the place" (in-doc find bar) vs "find the meaning" (semantic, pack-gated, labeled "related" and ranked *below* lexical hits — meaning never overrides exact words). Deep-linking with highlight (N5) closes the loop that search opens; the shared highlight system (F-069) exists so the two surfaces cannot drift.

**AI (F-071…082).** Three principles produce every AI requirement: (1) *explicit over ambient* — preview cards, no ghost text (Law L10); (2) *ladder over error* — every unavailability is a graceful descent with a reason (§19.4), never a dead button; (3) *packs over bundling* — the APK stays small and the owner chooses what fits the device (C5). The LLM is Tier A-only in v1.0 because extractive fallbacks cover 80% of summarize/rewrite value at 0% of the RAM cost; the ladder makes that trade invisible except in the method label (UX-47), which is exactly as honest as P5 demands.

**A11y & settings (F-083…090).** TalkBack-complete is scoped to the letter flow (UX-37) because "accessibility everywhere" without a verified flow produces checkbox compliance; the letter flow exercises every mechanism (creation, selection, marks, export). Settings are few and instant-apply; themes are token-remaps (§6.3) not skins; diagnostics is a power tool with an off switch (it shows nothing unless opened).

## 3.5 Feature coverage sanity (by the numbers)

90 features over 10 areas — library 12, editor core 18, structure 14, templates 6, files 10, state 6, search 4, AI 12, read/a11y 4, settings/platform 4. P0 mass: editor core (13) + AI (9) + files (7) + state (4) = 33 of 48 P0s — the product *is* the editor and its durability; everything else earns its P1/P2 by the same testability bar. The count table regenerates with the catalogue (`traceability.py --stats`) so drift shows in CI, not at review.

## 2.8 What OneDoc tells users it is NOT (positioning honesty)

The welcome card and About say it plainly: OneDoc is not a cloud suite (nothing syncs, nothing signs in); not a PDF editor (PDFs export, they don't import — Scan is the path for paper); not a spreadsheet (tables are document furniture, not cells-with-formulas); not an AI assistant with a personality (the assistant edits text, it doesn't chat). Saying what a tool is not, in the product, prevents the one-star reviews that come from mismatched expectations — and keeps every promise in this document falsifiable.
