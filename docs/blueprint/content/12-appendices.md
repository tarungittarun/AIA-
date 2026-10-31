@PART: PART XI — APPENDICES
@PARTDESC: Reference material an executor needs at arm's length: the complete test-case catalogue, worked calculator traces, the recurrence golden corpus, guide-coverage maps, microcopy dictionary, error catalogue, pack format, gesture map, runbooks, constraint register, fixture inventory and agent templates.

# Appendix A — Complete test-case catalogue

Machine-readable source of truth: `qa/testcases.csv` (generated from this table by `tools/traceability.py`; drift fails CI). Status column = latest full-lane result (populated from G3 onward). Binding = feature/UX ids.

## A.1 Calculator parity (ONE) and engine (CALC/LAW)

| Case | Binding | Verifies | Layer |
|---|---|---|---|
| TC-ONE-C-001…026 | §20.6 table | guide-parity set (26 cases) | L4/L5 |
| TC-LAW-001 | F-008 | L1 round-trip, 10k seeded cases | L1 |
| TC-LAW-002 | F-001/8 | L2 exact identity | L1 |
| TC-LAW-003 | F-008 | L3 rendering never invents 0.999… | L1 |
| TC-LAW-004 | F-003 | L4 percent consistency | L1 |
| TC-LAW-005 | F-002 | L5 implicit-mul AST equivalence | L1 |
| TC-LAW-006 | F-006 | L6 balance completeness | L1 |
| TC-LAW-007 | F-005 | L7 replacement determinism | L1 |
| TC-LAW-008 | F-008 | L8 continuation fidelity (1e15+1 class) | L1 |
| TC-LAW-009 | F-007 | L9 locale independence | L1 |
| TC-LAW-010 | F-024 | L10 history fidelity | L1 |
| TC-CALC-edge-001…020 | §7.2.8 register | edge inputs (20 rows) | L1/L2 |
| TC-CALC-frac-01 | F-030 | fraction rendering + fallback >999 denom | L1 |
| TC-CALC-deg-01 | F-009 | DEG/RAD toggle + persistence + INV arc | L4 |
| TC-CALC-perf-01 | §23.6 | keystroke→frame ≤ 16 ms p50 ≤ 64 chars | L1 bench |
| TC-PERF-key | §23.6 | 30 keys/s stress, no drops, no >24 ms frames | L4 |

## A.2 Calculator UX / state / system

| Case | Binding | Verifies | Layer |
|---|---|---|---|
| TC-STATE-calc-01 | F-043 | expression+caret+selection survive death | L4 |
| TC-STATE-calc-02 | UX-017 | rotation mid-selection | L4 |
| TC-SYS-theme-01 | F-035 | light/dark token resolution live | L3/L4 |
| TC-SYS-reduced-motion-01 | X8 | effects/motion removed under setting | L4 |
| TC-A11Y-calc-01 | §6.6 | TalkBack key announcements + caret context | L4 |
| TC-A11Y-contrast-01 | §6.6 | all 8 key themes × light/dark contrast programmatic | L1 |
| TC-ONE-haptics | F-029 | on/off honored | L4 |
| TC-ONE-clipclear | F-014/SEC-07 | clipboard 60 s auto-clear | L4 |

## A.3 Hub / search

| Case | Binding | Verifies | Layer |
|---|---|---|---|
| TC-HUB-001 | F-041 | grouped results across 4+ sources, deep links | L4 |
| TC-HUB-002 | F-042 | semantic merge + "related" tag (pack) | L4 |
| TC-HUB-003 | F-043 | continue-row exact restoration | L4 |
| TC-HUB-004 | F-044 | status lines freshness ≤ 1 s | L2 |
| TC-HUB-005 | F-046 | first-run cards exactly once | L4 |
| TC-HUB-006 | §5.5 | budgets: 25 ms/source, 120 ms paint @10k | L1 perf |
| TC-HUB-007 | §5.5 | FTS sanitization (operators as literals) | L2 |

## A.4 Notes

