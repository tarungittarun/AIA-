@PART: PART I — FOUNDATIONS, SCOPE AND PROMISE
@PARTDESC: Why this product exists, what it must never do, who it serves, and the constraints that shape every later decision. Read this part first: every technical choice in Parts II–X traces back to a promise or a constraint stated here.

This part fixes the product's identity before a single line of code is specified. It is deliberately short and absolute: missions, promises, constraints and people. Everything else in the blueprint is a consequence of what is written here.

# Chapter 1 — Mission, vision and non-negotiables

## 1.1 Mission statement

> **MySpace One gives one person, on one offline phone, every everyday tool they need — calculate, write, scan, plan, organize, listen, record, and diagnose — in one fast, private application that never requires an account, a network, or a subscription.**

The mission sentence is testable. "One application" means exactly one icon, one installer, one data store. "Offline phone" means the product must deliver one hundred percent of its value in airplane mode from first launch. "Never" means never — not "unless the user accepts a prompt", not "except for crash reporting".

## 1.2 The five promises

Every requirement in this document serves one of five promises. When two requirements conflict, the promise ranked lower yields.

1. **P1 — Works everywhere, always.** Full functionality in airplane mode, on a low-end phone, on first launch, with no configuration. If a feature cannot honor this, the feature changes, not the promise.
2. **P2 — Private by architecture.** The app never transmits user content because it *contains no transmit path*: no network permission, no WebView, no telemetry SDK. Privacy is structural, not a policy.
3. **P3 — One home, zero friction.** All tools live behind one icon and at most two taps. No module makes the user re-learn basic patterns; one design system everywhere.
4. **P4 — Fast and gentle.** Cold start under 1.2 s on Tier B hardware; jank-free scrolling; battery-safe background behavior; no notifications except alarms the user created.
5. **P5 — Built to be verified.** Every claim in this document maps to an automated check or a reviewable artifact. The agent proves, it does not assert.

## 1.3 Non-negotiable constraints

The constraints below are hard. They are repeated or refined in later chapters but never weakened.

| ID | Constraint | Rationale | How it is verified |
|---|---|---|---|
| C1 | No `INTERNET` and no `ACCESS_NETWORK_STATE` permission in the merged manifest of any shipped APK | P2; user asked for local-only operation | S2 check: `apkanalyzer manifest` on release APK, CI gate in §24 |
| C2 | No sign-in, no account, no user identity of any kind | P1, P2 | Code review checklist §14.2; no auth classes in dependency scan |
| C3 | No ads, no ad SDKs, no tracking SDKs, no purchase flows | Explicit user instruction; P2 | Dependency audit in CI (deny-list of package prefixes, §24.4) |
| C4 | All user data stays in app-private storage or user-granted SAF locations | P2 | Security test suite TC-SEC-* (§20.7) |
| C5 | AI models are side-loaded packs verified by SHA-256; the app never downloads | P1, P2; optional AI on offline devices | Model-pack manager tests TC-AI-pack-* (§16.8) |
| C6 | Android 8.0 (API 26) minimum; phones and tablets; portrait and landscape | Compatibility promise | Emulator matrix (§21.2) |
| C7 | Calculator parity behaviors from the guide (percent, implicit multiplication, digit grouping, selection memory actions) are release blockers | User's core daily tool; guide §C/§D | Catalogue-0 cases TC-ONE-C-001…026 (§20.6) |
| C8 | Max 3 parallel CI runners, ≤ 30 jobs per full pipeline run | Runner quota discipline | Workflow configuration (§24.1) |
| C9 | A calculator-only flavor (`mycalc`) ships from the same codebase via build flavor, zero duplicated engine code | User asked for standalone calculator distribution | Flavor build tasks (§23.4) |
| C10 | Every shipped artifact carries provenance: commit SHA, workflow run ID, APK SHA-256 | The owner verifies, not trusts | Release evidence bundle (§25.6) |

## 1.4 Permanently out of scope

