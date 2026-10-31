@PART: PART VII — FILES, FORMATS AND FIDELITY
@PARTDESC: The honest format matrix, the exporters and importers, sharing and SAF, backup. OneDoc never lies about fidelity: every conversion states what it kept and what it dropped.

# Chapter 18 — Files and formats

## 18.1 Principles

1. **Refuse, don't guess.** An importer that cannot represent content returns a specific refusal (format X, feature Y), never an empty document (F-056, UX-15).
2. **Declare fidelity.** Every conversion result carries a fidelity level (§18.2) shown to the user (UX-45) and asserted by tests (property P7).
3. **Lossless native.** `.odoc` is the canonical form; every other format is a projection. Importers that cannot map something preserve it in a round-trip-safe extension when the target is `.odoc` (Law L8).
4. **No network, ever.** "Open with" handlers accept local files/streams only; URIs requiring remote fetch are refused with a reason (C1).

## 18.2 The fidelity matrix

![Format matrix with declared fidelity levels and covered subsets.](figures/fig-formats.png)

| Format | Direction | Level | Covered subset |
|---|---|---|---|
| OneDoc `.odoc` | in+out | **F3** | everything (zip: document.json + assets + meta) |
| Markdown `.md` | in+out | **F2** | h1–h3, para, bullet/number/check lists, quote, code, divider, strong/em/code/highlight/link marks, pipe tables |
| Plain text `.txt` | in+out | **F1** | text only; blank-line paragraph inference on import |
| HTML `.html` | in+out | **F2** | h1–h3, p, ul/ol/li, blockquote, pre/code, table (simple), img, strong/em/u/s/a, mark; scripts/styles stripped always |
| PDF (export) | out | **F3** | paginated via Print framework, fonts embedded, selectable text, TOC page numbers, table header repeat, footnotes |
| PDF (import) | — | **F0** | refused in v1.0 ("use Scan-to-doc for page images") — honest and better than garbage text |
| DOCX (export) | out | **F2** | styles for headings, para+marks, lists, tables, images, page setup |
| DOCX (import) | in | **F1** | best-effort text + basic marks; unsupported constructs listed per-paragraph in the conversion note |

F0 = refused with reason · F1 = best-effort, stated · F2 = lossless for the covered subset, everything else degrades with a note · F3 = lossless. The conversion note (UX-45) is generated from a structured diff (elements dropped/transformed count), not a canned string.

## 18.3 Exporters

Export is a pure function in `core-io`: `document.json → bytes` with golden-file tests per format (Law L6). PDF export uses `PdfDocument`/Print framework with the pagination metrics from §17.4; embedded fonts are subset Inter + DejaVu fallback chain; exported bytes are deterministic except the embedded creation timestamp (excluded from golden comparison). DOCX export writes a minimal but valid OOXML package (validated against the OOXML strict subset in tests by re-opening with the importer — round-trip gate). Share sheet (F-057) exports to cache and hands a `FileProvider` URI; private paths are never shared raw.

## 18.4 Importers

Import order of operations: sniff magic bytes/MIME → choose reader → parse to a candidate `document.json` → validate (I1–I4) → produce conversion note → open editor. SAF sources stream; sizes over 50 MB warn (mobile RAM honesty) but proceed. HTML import sanitizes by whitelist parser (no regex parsing, ever — the parser is a real tokenizer with tests; scripts/styles/event attributes cannot survive it, proven by TC-SEC-IO-01). DOCX import reuses the shared OOXML subset reader; features beyond it become per-paragraph notes.

## 18.5 Sharing, open-in and SAF (F-057 … F-059)

Intent filters: `application/zip` view for `.odoc`, `text/markdown`, `text/plain`, `text/html` — `android.intent.action.VIEW` with content: URIs only. Export uses `ACTION_CREATE_DOCUMENT`; import reads via `ContentResolver` with size caps. The app registers no launcher handlers for URLs/links that imply network fetch. Round-trip case TC-IO-012 proves share→receive→import→export parity for md/html/odoc on the emulator.

## 18.6 Backup and restore (F-060)

Weekly (default off) background backup: zip of all non-trashed documents (odoc form) + manifest with SHAs → user-chosen SAF folder → encrypted (§11.5). Restore imports the manifest, diffs by docId+content hash, and imports as new versions on top of existing docs (never silently overwrites); the restore report lists added/updated/conflicts. TC-IO-013 runs backup→wipe→restore on the emulator and asserts the library is byte-identical at F3.

## 18.7 Charset and encoding policy

All text is UTF-8 at rest (document.json, exports except UTF-16 for DOCX XML which mandates UTF-8 too — compliant). Offsets in the model are UTF-16 code units to mirror JVM strings exactly (§14.2 I2); exporters that emit UTF-8 bytes recount line/char metrics in their own units (word count is grapheme-cluster based via ICU, the number users see everywhere — one definition, TC-EDIT-015). BOM policy: readers accept and strip; writers never emit. Legacy encodings (latin-1, UTF-16 txt): sniffed via BOM/validators; converted with a conversion note; binary-garbage detection (NUL bytes, < 90% valid decode) refuses with reason (F-056).

## 18.8 IO error taxonomy and user strings (normative examples)

| Error | Verb | User string (en) |
|---|---|---|
| `E_IO_SAF_DENIED` | actionable | "OneDoc can't write to that folder. Pick a different location." |
| `E_IO_UNSUPPORTED {fmt}` | actionable | "{fmt} isn't supported. Supported: odoc, md, txt, html, docx." |
| `E_IO_CORRUPT {fmt, why}` | actionable | "This file is damaged ({why}). OneDoc won't risk opening it." |
| `E_IO_TOO_LARGE` | actionable | "That file is over 50 MB — too big for a phone to convert safely." |
| `E_IO_DISK_FULL` | retryable | "Storage is full. Free some space — OneDoc will retry." |
| `E_IO_PARTIAL_WRITE` | retryable | "Writing was interrupted. Retrying…" (auto; no partial file remains, UX-18) |

