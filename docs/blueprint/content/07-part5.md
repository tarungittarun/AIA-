@PART: PART V — METHOD AND INTELLIGENCE
@PARTDESC: How an autonomous AI agent runs this program without drift (Chapter 15) and how on-device AI is integrated into the product without violating its promises (Chapter 16). The two chapters share a philosophy: capability must be provable, bounded, and reversible.

# Chapter 15 — Agent methodology: building an app without a human in the loop

## 15.1 The mandate

The agent's mandate is: *produce the release defined by S1–S8 (front matter) by executing phases G0–G8, spending at most 30 CI jobs per full pipeline run and 3 parallel runners (C8), and leaving behind evidence, not assertions.* The agent may not: weaken a constraint; ship with a red P0; invent scope; or claim success without an artifact path a human can open.

## 15.2 Operating loop

Every unit of work — from "add a token" to "integrate OCR" — runs the same micro-cycle:

1. **Read** the binding sections (this document) for the task.
2. **Plan** the change: files, tests, acceptance mapping (task graph entry, §15.3).
3. **Implement** with tests written against acceptance criteria first where practical (the agent writes its own tests; it is both author and reviewer, so the tests are the reviewer).
4. **Verify locally**: compile, unit tests, lint; only then commit.
5. **Evidence**: test output paths, screenshots (for UI), updated traceability entries.
6. **Re-plan**: if acceptance cannot be met, the task splits or a defect/decision is filed — never silently skipped.

## 15.3 Task graph

The program is a DAG of tasks. Each task record contains: `id`, `phase` (G0–G8), `title`, `binding-spec` (§ refs), `acceptance` (TC/UX/F ids), `depends-on`, `estimate` (agent-hours proxy), `artifacts`. The graph lives at `docs/plan/task-graph.yaml` and is the agent's single source of scheduling truth; a task without binding-spec refs or acceptance ids is invalid. Sample slice:

```yaml
- id: T-CALC-014
  phase: G3
  title: Percent semantics (context-sensitive)
  binding-spec: [§9.2 F-003, §17.1.5]
  acceptance: [TC-ONE-C-004, TC-CALC-law-percent]
  depends-on: [T-CALC-003]
  artifacts: [core/domain/calc/Percent.kt, core/domain/test/calc/PercentTest.kt]
```

## 15.4 Context strategy (how the agent stays on-spec)

- **Load-on-phase**: at phase start the agent re-reads the phase's chapters; it does not rely on memory across long gaps.
- **Spec-to-code links**: every source file header carries `Spec: §…` comments; the traceability script (§27) flags code touched without spec refs during review.
- **Decision ledger**: `docs/plan/decisions.md` records every choice not dictated by this document (D-nnn: date, question, options, decision, consequence). The ledger is append-only; revisiting a decision requires a new entry, never an edit.
- **No silent context loss**: if a session boundary interrupts work, the agent resumes from the task graph + ledger, never from recollection.

## 15.5 Phase gates

![Nine gates from inception to operation; each opens only on demonstrated exit criteria.](figures/fig-lifecycle.png)

| Gate | Exit criteria (all machine-checkable unless noted) |
|---|---|
| G0 Inception | This blueprint accepted; task graph G1 slice populated |
| G1 Bootstrap | `app` builds; both flavors assemble; empty hub renders on emulator; CI green end-to-end |
| G2 Foundations | Design-system components + tokens done with screenshots; Room v1 + migrations tested; CI architecture tests active |
| G3 Calculator | Catalogue-0 CALC set green (incl. F-001…F-035 P0s); flavor parity J-09 green; property laws (§17.1.7) green |
| G4 Modules | Notes, Scanner, Calendar, Files, Music, Recorder, Hub P0 sets green; journeys J-01…J-10 green (AI-dependent steps mocked) |
| G5 On-device AI | Pack manager F-082; OCR/transcribe/summarize/semantic-search acceptance green on Tier A/B emulators; fallback ladder (§16.7) proven — features green with packs absent |
| G6 Hardening | A11y audit (TC-A11Y-*) green; perf budgets (§23.6) met on Tier B/C profiles; security checklist §14 verified; string/copy audit UX-015 green |
| G7 Release | S1–S8 all true; release APK + evidence bundle + regenerated docs published |
| G8 Operate | v1.1 backlog filed; defect ledger triaged; update-runbook (§29) committed |

