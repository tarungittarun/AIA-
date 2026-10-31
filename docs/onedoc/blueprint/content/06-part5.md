@PART: PART V — THE DOCUMENT MODEL AND EDITOR ENGINE
@PARTDESC: The ten editor laws that are release blockers, the block-and-mark data model, the operation/undo engine, IME coexistence, and the property-based test system that makes correctness provable rather than hoped for.

# Chapter 13 — The ten editor laws (release blockers)

## 13.1 Why laws

The predecessor program proved that a small set of absolute, test-bound behaviors — treated as laws — is what makes an autonomous build shippable: laws are few, precise, and each has a case id. OneDoc's editor has ten. A release candidate that fails any law does not ship, no matter what else is green.

| Law | Statement | Proven by |
|---|---|---|
| **L1 — What you see is the file** | After autosave (≤ 800 ms after last edit), the persisted document equals the on-screen content byte-for-byte in text and marks | TC-LAW-001 |
| **L2 — Marks are sane** | At any state, marks of the same type never improperly overlap; `normalize()` restores that invariant after every op, idempotently | TC-LAW-002, property P2 |
| **L3 — Zero-loss durability** | A process kill at any instant loses at most 2 s of typing; after relaunch the document is valid and cursor-consistent | TC-STATE-005 (100 kill trials) |
| **L4 — Undo is honest** | Undo after any op sequence returns a state previously on screen (not merely "shorter text"); redo mirrors it; no user-visible op escapes the stack | TC-EDIT-003, property P1 |
| **L5 — IME composition is sacred** | No op (autosave, snapshot, AI, find-highlight) ever mutates text inside an active composition; composition text is inviolable until committed | TC-EDIT-IME-01/02 |
| **L6 — Determinism** | The same op list applied to the same document yields the identical result, always — including snapshot ids and export bytes (excluding timestamps) | TC-LAW-003 (golden files) |
| **L7 — Exit never asks, never loses** | Leaving the editor (back, home, app-switch kill) silently persists everything committed; no save dialogs exist | TC-STATE-001/002 |
| **L8 — Structure is closed** | Only block kinds in the §14.3 set exist; unknown kinds from imports/opening new files are preserved verbatim (round-trip) with a conversion note, never dropped | TC-IO-002/005, TC-LAW-004 |
| **L9 — Selection survives** | Cursor/selection survive: mark toggles, style changes, snapshot/restore of *other* docs, sheet open/close, split-screen resize | TC-EDIT-004, TC-STATE-002 |
| **L10 — No silent mutations** | No code path (AI, importer, backup restore, migration) may modify document content without a visible, undoable, versioned operation | TC-AI-006, TC-STATE-004 |

## 13.2 Law provenance and precedence

Laws derive from the owner's acceptance criteria for the predecessor program (calculator laws L1–L10, CAT parity): a small surface must be *perfectly* right before breadth matters. When a feature task and a law conflict, the law wins and the feature is redesigned. Law violations are S1 defects by definition (§25.3).

# Chapter 14 — Document model

## 14.1 Model choice, argued

Rich-text on mobile is dominated by two architectures: span-over-TextView (native, fast, but undo/structure logic becomes spaghetti) and block-based CRDT-style models (web heritage, robust, heavier). OneDoc uses a **block-and-mark model with an operation log** — the Docs/Notion shape — because: (a) laws L2/L4/L6 need an explicit op log and normalizer; (b) tables/images/TOC are blocks, which spans cannot express; (c) versioning is trivially "this op prefix"; (d) it is implementable and testable in pure Kotlin (`core-model` has zero Android imports), so the JVM property tests run in seconds, not on emulators.

## 14.2 The document

![document.json: schema-versioned blocks with ids, inline marks, and a closed kind set.](figures/fig-docmodel.png)

```json
{
  "schema": 3,
  "docId": "d_9f2c1a7b",
  "meta": { "title": "Project Phoenix proposal",
            "created": 1761900000000, "wordCount": 1842,
            "pageSetup": { "paper": "A4", "margin": "normal" } },
  "blocks": [
    { "id": "b01", "type": "h1", "text": "Quarterly Business Review" },
    { "id": "b02", "type": "para", "text": "Revenue grew 14% quarter over quarter…",
      "align": "left",
      "marks": [ { "type": "strong", "start": 0, "end": 7 },
                 { "type": "link", "start": 22, "end": 34, "href": "…" } ] },
    { "id": "b03", "type": "list", "listType": "bullet",
      "items": [ { "id": "i1", "text": "Enterprise renewals +22%", "checked": null } ] },
    { "id": "b04", "type": "table", "header": true,
      "cols": [ { "width": "equal" } ],
      "rows": [ { "id": "r1", "cells": [ { "id": "c1", "blocks": [] } ] } ] }
  ]
}
```