| Case | Binding | Verifies | Layer |
|---|---|---|---|
| TC-NOTE-rt | F-047/52 | NoteDoc↔Markdown lossless round-trip (200 corpus) | L1 |
| TC-NOTE-save-01 | F-047 | autosave 500 ms + death restore | L4 |
| TC-NOTE-fts-01 | F-048 | ranking + snippet + budget | L2 |
| TC-NOTE-trash-01 | F-050 | undo snackbar + 30-day sweep | L4 |
| TC-NOTE-check-01 | F-051 | toggles + progress card | L2 |
| TC-NOTE-edge-01…09 | §7.14 | register rows | L1/L2/L4 |
| TC-AI-note-01 | F-054 | summarize preview/undo/provenance | L4 |
| TC-AI-note-02 | F-054 | rewrite tones + schema retry/fallback | L2 |

## A.5 Scanner

| Case | Binding | Verifies | Layer |
|---|---|---|---|
| TC-SCAN-cap-01 | F-055 | batch capture + torch + focus | L4 |
| TC-SCAN-imp-01 | F-055 | import path with camera denied | L4 |
| TC-SCAN-crop-01 | F-056 | corner detect on fixtures ≥ 95% IoU | L1 |
| TC-SCAN-ocr-01 | F-057 | OCR char accuracy ≥ 92% fixture set | L4 |
| TC-SCAN-exp-01 | F-058 | PDF export + page order editor | L4 |
| TC-SCAN-abs-01 | F-059 | graceful absence UX | L4 |
| TC-SCAN-edge-01…07 | §7.14 | register rows | L1/L4 |

## A.6 Calendar

| Case | Binding | Verifies | Layer |
|---|---|---|---|
| TC-CAL-rr-01 | F-061 | golden corpus 200 rules exact occurrences | L1 |
| TC-CAL-dst-01 | F-061 | DST-crossing series (ADR-08) | L1 |
| TC-CAL-alarm-01 | F-062 | exact fire in policy window (E33/E35) | L4 |
| TC-CAL-alarm-02 | F-062 | inexact fallback + one-time notice | L4 |
| TC-CAL-ics-01 | F-063 | import subset + unsupported→one-off+note | L2 |
| TC-CAL-ics-02 | F-063 | export range re-import identity | L2 |
| TC-CAL-edge-01…06 | §7.14 | register rows | L1/L4 |

## A.7 Files / backup

| Case | Binding | Verifies | Layer |
|---|---|---|---|
| TC-FILE-browse-01 | F-065 | private+SAF ops incl. rename/move/search | L4 |
| TC-FILE-saf-01 | F-065 | revoked grant card + re-grant | L4 |
| TC-FILE-anlz-01 | F-066 | donut correctness on fixture tree + yields | L2 |
| TC-SEC-backup-01 | F-067 | round-trip restore identity | L4 |
| TC-SEC-backup-02 | F-067 | wrong passphrase: clean fail, no partial state | L4 |
| TC-SEC-backup-03 | §14.1 | traversal/bomb fixtures rejected | L2 |
| TC-FILE-trash-01 | F-068 | trash lifecycle + shred | L2 |
| TC-FILE-edge-01…05 | §7.14 | register rows | L2/L4 |

## A.8 Music / Recorder

| Case | Binding | Verifies | Layer |
|---|---|---|---|
| TC-MUSIC-imp-01 | F-069 | SAF/MediaStore import diff, no dupes | L4 |
| TC-MUSIC-play-01 | F-070 | queue/shuffle/repeat/speed/gapless | L4 |
| TC-MUSIC-foc-01 | F-070 | audio focus + headset route loss | L4 |
| TC-MUSIC-pl-01 | F-071 | playlist CRUD + M3U export/import | L2 |
| TC-MUSIC-mini-01 | F-072 | miniplayer persists across modules | L4 |
| TC-MUSIC-edge-01…06 | §7.14 | register rows | L2/L4 |
| TC-REC-svc-01 | F-073 | FGS ≤ 200 ms + notification actions | L4 |
| TC-REC-mark-01 | F-074 | markers insert/seek; pause rejects flags | L4 |
| TC-REC-fmt-01 | F-075 | AAC default + WAV option; files in Files | L2 |
| TC-AI-asr-01 | F-076 | fixture WER ≤ 12%; segments monotonic | L4 |
| TC-REC-note-01 | F-077 | → Notes linked note content | L4 |
| TC-REC-edge-01…06 | §7.14 | register rows | L1/L4 |

