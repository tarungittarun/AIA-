@PART: PART IV — ARCHITECTURE AND DATA
@PARTDESC: Module boundaries, the Android stack, the Room schema, the journal and version system that make keystroke loss impossible, and the concurrency rules that keep the main thread boring.

# Chapter 10 — Architecture

## 10.1 Shape

![OneDoc architecture: feature modules over six core libraries over the Android platform, with the verification pyramid underneath.](figures/fig-architecture.png)

Single process, Kotlin-first, View-based UI (no experimental-UI dependency risk on API 26), modularized by Gradle:

| Module | Owns | Never contains |
|---|---|---|
| `app` | Navigation, DI graph, themes, home, settings | Business logic |
| `feature-editor` | Editor screen, toolbars, sheets | Persistence, IO |
| `feature-home`, `feature-templates`, `feature-scan`, `feature-assistant`, `feature-search` | Their screens | Each other |
| `core-model` | Document, Block, Mark, Op — pure Kotlin, no Android imports | Anything impure |
| `core-editor` | Operation engine, undo, IME bridge, layout metrics | UI classes |
| `core-storage` | Room DB, .odoc container, journal, versions | UI, formats |
| `core-io` | md/txt/html/pdf/docx readers+writers | DB access |
| `core-ai` | Pack manager, OCR, ASR, LLM runtime, embeddings | UI, DB writes |
| `core-search` | FTS5 indexing, vector index, ranking | Editor |

Dependency rule: arrows point downward only (`feature-*` → `core-*` → platform). `core-model` depends on nothing. Tests exist at every level; the highest proof is the direct-APK pipeline (Part X).

## 10.2 Threading model (§10.2 normative)

1. The **main thread** does UI and nothing else; any work over 4 ms measured at P95 moves off it.
2. One **storage executor** serializes all Room writes; the journal append is synchronous from the editor's perspective (write-ahead, §12.3) but executes on this executor with a bounded queue of 1 pending op batch.
3. **IO executors** (2 threads) run imports/exports/backups; cancellation is cooperative and checked at every file boundary.
4. **AI executors** (1 per active capability, max 2 concurrent) run OCR/ASR/LLM; priority: user-initiated action > background indexing.
5. Main-thread disk IO is a defect (category S-PERF, §25.3); strict-mode is enabled in debug builds and CI instruments it in tests.

## 10.3 Dependency and build hygiene

Version catalog for all deps; no dynamic versions (`+`); no annotation-processor beyond Room compiler and Hilt; R8 full-mode with keep rules owned by this repo; dependency deny-list enforced in CI (C1–C3): any artifact under `com.google.ads`, `com.facebook.ads`, `com.applovin`, `io.branch`, `com.mixpanel`, `com.amplitude`, `com.bugsnag`, `io.sentry`, or any `*analytics*` coordinate fails the build. New dependencies require a D-nnn ledger entry with an offline/no-telemetry justification.

# Chapter 11 — Data layer

## 11.1 Entity model

![Room schema v3: documents, versions, assets, FTS index, vectors, meta.](figures/fig-erd.png)

| Table | Purpose | Notable columns |
|---|---|---|
| `documents` | One row per document | `id` (text, `d_` + 8 hex), `title`, `updatedAt`, `wordCount`, `starred`, `deletedAt?`, `schemaVersion` |
| `versions` | Snapshot blobs (zip of document.json + asset manifest) | `docId`, `createdAt`, `kind` (auto/manual/pre_edit), `sizeBytes` |
| `assets` | Images etc. stored app-private | `docId`, `kind`, `path`, `sha256` |
| `docs_fts` | FTS5 over title+plain text | external-content mapped to a `doc_blocks` shadow table (block-level hits for §3.2 N5 deep-links) |
| `vectors` | MiniLM embeddings per block | `docId`, `blockId`, `embedding` (f32 blob), `model` |
| `meta` | Schema version, settings, pack registry | key-value |

## 11.2 The document payload

Authoritative content is a single `document.json` per document (schema in §14.2), stored zipped in app-private files, with the Room row as the index — never the other way. The database can be rebuilt from files + journal (the reverse is not true), which is what makes backup/export honest and crash recovery provable.

## 11.3 Journal