Invariants (checked by `core-model` validators after every op; violation = engine bug, fail-fast in debug):

- **I1** every block/item/cell has a stable id unique in the document; ids are never reused.
- **I2** blocks are ordered, no holes; text offsets are UTF-16 code-unit indices (matching Java/Kotlin strings exactly — no emoji off-by-one class of bugs).
- **I3** marks within one type are non-overlapping and half-open `[start, end)`; after `normalize()` the invariant holds and a second `normalize()` is a no-op.
- **I4** a list item's `checked` is non-null only for `check` lists; a table cell contains blocks (recursion depth 1 — no tables in tables in v1.0, refused at insert with a reason).

## 14.3 The closed block-kind set (Law L8)

`para, h1, h2, h3, list(bullet|number|check), quote, code, table, image, divider, toc, footnote, cover`. Thirteen kinds, schema-versioned. Adding a kind is a schema migration (§11.4) with round-trip golden files; no other extension point exists — custom plugins and embedded HTML are out of scope (§1.4).

## 14.4 Operations and undo

The engine's op set is minimal and sufficient: `insertText(block, pos, text)`, `deleteText(range)`, `setMarks(range, mark, on)`, `setBlockType(block, kind, params)`, `splitBlock(block, pos)`, `mergeBlocks(a, b)`, `moveBlock(from, to)`, `insertBlock(at, block)`, `removeBlock(block)`, `tableOp(kind, params)`. Composite ops (paste, AI insert, replace-all) are groups that undo atomically (UX-06).

Undo correctness is by **inverse application, not state snapshots**: each op knows its inverse; the stack stores committed batches with inverses and (for redo) reapplications. Coalescing: consecutive `insertText`/`deleteText` on the same block with no intervening op merge into one batch after a 600 ms idle boundary; cursor movements never enter the stack. Property P1 (§16.2) proves `apply(ops) then undo-all == original` over randomized op lists.

# Chapter 15 — Text input and the IME contract

## 15.1 The bridge

Android IMEs type through `InputConnection`; the editor implements it over the block model with three absolute rules (Law L5):

1. **Composition isolation:** an active composition (`composingText` region) pins its block; the engine queues all non-IME ops (autosave snapshot, find re-highlight, AI cancellation cleanup) until `finishComposing`. The queue is drained in order after commit.
2. **Batched commits:** `commitText` applies as one `insertText` op (undoable as one step); `deleteSurroundingText` maps to `deleteText` with the same batching as key events.
3. **No silent re-layout of composed text:** the block being composed re-renders only its own text region; neighbors do not reflow (UX-26).

## 15.2 The known hard cases (each has a test)

| Case | Behavior | Test |
|---|---|---|
| Emoji / surrogate pairs at selection | offsets in code units; deletion removes the pair atomically | TC-EDIT-017 |
| Gboard glide typing with autocorrect | full composition replace lands as one op; marks outside composition untouched | TC-EDIT-IME-01 |
| Hindi/Devanagari transliteration (owner locale) | combining-mark clusters never split; cluster-aware boundary helpers used everywhere | TC-EDIT-IME-03 |
| Two-finger scroll mid-composition | composition cancelled cleanly via `finishComposing` before scroll op | TC-EDIT-IME-02 |
| Physical keyboard + IME simultaneously | same op stream; no double-commit | TC-EDIT-016 |
| Samsung keyboard "rewrite" suggestions | treated as commit/replace stream; covered by IME fuzzer (§15.3) | TC-EDIT-IME-04 |

## 15.3 The IME fuzzer

A Robolectric+instrumentation harness replays recorded `InputConnection` call sequences from the API 26/33/35/36 emulators' default IMEs plus scripted Gboard patterns (recorded once, stored as JSON scripts). The fuzzer interleaves random valid call sequences with engine ops and asserts laws L2/L4/L5 hold after every step. It runs on every PR touching `core-editor` and nightly on emulators; a red fuzzer blocks release regardless of other greens.

