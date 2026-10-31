@PART: APPENDICES
@PARTDESC: Machine-readable catalogues (features, UX, test cases), gate DoDs, environment and dependency pins, the BLOCKED register, and working templates. The appendices are parsed by tools/onedoc/traceability.py — keep their format exact.

# Appendix A — Feature catalogue (machine table)

Format: `| F-id | Name | Priority | Bindings |`. The bindings column lists case ids (comma-separated). This table is normative; Chapter 4 is its prose mirror.

| F-id | Name | Priority | Bindings |
|---|---|---|---|
| F-001 | One-tap blank document | P0 | TC-LIB-001, TC-UX-001 |
| F-002 | Inline rename; title mirrors first heading | P0 | TC-LIB-002 |
| F-003 | Autosave via journal + debounced save | P0 | TC-STATE-001, TC-LAW-001 |
| F-004 | Star/pin | P1 | TC-LIB-003 |
| F-005 | Duplicate document | P1 | TC-LIB-004 |
| F-006 | Trash with undo snackbar | P0 | TC-LIB-005 |
| F-007 | Trash retention 30 days, restore, permanent delete | P1 | TC-LIB-006 |
| F-008 | Sorting modes persisted | P2 | TC-LIB-007 |
| F-009 | Empty states with CTA | P1 | TC-LIB-008 |
| F-010 | Document info sheet | P2 | TC-LIB-009 |
| F-011 | Multi-select bulk actions | P1 | TC-LIB-010 |
| F-012 | Cold start < 1.2 s Tier B / 200 docs | P0 | TC-PERF-001 |
| F-013 | Block editing with IME composition safety | P0 | TC-EDIT-001, TC-EDIT-IME-01 |
| F-014 | Enter split / Backspace merge | P0 | TC-EDIT-002 |
| F-015 | Undo/redo global stack, coalesced, grouped composites | P0 | TC-EDIT-003, TC-PROP-P01 |
| F-016 | Selection handles + floating toolbar | P0 | TC-EDIT-004 |
| F-017 | Marks set with non-overlap invariant | P0 | TC-EDIT-005, TC-LAW-002 |
| F-018 | Headings H1–H3, outline-driven | P0 | TC-EDIT-006 |
| F-019 | Lists: bullet, numbered, checklist | P0 | TC-EDIT-007 |
| F-020 | Quote and code blocks | P1 | TC-EDIT-008 |
| F-021 | Per-block alignment | P1 | TC-EDIT-009 |
| F-022 | Divider block | P2 | TC-EDIT-010 |
| F-023 | Paste (text/HTML subset/image), sanitized | P0 | TC-EDIT-011 |
| F-024 | Cut/copy multi-block; paste round-trip | P0 | TC-EDIT-012 |
| F-025 | Find & replace with pre-edit version on replace-all | P0 | TC-EDIT-013 |
| F-026 | Find bar counts and navigates hits | P0 | TC-EDIT-014 |
| F-027 | Live word/char count + info sheet | P1 | TC-EDIT-015 |
| F-028 | Hardware keyboard shortcuts | P1 | TC-EDIT-016 |
| F-029 | Typing P95 < 50 ms; no burst frame drops | P0 | TC-PERF-002 |
| F-030 | Orientation/process-death state restore | P0 | TC-STATE-002 |
| F-031 | Tables: structure ops, marks in cells | P0 | TC-TBL-001 |
| F-032 | Table width presets, wrap, no horizontal scroll | P0 | TC-TBL-002 |
| F-033 | Image insert (gallery/camera), captions, viewer | P0 | TC-IMG-001 |
| F-034 | Image resize presets + alt text | P1 | TC-IMG-002 |
| F-035 | TOC block from headings | P1 | TC-STRUCT-001 |
| F-036 | Document map sheet | P2 | TC-STRUCT-002 |
| F-037 | Page setup (paper/margins) | P1 | TC-STRUCT-003 |
| F-038 | Page-break guides parity with PDF ±1 line | P1 | TC-STRUCT-004 |
| F-039 | Footnotes (editor + PDF) | P2 | TC-STRUCT-005 |
| F-040 | Cover block | P2 | TC-STRUCT-006 |
| F-041 | Drag-to-reorder blocks + a11y equivalent | P1 | TC-STRUCT-007 |
| F-042 | Duplicate/delete block | P1 | TC-STRUCT-008 |
| F-043 | Code block language label | P2 | TC-STRUCT-009 |
| F-044 | Asset manager, unused cleanup | P2 | TC-IMG-003 |
| F-045 | 12 built-in templates | P0 | TC-TPL-001 |
| F-046 | Template preview | P1 | TC-TPL-002 |
| F-047 | Template instantiate-as-copy | P0 | TC-TPL-003 |
| F-048 | Placeholders incl. auto date | P1 | TC-TPL-004 |
| F-049 | Save-as-template from documents | P1 | TC-TPL-005 |
| F-050 | Template gallery states, user section | P2 | TC-TPL-006 |
| F-051 | PDF export (Print framework, embedded fonts) | P0 | TC-IO-001, TC-STRUCT-004 |
| F-052 | .odoc export lossless | P0 | TC-IO-002, TC-LAW-001 |
| F-053 | Markdown/txt/HTML export per fidelity | P0 | TC-IO-003 |
| F-054 | DOCX export (OOXML subset) | P1 | TC-IO-004 |
| F-055 | Import odoc/md/txt/html/docx with notes | P0 | TC-IO-005 |
| F-056 | Refuse unsupported with reason | P0 | TC-IO-006 |
| F-057 | Share via export + FileProvider | P0 | TC-IO-007, TC-SEC-IO-02 |
| F-058 | Open-in intent filters | P1 | TC-IO-008 |
| F-059 | SAF import/export | P0 | TC-IO-009 |
| F-060 | Encrypted weekly backup to SAF (off default) | P2 | TC-IO-010, TC-IO-013 |
| F-061 | Versions: auto/manual/pre-edit policy | P0 | TC-STATE-003 |
| F-062 | Version preview + non-destructive restore | P0 | TC-STATE-004 |
| F-063 | Journal durability (kill -9 zero loss) | P0 | TC-STATE-005, TC-LAW-003 |
| F-064 | Storage accounting + asset cleanup | P2 | TC-STATE-006 |
| F-065 | Schema migration chain tested | P0 | TC-STATE-007 |
| F-066 | Multi-window save-on-focus-loss | P1 | TC-STATE-008 |
| F-067 | FTS search < 300 ms / 200 docs | P0 | TC-SRCH-001 |
| F-068 | Deep-link to hit block with highlight | P0 | TC-SRCH-002 |
| F-069 | Shared highlight system with find bar | P1 | TC-SRCH-003 |
| F-070 | Semantic search when pack present, labeled | P2 | TC-SRCH-004 |
| F-071 | Scan-to-doc with confidence marks | P0 | TC-SCAN-001, TC-AI-001 |
| F-072 | Multi-page scan queue + reorder | P1 | TC-SCAN-002 |
| F-073 | OCR on-device only; graceful absence | P0 | TC-AI-002 |
| F-074 | Dictation with live partials, explicit insert | P0 | TC-AI-003 |
| F-075 | Assistant verbs with preview cards | P0 | TC-AI-004 |
| F-076 | gemma-2B Tier A; extractive fallbacks elsewhere | P0 | TC-AI-005 |
| F-077 | Streamed, cancellable, pre-edit snapshotted | P0 | TC-AI-006 |
| F-078 | Pack manager: side-load, SHA verify, delete | P0 | TC-AI-PACK-01 |
| F-079 | Corrupt pack refused; ladder descent | P0 | TC-AI-PACK-02 |
| F-080 | Read aloud with sentence highlight | P1 | TC-AI-007, TC-READ-001 |
| F-081 | Read-aloud ranges + system voice/rate | P2 | TC-AI-008 |
| F-082 | Unavailable AI hides with reason | P0 | TC-AI-009 |
| F-083 | Reader mode | P1 | TC-READ-001 |
| F-084 | TalkBack block traversal + actions | P0 | TC-A11Y-001 |
| F-085 | Contrast ≥ 4.5:1 all themes | P0 | TC-A11Y-002 |
| F-086 | 200% dynamic type, no clipping | P0 | TC-A11Y-003 |
| F-087 | 8 themes, match-system default | P1 | TC-SET-001 |
| F-088 | Editor settings (font/size/spell) | P1 | TC-SET-002 |
| F-089 | About + diagnostics + self-test | P1 | TC-SET-003, TC-DIAG-001 |
| F-090 | Locales en/hi/mr, RTL mirroring | P2 | TC-SET-004 |

