# Chapter 13 — Module technical deep dives

## 13.1 Calculator engine (core/domain/calc)

See §17.1 for the full language specification. Structure:

```
Lexer (tokens, unicode-aware) → Parser (Pratt, precedence climbing)
  → Ast (Num, Bin, Un, Percent, Call, Group)
  → Evaluator (exact first, Decimal fallback)
  → Renderer (exact → display string, grouping, fraction option)
LiveAnswer = Parser+Evaluate on a cancellable job per keystroke
```

The engine is a pure Kotlin class `CalcEngine` with one public method `evaluate(expr: String, cfg: EngineConfig): EvalResult` plus `format(result, cfg): String`. `EngineConfig` carries angle mode, fraction display, locale (for grouping only). **No Android imports**, no globals, no state — history/memory live above it. This is what makes the 10⁴-case property tests (§17.1.7) cheap and the Google-parity behaviors (F-001…F-009) provable.

## 13.2 Notes document model

`NoteDoc` = JSON: `{v:1, blocks:[Block]}`; `Block` = paragraph | heading{level} | bullet{items} | checklist{items:[{text,checked}]} | divider. Inline runs carry `{text, bold?, italic?}`. Rules: renderer and parser share one serialization (round-trip identity test TC-NOTE-rt); plainText projection strips marks for FTS; Markdown export/import maps every block (unknown Markdown constructs import as plain paragraphs with a one-time notice). Autosave writes bodyJson+plainText in one transaction 500 ms after last keystroke; editor state (scroll, cursor) goes to SavedState.

## 13.3 Scanner pipeline

```
CameraX ImageCapture → YUV→NV21 → DocumentCornerDetector (OpenCV-free:
  Hough-lite edge scan in pure Kotlin on 480p preview frames)
  → perspective warp (RenderScript-free: Android Matrix + Bitmap)
  → filter (Gray / adaptive B&W)
  → page store (JPEG q85, app-private)
OCR: page bitmap → resizer 960px long-edge → ONNX det model (DBNet-lite)
  → boxes → crop+rectify → ONNX rec model (CRNN en) → text lines
  → confidence merge → editable card
```

Per-page OCR budget: ≤ 2.5 s p50 on Tier B, ≤ 6 s Tier C, cancellable; progress on the card; images never leave the process (no share intents until user acts). Camera permission denied → import from Files path keeps the module alive (F-055).

## 13.4 Calendar recurrence engine

Pure Kotlin `RecurrenceEngine` (§17.4): input `CalEvent` + window → occurrences. Supports RRULE subset `FREQ=DAILY|WEEKLY|MONTHLY|YEARLY`, `INTERVAL`, `BYDAY` (weekly), `BYMONTHDAY` (monthly), `COUNT`, `UNTIL`, plus `EXDATE`. Monthly rules use the "same-day-of-month, skip missing" policy with a documented alternative (last-day clamp) as a setting. Unit-tested against a golden corpus of 200 rules with expected occurrence lists, plus DST-crossing cases (ADR-08 offsets).

## 13.5 Media: Music + Recorder

Music: Media3 `ExoPlayer` with `DefaultMediaSourceFactory` queueing playlists via ConcatenatingMediaSource2-style factory; artwork via a BitmapFactory-based decoder with a 64 MB LRU disk cache; library scanner walks SAF tree or MediaStore cursor in a cancellable coroutine, diffing into Room (no duplicates by (path,size,mtime)).
Recorder: `AudioRecord` (48 kHz mono) → AAC via `MediaCodec` + `MediaMuxer` (WAV path writes PCM directly); pause = stop feeding muxer, resume with new sync sample; markers = DB rows at flag time; waveform = decimated RMS ring buffer drawn by Compose Canvas at 20 fps max.
Media session: `MediaSessionService` for Music (headset/bluetooth controls, media notification); Recorder uses a plain FGS notification (pause/resume/stop actions) — it is not a media-session consumer.

## 13.6 Files & SAF