# Chapter 16 — Property-based testing of the engine

## 16.1 Why properties, not examples

Example tests encode the bugs you imagined; property tests encode the laws you promised. The engine's core properties run in JVM seconds on thousands of random documents and op lists — this is what lets an autonomous agent refactor the editor without fear.

## 16.2 The property suite (P1 … P10)

| P | Property | Source law |
|---|---|---|
| P1 | For any valid doc D and op list O: `undoAll(apply(D, O)) == D` (text + marks + ids) | L4 |
| P2 | `normalize` is idempotent and restores I3 for any doc reachable by ops | L2 |
| P3 | For any doc, `plainText()` contains no zero-width engine internals; length equals sum of block lengths + separators | L1 |
| P4 | Split/merge are exact inverses for any split point (marks redistributed, never dropped) | L1 |
| P5 | Move/remove preserve ids and the no-holes invariant | I1, I2 |
| P6 | Table ops never orphan cells; depth-1 invariant holds under any op sequence | I4 |
| P7 | Export→import round-trip (odoc, md subset, html subset) yields `same(normalize, markSet)` equality per fidelity level | L6, L8 |
| P8 | Journal replay of any op-batch sequence yields the same state as in-memory application | L3 |
| P9 | Snapshot restore then redo-stack clear leaves a valid cursor ≤ doc length | L9 |
| P10 | Generators: `insertText` with random Unicode planes (emoji, Devanagari, CJK) never throws and keeps offsets valid | L5 |

Generators live in `core-model/src/test/gen/`; seeds are logged on failure so any red property reproduces exactly (Law L6 for the tests themselves). Coverage gates: engine line coverage ≥ 90%, property suite green = G3 exit criterion (§21.5).

## 14.5 Mark semantics per type (the edge rules)

Marks look symmetric in the schema and asymmetric in behavior. The table is normative; property P2 tests the invariants, these tests pin the semantics.

| Mark | Typed at boundary | Overlap rule | Copy/paste | Export note |
|---|---|---|---|---|
| strong | extends (new char inherits bold) | merges with adjacent same-type | keeps | md `**` / html `<strong>` |
| em | extends | merges | keeps | md `*` / `<em>` |
| u | extends | merges | keeps | html `<u>` only (md has none — note) |
| strike | extends | merges | keeps | md `~~` / html `<s>` |
| code | does NOT extend (typed char is plain) | never merges; normalized to abut, not overlap | keeps | backticks / `<code>` |
| highlight | extends | same-type overlap forbidden (I3) | keeps | html `<mark>` (md: `==` extension, noted) |
| link | typed text inside link range extends href | one href per range; adjacent different-href links abut | keeps href; empty selection + paste-with-link = plain text (link not applied) | md `[t](href)` / `<a>` |

Boundary rule common to all: a mark is "at" a caret when `caret ∈ [start, end)` after normalization; toolbar buttons show active state from the single block containing the caret (multi-block selection shows active only if all non-empty ranges carry the mark — Docs behavior, TC-EDIT-004).

## 14.6 The rendering stack (model → pixels)

`core-editor` binds blocks to Android text infrastructure with a strict pipeline:

1. **Model → span state:** each block owns one `BlockTextView` (custom `AppCompatTextView` subclass with caret/handle drawing disabled — we draw our own) bound via a `MarkSpanner` that maps marks to framework spans (`StyleSpan(b)`, `UnderlineSpan`, `StrikethroughSpan`, `BackgroundColorSpan`, `ClickableSpan`-like custom link span, `TypefaceSpan(mono)`). The spanner is pure and unit-tested: `document block → Spanned` is deterministic (Law L6).
2. **BlockTextView rules:** no scroll inside blocks (the document scrolls); `includeFontPadding=false` with our own line metrics; text IS the source for IME (`InputConnection` reads/writes the `Spanned` window directly within the block, §15.1).
3. **List rendering:** the RecyclerView grid lays out list items as blocks whose left inset carries the marker (bullet/number/checkbox) drawn by the item decoration — markers are never part of the text (Law L1: what you see is the file, markers included in exports but derived, not typed).
4. **Tables:** RecyclerView-of-RecyclerViews is banned (scroll trap, §17.1). A table block renders one custom view: measured columns, per-cell `StaticLayout`, cell editor is a popup `BlockTextView` anchored to the cell (cell content edits in place visually; the popup is transparent to the user).
5. **Pagination guides:** a `PagerMetrics` engine computes break lines from the same `StaticLayout` objects the blocks render with — guides are drawn as decorations at zero extra measure cost (§17.4 parity guarantee).

