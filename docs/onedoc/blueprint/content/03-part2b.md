@PART: PART II — REQUIREMENTS AND PRODUCT SHAPE
@PARTDESC: Continuation: the fifty acceptance criteria that define "easy UX". These are pass/fail behaviors, not vibes; each is bound to test cases in the catalogue.

# Chapter 5 — UX acceptance criteria (UX-01 … UX-50)

## 5.1 How these were chosen

Each criterion below comes from a real friction pattern observed in mobile writing tools: the tap that should not exist, the dialog that interrupts thought, the state that silently vanishes. They are written as **verifiable behaviors** with exact counts (taps, seconds, milliseconds) because an autonomous builder needs numbers, not adjectives. Every criterion has at least one case in the catalogue; UX ids appear in test names as `UX-<nn>`.

## 5.2 Speed and directness

| ID | Criterion | Verified by |
|---|---|---|
| UX-01 | New-document FAB opens the editor directly: no template dialog, no naming dialog; a doc is created on first keystroke, not on tap | TC-UX-001 |
| UX-02 | Blank page to first typed character: ≤ 2 taps and ≤ 2 s on Tier B (cold) | TC-UX-001, TC-PERF-001 |
| UX-03 | Export PDF: ≤ 3 taps from editor (menu → Export PDF → share/save) | TC-UX-002 |
| UX-04 | Import a file from any app: share-to-OneDoc or open-in lands in import preview ≤ 2 taps | TC-UX-003 |
| UX-05 | Find & replace opens with the last find term preselected; Esc/back dismisses without leaving residue | TC-UX-004 |
| UX-06 | Undo of an AI insert is a single undo (grouped op), returning the document byte-exact to the pre-insert state | TC-UX-005, TC-EDIT-003 |
| UX-07 | Version restore completes in ≤ 30 s for a 50-page document including preview | TC-STATE-004 |
| UX-08 | Search-as-you-type: results start appearing after ≤ 2 characters, never a submit button | TC-SRCH-001 |
| UX-09 | Scan-to-doc: from camera open to editable text for one page ≤ 60 s on Tier B including OCR | TC-SCAN-001 |
| UX-10 | Dictation: first partial text on screen ≤ 1.5 s after speech starts | TC-AI-003 |

## 5.3 Never lose a keystroke

| ID | Criterion | Verified by |
|---|---|---|
| UX-11 | App killed (adb shell am kill / process death) mid-typing: zero loss on relaunch (journal replay) | TC-STATE-005 |
| UX-12 | Device rotation or split-screen mid-sentence: cursor, selection, IME composition state survive | TC-STATE-002 |
| UX-13 | Back from editor autosaves silently; no "Save?" dialogs anywhere in OneDoc, ever | TC-STATE-001 |
| UX-14 | Trash undo snackbar gives 7 s; after that, trash retains the doc for 30 days | TC-LIB-005/006 |
| UX-15 | A failed import (corrupt file) never creates an empty document and never destroys the clipboard | TC-IO-006 |
| UX-16 | Replace-all requires one confirm and creates a pre-edit version; a second tap of undo returns the original | TC-EDIT-013, TC-STATE-004 |
| UX-17 | Storage full during autosave: editor keeps running in memory, warning chip appears, retry is automatic — no data loss dialog storm | TC-STATE-009 |
| UX-18 | Export failure (SAF denied mid-write) leaves no partial file and shows the specific reason | TC-IO-011 |

## 5.4 The editor feels native

| ID | Criterion | Verified by |
|---|---|---|
| UX-19 | Selection toolbar never covers the selection; flips above/below by keyboard and screen edges | TC-UX-006 |
| UX-20 | Handles are ≥ 48 dp effective touch targets; toolbar buttons ≥ 44 dp (DQ-2) | TC-UX-006, DQ-2 |
| UX-21 | Long-press word → select shows system-standard behavior; drag handles work with stylus and mouse | TC-EDIT-004 |
| UX-22 | IME composition (pinyin, glide, Hindi transliteration): no flicker, no duplicate commit, no mark loss mid-composition | TC-EDIT-IME-01 |
| UX-23 | Enter on a list item continues the list; Enter on empty list item exits the list (Docs behavior) | TC-EDIT-007 |
| UX-24 | Heading style switch preserves inline marks; list↔paragraph switch preserves marks | TC-EDIT-006 |
| UX-25 | Scroll position anchors to the block being edited during IME keyboard show/hide (no jump) | TC-UX-007 |
| UX-26 | Typing never reflows the whole document: only the edited block and pagination guide update (measured via frame stats) | TC-PERF-002 |
| UX-27 | Two-finger scroll during IME composition does not corrupt text (composition is cancelled cleanly) | TC-EDIT-IME-02 |
| UX-28 | Hardware-keyboard shortcuts match §5.2 of the Android platform conventions; Ctrl+Z steps are identical to soft undo | TC-EDIT-016 |

## 5.5 Trust and calm

