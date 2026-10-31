# Appendix J — Fixture corpus

## J.1 Documents (seed + test fixtures, `tools/onedoc/testdata/corpus/`)

| Fixture | Purpose | Used by |
|---|---|---|
| `empty.odoc` | zero blocks; first-run edge | LIB, EDIT |
| `letter-1p.odoc` | 180-word letter, marks + H1 | J1, IO goldens |
| `report-50p.odoc` | 50 pages, H1–H3, 3 tables, 4 images, TOC, footnotes | STRUCT-004, IO-001, STATE-004 |
| `walls-20k.odoc` | single 20k-char paragraph block | renderer guard §14.7, PERF |
| `unicode-planfeast.odoc` | emoji planes 0/1/2/14, Devanagari, CJK, RTL runs | EDIT-017, IME-03, P10 |
| `tables-heavy.odoc` | 12 tables incl. 1×1 and 20-col | TBL, P6 |
| `marks-kitchen.odoc` | every mark type, overlapping boundary cases | EDIT-005, P2 |
| `lists-deep.odoc` | bullet/number/check nests, 1–5 levels | EDIT-007 |
| `seed-library-200/` | 200 synthetic docs (titles+1–5k words each) | PERF-001, SRCH-001 |
| `manual-appliances.odoc` | 6-page manual; "warranty" once oblique ("the manufacturer undertakes repairs for 24 months") | J4 |
| `future-kind.odoc` | hand-crafted block kind `widget_v9` | LAW-004 round-trip |
| `legacy-v1.odoc` | schema v1 synthetic | STATE-007 migrations |

## J.2 Images and audio

- `scan/page-0[1-3].jpg` — 300 dpi printed-letter photos with perspective skew (OCR fixtures, accuracy bar TC-AI-001).
- `scan/whiteboard-01.jpg` — low-contrast handwriting (confidence-marking demo, UX-46).
- `images/exif-gps.jpg` — GPS-tagged test image (proves EXIF strip, TC-IMG-001).
- `audio/minutes-en-60s.wav` — 60 s meeting speech, 2 speakers (dictation fixture, TC-AI-003).
- `audio/hi-sample-30s.wav` — Hindi sample (locale path, TC-SET-004 co-verification).

Fixtures are committed to the repo (they are small, synthetic, license-clean) so every run of every cycle is reproducible byte-for-byte — the same discipline Law L6 demands of exports.

# Appendix K — Glossary (owner-friendly)

| Term | Meaning |
|---|---|
| Block | One structural unit of a document: paragraph, heading, list, table, image… |
| Mark | Inline formatting on a text range: bold, italic, link… |
| Op | The smallest change the engine can apply/undo (typed char, split, mark toggle) |
| Journal | Append-only log that makes zero-keystroke-loss possible (L3) |
| Snapshot / Version | A saved copy of a document at a point in time (auto/manual/pre-edit) |
| Fidelity (F0–F3) | Honesty level of a file conversion: refused / best-effort / subset-lossless / lossless |
| Pack (.odpack) | A side-loaded, SHA-verified zip containing an AI model — never downloaded by the app |
| Ladder | The ordered fallback: best model → lighter model → system service → hidden with reason |
| Tier A/B/C | Device classes by RAM: 8+ / 4–8 / <4 GB — decide which AI runs |
| Law (L1–L10) | A release-blocking editor behavior with a dedicated proof |
| Gate (G0–G8) | A phase boundary that closes only with checked DoD evidence |
| Direct-APK QA | Tests that install the real release APK on an emulator and drive it — the only proof that counts for shipping |
| BLOCKED | "Could not test fairly" — never counted as pass or failure; logged with reason and retried |
| Evidence PDF | The owner's report: every claim traced to a case id with screenshots and provenance |
| D-nnn / S-nnn | Decision ledger / session log entries (append-only) |

# Appendix L — Risk register (full)

| # | Risk | P | Impact | Mitigation | Trigger → response |
|---|---|---|---|---|---|
| R1 | IME diversity breaks composition invariants | M | S1-class (text loss) | fuzzer + scripts per keyboard (§15) | any fuzzer red → feature freeze, IME-only gate |
| R2 | LLM too heavy for claimed Tier A floor | M | capability demotion | tier gate + budget timings (§19.8) | 2× latency miss → raise tier floor, D-nnn |
| R3 | Pagination guide/PDF drift | M | trust (WYSIWYG claim) | single metrics engine (§17.4) | ±1 line breach → font-fallback freeze + fix |
| R4 | APK size creep | H | budget breach, cheap-phone exclusion | per-PR size gate (§22.4) | +0.5 MB PR → shrink pass first |
| R5 | Figma/registry drift | M | UI inconsistency | DQ-3 + nightly drift check | drift found → re-sync task before UI merges |
| R6 | DOCX import surprises (real-world files) | H | fidelity trust | refusal+notes posture (§18.1), corpus tests | new malformed class → parser fix + corpus case |
| R7 | Property suite runtime bloat slows PRs | M | dev velocity | shard nightly; PR = 5k cases | PR pipeline > 15 min → move suites to nightly+merge |
| R8 | Emulator flakiness pollutes verdicts | H | wasted cycles, mistrust | boot snapshots, quarantine rules (§24.3) | flaky-twice → quarantine with defect id |
| R9 | Owner keystore delayed at G8 | M | release slip | RC keystore path defined (§26.1) | delay → ship RC-signed artifact + re-sign runbook |
| R10 | Scope pressure ("just one network feature") | L | promise break | §1.4 list + C1 gate | any proposal → invalid by charter; D-nnn refuses |

# Appendix M — Release-notes template (voice contract)

```
OneDoc v<X.Y.Z> (<versionCode>) — build <sha7>

New
- <feature>: <one line, user language>

Improved
- <improvement>: <one line>

Fixed
- <OD-xxx> <one line>

Honest notes
- <fidelity/BLOCKED/limit lines — no "known issues" framing of anything S1/S2 (they cannot exist at G8)>

Verify
- APK SHA-256: <hash>
- Evidence: <reports link> · Provenance: releases/<ver>/provenance.json
```

Rules: ≤ 200 words; no marketing adjectives; every Fixed line cites a tracker id; Honest notes are mandatory even when empty ("None — see evidence PDF.").
