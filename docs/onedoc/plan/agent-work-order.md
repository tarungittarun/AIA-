# MASTER WORK ORDER — OneDoc v1.0 — for the autonomous AI build agent

You are the sole developer of OneDoc. This document is your complete operating manual: the goal, the rules, where every answer lives, how to decide when in doubt, how to prove your work, and exactly how to deliver. Everything referenced here exists in the repository or is a direct section of the blueprint PDF. If this work order and the blueprint ever disagree, the blueprint wins; if the blueprint is silent, follow its §1.5 defaults.

---

## 0. THE GOAL (memorize this)

**MAIN GOAL — one sentence:**
Build and deliver **OneDoc v1.0** (`app.onedoc`) — a fully offline, Word/Google-Docs-class document studio for Android 8.0+ — as a **release-quality, fully tested, signed APK**, together with machine-verifiable proof that every promised feature works on that exact APK.

**The goal is achieved ONLY when ALL of the following are true (final acceptance checklist):**

1. A signed release APK of OneDoc exists and installs on Android 8.0+ (phones and tablets).
2. Every P0 feature in the catalogue (blueprint Appendix A, 48 P0 features) passes its test cases **on the release APK** across the emulator matrix (API 26/33/35/36).
3. All five acceptance journeys (J1–J5, blueprint §27) pass end-to-end on the release APK.
4. All ten editor laws (§13) and all property tests P1–P10 (§16) are green.
5. Performance budgets hold (cold start < 1.2 s, typing P95 < 50 ms, search < 300 ms, APK ≤ 25 MB — §21.4).
6. Security proofs hold: zero internet permission, zero network sockets at runtime, exact permission set, no ads/trackers (§20, C1–C5).
7. No open S1/S2 defects; the defect tracker's final state is committed.
8. The evidence PDF exists (embedded screenshots, per-case PASS/FAIL/BLOCKED, budget actuals, provenance) and is committed.
9. All gates G0–G8 are closed with DoD evidence in `reports/onedoc/gates/`.
10. The owner can verify everything alone in 5 minutes using the provenance bundle (§28.5).

**What the goal is NOT (do not fool yourself):**
- NOT "the source compiles and unit tests pass" — source tests are aids; only the distributed APK is proof (§21.1).
- NOT a prototype or demo — it is a shippable product with a defect process.
- NOT "mostly works" — a feature without a passing test is unverified, and unverified equals not done (P5).
- NOT an app that needs the internet for anything, ever — 100% of value in airplane mode (P1).

---

## 1. THE PRODUCT IN ONE MINUTE

OneDoc is a **brand-new app** (no predecessor code): a document studio where a single user writes, structures, formats, scans-to-text, dictates, listens, and exports documents — entirely on one phone, with no account, no internet permission, no ads, no trackers, no exceptions.

- **Identity:** `app.onedoc` · minSdk 26 (Android 8.0+) · phones + tablets · portrait + landscape.
- **Core:** a block-based rich-text editor (13 block kinds, 7 mark types, IME-safe, honest undo) with a library (trash, versions, stars, full-text + semantic search), 12 templates, find & replace with pre-edit versioning, tables/images/TOC/footnotes, reader mode with text-to-speech.
- **Files:** export/import PDF, DOCX, Markdown, HTML, TXT, native `.odoc` — always with a *declared fidelity level* and a conversion note; it refuses rather than guesses.
- **AI (all on-device, optional packs side-loaded by the owner, never downloaded):** scan-to-doc OCR, dictation, writing assistant (Summarize / Rewrite / Continue / Fix via explicit preview cards), semantic search, read-aloud. Device tiers A/B/C with a strict fallback ladder; unavailable AI hides with a one-line reason.
- **Durability:** journal + snapshots make keystroke loss impossible (Law L3: zero loss under process kill).
- **Privacy:** structural — there is no network path in the app at all.

---

## 2. WHERE EVERY ANSWER LIVES (doubt-resolution map)

When you have a question, find the row and read the named source **before** improvising. The blueprint PDF: `docs/onedoc/blueprint/onedoc-development-blueprint.pdf` — online: https://github.com/tarungittarun/AIA-/blob/arena/e4dfeee3-aia/docs/onedoc/blueprint/onedoc-development-blueprint.pdf · direct download: https://github.com/tarungittarun/AIA-/raw/arena/e4dfeee3-aia/docs/onedoc/blueprint/onedoc-development-blueprint.pdf

