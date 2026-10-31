@PART: PART IV — ARCHITECTURE AND DATA
@PARTDESC: Layered architecture, module boundaries, the complete data model with schemas and migrations, per-module technical deep dives, and security/privacy engineering. This part converts product promises into a structure an agent can build without drift.

# Chapter 11 — System architecture

## 11.1 Layered view

![Normative layer diagram: UI, feature, core domain, data, AI runtime, Android platform.](figures/fig-architecture.png)

Six layers with **strict downward-only dependencies**:

1. **UI (Jetpack Compose)** — screens, components from `core/designsystem`, navigation host, per-module `Navigator`. No business logic; ViewModels only via DI.
2. **Feature** — one Gradle module per module (`feature/calculator`, `feature/notes`, …). Holds ViewModels, use-case classes, permission flows, feature contracts. Talks to core via interfaces.
3. **Core domain** — pure Kotlin: calculator engine, recurrence engine, note document model, search indexer, settings model, result types. No Android imports — runs on the JVM in unit tests.
4. **Data** — Room databases, DataStore, SAF repository, MediaStore bridge, file repository, encrypted backup. Owns all I/O.
5. **AI runtime** — ONNX Runtime Mobile, LiteRT, whisper.cpp JNI, MediaPipe LLM, system TTS bindings. A *leaf*: nothing in it knows about features.
6. **Android platform** — CameraX, Media3, AudioRecord, AlarmManager, WorkManager, Keystore, BiometricPrompt, notifications.

Rule enforcement: a Konsist-style architecture test (§20.3) fails the build if a layer import violates the arrow. The AI runtime being a leaf means a broken model pack can never break a feature compile.

## 11.2 Module map (Gradle)

```
myspace-one/
  app/                      # flavors: full (app.space.one), mycalc (app.space.calc)
  feature/calculator/       # + mycalc flavor reuses this wholesale
  feature/notes/  feature/scanner/  feature/calendar/
  feature/files/  feature/music/    feature/recorder/
  feature/diagnostics/      # health, logs, pack manager (hub is separate):
  feature/hub/              # home, search, continue row
  feature/settings/
  core/designsystem/        # tokens, theme, components, icons
  core/domain/              # engines + models (pure Kotlin)
  core/data/                # Room, DataStore, SAF, backup
  core/ai/                  # orchestrator + runtime bindings
  core/common/              # dispatchers, logging, result types
  core/testing/             # fakes, fixtures, screenshot harness
```

Dependency rules: `feature/* → core/*` only; `feature↛feature` (hub reaches modules through contracts in `core/domain`); `core/data ↛ core/ai`; `app` wires everything with Hilt. Each module has its own lint baseline and test source set; CI can run module-scoped test tasks in parallel within the 3-runner cap by sharding (§24.2).

## 11.3 Key architectural decisions (ADR digest)

| ID | Decision | Rationale | Rejected alternative |
|---|---|---|---|
| ADR-01 | Single-Activity + Compose Navigation | State restoration, predictive back, one theme owner | Multi-activity (state loss on process death) |
| ADR-02 | Room + FTS4 (not FTS5) for search index | FTS4 ships with API 26+ SQLite unconditionally; FTS5 needs newer SQLite than API 26 guarantees | FTS5, custom index |
| ADR-03 | DataStore (not SharedPreferences) | Coroutines-first, transactional, typed | SharedPreferences |
| ADR-04 | Koin over Hilt | Kapt/KSP-free fast builds on 2-runner CI budget | Hilt |
| ADR-05 | Media3 ExoPlayer for Music; AudioRecord+MediaCodec for Recorder | Media3 has no meaningful offline recorder gap to fill; raw capture gives markers + pause | MediaPlayer (no gapless/speed) |
| ADR-06 | ONNX Runtime Mobile as primary AI runtime; LiteRT only where a model exists only as .tflite | One runtime = one memory pool, one NNAPI delegation path | Two runtimes everywhere |
| ADR-07 | Event bus avoided; Kotlin SharedFlow per feature | Testability, no global pub/sub spaghetti | Event bus |
| ADR-08 | All dates stored as epoch-millis UTC + original tz offset | DST-safe recurrence, ICS interop | Local-time strings |
| ADR-09 | App-private storage default; SAF only where the user grants | C4 privacy constraint | MANAGE_EXTERNAL_STORAGE (play-policy and trust cost) |
| ADR-10 | No WorkManager for user-visible jobs; alarms for reminders, coroutines for the rest | WorkManager persists through reboots but adds unpredictability for a no-network app; reminders need exact alarms anyway | WorkManager everywhere |

