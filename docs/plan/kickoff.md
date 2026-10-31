# Draft execution work order — MySpace One v1.0 (for the AI build agent)

> **Status: DRAFT — pending owner G0 acceptance.** This file is the agent's entry point.
> It turns the blueprint (`docs/blueprint/myspace-one-development-blueprint.pdf`, v1.1)
> into the first working session. Nothing here overrides the blueprint; where this file
> and the blueprint differ, the blueprint wins (record a ledger entry about the conflict).

## 0. Who this is for and what "go" means

- **Executor:** an autonomous AI build agent with shell, editor, git, CI and emulator access.
- **"Go" condition:** the owner replies with blueprint acceptance (or corrections). Until
  then this package stays a draft; the agent may pre-stage G1 scaffolding locally but must
  not treat anything as approved.
- **First act on "go":** mark G0 closed in `reports/gates/G0.md` with the acceptance date,
  then start Day 1 of the bootstrap sprint below.

## 1. Mission in one line

Build `myspace-one` (full) and `mycalc` (flavor) release APKs that satisfy S1–S8
(blueprint front matter), through gates G0–G8, with evidence at every step.

## 2. Rules of engagement (the ten you can never break)

| # | Rule | Blueprint anchor |
|---|---|---|
| 1 | No internet permission, no network classes, ever | §1.3 C1, §14.2 |
| 2 | No sign-in, no accounts, no identity | §1.3 C2 |
| 3 | No ads / tracking / analytics SDKs | §1.3 C3, §24.4 |
| 4 | User data stays app-private or user-granted SAF | §1.3 C4 |
| 5 | AI = side-loaded packs, SHA-verified, never downloaded | §1.3 C5, §16 |
| 6 | minSdk 26; must be excellent on Tier C | §1.3 C6, §3.2 |
| 7 | Calculator parity set is release-blocking | §1.3 C7, §20.6 |
| 8 | ≤ 3 parallel runners, ≤ 30 jobs per pipeline | §1.3 C8 |
| 9 | mycalc flavor shares the codebase; zero module remnants | §1.3 C9, §23.4 |
| 10 | Every claim carries provenance (commit, run id, SHA) | §1.3 C10 |

Plus the working rules: never commit red; never push to protected branches; BLOCKED is
never FAIL and never silently skipped (§15.6); every task row cites binding spec + evidence
paths (§15.3); decisions not dictated by the blueprint go to `decisions.md` first (§15.7).

## 3. Reading order (30 minutes, before touching code)

1. Blueprint **Executive summary** + **Chapter 1** (promises, constraints).
2. **Chapter 15** (methodology: operating loop, task graph, gates, blocked work).
3. **Chapter 19** (lifecycle: your phase table and budgets).
4. **Appendix W** (quick-start) and **Appendix II** (the G1 sprint, day by day).
5. Skim **Appendix Q/R** (how acceptance will be proven later).

Load-on-phase thereafter: re-read the phase's chapters at each gate entry (§15.4).

## 4. Working files (this package)

| File | Purpose | Rule |
|---|---|---|
| `docs/plan/task-graph.yaml` | the single source of scheduling truth | update statuses in the same commit as the work |
| `docs/plan/decisions.md` | append-only decision ledger | new id per decision; never edit old entries |
| `docs/plan/sessions.md` | session log (Appendix L template) | one block per session, ends with "Next:" |
| `qa/testcases.csv` | generated test catalogue (source: blueprint Appendix A + §9.12 + §20.6) | regenerate with `tools/traceability.py --emit`; never hand-edit |
| `reports/gates/G0.md` | G0 gate report | currently DRAFT; close on owner acceptance |

## 5. Environment bootstrap (Day 0, before the sprint)

```bash
# one-time toolchain (pinned per §23.1)
sdkmanager "platform-tools" "emulator" "platforms;android-36" "build-tools;36.0.0" \
  "system-images;android-26;google_apis;x86_64" \
  "system-images;android-33;google_apis;x86_64" \
  "system-images;android-35;google_apis;x86_64"
avdmanager create avd -n e33b -k "system-images;android-33;google_apis;x86_64" -d pixel_4

# workspace sanity (first G1 task creates these files)
./gradlew help            # after T-BOOT-001
./gradlew assembleFullDebug assembleMycalcDebug   # after T-BOOT-002
python3 tools/traceability.py --check             # catalogue invariants (report mode in draft)
```

If any tool is unavailable in your sandbox, record it BLOCKED in the session log with the
exact command and error — do not substitute silently.

## 6. First sprint — G1 bootstrap (8 tasks, 8 working days)

Full task rows live in `task-graph.yaml`; the day plan is Appendix II of the blueprint:

| Day | Task | Done means |
|---|---|---|
| 1 | T-BOOT-001 workspace | `gradle help` green; version catalog resolves |
| 2 | T-BOOT-002 flavors | both debug flavors assemble; namespaces correct |
| 3 | T-BOOT-003 CI fast lane | PR lane green ≤ 12 min |
| 4 | T-BOOT-004 empty hub | hub renders on e33b; first screenshot golden |
| 5 | T-BOOT-005 provenance | BuildConfig SHA/time visible in a debug About row |
| 6 | T-BOOT-006 keystore | generated in secret store; owner backup receipt requested; rehearsal signs a test APK |
| 7 | T-BOOT-007 screenshot lane | Roborazzi runs in CI; diffs upload on failure |
| 8 | T-BOOT-008 G1 report | gate report committed with artifact paths |

After G1 closes: seed the G2 slice into the task graph at the next session start (§15.4),
not before, and not from memory.

## 7. What the agent must NOT do in draft state

- No production code before "go" (scaffolding experiments stay uncommitted or clearly `draft/`-scoped).
- No new dependencies (the catalog is frozen until G1; §23.5).
- No changes to `reports/` history (preservation standard, Appendix J).
- No rewrites of the blueprint PDF source without a ledger entry (docs-drift gate applies).

## 8. Definition of done for this draft package (G0 exit)

1. Owner acceptance recorded in `reports/gates/G0.md` (date + any corrections).
2. Task graph G1 slice fully specified with binding-spec + acceptance ids.
3. Test catalogue generated and invariant-checked.
4. Decision ledger + session log initialized.
5. Kickoff (this file) reviewed by the owner on request.

## 9. Owner actions requested (only these)

1. **Accept (or correct) the blueprint** — unlocks G0 → G1.
2. **Optional:** issue a read-only Figma REST token (§6.13 policy). Absence changes nothing.
3. **At G1 Day 6:** download and store the keystore backup offline; reply with the receipt.

Everything else is recorded, not asked.
