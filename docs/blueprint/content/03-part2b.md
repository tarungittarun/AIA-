# Chapter 7 — Module-by-module interaction specification

This chapter specifies what each screen *does*; Chapter 9 turns every behavior into numbered, testable requirements, and Chapter 20 into test cases. Structure rules from Chapter 5 apply everywhere (two taps, one design system, states per §7.11).

## 7.1 Hub (Home)

Specified in §5.3. The hub's acceptance-relevant behaviors: search across all modules with grouped results; continue-row restores exact module state; module status lines are computed locally (events today, storage free, new scans count, library size); long-press shortcuts; first-run privacy card shown exactly once. The hub is also the crash-recovery surface: after an abnormal process death the continue-row shows "Recovered — tap to reopen" for the interrupted module.

## 7.2 Calculator (the flagship module)

The calculator is the owner's primary tool and the most exactly specified module in this document. Structure: one screen, two pads (basic / scientific), an expression field with a **caret**, a **live answer** line, a **history sheet**, a **memory sheet**, and a settings sheet (key theme, key shape, haptics, "show as fraction"). Scientific pad appears by swipe-left on the pad area or an `INV`/sci toggle on tablets and landscape.

### 7.2.1 Expression field

- Single line that **autoscrolls horizontally** when longer than the field; caret is always visible as a 2 dp vertical bar; tapping inside the text places the caret between characters (not word-level); long-press enters text-selection mode.
- **Live answer** beneath the expression: evaluated as-you-type with the same engine that produces final results (no separate "fast path" that could disagree — §17.1.6). Rendered in `color/liveAnswer`; suppressed when the expression is not a complete evaluatable form (then nothing is shown — never a stale answer).
- Bracket balancing is auto-displayed: an unclosed `(2+3` shows live answer for `(2+3)` and the `=` key closes all open brackets (guide C6). The `( )` key inserts the pair when at a position where an operand is expected, else inserts only `)` when a bracket is open and an operator was just typed (§17.1.4).
- Operators replace, not append, when typed twice (`5+×` → `5×`); a leading `−` is unary minus, so `10×−` is legal (guide C4) and evaluates to `-10`.
- **Percent** is context-sensitive (§17.1.5): `200+10%` displays live `220`; `50%` alone displays `0.5`; `200×10%` displays `20`.

### 7.2.2 Selection and the memory pills (guide section B)

Long-press (≈ 300 ms, stationary) on the expression field opens selection mode: the touched token highlights (pink/primary highlight), and a floating **selection pill** appears: `Cut · Copy · MAdd · MUse · Paste`. Behaviors:

