# Appendix O — Worked examples (engine traces for the implementer)

## O.1 Trace: six keystrokes from screen to disk

Scenario: new document; user types `Hi!` then Enter then `Q3 report`, with `Q3` pre-typed bold via toolbar. Timeline (T = ms since first key):

| T | Event | Op applied | Journal record (after CRC, framing) | Notes |
|---|---|---|---|---|
| 0 | 'H' | insertText(b01, 0, "H") | rec#1 | block b01 created as `para` (new doc auto-creates one empty para; Law L1: the file contains it) |
| 120 | 'i' | insertText(b01, 1, "i") | rec#2 | coalescing window open (600 ms) |
| 300 | '!' | insertText(b01, 2, "!") | rec#3 | same batch |
| 980 | Enter | splitBlock(b01, 3) | rec#4 | new batch (idle > 600 ms); b02 created |
| 1100 | select "Q3" + Bold | setMarks(b02, strong, 0, 2) | rec#5 | toolbar one-tap; snapshot? no — policy §12.2 not met yet |
| 1500 | type 'Q','3',' ','r'… | insertText×4 coalesced | rec#6 | bold extends per §14.5 |

At T=2,300 ms (800 ms after last op): debounced save folds rec#1–6 into checkpoint `checkpoints/0.json.zip` and updates Room row (title="Hi", wordCount≈3). Journal truncates to empty after fold (§11.3 compaction bound). Kill at any T: replay produces exactly the table's states — this trace is TC-STATE-005's determinism fixture.

## O.2 Trace: mark normalization on merge

Before: block X: `[bold 0,5)`, block Y: `[bold 0,3)`; delete Y's first paragraph mark boundary then merge Y into X (Backspace at Y start) with Y text "abc def" → X "…xyzabc def":

```
X.text = "…xyz", Y.text = "abc def"
merge → text "…xyzabc def"
marks before normalize: [bold 0,5), [bold 5,8)      # adjacent same-type
normalize → [bold 0,8)                               # merged (idempotent check: second pass no-op)
```

Counter-case (different types): `[bold 0,5)`, `[italic 5,8)` → normalize keeps both (different types may abut); `[highlight 2,6)`, `[highlight 5,9)` → impossible post-op state; normalize folds to `[highlight 2,9)` and logs invariant repair (debug: fail-fast). P2 generates thousands of these; the trace above is the human-readable contract.

## O.3 Trace: one document through four exporters

Source: H1 "Invoice", para "Total **$42** due Friday", checklist 2 items (1 checked).

- **Markdown (F2):**
```markdown
# Invoice

Total **$42** due Friday

- [x] Send to Ada
- [ ] Archive receipt
```
- **HTML (F2):**
```html
<h1>Invoice</h1>
<p>Total <strong>$42</strong> due Friday</p>
<ul><li data-check="done">Send to Ada</li><li>Archive receipt</li></ul>
```
- **DOCX (F2):** Heading1 style "Invoice"; paragraph with bold run "$42"; list paragraphs `w:numPr` with checkbox glyphs for check lists (conversion note: "checklist state stored as glyph + custom prop").
- **PDF (F3):** A4 page 1: H1 20/26 at margins; body 15/22; checklist boxes drawn; fonts embedded (Inter subset); text layer selectable; word count 9 (matches editor chip; UX-49 tolerance ±1%).

Each exporter's full golden files for this exact source live at `core-io/src/test/resources/golden/showcase/` — a failing exporter diff explains itself against these.

## O.4 Trace: a blocked gesture correctly reported (doctrine in motion)

Claimed case: "drag handle from word A to selection end across 3 blocks fails". Scripted `adb input swipe` cannot perform a stationary hold-then-drag with intermediate events (predecessor doctrine). Verdict path: run → driver marks `TC-EDIT-004-draglong` **BLOCKED**, reason "input synthesis cannot reproduce hold-then-drag; requires physical device or instrumentation gesture injection", fingerprint `(api33, uiautomator2)` → register Appendix G entry → instrumented variant runs `MotionEvent` injection via `UiAutomation` → if that PASSes, case closes as PASS with both evidences; if it FAILs, defect OD-0nn with repro video frames. At no point does the blocked attempt count as a product failure or a health signal.