## 11.4 Threading and concurrency

- One `Dispatchers.Default` pool for compute (engine, OCR pre/post); a single-thread `Dispatchers.IO` queue per repository for writes (keeps SQLite happy); `Dispatchers.Main` never blocks.
- The calculator engine evaluates on the main thread *only* for expressions ≤ 64 chars (measured < 1 ms, §17.1.6 budget); longer/deeper forms hop to Default with a 50 ms budget and cancel on keystroke.
- Recorder service owns its own thread + handler; database writes marshalled through the repository queue.
- AI orchestrator: at most 2 concurrent model jobs (Tier B) / 1 (Tier C) with a cancel-on-new-request policy for UI-bound jobs (§16.6).

## 11.5 Error architecture

All repository/engine calls return `Result<T, AppError>`; `AppError` is a sealed hierarchy (`Storage`, `Input`, `Policy` (e.g., exact-alarm revoked), `Model` (pack missing/corrupt), `Internal`). UI maps each to the §7.11 states table. No exception crosses a module boundary; crash-causing states are caught at the last handler, logged to the diagnostics ring (§28.3), and the app attempts state-preserving restart of the screen (never silently dies).

## 11.6 Dependency injection graph

Koin modules declared per Gradle module and aggregated in `app/di.kt`:

```
commonModule     : DispatcherProvider, AppClock, AppLogger
dataModule       : AppDatabase, all DAOs, DataStore, LocalRepo, SafRepo, BackupManager
domainModule     : CalcEngine (singleton, stateless), RecurrenceEngine, NoteDocCodec,
                   SearchIndexer, SettingsRegistry
aiModule         : PackRegistry, AiOrchestrator, runtime bindings (lazy by pack)
featureModule(s) : per-module ViewModels + use-cases (factory scope)
navigationModule : NavGraph providers per feature, HubSearchAggregator with sources
```

Rules: singletons only for stateless engines, DB, orchestrator registry; ViewModels factory-scoped; no service locator access from composables (architecture test). The DI graph is startup-profile friendly (default-optimized dex layout generated at G6).

## 11.7 Data flow examples (end-to-end traces)

| Flow | Trace |
|---|---|
| Keystroke `7` | Compose key → ViewModel.onKey → ExpressionStore (state) → engine live-answer job (≤ 1 ms) → UI update + debounce-persist SavedState/DataStore → (on `=`) history DAO insert on repo queue |
| Save note | Editor change → NoteDocCodec.encode → NoteRepo.upsert (Room txn: note+FTS trigger) → indexer embeddings enqueue (pack) → continue-row DataStore update |
| Reminder fire | AlarmManager broadcast → ReminderReceiver (not exported) → read event → notification on `reminders` channel → tap opens event screen (deep link) |
| Record tap | Activity → RecorderController.start → FGS start (≤ 200 ms) → AudioRecord thread → muxer; marker taps → repo queue inserts |
| Scan to note | CameraX capture → page store → OCR job (orchestrator) → card edit → "→ Notes" → NoteRepo.create(body=ocrText, sourceScanId) → Files registers attachment |

Each trace has an instrumented test asserting the visible endpoints (no internal spying beyond fakes) — the traces table is the review map for TC-JOURNEY cases.

## 11.8 Architecture test exemplar (Konsist-style, runs in fast lane)

```kotlin
@Test fun `features depend only on core layers`() =
    scopes.modules().withFeaturePrefix().files
        .shouldNotImport { it.imports "space.one.feature." }          // no feature→feature
@Test fun `ai runtime is a leaf`() =
    scopes.module("core/ai").files
        .shouldNotImport { it.imports "space.one.feature." }
@Test fun `no network symbols anywhere`() =
    scopes.all().files.shouldNotImport {
        it.imports "java.net.*", "okhttp3.*", "android.webkit.*"
    }
@Test fun `compose files use token colors`() =
    scopes.modules().withFeaturePrefix().files
        .withExtension("kt").shouldNotContainPattern("Color\\(0x")
```

These four tests encode §11.1, §14.2 and §18.1 as executable law — architecture violations fail in under a minute, long before review.

## 11.9 Threading ownership table (who runs what, where)