The following are rejected for the lifetime of this program, and any task proposing them is invalid: cloud sync of user content; social features; accounts or profiles; push notifications from any external service; in-app purchases; advertising of any kind; third-party content feeds; cryptocurrency or payment features; root access; device administration; accessibility-service abuse (the app *serves* accessibility, it never *consumes* it); background location; contact access.

This list exists because autonomous agents drift toward "helpful" additions. Scope creep is a defect class (§20.9, category S-CREW) and is triaged as such.

## 1.5 Defaults where this document is silent

1. **Platform convention wins** over invention when they conflict (Material 3 behaviors, back-gesture semantics, share-sheet patterns).
2. **Simplest testable behavior wins** when two designs both satisfy a requirement.
3. **Battery and RAM win** over feature richness at equal user value.
4. **Determinism wins** over cleverness: same input, same output, same logs.
5. When genuinely ambiguous, the agent chooses the option closest to **Google Calculator / Google Keep / Google Files / Google Recorder** interaction patterns for the corresponding module, because the owner's prior feedback anchored on those references — then records the decision D-nnn in the ledger (§15.7).

# Chapter 2 — Why combined, why offline: product rationale

## 2.1 The case for one app

The owner's starting point was a suite of separate tools (a calculator app plus a "MySpace" bundle containing Notes, Scanner, Calendar, Files, Music, Recorder, Diagnostics). Maintaining several APKs multiplies every cost — build, test, release, support — while splitting the user's muscle memory across icons. Combining them produces compounding wins:

- **Cross-module flows become first-class**: scan → text lands in Notes; recording → summary lands in Notes; note → attach → export through Files; calculator result → paste anywhere. Inside one app these are function calls and shared UI; across apps they are fragile intents.
- **One data layer, one search**: a note, a scan's OCR text, a recording's transcript and a calendar event are all queryable from the hub search box (§8.1).
- **One design system, one accessibility story, one performance budget** — enforced once, applied everywhere.
- **One install and update path** for the owner, who distributes APKs directly.

The cost of combining — APK size, module coupling, review complexity — is real and is managed by architecture (§11.2: module boundaries as Gradle modules), the size budget (§23.6), and the flavor system that still yields a calculator-only distribution (C9).

## 2.2 The case for on-device, always-on offline

Three independent reasons, in priority order:

1. **The user's requirement.** The owner stated the main priority: work locally, on device, no sign-in, no internet. This is a product-definition fact, not a preference to be optimized away.
2. **Trust asymmetry.** An offline-first app has nothing to leak. There is no telemetry pipe to abuse, no terms-of-service to erode, no server breach risk. The privacy story fits in one sentence (P2).
3. **Reliability and latency.** On-device AI in 2026 covers the needed capability set (OCR, ASR, small-LLM summarization, embeddings) with 40–400 ms latencies and zero availability risk. A feature that depends on a network call is a feature that fails in airplane mode, on a metro, on a broken gateway — the exact moments a calculator-and-notes user reaches for the tool.

## 2.3 Risks of the combined approach and their engineered answers

| Risk | Consequence if ignored | Engineered answer |
|---|---|---|
| Module coupling turns releases brittle | One bug blocks all releases | Gradle module-per-feature with API surfaces (§11.2); CI runs module-scoped tests in parallel |
| APK bloat from media + AI code | Slows install; feels unprofessional | Size budget table §23.6; AI *models* are external packs (C5), AI *code* is a few hundred KB |
| Feature teams (or agent phases) drift in UI patterns | Frankenstein feel, violates P3 | Single design-system module; screenshot tests per component (§20.4) |
| Background media services drain battery | Violates P4 | Foreground-service-only policy, strict wakelock tests TC-PERF-* (§20.7) |
| Hub search over all modules gets slow | P3 erodes | Precomputed FTS + embedding indexes maintained incrementally (§12.5) |

## 2.4 Reference points the owner recognizes

