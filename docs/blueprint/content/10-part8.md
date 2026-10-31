@PART: PART VIII — QUALITY: STRATEGY, CATALOGUE, ENVIRONMENTS, HARNESS
@PARTDESC: How the product is proven: the test pyramid and CI pipeline, the complete test-case catalogue bound to feature IDs, test data and emulator environments, and the black-box harness contract that produces the owner-style evidence bundles. Quality here is measured in opened artifacts, not in assertions made.

# Chapter 20 — Testing strategy and catalogue

## 20.1 Philosophy

Tests exist to produce **evidence for the owner**, not comfort for the agent. Three consequences: (1) every test writes an artifact (results JSON, screenshot, or log) into the evidence tree; (2) the black-box layer runs against *distributed APKs*, mirroring how the owner actually receives software — a green source CI says nothing about a released APK; (3) honesty classes are explicit — PASS, FAIL, and **BLOCKED** (environment prevented a fair assertion; never counted as pass, never inferred as a product defect, §15.6).

![Test pyramid and per-PR CI pipeline with budgets.](figures/fig-testing.png)

## 20.2 The five layers

| Layer | Tech | Scope | Budget |
|---|---|---|---|
| L1 Unit (JVM) | JUnit4 + Truth + Koroutines-test | engines, models, repos with fakes; property laws | < 3 min |
| L2 Integration | Robolectric | Room/FTS round-trips, SAF fakes, orchestrator with fake runtimes | < 6 min |
| L3 Screenshot | Roborazzi | design-system components + module screens × (light/dark × font 1.0/2.0) | < 4 min |
| L4 Instrumented | Espresso/UIAutomator on Gradle-managed emulators | journeys J-01…J-10, TC-A11Y, TC-PERF | ≤ 30 min sharded |
| L5 Black-box APK QA | External Python harness (`qa/` pattern: OCR screenshot reader, deterministic taps, results JSON + screenshots) | distributed-APK behaviors: Catalogue-0, TC-ONE-*, parity, provenance | ≤ 40 min sharded |

L5 is deliberately external to the app build — it tests what shipped, in the style of the owner's existing campaigns (pinned APK SHAs, guide hashes, run IDs, evidence manifests).

## 20.3 Architecture and lint tests

Beyond behavior: Konsist architecture rules (§11.1 arrows), detekt custom rules (§18.1), manifest assertion tests (permission deny-list, C1), dependency deny-list audit (ad/tracking SDK prefixes), and the string audit (UX-015 network-vocabulary ban). These run as fast L1-class tests so violations fail in under a minute.

## 20.4 Screenshot discipline

Every design-system component and every module screen renders in a `ScreenshotSuite` activity; Roborazzi records golden PNGs at 1080×1920; PR diffs produce side-by-side evidence images; intentional changes re-record with a ledger note. Calculator key themes × key shapes generate a matrix of key-region shots consumed by the theme-diff check (UX-009: ≥ 10% pixel-diff on theme switch).

## 20.5 Naming and binding

`TC-<AREA>-<nnn>`: areas CALC, ONE (guide-parity set), HUB, NOTE, SCAN, CAL, FILE, MUSIC, REC, DIAG, SET, SEC, PERF, A11Y, STATE, AI, PACK, NAV, SYS, LAW (property laws). Every TC lists `binding: F-xxx/UX-xxx` and every F/UX lists its TCs — bidirectional, enforced by the traceability script (§27).

## 20.6 Catalogue-0 (release-blocking set)

The minimum demonstration a release build must pass (L4/L5): the full calculator parity set below plus one core scenario per other module (the module smoke set). This is the direct descendant of the owner's guide-driven cases; numbering intentionally echoes them.

