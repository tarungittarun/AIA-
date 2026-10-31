@PART: PART VI — DETAILED TECHNICAL SPECIFICATION
@PARTDESC: The single source of truth for behavior-level engineering: the calculator language with its exact grammar and laws, history and memory contracts, the note document format, recurrence rules, the recorder service, file handling, and every settings key. When Chapter 9 says what, this chapter says exactly how it must behave.

# Chapter 17 — Detailed specifications

## 17.1 The calculator language

### 17.1.1 Lexical structure

Characters: digits `0-9`, `.` (decimal point; locale comma input is accepted and normalized), operators `+ − × ÷ ^`, brackets `( )`, `%`, constants `π e`, function names `sin cos tan ln log` and inverse/`√`/`!` via pad, and `⌫ AC` as commands (not tokens). Unicode minus `−` and multiplication sign `×` are first-class; ASCII `- * /` are accepted on paste and normalized. Numbers: one dot max; digits beyond 15 significant are preserved in token form but evaluated in Decimal context (§17.1.2). Max expression length 512 chars (enforced at input).

### 17.1.2 Number model — exactness ladder

1. **Rational path** (default for `+ − × ÷` and integer `^`): every operand that originates from a literal, or from `+ − × ÷` over exact values, is a `BigRational` (numerator/denominator as BigInteger). `0.1+0.2` → `3/10` → displays `0.3`. `1÷3×3` → `1` exactly (the owner's documented `0.9999999999` bug class cannot exist on this path).
2. **Transcendental path** (`sin cos tan ln log √ non-integer-^ π e`): operands convert to `BigDecimal(34 significant digits, HALF_EVEN)`; results carry an `inexact` flag. `sin(π)` is handled by identity reduction (`π` argument → 0 exactly) so the classic `3e-17` artifact cannot appear.
3. **Rendering**: exact values render from the rational (up to 15 decimal places, trailing zeros trimmed; denominator powers of 2·5 only — otherwise longest-repeating detection shows up to 10 places with ellipsis option). Inexact values render to 10 significant digits by default (`show as fraction` renders rationals as `a/b`, F-030). The famous failure `0.9999999999` is structurally impossible because display never re-parses a rounded string; it renders the underlying exact/inexact value.
4. **Overflow/domain**: `÷0` → `Error` card "Cannot divide by zero"; `ln(−1)` etc. → `Error` card with the domain reason; factorial of non-neg integers > 169 → `Error` (result beyond display); exponent overflow → scientific rendering `1.234567891e+15` *with the exact value retained internally* so continued computation does not lose precision (the display-string-reuse bug of `1e+15+1 → Error` is prohibited: continuation always uses the internal exact value, F-008 note).

### 17.1.3 Canonical input form

The stored/compared form of any expression (history, clipboard-on-copy, logs) is canonical ASCII: `2+3*(4+1)`. The UI renders pretty glyphs (× − ÷ π) from tokens; copy/history/export use canonical form with one exception — copy of a *number* copies the display digits without grouping (F-007/F-014).

### 17.1.4 Grammar and parsing (EBNF)

```ebnf
expr    := term { ("+" | "-") term };
term    := power { ("*" | "/") power };
power   := unary [ "^" power ];            (* right associative *)
unary   := "-" unary | postfix;
postfix := primary [ "!" | "%" ];          (* postfix % §17.1.5 *)
primary := NUMBER | CONST | FUNC "(" expr ")" | "(" expr ")" | primary "(" expr ")";  (* implicit × *)
```

- **Implicit multiplication** (F-002) arises when a `primary` is followed by `(`, a constant, or a function: `2(5+2)`, `(2)(3)`, `2π`. The parser inserts a `MUL` node with the same precedence as `×` (left-assoc): `2(5+2)=28`, `1/2π` = `(1/2)π` = `0.5π` — matching Google Calculator's documented behavior.
- **Percent as postfix** (F-003): parsed as `Percent(expr)`; semantics in §17.1.5.
- **Auto-balance** (F-006): the `=` key appends missing `)` before evaluation; display shows the balance preview via live answer; the `( )` smart key inserts `()` pair when the parser expects a primary, else inserts `)`.
- **Operator replacement** (guide C4/F-005): typing an operator when the caret follows an operator replaces it (except unary `−` after `(`, `×`, or start: `10×−` legal); typing `+` right after `−`-as-unary is a replace.
- **Errors** surface as typed results: `SyntaxErr` (with caret position hint in the error card), `DomainErr`, `DivZero`, `TooLong`, `TooBig`.

### 17.1.5 Operator semantics — normative table

| Input | Result | Rule |
|---|---|---|
| `200+10%` | `220` | percent = 10% of 200 (context: additive) |
| `200−10%` | `180` | subtract 10% of 200 |
| `200×10%` | `20` | percent = plain ×0.1 |
| `200÷10%` | `2000` | divide by 0.1 |
| `50%` | `0.5` | standalone: value/100 |
| `200+10%+10%` | `242` | each percent of the accumulated left value |
| `5+` then `=` | `10` | **trailing-operator rule**: equals with a dangling operator repeats the left operand as the right (`5+5`) — Google parity F-004 |
| `5+` then `=` then `=` | `15` | repeat semantics chain (each equals adds 5 again) |
| `10×−` | `-10` (on `=`) | unary minus folds into power/term per EBNF |
| `2^3^2` | `512` | right-associative power |
| `(2+3` `=` | `25` | auto-balance |

### 17.1.6 Functions and constants

`sin cos tan` + INV (`asin acos atan`), `ln log` (natural, base-10), `√`, `^`, `!` (integer factorial, `0! = 1`), constants `π`, `e`. Angle mode: degree default with a `DEG/RAD` toggle on the scientific pad (persisted; INV sin in degree mode returns degrees — the owner's guide D6 case `Inv sin 0.5 → 30°`). Accuracy contract: transcendental results within 1 ulp of 34-digit computation; live-answer latency budget ≤ 1 ms for ≤ 64-char expressions on Tier B (measured by `CalcEngineBenchmark` in CI, §23.6).

### 17.1.7 The laws (property-based test suite)

The engine must satisfy all laws below over randomized expression corpora (≥ 10 000 cases per law in CI; seeds recorded in test output):

| Law | Statement |
|---|---|
| L1 Round-trip | `format(evaluate(s))` re-parses and re-evaluates to the same value for all renderable outputs |
| L2 Exact identity | `(a+b)−b = a` exactly on the rational path (no epsilon) |
| L3 Distribute-display | `0.1+0.2` renders `0.3`; `1/3*3` renders `1` (rendering never invents `0.999…`) |
| L4 Percent consistency | `x+p% ≡ x+(x*p/100)`; `x*p% ≡ x*p/100` for all sampled x,p |
| L5 Implicit equivalence | `2(5+2) ≡ 2*(5+2)` AST-equal after implicit-mul insertion |
| L6 Balance completeness | any prefix-valid expression with open brackets evaluates identically to its balanced form |
| L7 Replace determinism | the operator-replacement state machine is a pure function of (current token, typed token) |
| L8 Continuation fidelity | after `=`, operating on the displayed result equals operating on the internal exact value |
| L9 Locale independence | evaluation is identical across en-IN/en-US/de-DE inputs modulo punctuation normalization |
| L10 History fidelity | stored canonical expression re-evaluates to the stored exact result |

### 17.1.8 Rendering and grouping

Grouping: Indian style `1,23,456` for `en-IN`, western `123,456` otherwise; applied to the integer part only; never inside fraction display; never in canonical form. Decimal separator follows locale for display; input accepts both. Very large/small magnitudes switch to scientific display at ≥ 1e15 or < 1e−9 (display-only; §17.1.2 continuation rule).

## 17.2 History and memory contracts

- **History row** written on every successful `=` (and on `Error` — errors are history too, Google parity), fields per §12.2; write is synchronous with result display (≤ 16 ms, same frame).
- **Replay**: card tap → expression painted into the field (with caret at end) → sheet closes after paint (≥ 1 frame later) → double-tap race guard (debounce 350 ms) (F-022/F-023).
- **Persistence across restart** (F-024): tested by TC-ONE-C-013 — insert 5 entries, kill process (`adb shell am kill` + force-stop), relaunch, assert all 5 + exact order.
- **Memory slots**: slot 1 is the MAdd target; overflow menu `Memory` opens the sheet; `M+`/`M−`-style accumulation is *not* a separate key (not in the pad) — accumulation happens by repeated MAdd into the same slot? No: MAdd **adds** the selected value into slot 1 (guide semantics: `MAdd stored 123456`); `MC` clears the selected slot; up/down moves reorder (F-026). Values stored as exact strings; MUse inserts/replaces verbatim.

## 17.3 Notes document format (`NoteDoc`)

```json
{"v":1,
 "blocks":[
  {"t":"h","lvl":1,"runs":[{"x":"Field survey"}]},
  {"t":"p","runs":[{"x":"Plain "},{"x":"bold","b":true},{"x":" text"}]},
  {"t":"check","items":[{"x":"Milk","c":true},{"x":"Rice","c":true},{"x":"Turmeric","c":false}]},
  {"t":"bullet","items":[{"x":"First"}]},
  {"t":"div"}]}
```

Rules: unknown block types on import are preserved verbatim under `{"t":"raw"}` and rendered as plain text (forward compatibility); export to Markdown maps h→`#`, p→text, check→`- [x]`, bullet→`-`, div→`---`, bold `**`, italic `*`; import reverse-maps (lossless round-trip property TC-NOTE-rt over the fixture corpus). `plainText` projection concatenates run text with `\n` per block. Title = first h/first line, max 80 display chars.

## 17.4 Recurrence (supported RRULE subset)

```
FREQ = DAILY | WEEKLY | MONTHLY | YEARLY
INTERVAL = 1..999          BYDAY = MO,TU,WE,TH,FR,SA,SU (WEEKLY; multi-value allowed)
BYMONTHDAY = 1..31,-1 (MONTHLY)   COUNT = 1..9999   UNTIL = date
EXDATE = comma list of dates (stored separately)
```

- Weekly with BYDAY: occurrences on listed weekdays at INTERVAL-week steps anchored on `startUtc` local date.
- Monthly BYMONTHDAY: day exists in month else skipped (setting: `clamp to last day` alternative); `−1` = last day.
- Yearly: same month/day; Feb 29 skipped in non-leap years (setting: `Mar 1 alternative`).
- Expansion: lazily generated per visible window (month grid) + next-occurrence index for reminders; generation is pure and unit-golden-tested (§13.4).
- ICS mapping: exported RRULE strings limited to this subset; import of unsupported RRULE (e.g., BYSETPOS) → single occurrence on DTSTART + `note` suffix "recurrence simplified from ICS" (F-063).

## 17.5 Recorder service

- Lifecycle: `startForeground` within 200 ms of record tap (API 26+ `startForegroundService` contract); type `microphone`; notification actions Pause/Resume/Stop; process-death of the *activity* never stops recording; device reboot stops it (documented; no auto-resume).
- Audio: 48 kHz mono PCM 16-bit → AAC-LC 96 kbps (`MediaCodec`+`MediaMuxer`, `.m4a`); WAV alternative 48 kHz 16-bit PCM. Files: `Recordings/REC-yyyyMMdd-HHmmss.ext` + DB row.
- Pause: encoder stops, muxer kept open, `PresentationTimeUs` frozen (resumed timeline continuous); markers during pause are rejected.
- Marker: DB insert with `offsetMs = currentTimelinePosition`; max 200/recording; labels ≤ 40 chars.
- Failure: storage-full mid-record → finalize file gracefully, mark row `incomplete`, user toast with path (no data loss of already-written frames); mic loss (unplug) → auto-pause with notification update.
- Transcription (pack): segments = `{startMs,endMs,text}` list stored in `transcriptSegmentsJson`; searchable via `plainText` mirror; provenance block (model id, pack version, language guess, WER n/a) stored in DB `transcript` header line (§16.3).

## 17.6 Files handling rules

- SAF duplicate-name policy: numeric suffix `name (2).ext`; private-repo same. Case-insensitive collision check on FAT-style roots.
- Move across SAF roots = copy+delete with progress; cancellation leaves source intact (copy first, delete after verify).
- Trash: private files move to `.trash/` with restore manifest; SAF deletes are immediate (OS limitation, disclosed in UI confirm text, §13.6).
- Analyzer cache: sizes cached per directory with mtime/children-count invalidation; deep walks yield every 200 ms (jank budget §23.6).
- Backup/restore per §12.4/§14.1 (zip guards, transactional restore).

## 17.7 Settings key registry (normative)

| Key | Type | Default | Values / notes |
|---|---|---|---|
| `calc.haptics` | bool | true | key + selection haptics |
| `calc.fraction` | bool | false | show rationals as a/b |
| `calc.keyTheme` | enum | `mySpaceSettings` | mySpaceSettings, graphite, ocean, sunset, mint, rose, lemon, iris |
| `calc.keyShape` | enum | `roundedSquare` | circle, squircle, pill, roundedSquare, none |
| `calc.effects` | enum | `none` | none, bubbles, ripple, confetti |
| `calc.angleMode` | enum | `deg` | deg, rad |
| `calc.clipboardClearSec` | int | 60 | 0 disables |
| `app.theme` | enum | `system` | system, light, dark |
| `app.dynamicColor` | bool | true (A12+) | Material You |
| `app.lockEnabled` | bool | false | biometric+credential |
| `cal.defaultReminderMin` | int | 15 | −1 = none |
| `cal.exactAlarmFallbackNoticed` | bool | false | one-time notice flag |
| `rec.format` | enum | `aac` | aac, wav |
| `music.speed` | float | 1.0 | 0.5..3.0 |
| `files.sort` | enum | `name` | name, date, size, type |
| `ai.packs.<id>.enabled` | bool | true (when installed) | registry mirror |
| `hub.firstRunCardsDone` | bool | false | privacy card once |

Registry is a single Kotlin object with typed accessors; Settings UI is generated from it in tests (a missing row = TC-SET-* failure), preventing key drift.

## 17.8 Diagnostics self-test script (normative steps)

1. Engine: 100 seeded law-smoke cases (L1–L5) → pass/fail counts.
2. DB: `PRAGMA quick_check` + insert/read of one row per table in a transaction (rolled back).
3. Packs: re-hash each installed pack file vs registry.
4. Alarms: `AlarmManager.canScheduleExactAlarms()` report.
5. Notifications: channel existence + importance.
6. Storage: free bytes; warn < 500 MB.
Output: JSON + rendered card; nothing leaves the device unless the user shares it (F-080/F-081).

## 17.9 Fraction rendering rule (exact path)

When `calc.fraction` is ON: rationals with denominator ≤ 999 render as `a/b` (mixed form `3 1/2` when |a|>b, with thin-space grouping); denominators > 999 fall back to decimal (10 sig digits); inexact-path values never render as fractions (no fake precision). The `=` result and live answer both honor the setting; history stores canonical form regardless (rendering setting is display-only).

## 17.10 Worked evaluation traces (normative examples)

Traces for 30 expressions — including every row of §17.1.5 and the owner's historical failure cases (`5+ =`, `1÷3×3`, `1e15+1`, `0.1+0.2`) — are tabulated in **Appendix B** with token stream, path (exact/inexact), internal value, and rendered output. The law-suite corpus generator must include every Appendix B row as a fixed prefix so regressions on historical bugs are impossible to miss.

## 17.11 Notification text templates (normative)

| Notification | Title | Body | Actions |
|---|---|---|---|
| Reminder | `<event title>` | `<time> · <note-or-empty>` | Open |
| Recording | `Recording — MySpace One` | `<duration> · tap to return` | Pause / Stop |
| Paused recording | `Recording paused` | `<duration> so far` | Resume / Stop |
| Playback (media style) | `<title>` | `<artist> · <album>` | Prev / Play-pause / Next |
| Self-test failure (user-ran) | `Self-test found a problem` | `<n> of 6 checks failed` | Open Diagnostics |

Wording rules: no exclamation marks, no emoji, no "please"; numbers humanized (`1 hr 12 min`).

## 17.12 Per-module settings keys (registry extension)

| Module | Key | Type | Default |
|---|---|---|---|
| Notes | `notes.sort` | enum | edited |
| Notes | `notes.view` | enum | list |
| Notes | `notes.confirmTrash` | bool | false |
| Scanner | `scan.defaultFilter` | enum | original |
| Scanner | `scan.autoOcr` | bool | true (pack on) |
| Calendar | `cal.weekStart` | enum | locale |
| Calendar | `cal.monthlyOverflow` | enum | skip |
| Calendar | `cal.sound` | enum | system |
| Files | `files.showHidden` | bool | false |
| Files | `files.sortDir` | enum | asc |
| Music | `music.repeat` | enum | off |
| Music | `music.shuffle` | bool | false |
| Music | `music.crossfadeSec` | int | 0 |
| Recorder | `rec.markerHaptic` | bool | true |
| Recorder | `rec.keepScreenOn` | bool | true |
| Diagnostics | `diag.ringDays` | int | 7 |
| Hub | `hub.searchRecents` | bool | true |
| Global | `app.pureBlackDark` | bool | false (A10+) |

Rules: keys are never read from raw strings in feature code (registry accessors only — TC-SET-registry reflects); removals migrate per §29.6.

## 17.13 Worked parse trees (executor calibration)

`2(5+2)` →

```
BIN(+, BIN(×, NUM(2), GROUP(BIN(+, NUM(5), NUM(2)))))   # implicit × inserted, left-assoc
```

`200+10%+10%` →

```
BIN(+, BIN(+, NUM(200), PCT(NUM(10), ctx=ADD, lhs=200)),
        PCT(NUM(10), ctx=ADD, lhs=220))                  # lhs accumulates → 242
```

`10×−3^2` →

```
BIN(×, NUM(10), NEG(BIN(^, NUM(3), NUM(2))))             # unary binds under ^: −9 ×10 → −90
```

Property test oracles compare against these trees structurally (AST equality after implicit-mul insertion, law L5).

## 17.14 Rendering edge table (display rules digest)

| Case | Rule | Output |
|---|---|---|
| 15+ digits integer | group by locale, no exponent | `12,34,56,78,90,12,345` |
| ≥ 1e15 magnitude | sci display, exact kept | `1.000000001e+15` |
| ≤ 1e−9 magnitude | sci display | `3.333333333e−10` |
| repeating decimal | 10 places then `…` (fraction setting offers `a/b`) | `0.3333333333…` |
| exact half | shortest form | `2.5` |
| negative zero | normalized | `0` |
| `+0.5` leading ops | leading `+` dropped, `−` kept | `−0.5` |

## 17.15 Additional worked cases (Appendix B extension, B-31…B-45)

| # | Input | Path | Rendered |
|---|---|---|---|
| B-31 | `0.5+0.25` | exact | `0.75` |
| B-32 | `1÷3+1÷6` | exact | `0.5` |
| B-33 | `(1÷3)×3+0.2` | exact | `1.2` |
| B-34 | `2^0.5` | inexact | `1.414213562` |
| B-35 | `8^1÷3` | exact-fold | `2` (`8^(1/3)` rational exactness note: cube-root identity table) |
| B-36 | `10!÷8!` | exact | `90` |
| B-37 | `√(−4)` | domain | error card |
| B-38 | `log(0)` | domain | error card |
| B-39 | `e^0` | exact | `1` |
| B-40 | `π×2` | inexact | `6.283185307` |
| B-41 | `sin(sin(30°))` DEG | identity+inexact | `0.5` (inner exact-by-table, outer identity) |
| B-42 | `100−10%−10%` | exact | `81` |
| B-43 | `50+50%` | exact | `75` |
| B-44 | `−5+10` | exact | `5` |
| B-45 | `1.5!` | domain | error card (integer factorial only) |
