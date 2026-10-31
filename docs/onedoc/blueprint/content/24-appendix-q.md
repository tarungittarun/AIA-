# Appendix Q — Error catalogue (complete OdError enumeration)

Every error kind the app can surface, with verb (§10.5), user string key, and log treatment. The compiler-enforced enum is generated from this table (a test asserts table == enum == strings.csv coverage — no orphan error paths).

| Kind | Verb | String key | Log/diagnostics |
|---|---|---|---|
| E_STORAGE_DISK_FULL | retryable | err.disk.full | auto-retry ≤ 3, backoff 2/8/30 s |
| E_STORAGE_IO | retryable | err.storage.retry | same |
| E_JOURNAL_CRC | reportable | err.doc.repair | quarantine file, keep bytes, self-test flags |
| E_DOC_SCHEMA_FUTURE | actionable | err.doc.newer | refuse open older app; suggest update path (manual) |
| E_IMPORT_UNSUPPORTED | actionable | import.refused.format | reason names format |
| E_IMPORT_CORRUPT | actionable | import.refused.corrupt | why: zip/xml/codec |
| E_IMPORT_TOO_LARGE | actionable | import.refused.size | 50 MB cap |
| E_IMPORT_BINARY | actionable | import.refused.binary | NUL/decode gate |
| E_EXPORT_SAF_DENIED | actionable | export.denied.folder | one action: pick again |
| E_EXPORT_WRITE | retryable | export.retrying | no partial file (UX-18) |
| E_PACK_VERIFY | actionable | pack.verify.fail | both SHAs shown |
| E_PACK_RUNTIME_OLD | actionable | pack.runtime.old | runtime pin name |
| E_PACK_TIER | actionable (hidden control variant) | ai.unavailable.tier | long-press reason |
| E_AI_THERMAL | info (descent) | ai.descended | rung noted in card + diagnostics |
| E_AI_TIMEOUT | actionable | ai.timed.out | offer lighter method (ladder) |
| E_TTS_MISSING | info (hidden) | ai.unavailable.tts | reader control hides |
| E_MIC_PERMISSION | actionable | perm.mic.why | settings deep-link |
| E_CAMERA_PERMISSION | actionable | perm.camera.why | settings deep-link |
| E_IME_VIOLATION | reportable (debug fail-fast) | — (never user-visible) | fuzzer alert, defect |
| E_INVARIANT | reportable (debug fail-fast) | err.something.broke | quarantine + diagnostics ring |
| E_DB_MIGRATION | reportable | err.upgrade.repair | backup plan §11.4; never silent drop |

Reportable errors are the only ones that add a diagnostics entry beyond counts; they always preserve user data first (quarantine, not delete) — the tracker's S1 class is defined by exactly these plus Law violations.

# Appendix R — Gesture map (every gesture, its action, and the accessible path)

| Gesture | Context | Action | Accessible equivalent (TalkBack menu / a11y action) |
|---|---|---|---|
| Tap | block | place caret | same (default focus) |
| Double-tap | word | select word | selection action "select word" |
| Triple-tap | paragraph | select paragraph | "select paragraph" |
| Long-press | text | word select + drag handles | same via keyboard selection |
| Long-press | doc card | multi-select enter | custom action "select" |
| Long-press | block handle | drag-reorder | "Move block up/down" |
| Long-press | AI verb (hidden context) | show availability reason | reason is the content description |
| Two-finger scroll | during composition | cancel composition, scroll | same |
| Pinch | editor | zoom page scale (compose) 80–130% | font-size stepper in settings |
| Swipe from left edge | editor | back (system) | back action |
| Swipe down on handle | selected block | dismiss selection | Esc action |
| Drag corner handles | scan crop | perspective crop | numeric adjust fields |
| Drag within cell edge | table | (nothing — presets only, §17.1) | column preset menu |
| Swipe on snackbar | any | dismiss (undo remains via versions) | "Undo" action button |

# Appendix S — Gate demos (what the owner can watch at each gate)

| Gate | 30-second demo |
|---|---|
| G1 | `adb install` shell app; icon launches; empty home; CI run link green with ≤ 8 jobs |
| G2 | create doc, type, kill app mid-typing, reopen — words survived (journal proof on terminal) |
| G3 | type with IME, select, bold, undo/redo; typing-latency overlay showing P95 |
| G4 | build a table, insert an image with alt text, instantiate "Letter" template, replace-all with version created |
| G5 | export the same doc as PDF/md/docx; open the conversion note; import it back |
| G6 | install OCR pack (SHA shown), scan a page to text; hide the pack → capability explains itself |
| G7 | run the evidence PDF walkthrough: journeys strip, budget table, BLOCKED register |
| G8 | release page: signed APK, SHA, provenance.json, notes; verify-by-checksum demo |

# Appendix T — Coverage matrix (features × gates × levels)

Rule: a feature ships only after its cases pass at their levels on the matrix AVDs (§23.1). The matrix below is the map the G7 audit walks; the machine check is `traceability.py --check --strict` plus the run manifest.

| Area | Features | L1 | L2 | L4 | Gates | P0 cases |
|---|---|---|---|---|---|---|
| Laws | L1–L10 | ✓ | ✓ | ✓ | G3, G7 | all |
| Library | F-001…012 | — | ✓ | ✓ | G2–G7 | 001,002,003,005,012 |
| Editor core | F-013…030 | ✓ | ✓ | ✓ | G3, G4, G7 | 013–018,023,024,025,026,029,030 |
| Structure | F-031…044 | ✓ (props) | ✓ | ✓ | G4, G7 | 031–033 |
| Templates | F-045…050 | — | ✓ | ✓ | G4, G7 | 045,047 |
| Files/IO | F-051…060 | ✓ (goldens) | ✓ | ✓ | G5, G7 | 051–057,059 |
| State | F-061…066 | ✓ (P8) | ✓ | ✓ | G2, G4, G7 | 061,062,063,065 |
| Search | F-067…070 | ✓ | ✓ | ✓ | G4, G6, G7 | 067,068 |
| AI | F-071…082 | — | ✓ | ✓ | G6, G7 | 071,073,074,075,076,077,078,079,082 |
| Read/A11y | F-083…086 | — | — | ✓ | G4, G7 | 084,085,086 |
| Settings | F-087…090 | — | ✓ | ✓ | G4, G7 | — |
| UX | UX-01…50 | — | part | ✓ | G3–G7 | 01–03,05,06,08,11,19,22,29,30,32,37,39 |
| Security | TC-SEC-* | ✓ | ✓ | ✓ | G6, G7 | all |
| Perf/Env | TC-PERF/ENV | — | — | ✓ | G1, G3, G7 | 001,002, ENV all |
| Journeys | TC-J1…J5 | — | — | ✓ | G7, G8 | all |