| Case | Verifies | Binding |
|---|---|---|
| TC-ONE-C-001 | `2+3×4 = 14`; `(2+3)×4 = 20` | F-001 |
| TC-ONE-C-002 | implicit multiplication `2(5+2) = 28` | F-002 |
| TC-ONE-C-003 | percent `200+10% = 220`; `200×10% = 20`; `50% = 0.5` | F-003 |
| TC-ONE-C-004 | pending operator: `10+` then `−` → `10−`; `5+` `=` → `10` | F-004 |
| TC-ONE-C-005 | `10×−` evaluates `-10` | F-005 |
| TC-ONE-C-006 | auto-balance `(2+3` `=` → `25`; smart `( )` key | F-006 |
| TC-ONE-C-007 | `123456` displays `1,23,456`; copy strips commas | F-007 |
| TC-ONE-C-008 | exactness: `0.1+0.2 = 0.3`; `1÷3×3 = 1` | F-008 |
| TC-ONE-C-009 | functions: INV sin 0.5 → `30` (deg); domain error card for `ln(−1)` | F-009 |
| TC-ONE-C-010 | live answer appears/stays consistent; no stale answer on incomplete input | F-010 |
| TC-ONE-C-011 | caret: tap mid-number inserts digit; `⌫` deletes one char | F-011 |
| TC-ONE-C-012 | selection pill: long-press `123456` → highlight + `Cut Copy MAdd MUse Paste` | F-012 |
| TC-ONE-C-013 | history: 5 entries, force-stop, relaunch → 5 entries exact | F-021/F-024 |
| TC-ONE-C-014 | replay: tap card paints expression before close; race guard | F-022/23 |
| TC-ONE-C-015 | MAdd/MUse: select `4` in `3+4`, MUse stored `123456` → `3+123456` → `= 1,23,459` | F-019/20 |
| TC-ONE-C-016 | AC clears selection then expression | F-017 |
| TC-ONE-C-017 | tap-away exits selection, places caret | F-016 |
| TC-ONE-C-018 | cut & retype; copy/paste sanitize | F-014/15 |
| TC-ONE-C-019 | empty-caret menu (`MUse Paste`); insertion at caret | F-018 |
| TC-ONE-C-020 | memory sheet: slots, MUse/MAdd/MC, reorder | F-026 |
| TC-ONE-C-021 | key shape picker: 5 shapes, instant change, persists | F-028 |
| TC-ONE-C-022 | overflow list exactness (six items) | F-032 |
| TC-ONE-C-023 | key theme: 8 themes; Rose switch pixel-diff ≥ 10%; persists | F-027 |
| TC-ONE-C-024 | effects: 4 styles, `=` animation, persists | F-031 |
| TC-ONE-C-025 | no IME on calculator screen | F-033 |
| TC-ONE-C-026 | light/dark: expression/answer/caret colors per H1–H4 | F-035 |

Module smoke set (Catalogue-0, one each): note create-edit-search survives restart; scan import→export PDF; event+reminder fires in exact-alarm-permitted emulator; backup→wipe→restore (J-03); music folder import→play 5 s; record 10 s with marker→playback; hub search finds an item from 3 modules; MyCalc flavor runs TC-ONE-C-001…008 with zero module remnants (J-09); zero-permission manifest on flavor (F-038); airplane-mode cold start smoke (J-05).

## 20.7 Beyond Catalogue-0 (catalogue digest)

Full catalogue lives in `qa/testcases.csv` (generated-checked); digest:

- **SEC** (14 cases): manifest deny-list; dex network-class scan; backup zip-bomb/pTraversal rejections; wrong-passphrase restore; clipboard auto-clear; pack tamper → disabled; app-lock round-trip; SAF grant review; trash hard-delete shred; log PII scrub; intent export surface scan; custom-permission absence (flavor); WebView absence; receiver export scan.
- **PERF** (10): cold start budgets (UX-002); jank budgets: calculator 60 fps p50 keystroke→frame ≤ 16 ms (≤ 64 chars), lists 55 fps p50 scroll on Tier C profile; recorder FGS start ≤ 200 ms; hub search first page ≤ 120 ms @10k notes; DB write frame-safety; memory caps per AI tier (§16.6); APK size budgets (§23.6); battery: 10-min idle music paused = 0 wakelocks; analyzer walk no-jank; OCR job ≤ budget on Tier B fixture.
- **A11Y** (12): TalkBack core journeys; contrast token test per theme (programmatic); touch-target scan; focus order; font 2.0 no-clip; reduced-motion removal; content descriptions; live-region on live answer; dialog focus trap; heading structure; braille-display-friendly labels (no emoji in a11y text); audio-independent recorder UI.
- **STATE** (8): process-death storm J-06; rotation mid-record/capture/draft; restore-keys registry completeness; continue-row exactness; calculator expression+caret+selection restore; trash 30-day expiry sweep (local clock advance test); migration v1→v2 dry-run fixture; backup schema drift rejection (newer backup on older app → clear error).
- **AI/PACK** (16): orchestrator gate matrix (tier×battery×concurrency); each fallback rung (§16.7) forced and asserted; provenance fields present; pack import/reject/enable/disable/delete; hash mismatch disable; eval-kit thresholds (§16.8); LLM JSON schema validation; streaming cancel; warm-evict on Tier A; embedder batching budget; transcribe segment timestamps monotonic; semantic merge ordering; OCR confidence floor; label pack absent UX; assistant absent UX; TTS absence (engines without TTS) degrade silently.

## 20.8 Coverage gates

Line coverage ≥ 85% on `core/domain`, ≥ 75% on `core/data`, ≥ 60% on features (measured by Kover, reported per module in CI artifacts). Coverage is a floor, not a goal: a fully covered wrong expectation is still a bug — the binding to F/UX IDs (§20.5) is the real oracle.

## 20.9 Defect ledger

All FAILs (and any suspicious PASS) land in `reports/defects.md` with: id, TC, severity S1 (crash/data loss)…S4 (polish), repro, evidence path, status (New→Triaged→In-progress→Fixed→Verified→Closed / Blocked / Rejected-with-reason). Blocked items record the exact prevention (e.g., "emulator `input swipe` cannot reproduce stationary hold-then-drag; requires physical device — owner input"). Verified requires a green re-run on the pinned release APK (C10). Severity S1 blocks release unconditionally; S2 needs a gate-report waiver with rationale.

![Defect lifecycle with blocked and rejected paths.](figures/fig-defect-flow.png)

## 20.10 Severity/priority interaction and flake policy (normative)

Defect priority = severity × feature-priority matrix (`qa/severity.yaml`): an S2 on a P0 feature is release-blocking; an S2 on a P2 feature is fix-in-backlog. Reopened defects count double in the metrics (flaky fixes are the classic hidden cost).

Flake policy: a test that fails without product change is quarantined within one working day (moved to `quarantine/` with an owner and a one-week clock); two consecutive green full-lanes are required to release from quarantine. A flake root-cause note is mandatory (timing? ordering? resource?) — the owner's earlier campaigns showed ANR-dialog interference classes; the harness now records system-dialog encounters per case (§22.4) so flake analysis starts with evidence, not guesses.

## 20.11 Evidence retention