## A.9 Diagnostics / Settings / Security / System

| Case | Binding | Verifies | Layer |
|---|---|---|---|
| TC-DIAG-self-01 | F-079 | six-step script all green on clean build | L4 |
| TC-DIAG-log-01 | F-080 | ring caps + scrub + share preview | L2 |
| TC-PACK-mgr-01 | F-081 | import/enable/disable/delete lifecycle | L4 |
| TC-PACK-sec-01 | F-081/SC-06 | hash mismatch disables + card | L2 |
| TC-PACK-eval-01 | §16.8 | eval-kit thresholds met for pinned packs | L4 |
| TC-SET-lock-01 | F-082 | app lock threshold + credential fallback | L4 |
| TC-SET-about-01 | F-083 | provenance matches release bundle | L2 |
| TC-SET-lic-01 | F-084 | licenses regenerated, complete | L1 |
| TC-SEC-perm-full | F-034/SC-01 | full-app manifest allow-list exact | L1 |
| TC-SEC-perm-flavor | F-038 | flavor manifest zero permissions | L1 |
| TC-SEC-dex | SC-03 | no network-class symbols | L1 |
| TC-SEC-clip-01 | SC-07 | clipboard clear | L4 |
| TC-SEC-scrub-01 | SC-08 | PII scrubber battery | L1 |
| TC-SEC-lock-01 | SC-09 | app-lock round trip | L4 |
| TC-SYS-tokens | §6.7 | Kotlin tokens == tokens.csv | L1 |
| TC-ENV-01…16 | §3.5 | environment matrix rows | L4/L5 |
| TC-NAV-001 | UX-001 | two-tap traversal audit | L2 |
| TC-STATE-storm | J-06 | process death restoration | L4 |
| TC-STATE-mig-01 | §29.2 | migration fixture round trip | L2 |
| TC-STATE-bakdrift | §29.2 | newer backup rejected cleanly | L2 |

## A.10 Journeys (L4/L5)

J-01…J-10 as specified in §9.12, each with step tables in the harness YAML and per-step screenshots; J-09 pins flavor parity; J-10 uses the low-storage image.

# Appendix B — Worked calculator traces (normative examples)

Fixed prefix of every law-suite corpus (TC-LAW-*). "Path" = arithmetic route (§17.1.2). Internal value shown exactly (rational) or to 12 significant digits (inexact flag).

| # | Input | Tokens | Path | Internal value | Rendered |
|---|---|---|---|---|---|
| B-01 | `2+3×4` | 2 + 3 × 4 | exact | 14 | `14` |
| B-02 | `(2+3)×4` | ( 2 + 3 ) × 4 | exact | 20 | `20` |
| B-03 | `2(5+2)` | 2 ( 5 + 2 ) | exact (implicit ×) | 28 | `28` |
| B-04 | `(2)(3)` | ( 2 )( 3 ) | exact | 6 | `6` |
| B-05 | `200+10%` | 200 + 10 % | exact | 220 | `220` |
| B-06 | `200−10%` | 200 − 10 % | exact | 180 | `180` |
| B-07 | `200×10%` | 200 × 10 % | exact | 20 | `20` |
| B-08 | `200÷10%` | 200 ÷ 10 % | exact | 2000 | `2,000` |
| B-09 | `50%` | 50 % | exact | 1/2 | `0.5` |
| B-10 | `200+10%+10%` | 200 + 10% + 10% | exact | 242 | `242` |
| B-11 | `5+` `=` | 5 + ⇒ repeat | exact | 10 | `10` (owner bug class killed) |
| B-12 | `5+` `=` `=` | repeat chain | exact | 15 | `15` |
| B-13 | `10×−` | 10 × −(…) | exact | −10 | `-10` |
| B-14 | `2^3^2` | 2 ^ 3 ^ 2 | exact | 512 | `512` |
| B-15 | `(2+3` `=` | balance | exact | 25 | `25` |
| B-16 | `0.1+0.2` | exact rationals | exact | 3/10 | `0.3` |
| B-17 | `1÷3×3` | exact | exact | 1 | `1` (owner bug class killed) |
| B-18 | `1e15` then `+1` `=` | continuation uses internal exact | exact | 1000000000000001 | `1,000,000,000,000,001` (display may sci-format; continuation exact — owner bug class killed) |
| B-19 | `123456` | literal | exact | 123456 | `1,23,456` (en-IN) |
| B-20 | copy of B-19 result | clipboard | — | `123456` | raw digits, no commas |
| B-21 | `sin(90)` DEG | identity reduction | exact | 1 | `1` |
| B-22 | `cos(0)` | identity | exact | 1 | `1` |
| B-23 | `tan(90)` DEG | domain | — | — | `Error` card: undefined |
| B-24 | `asin(0.5)` DEG | exact-by-table (special angle) | exact | 30 | `30` |
| B-25 | `sin(π÷6)` RAD | inexact | inexact≈0.49999999999999994 → reduction | 1/2 by identity table | `0.5` |
| B-26 | `√2` | inexact | inexact | 1.414213562373… | `1.414213562` |
| B-27 | `ln(−1)` | domain | — | — | `Error` card: outside domain |
| B-28 | `5÷0` | domain | — | — | `Error` card: cannot divide by zero |
| B-29 | `2+3×(4+1` `=` | balance | exact | 25 | `25` |
| B-30 | `1/2π` | 1 ÷ 2 π implicit | exact | 1/2 π → inexact on π | `1.570796327` |

