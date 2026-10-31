@LEAD This blueprint is a complete, self-contained development instruction set for one Android application — **MySpace One** — that combines a calculator, notes, scanner, calendar, files manager, music player, voice recorder and diagnostics into a single install, with on-device artificial intelligence as an optional accelerator. It is written so that an autonomous AI build agent can execute the entire program — from an empty repository to a fully tested, signed, installable APK — without asking a human another question. Every requirement is testable, every stage has entry and exit criteria, and every artifact the agent must produce is named.

# Executive summary

**What.** One Android application — **MySpace One** — that combines Calculator, Notes, Scanner, Calendar, Files, Music, Recorder and Diagnostics behind a single icon, with an optional calculator-only flavor (**MyCalc**) built from the same code. **On-device AI** (OCR, transcription, summarization, semantic search via side-loaded model packs) accelerates features but is never required: every feature works fully offline with AI absent.

**The prime directive.** The app works **locally, on device, with no sign-in and no internet access — ever.** This is enforced structurally: the merged manifest contains no internet permission, the bytecode contains no network classes, and CI fails on any violation. No ads, no accounts, no telemetry — also structural.

**For whom.** Written for an **autonomous AI build agent** that executes the whole program — from empty repository to a fully tested, signed APK — using phase gates G0–G8, machine-checkable acceptance criteria, and evidence-first reporting in the style the owner's calculator QA already established: pinned APK SHAs, screenshot evidence, honest PASS/FAIL/BLOCKED states, and a PDF report of record. Publisher success is never conflated with passing results.