# Appendix B — UX acceptance criteria (machine table)

| UX-id | Criterion (short) | Bindings |
|---|---|---|
| UX-01 | FAB → editor directly, doc on first keystroke | TC-UX-001 |
| UX-02 | Blank→first char ≤ 2 taps, ≤ 2 s | TC-UX-001, TC-PERF-001 |
| UX-03 | Export PDF ≤ 3 taps | TC-UX-002 |
| UX-04 | Import ≤ 2 taps | TC-UX-003 |
| UX-05 | Find bar remembers term, clean dismiss | TC-UX-004 |
| UX-06 | AI/paste inserts undo as one group | TC-UX-005, TC-EDIT-003 |
| UX-07 | Restore ≤ 30 s / 50 pages | TC-STATE-004 |
| UX-08 | Search results from ≤ 2 chars | TC-SRCH-001 |
| UX-09 | Scan page → text ≤ 60 s Tier B | TC-SCAN-001 |
| UX-10 | Dictation first partial ≤ 1.5 s | TC-AI-003 |
| UX-11 | kill mid-typing: zero loss | TC-STATE-005 |
| UX-12 | Rotation/split keeps cursor + composition | TC-STATE-002 |
| UX-13 | No save dialogs, autosave silent | TC-STATE-001 |
| UX-14 | Trash undo 7 s; 30-day retention | TC-LIB-005, TC-LIB-006 |
| UX-15 | Failed import: no empty doc, clipboard intact | TC-IO-006 |
| UX-16 | Replace-all: confirm + pre-edit version + undo | TC-EDIT-013, TC-STATE-004 |
| UX-17 | Storage-full: in-memory continue, auto retry | TC-STATE-009 |
| UX-18 | Export failure: no partial file, specific reason | TC-IO-011 |
| UX-19 | Toolbar never covers selection | TC-UX-006 |
| UX-20 | Targets ≥ 48 dp (44 toolbar) | TC-UX-006 |
| UX-21 | System-standard long-press select; stylus/mouse | TC-EDIT-004 |
| UX-22 | IME composition: no flicker/dup/loss | TC-EDIT-IME-01 |
| UX-23 | Enter continues list; exits on empty | TC-EDIT-007 |
| UX-24 | Style switch preserves marks | TC-EDIT-006 |
| UX-25 | Scroll anchored during IME show/hide | TC-UX-007 |
| UX-26 | No whole-doc reflow while typing | TC-PERF-002 |
| UX-27 | Scroll mid-composition cancels cleanly | TC-EDIT-IME-02 |
| UX-28 | Hardware shortcuts match platform; undo parity | TC-EDIT-016 |
| UX-29 | AI only via preview + explicit insert | TC-AI-006 |
| UX-30 | Unavailable AI says why in one line | TC-AI-009 |
| UX-31 | No notifications beyond user-created/progress | TC-SEC-P-02 |
| UX-32 | One-card first launch; permissions at use | TC-UX-008 |
| UX-33 | Delete warns version count; trash double-confirm | TC-LIB-006 |
| UX-34 | Diagnostics on-device only, self-test ≤ 20 s | TC-SET-003, TC-DIAG-001 |
| UX-35 | Destructive: haptic + undoable/double-confirm | TC-UX-009 |
| UX-36 | Empty states one line one action | TC-LIB-008 |
| UX-37 | TalkBack-complete letter flow | TC-A11Y-001 |
| UX-38 | Alt-text prompted at insert | TC-IMG-001 |
| UX-39 | 200% scale: no clipping | TC-A11Y-003 |
| UX-40 | Dark + high-contrast themes pass contrast | TC-SET-001 |
| UX-41 | Color never sole carrier | TC-AI-001 |
| UX-42 | Primary actions bottom 40% | TC-UX-010 |
| UX-43 | RTL mirroring correct | TC-SET-004 |
| UX-44 | Reduced-motion honored | TC-UX-011 |
| UX-45 | Import states achieved fidelity | TC-IO-005 |
| UX-46 | OCR low-confidence marked/fixable; export honest | TC-AI-001 |
| UX-47 | AI results label method | TC-AI-004, TC-AI-005 |
| UX-48 | Pack install shows SHA; failure shows both | TC-AI-PACK-01, TC-AI-PACK-02 |
| UX-49 | Word count matches export ±1% | TC-IO-001 |
| UX-50 | No marketing/network content ever | TC-SEC-P-03 |

