# Appendix D — Gate definitions of done (full)

## G0 — Charter accepted
- [ ] Owner accepts this blueprint v1.0 as the build contract (the acceptance act is recorded in `reports/onedoc/gates/G0.md`).
- [ ] `docs/onedoc/plan/` seeded: kickoff, task graph (G1+G2 expanded), decisions (D-000 example), sessions (S-000).
- [ ] Traceability green: `tools/onedoc/traceability.py --check --strict` exit 0.

## G1 — Toolchain & shell
- [ ] JDK 17, SDK platform 36, build-tools 36.0.0, platform-tools installed; licenses accepted.
- [ ] AVDs per §23.1 created and boot-verified (API 26/33/35/36).
- [ ] Gradle multi-module skeleton per §10.1; `full` and `writer` flavors assemble; debug APK installs on all AVDs.
- [ ] CI pipelines per §22.2 registered; `pr.yml` green with ≤ 8 jobs; budgets enforced (≤ 3 runners).
- [ ] App icon, naming, `app.onedoc` applicationId, versioning scheme (§26.3) in place.

## G2 — Model & storage
- [ ] `core-model` complete: block kinds, marks, ops, normalize; invariants I1–I4 enforced.
- [ ] Property suite P1–P10 green in JVM.
- [ ] `core-storage`: Room schema v3 exported; journal write/replay/compact; kill-trial harness passes locally (API 33, 20 trials).
- [ ] Golden files for odoc container; .odoc save/open round-trip.

## G3 — Editor core
- [ ] Editor screen: block list, caret, selection, toolbar, tab row skeleton.
- [ ] IME contract implemented (§15); fuzzer harness running on all AVDs green.
- [ ] Undo/redo with coalescing; laws L1–L10 suites green.
- [ ] Typing budget met: P95 < 50 ms at 10k words on API 33 (TC-PERF-002 evidence).

## G4 — Rich features
- [ ] Tables, images, TOC/map, page setup + guides, templates (12 built-ins), find/replace, versions UI, reader mode.
- [ ] All EDIT/TBL/IMG/STRUCT/TPL/STATE cases green.
- [ ] DQ-1…DQ-8 checklist passes for every new screen.

## G5 — Formats & IO
- [ ] Exporters: pdf/odoc/md/txt/html/docx with goldens; importers: odoc/md/txt/html/docx with notes; refusal paths with reasons.
- [ ] Round-trip property P7 green; conversion-note UX verified.
- [ ] Share/open-in/SAF cases green (TC-IO-*).

## G6 — On-device AI (feature-flagged until G7)
- [ ] Pack manager + 4 pack types installable/verifiable/removable; ladder implemented with hidden-with-reason UX.
- [ ] Scan, dictation, assistant, semantic search, read-aloud flows green on their tiers (API 36 full; API 33 extractive/system rungs; API 26 degradation).
- [ ] Network-silence probe green across all AI flows (TC-SEC-P-03).

## G7 — Quality pass
- [ ] Full catalogue on release APK across §23.1 matrix; journeys J1–J5 green; evidence PDF assembled.
- [ ] Performance budgets green (§21.4); size ≤ 25 MB.
- [ ] Security suite green; zero open S1/S2; BLOCKED register reviewed with owner-visible reasons.

## G8 — Release
- [ ] Release checklist (§28.1) complete; provenance bundle committed; artifacts attached to GitHub Release; defect tracker final state; owner handoff note.

# Appendix E — Environment pins

| Tool | Pin |
|---|---|
| JDK | 17 (Temurin) |
| Android SDK | platforms;android-36, build-tools;36.0.0, platform-tools latest stable, cmdline-tools latest stable |
| Emulator images | system-images;android-26;google_apis;x86_64 · android-33 · android-35 · android-36 (google_apis, no playstore) |
| AVDs | `od-api26` Pixel 2 2 GB · `od-api33` Pixel 4 3 GB · `od-api35` Pixel 6 4 GB · `od-api36` Pixel 8 8 GB |
| Emulator boot | `-no-window -no-audio -gpu swiftshader_indirect -no-snapshot-save` (snapshots only for boot speed with `-snapshot` goldens) |
| CI runners | ubuntu-latest ×3 max parallel; concurrency cancel-in-progress per branch |