# Appendix C — Recurrence golden corpus (representative rows)

Full corpus: `core/domain/test/fixtures/rrules.json` (200 entries; these 24 are the pattern anchors). Each entry: rule, start (local), expected occurrence list (first 6), notes.

| # | Rule (relative to start) | Start | First occurrences | Note |
|---|---|---|---|---|
| C-01 | FREQ=DAILY | 01-Jan-26 | 01,02,03,04,05,06 Jan | base |
| C-02 | FREQ=DAILY;INTERVAL=3 | 01-Jan-26 | 01,04,07,10,13,16 | interval |
| C-03 | FREQ=DAILY;COUNT=4 | 15-Mar-26 | 15,16,17,18 Mar | count cap |
| C-04 | FREQ=DAILY;UNTIL=20260110 | 01-Jan-26 | 01..10 Jan | until inclusive |
| C-05 | FREQ=WEEKLY | Mon 05-Jan-26 | 05,12,19,26 Jan… | anchor weekday |
| C-06 | FREQ=WEEKLY;BYDAY=MO,WE,FR | 05-Jan-26 | 05,07,09,12,14,16 | multi-day |
| C-07 | FREQ=WEEKLY;INTERVAL=2;BYDAY=TU | 06-Jan-26 | 06,20 Jan,03 Feb | biweekly |
| C-08 | FREQ=MONTHLY | 31-Jan-26 | 31 Jan,31 Mar,31 May | 31st skips short months |
| C-09 | FREQ=MONTHLY (clamp setting) | 31-Jan-26 | 31 Jan,28 Feb,31 Mar | clamp variant |
| C-10 | FREQ=MONTHLY;BYMONTHDAY=-1 | 31-Jan-26 | 31 Jan,28 Feb,31 Mar | last-day |
| C-11 | FREQ=MONTHLY;BYMONTHDAY=15 | 15-Feb-26 | 15 Feb,15 Mar… | fixed day |
| C-12 | FREQ=YEARLY | 29-Feb-26* | (*2028 test year) 29 Feb,29 Feb | leap anchor |
| C-13 | FREQ=YEARLY;INTERVAL=2 | 10-Jun-26 | 10 Jun 26,28 | biennial |
| C-14 | FREQ=DAILY;EXDATE=20260103 | 01-Jan-26 | 01,02,04,05… | exdate |
| C-15 | FREQ=WEEKLY;BYDAY=MO;EXDATE 3 rows | 05-Jan-26 | skips listed Mondays | multi-exdate |
| C-16 | FREQ=MONTHLY;COUNT=12 over year boundary | 15-Aug-26 | …12 total | count over years |
| C-17 | DST spring gap US 2026-03-08 02:15 daily | 07-Mar-26 | 02:15 → 03:15 local post-gap | offset policy |
| C-18 | DST fall overlap 2026-11-01 01:30 daily | 31-Oct-26 | disambiguated to first instance | offset policy |
| C-19 | all-day weekly | 05-Jan-26 | dates only, no time shift | all-day + tz-free |
| C-20 | FREQ=DAILY in Kolkata tz over DST-irrelevant zone | 01-Jan-26 | fixed 09:00 IST | non-DST zone sanity |
| C-21 | BYDAY with INTERVAL misaligned anchor | 06-Jan-26 (Tue, interval 2) | 06,20 Jan | anchor=first occurrence |
| C-22 | UNTIL before start | 01-Jan-26; UNTIL=20251231 | empty series | empty legal |
| C-23 | COUNT=1 | 04-Jul-26 | 04 Jul only | single |
| C-24 | FREQ=YEARLY;BYMONTHDAY=29;BYMONTH=2 | 29-Feb-28 | leap years only | explicit leap |

