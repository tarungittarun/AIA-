@PART: PART VI — FEATURES: STRUCTURE AND OBJECTS
@PARTDESC: Implementation contracts for the features that make OneDoc Docs-class: tables, images, templates, search, reader mode, pagination. Part II said what; this part says how, with the cases that prove it.

# Chapter 17 — Structure and objects: engineering contracts

## 17.1 Tables (F-031, F-032)

Tables are blocks containing one level of cells; each cell holds paragraphs/lists. Rendering uses a measured grid table with per-column max-width; the doc never scrolls horizontally because of a table — narrow columns wrap (UX contract, TC-TBL-002). Editing: tap cell → caret with cell-scoped selection; the table toolbar (row/col add-remove, header toggle) appears anchored to the table. Column presets: equal or content-weighted (recomputed on "re-fit", not live — live reflow during typing causes layout thrash and is banned). Marks inside cells round-trip everywhere (property P6). PDF export renders tables with header repeat across page breaks (F-051).

## 17.2 Images (F-033, F-034)

Insert paths: gallery picker, camera, and from-scan (§19.2). Images are copied into `assets/` (JPEG 85 quality, max edge 2048 px, EXIF rotated and stripped of location data — privacy, §20.4); stored hash-named; referenced by asset id. Resizing is preset-based (S 25% / M 50% / L 75% / full measure) — free-drag resize is explicitly rejected (fiddly on touch, breaks measure). Alt-text (F-034): the insert flow ends with the alt-text field focused (UX-38), deferrable but tracked; an image without alt text shows a dotted outline in the editor and is listed in the asset manager. Full-screen viewer respects theme background and has TalkBack description from alt text.

## 17.3 Table of contents and document map (F-035, F-036)

The TOC block renders from H1–H3 at layout time (never a stored copy — always current); entries scroll to their block with position animation 200 ms. In exports, TOC becomes a static list with page numbers (PDF) or links (HTML/odoc). The map sheet (portrait rails) lists the outline with the live position dot; entries are drag-reorderable via the same moveBlock engine op, giving instant outline-level reorganization.

## 17.4 Pagination (F-037, F-038)

Compose mode shows page-break guides computed by the same metrics engine that drives PDF export (same font metrics, same line-breaking config) — the ±1 line guarantee (TC-STRUCT-004). Paper A4/Letter and margin presets change measure and guides live. Footnotes (F-039) render inline as superscripts with a bottom-of-page sheet on tap in editor; in PDF they are true page footnotes (Print framework region per page). This "one metrics engine, two renderers" rule is what makes WYSIWYG honest without a full pagination layout engine in-loop (which would wreck typing performance).

## 17.5 Templates (F-045 … F-050)

Built-ins are bundled `document.json` assets with placeholders `{name}`, `{date}`, `{your_name}` ( tapped → fill sheet; date auto-fills locale-aware). Templates never execute anything; they are data. "Save as template" copies the current document minus content-ids into the user template store (Room table `templates`, schema v3). Gallery ordering: built-ins in a fixed pedagogical order (blank, letter, meeting notes, …), user templates recency-first. Preview renders the template read-only in reader mode with placeholders visibly marked.

## 17.6 Search (F-067 … F-070)

Indexing: on document save (debounced), `core-search` extracts per-block plain text into the FTS5 external-content shadow table; indexing a 10k-word doc must take < 150 ms background (measured, TC-SRCH-005). Query path: FTS5 `MATCH` with prefix queries, snippet() for the hit context, per-doc hit counts; results ranked by (title match, recency, density). Semantic layer (F-070, pack-gated): per-block MiniLM embeddings computed during idle maintenance windows (JobScheduler-style periodic task, battery-constrained); query embeds once (23 ms on Tier B) and merges cosine hits below FTS hits with a "related" label. Without the pack, semantic search simply doesn't appear (F-082) — no empty section, no error.

## 17.7 Reader mode and read-aloud (F-083, F-080)

Reader mode renders the same `document.json` through the read-only renderer: no chrome beyond font-size stepper, theme follows reader theme; TTS entry starts `TextToSpeech` from the first visible block, highlighting the sentence currently spoken (utterance-range callbacks), pause/resume/stop. Ranges (F-081) start from cursor when present. TTS never reads mark punctuation noise (bullet markers are spoken as list items).