| Your question / doubt | Go to (exact source) |
|---|---|
| "What exactly am I building? What is the full feature list?" | Blueprint §4 (prose) + **Appendix A** (machine table F-001…F-090 with priorities and test bindings) |
| "What does 'easy UX' mean concretely?" | §5 (UX-01…UX-50 acceptance criteria with numbers) + Appendix AL (how each is auto-verified) |
| "How should a screen look and behave?" | §6 (design tokens/themes), §8 (wireframes + surface tables), `docs/onedoc/blueprint/ui-screens.csv` (22 screens: states, redlines), `design/onedoc-figma/tokens.json` (exact values) |
| "How does the editor engine work? How do I make text editing correct?" | §13 (ten laws L1–L10), §14 (document model, marks semantics §14.5, rendering stack §14.6, memory playbook §14.7), §15 (IME contract, fuzzer §15.3, selection §15.6), §16 (property tests) |
| "How should feature X (tables/images/TOC/search/reader) behave?" | §17 (per-feature engineering contracts) + the feature's F-row bindings |
| "How do file import/export work? What fidelity do I promise?" | §18 (fidelity matrix F0–F3, writer/reader specs §18.10–11, worked examples §18.12, PDF internals §18.13, goldens §18.9) |
| "How does the on-device AI work? What prompts do I use?" | §19 (pipelines §19.12, ladder §19.4, pack format §19.11, budgets §19.8, **verbatim prompts §19.10**, model cards §19.13, edge matrix §19.15) |
| "What are the security/privacy requirements?" | §20 (threat model, structural proofs, permission ledger §20.5) + Appendix X (compliance map) |
| "How do I test? What does PASS/FAIL/BLOCKED mean?" | §21 (verdicts §21.2, budgets §21.4, gates §21.5), §23 (emulator matrix), §24 (direct-APK pipeline, evidence PDF §24.4, procedures §24.5, log format §24.9), Appendix C/I (142 cases + given/when/then), Appendix U (run manifest), Appendix V (test fixtures + oracles) |
| "How do I set up CI? What are the job limits?" | §22 (pipelines, budgets C8: ≤3 runners, ≤30 jobs, quota math §22.5, secrets §22.6) |
| "How do I build? Gradle, flavors, signing, versioning?" | §26 (topology, flavors, versioning, size gate, dev scripts §26.7) + Appendix E/F (environment and dependency pins) |
| "How do I run the emulators / drive the APK?" | **Appendix N** (verbatim bootstrap, AVD creation, boot ritual, install+drive commands) |
| "What is 'done' for my current task/gate?" | `docs/onedoc/plan/task-graph.yaml` (task DoD) + **Appendix D** (gate DoDs) + Appendix Y (task plan) |
| "How do I release? What exactly do I hand over?" | §27 (journeys), §28 (release checklist §28.1, provenance §28.2, handoff note §28.4, release-day script §28.6, owner verification §28.5) + Appendix M (release-notes template) |
| "How should I work day to day? How do I decide? What if I'm blocked?" | §29 (reading order, ledgers, ambiguity ladder §29.4, PR checklist §29.5, daily loop §29.7, asking the owner §29.8, never-do list §29.9) |
| "Is feature X allowed?" | §1.4 (permanently out of scope — if listed there, the answer is NO, always) + constraints C1–C10 (§1.3) |
| "Two requirements conflict — which wins?" | Promise ranking §1.2 (P1 beats P3, P2 beats P4, laws beat features §13.2) |
| "What's the exact JSON schema of a document?" | §14.2 + **Appendix AN** (field tables) |
| "What strings/copy do I write in the UI?" | **Appendix P/AF** (normative strings — never invent copy; keys only in code) + Appendix AD (hi/mr) |
| "What error messages exist?" | §18.8 + **Appendix Q** (complete error catalogue — if your error is not there, add it via a D-nnn decision) |
| "What gestures does the app support?" | **Appendix R** (gesture map with a11y equivalents) |
| "How do I handle corrupt files / disk full / weird states?" | §11.8 (corruption drills) + §10.5 (error strategy) |
| "What test data do I use?" | **Appendix J** (fixture corpus — committed, synthetic, reproducible) + Appendix V (expected outputs) |
| "What A11y behavior exactly?" | §9 (annotations, focus order §9.3, announcements §9.4) + Appendix W (per-screen traversal contracts) |
| "How does Figma fit in? Do I need a Figma account?" | §7 (workflow, registry contract) + `design/onedoc-figma/README.md` — **you never need Figma access to progress**; build from the CSV registry + tokens.json |
| "How do I trace requirements to tests?" | Run `./.venv/bin/python tools/onedoc/traceability.py --check --strict` — must exit 0 (90 features, 48 P0, 50 UX, 142 cases) |
| "What has already been decided?" | `docs/onedoc/plan/decisions.md` (append-only ledger) |
| "What happened in past sessions?" | `docs/onedoc/plan/sessions.md` |
| "What is the task order right now?" | `docs/onedoc/plan/task-graph.yaml` (47 seeded tasks) |
| "What was learned from the OLD calculator program?" | `reports/` (read-only history): the BLOCKED doctrine, publisher-vs-QA separation, and defect discipline all come from there and are codified in §21–25 — do not modify those files |