| Work | Dispatcher | Notes |
|---|---|---|
| Compose UI + state reads | Main | never blocks |
| Engine evaluate (≤ 64 chars) | Main | measured < 1 ms |
| Engine evaluate (long) | Default | 50 ms cap, cancel-on-input |
| Room reads | IO (repo queue per DB) | serial writes |
| File copies/moves | IO (per-repo queue) | progress via Flow |
| Camera/OCR pre-post | Default | capture on camera thread |
| AI model inference | Default (single job lane) | tier caps §16.6 |
| Recorder audio | own handler thread | FGS contract |
| Alarms | Main (receiver) → IO | ≤ 10 s receiver budget |

# Chapter 12 — Data architecture

## 12.1 Stores overview

| Store | Tech | Contents |
|---|---|---|
| `msone.db` | Room (SQLite) | All structured data (tables below), schema `v1` |
| `prefs` | DataStore | Settings, key themes, effects, first-run flags |
| `files/` | App-private FS | Scans, recordings, attachments, exports, backups |
| `indexes/` | Files | Embedding vectors (binary), search metadata |
| Clipboard/SAF | External | Only via explicit user action |

## 12.2 Relational schema (v1)

![Room schema v1: calculator, notes, scans, calendar, music and recorder tables.](figures/fig-erd.png)

DDL (abridged, normative for column names/types):

```sql
CREATE TABLE CalcHistory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  expression TEXT NOT NULL,        -- canonical ASCII form (§17.1.3)
  result TEXT NOT NULL,            -- exact rendered string (grouped at display time only)
  createdAt INTEGER NOT NULL,      -- epoch millis UTC
  pinned INTEGER NOT NULL DEFAULT 0);
CREATE INDEX idx_calc_history_created ON CalcHistory(createdAt DESC);

CREATE TABLE MemorySlot (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  value TEXT NOT NULL,             -- exact numeric string
  label TEXT,                      -- user label (optional)
  updatedAt INTEGER NOT NULL);

CREATE TABLE Note (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL DEFAULT '',
  bodyJson TEXT NOT NULL,          -- NoteDoc JSON (§17.3)
  plainText TEXT NOT NULL,         -- denormalized for FTS + snippets
  createdAt INTEGER NOT NULL, updatedAt INTEGER NOT NULL,
  trashedAt INTEGER,               -- NULL = live; else 30-day trash
  pinned INTEGER NOT NULL DEFAULT 0,
  color INTEGER NOT NULL DEFAULT 0);
CREATE VIRTUAL TABLE NoteFts USING FTS4(
  title, plainText, content=`Note`, tokenize=unicode61);

CREATE TABLE ScanDoc (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pageUrisCsv TEXT NOT NULL,       -- app-private file paths
  ocrText TEXT NOT NULL DEFAULT '',
  createdAt INTEGER NOT NULL,
  noteId INTEGER REFERENCES Note(id) ON DELETE SET NULL);

CREATE TABLE CalEvent (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  startUtc INTEGER NOT NULL, endUtc INTEGER NOT NULL,
  startTzOffsetMin INTEGER NOT NULL,   -- original zone
  allDay INTEGER NOT NULL DEFAULT 0,
  rrule TEXT,                      -- NULL = one-off
  reminderOffsetMin INTEGER NOT NULL DEFAULT 15,
  color INTEGER NOT NULL DEFAULT 0,
  note TEXT NOT NULL DEFAULT '',
  icsUid TEXT, exDatesCsv TEXT);

CREATE TABLE Track (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mediaStoreId INTEGER, folderUri TEXT, relativePath TEXT,
  title TEXT NOT NULL, artist TEXT, album TEXT,
  durationMs INTEGER NOT NULL, sizeBytes INTEGER, trackNo INTEGER,
  artworkPath TEXT, lastPlayedAt INTEGER);

CREATE TABLE Playlist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, createdAt INTEGER NOT NULL);
CREATE TABLE PlaylistEntry (
  playlistId INTEGER REFERENCES Playlist(id) ON DELETE CASCADE,
  position INTEGER NOT NULL, trackId INTEGER REFERENCES Track(id),
  PRIMARY KEY(playlistId, position));

CREATE TABLE Recording (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filePath TEXT NOT NULL, durationMs INTEGER NOT NULL,
  format TEXT NOT NULL DEFAULT 'aac', sizeBytes INTEGER,
  createdAt INTEGER NOT NULL, trashedAt INTEGER,
  transcript TEXT, transcriptSegmentsJson TEXT);
CREATE TABLE RecordingMarker (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  recordingId INTEGER REFERENCES Recording(id) ON DELETE CASCADE,
  offsetMs INTEGER NOT NULL, label TEXT NOT NULL DEFAULT '');
```

