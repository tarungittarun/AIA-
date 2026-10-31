@PART: PART IX — BUILD, RELEASE AND OPERATIONS
@PARTDESC: The toolchain, variants, budgets, CI/CD lanes, audit gates, signing, release bundles, distribution and post-release operations. This part turns a green codebase into a verifiable artifact an owner can install and trust.

# Chapter 23 — Build system and configuration

## 23.1 Toolchain (pinned)

| Tool | Version policy |
|---|---|
| JDK | 17 (Temurin), pinned via wrapper + CI matrix |
| AGP/Kotlin | latest stable at G1, frozen for the release; upgrades post-G7 go through the ledger |
| Gradle | wrapper, configuration cache ON, build cache shared per runner |
| SDK | compileSdk 36, target 35, min 26 |
| R8 | full mode, `optimization.json` diff attached to release evidence |

## 23.2 Variants

| Variant | Purpose | Signing |
|---|---|---|
| `fullDebug` | dev | debug key |
| `fullRelease` | the product APK | release keystore (§25.2) |
| `mycalcDebug` | flavor dev | debug key |
| `mycalcRelease` | standalone calculator APK | release keystore |

Flavor config: `applicationId` per §9.3; `resValue` app names; source-set swaps (hub absent in mycalc; launcher icon per flavor; version-name suffix none). BuildConfig flags: `PROVENANCE_SHA` (git rev-parse injected), `BUILD_TIME` — surfaced in About (F-084).

## 23.3 Reproducibility

Deterministic flag set (`zipflinger` stable ordering, fixed file timestamps where supported, locale-independent resource merging); the CI builds twice on tag builds and compares SHA-256 (V1–V2 signatures stable) — a mismatch fails the release. Local-vs-CI drift is checked once per phase via a "release candidate" build on the runner and recorded in metrics.

## 23.4 Flavor parity mechanics