# Appendix F — Dependency and runtime pins (verify at adoption; record exacts in D-nnn)

| Concern | Choice | Notes |
|---|---|---|
| Language/build | Kotlin (latest stable at G1), AGP pinned, JDK 17 | version catalog; no dynamic versions |
| UI | Android Views + Material Components (m3) | no experimental UI toolkits (API 26 safety) |
| DI | Hilt | standard |
| DB | Room (schema export on) + FTS5 | external-content FTS |
| Editor rendering | RecyclerView + custom block views + `EditText`-free text stack (custom `BlockTextView` over `Layout`) | the IME bridge is ours, §15 |
| PDF | android.print framework + PdfDocument | fonts subset via bundled Inter |
| OCR | ONNX Runtime Mobile (or TFLite) hosting DBNet-lite + CRNN int8 | pack: `ocr-en` |
| ASR | whisper.cpp (pinned release), ggml int8 model | pack: `asr-en` |
| LLM | llama.cpp-compatible pinned runtime, gemma-2B-it 4-bit (q4_0) | pack: `llm-gemma2b`; Tier A only |
| Embeddings | ONNX MiniLM-L6 int8, tokenizers bundled in pack | pack: `embed-minilm` |
| TTS | android.speech.tts (system) | no pack |
| Crypto | Android Keystore + Tink-free standard JCE (AES/GCM, PBKDF2) | no crypto SDKs |
| Tests | JUnit4/5, truth, MockK, Robolectric, espresso/uiAutomator, macrobenchmark | property harness custom (§16) |

Model pack contents record exact file names + SHA-256 in their `manifest.json`; runtimes pin exact upstream versions in the version catalog and in the first D-nnn that adopts them.

# Appendix G — Pre-registered BLOCKED register

Empty at v1.0 by design. Doctrine (§21.2): emulator/input/accessibility limitations pre-register here with environment fingerprint the first time they appear; each entry is re-tried every cycle with current tooling; removal requires either a PASS or a defect id. Inherited examples that will likely apply: physical-device-only behaviors (stylus pressure, multi-touch edge cases) are L5 and pre-BLOCKED on emulators by definition.

# Appendix H — Templates and index

## H.1 Decision entry (decisions.md)

```
### D-003 · 2026-XX-XX · Export: DOCX subset boundary
Context: DOCX has constructs OneDoc cannot represent (tracked changes, SmartArt).
Decision: writer covers §18.2 subset; beyond it, per-paragraph conversion notes; never guess.
Consequences: fidelity promise is testable (TC-IO-004/005); risk of user surprise mitigated by UX-45 note.
Reversal condition: owner asks for tracked-changes preservation → new decision supersedes.
```

## H.2 Session entry (sessions.md)

```
## S-002 · 2026-XX-XX · G2 model+storage
Goal: land core-model + property suite.
Done: blocks/marks/ops; P1–P7 green; odoc goldens.
Failed/Blocked: P8 flaky on replay timing — root-caused to unsynced fsync; fix in S-003.
Next: kill-trial harness; schema v3 export.
```

## H.3 Index of normative tables

| Topic | Where |
|---|---|
| Constraints C1–C10 | §1.3 |
| Journeys J1–J5 | §2.4, §27 |
| Features F-001…F-090 | §4, App. A |
| UX-01…UX-50 | §5, App. B |
| Tokens/themes | §6 |
| Figma contract + registry | §7 |
| Design-QA DQ-1…DQ-8 | §9.2 |
| Architecture/threads | §10 |
| Schema/journal/migrations | §11 |
| Snapshot policy | §12.2 |
| Laws L1–L10 | §13 |
| Document model + invariants | §14 |
| IME contract | §15 |
| Property suite P1–P10 | §16 |
| Feature engineering contracts | §17 |
| Fidelity matrix F0–F3 | §18.2 |
| AI stack/ladder/packs | §19 |
| Security suite | §20 |
| Budgets + gates | §21 |
| CI pipelines + budgets | §22 |
| Emulator matrix | §23 |
| Direct-APK QA + evidence PDF | §24 |
| Defects | §25 |
| Build/flavors/versioning | §26 |
| Release checklist/provenance | §28 |
| Way of working | §29 |
| Env/dependency pins | App. E/F |
