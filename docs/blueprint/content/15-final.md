# Quick reference card

The whole program on two spreads — print this page and the next; they are the daily working surface for both the agent and the owner.

## The five promises and ten constraints (from Chapters 1)

| Promise | One-line test |
|---|---|
| P1 Works everywhere, always | airplane mode cold start, Tier C, first run — all green |
| P2 Private by architecture | no INTERNET permission, no network classes in dex |
| P3 One home, zero friction | every screen ≤ 2 taps; one design system |
| P4 Fast and gentle | hub ≤ 1.2 s cold; no jank; no surprise notifications |
| P5 Built to be verified | every claim has an artifact path |

| Constraint | Guard |
|---|---|
| C1 no internet permission | manifest-audit CI gate |
| C2 no sign-in | checklist + code audit |
| C3 no ads/tracking SDKs | dependency deny-list |
| C4 data stays private/SAF | TC-SEC-* |
| C5 packs side-loaded, hashed | TC-PACK-sec-01 |
| C6 Android 8.0+ (API 26) | E26C in matrix |
| C7 calculator parity is blocking | Catalogue-0 |
| C8 ≤ 30 jobs, ≤ 3 runners | CI config + metrics |
| C9 MyCalc flavor from same code | flavor gates |
| C10 provenance everywhere | S-criteria artifacts |

## Command cheat sheet

| Task | Command |
|---|---|
| Regenerate figures | `python tools/blueprint/figures.py` |
| Rebuild this PDF | `python tools/blueprint/build_pdf.py --content docs/blueprint/content --out docs/blueprint/myspace-one-development-blueprint.pdf` |
| Fast local checks | `./gradlew spotlessCheck detekt testDebugUnitTest` |
| Full local suite | `./gradlew test robolectricSuite roborazziVerify` |
| Device journeys | `./gradlew connectedShadedDebugAndroidTest` |
| Black-box QA (any APK) | `python3 qa/harness.py --profile release --apk <file> --pin-sha <sha>` |
| Traceability | `python3 tools/traceability.py --check` |
| Audits | `python3 tools/audits.py manifest dependencies docs-drift` |
| Verify a bundle | `python3 tools/verify_manifest.py releases/v<ver>/` |

## Where everything lives

| Want | Go to |
|---|---|
| Product identity & constraints | Part I (Ch 1–3) |
| Screen behavior | Part II (Ch 7 + wireframes) |
| Feature list with acceptance | Part III (Ch 9) |
| Architecture / data / security | Part IV (Ch 11–14) |
| Agent rules & gates | Part V (Ch 15) + Part VII (Ch 18–19) |
| AI models, packs, fallbacks | Part V (Ch 16) |
| Engine grammar, RRULE, services, settings | Part VI (Ch 17) |
| Tests and harness | Part VIII (Ch 20–22) |
| Build, CI, release, ops | Part IX (Ch 23–26) |
| Traceability, risks, glossary, sign-off | Part X (Ch 27–32) |
| Step-by-step scripts | Appendices Q, R, Y |
| Task/defect/decision templates | Appendix L |

## The program in one sentence each

- **Build**: one Kotlin/Compose codebase, two flavors, six layers, one design system.
- **Data**: one Room DB + DataStore + private files; backups are portable encrypted zips.
- **AI**: three side-loaded packs behind one orchestrator; features never touch runtimes.
- **Test**: five layers, evidence always, BLOCKED honest, Catalogue-0 blocks releases.
- **Ship**: reproducible signed APKs with manifests, PDFs of record, and provenance in the About screen.
- **Operate**: Diagnostics is support; the ledger is memory; the blueprint is law.

<!-- pagebreak -->

# Closure

This blueprint set out to do one unusual thing: hand an autonomous agent the complete, unambiguous, testable definition of a real product — a private, offline, combined tool that respects its user absolutely — together with the working method that keeps such an agent honest over a long build. Every chapter serves that single goal. The agent that executes it will make thousands of small decisions; the constraint tables, the acceptance criteria, the harness contract and the ledger discipline exist so that every one of those decisions lands in the same place this page does: **provable, reproducible, and owned.**