Gate + release evidence bundles are kept for the life of the repository (history is the audit trail); per-PR artifacts 30 days (CI-managed); local diagnostics ring 7 days by design. Nothing is ever deleted from `reports/` without a ledger entry (the owner's preservation standard).

## 20.12 One exemplar test per layer (house style reference)

```kotlin
// L1 (JVM, property): TC-LAW-003 — rendering never invents 0.999…
class LawL3RenderingTest {
  private val engine = CalcEngine()
  @Test fun `third-times-three renders one`() {
    val r = engine.evaluate("1÷3×3", EngineConfig.deg())
    assertEquals("1", engine.format(r, EngineConfig.deg()))
  }
  @Test fun `law holds on random decimals`() {
    Random(3311).decimalTriples(10_000).forEach { (a, b, c) ->
      val expr = "($a÷$b)×$b×$c÷$c"  // cancel back to a
      val r = engine.evaluate(expr, EngineConfig.deg())
      assertTrue(r.exact)                       // rational path all the way
      assertEquals(a, engine.format(r, EngineConfig.deg()))
    }
  }
}

// L2 (Robolectric): TC-NOTE-fts-01
@Test fun `search finds and ranks with snippets`() {
  db.noteDao().upsert(fixture("groceries"), fixture("laptop advice"))
  val hits = NoteSearch.query("laptop", budget = 25)
  assertEquals(1, hits.size); assertTrue(hits[0].snippet.contains("laptop"))
}

// L3 (Roborazzi): theme switch diff (UX-009)
@Test fun `rose theme repaints keys`() {
  val before = capturePad(theme = mySpaceSettings)
  setKeyTheme(Rose); val after = capturePad(theme = Rose)
  assertTrue(pixelDiff(before, after, region = KEYS) >= 0.10)
}

// L4 (instrumented): TC-ONE-C-004 trailing operator
onCalc { tapSequence("5", "+"); tap("=") }
onView(withText("10")).check(matches(isDisplayed()))

// L5 (black-box harness): Appendix Q script C-008 executes the same case
// from outside the app on the distributed APK, asserting via OCR + evidence shots.
```

House style rules visible above: tests cite spec rows in names/comments; seeds recorded; budgets explicit; no sleeps; assertions on user-visible state.

## 20.13 Coverage report example (Kover CI artifact, abridged)

```json
{"module": "core/domain", "line": 0.91, "branch": 0.87, "budget": 0.85, "ok": true},
{"module": "core/data",   "line": 0.84, "branch": 0.79, "budget": 0.75, "ok": true},
{"module": "feature/calculator", "line": 0.71, "budget": 0.60, "ok": true},
{"module": "feature/scanner",    "line": 0.63, "budget": 0.60, "ok": true}
```

Uncovered-code review happens at gates: any uncovered class in `core/*` needs either a test or a ledger reason (generated code, delegate-only, JNI shim).

# Chapter 21 — Test environments and data

## 21.1 Emulator matrix

| Profile | API | RAM/skin | Purpose |
|---|---|---|---|
| E26C | 26 | 2 GB, 1080p | floor: compatibility, Tier C |
| E33B | 33 | 4 GB | median: notifications model, exact alarms, media APIs |
| E35A | 35/36 | 8 GB | Tier A: LLM pack, predictive back, edge-to-edge |

Managed devices in CI (Gradle managed emulator or equivalent), 3 parallel runners max (C8), airplane-mode cold-start runs as a system-state step (J-05) on each profile.

## 21.2 Physical-device delta

Some behaviors cannot be honestly tested via emulator input injection (documented example: stationary hold-then-drag selection, B2/F-013 — `adb input swipe` starts a move immediately; the app's 300 ms stationary detector rejects it). Policy: emulator runs mark such cases **BLOCKED** with the prevention recorded; the release evidence lists them as "requires physical-device verification"; the owner's device run can execute the same harness (the L5 harness is plain adb+Python, runnable on any USB device).

## 21.3 Test data fixtures (in-repo, versioned)

`qa/fixtures/`: 40 OCR images (printed/handprint Latin, multi-size, incl. invoice-style), 20 audio clips (clean/noisy speech, 5–30 s) with reference transcripts, 200-note corpus (Markdown+NoteDoc) for search/eval, 200 RRULE golden corpus, 12 `.msone` backups (v1; incl. 2 malicious-pattern archives for rejection tests), 6 music fixtures (generated tones with metadata, 10–60 s), 3 model-pack dummies (correct-shape, bad-hash, oversized) for PACK tests, 40-image eval kit + 20-note summarization rubric set (§16.8). All synthetic; no personal data.

## 21.4 Determinism

Every randomized test takes a seed recorded in its output; law-suite corpora are seeded per CI run id so failures reproduce; screenshot tests pin font rendering (bundled fonts, fixed density). Time-dependent tests use an injected `Clock` (trade-off noted: system-clock paths get one dedicated smoke per module to catch real-world skew).

## 21.5 Fixture generation and provenance

All synthetic fixtures are generated by `tools/fixtures.py` (seeded) so they are reproducible: OCR images rendered from bundled fonts with affine jitter; audio clips from phoneme-balanced synthetic speech corpus + noise mixes; music = generated sine/chirp tones with ID3/Vorbis metadata; backups = built from the Room fixture seeds via the real backup manager (never hand-crafted zips), except the malicious-pattern set which is hand-built to exercise guards. Every fixture file carries a `fixtures-manifest.json` (sha256, generator seed, purpose) verified by a fast CI test — the same provenance habit the release evidence uses.

## 21.6 Fixture manifest example (checked by CI)

```json
{"ocr/inv-007.png": {"sha256": "3f2c…", "seed": "7", "purpose": "invoice printed 10pt"},
 "asr/clip-011.wav": {"sha256": "91aa…", "seed": "11", "ref": "asr/clip-011.txt"},
 "backups/v1-ok-03.msone": {"sha256": "bb0d…", "generator": "BackupManager@9c4e"},
 "packs/dummy-essentials.mspack": {"sha256": "5c1f…", "models": 3}}
```

A missing fixture or hash drift fails the environment test before any suite runs — QA never starts on a drifted tree.

## 21.7 Emulator provisioning script (runner bootstrap, normative)

```bash
sdkmanager "emulator" "platform-tools" "system-images;android-26;google_apis;x86_64"   "system-images;android-33;google_apis;x86_64" "system-images;android-35;google_apis;x86_64"
avdmanager create avd -n e26c -k "system-images;android-26;google_apis;x86_64" -d pixel_4   && adb emu avd snapshot reset qm  # cold each suite
# profile caps: e26c → 2048 MB heap, e33b → 4096, e35a → 8192 (tier parity with §3.2)
```

Snapshots are reset per suite (never reused across suites) to keep J-05/J-06 honest; airplane mode is toggled via `svc wifi disable && svc data disable` + `cmd connectivity airplane-mode enable`, and the harness *asserts* radio-down state before airplane-labeled cases (an asserted environment, not an assumed one).

## 21.8 Physical-device lab protocol (when a device is attached)

```
1. adb device fingerprint recorded (model, Android version, build) into evidence
2. Harness runs the same YAML cases; gestures B2-class attempted for real:
   long-press then continuous move with pressure/stationarity the emulator lacks
3. OEM quirks probed: alarm policy, FGS kill aggressiveness, SAF provider quirks
   (results appended to the OEM quirk register in the ledger)
4. Screenshots pulled per case; manifest verified; results merged with emulator runs
   (dedupe rule: device results annotate, never silently overwrite emulator ones)
```

## 21.9 CI schedule summary

| Lane | When | Contents |
|---|---|---|
| Fast | every PR | L1+L2+L3 + audits (≤ 12 min) |
| Full | trunk merge + nightly 02:00 | + L4 matrix + L5 nightly profile |
| Release | tags | reproducible builds + release L5 + docs + bundle |
| Owner-device | on demand | §21.8 protocol |

# Chapter 22 — Black-box APK QA harness contract

This chapter formalizes the L5 layer so its reports match the evidence style the owner already trusts (their calculator QA campaigns): pinned inputs, honest states, screenshots, manifests, and a PDF report of record.

## 22.1 Scope rule

The harness tests **distributed APKs** (release or dist builds), never debug builds, and never infers released-binary behavior from source CI. MySpace-module focus discipline: probes target the app's calculator (and the module under test); anything else recorded by a probe is context, never counted as calculator coverage.

## 22.2 Pinned-input manifest

Every run embeds: APK path, package, versionName/versionCode, SHA-256 (asserted against the manifest before install — a mismatch aborts the run as INVALID, not FAIL); the spec hash (this blueprint's section set, or the owner guide hash when the owner supplies one); source commit + workflow run id; emulator profile; host runner image. The report builder re-validates every row (stronger than trusting labels) — the owner's reports already set this standard.

## 22.3 Session discipline (per probe)

1. Fresh install (or `pm clear`) per suite unless the case tests persistence.
2. Deterministic route to the module (explicit activity/component when exported to self; else UI path) with a **navigation assert** — if the harness finds itself off-module (the historical "Pixel launcher" drift), it records BLOCKED-with-context and resets; it does not keep probing unrelated screens.
3. State-reset between cases (AC, close sheets, dismiss dialogs); popup vocabulary handled explicitly (e.g., a persistent history button is not a popup — the harness must not "back out" of the app hunting for it, a recorded past lesson).
4. Input honesty: taps/long-presses via instrumented UIAutomator when in-process (L4) or adb `input` (L5); gestures the input API cannot fairly reproduce are BLOCKED by rule (§21.2), never retried into false FAILs.
5. OCR-based assertions (screenshot → text) tolerate rendering variance with normalized matching; ambiguous reads capture the raw crop as evidence.

## 22.4 Stability rules from field lessons

No toast calls from worker threads in the app (the harness *tests* this via SYS cases; the historical crash class stays dead); harness waits are condition-based (idle-resource + idle-instrumentation), never fixed sleeps beyond 2 s; ANR dialog handling: the harness detects system ANR dialogs, selects *Wait* up to 3 times (recording each), then reports BLOCKED — mirroring the owner's harness behavior; every screenshot embeds the step name in its filename for mechanical manifest pairing.

## 22.5 Outputs

Per run, under `reports/evidence/<run-slug>/`:

```
raw/<shard>/user-journey-results.json     # per-case: id, status(PASS/FAIL/BLOCKED), actual, comment, shots[]
raw/<shard>/calculator-evidence-*.png     # step screenshots
raw/<shard>/logcat.txt                    # filtered, scrubbed
evidence-manifest.json                    # every file: sha256 + size (verified post-write)
qa-summary.json                           # counts, pinned inputs, run ids
```

The PDF builder consumes only manifest-verified files (any missing/mismatched file fails the build), then emits the report of record with: provenance page, version-alignment notes, per-case tables, embedded screenshots, blocked-items register, and source-CI context clearly labeled as *not* direct-APK proof. Publisher success is never conflated with passing results — the report shows failing cases even when the publishing job is green (field lesson §15.8(3)).

## 22.6 Acceptance style

Reports state: what was proven, what was blocked and why, what was not tested at all. No third-party substitutes for named comparisons (e.g., official Google Calculator parity is compared only when the genuine package is installable on the test device; absence is recorded, never substituted — the owner's explicit standard).

## 22.7 Harness case schema (normative example)

```yaml
- id: TC-ONE-C-004
  binding: [F-004]
  suite: calculator-parity
  pre: install(app=full, pin_sha=…), start_module(calculator), state_reset()
  steps:
    - tap_sequence: [5, +]
    - tap: "="
    - assert_ocr: {region: display, contains: "10", normalize: strip_grouping}
    - screenshot: user-tc-one-c-004-after-equals.png
  on_blocked: record(context="…"), continue_suite
  evidence: [results-json, screenshots, logcat-slice]
```

Rules: every step has an evidence artifact or a named assertion; `on_blocked` must record the prevention, not silently pass; regions are symbolic (resolved per layout) so the harness survives minor UI moves; OCR normalization rules (`strip_grouping`, `unicode_ops`) are shared code with the app's renderer tests to avoid double standards.

## 22.8 Harness run profiles (normative)

| Profile | Trigger | Suites | Artifacts |
|---|---|---|---|
| PR-smoke | every PR (L5-capable runner free) | calculator parity subset (C-001…008) on E33B debug-as-dist build | results JSON, 8 screenshots |
| nightly | schedule | full ONE set + module smokes on E26C/E33B/E35A | 3 × results JSON + manifest |
| release-candidate | tag build | full set against signed release APKs (both flavors), airplane-mode profile included | qa-summary + PDF of record inputs |
| owner-device | on demand (USB device attached) | full set on physical device, B2-class gestures attempted for real | results + device screenshots |

Profiles share the case YAML (§22.7); only environment blocks differ. A release-candidate profile red blocks the release regardless of other lanes (Catalogue-0 rule).

## 22.9 Evidence naming conventions (normative)

- Screenshots: `calculator-evidence-<case-or-step-id>-<slug>.png` (the owner's existing pattern), lowercase, hyphenated.
- Results: `user-journey-results.json` per shard (compatibility with the owner's downstream tooling).
- Manifest: `evidence-manifest.json` at bundle root; every file listed with sha256 + bytes; verified post-write by the publisher before any report build.
- Logs: `logcat-<shard>.txt` filtered to the app pid + harness tags, scrubbed per §28.3.

## 22.10 Journey YAML sample (J-02, trimmed)

```yaml
- id: J-02
  title: Record to minutes
  pre: [install(pinned), grant(mic), pack(speech=installed)]
  steps:
    - {do: start_module, arg: recorder, shot: j02-01-open}
    - {do: tap, arg: record, wait: {notification: "Recording"}}
    - {do: sleep, arg: 30}
    - {do: tap, arg: flag, shot: j02-04-flag}
    - {do: tap, arg: done}
    - {do: assert_db, arg: "recording row exists, duration>=29000"}
    - {do: tap, arg: transcribe, budget: {s: 120}, shot: j02-07-transcribed}
    - {do: assert_ocr, region: transcript, contains_any: ["meeting", "agenda"]}
    - {do: tap, arg: to_notes}
    - {do: assert_db, arg: "note created with sourceRecordingId"}
  blocked_if: [mic_denied_unexpected, fgs_start_slow]
```

## 22.11 OCR assertion normalization rules (shared with renderer tests)

| Rule | Input sample | Normalized |
|---|---|---|
| strip_grouping | `1,23,459` | `123459` |
| unicode_ops | `3+4×2` (with U+2212/00D7) | `3+4x2` ASCII-fold |
| collapse_ws | multi-space OCR jitter | single space |
| casefold_alpha | `History` vs `HISTORY` | lower |
| superscript_fold | `10³` | `10^3` |
| ligature_fold | `ﬁ` | `fi` |
| minus_unify | `− – —` | `-` |

Both the app's renderer tests and the harness import the same normalization module (`qa/normalize.py` ↔ `core/designsystem/testutil`) — one definition of "equal" everywhere (the owner's harness philosophy).

## 22.12 `user-journey-results.json` sample (schema-compatible with owner tooling)

```json
[{"id": "TC-ONE-C-004", "binding": ["F-004"], "status": "PASS",
  "actual": "display=10; second equals=15", "comment": "trailing-operator rule proven",
  "shots": ["calculator-evidence-tc-one-c-004-after-equals.png"], "ms": 4120},
 {"id": "TC-ONE-C-B2", "binding": ["F-013"], "status": "BLOCKED",
  "actual": "hold-then-drag not reproducible via adb input",
  "comment": "no product failure inferred; requires physical device"}]
```

## 22.13 Harness code skeleton (Python, `qa/` layout contract)

```python
# qa/harness.py — entrypoint: run(profile) → evidence dir
class Device:            # adb wrapper: tap/swipe/longpress/key/shell/screenshot
    def tap(self, x, y): ...
    def longpress(self, x, y, ms=300): ...
class OcrReader:         # screenshot → normalized text (§22.11 rules)
    def text(self, img, region=None) -> str: ...
class Case:              # loaded from YAML (§22.7)
    id: str; steps: list[Step]; on_blocked: str
class Runner:
    def run_case(self, case, device, ocr) -> CaseResult:   # PASS/FAIL/BLOCKED + evidence
class Publisher:
    def write_results(self, results): ...                  # user-journey-results.json
    def write_manifest(self, files): ...                   # sha256 + verify pass
# CLI: python3 qa/harness.py --profile nightly --apk artifacts/MySpace-…-dist.apk --pin-sha …
```

The harness stays independent of the app build (own venv, own deps) — it must be runnable by the owner against any APK file without the repo's toolchain.