## 14.7 Memory and performance playbook

- **Window the document:** blocks are realized lazily (RecyclerView); a 300-page document keeps ~60 realized blocks. PagerMetrics for guides computes over offscreen blocks with cached `StaticLayout`s capped at 400.
- **Precompute once:** `StaticLayout` per block is cached by (text hash, width, textcache key); typing invalidates only the edited block (UX-26).
- **No allocation in `onDraw`** (lint + perf test): pens, paint, path objects are pooled per view.
- **Large text guard:** blocks > 20k chars (pasted walls) split visually into measured tiles internally while remaining one block in the model (Law L8 — the model never mutates to please the renderer).
- **Startup:** home renders first frame from Room index only; document content loads on open; cold-start budget §21.4 verified by macrobenchmark (TC-PERF-001).

## 15.4 Physical keyboards and pointers

| Input | Behavior | Test |
|---|---|---|
| Arrow keys | caret traversal across block boundaries in visual order; Up/Down preserve target x-column (column memory) | TC-EDIT-016 |
| Tab / Shift-Tab | indent/outdent list items; in tables moves cell focus | TC-EDIT-016 |
| Ctrl+B/I/U/S | mark toggles on selection or at caret (word-scope) | TC-EDIT-016 |
| Ctrl+Z / Ctrl+Y (Ctrl+Shift+Z) | same undo stack as soft keys (UX-28) | TC-EDIT-016 |
| Ctrl+F | opens find bar preselecting current word | TC-EDIT-016, TC-UX-004 |
| Esc | dismiss selection → toolbar → keyboard in that order | TC-UX-004 |
| Mouse/stylus selection | same handles logic; right-click opens local context menu (TalkBack-menu parity) | TC-EDIT-004 |
| IME + keyboard simultaneously | single op stream; composition from IME, shortcuts from keyboard — serialized by the bridge | TC-EDIT-IME-04 |

## 15.5 IME script format (the fuzzer's data)

Recorded scripts are JSON: `{ "keyboard": "gboard-en-sim", "events": [ {"t": 12, "call": "setComposingText", "args": ["hel"]}, {"t": 40, "call": "setComposingText", "args": ["hello"]}, {"t": 60, "call": "finishComposingText"}, {"t": 62, "call": "commitText", "args": ["\n"]}, ... ], "invariants": ["L2","L4","L5"] }`. Scripts ship in `core-editor/src/main/assets/imescripts/` (committed, reviewable). The fuzzer interleaves scripted events with random valid engine ops at recorded boundaries and asserts the listed invariants after every step (§15.3). Adding a keyboard = recording its script once; no code change.

## 16.3 Generator recipes (how the fuzzers randomize)

| Generator | Produces |
|---|---|
| `docs(n, kinds)` | valid documents: 1–400 blocks, kind mix honoring I4 (no nested tables), random marks satisfying I3 |
| `ops(k)` | op sequences biased toward the hard 20%: 40% split/merge at mark boundaries, 20% mark toggles spanning blocks, 20% list indent/outdent, 10% table ops, 10% unicode insert (planes 0/1/2/14: emoji, Devanagari, CJK, tags) |
| `imeEvents(k)` | valid `InputConnection` sequences from grammar (composing regions well-formed by construction) |
| `journals(k)` | op batches with randomized kill points for replay tests (P8, TC-STATE-005) |

Seeds print on failure and reproduce byte-identically in CI (Law L6 applied to the tests). The suite runs 5,000 cases per property per PR and 50,000 nightly; shrinking (minimal counterexamples) is required output for any red.

## 15.6 Selection engine internals

Selection state is a five-tuple: `(anchorBlock, anchorOffset, focusBlock, focusOffset, mode)` where mode ∈ {caret, word, paragraph, all, handle-drag}. Rules:

