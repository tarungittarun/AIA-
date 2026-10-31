## 6.12 UI design grammar (how any screen is composed)

Every screen in the product is assembled from the same grammar. An executor who has internalized these six rules can build any screen in this document — or correctly refuse a screen that breaks them.

**The five-layer anatomy (bottom → top):**

| Layer | Contents | Rules |
|---|---|---|
| L1 Background | `color/background` (or pure-black variant) | never holds content directly; one layer only |
| L2 Surface | cards, sheets, bars: `color/surface` + `elevation/*` + `radius/*` | surfaces group; never nest surfaces more than 2 deep |
| L3 Content | text, media, waveforms, grids: `type/*` + `color/onSurface*` | content is the screen (X4); chrome shrinks around it |
| L4 Controls | buttons, keys, FAB, selection pill, toolbars | ≥ 48 dp touch; only `color/primary`/`danger` accents |
| L5 Overlays | sheets, dialogs, snackbars, MiniPlayer, AI previews | one blocking overlay at a time; back always dismisses |

**The slot template (every screen answers five slots):**

1. **Bar slot** — `AppTopBar`: title = screen name (or context object), nav = back/home, actions ≤ 3 + overflow. Calculator hides the bar into the field area by design (§7.2); that is the single sanctioned exception.
2. **Primary canvas slot** — the module's reason to exist (expression field, note blocks, month grid, waveform). Gets the largest area and the first 200 ms of attention.
3. **Action slot** — the primary action lives in the bottom third (FAB, keypad, transport controls, Done). One primary per screen; secondaries are text buttons or overflow.
4. **Status slot** — inline, per-card or per-row feedback (saving chip, OCR progress, marker count). Never a global modal spinner (§4.3).
5. **System slot** — insets, gesture areas, IME detection (to *move content*, never to enable typing in Calculator — F-033).

**Selection map (job → component):** list of items → `ResultRow` in `LazyColumn`; single choice → `BottomSheet` with radio rows; confirm → `ConfirmSheet`; text entry → inline field (no dialog input); progress > 300 ms → per-card indicator; empty → `EmptyState`; error → `ErrorState`; anything else → do not invent (propose via ledger, §15.7).

**Rhythm and spacing:** all vertical rhythm is a multiple of `space/unit` (4 dp): row height 56 = 8+40+8; card padding 16; section gap 24; screen margin 16. If a layout needs 10 dp, the layout is wrong — drop to 8 or up to 12.

**Elevation ladder:** list card 1 dp → bar 4 dp → dragged item 8 dp → sheet 8 dp → dialog/FAB 8–12 dp. Two surfaces at the same elevation must never overlap; that is a design bug, not a shadow problem.

**Worked example — Notes list in grammar terms:** L1 background; L2 = search surface chip + note cards; L3 = card text (`titleS` title + `bodyS` snippet + `caption` date, checklist progress chip); L4 = new-note FAB (action slot) + card overflow icons; L5 = none at rest, delete snackbar on event; slots: bar "Notes", canvas = pinned+others lists, action = FAB, status = autosave chip inside editor only.

## 6.13 Figma workflow — design linking, usage and the design↔code loop

Figma is the **design mirror** of this blueprint; the repository is the law. This section defines the exact linking so any designer, reviewer or the AI agent can move between frame and code without translation loss.

![Figma workflow: one-way sync from repo tokens, component mapping, design-QA acceptance loop, and the agent access policy.](figures/fig-figma-workflow.png)

**File structure (`MySpace One DS` — file key recorded in `design/figma/README.md`):**

