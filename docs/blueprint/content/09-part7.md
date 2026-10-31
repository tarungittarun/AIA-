@PART: PART VII — ENGINEERING STANDARDS AND THE AGENT LIFECYCLE
@PARTDESC: The rules the code itself must follow (Chapter 18) and the full G0–G8 lifecycle the agent executes (Chapter 19), including per-phase task slices, review checklists, and definitions of done. Together they make the build auditable end to end.

# Chapter 18 — Engineering standards

## 18.1 Language and style

- **Kotlin 2.x**, JVM target 17, Compose compiler aligned; coroutines + Flow for asynchrony; no `GlobalScope`; explicit `Dispatchers` injection (no hardcoded `Dispatchers.IO` in classes — injected `DispatcherProvider` for testability).
- Formatting: ktfmt (standard style), enforced by spotless; detekt default suite + custom rules: `NoHardcodedColor` (use tokens), `NoDirectToastFromWorker`, `NoNetworkApis` (blocks `java.net`, `okhttp`, `WebView` symbols), `SpecHeaderPresent` (file header carries `Spec: §…`).
- Commits: conventional prefixes (`feat(calc):`, `fix(calendar):`, `test:`, `docs:`, `chore:`); every commit message ends with `Refs: F-xxx…` where applicable — the traceability script consumes this (§27).

## 18.2 Definition of done (per task)

1. Implementation + tests committed; `Refs:` present.
2. Local: compile, module tests, detekt/lint clean, `git diff --check` clean.
3. New UI → screenshot tests added/updated; new schema → migration test; new engine behavior → property or table test.
4. Task graph entry updated (status, artifacts); acceptance IDs linked.
5. No new `TODO` without a linked task id.

## 18.3 Branching and review

Trunk-based with short-lived feature branches (`t-<task-id>`), squash-merged by the agent after self-review. Self-review is a distinct act: the agent re-reads the diff against the binding spec sections and records a one-line review note in the merge commit (`Reviewed against §17.1.5: percent table rows 1–7 covered`). CI protects `main`: no direct pushes, all checks required (§24.3).

## 18.4 Review checklists (condensed)

**Privacy checklist (every PR):** no new permission; no network-class API; no new identifier; no logging of content beyond PII-scrubbed ring; new user data classified (§14.3).
**AI checklist (AI-touching PRs):** fallback path exists + tested; provenance captured; budgets enforced; cancel works; pack-absent UX correct.
**Calc checklist (engine PRs):** laws re-run; §17.1.5 table rows touched by the change re-tested; canonical-form tests updated.
**UX checklist (UI PRs):** token-only colors; touch targets ≥ 48 dp; state triple (empty/error/content) present; TalkBack labels; dark mode screenshot.

## 18.5 Documentation standards

Code documents *how*, this blueprint documents *what/why*: source comments stay local (no essay comments), `docs/` mirrors decisions via the ledger, and every module ships a `README.md` ≤ 40 lines (purpose, spec refs, test entry points). The release regenerates: this blueprint PDF (from `docs/blueprint/`), the traceability matrix, the license list, and the OpenAPI-less API surface summary (`tools/api-surface.py` output) — all archived in the release evidence (S8).

## 18.6 Annotated review example (quality bar for self-reviews)

Diff under review (task T-CALC-014, percent accumulation fix):

```diff
-    val left = eval(node.left)
-    val pct = eval(node.right) / Decimal(100)
-    return when (node.parent) {         // BUG: used syntax parent, not semantic lhs
+    val left = eval(node.left)          // §17.1.5 rows 1-3,6: context = left value
+    val pct = eval(node.right) * left / Decimal(100)  // additive rows: % of accumulated left
+    return when (node.kind) {           // ADD vs MUL path per normative table
```

Review note (merge commit): `Reviewed against §17.1.5: all 7 table rows re-tested incl. row 6 chains; L4 law corpus re-run seed 3311 green; found and fixed wrong-parent bug via row 6 (200+10%+10%=242). Refs: F-003`. The bar: the reviewer-voice note cites the exact spec rows touched and names the test that caught the bug — a reader can audit without re-deriving.

# Chapter 19 — The agent lifecycle G0–G8 in full

## 19.1 Phase table