## 12.3 Migration and integrity policy

- Schema changes ship as numbered Room `Migration`s with unit tests over exported schemas (`core/data/schemas/`), auto-migration only for additive cases.
- Every app start runs `PRAGMA quick_check` in Diagnostics' data (not blocking launch); a failure surfaces the Diagnostics error state with backup guidance — never auto-deletes.
- WAL mode ON; `busy_timeout` 3 s; all writes through the repository queue (§11.4).

## 12.4 Backup format (`.msone`)

Zip (deflate) of: `manifest.json` (schema version, app version, counts, SHA-256 of each member), `data.json` (all tables), `files/…` (recordings, scans, attachments). Encryption (optional but default): AES-256-GCM; key = PBKDF2-HMAC-SHA256 (210 000 iterations, 16 B salt) from the user's passphrase; passphrase never stored. Restore is transactional: verify all hashes → stage in `files/incoming-restore/` → swap → vacuum. A failed restore leaves the original data untouched (J-03).

## 12.5 Search indexing pipeline

- On write: Note/Scan/Recording triggers FTS update (Room trigger) + a cheap local embedding of the first 2 000 chars when the Essentials pack is enabled (batched, ≤ 50 ms budget per note, queued).
- Vectors stored in `indexes/vectors.bin` (f32, one row per item, L2-normalized); hub search = FTS top-50 ∪ cosine top-50 (only when pack on), merged with a stable score (FTS rank primary, cosine tiebreak).
- Rebuild commands exist in Diagnostics (FTS rebuild, embeddings rebuild) for support scenarios.

## 12.6 State restoration contract

Per-screen SavedState keys are registered in a single `RestoreKeys` object; the continue-row reads from a small `LastSession` DataStore record updated debounced 500 ms: last module, last screen, last expression, draft note id, recording id. Calculator additionally persists its live expression+caret+selection on every change (guide-critical: B-journeys survive death). Process-death restoration is tested by TC-STATE-* cases including the J-06 storm.

## 12.7 Index catalog (all indexes in schema v1)

| Table.Index | Columns | Serves |
|---|---|---|
| CalcHistory.created | createdAt DESC | history sheet order + LRU eviction |
| Note.updated | updatedAt DESC | list sort default |
| Note.trashed | trashedAt | trash sweep |
| CalEvent.start | startUtc | month window queries |
| CalEvent.reminder | reminderOffsetMin partial (WHERE rrule NOT NULL or one-off) | next-reminder scan |
| Track.album / Track.artist | albumId/artist cols | library tabs |
| PlaylistEntry.pk | (playlistId, position) | queue order |
| Recording.created | createdAt | list order |
| RecordingMarker.rec | recordingId, offsetMs | marker list + seek |
| NoteFts | FTS4(title, plainText) | search |

## 12.8 Query pattern contracts (perf-relevant SQL, all via Room)

- Month window: `SELECT * FROM CalEvent WHERE endUtc >= :winStart AND startUtc <= :winEnd` (index range scan).
- Next reminders: `SELECT ... WHERE startUtc + reminderOffset*60000 BETWEEN now AND now+86400000` — re-armed at boot and after edits.
- History page: `SELECT * FROM CalcHistory ORDER BY createdAt DESC LIMIT 50 OFFSET ?` (pinned first: `UNION` with pinned subset).
- Note list page: title+snippet projection, `LIMIT 100` keyset by updatedAt (`WHERE updatedAt < :cursor`), never OFFSET on large sets.
- FTS search: `SELECT rowid, ... FROM NoteFts WHERE NoteFts MATCH :q` joined to Note; snippet() for highlight.

## 12.9 Entity field dictionaries (complete executor reference)

`CalcHistory` — `id` rowid PK · `expression` canonical ASCII (§17.1.3) · `result` exact rendered-canonical string (ungrouped) · `createdAt` epoch ms UTC · `pinned` 0/1.

`MemorySlot` — `id` PK · `value` exact numeric string (never float) · `label` optional user label ≤ 40 chars · `updatedAt` epoch ms.

