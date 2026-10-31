@PART: PART I — CHARTER, USERS AND NON-NEGOTIABLES
@PARTDESC: What OneDoc is, the five promises every requirement serves, the constraints that can never be weakened, and what is permanently out of scope. Everything in Parts II–XII is a consequence of this part.

# Chapter 1 — Mission, promises and hard constraints

## 1.1 Mission statement

> **OneDoc gives one person, on one offline phone, a complete document studio — write, structure, format, scan to text, dictate, listen, and share — in one fast, private application that never requires an account, a network, or a subscription.**

The mission sentence is testable, word by word. "One application" means exactly one icon, one installer, one data store. "Offline phone" means the product delivers one hundred percent of its value in airplane mode, from first launch, with no configuration. "Never" means never — not "unless the user accepts a dialog", not "except for crash reporting", not "only on first run".

The reference bar is the writing experience of Google Docs and Microsoft Word: not their cloud features — their *editing* features. A user who writes letters, reports, minutes, essays, or a novel on OneDoc must not feel like they settled for a toy.

## 1.2 The five promises

Every requirement in this document serves exactly one of five promises. When two requirements conflict, the lower-ranked promise yields.

1. **P1 — Works everywhere, always.** Full functionality in airplane mode, on a low-end phone, on first launch, with no configuration. If a feature cannot honor this, the feature changes, not the promise.
2. **P2 — Private by architecture.** OneDoc never transmits user content because it *contains no transmit path*: no `INTERNET` permission, no WebView, no telemetry SDK, no updater. Privacy is structural, not a policy page.
3. **P3 — Zero-friction writing.** New document to first sentence in under two seconds and two taps. No modal walls, no wizards, no "sign in to continue" — there is nothing to sign in *to*.
4. **P4 — Fast and gentle.** Cold start under 1.2 s on Tier B hardware; typing latency P95 under 50 ms at 10,000 words; jank-free scrolling; battery-safe background behavior; no notifications except the reminders the user created.
5. **P5 — Built to be verified.** Every claim in this document maps to an automated check or a reviewable artifact. The agent proves, it does not assert. "It should work" is not a state; PASS, FAIL and BLOCKED are states.

## 1.3 Hard constraints

The constraints below are hard. They are repeated or refined in later chapters but never weakened. A task that violates a constraint is invalid, no matter how much work it embeds.

| ID | Constraint | Rationale | Verified by |
|---|---|---|---|
| C1 | No `INTERNET` and no `ACCESS_NETWORK_STATE` permission in the merged manifest of any shipped APK | P2; the owner's explicit requirement | `apkanalyzer` manifest check as a CI gate (§26.4) |
| C2 | No sign-in, no account, no user identity of any kind | P1, P2 | Dependency + code scan: no auth classes, no account APIs (§26.4) |
| C3 | No ads, no ad SDKs, no tracking SDKs, no analytics, no purchase flows | Owner's explicit requirement | Deny-list dependency audit in CI (§26.4); direct-APK QA case TC-SEC-P-03 |
| C4 | All user data stays in app-private storage or user-granted SAF locations | P2 | Security suite TC-SEC-* (§20.6) |
| C5 | AI models are side-loaded packs verified by SHA-256; the app never downloads anything | P1, P2; AI must work on offline devices | Pack-manager tests TC-AI-PACK-* (§19.6) |
| C6 | Android 8.0 (API 26) minimum; phones and tablets; portrait and landscape | Compatibility promise | Emulator matrix API 26/33/35/36 (§27.2) |
| C7 | Editor laws L1–L10 (§13) are release blockers, exactly like the calculator laws were in the predecessor program | The editor *is* the product | Catalogue TC-EDIT-* + direct-APK QA (Part X) |
| C8 | Max 3 parallel CI runners, ≤ 30 jobs per pipeline run | Runner quota discipline | Workflow configuration (§26.1) |
| C9 | A single codebase ships both the full studio and, if the owner later asks, a lean "writer-only" flavor via Gradle flavor — zero duplicated editor code | Optionality without cost | Flavor build tasks (§26.2); not exercised at v1.0 unless the owner opts in |
| C10 | Every shipped artifact carries provenance: commit SHA, workflow run ID, APK SHA-256 | The owner verifies, not trusts | Release evidence bundle (§28.2) |

## 1.4 Permanently out of scope

The following are rejected for the lifetime of this program, and any task proposing them is invalid: cloud sync of user content; accounts or profiles; social features; comments-from-others or real-time co-editing (single-user device product); push notifications from external services; in-app purchases; advertising of any kind; third-party content feeds; WebView-based document rendering; root access; device administration; accessibility-service abuse (OneDoc *serves* accessibility, it never *consumes* it); background location; contact, call-log or SMS access; cryptocurrency or payment features; executing arbitrary macros or scripts inside documents (a deliberate security stance — macro malware has no place here).

