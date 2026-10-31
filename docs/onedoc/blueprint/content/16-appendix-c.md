# Appendix C — Test catalogue (case tables, part 2)

## Templates (TPL)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-TPL-001 | F-045 | 12 built-ins listed, each instantiates valid doc | L2/L4 |
| TC-TPL-002 | F-046 | preview renders read-only, placeholders marked | L4 |
| TC-TPL-003 | F-047 | instantiate copies; template file unmutated | L2 |
| TC-TPL-004 | F-048 | placeholder fill incl. locale-aware date | L2/L4 |
| TC-TPL-005 | F-049 | save-as-template round-trip | L2/L4 |
| TC-TPL-006 | F-050 | user section delete; gallery states | L4 |

## Files & formats (IO)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-IO-001 | F-051, UX-49 | PDF export: fonts, selection text, pagination, count ±1%, < 10 s | L4 |
| TC-IO-002 | F-052 | odoc lossless round-trip incl. assets | L1/L4 |
| TC-IO-003 | F-053 | md/txt/html exports at declared fidelity | L1/L4 |
| TC-IO-004 | F-054 | docx export valid per OOXML subset; re-import parity | L1/L4 |
| TC-IO-005 | F-055, UX-45 | imports with correct fidelity + conversion notes | L2/L4 |
| TC-IO-006 | F-056, UX-15 | unsupported refused with reason; no empty doc | L2/L4 |
| TC-IO-007 | F-057 | share sheet hands FileProvider URI, cache cleaned | L4 |
| TC-IO-008 | F-058 | open-in for odoc/md/txt/html from file manager | L4 |
| TC-IO-009 | F-059 | SAF create/open flows | L4 |
| TC-IO-010 | F-060 | backup zip encrypted, manifest SHAs correct | L2/L4 |
| TC-IO-011 | UX-18 | SAF denial mid-export: no partial file + reason | L4 |
| TC-IO-012 | F-057, F-058 | share→receive→import→export parity loop | L4 |
| TC-IO-013 | F-060 | backup→wipe→restore byte-identical at F3 | L4 |

## Search (SRCH)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-SRCH-001 | F-067, UX-08 | FTS speed + snippets + counts on corpus | L2/L4 |
| TC-SRCH-002 | F-068 | deep-link opens hit block highlighted | L4 |
| TC-SRCH-003 | F-069 | shared highlight with find bar | L2 |
| TC-SRCH-004 | F-070 | semantic "related" merge labeled; absent without pack | L4 |
| TC-SRCH-005 | F-067 | indexing 10k words < 150 ms background | L2 |

## Scan & OCR (SCAN / AI)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-SCAN-001 | F-071, UX-09 | capture→crop→OCR→review→insert ≤ 60 s/page | L4 |
| TC-SCAN-002 | F-072 | multi-page queue, reorder, batch OCR | L4 |
| TC-AI-001 | F-071, UX-41, UX-46 | fixture accuracy ≥ 95%; confidence marks color+style | L4 |
| TC-AI-002 | F-073 | no pack: flow ends at save-image with reason | L4 |
| TC-AI-003 | F-074, UX-10 | dictation partials ≤ 1.5 s; explicit insert | L4 |
| TC-AI-004 | F-075, UX-47 | four verbs produce labeled preview cards | L4 |
| TC-AI-005 | F-076 | gemma on Tier A; extractive rung on Tier B labeled | L4 |
| TC-AI-006 | F-077, UX-29 | streaming, cancel, pre-edit snapshot, single undo | L2/L4 |
| TC-AI-007 | F-080 | TTS play/pause/stop + sentence highlight | L4 |
| TC-AI-008 | F-081 | range start at cursor; system rate honored | L4 |
| TC-AI-009 | F-082, UX-30 | controls hidden with reason per tier/pack/ram | L4 |
| TC-AI-010 | §19.5 | prompt fixtures: runtime invariance + faithfulness rubric | L1 |

## Packs (AI-PACK / SEC-PK)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-AI-PACK-01 | F-078, UX-48 | install flow: SHA shown, verify, capability appears | L2/L4 |
| TC-AI-PACK-02 | F-079, UX-48 | corrupt/wrong-SHA refused, both hashes shown, ladder descent | L2/L4 |

## Reading & a11y (READ / A11Y)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-READ-001 | F-083, F-080 | reader mode + TTS entry from reader | L4 |
| TC-A11Y-001 | F-084, UX-37 | TalkBack-complete letter: create/edit/format/export | L4 |
| TC-A11Y-002 | F-085, UX-40 | contrast across 8 themes | G (snapshot) |
| TC-A11Y-003 | F-086, UX-39 | 200% scale, no clipping, all screens | L4 |