The owner's test guides referenced Google Calculator behaviors (percent handling, digit grouping, history replay) and Google-suite interactions. The product deliberately mirrors interaction *patterns* — not visuals — of: **Google Calculator** (expression caret, live answer, history sheet), **Google Keep** (note cards, checklists, pinning), **Google Files** (browse + clean), **Google Recorder** (markers + transcript), **Proton/Aegis-style local-first security** (encrypted exports). No Google code, assets, or trademarks are used; the parity is behavioral, and Chapter 17 specifies each behavior precisely enough to test without the original.

## 2.5 Why-combined per module (value table)

| Module | Value alone | Value combined (unique to one app) |
|---|---|---|
| Calculator | core tool | results into notes; history searchable from hub |
| Notes | capture | receives scans/transcripts; AI actions share one pack store |
| Scanner | capture | text flows into notes; analyzer counts scans |
| Calendar | planning | reminders integrate one notification model; ICS via Files |
| Files | organization | private store for all modules' outputs; backup covers everything |
| Music | playback | library via Files' SAF grants; miniplayer across modules |
| Recorder | capture | transcripts → notes; files visible in Files |
| Diagnostics | support | one health view for the whole app; pack manager for all AI |

## 2.6 Alternatives considered (and why combined won)

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| Keep N separate APKs | small per-APK size; independent releases | N× build/test/release cost; no shared data; owner distributes more files; cross-module flows impossible | rejected |
| One suite app (this blueprint) | shared design system, one data layer, cross-module flows, one release train | bigger APK; module coupling risk | **chosen** — coupling managed by Gradle modules + budgets |
| Suite + plugin modules (dynamic feature) | on-demand modules | needs Play (owner sideloads); complexity unjustified offline | rejected |
| Web wrapper suite | tiny APK | violates P2 structurally (WebView, needs network culture) | rejected forever (§1.4) |

# Chapter 3 — Users, personas and environments

## 3.1 Personas

| Persona | Device | Data context | What they do daily | What they never forgive |
|---|---|---|---|---|
| **Asha — the owner-distributor** | Mid-range Android, often airplane mode | Sideloads APKs for family and friends | Tests each release; shares installs; reads reports | A release that behaves differently from its report |
| **Ravi — the student** | 2–3 GB RAM phone | No Google account configured on device | Calculator for homework; notes for class; scans of handouts | A calculator that says `0.9999999999` where `1` is expected |
| **Meera — the field worker** | Rugged device, offline all day | Works in low-connectivity zones | Scans receipts; records voice memos; plans visits in calendar | Losing a recording or a scanned page |
| **Usha — the archivist** | Tablet, large storage | Keeps years of notes and audio | Organizes files, playlists, old notes; exports backups | A silent data migration that renames or drops content |

Persona-driven acceptance checks appear in Chapter 9 as journey tests (J-nnn).

## 3.2 Device tiers and environments

The product must be *excellent* on low-end hardware, not merely functional. Tiers:

| Tier | RAM | Typical API | Storage | Product stance |
|---|---|---|---|---|
| C | 2–3 GB | 26–30 | 32 GB shared | Everything usable; AI essentials pack only; 60 fps p50 on calculator, 55 fps p50 lists |
| B | 4–6 GB | 29–33 | 64 GB | Everything fast; + speech pack; recorder waveform real-time |
| A | ≥ 8 GB | 31+ | 128 GB+ | + assistant pack (small LLM); instant hub search over embeddings |

Environments the agent must honor: airplane mode; "no accounts on device"; restricted profile with storage permission denied (Scanner falls back to in-app capture only); dark and light system themes; font scale 1.0–2.0; TalkBack enabled; locale `en-IN` (default) plus `en`-generic; battery saver active.

## 3.3 Accessibility as a persona, not a feature

TalkBack users, low-vision users (font scaling, contrast), motor-impaired users (no gesture-only paths — every gesture has a button equivalent), and deaf users (recorder and music never rely on sound alone) are first-class personas. Chapter 8 specifies the accessibility contract per module and Chapter 20 tests it (TC-A11Y-*).

## 3.4 Locale expectations

Default locale `en-IN`: Indian digit grouping (`1,23,456`) in Calculator and Files sizes, DD-MMM-YYYY dates, 24-hour clock respected from system settings. The string layer is externalized from day one so additional locales cost translations, not code (§14.5). Number formatting is *presentation-only*: stored values are exact strings/rationales (§12.2), never locale-mangled floats.