**How the document is organized.** Parts I–III fix identity, experience and features (84 features, each with acceptance criteria and tests). Parts IV–VI specify architecture, data, security, on-device AI and every engine behavior (the calculator language is specified to the grammar, with the owner's historical bugs — `5+ = → 5`, `0.9999999999`, `1e15+1 → Error` — structurally impossible). Parts VII–IX define the agent's methodology, testing, build and release. Part X–XII carry traceability, risks, glossaries and step-level appendices, including the owner's personal 15-minute acceptance manual.

**Definition of done for the program.** Eight criteria (S1–S8, front-matter table): release APKs install on API 26/33/35 in airplane mode; zero internet-class permissions; the release-blocking test catalogue green; the calculator law suite green (10 000+ randomized cases per law); every feature traced to tests and commits; static audits clean; APK size budgets met; documentation regenerated and archived with the release.

**Standing constraints honored.** Calculator-only QA focus discipline, ≤ 3 parallel CI runners and ≤ 30 jobs, preservation of historical reports, official-Google-Calculator-only comparisons (never substituted), and BLOCKED-never-FAIL honesty for gestures the test environment cannot fairly reproduce.

# About this blueprint

This document exists to remove ambiguity. It is not a brochure or a wish list; it is an operating contract between the product owner and the AI agent that will build the product. It defines what is being built, why, for whom, how it must behave, how it must be architected, how the agent must work, how everything is tested, and what "done" means at every level of granularity.

The document is long by design. A human reader does not need to read it linearly; an executing agent should treat it as its primary context source and re-read the relevant chapter before starting each phase. The table of contents carries bookmark links in the PDF outline for fast navigation.

## Who reads this document

- **Primary reader — the AI build agent.** The agent executes phases G0 through G8 (§15.5, §19). For the agent this document is binding: where the agent's intuition conflicts with this document, the document wins. Where the document is silent, the agent must follow the default rules in §1.5 and record the decision in the decision ledger (§15.7).
- **Secondary reader — the product owner.** A human who wants to verify that the product being built is the product they asked for. The owner reviews phase-gate evidence (§15.5) rather than the code itself.
- **Tertiary reader — future maintainers and auditors.** Chapters 12, 14, 20 and 23–26 are written so that a new engineer (human or AI) can understand the system years later without oral history.

## What this document commits to

1. **One installable APK** (plus an optional calculator-only flavor of the same codebase) that installs on Android 8.0+ and works with **no sign-in, no internet access, and no background network use**.
2. **Eight modules** — Calculator, Notes, Scanner, Calendar, Files, Music, Recorder, Diagnostics — plus a combined Home hub and Settings, specified to acceptance-test level in Chapters 8–10.
3. **On-device AI** that accelerates features (OCR, transcription, summarization, semantic search) but is never required for any feature to function (§16).
4. **A development methodology** purpose-built for an autonomous agent: phase gates, machine-checkable acceptance criteria, evidence artifacts, and a defect ledger (§15, §19–§20).
5. **A full quality and release pipeline**: unit, integration, screenshot, instrumented and black-box emulator testing; signing; distribution; and a maintenance plan (Chapters 20–26).

## How to read this document

- If you are **starting execution**: read Chapter 1 (mission), Chapter 15 (methodology) and Chapter 19 (lifecycle) first; then work phase by phase, re-reading the chapter cited by each task.
- If you are **reviewing scope**: read Chapters 1–3 (why and for whom), Chapters 8–10 (what the product does), Chapter 27 (traceability).
- If you are **reviewing engineering**: read Chapters 11–14 (architecture and data), Chapter 16 (AI), Chapters 20–26 (quality, build, release).
- If you are **testing**: Chapters 8–10 give behavior, Chapter 20 gives the test case catalogue, Chapter 22 gives the harness contract, and Chapter 27 maps everything together.

### Document conventions

- **§** denotes a section reference inside this document (e.g., §12.4 is Data architecture, section 4).
- **SHALL / MUST** denote a binding requirement; **SHOULD** denotes a strong default that may be overridden with a recorded decision; **MAY** denotes an explicit option.
- **TC-XXX-nnn** identifies a test case (Chapter 20). **F-nnn** identifies a feature requirement (Chapter 9). **R-nnn** identifies a risk (Chapter 30). **D-nnn** identifies a decision-ledger entry template.
- **Code font** denotes literal identifiers — file names, class names, SQL, commands.
- Every figure has a caption and is referenced from at least one section.
- Word counts are deliberately uneven: specification-dense chapters (8, 9, 17, 20) run much longer than rationale chapters.

## Scope: in and out

In scope — the complete lifecycle:

1. Inception and scope agreement (this document, Part I).
2. Experience design: navigation, design system, module-by-module UX specification (Part II).
3. Feature requirements with acceptance criteria (Part III).
4. Architecture, data model, security and privacy engineering (Part IV).
5. On-device AI strategy: models, runtimes, orchestration, fallbacks, packs, evaluation (Part V).
6. Detailed technical specifications: engine grammar, schemas, services, settings (Part VI).
7. The agent's development methodology and lifecycle (Part VII).
8. Quality: test strategy, test catalogue, environments, harness contract (Part VIII).
9. Build, CI/CD, signing, distribution (Part IX).
10. Traceability, observability, maintenance, risks, glossary, sign-off (Part X).

Out of scope — stated plainly so the agent never wanders:

- Any server, cloud service, account system, analytics pipeline or remote-config service.
- iOS, web, or desktop builds (the architecture isolates platform code so ports remain *possible*, but no port is planned here).
- Content syncing *between devices* (local backup/restore files are in scope; a sync protocol is not).
- Monetization of any kind — no ads, no purchases, no offers (§1.3).
- Root/privileged operation or system-app signing.

## Success criteria for the whole program

The program is successful when **all** of the following are true simultaneously:

| # | Criterion | Evidence artifact |
|---|---|---|
| S1 | `myspace-one-release.apk` installs and launches on API 26, 33 and 35 emulators with airplane mode ON | CI run logs + emulator videos (§24) |
| S2 | Zero internet-class permissions requested (`INTERNET`, `ACCESS_NETWORK_STATE` absent from merged manifest) | `apkanalyzer manifest` output attached to release evidence |
| S3 | All Catalogue-0 test cases (§20.6) pass on the release build | Test results JSON + PDF report |
| S4 | Calculator engine passes the full property-based law suite (§17.1.7) | Unit-test logs, 10⁴+ randomized cases per law |
| S5 | Every feature F-001…F-084 maps to at least one passing test and one commit | Traceability matrix generated by `tools/traceability.py` |
| S6 | Static analysis is clean: zero blocking lint/detekt findings; no `WebKit`, `WebView`, socket, or reflection-to-network APIs in release bytecode | detekt/lint reports + `apkanalyzer` scan |
| S7 | APK size ≤ 30 MB without optional AI packs; AI packs are separate side-loaded files | Build outputs + size budget report (§23.6) |
| S8 | Documentation set is regenerated from the final source tree and archived with the release | Release bundle manifest (§25.6) |

These criteria are restated as phase-gate G7 exit conditions in §15.5. If any criterion cannot be met, the agent must file a defect (§20.9) and stop the release — a red release is always preferable to a green lie.