Two abstractions: `LocalRepo` (app-private: list/copy/move/rename/delete/trash via `java.io`+`AtomicFile`) and `SafRepo` (DocumentFile tree from persisted grants, with a SAF-can't-do-X map: no true rename-move across roots → copy+delete with progress + undo impossible on SAF deletes (documented in UI as "deleted permanently" for SAF)). Open-with hands off `ACTION_VIEW` + `ClipData` with grant flags. The analyzer walks with a 200 ms-yielding coroutine so the UI never janks; results cached with mtime invalidation.

## 13.7 Hub search federation

`SearchAggregator` fans out to per-module `SearchSource` implementations (NotesFts, Scans, Events, FilesNames, Tracks, Recordings+Transcripts, CalcHistory) with per-source budgets (25 ms first page, cancellable), then groups results by module in fixed order. Semantic search (pack on) runs post-FTS for note sources only (§12.5). Debounce 120 ms; the aggregator is unit-tested with fake sources for ordering, budget and cancellation (TC-HUB-*).

## 13.8 Notifications and alarms inventory

| Channel | Type | When |
|---|---|---|
| `reminders` | High-importance, sound+vibration | Calendar alarms (user-created) |
| `recording` | Low-importance, ongoing FGS | During recording only |
| `playback` | Media style | Music playback |
| `diagnostics` | Default, silent | Only on self-test failure the user asked to run |

Nothing else ever posts (P4). Exact alarms via `AlarmManager.setExactAndAllowWhileIdle`; `canScheduleExactAlarms()==false` → setInexactWindow fallback + one-time silent notice in Calendar settings (never a blocking dialog).

## 13.9 Public API surfaces per module (executor contract tables)

Calculator (`core/domain/calc` + `feature/calculator`):

| Symbol | Signature | Notes |
|---|---|---|
| `CalcEngine.evaluate` | `(expr: String, cfg: EngineConfig): EvalResult` | pure, thread-safe |
| `CalcEngine.format` | `(r: EvalResult, cfg: EngineConfig): String` | grouping/fraction display |
| `EvalResult` | `value: ExactValue, exact: Boolean, error: CalcError?` | sealed |
| `EngineConfig` | `angleMode, fraction, localeTag` | value class |
| `ExpressionViewModel` | `onKey/onCaret/selection ops/history/mem` | single source of UI state |
| `SelectionController` | `enter/resize/commit/cancel` | gesture-driven state machine |

Notes:

| Symbol | Signature | Notes |
|---|---|---|
| `NoteDocCodec.encode/decode` | `(NoteDoc): String` / `(String): NoteDoc` | round-trip identity |
| `NoteRepo.upsert/get/trash/restore/purgeExpired` | coroutines | Room txn + FTS |
| `NoteSearch.query` | `(q: String, budget): List<Hit>` | FTS + snippets |

Scanner:

| Symbol | Signature | Notes |
|---|---|---|
| `CaptureController.start/torch/focus` | CameraX wiring | permission-aware |
| `DocDetector.corners` | `(Bitmap): Quad?` | pure Kotlin |
| `OcrRunner.recognize` | `(Bitmap, budget): OcrPayload` | orchestrator client |
| `ScanRepo.savePage/exportPdf` | page store + PDF mux | app-private |

Calendar:

| Symbol | Signature | Notes |
|---|---|---|
| `RecurrenceEngine.occurrences` | `(CalEvent, Window): List<Instant>` | pure |
| `CalRepo.upsert/delete/window` | CRUD | index-backed |
| `ReminderScheduler.arm/cancel/rearmAll` | AlarmManager | boot-aware |

Files:

| Symbol | Signature | Notes |
|---|---|---|
| `LocalRepo.list/copy/move/rename/trash` | path ops | queue writes |
| `SafRepo.*` | DocumentFile mirrors | can't-do map honored |
| `Analyzer.walk/cancel` | sizes by category | yielding |
| `BackupManager.create/restore` | `.msone` | transactional |

Music:

| Symbol | Signature | Notes |
|---|---|---|
| `LibraryImporter.scan` | SAF/MediaStore diff | cancellable |
| `PlaybackController.play/pause/seek/speed/queue` | Media3 | session-backed |
| `PlaylistRepo` | CRUD + M3U export | — |

Recorder:

| Symbol | Signature | Notes |
|---|---|---|
| `RecorderService.startPause/stop/flag` | FGS intents | ≤ 200 ms start |
| `RecordingRepo` | rows + markers | — |
| `Transcriber.run` | pack client | segments out |

Diagnostics:

| Symbol | Signature | Notes |
|---|---|---|
| `SelfTest.run` | 6 checks → report | §17.8 |
| `LogRing.append/scrub/export` | rolling store | §28.3 |
| `PackRegistry` | import/enable/disable/verify | §16.8 |

## 13.10 Recorder end-to-end sequence (numbered, for the executor)

1. User taps record → `RecorderController.start()` requests mic permission if needed (§14.7 copy) → `startForegroundService` (≤ 200 ms, type `microphone`).
2. Service acquires `AudioRecord` (48 kHz mono), starts encoder thread, opens `MediaMuxer` on the final file path, inserts `Recording` row (state=recording).
3. Waveform: ring buffer of decimated RMS pushed via SharedFlow; Compose Canvas renders ≤ 20 fps.
4. Pause: stop feeding muxer; freeze presentation time; update notification (Resume/Stop); state=paused.
5. Flag: validate not paused → insert `RecordingMarker(offsetMs=timeline)` → haptic.
6. Done: stop/muxer stop/finalize → row state=saved, durationMs=timeline → notification dismissed.
7. Call interruption: audio focus loss → auto-pause (§7.14) with notification note.
8. Storage threshold: pre-write check each 5 s chunk → below floor → graceful finalize, row state=incomplete, user card (not toast-from-worker — the historical crash class stays dead).
9. Process death of service (OEM kill): file finalized best-effort on `onTaskRemoved`/`onDestroy`; row honest about interruption.

## 13.11 Scanner end-to-end sequence (numbered)

1. Module opens → CameraX preview binds (permission flow §14.7); guides overlay.
2. Shutter → `ImageCapture.takePicture` → freeze overlay ≤ 250 ms.
3. Corner detection on 480p frame → quad found → perspective warp to page.
4. Filter applied (user default) → JPEG q85 → `Scans/page-<n>.jpg` → row update.
5. Review opens (auto); OCR auto-runs when Essentials pack enabled (§16.6 tier rules).
6. OCR: bitmap normalized (≤ 960 px) → det → rec per box → merge → card editable; conf badges.
7. User edits text; actions Copy/→Notes/Re-OCR/Delete per §7.4.
8. Export: PDF mux (pages in order) or image copy or text → destination (Files/Notes/clipboard).
9. Batch chip counts pages; duplicate-detection warns (§7.14); page manager reorders/deletes.

# Chapter 14 — Security and privacy engineering

## 14.1 Threat model (STRIDE-lite, offline)

| Threat | Vector | Mitigation |
|---|---|---|
| Data theft from device | Lost phone, backup file | App-private storage; optional app lock; encrypted `.msone` (PBKDF2 210k, AES-GCM) |
| Malicious file import | Crafted image/audio/ICS/pack | Decode via platform codecs only; no native parsers beyond vetted runtimes; pack SHA-256 + zip-bomb guards (max ratio 100×, max entries 10k); ICS parser with depth/size caps |
| Intent abuse | Another app invokes components | All activities `exported=false` except launcher; receivers not exported (except media-button receiver pattern per API level); `review` grants not persisted |
| Clipboard leakage | Sensitive calc values on clipboard | Clipboard auto-clears 60 s after calculator copy (setting, default on) |
| Model-pack tampering | Swapped pack file | SHA-256 manifest verified at import AND at load; mismatch → pack disabled + Diagnostics card |
| SQLite injection | Search strings | Room bound parameters only; FTS query sanitized (quotes escaped) |
| Path traversal in backup | Crafted `.msone` entries | Entry names validated (`../` rejected, only `data.json` + whitelisted dirs extracted) |

## 14.2 Privacy guarantees (structural)

The merged manifest contains **no** `INTERNET`, `ACCESS_NETWORK_STATE`, `READ_CONTACTS`, `LOCATION*`, `READ_PHONE_STATE`, `BLUETOOTH_*` (classic), `QUERY_ALL_PACKAGES`, or ad-class permissions (C1). No WebView, no JavaScript engine, no `URL`/`Socket`/`HttpURLConnection` classes in release bytecode — CI scans with `apkanalyzer` + a dex-name grep (§24.4). Unique identifiers: none generated; `Settings.Secure.ANDROID_ID` never read. Crash logs live only in the local ring; `Share log` shows the exact content in a preview sheet before any system share target appears.

## 14.3 Data lifecycle

Create → live tables/files; Delete → trash (30 d) → hard delete with file shred (overwrite + delete for private files; SAF deletes are OS-level); Backup → user-initiated only; Restore → transactional (§12.4). Telemetry: **there is none** — the only counters are in the local diagnostics ring (§28.3), PII-scrubbed (paths reduced to basenames, expressions kept verbatim because they are the product's content — the log preview makes this visible before sharing).

## 14.4 Permissions matrix (full app)

| Permission | Type | Why | Request moment |
|---|---|---|---|
| `CAMERA` | Dangerous | Scanner viewfinder | First scanner open |
| `RECORD_AUDIO` | Dangerous | Recorder | First record tap |
| `READ_MEDIA_AUDIO` (API 33+) / `READ_EXTERNAL_STORAGE` (26–32, maxSdk 32) | Dangerous | Music import | First music open |
| `POST_NOTIFICATIONS` (API 33+) | Dangerous | Reminders, recording, playback | First reminder creation |
| `SCHEDULE_EXACT_ALARM` | Normal (26–32) / declared with user grant path 33+ | Reminder precision | First reminder (settings fallback per §13.8) |
| `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_MICROPHONE`, `FOREGROUND_SERVICE_MEDIA_PLAYBACK` | Normal | Recorder / Music FGS types | — |
| `RECEIVE_BOOT_COMPLETED` | Normal | Re-arm reminder alarms | — |
| `VIBRATE` | Normal | Haptics | — |

`mycalc` flavor: **none of the above** — the flavor's manifest is empty of permissions; calculator needs nothing (F-038). The one historical wart — an auto-generated `DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`-class custom permission — is explicitly checked in CI and must not appear (the owner's v3.12.39 QA flagged it; §24.4 gate `no-custom-permissions`).

## 14.5 Data-in-transit and crypto inventory

There is no transit. Crypto inventory: Java `Cipher AES/GCM/NoPadding`, `SecretKeyFactory PBKDF2WithHmacSHA256`, `KeyStore` for the app-lock integrity attestation blob only (never for data keys — those derive from the passphrase so backups are portable). No third-party crypto libraries (smaller APK, smaller audit).

## 14.6 Security review checklist (per release, automated + human-walkable)

| # | Check | Method |
|---|---|---|
| SC-01 | Merged manifest permission set == allow-list (full + flavor separately) | CI manifest-audit diff |
| SC-02 | Exported components == launcher activities only | manifest parse test |
| SC-03 | No network-class symbols in dex (URL/Socket/okhttp/WebView/JS engines) | apkanalyzer + grep gate |
| SC-04 | Backup zip guards reject traversal/bomb fixtures | L2 tests on fixture set |
| SC-05 | Wrong-passphrase restore fails with no partial state | L4 J-03 negative case |
| SC-06 | Pack hash mismatch disables pack and surfaces card | L2/L4 PACK cases |
| SC-07 | Clipboard auto-clear works and is discoverable (settings row) | L4 |
| SC-08 | Log ring scrubber passes PII fixture battery | L1 |
| SC-09 | App-lock locks after background threshold; credential fallback works | L4 (biometric emulators) |
| SC-10 | No custom permissions declared (esp. the historical `*_NOT_EXPORTED_PERMISSION` pattern) | manifest-audit hard gate |
| SC-11 | Debuggable=false, cleartextTrafficPermitted=false, backup agent absent or agentless-allowlist | build output scan |
| SC-12 | Mapping.txt + APK SHA-256 archived in evidence bundle | release lane artifact check |

## 14.7 Permission request copy (exact strings, normative)

| Permission | Dialog title | Dialog body |
|---|---|---|
| CAMERA | Allow camera? | Scanner uses the camera to capture pages. Images stay on this phone. You can also import images instead. |
| RECORD_AUDIO | Allow microphone? | Recorder stores audio on this phone only. Nothing is uploaded — MySpace One has no internet permission. |
| READ_MEDIA_AUDIO | Allow music access? | Music lists audio files to build your library. Files are read, never changed or uploaded. |
| POST_NOTIFICATIONS | Allow notifications? | Reminders, recordings and playback need notifications. No marketing, ever. |

Denied-state copy (in-feature cards) states the manual alternative (§7.11) and never nags — one card, dismissable, persistent entry in Settings.

## 14.8 Data classification register

| Data | Class | Storage | Leaves device? |
|---|---|---|---|
| Note bodies/titles | Sensitive | Room (private) | only via explicit share/export |
| Calculator history | Sensitive | Room | only via explicit share/export |
| Recordings audio | Sensitive | private files | never auto |
| Transcripts | Sensitive | Room | only via share/export |
| Scan images + OCR | Sensitive | private files/Room | only via share/export |
| Events | Sensitive | Room | only via ICS export |
| Music library metadata | Personal | Room | never |
| Settings/preferences | Personal | DataStore | never |
| Backups (.msone) | Sensitive (encrypted) | user-chosen location | user-controlled |
| Diagnostics ring | Operational (scrubbed) | private files | only via user share |
| AI pack files | Public asset | private files | never |
| Crash breadcrumbs | Operational (scrubbed) | private files | only via user share |

## 14.9 Android component inventory (merged manifest, normative)

| Component | Flavor | Exported | Purpose |
|---|---|---|---|
| `MainActivity` | both | yes (launcher) | single-activity host |
| `RecorderService` (FGS) | full | no | recording |
| `PlaybackService` (MediaSession) | full | no | music |
| `ReminderReceiver` | full | no | alarm firings |
| `BootReceiver` | full | no | re-arm alarms |
| `MediaButtonReceiver` | full | no | headset controls |
| `ShareLogActivity` | full | no | share-sheet source |
| `CalcShortcutActivity` | both | no | app shortcuts trampoline |

No content providers; no broadcast senders to third parties; every receiver `exported=false` with explicit intent actions internal to the app (media-button receiver pattern per API level documented in code).

## 14.10 Local incident response runbook (worst-case playbook)

| Incident | Immediate steps | Recovery |
|---|---|---|
| DB corruption detected | app switches read-only mode; banner; backup prompt | restore latest `.msone`; FTS rebuild; defect S1 |
| Recording file damaged | row marked; player shows reason; raw file kept | partial playback attempt (WAV header resync tool in Diagnostics v1.1) |
| Pack loads but produces garbage | disable pack automatically; provenance row flags model hash pair | re-import correct version; eval re-run |
| Restore half-applied (crash) | staging swap design prevents; if bootstrapped mid-restore, startup detects `incoming-restore/` and rolls back | re-run restore |
| App-lock locks out (no biometrics enrolled) | device-credential fallback per BiometricPrompt contract | OS-level recovery only (by design; no backdoor) |

## 14.11 In-app privacy statement (exact text, About → Privacy)

> **MySpace One is offline by design.**
> This app has no internet permission. It cannot connect to anything, so nothing you write, scan, record, calculate or play can be transmitted — by the app or by anyone using it.
> Your notes, scans, recordings, events, files and history live in the app's private storage on this phone. Backups are files you create and keep (encrypted with your passphrase). Optional AI features run entirely on this phone using model packs you install yourself.
> The app collects nothing, phones nothing home, and has no accounts. Diagnostics logs stay on the phone until you choose to share them, and you see exactly what will be shared.
> Delete the app and the private data goes with it — export a backup first if you want to keep anything.

This statement is asserted in tests (strings key `privacy.statement.body`) so it can never silently drift from the app's actual behavior — the statement is a spec artifact as much as a legal one.

## 14.12 Crypto test vectors (fixed answers the tests pin)

The crypto suite pins known-answer tests: PBKDF2-HMAC-SHA256("passphrase", salt=0x00..0f, 210000, 32B) → recorded hex; AES-256-GCM round-trip with AAD=`msone-v1`; tampered-ciphertext must fail GCM tag verification. Vectors live in `core/data/test/crypto-vectors.json` (generated once, reviewed) — upgrades to iteration counts are ledger decisions (they break old backups only if the *reading* app changes; the format records its own parameters so old backups stay readable).