1. Selection may span blocks (unlike marks — marks never cross block boundaries; a cross-block selection applying bold splits into per-block ranges, TC-EDIT-005).
2. Word/paragraph snapping uses ICU `BreakIterator` (same as find, §17.9); double-tap = word, triple = paragraph (never "select all" on triple — one-handed accidents).
3. Handle-drag dispatches through the gesture arena with slop 8 dp and a 100 ms pre-drag delay on handles only; during drag, auto-scroll activates within 10% screen margins at velocity ∝ overshoot, and the selection preview updates per frame (no commit until release — undo sees one composite op).
4. The floating toolbar positions from the focus rect: above by default, flips below when clipped by app bar or IME top; x clamps to screen; it never overlays the selection band (UX-19) — verified by a geometry unit test with a matrix of rects.
5. "Select all" exists only in the overflow sheet and local context menu (not a gesture) to prevent accidental whole-doc operations; it confirms when doc > 5k words (destructive-paste risk).

## 15.7 The toolbar as a state machine

Toolbar visibility = f(selection, IME, sheets): visible iff selection non-caret ∧ no sheet open ∧ IME allowed visible. State transitions are explicit (sealed class), making the "toolbar stuck" bug class structurally impossible; the machine is exhaustively unit-tested (every event × every state). Buttons read active-state from the §14.5 boundary rule and disable nothing — unavailable actions hide (same philosophy as F-082, applied to formatting: e.g., "clear marks" hides when selection has none).

## 16.4 The failure museum (classic editor bugs and what kills each)

Every exhibit is a real bug class from a decade of mobile editors. The museum's label names the killing test — this is why the property suite exists.

| # | Exhibit | Killing test |
|---|---|---|
| 1 | "Undo deletes the wrong word after IME autocorrect" (composition commits as several ops) | IME-01 + P1: composition = one op |
| 2 | "Emoji splits into boxes when bolded" (surrogate halves) | EDIT-017 + P10 |
| 3 | "Bold bleeds into the next paragraph after merge" (mark ranges not remapped on merge) | EDIT-002 + P4 |
| 4 | "Cursor jumps to document start after rotation" (state in Activity, not retained core) | STATE-002 + L9 |
| 5 | "Typing lags after page 40" (whole-doc reflow per keystroke) | PERF-002 + §14.7 windowing |
| 6 | "Autosave wrote half a document during kill" (save not transactional) | STATE-005 + P8 |
| 7 | "Select-all + paste lost the last paragraph" (range end-exclusive mixups) | EDIT-012 + P1 half-open invariants |
| 8 | "Checkbox state ignored in export" (kind-specific fields dropped by exporter) | P7 + goldens |
| 9 | "Toolbar stayed after keyboard closed" (state machine holes) | §15.7 exhaustive transition test |
| 10 | "Same doc, different export bytes on re-export" (timestamps/hash drift) | LAW-003 goldens minus timestamps |
| 11 | "Numbered list renumbered wrong after deleting item 2 of 5" (renumber not an op) | EDIT-007 + P5 |
| 12 | "Link swallowed the space after it" (boundary rule §14.5 absent) | EDIT-005 boundary matrix |

Rule: any bug found in the wild joins the museum with a test id — the museum is append-only, like everything else in this program.

## 15.8 The composition queue (exact semantics)

States: `idle` → `composing(block, range)` → `committing` → `idle`. While `composing`: (1) all non-IME mutation requests enqueue (never merge); (2) journal writes for *prior committed* batches continue (durability does not wait for composition); (3) snapshots may run (they read last committed state); (4) find-highlight refresh defers; (5) AI cancellation cleanup defers. On `committing`: apply queued IME delta as one op batch; drain queue in FIFO; each drained item re-validates its precondition (e.g., highlight term still present) and self-drops if stale. Death in `composing`: uncommitted composition text is lost *by platform design* (never entered the op log); loss ≤ the composition itself — documented in the LAW-003 evidence, counted inside the 2-second L3 bound. Queue depth is bounded at 64 with overflow = invariant alarm (E_IME_VIOLATION) — deeper than any real burst.

## 16.5 Property-suite economics

PR runs: 5,000 cases/property ≈ 40 s JVM parallel — cheap enough to never skip. Nightly: 50,000 + cross-property composition (P1×P2×P8 chains). Failure budget: a property red is a G3/G4 gate blocker regardless of other greens (laws outrank features, §13.2). Shrink results are cached per seed so triage reads a minimal counterexample, not a stack trace. The suite's runtime is itself budgeted (§21.4 table) — property runtime creep is a defect against developer velocity, treated like any budget breach.