| Phase | Goal | Key tasks (slice) | Gate | Budget (agent iterations) |
|---|---|---|---|---|
| G0 | Alignment | Blueprint acceptance; task graph seed | G0 report | 1–2 |
| G1 | Skeleton | Gradle workspace, flavors, CI scaffold, empty hub, smoke UI test | Builds on CI, both APKs assemble | 6–10 |
| G2 | Foundations | Design system (tokens→components), Room v1, repositories, arch tests, RestoreKeys | G2 report; screenshot suite green | 15–25 |
| G3 | Calculator | Engine (laws) → UI (pads/caret/selection) → history/memory/themes → flavor parity; Catalogue-0 calc green | G3 report | 25–40 |
| G4 | Modules | Notes → Scanner → Calendar → Files → Music → Recorder → Hub; P0 sets + journeys (AI mocked) | G4 report | 60–90 |
| G5 | AI | Pack manager, OCR, ASR, embeddings, LLM features, fallbacks, eval kit | G5 report; fallback ladder proven | 25–40 |
| G6 | Hardening | A11y, perf budgets, security checklist, copy audit, battery/thermal tests, i18n externalization | G6 report | 15–25 |
| G7 | Release | Versioning, signing, shrink, release QA (black-box harness), evidence bundle, docs regen, distribution builds | S1–S8 | 8–12 |
| G8 | Operate | Backlog, defect triage, update runbook, post-release monitoring-by-diagnostics | G8 report | 3–5 |

Budgets are iteration guides, not deadlines; gates, not calendars, control progression.

## 19.2 Per-phase verification depth

- G1–G2: JVM tests + Robolectric + first emulator smoke (one runner).
- G3–G4: full pyramid per §20.2; emulator matrix API 26/33/35 sharded across the 3 runners; black-box harness (§22) starts at G3 (calculator) because it is the owner's proof instrument.
- G5: adds device-tier profiles (2 GB / 4 GB / 8 GB emulator skins) and pack fixtures.
- G6–G7: release-type builds only; black-box harness runs against the *unsigned-then-signed release* APK with the same evidence style as the owner's prior campaigns (results JSON + screenshots + manifest, §22.6).

## 19.3 Metrics that steer the agent

Tracked per phase, committed as `reports/metrics.json`: task burn (done/total per phase), defect discovery rate (§20.9), test flake rate (< 1% hard limit — a flaky test is quarantined within one day), build time p50 (< 6 min), APK size trend, coverage on core modules (≥ 85% line on `core/domain`, §20.8), and law-suite runtime (< 90 s CI budget). Metrics feed the gate reports; the agent re-plans any metric trending red.

## 19.4 Interruption and resumption protocol

If a session ends mid-phase: the next session (a) reads task graph + ledger + last gate report, (b) runs the phase's fast verification (compile + module tests) to re-earn trust in the working tree, (c) resumes the first open task in dependency order. No work is redone on guesswork; no state is trusted without verification — the same evidence discipline the owner's QA harnesses already follow.

## 19.5 Owner interaction points

Only four moments require the owner: blueprint acceptance (G0), any P2 deferral or cutline decision (§10.3), provision of anything genuinely unobtainable (e.g., a physical device for B2-class gestures), and release acceptance (G7). Everything else is recorded, not asked.

## 19.6 Phase task slices (representative task graph rows)

G1 (skeleton, 8 tasks): T-BOOT-001 workspace+wrappers; T-BOOT-002 flavors assemble; T-BOOT-003 CI fast lane; T-BOOT-004 empty hub on emulator; T-BOOT-005 provenance BuildConfig; T-BOOT-006 keystore ceremony + owner backup rehearsal; T-BOOT-007 screenshot harness bootstrap; T-BOOT-008 G1 gate report.

G2 (foundations, 22 tasks): tokens table+tests; theme light/dark; AppTopBar/BottomSheet/Fab/EmptyState/ErrorState/SearchField/ConfirmSheet screenshots; Room v1 schema + export; DAOs + repo tests; SAF repo + fakes; DataStore settings registry; RestoreKeys; arch tests active; hub shell + continue-row plumbing; G2 report.