## 3.5 Environment acceptance matrix

Each row is an environment the QA matrix must exercise at least once per gate from G3 onward (TC-ENV-*). "Expectation" is the acceptance bar in that environment.

| Environment | Emulator/device profile | Expectation |
|---|---|---|
| Airplane mode, cold | E33B, radios off before launch | 100% functionality; no network-vocabulary strings; J-05 green |
| No accounts configured | E33B, factory profile, no Google sign-in | No account prompts anywhere; all modules work |
| Fresh install, denied all permissions | E26C | Hub + Calculator + Notes fully usable; Scanner import path; Recorder explains need; no repeated prompts |
| Battery saver ON | E33B | Effects → None; AI deferral chips; no job started > budget without user tap |
| Font scale 2.0 | E33B display size max | No clipped text; calculator keys 1.3× cap with 48 dp targets |
| Dark theme + dynamic color | E35A (A12+) | Tokens re-resolve; no white flash; screenshots match goldens |
| TalkBack on | E33B | Core journeys completable; focus order correct |
| Locale en-US | E26C | Western grouping; period decimals; history renders identically post-restore |
| Locale de-DE | E26C | Comma decimals accepted on input; grouping localized; laws L9 green |
| Low storage (< 100 MB) | E26C 8 GB image filled | Banner + graceful refusals; no corruption (J-10) |
| Doze / deep idle | E33B forced idle | Reminder fires within policy window; no wakelock abuse counters |
| Process death storm | E33B `am kill` loop | J-06 restoration green |
| Rotation storm | E33B | No state loss mid-draft/record/capture |
| Tablet 900×1600 | E35A tablet skin | Two-pane layouts per §7.12; no stretched phones UI |
| Very old WebView-less image | E26C (no WebView present) | Nothing breaks (app never uses WebView — structural) |

## 3.6 Persona journey narratives (design anchors)

**Asha's release day.** Asha builds/downloads the release on her laptop, copies the APK and the report PDF to her phone, installs over the previous version, and runs the Diagnostics self-test. It passes in seconds. She opens Calculator, tries her acceptance list (the Catalogue-0 spot checks), shares the report with two friends, and sideloads via a file transfer — all without internet on the receiving phones. Her acceptance bar: the report's claims match what her thumb just did.

**Ravi's homework sprint.** Ravi opens Calculator in airplane mode during a commute: 20 minutes of mixed arithmetic, percent discounts, a bracket-heavy physics expression on the scientific pad, replaying two earlier results from history, storing his roll number via MAdd for reuse. He switches to Notes between problems, checklisting formulas. Latencies he notices: none. His acceptance bar: `5+ =` → `10`, `1÷3×3` → `1`, zero IME popups, history intact after the phone's aggressive battery manager killed the app yesterday.

**Meera's field day.** Meera scans eight receipts at a market (storage-tight phone), transcribes one voice note at lunch on her Tier B device (2 min clip, ~90 s), sends both into Notes as one trip record, backs up at night via encrypted `.msone` to her laptop. Her acceptance bar: OCR usable in sunlight (high-contrast B&W filter), no silent failures, backup restore verified on a second phone.

## 3.7 Persona → priority influence map

| Persona | Strongest priorities | Features most shaped |
|---|---|---|
| Asha (owner) | provenance, honest QA, flavor | C10, F-084, L5 evidence style, mycalc |
| Ravi (student) | calc parity, speed, offline | F-001…F-035 core, P4 budgets |
| Meera (field) | scanner/recorder resilience, storage | F-055…F-059, F-073…F-077, J-10 |
| Usha (archivist) | backup, migrations, files | F-067, §29.2, Files edge register |
| A11y personas | §6.6 everywhere | TC-A11Y-*, UX-012 |

This part fixes the product's identity before a single line of code is specified. It is deliberately short and absolute: missions, promises, constraints and people. Everything else in the blueprint is a consequence of what is written here.