| Page | Contents | Linked to |
|---|---|---|
| `00 Foundations` | color styles, type styles, effect styles, grid styles, Variables sets (Light/Dark) | `tokens.csv` (§6.2, §6.7) |
| `01 Components` | `DS/*` component library with variants and auto-layout | `core/designsystem` composables (§6.4, §6.8) |
| `02 Hub` … `09 Diagnostics` | one page per module: all screens, all states (empty/content/error/loading), light+dark | Chapters 7, §6.14 inventory |
| `10 Prototype flows` | J-01…J-10 journey prototypes (step names = harness step names) | §9.12, Appendix R |
| `11 Archive` | deprecated frames (never deleted — the owner's preservation standard) | ledger |

**Naming and mapping contract:**

| Figma object | Name pattern | Code counterpart |
|---|---|---|
| Variable / style | `color/primary`, `type/body`, `space/l`, `radius/m`, `motion/standard` | token constants (§6.2, §6.7) |
| Component | `DS/AppTopBar`, `DS/CalcKey`, `DS/SelectionPill`, … | `AppTopBar`, `CalcKey`, `SelectionPill`, … (§6.4) |
| Variants | `theme=light/dark`, `state=empty/content/error`, `shape=circle/pill/…` | sealed state/enum params |
| Frame (screen) | `<MODULE>-<nnn> <Screen> <State>` e.g. `CALC-003 Calculator Selection` | screen + state id (§6.14 registry) |
| Prototype flow | `J-01 Scan to note` | journey harness id (§9.12) |
| Annotation | a11y plugin labels: role, focus order, announcement | Compose semantics (§6.6, §6.17) |

**Token pipeline (one-way: repo → Figma).** `tokens.csv` is canonical (TC-SYS-tokens). `tools/tokens-export.py` emits Tokens-Studio-compatible `tokens.figma.json`; the designer imports it into Figma Variables (or the owner's token pushes it via REST). Figma-only color tweaks are invalid — they ride a tokens PR or do not happen. This keeps the detekt no-hardcoded-color rule and the screenshot goldens meaningful.

**Using Figma to build (the agent's or a developer's read path):**

1. Open the screen's frame from the §6.14 registry (or Dev Mode search by name).
2. Dev Mode spec panel shows: token names for every fill/text (never raw hex in review), spacing multiples, auto-layout values → these are the §6.15 redlines.
3. Component descriptions in `01 Components` carry the code anchor (`core/designsystem/…/AppTopBar.kt`) and the binding § refs.
4. Prototype flows demonstrate intended motion (compare §6.5 durations); Figma smart-animate values are illustrative, the motion tokens are normative.
5. Any behavior not visible in a frame lives in this document (§ chapters) — frames show *look*, the document rules *behavior*; conflicts resolve to the document and a ledger entry.

**Design-QA acceptance loop (UI acceptance against Figma, §6.18 operationalizes it):** per screen, export the frame at 1080×1920 and compare to the Roborazzi golden: perceptual hash ≥ 0.98, token-derived colors exact, key spacing within ±2 dp. Diffs produce a side-by-side artifact reviewed at gates. The loop closes design↔code drift mechanically instead of by eye.

**AI agent access policy.** If the owner issues a read-only Figma REST token, the agent may read frame specs, exports, variables and component descriptions to sharpen implementation fidelity; it may not edit the file, treat Figma-only additions as scope (§1.4), or import plugin output as code. If no token exists (the default), the agent builds from this document alone — it is complete by design, and every visual fact needed is in §6.14/§6.15 and the wireframes.

**Version discipline.** Design changes land as PRs to `tokens.csv`/components + a Figma re-sync in the same merge (docs-drift gate covers `design/figma/README.md` staleness). Figma branch/merge flows mirror the repo: a design PR = a frame branch; merged = moved out of Archive only via PR.

## 6.14 Screen inventory with Figma frame registry (master UI table)

This table is the single registry of every screen: route, wireframe/section, states, and the Figma frame ids that mirror it. It is mirrored as `docs/blueprint/ui-screens.csv` (generated-checked like `qa/testcases.csv`). The build checklist columns serve G4/G6 review (this table supersedes the pointer-former Appendix M).

| # | Screen | Route | Figma frames (page) | States to build | Spec |
|---|---|---|---|---|---|
| 1 | Hub Home | `myspace://hub` | HUB-001..004 (02) | first-run, content, search-zero, recovered | §5.3, §5.6 |
| 2 | Hub search results | `hub/search` | HUB-010..012 (02) | streaming, grouped, semantic-tagged | §5.5, §5.7 |
| 3 | Calculator main (basic) | `calc` | CALC-001..006 (03) | empty, typing, live-answer, selection+pill, caret-menu, result | §7.2, §7.2.1–.3 |
| 4 | Calculator scientific | `calc?pad=sci` | CALC-010..013 (03) | INV on/off, DEG/RAD | §7.2.3 |
| 5 | History sheet | sheet | CALC-020..023 (03) | empty, list, pinned, replay-paint | §7.2.4, §7.2.9 |
| 6 | Memory sheet | sheet | CALC-030..032 (03) | empty, slots, reorder | §7.2.5, §7.2.9 |
| 7 | Calculator settings sheet | sheet | CALC-040..042 (03) | defaults, theme/shape pickers | §7.2.6 |
| 8 | Effects picker | sheet | CALC-045..046 (03) | 4 styles + preview | §7.2.5 |
| 9 | MyCalc home | flavor root | MCALC-001..006 (03) | same as CALC subset, zero module UI | §7.2.7 |
| 10 | Notes list | `notes` | NOTE-001..005 (04) | empty, pinned, grid view, trash-entry | §7.3 |
| 11 | Notes editor | `notes/{id}` | NOTE-010..016 (04) | typing, checklist, AI row (ready/running/missing), autosave chip | §7.3, §16.3 |
| 12 | Notes trash | `notes/trash` | NOTE-020..021 (04) | items, empty | §7.3, F-050 |
| 13 | Scanner viewfinder | `scan` | SCAN-001..004 (05) | guides, batch chip, denied-import card | §7.4 |
| 14 | Scanner review | `scan/review` | SCAN-010..014 (05) | pages, crop, filters, dup warning | §7.4, §13.11 |
| 15 | Scanner OCR card | in review | SCAN-020..023 (05) | running, editable, low-conf, pack-missing | §7.4, F-057/59 |
| 16 | Scanner export sheet | sheet | SCAN-030..031 (05) | targets + destinations | §7.4 |
| 17 | Calendar month+agenda | `cal` | CAL-001..004 (06) | today, dots, agenda, empty day | §7.5 |
| 18 | Event editor | `cal/new` `cal/{id}` | CAL-010..015 (06) | fields, validation, repeat sheet + preview, test-alarm | §7.5 |
| 19 | Files browser | `files` | FILE-001..005 (07) | roots, rows, select-mode, saf-revoked | §7.6 |
| 20 | Files analyzer | `files/analyzer` | FILE-010..012 (07) | donut, category list, clean flow | §7.6 |
| 21 | Files trash | `files/trash` | FILE-020..021 (07) | items, empty | F-068 |
| 22 | Music library | `music` | MUSIC-001..005 (08) | tabs, import sheet, empty | §7.7 |
| 23 | Music player | `music/player` | MUSIC-010..014 (08) | artwork, speed/sleep chips, queue sheet | §7.7 |
| 24 | MiniPlayer | overlay | MUSIC-020..021 (08) | collapsed, hidden | §6.8 |
| 25 | Recorder record | `rec` | REC-001..004 (09) | idle, recording, paused, call-interrupted | §7.8, §13.10 |
| 26 | Recorder saved list | `rec/list` | REC-010..012 (09) | empty, cards, badges | §7.8 |
| 27 | Recorder recording view | `rec/{id}` | REC-020..025 (09) | waveform seek, markers, transcript, transcribe states | §7.8 |
| 28 | Diagnostics health | `diag` | DIAG-001..004 (10) | cards, self-test running/done/failed | §7.9 |
| 29 | Model packs | `diag/packs` | DIAG-010..013 (10) | installed, missing, importing, rejected | §7.9, §16.8 |
| 30 | Logs + share preview | `diag/logs` | DIAG-020..022 (10) | ring list, preview verbatim | §7.9, §28.3 |
| 31 | Settings root + sections | `settings/*` | SET-001..008 (10) | registry-driven rows, about provenance, licenses | §7.10 |
| 32 | App lock | overlay | SET-020..021 (10) | prompt, fallback | F-082 |
| 33 | Confirm sheets (global) | overlay | GLOB-001..003 (01) | destructive pattern | §6.8 |
| 34 | Snackbar/undo (global) | overlay | GLOB-010..011 (01) | undo pattern | UX-014 |
| 35 | Empty states (global) | per module | GLOB-020..028 (01) | 8 module empties + illustration | §6.11 |
| 36 | Tablet two-pane set | — | TAB-001..010 (11) | per §7.16 rows | §7.16 |
| 37 | Landscape set | — | TAB-020..026 (11) | calculator, recorder, calendar | §7.16 |
| 38 | Font-scale 2.0 set | — | A11Y-001..010 (11) | core screens at 2.0 | UX-011 |

## 6.15 Redline specifications (numbers an implementer can build from)

Global redlines (apply everywhere; per-screen deltas only where §7 states otherwise):

| Element | Redline |
|---|---|
| Screen margin | 16 dp left/right; 8 dp top under the bar |
| Top bar height | 56 dp; large-title variant 96 dp collapsing to 56 on scroll |
| List row (single line) | 56 dp: icon 24 dp at x16, text x56, chevron/trail at right-16 |
| List row (two lines) | 72 dp: title `titleS` at +12, subtitle `bodyS` at +34 |
| Card padding | 16 dp; inter-card gap 8 dp; section header gap 24 dp top / 8 dp bottom |
| FAB | 56 dp, margin 16 dp, above insets + 16 dp |
| Keypad key | height 52 dp basic / 44 dp scientific rows; gap 6 dp; side padding 12 dp; touch bounds ≥ 48 dp |
| Expression field | text `displayMono` 30 dp, left 20 dp; caret 2 dp wide, line-height tall; live answer `type/titleM` right-aligned 20 dp |
| Sheet | radius 24 top, handle 32×4 at +8, content padding 20 dp, max height 90% |
| Snackbar | above insets + 8 dp, full-width minus 16 margins, 4.5 s default |
| Selection pill | height 40 dp, radius 20, shadow 8 dp, offset 8 dp above selection bbox (below if clipped) |
| Touch targets | ≥ 48×48 dp everywhere; icon buttons 40 dp visual + 8 dp invisible bounds |
| Focus ring (keyboard) | 2 dp `color/primary`, offset 2 dp, radius follows target |

Screen-specific redlines live as Figma Dev Mode specs per §6.14 frames and repeat in the frame annotations; where this table and a frame disagree, the frame's numbers win only if they are multiples of the 4 dp grid — otherwise the table wins (ledger entry on the frame).

## 6.16 Interaction specification index (control-level motion + haptics)

| Control | Trigger | Motion (token) | Haptic | State after |
|---|---|---|---|---|
| `CalcKey` | press down/up | scale 0.97, 120 ms | tick (if on) | inserted; live answer updates |
| `=` key | press | none on result (instant) + effects if set | confirm tick | history row written |
| `AC` | press | none | tick | selection or expression cleared |
| Selection pill | long-press entry | scale-in 150 ms at touch point | double-tick | selection mode |
| Selection resize | slide | live highlight; pill follows x | none | selection bounds |
| History replay | card tap | sheet closes after paint (≥1 frame) | none | expression painted, caret end |
| Sheet | open/close | 250 ms slide, damping 0.8; back dismisses | none | previous focus restored |
| Checkbox | tap | 150 ms fill | tick | progress chip updates |
| List reorder | drag | lift 8 dp, settle 180 ms | tick on drop | positions persisted |
| Swipe-to-delete | swipe | row collapse 200 ms + undo snackbar 4.5 s | none | trash (undoable) |
| FAB | press | 200 ms extend (extended variant) | none | create flow opens |
| MiniPlayer | track change | crossfade title 200 ms | none | progress resets |
| Record | press | FGS ≤ 200 ms; timer starts on first sample | long-tick | notification visible |
| Flag marker | press | marker dot drops onto waveform (150 ms) | tick | marker row |
| Theme change | pick | 200 ms crossfade; no layout shift | none | persisted |
| Pull-to-refresh | — | not used anywhere (nothing to refresh — X6) | — | — |

## 6.17 Accessibility annotations (Figma labels → Compose semantics)

Figma a11y annotations (plugin format) ride every frame: `role`, `label`, `focus-order`, `announcement`. The code contract mirrors them 1:1:

| Frame annotation | Compose implementation | Test |
|---|---|---|
| `role: button` | `Modifier.semantics { role = Role.Button }` | TC-A11Y scan |
| `label` | `contentDescription` or `semantics { contentDescription }` (keys announce actions: "plus", "equals") | TC-A11Y-calc-01 |
| `focus-order: n` | explicit `semantics { traversalIndex = n }` on custom layouts | focus-order test |
| `announcement` (live) | `liveRegion = LiveRegion.Polite` on live answer, saving chip, OCR progress | UX-006/025 |
| decorative | `clearAndSetSemantics { }` (excluded from tree) | tree scan |
| heading | `semantics { heading() }` on section titles | TalkBack rotor |

Focus-order defaults per core screen: Hub = search → continue → grid (row-major) → pinned → overflow; Calculator = expression (readonly announce) → history button → pad row-major (`=` last); Notes editor = title → toolbar (grouped) → blocks → AI row → overflow. Dialogs trap focus and restore on dismiss (§6.6).

## 6.18 Design-QA gate (per-screen UI acceptance)

A screen is UI-accepted at G4/G6 when every row below has an artifact:

| # | Check | Bar | Artifact |
|---|---|---|---|
| DQ-1 | Grammar compliance (§6.12) | slots/layers correct; no invented components | review note |
| DQ-2 | Tokens only | detekt rule clean; screenshot colors == token expectations | CI rule + goldens |
| DQ-3 | Figma fidelity | frame export vs golden: pHash ≥ 0.98; spacing ±2 dp | side-by-side diff |
| DQ-4 | States complete | empty/content/error/loading (+ module-specific) all built and shot | screenshot set |
| DQ-5 | Redlines | §6.15 numbers hold (bounds scan) | bounds JSON |
| DQ-6 | Motion | §6.16 table honored; reduced-motion kills all | recording/frames |
| DQ-7 | A11y | labels/roles/focus per §6.17; contrast token test green | a11y audit output |
| DQ-8 | Responsive | tablet/landscape rows built per §7.16 without state loss | screenshots |
| DQ-9 | Font scale | 2.0 no-clip sweep | clipping detector JSON |
| DQ-10 | Dark + themes | dark goldens; calculator themes × shapes matrix | screenshot matrix |

The gate reviewer is the agent (self-review, §18.4 UX checklist) with the owner spot-checking the side-by-side set. A failed DQ row is a defect with a screenshot pair — never a "known difference".

## 6.19 Where to find anything about UI (the everything-index)

| UI aspect | Normative home |
|---|---|
| Principles & emotional goals | §4.1–4.3 |
| Navigation, hub regions, search UI | §5.1–5.8 |
| Color/type/spacing/shapes/elevation tokens | §6.2, §6.7 |
| Component inventory + behavior specs | §6.4, §6.8 |
| Motion (system + control-level) | §6.5, §6.11, §6.16 |
| Icons & illustrations | §6.3, §6.11 |
| Key themes & shapes (calculator theming) | §6.9, §6.10 |
| Screen-by-screen behavior | §7.1–7.10 |
| States, errors, edge cases | §7.11, §7.14 |
| Responsive/tablet/landscape | §7.16 |
| First-run education lines | §7.17 |
| Feel budgets (latency per interaction) | §7.18 |
| Wireframes (19 figures) | figures index (Appendix BB) |
| Screen registry + Figma frames | §6.14 (+ `ui-screens.csv`) |
| Redlines | §6.15 |
| Design grammar | §6.12 |
| Figma workflow & linking | §6.13 |
| Accessibility annotations | §6.6, §6.17 |
| Microcopy strings | Appendix E |
| Gestures & control twins | Appendix H |
| UX acceptance criteria (all levels) | Chapter 8 (§8 table + §8.1–8.3) |
| UI test layers (goldens, a11y, journeys) | §20.2–20.4, Chapter 8 |
| Design-QA gate | §6.18 |

Nothing about the UI is decided anywhere else: if a pixel, dp, millisecond, label or frame id is not traceable to one of the rows above, it does not exist.