This list exists because autonomous agents drift toward "helpful" additions. Scope creep is a defect class (§25.3, category S-CREW) and is triaged as such: a feature nobody asked for is a bug somebody must now maintain.

## 1.5 Defaults where this document is silent

1. **Platform convention wins** over invention when they conflict: Material 3 behaviors, back-gesture semantics, share-sheet patterns, system back predictiveness.
2. **Simplest testable behavior wins** when two designs both satisfy a requirement.
3. **Battery and RAM win** over feature richness at equal user value.
4. **Determinism wins** over cleverness: same input, same output, same logs.
5. When genuinely ambiguous, the agent chooses the option closest to **Google Docs / Google Keep / Google Files** interaction patterns for the corresponding surface — because the owner's feedback history anchors on those references — then records the choice as a D-nnn entry in the decision ledger (`docs/plan/decisions.md`).

# Chapter 2 — Product rationale

## 2.1 Why a document studio

Documents are the most universal personal-computing artifact: a shopping list, a lease summary, a school essay, meeting minutes, a resume, the first chapter of a novel. The owner's requirement is a **fresh app** — not a continuation of any prior product — whose core is creating documents of Word/Google-Docs quality on a phone, fully offline.

Phones are where thought happens in stolen moments. Yet mobile writing tools mostly come in two broken flavors: crippled "note apps" that collapse the moment a document grows structure (headings, lists, tables), and office suites that are desktop UIs squeezed onto a screen, complete with sign-in walls and cloud nagging. OneDoc takes the third path: a native Android editor with a real block-and-mark document model (Part V), on-device AI that earns its place (Part VIII), and file handling honest about fidelity (Part VII).

## 2.2 Why offline-first, on-device AI

Three independent reasons, in priority order:

1. **The owner's requirement.** Work locally, on device, no sign-in, no internet. This is a product-definition fact, not a preference to optimize away.
2. **Trust asymmetry.** An offline-first app has nothing to leak. There is no telemetry pipe to abuse, no server to breach, no terms to erode. The privacy story fits in one sentence: *your words never leave your phone because there is no path out.*
3. **Reliability and latency.** On-device AI in 2026 covers the needed capability set — OCR (scan a page, get text), dictation (speak, see words), summarization and rewriting (small LLM), semantic search (embeddings) — at 40–800 ms latencies with zero availability risk. A feature that needs the network is a feature that dies in airplane mode, on a metro, in a basement classroom: exactly the moments people write.

## 2.3 Risks and their engineered answers

| Risk | Consequence if ignored | Engineered answer |
|---|---|---|
| Editor complexity balloons; text-input bugs ship | Lost characters, broken undo — reputation-ending for a writing app | Strict block-and-mark model with property-based tests (§16); editor laws L1–L10 as release blockers (§13); IME composition test suite from day one (§15.3) |
| Document model is a dead end (no tables, no images) | Product hits a wall at G4 and needs a rewrite | Closed block-kind set designed up front, schema-versioned with migrations (§18.2); tables/images are block kinds v1, not afterthoughts |
| Format support over-promises ("opens .docx!") then corrupts | User loses trust and data | Declared fidelity levels F0–F3 per format (§18.2); importers refuse with reasons rather than guess; round-trip tests are release blockers |
| On-device AI drains battery or RAM on cheap phones | The promise P1 breaks exactly where it matters most | Device tiers A/B/C with fallback ladders; packs are opt-in side-loads; assistant controls hide (with reason) when hardware cannot run them (§19.4) |
| APK bloat toward office-suite gigantism | Slow installs, cheap-phone exclusion | Size budget 25 MB without packs (§26.4); per-PR APK-size check |
| Autonomous agent drifts, invents UI, invents scope | Incoherent product, unverifiable claims | Screen registry + token contract (Part III); gates with DoD (Part X); decision ledger reviewed at every gate |

## 2.4 Users and the top journeys

OneDoc serves one user per device, and designs for three of them:

- **The correspondent** — letters, applications, filled forms; cares about clean print/export (PDF) and templates.
- **The compiler** — students, analysts, writers; long documents, headings, tables, versions, search across everything.
- **The capturer** — photographs pages and whiteboards, dictates on the move; cares about scan-to-text and dictation accuracy.

The five journeys that shape acceptance (full step-by-step versions with case ids in §27):

