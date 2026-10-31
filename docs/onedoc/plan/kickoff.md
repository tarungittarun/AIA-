# OneDoc — Agent kickoff (work order, draft pending G0)

**Status: DRAFT — nothing in this package is approved until the owner accepts the OneDoc blueprint v1.0 (G0).** On acceptance: close `reports/onedoc/gates/G0.md`, record D-001, then execute T-G1-001.

## 0. The go condition

G0 closes when the owner accepts `docs/onedoc/blueprint/onedoc-development-blueprint.pdf` as the build contract. Until then this package is a draft: read it, verify it, do not build from it.

## 1. Rules of engagement (absolute)

1. Fully local/on-device: no sign-in, no internet permission, no ads, no trackers, no exceptions (blueprint C1–C5).
2. Android 8.0+ (API 26); phones and tablets; portrait and landscape (C6).
3. Editor laws L1–L10 and journeys J1–J5 are release blockers (§13, §27).
4. Prove on the artifact: source tests help, only direct-APK QA passes ship (§21.1).
5. CI budgets: ≤ 3 parallel runners, ≤ 30 jobs/run (C8); publisher green ≠ QA pass (§22.3).
6. BLOCKED discipline: never a product verdict; log, retry, never fake (§21.2).
7. Preserve the predecessor program's artifacts under `reports/` and `qa/` — read-only history (defect tracker, v3.12.x regressions).
8. Ledgers always: D-nnn decisions, S-nnn sessions, gate reports (§29.2).
9. Traceability green after any catalogue change: `tools/onedoc/traceability.py --check --strict`.
10. Work only on the session branch; incremental commits; no history rewrites.

## 2. Reading order (first 30 minutes)

Blueprint Part XII §29 (loop) → Part I (charter) → Part X §21–22 (quality/CI) → Part V §13 (laws) → Appendix D (gate DoDs). Then Appendix N (environment) before T-G1-001.

## 3. Environment bootstrap (Day 0)

Follow Appendix N.1–N.3 verbatim: JDK 17, SDK 36, build-tools 36.0.0, AVDs `od-api26/33/35/36`, golden boot snapshots. Recreate the tool venv after any sandbox restore: `python3 -m venv .venv && .venv/bin/pip -q install reportlab pypdf pillow matplotlib pymupdf pyyaml`.

## 4. First sprint (G1 = T-G1-001…005)

| Day | Tasks |
|---|---|
| 1 | T-G1-001 environment; T-G1-002 Gradle skeleton assembling both flavors |
| 2 | T-G1-003 CI pr.yml green within budgets; T-G1-004 shell app (home empty-state, settings stub, About) |
| 3 | T-G1-005 qa-driver skeleton + AVD snapshots; close G1 with DoD evidence |

## 5. Working files

| File | Role |
|---|---|
| `docs/onedoc/plan/task-graph.yaml` | seeded graph (47 tasks) — statuses move, ids never change |
| `docs/onedoc/plan/decisions.md` | append-only decision ledger |
| `docs/onedoc/plan/sessions.md` | append-only session log |
| `reports/onedoc/gates/G0.md` | gate report (draft; closes on acceptance) |
| `tools/onedoc/traceability.py` | catalogue generator + invariant checks |
| `qa/onedoc/testcases.csv` | generated catalogue (regenerate, never hand-edit) |

## 6. Not-to-do while in draft

No toolchain installs, no repository restructuring, no CI edits, no app code — G0 pending means reading and verifying only.

## 7. G0 exit checklist

- [ ] Owner acceptance recorded in `reports/onedoc/gates/G0.md` (verdict CLOSED, date, evidence)
- [ ] D-001 appended (decision: charter accepted)
- [ ] S-001 session block written
- [ ] `traceability.py --check --strict` exit 0

## 8. Owner actions

1. Accept the blueprint (reply "go" — that acceptance is the G0 evidence).
2. Optional: a Figma personal-access token for the nightly registry-drift check (§7.4) — the agent proceeds without it.
3. Day-6 (G8 prep): the release keystore — an RC keystore covers everything until then (§26.1).