When the final gate report is signed, the measure of success is simple: the owner installs one APK on an offline phone, and everything — calculation, notes, scans, plans, files, music, recordings, diagnostics, and the quiet intelligence of on-device models — simply works. Nothing more was promised; nothing less will ship.

<!-- pagebreak -->

# Phase-gate checklist card

Print or keep open during execution; a gate closes only when every box has an artifact path written next to it.

## G0 Inception
- [ ] Blueprint accepted by owner (this PDF, version recorded)
- [ ] Task graph seeded for G1 (`docs/plan/task-graph.yaml`)
- [ ] Decision ledger file created (`docs/plan/decisions.md`)

## G1 Bootstrap
- [ ] Both flavors assemble (full + mycalc, debug)
- [ ] Empty hub renders on E33B emulator (screenshot evidence)
- [ ] CI fast lane green (build + lint + unit, ≤ 12 min)
- [ ] Keystore generated; owner backup receipt; restore rehearsal signed test APK
- [ ] Screenshot harness records first golden
- [ ] G1 gate report committed

## G2 Foundations
- [ ] Token table + token unit test (Kotlin == tokens.csv)
- [ ] Design-system components with screenshot goldens (light/dark)
- [ ] Room v1 schema + exported-schema tests + DAO tests
- [ ] Settings registry + RestoreKeys
- [ ] Architecture tests active in fast lane (Konsist-style)
- [ ] G2 gate report committed

## G3 Calculator
- [ ] Engine: §17.1 normative tables implemented; laws L1–L10 green (10k cases/law)
- [ ] Catalogue-0 CALC cases TC-ONE-C-001…026 green (L4)
- [ ] Flavor parity J-09 green; mycalc dex has zero module classes
- [ ] Perf: keystroke→frame ≤ 16 ms; cold start ≤ 0.8 s (flavor)
- [ ] L5 calculator campaign on dist APK: results JSON + screenshots + manifest
- [ ] G3 gate report committed

## G4 Modules
- [ ] Notes / Scanner / Calendar / Files / Music / Recorder / Hub P0 sets green
- [ ] Journeys J-01…J-10 green (AI mocked)
- [ ] Edge registers (§7.14) covered in L1/L2/L4
- [ ] Storage-full drill J-10 green
- [ ] G4 gate report committed

## G5 On-device AI
- [ ] Pack manager lifecycle + hash gates (TC-PACK-*)
- [ ] OCR / ASR / embeddings / LLM acceptance per §16.5 on tier profiles
- [ ] Fallback ladder rungs forced and asserted (TC-AI-fallback-*)
- [ ] Eval kit thresholds met for pinned pack versions (JSON evidence)
- [ ] Features green with packs absent (structural optionality)
- [ ] G5 gate report committed

## G6 Hardening
- [ ] TC-A11Y-* battery green; TalkBack journeys
- [ ] Perf budgets §23.6 + feel budgets §7.18 on Tier B/C profiles
- [ ] Security checklist SC-01…SC-12 verified
- [ ] String/copy audits (UX-015; microcopy dictionary exact)
- [ ] Battery/Doze + rotation + death-storm suites green
- [ ] G6 gate report committed

## G7 Release
- [ ] S1–S8 all true on the exact release artifacts
- [ ] Reproducible double-build SHA match
- [ ] L5 release-candidate profile green (both flavors, airplane-mode profile included)
- [ ] Evidence bundle manifest verified; PDF of record built
- [ ] Docs regenerated (blueprint, traceability, licenses, api-surface)
- [ ] Owner walkthrough §32 accepted; sign-off record filled
- [ ] Release published per §25.5 with RELEASE-NOTES

## G8 Operate
- [ ] v1.1 backlog seeded (P2 + ledger wishes)
- [ ] Defect ledger triaged; runbook committed
- [ ] Maintenance calendar scheduled (§29.8)
- [ ] G8 gate report committed