| ID | Criterion | Verified by |
|---|---|---|
| UX-29 | Every AI output appears in a preview card with an explicit Insert/Replace/Discard; nothing enters the doc implicitly | TC-AI-006 |
| UX-30 | Assistant unavailable states say *why* in one line ("gemma needs 8 GB RAM — this device has 4 GB") | TC-AI-009 |
| UX-31 | No notification is ever shown unless the user created a reminder or starts an export that needs progress | TC-SEC-P-02 |
| UX-32 | First launch shows a single welcome card (3 lines) with one button "Start writing"; no permission pre-prompt for camera/mic until the feature is used | TC-UX-008 |
| UX-33 | Deleting a document with versions warns about version count; deleting from trash is the only permanent path, double-confirm | TC-LIB-006 |
| UX-34 | Diagnostics screen shows only on-device facts; the "self-test" runs offline and takes ≤ 20 s | TC-SET-003 |
| UX-35 | All destructive actions have haptic confirm (tick) and are undoable or double-confirmed — never both silent and permanent | TC-UX-009 |
| UX-36 | Empty states teach one action, one line, one button; never a wall of tips | TC-LIB-008 |

## 5.6 Inclusive by default

| ID | Criterion | Verified by |
|---|---|---|
| UX-37 | TalkBack can create, edit, format and export a complete letter without sighted help | TC-A11Y-001 |
| UX-38 | Every image requires an alt-text prompt at insert (can be deferred, never silently skipped) | TC-IMG-001 |
| UX-39 | 200% font scaling leaves every control usable; no text clipped by containers (DQ-5) | TC-A11Y-003 |
| UX-40 | Themes: dark theme is a first-class citizen; high-contrast themes pass 7:1 for body text | TC-SET-001, DQ-4 |
| UX-41 | Color is never the only carrier of meaning (OCR confidence uses color + underline style) | TC-AI-001, DQ-4 |
| UX-42 | One-handed reach: primary actions (FAB, toolbar, assistant) live in the bottom 40% of the screen | TC-UX-010 |
| UX-43 | RTL mirroring: layout, toolbar order and handle behavior mirror in RTL locales | TC-SET-004 |
| UX-44 | Reduced-motion setting removes non-essential animation | TC-UX-011 |

## 5.7 Honest machine behavior

| ID | Criterion | Verified by |
|---|---|---|
| UX-45 | Importers state the fidelity level achieved ("Imported as HTML — F2: lists and marks kept; tracked changes dropped") | TC-IO-005 |
| UX-46 | OCR low-confidence words are visually marked and tappable to fix; export never silently ships guessed words in a scan-sourced doc | TC-AI-001 |
| UX-47 | Summaries and rewrites state their method ("on-device gemma-2B" / "extractive fallback") in the preview card | TC-AI-004/005 |
| UX-48 | Pack install shows SHA-256 and asks for explicit confirm; verification failure shows both SHAs | TC-AI-PACK-01/02 |
| UX-49 | Word count matches the export (PDF text extraction within ±1%) | TC-IO-001 |
| UX-50 | The app never shows marketing, ratings prompts, "upgrade" nudges, or any network-dependent content — verifiable by string scan + traffic probe | TC-SEC-P-03 |

**Count:** UX-01…UX-50. The catalogue's ENV/A11Y/DIAG rows re-verify the platform-level ones; the direct-APK QA pipeline (Part X) runs the full UX set on every release candidate.

## 5.8 Why fifty criteria, in seven groups

The groups are ordered by the cost of getting them wrong. Speed (5.2) and durability (5.3) come first because they are the two ways a writing app loses users forever: wasted seconds and lost words. Native-feel (5.4) is where competitors leak trust daily — every toolbar-over-selection bug reads as "not a real app". Trust (5.5) is the AI contract: preview-explicit insertion is what makes on-device AI feel like a tool rather than an autonomous co-author. Inclusivity (5.6) is scope, not charity: TalkBack-complete flows find real bugs (traversal exposes states eyes skip). Honest machines (5.7) exist because fidelity lies and silent OCR guesses are the two fastest ways to corrupt someone's document without ever crashing.

Counts per group: speed 10 · durability 8 · native feel 10 · trust 8 · inclusivity 8 · honesty 6. The distribution is deliberate: no group may dominate, and any new criterion joins the group whose *failure* it prevents, which keeps the set from drifting into feature-list territory (S-CREW, §25.3).

## 5.9 Per-criterion rationale (why each exists, compressed)

UX-01/02 exist because dialog-gated creation is the #1 abandonment cause in note apps; the keystroke-not-tap doc creation makes "new document" free. UX-03/04 measure export/import reachability because file features hidden three menus deep don't get used. UX-05/06 are undo-dignity rules (AI must feel reversible or users stop trusting it). UX-07/08 put numbers on the two async surfaces (restore, search) so "slow" has a definition. UX-09/10 bound the AI capture paths — scan and dictate live or die by latency, not accuracy alone. UX-11…18 are the durability eight: every silent-loss scenario from the predecessor program's defect history became a criterion. UX-19…28 codify native-feel details competitors get wrong daily. UX-29…36 define the AI trust contract and calm-UI rules. UX-37…44 are inclusion as scope (each is testable, none is aspirational). UX-45…50 make the machine honest in writing — fidelity notes, confidence marks, method labels, hash transparency, count parity, and the absolute absence of marketing.