`Note` — `id` PK · `title` derived-but-stored (first heading/line, ≤ 200 stored) · `bodyJson` NoteDoc v1 (§17.3) · `plainText` projection for FTS/snippets (marks stripped, `
` per block) · `createdAt/updatedAt` epoch ms · `trashedAt` null or epoch ms (sweep at +30d) · `pinned` 0/1 · `color` index into 6-swatch palette.

`NoteFts` — content-linked FTS4 mirror of (`title`, `plainText`); rebuilt via `INSERT INTO NoteFts(NoteFts) VALUES('rebuild')` command in Diagnostics.

`ScanDoc` — `id` PK · `pageUrisCsv` ordered page file names (private `Scans/`) · `ocrText` concatenated page text · `createdAt` · `noteId` nullable link (SET NULL on note delete).

`CalEvent` — `id` PK · `title` ≤ 200 · `startUtc/endUtc` epoch ms (all-day: local midnight normalized with `startTzOffsetMin` preserving the creating zone) · `startTzOffsetMin` original offset · `allDay` 0/1 · `rrule` subset string or null · `reminderOffsetMin` −1=none, else 0..1440 · `color` palette index · `note` ≤ 2000 chars · `icsUid` import dedup key · `exDatesCsv` ISO dates.

`Track` — `id` PK · `mediaStoreId` nullable · `folderUri+relativePath` SAF address or MediaStore data · `title/artist/album` tags (fallbacks: filename/`Unknown`) · `durationMs/sizeBytes/trackNo` · `artworkPath` cache file or null · `lastPlayedAt` epoch ms.

`Playlist/PlaylistEntry` — name unique per user view (not enforced in DB); entries ordered by `position` (compacted on reorder); FK cascade on playlist delete.

`Recording` — `id` PK · `filePath` private path · `durationMs` (timeline excludes paused spans) · `format` `aac/wav` · `sizeBytes` · `createdAt` · `trashedAt` · `transcript` full text with provenance header line · `transcriptSegmentsJson` `[{s,e,t}]`.

`RecordingMarker` — `id` PK · `recordingId` FK cascade · `offsetMs` timeline position · `label` ≤ 40 chars.

`diag_ring` — §28.5.

## 12.10 Backup `data.json` shape (normative)

```json
{"format":"msone","schema":1,"appVersion":"3.13.0","exportedAt":1769900000000,
 "tables":{"CalcHistory":[…], "MemorySlot":[…], "Note":[…], "ScanDoc":[…],
           "CalEvent":[…], "Track":[…], "Playlist":[…], "PlaylistEntry":[…],
           "Recording":[…], "RecordingMarker":[…]},
 "files":["recordings/REC-20261027-133601.m4a", "scans/page-0001.jpg"],
 "counts":{"Note":42,"CalEvent":17}}
```

Restore verifies: format, schema ≤ current, member hashes, counts vs `tables` lengths, then transactional swap. Files restore to identical relative paths; collisions impossible (staging swap).

## 12.11 Query performance validation (fixtures vs budgets)

| Query | Fixture scale | Budget | Measured target |
|---|---|---|---|
| History page 50 | 500 rows | 8 ms | index range scan |
| Note list page 100 | 20k notes | 15 ms | keyset by updatedAt |
| FTS search `engine` | 20k notes | 25 ms | FTS4 match + join limit 50 |
| Month window 3 months | 3k events | 5 ms | start/end index |
| Library songs page | 50k tracks | 15 ms | album/artist index |
| Recording + markers | 5k recordings | 10 ms | FK index |
| Hub aggregate first page | all of the above | 120 ms | parallel sources, 25 ms caps |

Validation runs as a JUnit perf test on the seeded corpora (Appendix K) in the nightly lane; regressions > 2× budget fail.

## 12.12 DataStore schema (prefs store, normative keys)

```
settings.<registry-key>            # §17.7 + §17.12, typed via registry
session.lastModule / .lastScreen   # continue-row
session.calc.expression/.caret/.sel
stats.moduleOpens.<module>          # counters (clearable)
hub.recentSearches                  # string list, max 10
firstRun.<card-id>                  # shown-once flags
```

One DataStore file (`prefs.preferences_pb`); all access via `SettingsRegistry` and `SessionStore` — feature code never touches DataStore directly (architecture test).