---

## 3. NON-NEGOTIABLE RULES (violating any of these fails the whole program)

1. **No internet, ever:** no `INTERNET`/`ACCESS_NETWORK_STATE` permission, no account, no sign-in, no ads, no trackers, no analytics, no WebView rendering, no downloads — the app never opens a socket (C1–C5). A task proposing otherwise is invalid.
2. **Android 8.0+ (API 26)** minimum; phones and tablets; portrait and landscape (C6).
3. **Laws and journeys are release blockers:** L1–L10 (§13) and J1–J5 (§27) must pass on the release APK. A red law blocks shipping regardless of everything else green.
4. **Prove on the artifact:** QA verdicts about shipping come only from installing the built release APK on emulators and driving its real UI (§21.1, §24). Source-level green is supporting evidence, never proof.
5. **CI budgets:** max 3 parallel runners, ≤ 30 jobs per run (C8). Publisher/report jobs run `if: always()`; a green publisher is NOT a passing QA result.
6. **BLOCKED discipline:** if the emulator/accessibility/input layer prevents a fair assertion, record BLOCKED with reason + environment fingerprint. BLOCKED is never a product defect and never a PASS. Re-try every cycle. Never fake a result either direction (§21.2).
7. **Privacy claims need proof:** "no ads / no network" is certified by manifest check + dependency deny-list + zero-socket runtime probe (TC-SEC-P-01/02/03), never by a UI scan.
8. **Traceability stays green:** after any catalogue/plan change run `tools/onedoc/traceability.py --check --strict` — exit 0 required. The CSV is generated, never hand-edited.
9. **Append-only ledgers:** never edit or delete `decisions.md` entries, `sessions.md` blocks, closed gate reports, or the predecessor's files under `reports/` and `qa/`. New insight = new entry.
10. **Git discipline:** work only on branch `arena/e4dfeee3-aia`; commit incrementally after every meaningful step; NEVER rebase, force-push, or rewrite history.
11. **No silent mutations:** nothing (AI, importer, migration, restore) may alter document content without a visible, undoable, versioned operation (Law L10). AI output enters a document only via preview card + explicit insert.
12. **Tokens and keys only:** no hardcoded colors/sizes in UI (DQ-1); no literal user-facing strings in code (strings catalog, Appendix P/AF); errors only from the taxonomy (Appendix Q).
13. **Every fix ships with the test that failed first.** No test, no fix (§25.2).
14. **Every artifact carries provenance:** commit SHA, workflow run URL, APK SHA-256 (C10).

---

## 4. ENVIRONMENT SETUP (Day 0 — run verbatim, full details Appendix N)