# Appendix AN — document.json schema reference (field tables)

**Root**: `schema:int` (3) · `docId:string` (`d_`+8 hex) · `meta{title, created, modified?, wordCount, pageSetup{paper:A4|Letter, margin:normal|narrow|wide}}` · `blocks:Block[]`.

**Block** (all kinds): `id:string` (`b`+n, unique) · `type:Kind` · optional `align:left|center|right|justify` (non-heading). Per kind:

| Kind | Extra fields |
|---|---|
| para | `text:string`, `marks:Mark[]` |
| h1/h2/h3 | `text`, `marks` |
| list | `listType:bullet|number|check`, `items:[{id, text, marks, checked:bool|null}]`, `level:int (0–4)` |
| quote | `text`, `marks` |
| code | `text` (marks empty, enforced), `language:string?` |
| table | `header:bool`, `cols:[{width:equal|content}]`, `rows:[{id, cells:[{id, blocks:Block[] (depth 1: para/list only)}]}]` |
| image | `assetId`, `size:S|M|L|full`, `alt:string?`, `caption:blockId?` |
| divider | — |
| toc | `depth:1|2|3` (rendered, not stored per entry) |
| footnote | `text`, `marks` |
| cover | `title`, `subtitle?`, `date?` |

**Mark**: `type:strong|em|u|strike|code|highlight|link` · `start:int` · `end:int` (half-open, UTF-16 units) · `href:string?` (link only).

Validation (I1–I4, §14.2) runs on open, on import, and after every op batch in debug. The schema is versioned by `schema`; migrations map N→N+1 only (§11.4); unknown `type` values are preserved verbatim (L8) with round-trip tests (TC-LAW-004).