`feature/calculator` is flavor-agnostic; `app/mycalc` contributes only: launcher, app name, nav graph root = calculator, and a compile-time `BuildConfig.IS_STANDALONE` consumed by the calculator module to hide cross-module actions (vs. runtime ifs — the R8 tree in mycalc proves no hub classes remain: lint check `mycalcNoCrossModule` scans the flavor's dex for `feature/hub` + `feature/*` class references and fails on any, enforcing F-040/F-039 structurally).

## 23.5 Dependency policy

Curated, small: Compose BOM, Room, DataStore, Koin, Media3, CameraX, Biometric, ONNX Runtime Mobile, LiteRT (pack-gated code path), MediaPipe LLM task lib, whisper.cpp JNI (self-built, prebuilt .so per ABI), kotlinx libs, Robolectric/Espresso/Roborazzi (test). Rules: no transitive network stacks even transitively present (a `dependencies` audit fails if `okhttp/retrofit` appears in the release graph — the AI libs are verified network-free configurations); new dependency requires a ledger entry + size delta note; licenses re-generated per release (F-085).

## 23.6 Size and performance budgets (release, per ABI set)

| Budget | Limit | Measured by |
|---|---|---|
| fullRelease APK | ≤ 30 MB | build output + size report |
| mycalcRelease APK | ≤ 6 MB | build output |
| cold start hub (Tier B) | ≤ 1.2 s p50 | Macrobenchmark in CI |
| cold start mycalc | ≤ 0.8 s p50 | Macrobenchmark |
| keystroke→frame (≤ 64 chars) | ≤ 16 ms p50 | engine benchmark + compose tracing |
| hub first search page @10k notes | ≤ 120 ms p50 | JUnit perf test on fixture corpus |
| recorder FGS start | ≤ 200 ms p95 | instrumented timing |
| DB write on main path | never (queue) | architecture test + strict-mode detector in debug |

Budgets are asserted in CI (fail the build, not a dashboard); deliberate budget raises require a ledger entry + owner-visible note at the next gate.

## 23.7 Variants DSL (trimmed, normative shape)

```kotlin
android {
  flavorDimensions += "dist"
  productFlavors {
    create("full") {
      dimension = "dist"
      applicationId = "app.space.one"
      resValue("string", "app_name", "MySpace One")
    }
    create("mycalc") {
      dimension = "dist"
      applicationId = "app.space.calc"
      resValue("string", "app_name", "MyCalc")
      versionNameSuffix = ""
    }
  }
  buildTypes {
    release {
      isMinifyEnabled = true; isShrinkResources = true
      proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"),
                    "proguard-rules.pro")
      signingConfig = signingConfigs.getByName("release")
      buildConfigField("String", "PROVENANCE_SHA", "\"${ext["gitSha"]}\"")
    }
  }
  androidResources { localeFilters += listOf("en", "en-IN") }
  packaging { jniLibs.useLegacyPackaging = false }
}
```

## 23.8 R8 keep rules (release, near-complete file)

```
# AI JNI bridges (reflection from native)
-keep class space.one.core.ai.jni.** { *; }
# Compose + Room generated are handled by their rules; add:
-dontwarn org.slf4j.**
# DataStore serializers via kotlinx
-keepclassmembers class * extends com.google.protobuf.GeneratedMessageLite { <fields>; }
# ONNX Runtime
-keep class ai.onnxruntime.** { *; }
# MediaPipe tasks
-keep class com.google.mediapipe.tasks.** { *; }
# Keep line numbers for local symbolication
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile
```

`optimization.json` + `mapping.txt` archived per release (§25.3); a CI check fails if rules grow beyond ~40 lines without a ledger entry (rule bloat = design smell).

## 23.9 Build performance techniques (why CI fits the budget)

| Technique | Effect |
|---|---|
| Gradle configuration cache + build cache | 30–50% faster re-builds |
| Module-parallel test tasks (3 runners) | device lane fits 90 min cap |
| Test sharding by module (§11.2) | no single runner bottleneck |
| Robolectric over emulator for L2 | minutes cheaper per case |
| Roborazzi on JVM (not device) | screenshot lane < 4 min |
| `androidResources.localeFilters` | smaller resources, faster AAPT |
| Baseline profiles generated at G6 | cold-start budget without runtime JIT cost |

## 23.10 Version catalog (gradle/libs.versions.toml, excerpt)

```toml
[versions]
kotlin = "2.0.21"
agp = "8.7.3"
compose-bom = "2024.12.01"
room = "2.6.1"
media3 = "1.5.1"
camerax = "1.4.1"
onnxruntime = "1.20.0"
mediapipe-tasks = "0.10.21"
[libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
# (single source of dependency truth; dependabot-style bumps are ledger-gated)
```

# Chapter 24 — CI/CD

## 24.1 Pipeline shape

One workflow per PR (fast lane: L1+L2+L3, architecture/lint, ~12 min) and one per trunk-merge or nightly (full lane: + L4 matrix + L5 harness, ≤ 90 min wall with 3 runners sharding; ≤ 30 jobs per run, C8). Release lane (tags): build, reproducibility double-build, L5 against release APK, docs regen, evidence bundle, GitHub Release draft.

## 24.2 Runner discipline

Concurrency groups cancel superseded runs; emulator jobs (the scarce resource) shard: E26C+E33B on runner 1, E35A on runner 2, L5 on runner 3; module test tasks shard by module; artifacts (results JSON, screenshots, logs) upload even on failure — a red run with no evidence is itself a pipeline defect.

## 24.3 Required checks (branch protection)

`build+lint`, `unit+property`, `integration`, `screenshots`, `instrumented-matrix`, `blackbox-apk-qa`, `size-budgets`, `manifest-audit`, `dependency-audit`, `traceability`. All green = mergeable. The historical publisher pattern (report commit by CI) is retained for release lane only; PR lanes never write to the repo.

## 24.4 Audit gates (config as law)

- `manifest-audit`: deny-list permissions (C1 set), exported-component allow-list, flavor zero-permission assert (F-038).
- `dependency-audit`: deny-list package prefixes (ads/tracking: `com.google.android.gms.*` ad classes, `com.facebook.*`, `com.applovin*`, `com.adcolony*`, `com.unity3d.ads*`, `io.branch*`, `com.mixpanel*`, `com.amplitude*`, analytics/crash reporters), plus network-stack presence scan (§23.5).
- `traceability`: every F/UX has ≥ 1 TC; every TC has binding; every commit in the release range carries `Refs:` or maps to chore/docs (warn).
- `docs-drift`: blueprint § refs in code must exist in the document set (regex parse), preventing stale pointers.

## 24.5 CI workflow sketch (structure, trimmed)

```yaml
name: full-lane
on: { push: { branches: [main] }, schedule: [{cron: "0 2 * * *"}] }
concurrency: { group: full-lane, cancel-in-progress: true }
jobs:
  fast:        # runner 1
    steps: [checkout, setup-jdk-17, gradle: spotlessCheck detekt lint testAll]
  integration: # runner 1 (after fast)
    steps: [robolectric suite, manifest/dependency/traceability/docs-drift audits]
  shots:       # runner 2
    steps: [roborazzi verify, upload diff artifacts on failure]
  device:      # runner 3, matrix [E26C, E33B, E35A]
    steps: [managed-emulator up, connectedShadedAndroidTests (journeys, a11y, perf)]
  blackbox:    # runner 3 (after device)
    steps: [assembleRelease both flavors, pin SHAs, run qa harness, upload evidence]
  report:
    needs: [blackbox]
    steps: [build PDF of record from evidence, attach to run summary]
```

Job count per full lane stays ≤ 30 (matrix expansion counted); the fast PR lane is a strict subset (≤ 8 jobs).

## 24.6 Fast PR lane YAML (trimmed)

```yaml
name: fast-lane
on: {pull_request: {}}
concurrency: {group: pr-${{ github.ref }}, cancel-in-progress: true}
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: {distribution: temurin, java-version: "17"}
      - run: ./gradlew spotlessCheck detekt :app:lintFullDebug
      - run: ./gradlew testDebugUnitTest robolectricSuite
      - run: ./gradlew roborazziVerify
      - run: python3 tools/traceability.py --check
      - run: python3 tools/audits.py manifest dependencies docs-drift
      - uses: actions/upload-artifact@v4
        if: always()
        with: {name: reports, path: build/reports/}
```

## 24.7 Nightly lane additions (beyond PR fast lane)

```yaml
  nightly:   # after fast jobs pass on main
    steps:
      - run: ./gradlew connectedShadedDebugAndroidTest  # journeys J-01..J-10 (3 runners)
      - run: python3 qa/run_blackbox.py --profile nightly --emulators E26C,E33B,E35A
      - run: ./gradlew macrobenchmarkHub macrobenchmarkCalc
      - run: python3 tools/traceability.py --emit reports/traceability.csv
      - uses: actions/upload-artifact@v4
        with: {name: nightly-evidence, path: reports/evidence/nightly-*/}
```

## 24.8 CI artifact retention

| Artifact | Where | Retention |
|---|---|---|
| Test reports (fast lane) | CI artifacts | 30 d |
| Screenshot diffs | CI artifacts | 30 d |
| Nightly evidence | CI artifacts | 90 d |
| Release bundles | Git release assets + repo `releases/` | forever |

# Chapter 25 — Release engineering

## 25.1 Versioning

`versionName = MAJ.MIN.PAT` (user-visible), `versionCode = MAJ*10000+MIN*100+PAT*10+flavorBit` (full=0, mycalc=1, keeping the owner's monotonic scheme familiarity). Release candidates: `3.13.0-rc1` locally, stripped on tag.

## 25.2 Signing

Keystore generated once in CI secrets flow (owner-held backup is an owner action item at G1); PKCS12, RSA-3072, 25-year validity; `sigv1+sigv2+sigv3` enabled for sideload compatibility. Signing happens only in the release lane; the keystore never touches the workspace outside the secret mount; public SHA-256 of the signing cert is published in the About screen + reports (owners can verify install provenance).

## 25.3 Shrink and hardening

R8 full + resource shrink; keep rules minimal (reflection only in AI JNI bridges — pinned rules); `-allowaccessmodification`; debug metadata stripped except line info (crash-free local symbolication via committed `mapping.txt` per release into the evidence bundle).

## 25.4 Pre-flight checklist (automated)

S1–S8 re-run on the exact release artifacts; zero-permission flavor assert; size budgets; reproducibility double-build; L5 release run green (blocked items enumerated); docs regenerated; licenses regenerated; About provenance matches. Any red → no release, defect filed (§20.9).

## 25.5 Release artifacts (the bundle)

```
releases/v3.13.0/
  myspace-one-3.13.0-<code>-release.apk
  mycalc-1.1.0-<code>-release.apk
  qa/qa-summary.json + report.pdf (L5 report of record)
  evidence/ (manifest-verified screenshots, logs, law-suite results)
  docs/ (blueprint PDF, traceability.csv, api-surface.txt, LICENSES.md)
  RELEASE-NOTES.md (human, short, honest: features, fixes, blocked register)
```

## 25.6 Distribution (owner model)

Direct sideload via the owner's existing pattern (GitHub-hosted artifacts on the repo/branch the owner controls) + pack files distributed alongside with their SHA-256 manifest. In-app updater: none (no network, by design) — update = install-over, tested with signature-continuity check (TC-SEC-upgrade: v(n)→v(n+1) install-over preserves data through Room migrations).

## 25.7 RELEASE-NOTES.md template

```markdown
## MySpace One 3.13.0 (code 31300) · MyCalc 1.1.0 (code 11100)
Date / provenance: commit <sha>, CI run <id>, APK SHA-256 <…>

### Highlights
- Calculator: [user-visible changes only]
- Notes / Scanner / …: …

### Fixes
- …

### Honest register
- Blocked during QA: [list with reasons and device-test recommendations]
- Known limitations: [e.g., ICS RRULE subset]

### Upgrade notes
- Install over the previous version; data migrates automatically (tested: v(n)→v(n+1)).
- Backups made by newer versions cannot be restored by older versions.
```

## 25.8 Signing ceremony (normative steps)

```
# One-time (G1): generate in CI secret store
keytool -genkeypair -v -keystore msone-release.p12 -alias msone   -keyalg RSA -keysize 3072 -validity 9125   -dname "CN=MySpace One, O=Owner"
# Owner action: download + verify passphrase + store offline (two copies) → rehearse restore
# Release lane: mount secret → gradle signReleaseBundle → verify
apksigner verify --print-certs myspace-one-release.apk   # cert SHA-256 recorded in evidence + About
# Tag the keystore fingerprint into reports (provenance continuity across versions)
```

Loss of the key after first public release = cannot install-over (new key = uninstall). The G1 rehearsal (owner re-imports keystore from backup into a clean runner and signs a test APK) is the cheapest insurance in the whole program (R-010).

## 25.9 Release QA session script (the G7 instrument)

```
1. gradle assembleFullRelease assembleMycalcRelease        → record SHAs
2. Reproducibility: rebuild both → SHA equal? (fail = stop)
3. Install both on E33B (airplane ON):
   a. run L5 release profile (Appendix Q scripts verbatim)
   b. J-05, J-06, J-10 on the *release* artifacts
4. Owner-device optional pass for B2-class gestures
5. Diagnostics self-test on device → JSON into evidence
6. Assemble bundle (§25.5), verify manifest, build PDF of record
7. Pre-flight checklist §25.4 → G7 sign-off pack
```

Every step emits into `releases/v<ver>/qa/…`; the session is re-runnable byte-for-byte from the script (deterministic session — the owner can watch any step).

## 25.10 Filled RELEASE-NOTES example (illustrative v3.13.0)

```markdown
## MySpace One 3.13.0 (code 31300) · MyCalc 1.1.0 (code 11100)
2026-12-18 · commit 9c4ef21 · CI run 4123 · full APK sha256 8f31… · mycalc sha256 2b7d…

### Highlights
- Calculator: exact engine — `1÷3×3 = 1`, percent chains, Google-style pending operators.
- Selection memory: hold any number → Cut/Copy/MAdd/MUse/Paste.
- Notes: checklists, full-text search, optional on-device AI actions (preview + undo).
- Scanner: documents to clean PDFs with on-device OCR.
- Calendar: recurrence + exact reminders, ICS import/export.
- Files: private + SAF browsing, storage analyzer, encrypted backup/restore.
- Music and Recorder: gapless playback, speed, sleep timer; recordings with markers.
- Diagnostics: self-test, model-pack manager, share-with-preview logs.

### Fixes
- First release.

### Honest register
- Blocked during QA: stationary hold-then-drag selection needs a physical device
  (emulator input limitation). Everything else in Catalogue-0: PASS.
- Known limitations: OCR v1 is Latin-script; ICS import supports the documented
  RRULE subset; Assistant pack needs an 8 GB-class device.

### Upgrade notes
- First release: install fresh. Backups from this version restore here and in later versions.
```

## 25.11 Bundle verification commands (owner-runnable)

```bash
sha256sum myspace-one-3.13.0-31300-release.apk   # == About screen + release notes
apkanalyzer manifest print …apk | grep uses-permission   # expected list only
python3 tools/verify_manifest.py releases/v3.13.0/        # checks evidence-manifest.json
```

# Chapter 26 — Post-release operations (G8)

## 26.1 Support model

The Diagnostics module is the support surface: self-test card, log share (user-initiated), pack manager, and the About provenance block — an owner receiving a friend's bug report asks for exactly these three things. Support runbook (`docs/ops/runbook.md`): triage by severity template, evidence request templates, known-issue list from the defect ledger.

## 26.2 Update cadence and backports

Patch releases for S1/S2 defects (engine/data correctness first); minor for P1 completions; the blueprint version-bumps with each minor. Backport policy: only to the latest minor. Every update release re-runs the full release lane (no "quick builds" — C10 applies forever).

## 26.3 EOL and data exit

If the program ends: last release ships with a built-in "Export everything" deep action (Settings → Privacy → Export all data → `.msone` unencrypted option) and the docs note key escrow-free backup reality (user passphrases are the only keys; lost passphrase = lost backup — disclosed at backup creation, §14.3).

## 26.4 Support playbook (triage decision tree)

```
Report arrives → ask for Diagnostics self-test JSON + shared log (user-initiated)
├─ self-test fails engine/DB  → S1/S2 defect, reproduce via fixture seed, fix + law re-run
├─ self-test fails pack hash  → guide re-import of pack (corrupt transfer), no code change
├─ alarm missed              → check canScheduleExactAlarms in log slice → OEM policy doc + fallback notice
├─ SAF oddity                → capture root URI pattern → §13.6 map → workaround task
└─ UX complaint              → ledger entry; batch into next minor; never silent-fix without traceability
```

## 26.5 Support FAQ (owner-facing, from the runbook)

| Symptom | First response |
|---|---|
| "Reminder didn't ring" | Settings → Calendar shows exact-alarm status? Share self-test JSON (step 5). OEM battery settings guide. |
| "Backup won't open" | Passphrase is case-sensitive; version note: newer backups need the newer app. |
| "Music files missing after cleanup" | Files → Media folders re-grant; library rescan button in Music → ⋮ |
| "Recording stopped by itself" | Check diag ring: call interruption vs storage event; file kept to pause point (by design). |
| "AI button greyed" | Diagnostics → Model packs → install/import the named pack; check device tier note. |
| "App is slow on old phone" | Tier C expectations §3.2; effects default off; try battery-saver-aware mode. |

## 26.6 Owner feedback loop

Feedback enters exactly like defects: the owner's observation → ledger/defect entry (with the owner's own evidence style — screenshots welcome) → triage per Appendix U → fix in the normal loop with `Refs:` traceability. Feature wishes compete in the v1.1 backlog by the same priority rules as everything else — the owner's word is the spec, and the spec is versioned.

## 26.7 Update announcement template (owner channel)

```
MySpace One v3.13.1 is out (MyCalc unchanged at 1.1.0).
Install-over: open the APK, allow install, done — your data stays.
Highlights: <2-3 bullets from RELEASE-NOTES>
Verify: Diagnostics → About shows build 31301 / commit <sha7>.
Full report: <link to the release bundle PDF>
```