G3 (calculator, 34 tasks): tokenizer; parser; exact evaluator; Decimal path; renderer+grouping; percent; implicit-mul; trailing-op; balance; errors; law suite; keypad UI basic; sci pad; ExpressionField caret; live answer; selection detector+pill; B-actions (cut/copy/paste/MAdd/MUse); empty-caret menu; history sheet+persistence+replay+race guard; memory sheet; themes×shapes; effects; haptics; overflow exactness; flavor swap+lint; mycalc zero-permission gate; L5 calculator campaign; perf budgets; a11y pass; G3 report.

G4 (modules, 58 tasks): notes (12), scanner (9), calendar (9), files (9), music (7), recorder (7), hub (5) — each task carries its §9 feature IDs; journeys J-01…J-10 with AI mocked; G4 report.

G5 (AI, 26 tasks): pack format+manager; registry+hash gates; orchestrator+budgets; ONNX bindings; det/rec OCR pipeline; embeddings+semantic merge; whisper JNI; MediaPipe LLM + prompts.yaml; per-feature integration (notes actions, recorder transcribe, scanner OCR, hub semantic, calendar parse); fallback ladder tests; eval kit runs; tier profiles; G5 report.

G6 (hardening, 18 tasks): a11y audit battery; TalkBack journeys; contrast tests; font-scale sweeps; Macrobenchmarks; memory caps; battery/Doze tests; security checklist SC-01..12; string audits; dynamic color; predictive back; tablet layouts; locale sweeps; flake quarantine sweep; G6 report.

G7 (release, 10 tasks): versioning; R8 tuning; reproducible double-build; release L5 campaign on artifacts; docs regen (this blueprint, traceability, licenses, api-surface); evidence bundle assembly; RELEASE-NOTES; distribution staging; sign-off pack for owner; publish.

G8 (operate, 4 tasks): defect triage; backlog v1.1; runbook; G8 report.

## 19.7 Filled example — G1 gate report (target quality bar)

```markdown
# Gate G1 report — Bootstrap
Date: (execution date) · Sessions: S-001…S-006
## Criteria
| Criterion | Status | Artifact |
| Workspace builds (both flavors, debug) | PASS | ci-run-1207/log.txt |
| Empty hub renders on E33B emulator | PASS | evidence/g1/hub-cold-start.png |
| CI fast lane green (build+lint+unit) | PASS | ci-run-1208/summary.json |
| Keystore ceremony + owner backup rehearsal | PASS | evidence/g1/keystore-rehearsal.md |
| Screenshot harness bootstrap (hub golden) | PASS | shots/hub-golden.png |
## Defects
D-001 (S3) flavor res merge order → fixed, verified (ci-run-1209)
## Ledger
D-0001 Koin over Hilt (ADR-04 confirmed at build time; build 38% faster)
## Owner actions
None. (Keystore backup download receipt requested at G2.)
```

Quality bar: every row has an artifact path that opens; every open item has an owner and a next check date; nothing is asserted without a path.

## 19.8 metrics.json example (per-phase artifact)

```json
{"phase": "G3", "generated": "2026-11-14T18:02Z",
 "tasks": {"done": 31, "open": 3, "blocked": 1},
 "tests": {"total": 712, "flake_rate": 0.004, "quarantined": 1},
 "build": {"p50_min": 4.6, "p95_min": 7.1},
 "apk_mb": {"full": 21.4, "mycalc": 5.1},
 "coverage": {"core.domain": 0.91, "core.data": 0.84, "features": 0.63},
 "laws": {"cases_per_law": 12000, "runtime_s": 71},
 "defects": {"open_s1": 0, "open_s2": 0, "opened_this_phase": 14, "fixed": 14},
 "ci": {"jobs_last_full_lane": 26, "runner_cap_ok": true}}
```

## 19.9 Phase-level definitions of ready and done

| Phase | Ready when | Done when |
|---|---|---|
| G1 | blueprint accepted; graph seeded | gate report committed |
| G2 | G1 closed; tokens table drafted | design-system screenshots + Room v1 tests green |
| G3 | G2 closed | Catalogue-0 CALC + laws + flavor parity green on CI |
| G4 | G3 closed | module P0 sets + journeys green (AI mocked) |
| G5 | G4 closed | packs + fallback ladder proven on tier profiles |
| G6 | G5 closed | a11y/perf/security/copy audits green on release-type builds |
| G7 | G6 closed | S1–S8 artifacts published; owner walkthrough accepted |
| G8 | G7 published | backlog + runbook + triaged ledger committed |