Every error kind has exactly one string in every shipped locale; the strings catalog test enumerates the taxonomy (no orphan strings, no missing strings — TC-SET-004 extended).

## 18.9 Golden-file management

Golden corpus: `core-io/src/test/resources/golden/<format>/` — input fixtures + expected outputs, byte-exact for odoc/md/html/txt, normalized (timestamps stripped) for pdf/docx. Regeneration is an explicit task (`--update-goldens`) whose diff MUST be reviewed line-by-line in the PR (silent golden churn is how fidelity regressions sneak through). New exporter feature ⇒ new golden case in the same PR (checklist §29.5). Round-trip goldens pair with property P7; a golden change without a P7-observed behavior change is suspect by default.

## 18.10 Per-format implementation specs (writers)

**Markdown writer rules.** Headings `#`×level; blank line between blocks; bold `**`, italic `*` (nested → `***` at shared boundaries); code spans pick backtick runs (longest-run fencing, §13.4-style rule); lists `-` / `1.` / `- [x]`; tables GFM pipe style with escaped pipes (`\\|`); links `[t](href)` with URL-escaped parens/spaces; check state → `[ ]`/`[x]`; no reference links (inline only — deterministic output).

**HTML writer rules.** One `<article>` root; semantic tags only from the §18.2 subset; marks map strong/em/u/s/code/mark/a; `lang` on root; checklists render `<li data-check="done">` (documented extension); images `<img src="assets/<sha>.<ext>">` inside a zip-flavored payload when sharing, or base64 when single-file requested (size warn > 2 MB).

**DOCX writer rules.** Styles: Heading1–3 ↔ h1–h3; Normal ↔ para; ListParagraph+numbering.xml ↔ lists; bold/italic/underline/strike runs ↔ marks; `w:shd` highlight ↔ highlight; tables `w:tbl` with `w:tblW` pct; images inline with extent; core props (title, created) from meta. The writer emits a minimal, valid package — validated by reopening with the importer plus an XML-schema subset check (TC-IO-004).

## 18.11 Per-format implementation specs (readers)

**Markdown reader.** Line-based state machine: ATX headings, setext rejected (note), fences with language capture, GFM tables, task lists, nested lists by indent (2/4-space tolerated, normalized), emphasis parser (delimiter-run algorithm, CommonMark subset), links inline only, HTML passthrough **rejected** (security posture, §20.4) with note. Undecidable constructs are not guessed: a setext heading becomes a paragraph with a note line, never silently.

**HTML reader.** Real tokenizer (state machine per WHATWG scanning subset) → whitelist tree → model. Unknown-but-harmless tags unwrap (keep text); hostile constructs (script/style/iframe/object/embed/form, on* attributes, javascript: URLs) drop structurally and count into the conversion note. Entities decoded via a fixed table (no external fetches — ever, for any purpose).

**DOCX reader.** Zip → document.xml walk: paragraphs with runs (rPr → marks), numbering refs → list kinds, tables (nested tables → flattened with note), images → assets, headers/footers/footnotes → v1.0: footnotes mapped to footnote blocks; headers/footers dropped with note. `w:ins`/`w:del` (tracked changes) → accepted text with a "tracked changes were flattened" note (§30.2 shelf: preserve as suggestions).

## 18.12 Worked fidelity examples (what the note actually says)

1. **Docs-exported HTML with a comment thread** → import: "Imported as HTML — F2. Kept: headings, paragraphs, bold/italic, one list. Dropped: 2 comment threads, 1 embedded drawing (image-only frame kept as image)."
2. **Word file with tracked changes** → "Imported as Word — F1. Kept: text, headings, bold/italic/underline, one table (2 columns flattened to paragraphs: 1 of 9). Flattened: tracked changes (accepted text). Dropped: header/footer."
3. **Markdown with setext heading** → "Imported as Markdown — F2. Note: 1 underline-style heading read as a paragraph (OneDoc keeps # headings)."
4. **HTML with script** → "Imported as HTML — F2. Removed for safety: 1 script block, 1 form." (SEC-IO-01 pairs with this note in tests.)
5. **DOCX with SmartArt** → "Imported as Word — F1. Dropped: 1 SmartArt diagram (content listed below as text)."
6. **PDF** → refused: "PDF isn't imported in OneDoc. Use Scan to doc for page images — it's better for real-world PDFs."

Each example is a golden test input (§18.9) — the note text above is asserted verbatim (en locale) by TC-IO-005's dataset.

## 18.13 PDF export internals

Engine: `android.print` with a custom `PrintDocumentAdapter` rendering through the same PagerMetrics (§17.4) to `PdfDocument` pages (A4/Letter per F-037). Fonts: Inter regular/semibold subsets embedded per page-family; DejaVu fallback chain for glyphs Inter lacks (Devanagari matras render via system Noto — subset embedded likewise). Text layer: real glyph runs (selectable/searchable, UX-49 count source). TOC entries carry link annotations to target pages; internal links (F-035) preserved; table headers repeat per break via per-page re-render of the header row region; footnotes bottom-of-page regions (§17.4). Metadata: title/author from doc meta; creation timestamp only (excluded from goldens). Deterministic layout: same doc+settings+font set → identical page breaks (LAW-003 asserts).
