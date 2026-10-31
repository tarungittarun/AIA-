# Appendix Y — The v1.0 build plan (seed tasks per gate)

Sequenced seed tasks; the agent expands just-in-time (§29.3) into `docs/onedoc/plan/task-graph.yaml`. Dependencies are within-gate unless noted. IDs are stable (T-Gn-nnn).

| Task | Gate | Depends | Deliverable (DoD hint) |
|---|---|---|---|
| T-G0-001 | G0 | — | owner acceptance recorded; ledgers seeded; traceability green |
| T-G1-001 | G1 | T-G0-001 | JDK/SDK/AVDs per App. E installed and boot-verified |
| T-G1-002 | G1 | T-G1-001 | Gradle skeleton: all modules assemble (full+writer flavors) |
| T-G1-003 | G1 | T-G1-002 | CI pr.yml green ≤ 8 jobs; budgets enforced (§22) |
| T-G1-004 | G1 | T-G1-002 | shell app: home empty-state + settings stub + About; icon/theme tokens in |
| T-G1-005 | G1 | T-G1-001 | qa-driver module skeleton; AVD boot snapshots; N.3 ritual scripted |
| T-G2-001 | G2 | T-G1-002 | core-model: blocks/marks/ops/normalize; invariants enforced |
| T-G2-002 | G2 | T-G2-001 | property harness + P1–P10 green (§16) |
| T-G2-003 | G2 | T-G2-001 | core-storage: Room schema v3 exported; ERD as built (§11) |
| T-G2-004 | G2 | T-G2-003 | journal write/replay/compact; kill-trial harness local pass (§12) |
| T-G2-005 | G2 | T-G2-003 | odoc container save/open + goldens; LAW-001/004 green |
| T-G3-001 | G3 | T-G2-005 | editor screen: block list + caret + keyboard bridge (§15.1) |
| T-G3-002 | G3 | T-G3-001 | IME contract + fuzzer harness green on 4 AVDs |
| T-G3-003 | G3 | T-G3-001 | selection engine + toolbar state machine (§15.6/15.7) |
| T-G3-004 | G3 | T-G3-003 | marks engine + §14.5 semantics + EDIT-005/006 |
| T-G3-005 | G3 | T-G3-001 | undo/redo + coalescing + EDIT-003; typing budget met |
| T-G3-006 | G3 | T-G3-005 | editor core DQ pass; a11y node contract (W.1) |
| T-G4-001 | G4 | T-G3-004 | tables (§17.1) + TBL cases |
| T-G4-002 | G4 | T-G3-004 | images/assets/alt (§17.2) + IMG cases |
| T-G4-003 | G4 | T-G3-004 | lists + quote/code + EDIT-007/008 |
| T-G4-004 | G4 | T-G3-003 | find bar + replace-all + versions-first (F-025/026) |
| T-G4-005 | G4 | T-G2-004 | versions UI + restore + STATE-003/004 |
| T-G4-006 | G4 | T-G2-003 | templates: 12 built-ins + save-as (§17.5) + TPL cases |
| T-G4-007 | G4 | T-G4-001 | TOC/map + page setup/guides (§17.3/17.4) |
| T-G4-008 | G4 | T-G4-007 | reader mode (§17.11) + READ-001 |
| T-G4-009 | G4 | T-G1-004 | library complete: filters, trash, multi-select, info sheet |
| T-G4-010 | G4 | all G4 | DQ-1…8 pass on every G4 screen |
| T-G5-001 | G5 | T-G2-005 | md/txt writers + goldens |
| T-G5-002 | G5 | T-G5-001 | html writer/reader (tokenizer) + SEC-IO-01 |
| T-G5-003 | G5 | T-G5-001 | docx writer/reader + round-trip gate |
| T-G5-004 | G5 | T-G5-002 | PDF export via Print framework + STRUCT-004 parity |
| T-G5-005 | G5 | T-G5-003 | share/open-in/SAF + IO-007/008/009/012 |
| T-G5-006 | G5 | T-G5-001 | conversion-note UX + refusal paths + IO-005/006/011 |
| T-G5-007 | G5 | T-G4-005 | backup/restore encrypted + IO-010/013 |
| T-G6-001 | G6 | T-G5-003 | pack manager + .odpack verify + AI-PACK cases |
| T-G6-002 | G6 | T-G6-001 | OCR pipeline (§19.12) + scan flows + SCAN/AI-001/002 |
| T-G6-003 | G6 | T-G6-001 | ASR streaming + dictation UX + AI-003 |
| T-G6-004 | G6 | T-G6-001 | LLM runtime (Tier A) + 4 verbs + preview cards + AI-004/005/006/010 |
| T-G6-005 | G6 | T-G6-001 | embeddings + semantic search + SRCH-004/005 |
| T-G6-006 | G6 | T-G4-008 | read aloud + AI-007/008 |
| T-G6-007 | G6 | T-G6-004 | ladder + hidden-with-reason everywhere + AI-009 |
| T-G6-008 | G6 | T-G6-002 | network-silence probe across AI flows (SEC-P-03) |
| T-G7-001 | G7 | all | full catalogue on matrix; journeys J1–J5 |
| T-G7-002 | G7 | T-G7-001 | perf budgets + size gate evidence |
| T-G7-003 | G7 | T-G7-001 | security suite + compliance map (X) current |
| T-G7-004 | G7 | T-G7-001 | evidence PDF assembled; BLOCKED register reviewed |
| T-G8-001 | G8 | T-G7-004 | release checklist (§28.1); provenance; GitHub Release; handoff note |

Rule: a task moves to `done` only with its evidence link in the graph; `blocked` requires reason + unblock plan (§29.4).

# Appendix Z — Redline tables for the remaining surfaces

## Z.1 Find & replace bar (OD-EDIT-004)

Bar height 48 dp under app bar; fields: find (auto-focused, last term preselected — UX-05), match count "n of total", prev/next (44 dp), toggle-case (Aa), whole-word (ab|), replace field + Replace / Replace all. Dismiss (×) clears highlights, leaves document untouched. Geometry: bar never pushes content down — it overlays with canvas inset animation 200 ms.

## Z.2 Replace-all confirm (dialog)

Title "Replace {n} matches?"; body one line: "A version of this document is saved first."; buttons Cancel / Replace (filled, amber-on-dark in HC themes). Second confirm never appears — the version IS the safety (UX-16).

## Z.3 Versions list (OD-FILE-001) redlines

Row: kind chip (Auto gray / Manual teal / Before change amber) + relative time + size; tap row = preview (read-only banner "Preview — Restore to edit"); Restore = primary button on preview, confirm only when current doc has unsaved-seeming deltas > 0 (it never does — autosave) — so no confirm: the pre-edit snapshot is the safety. Empty state: "Versions appear as you work. Nothing to manage yet."

## Z.4 Template gallery (OD-TPL-001/002)

Grid 2-col cards: name + 3-line ghost preview (no real text — privacy in screenshots); preview screen = reader-mode render with placeholders as amber pills; create = primary button "Use template" → new doc with placeholders filled (date auto). User section header "Your templates" with delete via long-press → confirm dialog (destructive).

## Z.5 Image alt-text editor (modal over editor)

Field focused on open (UX-38); helper "Describe this image (helps screen readers)"; Skip = secondary text button (never silent — dotted outline persists per §17.2); Save = primary. The editor also lists alt text from TalkBack (W.1 contract).

## Z.6 TOC insert sheet

Options: depth (H1 / H1–2 / H1–3 default), style (links on tap → scroll). Insert places TOC block at caret; empty-heading edge: TOC renders "Add headings to fill this table." state (DQ-8).