```bash
# Java + Android SDK (pins: Appendix E)
sudo apt-get update && sudo apt-get install -y openjdk-17-jdk
mkdir -p $HOME/android-sdk/cmdline-tools
curl -o /tmp/cmdtools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q /tmp/cmdtools.zip -d $HOME/android-sdk/cmdline-tools
mv $HOME/android-sdk/cmdline-tools/cmdline-tools $HOME/android-sdk/cmdline-tools/latest
export ANDROID_HOME=$HOME/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator
yes | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-36" "build-tools;36.0.0" "emulator" \
  "system-images;android-26;google_apis;x86_64" "system-images;android-33;google_apis;x86_64" \
  "system-images;android-35;google_apis;x86_64" "system-images;android-36;google_apis;x86_64"
# AVDs (§23.1): od-api26 Pixel2 2GB · od-api33 Pixel4 3GB · od-api35 Pixel6 4GB · od-api36 Pixel8 8GB
echo no | avdmanager create avd -n od-api26 -k "system-images;android-26;google_apis;x86_64" -d pixel_2 --force
echo no | avdmanager create avd -n od-api33 -k "system-images;android-33;google_apis;x86_64" -d pixel_4 --force
echo no | avdmanager create avd -n od-api35 -k "system-images;android-35;google_apis;x86_64" -d pixel_6 --force
echo no | avdmanager create avd -n od-api36 -k "system-images;android-36;google_apis;x86_64" -d pixel_8 --force
# Python tooling for repo scripts (recreate after any machine restore)
python3 -m venv .venv && ./.venv/bin/pip -q install reportlab pypdf pillow matplotlib pymupdf pyyaml
```

Every QA run starts from clean app state: `adb uninstall app.onedoc || true` first — no run ever sees a previous run's data (§23.3).

---

## 5. HOW TO WORK (the operating loop)

**Reading order before any code (first 30 minutes):** Blueprint Part XII §29 → Part I (charter) → Part X §21–22 (quality/CI) → Part V §13 (laws) → Appendix D (gate DoDs). Then Appendix N before T-G1-001.

**Gate order:** G0 (owner acceptance) → G1 (toolchain+shell) → G2 (model+storage) → G3 (editor core) → G4 (rich features) → G5 (formats+IO) → G6 (on-device AI) → G7 (quality pass) → G8 (release). A gate closes only when every DoD item in Appendix D is checked with an evidence link committed to `reports/onedoc/gates/G<k>.md`. Never start a later gate with an open blocking gap.

**Task order:** follow `docs/onedoc/plan/task-graph.yaml` (47 seeded tasks with dependencies and DoDs; expand upcoming slices just-in-time). A task moves to `done` only with its evidence link in the file; `blocked(reason)` requires a reason and an unblock plan.

**Ledgers (append-only, always current):**
```markdown
### D-012 · 2026-11-02 · Adopt ONNX Runtime for OCR packs
Context: <why this decision now, alternatives considered>
Decision: <what was chosen, exact pin>
Consequences: <what this binds/blocks; budgets affected>
Reversal condition: <what would make us revisit>
```
```markdown
## S-007 · 2026-11-02 · G3 editor core
Goal: <what this session set out to do>
Done: <honest list with evidence paths>
Failed/Blocked: <what failed and why — especially this>
Next: <exact next steps>
```

**Daily loop (§29.7):** red nightly = first task of the day. Pull the top unblocked task. Write the test/procedure first where the type demands it (laws, formats, security). Small PRs (≤ ~400 changed lines excluding generated), self-review against the §29.5 checklist (laws→properties? UI→registry+DQ? formats→golden round-trip? schema→migration+D-nnn? perf→re-measure? catalogue→traceability green?). Update ledgers at decision time and session end. Never mark done without DoD evidence.

**Commit style:** frequent, small, imperative subject lines referencing task ids (e.g., `T-G3-004: marks engine + boundary semantics (TC-EDIT-005 green)`).

---

## 6. WHEN IN DOUBT — the decision ladder (apply in this exact order)

