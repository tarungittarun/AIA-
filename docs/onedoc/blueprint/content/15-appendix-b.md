# Appendix C — Test catalogue (case tables, part 1)

Format per area: `| Case | Binding | Proves | Level |`. Levels: L1 JVM, L2 Robolectric, L4 instrumentation/emulator, L5 physical-only (pre-registered BLOCKED otherwise), G = CI gate. The catalogue is parsed by `tools/onedoc/traceability.py`; `--check` enforces that every F/UX binding above resolves to a case here.

## Laws (L)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-LAW-001 | F-003, F-052 | persisted doc equals on-screen text+marks after autosave | L2/L4 |
| TC-LAW-002 | F-017 | normalize restores non-overlap; idempotent | L1 |
| TC-LAW-003 | F-063 | deterministic engine: same ops → identical results + export bytes | L1 |
| TC-LAW-004 | F-052, F-055 | unknown block kinds round-trip verbatim | L1/L4 |

## Library (LIB)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-LIB-001 | F-001 | FAB opens editor; doc created on first keystroke | L4 |
| TC-LIB-002 | F-002 | rename inline; untitled mirrors first heading | L2/L4 |
| TC-LIB-003 | F-004 | star pins to top on All | L2/L4 |
| TC-LIB-004 | F-005 | duplicate copies content+assets, new id | L2 |
| TC-LIB-005 | F-006 | trash + 7 s undo snackbar restores | L4 |
| TC-LIB-006 | F-007 | retention timer, restore, permanent delete confirm | L2/L4 |
| TC-LIB-007 | F-008 | sort modes persist across launch | L2/L4 |
| TC-LIB-008 | F-009, UX-36 | empty states render with CTA | L4 |
| TC-LIB-009 | F-010 | info sheet numbers correct (words/chars/size) | L2/L4 |
| TC-LIB-010 | F-011 | multi-select actions on 3 docs | L4 |

## Editor core (EDIT)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-EDIT-001 | F-013 | per-block typing; caret behavior at block edges | L4 |
| TC-EDIT-002 | F-014 | split/merge preserves marks per rules | L2/L4 |
| TC-EDIT-003 | F-015, UX-06 | undo/redo semantics incl. grouped composites | L2 |
| TC-EDIT-004 | F-016, UX-21 | selection handles, toolbar actions, stylus/mouse | L4 |
| TC-EDIT-005 | F-017 | each mark type on/off/overlap normalization | L2 |
| TC-EDIT-006 | F-018, UX-24 | heading switches keep marks; outline updates | L2/L4 |
| TC-EDIT-007 | F-019, UX-23 | list continue/exit, renumber, checkbox toggle | L2/L4 |
| TC-EDIT-008 | F-020 | quote/code blocks; code disables marks | L2/L4 |
| TC-EDIT-009 | F-021 | four alignments render and persist | L2/L4 |
| TC-EDIT-010 | F-022 | divider insert/delete semantics | L2 |
| TC-EDIT-011 | F-023 | paste text/HTML subset/image, sanitized | L2/L4 |
| TC-EDIT-012 | F-024 | multi-block cut/copy/paste exact round-trip | L2/L4 |
| TC-EDIT-013 | F-025, UX-16 | find/replace options; replace-all versions first | L2/L4 |
| TC-EDIT-014 | F-026 | hit count, navigation, non-destructive highlight | L2/L4 |
| TC-EDIT-015 | F-027 | live counts correct on edit/undo | L2 |
| TC-EDIT-016 | F-028, UX-28 | hardware shortcuts + undo parity | L4 |
| TC-EDIT-017 | F-013 | emoji/surrogate boundaries edit atomically | L2 |

## IME (EDIT-IME)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-EDIT-IME-01 | F-013, UX-22 | glide/autocorrect full-replace lands as one op | L4 |
| TC-EDIT-IME-02 | UX-27 | scroll mid-composition cancels cleanly | L4 |
| TC-EDIT-IME-03 | F-013 | Devanagari clusters never split | L2/L4 |
| TC-EDIT-IME-04 | F-013 | IME fuzzer: laws hold under random valid sequences | L2/L4 |

## Property suite (PROP) — `core-model`/`core-editor`

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-PROP-P01 | F-015 | undoAll(apply(D,O)) == D | L1 |
| TC-PROP-P02 | F-017 | normalize idempotent | L1 |
| TC-PROP-P03 | F-003 | plainText integrity, length sums | L1 |
| TC-PROP-P04 | F-014 | split/merge inverses | L1 |
| TC-PROP-P05 | F-041 | move/remove preserve ids, no holes | L1 |
| TC-PROP-P06 | F-031 | table ops never orphan cells; depth-1 | L1 |
| TC-PROP-P07 | F-052, F-055 | export/import round-trip per fidelity | L1 |
| TC-PROP-P08 | F-063 | journal replay == in-memory application | L1 |
| TC-PROP-P09 | F-062 | restore leaves valid cursor | L1 |
| TC-PROP-P10 | F-013 | random Unicode planes never corrupt offsets | L1 |

## State & durability (STATE)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-STATE-001 | F-003, UX-13 | silent autosave; exit never asks | L2/L4 |
| TC-STATE-002 | F-030, UX-12, L9 | rotation/split restore cursor+selection | L4 |
| TC-STATE-003 | F-061 | snapshot policy fires at 5 min/50 ops/pre-edit | L2/L4 |
| TC-STATE-004 | F-062, UX-07 | preview + restore non-destructive, ≤ 30 s | L4 |
| TC-STATE-005 | F-063, UX-11 | 100 kill trials: ≤ 2 s loss bound (in practice 0) | L4 |
| TC-STATE-006 | F-064 | storage accounting matches files; cleanup safe | L2 |
| TC-STATE-007 | F-065 | migration chain v1→vN on seeded corpora | L4 |
| TC-STATE-008 | F-066 | split-screen focus-loss saves | L4 |
| TC-STATE-009 | UX-17 | storage-full: memory continue, auto retry | L2/L4 |

## Tables / Images / Structure

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-TBL-001 | F-031 | table ops + marks in cells + editing | L2/L4 |
| TC-TBL-002 | F-032 | wrap, presets, no horizontal doc scroll | L4 |
| TC-IMG-001 | F-033, UX-38 | insert flows, EXIF strip, alt-text prompt, viewer | L4 |
| TC-IMG-002 | F-034 | resize presets + alt-text editor | L2/L4 |
| TC-IMG-003 | F-044 | asset manager, unused cleanup with confirm | L2/L4 |
| TC-STRUCT-001 | F-035 | TOC generation, scroll, refresh | L2/L4 |
| TC-STRUCT-002 | F-036 | map sheet live position | L4 |
| TC-STRUCT-003 | F-037 | page setup changes measure + export | L2/L4 |
| TC-STRUCT-004 | F-038, F-051 | guide/PDF pagination parity ±1 line | L2/L4 |
| TC-STRUCT-005 | F-039 | footnotes editor + PDF | L2/L4 |
| TC-STRUCT-006 | F-040 | cover block renders + exports | L2/L4 |
| TC-STRUCT-007 | F-041 | drag reorder + a11y move actions | L4 |
| TC-STRUCT-008 | F-042 | duplicate/delete block | L2/L4 |
| TC-STRUCT-009 | F-043 | code language label persists | L2 |