A gate closes with a **gate report**: one page per gate listing criteria, artifact paths, and open defects, committed under `reports/gates/Gn.md`. The owner can stop the program at any gate; the graph's later tasks are all downstream of closed gates.

## 15.6 Handling blocked work

Blocked ≠ failed. The agent records: what was attempted (commands, inputs), the observable outcome, why fair assertion was impossible, and the unblock condition. Blocked items never masquerade as passes; they appear in gate reports as `BLOCKED` with owners (agent-fixable vs owner-input-needed). Example class: a gesture the emulator input API cannot reproduce (the owner's past QA showed `adb input swipe` cannot do a stationary hold-then-drag); the honest state is BLOCKED with a device-test recommendation, not a FAIL invention or a silent skip.

## 15.7 Decision ledger discipline

Entries are cheap and frequent. A change is ledger-worthy when: the document is silent; two spec sections tension; a dependency forces a deviation; or a budget cannot be met. Each entry names the binding sections it *could* have affected. The G7 review walks the ledger top-to-bottom — this is how the owner audits an autonomous build.

## 15.8 Field lessons baked into this methodology

The owner's previous QA campaigns surfaced failure modes this methodology explicitly prevents: (1) harness navigation drift — probes wandering to launchers and other modules — now prevented by module-scoped sessions and state-reset steps (§22.3); (2) toast crashes on background instrumentation threads — now a harness rule: UI assertions only from the instrumented main path, service work posted to the app's own handlers (§22.4); (3) publisher-success confusion — a green publish job is not a passing result, so gate reports and the PDF report always carry per-case results, never job status alone (§22.6); (4) cross-release guide mismatch — every run pins APK SHAs and guide hash (§22.2, C10).

## 15.9 Gate report template (normative shape)

```markdown
# Gate G3 report — Calculator
Date / agent session ids: …
## Criteria table
| Criterion | Status | Artifact |
| TC-ONE-C-001..026 | 26/26 pass | reports/evidence/g3/raw/*/user-journey-results.json |
| Law suite L1–L10 | pass (12,000 cases/law, seed 3311) | reports/evidence/g3/laws.json |
| Flavor parity J-09 | pass | … |
## Blocked register
| TC-ONE-C-B2 hold-then-drag | BLOCKED | emulator input cannot reproduce stationary hold; needs physical device |
## Defects opened/closed
D-014 trailing-op repeat chain (closed), …
## Decision ledger entries this phase
D-009 …
## Owner actions requested
None / device session request …
```

## 15.10 Worked micro-task (illustrative agent trace)

Task T-CALC-014 (percent semantics): read §9.2 F-003 + §17.1.5 → write table-driven tests for the seven normative rows + 200 randomized law-L4 cases (seed pinned) → implement `PercentNode` fold in evaluator → run module tests (fail: `200+10%+10%` row) → fix accumulation semantics (percent of accumulated left value) → re-run (green) → detekt/kfmt → commit `feat(calc): context-sensitive percent semantics; Refs: F-003` → update task graph + traceability row → screenshot unaffected (no UI delta). Total: one iteration; evidence = test output file path recorded in task entry.

## 15.11 Agent tool inventory and use policies

The executor is an AI agent with a fixed toolkit; misuse of tools is a defect class, so use policies are normative:

| Tool | Use for | Policy |
|---|---|---|
| Local shell (build/test/git) | compile, run tests, commits | never push to protected branches; never force-push; commits carry Refs |
| Emulator (managed) | L4/L5 runs | 3-runner cap; snapshot reset per suite; airplane-mode toggles scripted |
| File editor | code/docs edits | edits only with a task id; no edits to `qa/testcases.csv` by hand (generated) |
| Web/docs access | dependency docs, API references | read-only; no downloads outside pinned dependency managers |
| Issue/ledger files | defects, decisions | append-only patterns (§15.7, §20.9) |
| Report builder | gate reports, PDF of record | only from manifest-verified evidence |

Guardrails: no secrets in the repo (keystore via CI secret store only); no network egress attempts from app code ever; no dependency added without ledger + audit pass; no CI job count growth beyond caps (C8); any tool failure on a critical step (install, build, harness) is recorded with raw output in the evidence tree — silent retries without evidence are forbidden (the owner's honesty standard).

## 15.12 Anti-drift reviews (weekly cadence)

Once per agent-week (or 40 tasks, whichever first): re-read §1.2–§1.4 (promises/constraints), diff `task-graph.yaml` against the actual commit log (detect tasks done without graph entries), sample three merged PRs and re-review against their binding sections, and re-run the full fast lane from clean. Drift findings go to the ledger with corrective tasks. The G-gates remain the hard checkpoints; anti-drift reviews are the soft Cadence that keeps gates boring.

## 15.13 Context-recovery worked example (session resume)

Session S-019 ends mid-G4 after `fix(calendar): DST clamp` compiles but tests hang. Next session S-020: (1) reads task graph (T-CAL-014 in-progress, blocked-on flaky timer test), ledger (D-0031 fake-clock injection for alarm tests), last session log; (2) runs module tests with a 120 s timeout — reproduces the hang with stack: `TestDispatcher` idle-wait; (3) applies ledger decision D-0031 (inject `TestClock`), test green, commit, task closed; (4) logs session and proceeds to next task. Nothing was remembered — everything was read. If the recovery had failed twice, protocol says: quarantine the flaky test (§20.10), open defect with stack, continue with the next independent task.

# Chapter 16 — On-device AI strategy

## 16.1 Principles

1. **AI is optional by architecture**: every AI affordance has a manual path of equal correctness (slower or less convenient); absence of packs changes speed, not capability (X7).
2. **Nothing downloads**: packs are side-loaded files imported by the user, SHA-256-verified (C5).
3. **Deterministic degradation**: each capability has an explicit fallback ladder (§16.7); the app never guesses whether AI ran — provenance is recorded with every AI output (`model`, `pack version`, `seed`, `timestamps`).
4. **Bounded resources**: one model hot at a time (except embedder, small); hard memory caps per tier; eviction on background; thermal/battery gates.

## 16.2 Capability × module map

| Capability | Used by | Manual equivalent | Pack | Priority |
|---|---|---|---|---|
| OCR (det+rec, Latin) | Scanner, hub search over scans | Type text manually / import text files | Essentials | P0 (F-057) |
| Image labels | Files analyzer auto-albums (v1.1), scanner suggestions | Manual naming | Essentials | P2 |
| Embeddings (MiniLM-L6 int8) | Semantic note search, "find related" | FTS search | Essentials | P1 (F-042, F-054) |
| ASR (whisper-tiny/base int8) | Recorder transcribe; voice search (v1.1) | Manual notes | Speech | P1 (F-076) |
| Small LLM (Gemma-2B-it, 4-bit, MediaPipe) | Summarize, rewrite, checklist-ify, smart event parse ("lunch with Ravi tomorrow 1 pm" → fields) | Manual editing | Assistant | P1 (F-054) |
| TTS | Read note aloud, read transcript | Reading | System TTS (no pack) | P2 |

## 16.3 Interaction contract for AI features

Every AI action follows one UX contract: (1) entry is a clearly-marked secondary action (`✦` prefix, `AI` tag); (2) a visible running state with cancel; (3) results appear as a **preview** (diff or draft card) — the user applies, edits, or discards; (4) undo survives apply (trash-backed original block); (5) if the pack is missing the row shows the install path ("Diagnostics → Model packs"), never a dead button; (6) outputs carry a provenance footnote (model + pack version) in the note's front-matter (hidden by default, visible in export info).

## 16.4 The AI orchestrator (core/ai)

Single entry: `AiOrchestrator.run(capability, input, budget): AiResult`. Responsibilities: capability gate (pack present? device tier OK? battery/thermal OK? concurrency slot free?); runtime selection; budget enforcement (wall-clock, memory, tokens); cancellation; provenance capture; result validation (schema checks on LLM JSON, confidence floors on OCR); fallback triggering. The orchestrator is feature-agnostic and unit-tested with fake runtimes — features never touch a runtime directly (ADR leaf rule).

![AI stack: features → orchestrator → runtimes; model store side-loaded; device tiers and guarantees.](figures/fig-ai-stack.png)

## 16.5 Models and runtimes (pinned catalogue)

| Pack | Contents | Runtime | Size (approx) | Notes |
|---|---|---|---|---|
| Essentials | DBNet-lite det + CRNN rec (OCR, Latin); MobileNetV3 labels; MiniLM-L6 int8 embeddings | ONNX Runtime Mobile (NNAPI/CPU) | 18–25 MB | Tier C usable |
| Speech | whisper-tiny int8 (multi-core) with optional whisper-base int8 on Tier A | whisper.cpp JNI | 45–80 MB | 1× realtime on Tier B |
| Assistant | gemma-2B-it 4-bit (or Qwen2.5-1.5B-it 4-bit alternative, one pack format) | MediaPipe LLM Inference | 1.3–1.7 GB | Tier A only; warm-idle ≤ 40 s then evict |

Pack format: zip with `pack.json` (id, version, models[], sha256 per file, min-tier, license text), models under `models/`. Import: hash-verify → atomic move into `files/packs/<id>/<version>/` → registry row → enabled state. Pinned model versions are recorded in `core/ai/catalog.csv`; the pack manager displays them (§7.9).

## 16.6 Resource governance

| Tier | Max concurrent jobs | LLM context | Eviction | Battery gate |
|---|---|---|---|---|
| A | 2 (1 LLM) | 2 048 tok | LRU 40 s idle | none beyond Doze |
| B | 2 (no LLM) | — | LRU 20 s idle | defer > 30 s jobs on saver |
| C | 1 | — | immediate on background | defer all AI on saver except on-demand OCR tap |

Memory caps: embedder 80 MB, ASR 220 MB, OCR 150 MB, LLM 1.6 GB (A-only). Runtime `Debug.MemoryInfo` sampling asserts caps in instrumented tests (TC-AI-perf-*).

## 16.7 Fallback ladder (per capability)

- **OCR**: det+rec → rec-only line strips (det fail) → "crop manually" hint → manual text (module stays usable: F-059).
- **Semantic search**: cosine → FTS-only (silent downgrade, provenance row in diagnostics).
- **Summarize/rewrite (LLM)**: LLM → extractive (TextRank-ish, embeddings) → heuristic (first sentences/checklist regex) with a visible "basic result" tag.
- **Event parse**: LLM → regex/date-parser → manual editor pre-filled from text.
- **Transcribe**: whisper → (nothing; manual notes) — transcription is all-or-nothing but never blocks recording.
Every fallback is a tested path (TC-AI-fallback-*), not an aspiration.

## 16.8 Pack security and evaluation

Security: SHA-256 from `pack.json` re-hashed at every load; signature pinning optional (pack may carry an ed25519 signature verified against a key baked into the app — recommended for owner-distributed packs); zip guards (§14.1). Evaluation: before a pack version is marked *supported*, it must pass the offline eval kit (`tools/ai-eval/`): OCR ≥ 92% char-accuracy on the 40-image fixture set; ASR ≤ 12% WER on 20 fixture clips; LLM summarization ≥ 4/5 rubric on 20 fixture notes (rubric in-repo); embedding retrieval recall@10 ≥ 0.8 on the fixture corpus. Results are committed as JSON evidence — the same artifact style the owner's QA reports already use.

![Device capability ladder: always a subset, never a requirement.](figures/fig-ai-ladder.png)

## 16.9 What on-device AI will not do here

No generation of note content unprompted; no auto-sending, auto-filing, or auto-deleting; no model-initiated notifications; no personalization profiles; no fine-tuning on device (v1); no voice printing or speaker ID; no cloud fallback "just this once". These are promise-level negatives (P1/P2) and are enforced by review checklist §18.4.

## 16.10 Orchestrator API reference (core/ai)

| Signature | Purpose |
|---|---|
| `run(cap: Capability, input: AiInput, budget: Budget): AiResult` | single entry; never throws (Result) |
| `Availability.check(cap): Avail(packInstalled, tierOk, thermalOk, batteryOk, slotFree)` | UI gate for enabling rows + reason strings |
| `warm(cap, ttl)` / `evict(cap)` | Tier A LLM lifecycle |
| `register(packs: List<PackMeta>)` | called by pack manager after import/enable/disable |
| `provenance(result): Provenance` | model id, pack id/version, timings, fallback rung |
| Budget | wallMs, memCapMb, maxConcurrent, cancelToken |
| AiResult | Ok(payload, prov) | Degraded(payload, rung, prov) | Unavailable(reason) | Cancelled |

Feature modules depend only on this interface + `Availability` for UI state — fake implementations in `core/testing` make features fully testable without packs (G4 runs this way by design).

## 16.11 Per-capability integration specs (concise)

- **OCR**: input = page bitmap (≤ 960 px long edge normalized) → det boxes (conf ≥ 0.4) → rec per box (conf ≥ 0.55 floor, else line marked low-confidence) → reading-order merge (column-aware simple: sort by y then x with 0.6 line-height clustering) → `OcrPayload(lines, meanConf)`. UI: editable card; provenance footnote.
- **Embeddings**: input = note plainText first 2 000 chars → MiniLM int8 (seq 128, mean-pool, L2 norm) → f32[384] stored. Batched 16/batch on idle coroutine; rebuild tool in Diagnostics.
- **ASR**: input = 16 kHz mono PCM stream → whisper-tiny int8, language hint `en` (user-settable later), vad-trimmed segments; output segments `{startMs,endMs,text}` + mean log-prob; monotonic timestamps asserted.
- **LLM (Assistant pack)**: tasks = summarize (map-reduce over 1 500-token chunks, 5 bullets, JSON schema), rewrite (tone presets: shorter/formal/bullets), checklist-ify (extract actionable items JSON), event-parse (fields JSON). All prompts stored in `core/ai/prompts.yaml` with versioning; temperature 0.2; max output 512 tokens; JSON schema validated, retry once on schema fail, then fallback rung.
- **TTS**: system engine only; queue per note reading; speed follows music speed? no — separate setting default 1.0; graceful no-engine state (card, not error).

## 16.12 `core/ai/prompts.yaml` (initial content, normative)

```yaml
version: 1
defaults: {temperature: 0.2, max_output_tokens: 512, lang: en}
summarize:
  system: >
    You summarize personal notes for their author. Output 3-5 short bullets,
    each <= 15 words, preserving names, numbers and dates verbatim.
    Never invent facts. Output JSON: {"bullets": ["..."]}.
  user: "Summarize this note:
---
{body}"
rewrite:
  system: >
    You rewrite the user's note text in the requested style. Keep meaning,
    names and numbers. Do not add new facts. Keep language = input language.
    Output JSON: {"text": "..."}.
  user: "Style: {style}
Text:
---
{text}"
checklistify:
  system: >
    Extract actionable checklist items from the text. Keep the original
    wording where possible; one item per action; <= 20 items.
    Output JSON: {"items": [{"text": "...", "done": false}]}.
  user: "Text:
---
{body}"
event_parse:
  system: >
    Extract one calendar event from the text. The reference time is
    {now_local} ({tz}). Resolve relative dates ("tomorrow", "next Friday").
    If a field is unknown, omit it. Output JSON:
    {"title": "...", "start": "YYYY-MM-DDTHH:MM", "duration_min": n,
     "all_day": bool, "repeat": null}.
  user: "Text: {text}"
json_retry: 1      # on schema failure, re-ask once with the error, then fall back
```

Prompt changes are versioned with eval re-runs (§16.8); a prompt change without a green eval is revertible debt.

## 16.13 Capability × tier × power behavior matrix (normative)

| Capability | Tier C | Tier B | Tier A | Battery saver (any tier) |
|---|---|---|---|---|
| OCR scan tap | allowed, ≤ 6 s budget | ≤ 2.5 s | ≤ 2 s | allowed (user-initiated) |
| OCR auto-batch | deferred to charge | allowed | allowed | deferred with chip |
| Embeddings write-time | off (batch on idle) | batched | batched | off until charge |
| Semantic search | off silently | on | on + LLM rerank v1.1 | off silently (provenance row) |
| ASR transcribe tap | allowed ≤ 2× RT | ≤ 1× RT | ≤ 1× RT | allowed (user-initiated) |
| LLM summarize/rewrite/parse | unavailable row | unavailable row | allowed, warm ≤ 40 s | one-shot allowed, warm disabled |
| TTS read aloud | system engine | system | system | allowed |
| Warm eviction | immediate on background | 20 s idle | 40 s idle | immediate |

The matrix is encoded in `core/ai/TierPolicy.kt` as data (not scattered ifs) and unit-tested as a table — the orchestrator's `Availability.check` reads exactly this policy.

## 16.14 Pack distribution README (ships beside packs)

```
MySpace One — AI model packs (side-loaded, offline)
1. Download the .mspack file (this repo's releases) — check the SHA-256 beside it.
2. In the app: Diagnostics → Model packs → Import → pick the file.
3. Status shows "installed · SHA ✓". Enable per pack. Delete anytime.
Requirements per pack: Essentials any device; Speech 4 GB+ RAM; Assistant 8 GB+ RAM.
Never download packs from other sources: the app verifies hashes, and signed packs verify signatures too.
```

## 16.15 Sample AI outputs (calibration fixtures, abbreviated)

| Capability | Input | Output (verified shape) |
|---|---|---|
| OCR | fixture `inv-007.png` | `{"lines": [{"t": "INVOICE #118", "conf": 0.97}, {"t": "2 x USB-C cable 1,350", "conf": 0.93}], "meanConf": 0.94}` |
| ASR | fixture `clip-011.wav` | segments `[{s:0,e:4120,t:"please review the invoice"}, …]`, lang `en` |
| Summarize | fixture note `field-survey` | `{"bullets": ["Survey covered plots 12-18", "Soil samples due Friday", "Budget approved 45k"]}` |
| Checklist-ify | groceries paragraph | `{"items": [{"text": "Milk", "done": false}, …]}` |
| Event parse | "lunch with Ravi tomorrow 1 pm" (now=27 Oct 13:36 IST) | `{"title": "Lunch with Ravi", "start": "2026-10-28T13:00", "duration_min": 60, "all_day": false, "repeat": null}` |

Every sample is also a fixed eval case — drift in output shape/quality fails the eval kit, not a user's afternoon.

## 16.16 Pack-of-record provenance block (About → packs detail)

```
essentials 1.2.0 · installed 2026-10-28 · sha256 5c1f…
  models: det.onnx (DBNet-lite) · rec.onnx (CRNN en) · minilm.int8.onnx
  eval: char-acc 94.1% (threshold 92) · retrieval recall@10 0.86 (0.8) · PASS
speech 1.1.0 · eval WER 9.8% (12) · PASS
assistant 1.0.2 · eval rubric 4.4/5 (4) · schema discipline 100% · PASS
```

## 16.17 Summarize flow — numbered orchestrator sequence

1. User taps `Summarize` on note → feature calls `Availability.check(SUMMARIZE)`.
2. Gate result drives UI: enabled / reason ("Assistant pack needs an 8 GB device").
3. Enabled → `run(SUMMARIZE, {body}, budget(wall=20s, mem=1.6GB))`; UI shows running + cancel.
4. Orchestrator: tier/battery/concurrency checks → load LLM (warm or cold, evict timer reset).
5. Chunk body ≤ 1 500 tokens → per-chunk summarize → reduce to 5 bullets (2 LLM calls max).
6. Validate JSON schema; on fail retry once with error; on second fail → extractive fallback (rung 2, visible tag).
7. Provenance captured (model, pack, rungs, ms, tokens) → payload to feature.
8. UI renders preview card (Apply / Edit / Discard); Apply writes block + provenance footnote + undo anchor.
9. Every step's outcome appended to the diag ring AI record (§28.2).