1. **Blueprint:** search the doubt map (§2 above) — the answer almost always exists (the PDF is written to be self-sufficient; its Appendix H.3 indexes every normative table).
2. **§1.5 defaults:** platform convention wins; simplest testable behavior wins; battery/RAM win; determinism wins; when ambiguous, choose the option closest to Google Docs/Keep/Files interaction patterns for that surface.
3. **Record it:** any non-trivial choice becomes a D-nnn entry in `docs/onedoc/plan/decisions.md` BEFORE the code lands.
4. **Smallest reversible option:** if two choices are defensible and consequential, pick the one that is easiest to reverse, and note the reopen condition in the D-nnn entry.
5. **Surface it:** list any decision awaiting owner review in the current gate report under "Decisions awaiting owner review".
6. **Truly hard-blocked** (missing tool, exhausted quota, broken environment, need owner material like the release keystore): mark tasks `blocked(reason)`, close everything closeable, and post ONE structured ask in the gate report — then continue with unblocked work. Never stall silently, never nag repeatedly, never invent scope to look busy. Ask format (§29.8):
```markdown
ASK-<n> (date, gate)
Need: <one sentence>
Options: A) <x — cost/risk> B) <y — cost/risk> C) do-nothing <consequence>
Recommendation: <option + why>
Workaround until answered: <what proceeds without this>
```

---

## 7. HOW TO TEST AND PROVE (verification discipline)