Every committed operation batch appends a framed, CRC-checked record to `<docId>.journal` (length-prefixed, fsync'd batch) **before** the debounced model save. On open, if the model file is newer than the last checkpoint, the journal replays forward. Compaction: at 512 records or 2 MB, fold into a new checkpoint file. The journal is the reason UX-11 can promise zero loss under `kill -9`.

## 11.4 Schema migrations

Room schema exports versioned JSON; each migration ships with (a) an up-test using a synthetic v(n-1) database from `core-storage/src/test/resources/`, (b) a dry-run against the seed corpus (§23.2), (c) a rollback *plan* (restore from journal + backup) documented in the migration notes. TC-STATE-007 runs the full v1→vN chain on emulators.

## 11.5 Encryption and privacy

Android Keystore-generated key (AES-256-GCM) encrypts the document store directory on devices with a lock-screen credential (StrongBox when available); on credential-less devices files stay app-private (sandbox) with a clear statement in About. The backup zip (F-060) is created in app cache and handed to SAF; it is encrypted with a user-passphrase-derived key (PBKDF2, 200k iterations) — the passphrase prompt is the only dialog in OneDoc that exists for security, and it explains itself in one line.

# Chapter 12 — State, versions and the autosave pipeline

## 12.1 One document's life

![From keystroke to journal to debounced save to snapshots to restore points.](figures/fig-versioning.png)

## 12.2 Snapshot policy (F-061 normative)

| Kind | When | Kept |
|---|---|---|
| `auto` | 5 min of activity or 50 committed op batches, whichever first | last 20 per doc |
| `manual` | "Save version" action | unlimited until user deletes |
| `pre_edit` | Before replace-all, AI insert/replace-all, import-merge, version restore | last 5 per doc, never auto-pruned |

## 12.3 Crash-consistency rules (Law L3 machinery)

1. Journal record written+fsynced **before** ack of the edit batch in memory.
2. Model save (checkpoint + Room index update) is debounced 800 ms and always follows a checkpoint fold or journal replay boundary — never mid-batch.
3. On any open: `replay(journal) → validate CRC → repair or quarantine`. A quarantined journal is preserved byte-exact and the document opens at its last good state with a diagnostic note; data is never silently dropped.
4. `TC-STATE-005` proves the chain with instrumented kills at randomized points (100 trials); UX-11 is its user-facing promise.

## 12.4 Multi-window and process death

The editor is `singleTask`; a second launch intent brings the existing instance forward. Configuration changes (rotation, split, resize) never recreate the editor activity: state lives in a retained editor core; the view layer re-binds (TC-STATE-002). Process death restores via journal replay + saved scroll/cursor snapshot (F-030).

## 10.4 The DI graph (Hilt)

Components: `SingletonComponent` holds storage (DB, container store, journal service), pack registry, executors, token store (themes); `ActivityRetainedComponent` holds editor cores (one per open document, max 2); `ViewModelComponent` holds screen state. Rules: no `@Singleton` may hold a `Context` beyond `ApplicationContext`; no DI scope may reference UI classes; the editor core is created by an explicit `EditorCoreController` (not inject-on-demand) so its lifecycle (open → active → idle-saved → closed) is testable without UI.

## 10.5 Error-handling strategy (one taxonomy app-wide)

Every failure is a sealed `OdError` with three user-facing verbs: **retryable** (transient IO — auto-retry ≤ 3 with backoff, then calm banner), **actionable** (needs the user — specific reason + exactly one action button), **reportable** (engine invariant violated — quarantine + diagnostics entry + one-line apology, never a stack trace dialog). User strings live in the strings catalog; no error text is composed ad hoc in feature code (lint-enforced). The mapping error→verb is table-driven in `core-model/errors` so tests can enumerate it exhaustively (every error kind has a string and a verb — asserted within the TC-SET-004 strings tests).

## 11.6 On-disk layout (normative)

```
files/
  docs/<docId>/document.json(.zip)     # authoritative content
  docs/<docId>/journal                 # CRC-framed op log (§11.3)
  docs/<docId>/checkpoints/<n>.json.zip
  assets/<sha256>.<ext>                # content-addressed images etc.
  packs/<packName>/                    # verified side-loaded packs (§19.6)
  tmp/export|import|backup/            # lifecycle-managed temp (§20.3)
databases/onedoc.db (+ -wal, -shm)     # Room index (rebuildable, §11.2)
```

Invariant: `databases/` can be deleted and rebuilt from `files/docs` (the integrity self-test F-089 verifies this rebuildability on a sample document). Nothing under `files/` is world-readable; `tmp/` is cleared on start and after each operation completes or cancels.

## 12.6 Clocks and time

Documents store UTC epoch millis; display uses relative formatting ("2 h ago", locale-aware absolute after 7 days). Snapshot timing uses `SystemClock.elapsedRealtime` deltas (immune to wall-clock jumps); exported files embed wall time in metadata only (excluded from golden comparison, Law L6). Time-zone and clock-change torture is part of TC-STATE-006 (set clock forward/back across a save → no snapshot storm, no ordering flip).

## 11.7 Indexes and query plans

Room indices: `documents(deletedAt, updatedAt)` (library list), `documents(starred)` partial where starred=1, `versions(docId, createdAt)`, `assets(docId)`, `vectors(docId, blockId)` unique. FTS5 external-content with prefix index; `doc_blocks` shadow carries `(docId, blockIdx, plainText)`. The library list query is a single indexed scan + counts (EXPLAIN QUERY PLAN checked in a unit test — "no full scans on the hot path" is a test, not a hope). Search query plan: FTS MATCH → join to documents for title/updated → snippet materialization limited to top 50 hits. Any schema change re-runs the plan tests (schema checklist §29.5).

## 12.7 Compaction and vacuum runbook

Journal compaction (§11.3) triggers at 512 records/2 MB during open or idle (never during active composition — Law L5 respects the queue). Compaction = fold journal onto checkpoint → fsync new checkpoint → atomically swap pointer → delete old files. Vacuum (Room) runs at app update detection only (schema version change), wrapped in a pre-edit-style backup of the db file (cheap, local). Both procedures are idempotent and crash-safe: power loss mid-compaction leaves either old or new state, verified by TC-STATE-005's kill trials hitting the compaction window deliberately (1 of every 10 trials targets it).

## 10.6 The dependency ledger (allowed per module, with weight budgets)

| Module | Allowed (summary) | Compiled weight budget |
|---|---|---|
| core-model | kotlin-stdlib only | < 100 KB |
| core-editor | + androidx.core-ktx, text/ICU via platform | < 300 KB |
| core-storage | + Room runtime, security-crypto-free (JCE) | < 2 MB |
| core-io | + none (platform XML/zip/print) | < 500 KB |
| core-ai | + onnxruntime OR llama.cpp binaries (pack-gated) | < 8 MB total both |
| core-search | + Room (shared) | < 200 KB |
| feature-* / app | + material, hilt, camerax (scan), recyclerview | < 10 MB combined |
| qa-driver | + espresso, uiautomator, truth | test-only |

Dex budget total ≤ 25 MB APK (§26.4); a dependency exceeding its budget needs a D-nnn with an alternative analysis. No module may add: image loaders, network stacks, JSON mappers beyond org.json platform, DI beyond Hilt, or any Kotlin multiplatform library (support burden).

## 12.8 The save pipeline state machine

`EDITING` →(batch committed)→ `JOURNAL_PENDING` →(fsync ack)→ `EDITING`; `EDITING` →(800 ms idle)→ `CHECKPOINTING` →(fold done)→ `SAVING_INDEX` →(Room txn ack)→ `IDLE_SAVED`; any state →(kill)→ recovery replays per §12.3. Invariants: exactly one `CHECKPOINTING` at a time per doc; `JOURNAL_PENDING` holds a bounded single pending batch (older batches are already fsynced); `SAVING_INDEX` failure retries with backoff and never blocks further editing (journal already has the truth — the index catches up). The machine is a sealed class with exhaustive transitions tested (TC-STATE-001 harness).

## 11.8 Corruption scenarios and drills (each has a test)

| Scenario | Drill | Expected |
|---|---|---|
| truncated journal (power loss mid-write) | TC-STATE-005 kill window variant | last good frame replayed; partial frame discarded by CRC; no user loss |
| bit-rot in checkpoint zip | harness flips a byte | CRC/zip failure → rebuild from journal; self-test flags doc |
| corrupted document.json (invalid model) | harness mutates kind/offsets | validator refuses; doc opens read-only from last good checkpoint with repair banner |
| deleted asset file (image gone) | harness removes asset | missing-asset placeholder in doc; asset manager offers re-link/remove; export notes it |
| db wiped (§11.2 rebuild) | harness deletes databases/ | index rebuilds from files+journal; library identical (sample verified) |
| partially-copied backup restore | harness truncates restore zip | restore aborts; existing library untouched; report explains |

Drills live in `core-storage/src/test/drills/` and run in G2/G7 pipelines. Rule: corruption is an engineering input, not an error message — every scenario above ends with *user data safe or honestly reported*.

## 12.9 Uninstall and data lifecycle

Uninstall removes everything app-private (docs, packs, keys) by platform rule — the About screen says so in one line, because "where do my words live?" deserves a straight answer. SAF exports/backups persist by design (user-chosen locations); the backup passphrase is required to read them — OneDoc cannot recover it (no escrow, no account; the only unrecoverable secret in the product, stated at set-up). Clear-data (without uninstall) wipes the same stores; the next launch re-seeds schema and offers import/restore via the backup flow (TC-STATE-010 covers the clear-data → restore path).

## 10.7 The editor core class map (who does what)

| Class (core-editor) | Responsibility |
|---|---|
| `EditorCore` | the retained non-UI brain: owns document, op log, undo stack, journal client |
| `OpEngine` | applies/normalizes ops; the only code allowed to mutate the model |
| `UndoStack` | batches + inverses + coalescing timers (§14.4) |
| `ImeBridge` | InputConnection implementation; composition queue (§15.8) |
| `Spanner` | block ↔ Spanned mapping (pure, deterministic, §14.6) |
| `SelectionState` | the §15.6 five-tuple + snapping + handle math |
| `ToolbarStateMachine` | §15.7 sealed transitions |
| `PagerMetrics` | pagination guides + PDF shared metrics (§17.4) |
| `BlockTextView` | the one custom text view; renders Spanned, hosts IME |
| `JournalClient` | CRC frames, fsync, compaction triggers (§11.3) |

Everything UI-side (feature-editor) is rendering and gesture wiring only; a UI-free Robolectric test drives `EditorCore` through the full IME script set — the same tests CI runs, the same laws it checks.