# Appendix D — Owner-guide coverage map (B/C/D/E → requirements)

Each historical guide section maps to requirements and tests — this is how the blueprint guarantees the owner's past acceptance language is preserved, extended, and never silently dropped.

| Guide item | Intent | Requirement(s) | Test(s) |
|---|---|---|---|
| B1 hold `123456` → highlight + pill | selection entry | F-012 | TC-ONE-C-012 |
| B2 hold-then-slide resize | gesture | F-013 | TC-ONE-C-B2 (device-class) |
| B3 boundary handles | (old-guide) | superseded by B2 char-wise resize; documented in ledger D-002 | — |
| B4 copy/paste no commas | clipboard sanitize | F-014 | TC-ONE-C-018 |
| B5 cut + type into gap | edit flow | F-015 | TC-ONE-C-018 |
| B6 tap clears menu, places caret | selection exit | F-016 | TC-ONE-C-017 |
| B7 AC clears selection | staged clear | F-017 | TC-ONE-C-016 |
| B8 selection vs scroll | gesture priority | F-012 (detector spec §7.2.2) | TC-CALC-edge |
| B11 empty caret menu | insertion | F-018 | TC-ONE-C-019 |
| B12 MAdd/MUse mid-expression | memory | F-019/20 | TC-ONE-C-015 |
| C1 long expr + live answer | field | F-010 | TC-ONE-C-010 |
| C4 `10×−` unary | parser | F-005 | TC-ONE-C-005 |
| C5 `200+10%` | percent | F-003 | TC-ONE-C-003 |
| C6 `5+3×2=11`, auto-balance | engine | F-001/6 | TC-ONE-C-001/006 |
| C8 caret visible + autoscroll | field | F-011 | TC-ONE-C-011 |
| C9 no device keyboard | input mode | F-033 | TC-ONE-C-025 |
| D1 `2(5+2)=28` | parity | F-002 | TC-ONE-C-002 |
| D2 `10+` then `−` | operator replace | F-004 | TC-ONE-C-004 |
| D3 `5+` `=` → 10 | trailing-op | F-004 | TC-ONE-C-004 |
| D4 `1,23,456` grouping | rendering | F-007 | TC-ONE-C-007 |
| D6 INV sin degrees | functions | F-009 | TC-CALC-deg-01 |
| D8 backspace one char | edit | F-011 | TC-ONE-C-011 |
| D9 history replay paint-then-close | history | F-022 | TC-ONE-C-014 |
| D10 replay race guard | robustness | F-023 | TC-ONE-C-014 |
| E1 history newest-on-top | history | F-021 | TC-ONE-C-013 |
| E2 swipe-down opens history | entry points | F-021 | TC-ONE-C-013 (entry matrix) |
| E3 3-dot: five items + Effects | menu exactness | F-032/F-026 | TC-ONE-C-022/020 |
| E4 effects ≥ 4 styles | effects | F-031 | TC-ONE-C-024 |
| H1–H4 themes/caret | theming | F-035/F-027 | TC-SYS-theme-01/TC-ONE-C-023 |
| F MyCalc zero permissions | flavor | F-036…040 | TC-SEC-perm-flavor/J-09 |

<!-- pagebreak -->