- **Four layers (§21.3):** JVM property/golden tests (seconds) → Robolectric (editor/journal) → instrumentation on API 26/33/35/36 → **direct-APK QA** (the proof that ships).
- **Verdicts (§21.2):** PASS = exercised and held · FAIL = exercised and broken (opens a defect) · BLOCKED = environment prevented a fair assertion (neither; log + retry). No other verdicts exist.
- **Direct-APK pipeline (§24, Appendix N.4):** build release APK → static gates (manifest permission set == §20.5 exactly, deny-list, size ≤ 25 MB) → install on clean emulators → drive real UI via accessibility ids (`od_*`) → per-case PASS/FAIL/BLOCKED + screenshots with corner stamps → publisher assembles the evidence PDF (§24.4 schema).
- **Anti-flake rules (§24.6):** assert on the accessibility tree, never pixels; wait for states, never sleep; pin seeds; flaky-once rerun, flaky-twice quarantine with a defect id.
- **Budgets are tests (§21.4):** cold start < 1.2 s · typing P95 < 50 ms · search < 300 ms · export 50-page PDF < 10 s · APK ≤ 25 MB. A breach is an S2 defect.
- **Evidence PDF (the owner's artifact):** cover with commit/run/SHA → verdict banner → journey strips with screenshots → full per-case table → performance actuals → BLOCKED register → defect summary → method appendix. Committed to `reports/`, linked from the release.

---

## 8. HOW TO DELIVER (the endgame, step by step)

1. **G7 (quality pass):** run the FULL catalogue + journeys J1–J5 on the release APK across the matrix; assemble the evidence PDF; security suite green; performance table green; zero open S1/S2; present the audit in the §21.8 order.
2. **G8 (release) — release checklist §28.1, in order:**
   a. Verify G7 evidence is green for the EXACT release SHA (same bytes you ship).
   b. Build `assembleFullRelease` (+AAB) — owner keystore when provided (owner delivers near Day-6; until then the RC keystore per §26.1; re-sign runbook §N.5 if the keystore arrives late).
   c. Static gates on the release artifact: manifest, deny-list, size, SBOM.
   d. Direct-APK QA smoke on the tag build (journeys + TC-SEC-P-03) — proves *this* artifact.
   e. Defect tracker final pass: no open S1/S2; S3 list accepted into release notes.
   f. Write release notes in the Appendix M voice (≤ 200 words, facts, Fixed lines cite tracker ids, "Honest notes" section mandatory) + handoff note (§28.4 template).
   g. Write `releases/<version>/provenance.json` (§28.2): version, versionCode, commit SHA, run id+URL, APK SHA-256+size, SBOM, catalogue version, tool versions.
   h. Tag `v<X.Y.Z>`; create the GitHub Release with APK + evidence PDF + provenance attached.
3. **Definition of delivered:** the owner can, in 5 minutes offline (§28.5): download the APK, recompute its SHA-256 and match it to provenance, install, run About→self-test (≤ 20 s), walk journey J1 (write→format→export PDF), and check the permission list. If any step fails, the release is not accepted.
4. **After release:** arm maintenance mode (§30.4) — nightlies continue; any rebuild re-runs the gates on that exact artifact; v1.1 shelf items (§30.2, Appendix AG) wait for an owner decision (D-R101…).

---

## 9. NEVER-DO LIST (each item has ended real programs — §29.9)

1. Never add a network permission, account, ad SDK, or telemetry — such tasks are invalid by charter (§1.3/§1.4), not negotiable.
2. Never rebase/force-push, edit closed gate reports, ledger rows, or the predecessor program's artifacts.
3. Never mark a gate/task done without its DoD evidence link.
4. Never write a user-visible string in code (keys only), a color literal in UI (tokens only), or an ad-hoc error message (taxonomy only).
5. Never let AI output enter a document without preview + explicit insert + pre-edit version (Law L10).
6. Never report a blocked gesture as FAIL — or as PASS (§21.2 cuts both ways).
7. Never make fidelity claims beyond §18.2 — state the level achieved.
8. Never bundle a model into the APK (C5) or fetch anything at runtime (C1).
9. Never ship a rebuild without re-running the gates on that exact artifact (§28.6).
10. Never "temporarily" disable a test to go green — quarantine with a defect id is the only honest path.

---

## 10. OWNER ACCEPTANCE ACT (G0)

This work order constitutes the owner's formal acceptance of "OneDoc · Application Development Blueprint v1.0" (200 pages, commit `2244cea`) as the build contract.

**Do this first, before anything else:** edit `reports/onedoc/gates/G0.md` — flip the PENDING row to PASS with today's date and this work order as evidence; set verdict CLOSED; append D-001 to `docs/onedoc/plan/decisions.md` ("G0 closed by owner acceptance in work order"); append S-001 to `sessions.md`; commit. Then begin §11.

---

## 11. FIRST ACTIONS (today, in order)

1. Clone: `git clone https://github.com/tarungittarun/AIA-.git && cd AIA- && git checkout arena/e4dfeee3-aia` (verify `git log -1` shows `2244cea` or later on this branch).
2. Read: blueprint Part XII, Part I, Part X §21–22, Part V §13, Appendix D, Appendix N, `docs/onedoc/plan/kickoff.md`.
3. Close G0 (§10 above).
4. Environment setup (§4 / Appendix N.1–N.3): JDK 17, SDK 36, four AVDs boot-verified, venv created.
5. T-G1-002: Gradle multi-module skeleton (§10.1 modules, `full` + `writer` flavors) with both flavors assembling empty-shell APKs; `app.onedoc` applicationId; versioning scheme (§26.3).
6. T-G1-003: CI `pr.yml` green with ≤ 8 jobs; budgets enforced (§22).
7. T-G1-004/005: shell app (home empty-state, settings stub, About) + qa-driver module skeleton; close G1 with DoD evidence.
8. Proceed to G2 (T-G2-001…005): `core-model`, property suite P1–P10, Room schema v3, journal + kill-trial harness, `.odoc` container + goldens.

Begin. The blueprint is your single source of truth; this document is your map of it.

---

## 12. ALL LINKS IN ONE PLACE

- Repository: https://github.com/tarungittarun/AIA- (clone: `https://github.com/tarungittarun/AIA-.git`)
- Branch: `arena/e4dfeee3-aia` (tip `2244cea`)
- Blueprint (view): https://github.com/tarungittarun/AIA-/blob/arena/e4dfeee3-aia/docs/onedoc/blueprint/onedoc-development-blueprint.pdf
- Blueprint (direct download): https://github.com/tarungittarun/AIA-/raw/arena/e4dfeee3-aia/docs/onedoc/blueprint/onedoc-development-blueprint.pdf
- Kickoff work order: `docs/onedoc/plan/kickoff.md`
- Task graph: `docs/onedoc/plan/task-graph.yaml` · Ledgers: `docs/onedoc/plan/decisions.md`, `docs/onedoc/plan/sessions.md`
- Gate G0 report: `reports/onedoc/gates/G0.md`
- Screen registry: `docs/onedoc/blueprint/ui-screens.csv` · Tokens: `design/onedoc-figma/tokens.json` (+ `README.md`)
- Test catalogue: `qa/onedoc/testcases.csv` · Checker: `tools/onedoc/traceability.py --check --strict`
- Plan sources (if the PDF must be rebuilt): `docs/onedoc/blueprint/content/` + command in blueprint §30.6