- **B2 — hold-and-slide**: without lifting, sliding the finger left/right grows/shrinks the selection character by character. This is a custom `longPress + drag` detector (pointer-ID tracked, slop-disabled); *not* platform `selectionHandle` UI.
- **B4 — Copy/Paste**: copy puts the exact selected substring on the clipboard (no grouping commas); paste inserts clipboard text at the caret (sanitized to legal characters, §17.1.3).
- **B5 — Cut**: removes selection to clipboard; typing immediately after inserts at the now-empty position.
- **B6 — tap elsewhere**: a tap on another part of the expression (or on empty field) exits selection mode, dismisses the pill, and leaves the caret at the tapped position.
- **B7 — AC**: pressing `AC` clears selection first; a second press clears the expression. (Single-press semantics: if a selection exists, AC clears just the selection and the expression remains.)
- **B11 — caret menu**: long-press on *empty* expression (or beyond text end) opens the same pill reduced to `MUse · Paste` — insertion at an empty caret.
- **B12 — MAdd / MUse**: `MAdd` stores the numeric value of the selection (parsed with the engine's evaluator; `1,234` and `2+3` both store `5`/`1234` appropriately) into the single memory slot shown in the memory sheet; `MUse` **replaces the current selection** with the stored value, or inserts at caret when no selection. Typed digits may also land *inside* a selection, replacing it (guide B5 pattern).
- Selection state never survives the expression being cleared, a history replay, or an `=` press.

### 7.2.3 Keypad

Basic pad: `AC ( ) % ÷ / 7 8 9 × / 4 5 6 − / 1 2 3 + / 0 . ⌫ =`. Scientific pad adds rows above (`INV sin cos tan / π e ^ √ / ln log !`) and replaces the layout per the wireframe; `INV` reveals `sin⁻¹ cos⁻¹ tan⁻¹` and `eˣ 10ˣ`. Key behaviors: press haptic (if enabled) + 120 ms scale; `⌫` deletes one character at the caret (or the whole selection); press-and-hold `⌫` repeats after 400 ms at 15 Hz; Long-press on `AC` does nothing — destructive shortcuts are deliberate omissions, and history clearing lives only in the history sheet behind a confirmation.

![Calculator basic pad and scientific panel with engine and persistence contracts annotated.](figures/fig-calc-wireframe.png)

### 7.2.4 History sheet

- Opens by: the history button (persistent, top-right of expression area), swiping down on the expression field, or the overflow menu. Title `History · n` with `Clear` and close actions.
- **Newest on top**; each card shows expression (small, muted) and result (large); timestamps shown as `27th Oct, 13:36` style. Tap a card → **replay**: the expression paints into the expression field first, the sheet closes after paint, caret at end (guide D9/D10 — replay is debounced 350 ms against double-tap races).
- History persists in Room (§12.2) and **survives restart** (TC-ONE-C-013); pinned cards survive `Clear` (clear asks confirm; pins are kept, unpinned are deleted).
- Caps at 500 rows, LRU-evicted, `VACUUM`-free (Room handles page reuse).

### 7.2.5 Memory sheet and effects

- Overflow → `Memory` opens a sheet listing saved values (the MAdd slot and any `M+`-accumulated slots, cap 10) with `MUse / MAdd / MC` per row and up/down reordering (guide E3 "Move up/down from place n").
- Overflow → `Effects` opens the effects picker with at least four styles (`None`, `Bubbles`, `Ripple`, `Confetti`) that animate on `=`; selection persists; `None` is default on Tier C devices if battery saver is on.

![History, memory and key-theme surfaces.](figures/fig-calc-panels.png)

### 7.2.6 Calculator settings sheet

Items (exact overflow list): `Haptics: On/Off`, `Memory`, `Show as fraction On/Off` (display `1/3` instead of `0.3333333333` where the engine keeps a rational), `Key theme`, `Key shape`, `Effects`. These six items are the complete overflow menu — the owner's harness asserted this exact list on the standalone flavor.

### 7.2.7 MyCalc flavor differences

The `mycalc` flavor renders the calculator as home with a compact app bar (`MyCalc` title, STANDALONE tag in diagnostics), the same overflow list, and **no** hub, modules, or cross-module actions (no "→ Notes" anywhere). Package `app.space.calc`, `versionCode` shared scheme (§23.4). Zero permissions is the flavor goal: even `CAMERA`-class permissions are compiled out because Scanner is absent from the flavor's merged manifest.

### 7.2.8 Key-by-key specification (normative)

Every key: id, gesture behaviors, inserted token, TalkBack label, and notes. "Press" = tap; long-press behaviors listed where they exist.

| Key | Press inserts/does | Long-press | TalkBack label | Notes |
|---|---|---|---|---|
| `AC` | clear selection, else clear expression | none | "All clear" | two-stage semantics F-017 |
| `( )` | `()` pair or `)` per parser state | none | "Bracket" | §17.1.4 smart insert |
| `%` | `%` postfix | none | "Percent" | semantics §17.1.5 |
| `÷ × − +` | operator (replace-on-operator) | none | "Divided by/Times/Minus/Plus" | replacement F-005 |
| `7 8 9 4 5 6 1 2 3 0` | digit at caret | none | digit name | — |
| `.` | decimal point (guard: one per number) | none | "Point" | input normalization §17.1.1 |
| `⌫` | delete one char left of caret / selection | repeat 400 ms then 15 Hz | "Delete" | delete-stops-at-start; no wraparound |
| `=` | evaluate; history write; auto-balance | none | "Equals" | trailing-operator rule F-004 |
| `INV` | toggle inverse/secondary sci keys | none | "Inverse" | toggle persists per session only |
| `sin cos tan` | `sin(` … | none | function name | auto-open bracket |
| `π e` | constant | none | "Pi"/"Euler's number" | — |
| `^` | `^` | none | "Power" | right-assoc |
| `√` | `√(` | none | "Square root" | — |
| `ln log` | `ln(` / `log(` | none | "Natural log"/"Log base 10" | — |
| `!` | `!` postfix | none | "Factorial" | integer domain |
| `sin⁻¹ cos⁻¹ tan⁻¹` (INV) | `asin(` … | none | "Inverse sine" etc. | DEG/RAD aware |
| `DEG/RAD` toggle | switch angle mode | none | "Angle mode degrees/radians" | persisted setting |
| history button | open history sheet | none | "History, n entries" | persistent control (E1 parity) |

Edge-case register for the calculator (TC-CALC-edge*):

| Input / situation | Required behavior |
|---|---|
| `00.5` | renders `0.5` (leading zero normalization, value exact) |
| `1.2.3` | second dot ignored (input guard), expression remains valid |
| `5+%` | syntax error card with caret hint (percent needs left operand) |
| `((2+3)` | auto-balance → `25` |
| `()` empty pair | syntax error card; AC recovers |
| `2+-3` | `2−3` after replacement rule → `-1` |
| `2--3` | unary fold → `2−(−3)` = `5` |
| `10!` | `3628800` |
| `170!` | error card (overflow, reason shown) |
| `π^2` | inexact path, renders `9.869604401` |
| `sin(90)` (DEG) | `1` exactly (degree identity reduction) |
| `cos(0)` | `1` exactly |
| `tan(90)` (DEG) | domain error card |
| expression of 512 chars | input blocked at limit with counter chip |
| rapid 30 keystrokes/s (stress) | no dropped chars, no frame > 24 ms (TC-PERF-key) |
| `=` with empty expression | no-op, no history row |
| history 500 rows + new solve | oldest unpinned evicted, pinned kept |
| MUse with empty memory | action disabled with tooltip "Memory is empty" |
| theme change mid-selection | selection preserved, pill repositioned |
| process death mid-expression | expression+caret+selection restored (F-043 family) |

## 7.3 Notes

- **List**: cards (title + snippet + date + pin + checklist progress); sections: Pinned / Others; search field on top; sort menu (date-edited default, date-created, title); view toggle list/grid; trash entry point.
- **Editor**: title field, body with lightweight rich text (bold, italic, H1/H2, bullet list, checkbox list, divider), toolbar (B I H1 • ☑ ―), undo/redo, pin toggle, background color (6 palette options, token-defined), attach from Files, and the **AI row** (§16.3): `Summarize · Rewrite · Checklist-ify · Find related` — each optional, each preview-with-undo, each disabled with a visible reason when its pack is missing ("Install the Essentials pack in Diagnostics").
- Checklists: tap checkbox toggles; progress `3/7` shows on the list card.
- Note storage: a single `note` table + FTS mirror (§12.2); bodies are a structured JSON document (§17.3) — never HTML strings — so search, export (Markdown) and import are lossless.
- Autosave 500 ms after typing stops; drafts survive process death; trash keeps 30 days with restore.

![Notes list and editor with the on-device AI action row.](figures/fig-notes-wireframe.png)

## 7.4 Scanner

- **Viewfinder** (CameraX): guide-frame corners, tap-to-focus, torch toggle, shutter, batch counter chip ("3 pages"), import-from-Files button (image/PDF import path works when camera permission is denied — the module is still usable).
- **Capture pipeline**: auto-crop via document-corner detection → optional filter (`Original`, `Gray`, `B&W`) → multi-page document.
- **OCR card** per page: recognized text editable; actions `Copy / → Notes / Re-OCR / Delete`; language initially `en` (Latin); the OCR model is the Essentials pack (§16.5) — without it, capture+export still work and the card shows "OCR needs the Essentials pack".
- Export: single page → image/PDF into Files; document → PDF with page order editor; text → new note or clipboard. Images are stored app-private; "Clean scans" in Files analyzer can purge them by size.

![Scanner viewfinder and OCR result card.](figures/fig-scanner-wireframe.png)

## 7.5 Calendar

- **Month grid + agenda below** (the wireframe layout): today circled, event dots, agenda rows for the visible day(s); swipe between months; `Today` chip when scrolled away; list alternative view.
- **Event editor**: title, all-day toggle, start/end date-time pickers (local time), **Repeat** menu (None, Daily, Weekly on <day>, Monthly on day <n>, Yearly, Custom — Custom exposes the supported RRULE subset §17.4), Alert (None/At start/5/15/30/60 min before/1 day before), Note field, calendar color (personal palette).
- Reminders fire via exact alarms (`SCHEDULE_EXACT_ALARM` with `USE_EXACT_ALARM`-policy compliance — see §14.4: the app targets a category allowed to use inexact fallback gracefully if the OS revokes exact); full-screen intent permission NOT used (a heads-up notification with sound + vibration is enough; avoids the special-access permission).
- ICS: import multiple events from a `.ics` in Files; export single event or a date range (respects the supported RRULE subset both ways; unsupported RRULEs import as one-off with a note).
- No accounts, no invites, no attendees — a personal calendar.

![Calendar month+agenda and the event editor.](figures/fig-calendar-wireframe.png)

## 7.6 Files

- **Browser** over: (a) app-private storage (`Files`, `Scans`, `Recordings`, `Backups`, `Exports`), (b) user-added SAF roots (persistent URI grants), (c) the media folders the user granted via `READ_MEDIA_*` for music import (read-only).
- Operations: open (hand-off to system viewers via `ACTION_VIEW` with `FLAG_GRANT_READ` — works offline), rename, move (private+SAF), copy, delete (to app trash for private files), new folder, sort (name/date/size/type), multi-select with actions, search (name + content for text formats).
- **Storage analyzer**: donut by category (Scans, Audio, Notes+DB, Exports, Other) computed locally, with `Clean scans` (deleteable-by-age) and `Export report` (JSON into Exports).
- Encrypted export: `Backups` produces a `.msone` archive (zip of JSON+files, AES-256-GCM with a key from the user's passphrase via PBKDF2, §14.3); import verifies and restores.

![Files browser and storage analyzer.](figures/fig-files-wireframe.png)

## 7.7 Music

- **Library** tabs: Songs, Albums, Artists, Folders, Playlists. Import: on first open, offer folder pick (SAF) or MediaStore scan of the granted audio; library is a Room mirror with artwork thumbnails cached.
- **Player**: artwork, title/artist, seek bar, prev/play/next, shuffle/repeat (off/all/one), speed (0.5–3.0×), sleep timer (5/15/30/60 min/end-of-queue), queue view with drag-reorder.
- Playback via Media3; a compact **MiniPlayer** persists over module screens; headset (media button) and Bluetooth controls work; audio focus respected (duck on navigation prompts); gapless for consecutive tracks; no lyrics fetching (offline).
- Playlist export: M3U (relative paths where possible) into Files.

![Music library and now-playing surfaces.](figures/fig-music-wireframe.png)

## 7.8 Recorder

- **Record screen**: big timer, live waveform, `Pause/Resume`, `Flag` (drop a timestamped marker, with optional 20-char label), `Done`. Recording is a **foreground service** with a persistent notification (pause/resume actions); mic permission requested at first record with a one-line privacy line ("Audio never leaves this phone").
- **Saved recording screen**: file card (duration, codec, size), markers list (tap to seek), `Transcribe` and `Summarize` buttons (pack-gated, §16.5), rename, delete (trash), `→ Notes` (creates linked note with transcript/summary).
- Formats: AAC-LC 96 kbps default (storage-friendly), WAV optional setting; recordings land in app-private `Recordings/` and are visible/copyable through Files.
- Transcripts are stored with segment timestamps; searchable from hub search when present.

![Recorder capture and saved-recording surfaces.](figures/fig-recorder-wireframe.png)

## 7.9 Diagnostics

- **Health cards**: storage (free %, DB size), battery (no wakelock abuse statement computed from actual counters), database integrity (`PRAGMA integrity_check` result, schema version), AI packs status.
- **Self-test**: runs engine property-suite smoke (100 cases), DB round-trip, model-pack hash verification, notification channel, alarm-can-schedule check; outputs a local result card.
- **Logs**: rolling in-app log ring (7 days, 2 MB cap, PII-scrubbed per §28.3); `Share log` exports via system share sheet (user-initiated only).
- **Model packs manager**: list packs (Essentials, Speech, Assistant) with status (`installed SHA ✓`, `not installed · size`), install = import pack file from Files, verify SHA-256 against the pack manifest, enable/disable, delete. No download path exists in the app (C5).

![Diagnostics health and model-pack manager.](figures/fig-diagnostics-wireframe.png)

## 7.10 Settings (global)

Sections: **Appearance** (theme Light/Dark/System, dynamic color on A12+, key theme/shape shortcuts), **Calculator** (haptics, fraction display, effects), **Privacy** (app lock with device credential, encrypted backup passphrase change, trash-empty-now), **Reminders** (default alert, sound per channel), **Storage** (link to Files analyzer), **AI packs** (link to Diagnostics manager), **About** (version, build provenance block — commit SHA, CI run link text, APK SHA-256 — the same provenance the owner's reports carry), **Licenses** (OSS licenses screen).

App lock (optional, off by default): locks on background>2 min; uses `BiometricPrompt` with device-credential fallback; zero biometric data stored by the app.

## 7.11 States, errors, and edge cases (module-spanning)

| State | Rule |
|---|---|
| Empty | One icon + one sentence + one action. Calculator history empty: "Solved calculations appear here." |
| Loading | Only for > 100 ms local work: first Files scan, first music import, OCR runs (progress on card), LLM runs (streaming preview). |
| Error | Local errors only; message + one action ("Try again" only when retry can succeed; otherwise "Open Diagnostics"). |
| Permission denied | Feature degrades per §7.11 (this table); never dead-ends. |
| Storage full | Global banner once: "Storage is full — recordings and scans will fail. Clean up in Files." Writes fail soft with per-operation messages. |
| Battery saver | Effects default to None; AI jobs above size threshold deferred with a visible chip. |
| Process death | All drafts/expressions/selections restored (§12.6). |
| Very long content | Expression 512 chars max (enforced, counter at 500+); notes unlimited but list virtualizes; recordings capped by storage check (refuse start when < 50 MB free). |

## 7.12 Responsive behavior (phones, tablets, landscape)

- ≥ 600 dp width: hub grid becomes 4-column; Calculator becomes two-pane (history side panel instead of sheet; keypad centered max-width 480 dp); Notes becomes list+editor two-pane; Calendar month+agenda side-by-side; Music player expands artwork with queue side panel.
- Landscape phones: Calculator keeps keypad full-width with scientific pad as horizontal scroll row; Recorder keeps controls reachable (bottom).
- All screens support font scale 2.0 without clipping (scroll instead of truncate); none require landscape-only.

## 7.13 What the UX deliberately does not include

No onboarding carousel (a first-run card is enough); no ratings/feedback prompts; no "what's new" popups (a quiet About → changelog list instead); no notification badges beyond reminder alarms; no sounds other than playback and alarms; no emoji in UI copy.

## 7.14 Module edge-case registers (normative)

Notes (TC-NOTE-edge*):

| Situation | Required behavior |
|---|---|
| Note with 10 000 blocks | editor virtualizes; save < 300 ms; no ANR |
| Paste of 1 MB text | import as one block with cap notice at 100k chars |
| Concurrent edit impossible (single user) — but process death mid-keystroke | last good autosave + draft restore |
| Title-only note | allowed; list shows title, snippet placeholder "No additional text" |
| Empty note closed | discarded entirely — nothing was written, so there is no trash entry and no confirmation dialog |
| Checkbox spam (50 toggles/s stress) | progress recomputes, no dropped toggles |
| Markdown import of unknown syntax | preserved as raw block, rendered plain, one-time notice |
| Export note with image attachments | images included in export archive |
| Search query with FTS operators (`AND`, quotes) | sanitized to plain terms, still matches |

Scanner (TC-SCAN-edge*):

| Situation | Required behavior |
|---|---|
| Camera permission permanently denied | import-from-files path + explainer card; module never dead-ends |
| Photo without document edges | manual crop UI fallback (corner drag) |
| OCR on blurry image | low-confidence badge; Re-OCR suggests retake |
| 50-page batch | page manager paginates; export PDF < 10 s Tier B |
| Duplicate page detection | warn chip "Page 3 looks like page 2" with remove action |
| Storage full mid-capture | capture blocked at shutter with storage card, no partial page |
| Rotate device mid-review | page order preserved |

Calendar (TC-CAL-edge*):

| Situation | Required behavior |
|---|---|
| Event across DST boundary (recurring) | occurrences per ADR-08 offsets; golden corpus cases |
| Monthly on the 31st | skip short months (default) / clamp (setting) |
| Alarm during Doze | fires within policy window; no missed silent drops |
| ICS with VALARM, ATTENDEE | VALARM maps to reminderOffsetMin if supported; attendees ignored (documented) |
| 3 000 events load | month grid virtualized; agenda lazy |
| Overlap reminders | coalesced into one notification group per §13.8 channel |

Files (TC-FILE-edge*):

| Situation | Required behavior |
|---|---|
| SAF root revoked by system | root card shows "Access removed — re-grant"; no crash; re-grant restores |
| 50k-entry folder | virtualized; search still index-free substring with budget |
| Move 2 GB file cross-root | progress; cancel leaves source intact; disk-full pre-check |
| File without extension / weird UTF-8 name | renders; rename sanitizes only illegal FS chars |
| Hidden files | shown only via Sort menu toggle (persisted) |

Music (TC-MUSIC-edge*):

| Situation | Required behavior |
|---|---|
| File deleted while queued | skip next, toast-free row strikethrough, queue self-heals |
| Corrupt/unplayable file | row marked unplayable after 2 failures; library keeps entry with reason |
| 5 000-track library | library tabs virtualized; search < 120 ms first page |
| Bluetooth headset disconnect | pause (audio focus loss), state preserved |
| Speed change mid-track | seamless (no restart), pitch-corrected |
| Sleep timer end during gapless transition | fades out at next boundary (≤ 2 s) |

Recorder (TC-REC-edge*):

| Situation | Required behavior |
|---|---|
| Call arrives during recording | mic is taken by system: auto-pause with notification note (best-effort across OEMs) |
| Mic permission revoked mid-record (Settings) | service stops gracefully, file finalized to pause point |
| 3-hour recording | file fine (AAC ~130 MB); waveform decimates; markers seek correctly |
| Flag during pause | rejected with inline hint (documented) |
| Device storage hits threshold mid-record | graceful finalize + incomplete flag (§17.5) |
| Reboot during recording | file finalized at reboot broadcast; row marked interrupted |

Diagnostics/Settings (TC-DIAG-edge*):

| Situation | Required behavior |
|---|---|
| Pack file with wrong hash | import rejected, reason card, file not moved |
| Pack too large for remaining storage | pre-checked with required-size message |
| quick_check reports corruption | Diagnostics error card with backup guidance; app never auto-deletes |
| Log share when ring empty | share disabled with hint "No logs yet" |

## 7.15 Screen-by-screen walkthroughs (executor-facing UX narrative)

These walkthroughs describe each core screen exactly as the executor will build it — the regions top-to-bottom, the interactive elements, and the state transitions. They complement the wireframes (which fix layout) and the feature catalogue (which fixes behavior).

### 7.15.1 Calculator walkthrough

The screen opens on the last pad (basic/scientific) with the restored expression (or empty), caret at end. Top bar: hub breadcrumb (full flavor only), pad toggle, overflow kebab. Expression field occupies the upper third: canonical pretty text left-aligned, autoscrolling; the caret bar blinks 530 ms period; the live answer sits directly beneath in amber, right-aligned when expression overflows. The persistent history button docks at the field's top-right corner with an entry-count badge. Keypad fills the lower two-thirds. Interactions: any key press evaluates live answer; `=` animates per effects setting, writes history, renders result in display size beneath (replacing live answer), and moves caret after result so continued typing starts fresh (continuation uses exact internal value §17.1.2). Selection: long-press enters selection; pill floats; all B-actions per §7.2.2. Sheets (history/memory/settings) slide from bottom with drag handles; history replay paints before close. Theme changes crossfade 200 ms without layout shift.

### 7.15.2 Notes walkthrough

List: search bar, pinned section, cards with title/snippet/date/checklist-progress; FAB "new note". Editor: title auto-styled from first heading; toolbar chips (B I H1 • ☑ ―); body blocks render WYSIWYG; AI row collapsed above keyboard, expandable; overflow: pin, color, attach, export, move to trash. Autosave chip shows "Saving…"→"Saved" locally (300 ms display minimum so it never flickers). Transitions: list↔editor shared-axis X 200 ms; trash restores from list trash view with undo window.

### 7.15.3 Scanner walkthrough

Viewfinder with corner guides; bottom row Scan/Batch/Import; torch toggle floats right. On shutter: freeze-frame 250 ms with shutter sound-off (respects ringer), page thumbnail flies into batch chip. Review screen: page carousel, crop tool (auto first, manual corners draggable), filter chips, OCR card per page. Export sheet: PDF/image/text targets with destination (Files/Notes/clipboard). All progress is per-card (never blocking modal).

### 7.15.4 Calendar walkthrough

Month grid occupies upper 60%, agenda list below for selected day; tapping a day moves focus (dot rings), tapping an event opens editor; FAB "new event" pre-fills selected day. Editor fields stack per §7.5 with bottom-sheet date/time pickers; RRULE custom sheet shows human summary ("Every 2 weeks on Tue") with occurrences preview (next 3). Reminder test action in the editor overflow lets the user fire a sample notification immediately (confidence builder, offline).

### 7.15.5 Files walkthrough

Left rail (tablet) / dropdown (phone) switches root: Internal (sections), each SAF root, Media folders. Rows: icon-by-type, name, meta line, selection checkboxes on long-press. Actions bar appears contextually (share, move, copy, delete, rename). Analyzer tab: donut + category list; category tap lists files by size with clean actions. Breadcrumb truncates middle paths with leading "…" menu to jump levels.

### 7.15.6 Music walkthrough

Library tabs on top; rows show artwork thumb, title, artist; FAB shuffle-all. Player: full-bleed artwork card, scrubber, transport, speed/sleep chips in an expander; queue sheet lists upcoming with drag handles; MiniPlayer docks above nothing (no bottom bar) with 4 dp elevation. Import flow: first-open sheet explains two paths (SAF folder / MediaStore scan) with privacy line; progress card streams found-count.

### 7.15.7 Recorder walkthrough

Record screen: giant timer mono font, live waveform band, marker list beneath (latest first), controls Pause/Flag/Done bottom-centered. Saved list: cards with duration, date, marker count, transcript badge. Recording view: seekable waveform (scrub shows timestamp bubble), marker ticks overlaid, transcript segments (when present) tappable to seek. Transcribe/Summarize buttons show pack state inline.

### 7.15.8 Diagnostics walkthrough

Health cards grid; tapping a card opens detail (e.g., DB card → table counts + integrity + last backup age). Self-test runs inline with six step rows checking off; result card has Share. Packs tab: three pack rows with status chips + import button; pack detail shows models table (file, sha-prefix, purpose). About: provenance block, licenses, changelog.

### 7.15.9 Settings walkthrough

Sections list with summary lines; each section is a subpage (no mega-screen). Toggles write the settings registry directly (§17.7) with immediate effect; every control has an inline effect where possible (theme switch previews live behind the dialog on A12+ dynamic color).

### 7.15.10 Hub walkthrough

Covered by §5.6 regions; interaction notes: search field expands full-width on focus with recent searches; continue-row card shows a state icon (pencil/note/waveform) + timestamp; grid cells animate press 0.97; pinned strip scrolls horizontally with snap.

## 7.16 Tablet and landscape layout specifications (normative)

| Module | ≥ 600 dp width layout | Landscape phone |
|---|---|---|
| Hub | 4-col grid + right rail (continue+pinned stacked) | grid 3-col, search sticky top |
| Calculator | two-pane: history list left (360 dp), pad right centered ≤ 480 dp | keypad full-width; sci pad horizontal scroll row above; history as overlay sheet |
| Notes | list 40% / editor 60% split, draggable divider | editor fullscreen; list via back |
| Scanner | viewfinder left, OCR cards rail right | fullscreen viewfinder; cards sheet |
| Calendar | month left, agenda right | month scroll-row top, agenda below |
| Files | dual-pane browser (roots left) | rows + contextual bar unchanged |
| Music | player centered 480 dp with queue rail right | standard |
| Recorder | timer+waveform centered, markers right rail | standard |
| Diagnostics | cards 3-col grid | 2-col |
| Settings | two-pane (sections left) | standard |

Rules: two-pane states are independent (list selection does not reset editor); divider drag persists; on width loss the app falls to stacked layouts without losing state (rotation matrix TC-STATE covers each pane).

### 7.2.9 History card anatomy and memory reorder (normative)

History card (tap target ≥ 56 dp): result line `type/display` (grouped), expression line `type/bodyS` muted beneath, timestamp right-aligned `type/caption` (`27th Oct, 13:36`), pin affordance on long-press, error rows show the error card copy as result. Selected card ripples token; replay paints expression, never result (result recomputes — proving engine consistency, F-022 note).

Memory sheet reorder: rows show value + label; up/down affordances both as buttons and drag handles (a11y twin); reorder writes positions transactionally; MUse from the sheet inserts at caret of the underlying expression (sheet dismisses, caret unchanged).

## 7.17 First-run education per module (one line each, shown once, dismissable)

| Module | First-run line |
|---|---|
| Calculator | "Type naturally — try `200+10%`. Hold a number for Cut, Copy and memory actions." |
| Notes | "Notes save themselves. Select text and use the ✦ row for on-device AI helpers." |
| Scanner | "Point at a page. Text is read on this phone and can go straight into Notes." |
| Calendar | "Reminders ring even in airplane mode — alarms are set on the device." |
| Files | "Everything the app makes is here. Add any folder to manage it too." |
| Music | "Pick a folder once — your library stays on this phone." |
| Recorder | "Record, flag moments, and transcribe later (optional speech pack)." |
| Diagnostics | "Run a self-test any time. Nothing leaves this phone unless you share it." |
| Hub search | "One search across everything — it all lives here." |

Education lines appear only on first entry per module (`hub.firstRunCardsDone`-style per-module flags), never repeat, and are excluded from screenshot goldens via a test-mode flag.

## 7.18 Per-module performance feel budgets (user-perceivable norms)

| Module | Interaction | Budget (Tier B p50) |
|---|---|---|
| Calculator | keystroke → live answer | ≤ 16 ms (≤ 64 chars) |
| Notes | open note (1k blocks) | ≤ 250 ms |
| Notes | search first paint | ≤ 120 ms @20k notes |
| Scanner | shutter → review | ≤ 400 ms |
| Scanner | OCR page | ≤ 2.5 s (Tier C ≤ 6 s) |
| Calendar | month swipe | ≤ 100 ms |
| Files | open 50k-entry folder | ≤ 300 ms first paint, virtualized |
| Files | analyzer full walk | streamed, no jank, ≤ 3 s @100k files |
| Music | play press → audio | ≤ 300 ms |
| Recorder | record tap → FGS up | ≤ 200 ms |
| Hub | search first page | ≤ 120 ms @10k notes |
| App | cold start | ≤ 1.2 s (mycalc ≤ 0.8 s) |

These extend §23.6 from build-level to feel-level; the L4 perf cases assert them on the tier profiles.

# Chapter 8 — UX-level acceptance criteria

These criteria gate the design phase (G2) and are re-verified on the release build (G7). They are intentionally user-verifiable: the owner can check each one on a device in minutes.

| ID | Criterion | Pass condition |
|---|---|---|
| UX-001 | Two-tap reach | Every leaf screen reachable from cold start in ≤ 2 taps; audited via nav-graph traversal test |
| UX-002 | Cold start | App (hub) interactive ≤ 1.2 s p50 on Tier B emulator; calculator flavor ≤ 0.8 s |
| UX-003 | First run privacy card | Shown once; dismiss persists; wording contains "no internet permission" |
| UX-004 | Calculator layout | All 19 basic keys visible on a 320×480 dp screen without scroll; key ≥ 44 dp visual/48 dp touch |
| UX-005 | Caret behavior | Tap places caret between characters; caret visible in light+dark+all key themes; autoscroll keeps caret on screen |
| UX-006 | Live answer | Appears ≤ 1 frame after input stops (≤ 16 ms engine round-trip for expressions ≤ 64 chars, else 50 ms budget with no jank) |
| UX-007 | Selection pill | Long-press 250–350 ms opens pill; pill never covers the selected text (repositions above/below) |
| UX-008 | History replay | Tap paints expression before sheet close; double-tap does not double-paint (race guard) |
| UX-009 | Theme switch | Key theme change repaints keypad within 1 frame pair (≤ 32 ms) with 200 ms crossfade; region pixel-diff ≥ 10% |
| UX-010 | Dark mode | All screens reviewed in dark: no pure-white flashes, LED-amber live answer present on calculator |
| UX-011 | Font scale 2.0 | No clipped/truncated text on any core screen (scroll or wrap instead) |
| UX-012 | TalkBack pass | Core journeys (§9 J-journeys) completable with TalkBack; no unlabeled controls |
| UX-013 | Empty states | Every module has an empty state with a working action button |
| UX-014 | Undo affordance | Delete note/recording/event → undo snackbar ≥ 5 s; trash holds 30 days |
| UX-015 | Offline invisibility | String audit: zero occurrences of "offline", "sync", "retry connection", "no internet" in user-facing copy |
| UX-016 | Provenance screen | About → build info shows version, commit SHA, build date; matches release evidence |
| UX-017 | Landscape | No data loss or state reset on rotation in any module (incl. mid-recording, mid-capture) |
| UX-018 | Back semantics | System back matches expected pop on every screen (nav audit) |
| UX-019 | MyCalc flavor | Contains no hub/modules; overflow list exactly the six calculator items; no cross-module UI text |
| UX-020 | Screenshot suite | Roborazzi suite over design-system components passes with 0 unreviewed diffs |

A criterion may be refined into multiple automated cases in Chapter 20, but the UX-level statement above is what the owner reviews at the G2 gate.

## 8.1 UX criterion verification detail (how each UX-0xx is proven)

| Criterion | Verification method | Evidence artifact |
|---|---|---|
| UX-001 | nav-graph traversal test computes shortest path per screen | TC-NAV-001 JSON |
| UX-002 | Macrobenchmark cold start, 10 iterations, p50 | perf HTML + JSON |
| UX-003 | fresh-install test asserts single show; relaunch asserts absent | L4 log |
| UX-004 | layout test on 320×480 dp: all keys visible; bounds scan ≥ thresholds | screenshot + bounds JSON |
| UX-005 | tap coordinates between glyphs; screenshot caret present; autoscroll case | screenshots |
| UX-006 | benchmark engine round-trip; compose tracing frame report | benchmark JSON |
| UX-007 | long-press timing sweep 200–400 ms; pill bbox vs selection bbox | screenshots |
| UX-008 | replay double-tap; count expression paint events via state log | L4 log |
| UX-009 | screenshot key-region before/after Rose; pixel-diff ≥ 10% | diff image + number |
| UX-010 | dark-mode screenshot sweep; token asserts for LED/amber/caret | screenshots |
| UX-011 | fontScale 2.0 sweep; clipping detector (bounds vs text layout) | JSON |
| UX-012 | TalkBack journeys J-04/J-08 green | a11y audit output |
| UX-013 | visit each module fresh; EmptyState visible; action works | screenshots |
| UX-014 | delete flows; snackbar present ≥ 5 s; trash count | L4 log |
| UX-015 | strings.csv scan for banned vocabulary | CI grep output |
| UX-016 | About text vs BuildConfig vs evidence manifest equality | JSON |
| UX-017 | rotation matrix; state hash before/after | logs |
| UX-018 | back-stack assertions per screen | nav audit JSON |
| UX-019 | flavor dex scan + overflow label list assert | CI outputs |
| UX-020 | roborazzi clean run on release branch | CI artifact |

## 8.2 Extended UX criteria (UX-021…UX-040)

| ID | Criterion | Pass condition |
|---|---|---|
| UX-021 | Calculator one-hand reach | `=` center ≤ 55% screen height from bottom on 6.1" profile |
| UX-022 | History sheet snap | drag-open ≥ 3 velocity bands; back gesture closes; scroll preserved |
| UX-023 | Theme picker preview | long-press a theme previews it live; release reverts unless tapped |
| UX-024 | Effects preview | picker plays a sample animation per row on first scroll-into-view |
| UX-025 | Note autosave chip | never flickers < 300 ms; "Saved" fades 800 ms |
| UX-026 | Scanner shutter latency | freeze ≤ 250 ms; review entry ≤ 400 ms p50 |
| UX-027 | Calendar day tap | agenda crossfade ≤ 150 ms; no layout jump |
| UX-028 | Files breadcrumb jump | middle-path menu opens ≤ 100 ms with 50k entries cached |
| UX-029 | Player scrub | waveform/timestamp bubble tracks finger 1:1; release seeks once |
| UX-030 | Recorder flag reachability | Flag within thumb arc on 6.1"; reachable one-handed |
| UX-031 | Search zero-state | recents ≤ 80 ms paint; clear affordance visible |
| UX-032 | Global back predictability | predictive-back previews on A33+ on all sheets |
| UX-033 | Dark pure-black option | A10+ OLED black background setting; screenshots goldens |
| UX-034 | Icon legibility | all 8 module glyphs recognizable at 24 dp (review shot) |
| UX-035 | Error card tone | no blame language ("Can't" not "You failed to"); strings audit |
| UX-036 | Confirmation weight | destructive confirms require explicit tap on danger label, never Enter-by-default |
| UX-037 | Loading honesty | skeleton only > 300 ms operations; no spinners on instant ops |
| UX-038 | Notification actions | recording/playback actions ≤ 3; labels single verbs |
| UX-039 | First-run time-to-value | fresh install → first calculation ≤ 3 taps |
| UX-040 | Consistency audit | identical confirm-sheet pattern across modules (screenshot strip) |

## 8.3 Final UX criteria (UX-041…UX-050)

| ID | Criterion | Pass condition |
|---|---|---|
| UX-041 | History card density | 6+ cards visible on 6.1" without scroll feeling cramped (review shot) |
| UX-042 | Memory reorder discoverability | both affordances visible ≥ 4.5:1 contrast |
| UX-043 | Editor toolbar reach | toolbar within bottom-40% on phones |
| UX-044 | Scan review carousel | page switch ≤ 100 ms cached; indicator position honest |
| UX-045 | Repeat preview honesty | preview list == generated occurrences (engine shared) |
| UX-046 | Analyzer honesty | donut % sums to 100±1; tooltip numbers == list numbers |
| UX-047 | Queue drag | drop reorders without playhead glitch; audio continues |
| UX-048 | Marker tap accuracy | seek lands within ±150 ms of marker offset |
| UX-049 | Self-test timing | completes ≤ 10 s on Tier C; progress steps animate |
| UX-050 | About parity | version string identical in: About, release notes, evidence manifest |
