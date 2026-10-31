# Appendix AB — Journey step tables (driver-ready)

Each step: action (driver command class), assertion, evidence. Verbatim source for TC-J* procedures (§24.5).

## AB.1 J1 — letter to PDF

| # | Action | Assertion | Evidence |
|---|---|---|---|
| 1 | cold launch (data cleared) | home empty-state visible ≤ 1.2 s (frame log) | screenshot + startup log |
| 2 | tap FAB | editor visible, caret in body, no dialogs | screenshot |
| 3 | type 40-word salutation+body (scripted) | text present; count chip = truth | a11y tree dump |
| 4 | select first sentence | toolbar visible, not covering selection | screenshot |
| 5 | tap Bold | marks applied (tree: bold prefix) | tree |
| 6 | cursor to title line, apply H1 | heading role on block | tree |
| 7 | menu → Export PDF | export sheet, fidelity badge F3 | screenshot |
| 8 | save via SAF (Downloads) | done state ≤ 10 s (50th-pct of 3 runs) | log + timing |
| 9 | open exported PDF (system viewer) | pages render, text selectable (pdftotext on pull) | artifact PDF |
| 10 | assertions rollup | ≤ 2 taps to editor; word count ±1%; total ≤ 3 min median | steps.json |

## AB.2 J2 — scan three pages

| # | Action | Assertion |
|---|---|---|
| 1 | FAB → Insert → Scan | camera preview (virtual scene fixture) ≤ 2 s |
| 2 | capture page-01/02/03 | 3 thumbnails queued |
| 3 | drag page-02 before page-01 | order persists in queue |
| 4 | run OCR | processing state ≤ 12 s/page; cancel button live |
| 5 | review screen | low-confidence words marked (incl. fixture's 2 degraded words) |
| 6 | fix "cartridge" via fix field | corrected text replaces; mark cleared |
| 7 | Insert | paragraphs in chosen order; page separators; images as assets |
| 8 | conversion note | "OCR from 3 pages; 2 low-confidence words flagged; source images attached." |
| variant | no pack installed | flow ends after crop at save-image with reason (F-073) |

## AB.3 J3 — dictate, tidy, share DOCX

| # | Action | Assertion |
|---|---|---|
| 1 | new doc → dictate | mic permission at first use (UX-32); strip appears |
| 2 | play fixture audio | first partial ≤ 1.5 s; partials stream |
| 3 | stop | preview card with method label |
| 4 | Insert | one grouped op (single undo reverts) |
| 5 | H1 the date line; select paragraph | toolbar states correct |
| 6 | Summarize | rung-labeled card (extractive on 33; gemma on 36) |
| 7 | Insert below | pre_edit version created (versions screen count +1) |
| 8 | Export DOCX → share sheet | docx received by test receiver app |
| 9 | re-import the docx | headings/list parity per F2; note present |

## AB.4 J4 — find the warranty clause

| # | Action | Assertion |
|---|---|---|
| 1 | seed 200-doc corpus + manual | library shows 201 docs |
| 2 | search "warr" (2+ chars) | results streaming ≤ 300 ms; 3 docs hit |
| 3 | tap manual result | editor at hit block; "warranty" highlighted |
| 4 | back → search "what covers repairs" (embed pack) | related section labels manual; FTS section still primary |
| variant | no pack | related section absent; no error |

## AB.5 J5 — recover deleted half

| # | Action | Assertion |
|---|---|---|
| 1 | open report-50p.odoc | renders, position top |
| 2 | select blocks 100–214, delete | content gone; count drops |
| 3 | type replacement sentence | present |
| 4 | wait 1 s → `am kill` → relaunch → open doc | ALL content intact (zero loss) — journal replay |
| 5 | Versions → preview pre-delete auto snapshot | preview renders read-only |
| 6 | Restore | pre_edit snapshot created; deletion undone; redo cleared |
| 7 | timing | restore ≤ 30 s (50-page doc) |

# Appendix AC — Screen-to-feature trace

| Screen | Implements features | Cases exercising it |
|---|---|---|
| OD-HOME-001/002/003 | F-001…012, F-067 (entry) | LIB-001…010, SRCH-001/002, PERF-001 |
| OD-EDIT-001 compose | F-013…030, F-043, F-088 | EDIT-*, IME-*, PROP (indirect) |
| OD-EDIT-002 selection | F-016/017, F-041/042, UX-19/20/21 | EDIT-004/005, UX-006, A11Y-001 |
| OD-EDIT-003 insert sheet | F-031…040, F-071 (entry) | TBL/IMG/STRUCT cases, SCAN-001 |
| OD-EDIT-004 find bar | F-025/026, F-069 | EDIT-013/014, SRCH-003 |
| OD-TPL-001/002 | F-045…050 | TPL-001…006 |
| OD-SCAN-001…003 | F-071…073 | SCAN-001/002, AI-001/002, J2 |
| OD-AI-001…003 | F-074…082, F-078/079 | AI-*, AI-PACK-*, J3 |
| OD-FILE-001 versions | F-061…064 | STATE-003…006, J5 |
| OD-FILE-002/003 | F-051…060 | IO-* |
| OD-SET-001…004 | F-087…090, F-089 self-test | SET-001…004, DIAG-001 |