## 17.8 The features that deliberately do not exist in v1.0

Word count goals, distraction-free timers, markdown shortcuts while typing (a v1.1 candidate — D-nnn reserved), collaborative anything, macros, plugins, custom themes beyond the token system. Each exclusion has a reason logged in §1.4 or §30; the agent adds none of them without an owner decision.

## 17.9 Find & replace internals

Find shares the highlight system with search deep-links (F-069): highlights are `BackgroundColorSpan` ranges recomputed on `textChanged` for the visible window only (never the whole doc). Match engine: case-fold via `String.equalsIgnoreCase` semantics (locale-invariant root fold for the default toggle), whole-word via ICU `BreakIterator` word boundaries (never regex `` — that is ASCII-only). Replace-all applies as one grouped composite op and snapshots `pre_edit` first (F-025); replacement text containing block-separator markers is rejected with a hint (use per-match replace). Regex mode is deliberately absent in v1.0 (recorded shelf item §30.2) — the support cost of 100 user regexes was judged worse than the feature's value.

## 17.10 How features join the undo system

| Feature | Undo shape |
|---|---|
| paste (any flavor) | one composite group |
| replace-all | one composite group + pre-edit version |
| AI insert/replace | one composite group + pre-edit version (Law L10) |
| import-merge (scan multi-page into existing doc) | one composite group + pre-edit version |
| checklist toggle | single op, coalesces with adjacent same-block toggles |
| drag-reorder | one moveBlock op; a11y move actions emit the same op |
| table row/col ops | composite of remove/insert ops, atomic undo |
| template instantiate | not an undo — it is a new document |
| version restore | clears redo stack, snapshots current first (F-062) |

Rule: any new feature that mutates content MUST join this table (PR checklist §29.5) — an unundoable mutation is a Law L4 violation by definition.

## 17.11 Reader-mode rendering rules

Reader reuses the same spanner (§14.6) with a chrome-free viewport: no toolbars, no guides; measure widens to screen minus 20 dp; theme = reader theme (sepia default at night by system clock); font-size stepper persists per document. Lists render markers from decoration (same as editor); tables render static with horizontal-in-block scrolling only when exceeding measure (allowed here — no editing in reader); images render at measure width with alt text as caption-on-tap. TTS (§19.7) anchors to the first visible block and follows scroll by pausing on exit (never reading offscreen).

## 17.12 Accessibility of custom views (engineering contract)

Custom views (BlockTextView, table view, toolbar) expose: role (`AccessibilityNodeInfo` class names kept semantic), state (selected/marked), actions (format toggles, move up/down, delete, duplicate — mirroring §17 handle menu), and traversal order matching visual order via `screenReaderFocusOrder`. Table view exposes cell matrix with row/column headers in `collectionInfo`. The toolbar exposes each action with state (bold on/off). The a11y audit (TC-A11Y-001) walks these nodes; any custom view merged without node contract fails review (DQ-6).

## 17.13 Checklists (the quiet feature done right)

Check items are list items of kind `check`; the tap target is the box (48 dp) or the whole row toggle; checked state is a mark on the item (exports per §18.2: md `- [x]`, html `data-check`, docx glyph, pdf drawn box). Progress: a check-list block with ≥ 2 items shows a subtle "2/5" chip in its top-right that fades after first interaction — progress is information, not gamification (no bars, no colors beyond token ramps). Long lists (> 30 items) paginate guides as normal blocks; no virtualized special case (blocks already window, §14.7).

## 17.14 Statistics and the info sheet (counting contracts)

Words = ICU grapheme clusters split on line/space boundaries (same number everywhere: chip, info sheet, exports — UX-49's ±1% is for PDF extraction noise, not definitional drift). Characters = code points (what users think); the info sheet shows both chars and "chars with spaces". Reading time = words ÷ 200 wpm rounded up. Size = document.json.zip + assets on disk. Version count = rows in `versions`. Every number names its definition in the info sheet's fine print — honest counts are part of P5.

## 17.15 Export-presets memory (small kindness, defined precisely)

The export sheet remembers the last used format+paper per user (device-local, one row in `meta`), preselecting it next time — nothing cloud, nothing clever; it just stops asking the same question daily. Reset by long-press on the format list ("Always ask again"). Tested in TC-IO-001-b (preselect honored; long-press resets).