| J-id | Journey | Success definition |
|---|---|---|
| J1 | Blank page → formatted letter → PDF export | Under 3 minutes on first launch, no settings touched, PDF paginates cleanly |
| J2 | Photograph 3 printed pages → one document with corrected OCR text | Under 2 minutes; OCR text lands in the editor as editable paragraphs |
| J3 | Dictate meeting minutes → tidy → share as .docx | Speaker's words appear live; tidy-up pass is one tap; export keeps lists/headings |
| J4 | 20-document library → find "the paragraph about the warranty" | Full-text hit in <300 ms; semantic hit surfaced with pack installed |
| J5 | Accidental deletion of half a document → recover | Version restore in under 30 s losing at most the last 2 s of typing (Law L3) |

If a release candidate fails any journey end-to-end on the emulator matrix, the release does not ship. Journeys are tested on the **distributed APK**, not on source (§24).

## 2.5 What "done" means for v1.0

OneDoc v1.0 is done when: (a) all gates G0–G8 are closed with evidence (Part X); (b) the release APK passes every P0 case in the test catalogue on the emulator matrix; (c) the defect tracker has no open S1/S2; (d) the owner holds a signed artifact plus an evidence PDF whose every claim traces to a test id. Status without evidence does not exist in this program.

## 2.6 Reference teardown: what we take, what we reject

The bar is "writing quality of Google Docs / Word on a phone". That claim is only actionable when broken into specific, stolen-or-rejected behaviors. The teardown below is the design diligence behind Parts III and V; "TAKE" entries are requirements in Chapter 4 by reference.

| App | TAKE (and where it lands here) | REJECT (and why) |
|---|---|---|
| Google Docs | selection toolbar that flips around the selection (UX-19); Enter-continues-list semantics (UX-23); outline/TOC coupling (F-035); live word count in context (F-027); find bar with counts (F-026) | account wall and "connect to network" states (C1/C2); offline as a degraded mode — OneDoc has no other mode; comment threads (single-user product) |
| Microsoft Word | real page metaphor with margins and break guides (F-037/038); print-fidelity PDF (F-051); table header repeat (§17.1); footnote handling (F-039) | ribbon-density UI (one-handed phones); sign-in-first flow (C2); file-format lock-in via fidelity FUD — OneDoc declares fidelity honestly (§18.2) |
| Google Keep | instant capture: FAB → editor with zero dialogs (UX-01); checklists as first-class (F-019); calm empty states (UX-36) | notes-not-documents ceiling (no structure, no tables) — the exact gap OneDoc exists to fill; color-as-organization only (UX-41) |
| Obsidian | plain-file honesty, fast full-text search (F-067), local-first durability mindset (Law L3) | markdown-source-as-truth (OneDoc's source is structured, exports markdown); plugin free-for-all (§1.4: no code execution in documents); link-graph UI complexity |
| LibreOffice mobile | format breadth ambition (F-054/055) | desktop-file dialogs on touch (F-031); fidelity overpromising without notes — the anti-pattern §18.1 outlaws; heavyweight APK (budget §26.4) |

## 2.7 Why each promise earns its rank

The five promises (§1.2) are ranked for one reason: autonomous construction needs a tiebreaker more than a philosophy. The practical resolutions recorded here are citable in decisions:

- **P1 beats P3.** If a lovely two-tap flow requires a permission pre-prompt or a network check, the flow changes, not the rule (e.g., dictation requests mic at first use, not at launch — UX-32).
- **P2 beats P4.** The security suite runs on every RC even when it costs a day of schedule; there is no "ship first, encrypt later" (§20.3).
- **P4 beats breadth.** When G4 runs late, features drop before budgets do: a fast editor with fewer features is OneDoc; a slow editor with all features is a rejection (§21.4).
- **P5 outranks everything moment-to-moment.** Any work that cannot be evidenced (a "quick hack", an untested fix) is, by definition, not part of this program (§29.5).

## 2.9 Naming conventions (ids, files, branches, artifacts)

Feature ids `F-nnn`, UX `UX-nnn`, laws `L-n`, constraints `C-n`, cases `TC-<AREA>-<nnn>` (areas per Appendix C), journeys `J<n>`, gates `G<n>`, decisions `D-nnn`, sessions `S-nnn`, defects `OD-nnn`, risks `R-n`, screens `OD-<AREA>-<nnn>`, pack names `<cap>-<lang>`. Code: modules per §10.1; resources prefixed `od_`; a11y ids mirror screen ids (`od_edit_001_toolbar`). Branches: trunk-based short-lived `agent/<task-id>` branches merged to `arena/…` per session; tags `v<X.Y.Z>`; artifacts `OneDoc-v<X.Y.Z>-<code>-<sha7>.apk`. One naming style per thing, everywhere, forever — the traceability tooling greps these patterns, and ambiguity in names is ambiguity in evidence.