## Settings & diagnostics (SET / DIAG)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-SET-001 | F-087, UX-40 | 8 themes + match-system; accent choices | L4 |
| TC-SET-002 | F-088 | editor settings apply + persist | L2/L4 |
| TC-SET-003 | F-089, UX-34 | about/diagnostics facts; self-test ≤ 20 s offline | L4 |
| TC-SET-004 | F-090, UX-43 | locale strings + RTL mirroring | L4 |
| TC-DIAG-001 | F-089 | diagnostics ring buffer, no PII, never written out | L2 |

## Security (SEC)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-SEC-P-01 | C1 | merged manifest permission set == §20.5 exactly | G |
| TC-SEC-P-02 | UX-31 | no notifications except user-created/progress | L4 |
| TC-SEC-P-03 | UX-50, C5 | network silence: zero sockets across all flows on release APK | L4 |
| TC-SEC-P-04 | §20.4 | clipboard read only on paste; no background reads | L4 |
| TC-SEC-IO-01 | §20.4 | hostile HTML/scripts stripped structurally | L1/L4 |
| TC-SEC-IO-02 | F-057 | FileProvider grants scoped; cache cleaned | L4 |
| TC-SEC-ST-01 | §20.3 | encryption-at-rest smoke with keystore | L4 |
| TC-SEC-ST-02 | §20.3 | export temp lifecycle (created granted, deleted) | L4 |
| TC-SEC-PK-01 | §20.4 | tampered pack zip refused (hash mismatch) | L1/L4 |
| TC-SEC-PK-02 | §20.4 | path-traversal pack entry names refused | L1/L4 |

The SEC suite is deliberately small and absolute: each case is a structural proof, not a scan. P-cases run on the release APK every RC; IO/PK cases run in JVM plus on-APK variants; a security suite red blocks the gate regardless of every other green (§20.6).

## UX platform cases (UX-TC)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-UX-001 | UX-01, UX-02 | FAB→editor speed and directness | L4 |
| TC-UX-002 | UX-03 | export ≤ 3 taps | L4 |
| TC-UX-003 | UX-04 | import ≤ 2 taps via share/open-in | L4 |
| TC-UX-004 | UX-05 | find bar memory + clean dismiss | L4 |
| TC-UX-005 | UX-06 | composite insert single undo | L2 |
| TC-UX-006 | UX-19, UX-20 | toolbar placement + target sizes | L4 |
| TC-UX-007 | UX-25 | IME anchor scrolling | L4 |
| TC-UX-008 | UX-32 | first-launch card; permission timing | L4 |
| TC-UX-009 | UX-35 | destructive-action haptic + confirm/undo | L4 |
| TC-UX-010 | UX-42 | reachability: primary actions bottom 40% | G (layout audit) |
| TC-UX-011 | UX-44 | reduced-motion honored | L4 |

## Performance & environments (PERF / ENV)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-PERF-001 | F-012, UX-02 | cold start < 1.2 s, 200 docs, API 33 | L4 |
| TC-PERF-002 | F-029, UX-26 | typing P95 < 50 ms; no burst jank | L4 |
| TC-ENV-001 | C6 | API 26 smoke: full P0 subset | L4 |
| TC-ENV-002 | C6 | API 36 smoke incl. Tier A AI | L4 |
| TC-ENV-003 | C6 | tablet/landscape layout sweep | L4 |
| TC-ENV-004 | C1 | airplane-mode full journey pass | L4 |

## Journeys (J)

| Case | Binding | Proves | Level |
|---|---|---|---|
| TC-J1 | §27.1 | letter journey end-to-end on APK | L4 |
| TC-J2 | §27.2 | scan journey (+ -degraded variant, no pack) | L4 |
| TC-J3 | §27.3 | dictate→tidy→docx journey (+ -llm variant Tier A) | L4 |
| TC-J4 | §27.4 | search journey (+ -semantic variant with pack) | L4 |
| TC-J5 | §27.5 | deletion-recovery journey incl. version restore | L4 |

## Journey variant matrix

Variants are procedure alternates of their base case (§24.5) — one manifest row, several runs:

| Variant | Base | Difference | Runs when |
|---|---|---|---|
| TC-J2-degraded | TC-J2 | no OCR pack; flow ends at save-image with reason (F-073) | G6 matrix on API 33 without packs |
| TC-J3-llm | TC-J3 | gemma rung on Tier A; method label asserted | API 36 with llm pack |
| TC-J4-semantic | TC-J4 | "related" section asserted with embed pack | API 33/36 with embed pack |
| TC-EDIT-004-draglong | TC-EDIT-004 | hold-then-drag via UiAutomation injection (O.4) | nightly API 33 |
