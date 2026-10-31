@PART: PART III — DESIGN LANGUAGE, FIGMA WORKFLOW AND SCREENS
@PARTDESC: The token system, typography, themes, motion; the Figma file contract and the screen registry the agent must obey; wireframes for the editor; accessibility annotations and the design-QA gate that blocks bad UI.

# Chapter 6 — Design language

## 6.1 The contract in one line

**OneDoc looks like a calm piece of paper with great tools.** The design system optimizes for long-form reading and writing: high legibility, low chrome, generous white space, and controls that appear when needed and disappear when not. Nothing in the UI blinks, bounces, or begs.

## 6.2 Tokens (single source of truth)

![OneDoc tokens: four ramps (ink, teal, amber, paper), typography scale, shape and motion values.](figures/fig-tokens.png)

All colors, type sizes, radii, spacing and durations are declared in **`design/figma/tokens.json`** and consumed two ways: the Figma library publishes them as styles/variables, and the Android build generates `OdTokens` from the same file (one-way, repo → Figma). Hand-picking a color in code or in Figma is a design-QA failure (DQ-1).

| Token group | Values |
|---|---|
| `color.ink.*` | #0F172A · #1E293B · #334155 · #64748B |
| `color.teal.*` | #134E4A · #0F766E (accent) · #14B8A6 · #5EEAD4 |
| `color.amber.*` | #92400E · #D97706 · #F59E0B · #FDE68A (highlights, warnings) |
| `color.paper.*` | #FFFFFF · #F8FAFC · #F1F5F9 · #E2E8F0 (surfaces) |
| `font.*` | display 28/34 · title 22/28 · h1 20/26 · h2 17/24 · body 15/22 · small 12/16 · code 13/18 (Inter, system fallback; editor body min 14 sp) |
| `radius.*` | s 8 · m 12 · l 16 · sheet 28 dp |
| `space.*` | 4 dp grid: 4 · 8 · 12 · 16 · 24 · 32 |
| `motion.*` | enter 150 ms · move 200 ms · sheet 250 ms; easing standard (decelerate 0.6) |

## 6.3 The eight themes

Light · Dark · Sepia · Paper (warm white, low blue) · High-contrast white · High-contrast black, each with a teal or amber accent choice — 8 effective combinations. "Match system" is the default. Themes restyle *surfaces and text only*; the teal accent and semantic colors keep their relative luminance contract so contrast guarantees hold per theme (DQ-4 verifies per theme, not just in light).

## 6.4 Typography rules

1. Editor body text defaults to 15 sp Inter (system serif and mono selectable in settings); minimum 14 sp anywhere.
2. Heading scale is fixed relative to body (H1 1.33×, H2 1.13×, H3 1.0× semibold) so user font-size scaling flows through everything.
3. Line length in compose mode targets 60–75 characters at default width on phones; margins adapt on tablets to keep the measure.
4. Dynamic type to 200% must not clip: every container either grows or scrolls; `fixedSize()` is a banned modifier in editor UI (DQ-5).

## 6.5 Iconography, imagery, empty states

Icons: Material Symbols (outlined), 24 dp, 2 dp stroke optical weight, single color from `ink`. No illustrations in tool surfaces; at most one restrained spot illustration per empty state, drawn from the paper metaphor. Empty states (UX-36): one line, one action.

## 6.6 Motion and haptics

Motion exists to explain continuity, never to decorate: sheet enter 250 ms, toolbar appear 150 ms fade+8 dp slide, block drag 200 ms settle. `Animator` durations scale by 0.5× under battery saver and vanish under reduced-motion (UX-44). Haptics: tick on mark toggle, double-tick on insert (AI/asset), single confirm on destructive press — calibrated via `HapticFeedbackConstants`, no vibration SDK.

# Chapter 7 — Figma workflow and the screen registry

## 7.1 Why Figma is in this document

The owner required the blueprint to specify how Figma links to development and how the file is used. The working model is **repo-first**: the repository is the source of truth for tokens; Figma is the mirror where the owner reviews and edits screens visually; changes flow back as token/registry pull requests. The agent never invents UI, and never waits on design: if a screen has a registry row, it is buildable; if it doesn't, the task is BLOCKED until a row exists.

## 7.2 The Figma file structure

File: **`OneDoc Design System`** (single file, two pages — "🧱 Foundations" and "📱 Screens"), mirroring the registry exactly:

| Figma page | Contents | Mirrors |
|---|---|---|
| Foundations | Color styles per token (`od/ink/900`…), text styles per token (`od/body/15`), effect styles, grid styles (4 dp), component set: buttons, chips, cards, toolbar, sheet, list item, FAB, app bar | `design/figma/tokens.json` |
| Screens | One frame per registry row, named `OD-<AREA>-<nnn> <name>`, organized in sections by area; every state in the registry's `states` column exists as a named variant or a marked frame | `docs/onedoc/blueprint/ui-screens.csv` |

Frame naming is the join key: `OD-EDIT-002` in Figma ⇄ `OD-EDIT-002` in the registry ⇄ `odEdit002` screen id in code. Redlines: spacing/type specs are attached as Figma dev-mode annotations; the agent reads them via the registry's exported CSV mirror rather than screen-scraping Figma.

## 7.3 The workflow (one-way sync, review loop)

![Figma workflow: tokens.json is the source; the Figma library and screens mirror it; owner edits return as reviewed token/registry PRs; the design-QA gate blocks merges.](figures/fig-figma-workflow.png)

1. **Agent** generates/updates tokens → runs the export script → commits both the JSON and the regenerated CSV mirror.
2. **Owner** (optional, no account needed by the agent) edits in Figma; at sync time the owner (or the agent with a read-only token, if the owner supplies one) exports the frame-name + style list and diffs it against the registry.
3. **Deltas** land as PRs titled `design: <frame-or-token>`; the design-QA checklist (§9.2) must pass before merge.
4. **The agent implements screens only from registry rows**; a frame without a row, or a row without a frame, fails DQ-3.

## 7.4 How the agent uses the file (no account required)

- **Default path:** the agent uses `ui-screens.csv` (screen id, frame, entry, exit, states, redline summary) as the buildable spec — it is committed to the repo and complete for v1.0.
- **Token path:** `design/figma/tokens.json` is authoritative for values; the CSV carries no values, only names.
- **Optional owner token:** if the owner provides a Figma personal access token in repo settings, the agent may run a nightly "registry drift" check (list frames, compare to CSV). Without a token, this check is skipped and drift is caught at the design-QA gate by the owner's review. The agent never requires Figma access to make progress — the CSV is sufficient.
- **Redlines:** for every interactive component, the CSV `redline` column names the Figma component and the key measurements (heights, insets, states). This is what the agent implements against.

## 7.5 The screen registry contract (normative)

`docs/onedoc/blueprint/ui-screens.csv` columns: `screen_id, name, figma_frame, area, entry, exit, states, redline, test_ids`. Rules:

1. Every screen in §3.4 has exactly one row; frame ids match Figma exactly.
2. `states` lists all reachable states (loading/empty/error/content + feature states); the implementation must render each one; the catalogue tests the P0 ones.
3. A PR that adds UI without a registry row is rejected by the design-QA gate (DQ-3).
4. The registry is regenerated from the blueprint appendix by `tools/onedoc/traceability.py --emit-registry`, so PDF, CSV and Figma names can never drift silently.

# Chapter 8 — Screen wireframes (editor)

## 8.1 The editor surface

![Editor (OD-EDIT-001/002): app bar with doc title and undo/redo; page canvas; floating selection toolbar; category tab row; assistant row with offline-only actions.](figures/fig-editor-wireframe.png)

The editor is a page metaphor, not a notes-list metaphor: text sits on a white page with margins and (in compose mode) dashed page-break guides (F-038). Chrome inventory is fixed: app bar (title, undo/redo, overflow), selection toolbar (appears on selection, §9 redlines), format tab row (Text · Insert · AI · Format) shown when the cursor is active and the keyboard is up, assistant row (only when relevant packs/tiers allow). Everything else — versions, export, find — lives in sheets so the page stays clean.

## 8.2 Behavior highlights tied to wireframe regions

| Region | Rules |
|---|---|
| App bar | Title shows doc title (editable via rename sheet); back is N1/N2; overflow holds Export, Find, Versions, Info, Settings |
| Page canvas | 16 dp side margins on phones; blocks are the touch units; tap empty page bottom = new paragraph at end |
| Selection toolbar | Layout: B I U S | H1 H2 H3 | list quote | align link; horizontal scroll beyond 8 actions; never covers selection (UX-19) |
| Tab row | Categories not commands: tapping Insert opens the insert sheet (image, table, divider, TOC, link); tapping AI opens the assistant sheet with availability reasons |
| Assistant row | Quick actions for the four assistant verbs when a selection or whole-doc context exists; hidden entirely when no AI capability is active (F-082) |

# Chapter 9 — Accessibility annotations and the design-QA gate

## 9.1 Accessibility is design, not a patch

Every screen ships with a traversal order matching the visual order; every interactive element has a role, a label and (where useful) a state description; every custom gesture has a menu equivalent. The editor exposes blocks as traversable units (F-084) with per-block actions: format, move up/down, delete, duplicate. Marks are announced as "bold, italic" prefixes on the affected text. Tables expose row/column headers. The full a11y acceptance script is catalogue section A11Y; the design-QA gate enforces the design half.

## 9.2 Design-QA gate (DQ-1 … DQ-8)

The gate runs as a PR checklist plus emulator checks; any DQ failure blocks merge of UI changes:

| ID | Check | Method |
|---|---|---|
| DQ-1 | No hardcoded colors/sizes in UI code: everything resolves to a token | Lint rule + code scan |
| DQ-2 | Touch targets ≥ 48 dp (44 dp inside toolbars) | Lint + Compose/View inspection on emulator |
| DQ-3 | Screen exists in registry with matching Figma frame; states match `states` column | Registry check in CI |
| DQ-4 | Contrast: body 4.5:1, large 3:1, high-contrast themes 7:1 — all 8 themes | Theme snapshot tests |
| DQ-5 | 200% font scale: no clipped/truncated text on all screens | Emulator `font_scale=2.0` screenshot diff |
| DQ-6 | Traversal order matches visual order; all actions reachable via TalkBack menu | Instrumented a11y audit |
| DQ-7 | Motion respects reduced-motion and battery saver | Emulator setting toggle test |
| DQ-8 | Empty/error states present per registry (no blank screens) | State-walk script per screen |

Gate evidence lands in `reports/gates/` alongside the build gates; DQ failures are defects (severity S3 unless they hide a functional break).

## 8.3 Scan surfaces (OD-SCAN-001 … 003)

| Screen | Purpose | States (registry `states` column) | Key redlines |
|---|---|---|---|
| OD-SCAN-001 camera | viewfinder with auto-capture on focus; page edges hint overlay | idle · focusing · captured-flash · no-camera-permission (rung-6 explanation + settings link) | shutter ≥ 56 dp bottom-center; permission state is a full-screen card, never a toast |
| OD-SCAN-002 review/crop | per-page perspective crop (4 corner handles, rotate ±90°), thumbnail queue with drag reorder (F-072) | single-page · queue · dragging · empty-queue | handles ≥ 48 dp; reorder uses long-press + drag with a11y "move page up/down" actions |
| OD-SCAN-003 OCR confirm | recognized text beside page image, confidence marks (UX-41), per-word fix field, insert CTA | processing (progress + cancel) · ready · no-pack (ends at save-image with reason, F-073) · low-yield (< 20 chars: warn, offer retry) | confidence uses color + underline style; fix field ≥ 44 dp; insert button bottom-anchored, always visible |

Rules: capture resolution fixed at 2048 px long edge; processing happens on the AI executor with a cancel that reaches the native runtime within one frame; the review screen is the only place OCR errors are fixable before insert — after insert, confidence marks are gone (document is plain text + optional source-image asset).

## 8.4 Assistant surfaces (OD-AI-001 … 003)

| Screen | Purpose | States | Key redlines |
|---|---|---|---|
| OD-AI-001 pack manager | list packs (OCR/ASR/LLM/embed), size, license, tier requirement, verify state; install via SAF; delete | no-packs (education card) · installed · verifying · failed (both SHAs, UX-48) · deleting-confirm | rows ≥ 64 dp; install is two explicit confirms (pick + SHA shown); no silent background verification loops |
| OD-AI-002 action sheet | the four verbs with availability per selection/doc context; unavailable rows hidden (F-082) with long-press reason | ready · partial (some verbs hidden) · all-hidden (sheet offers pack manager link) | sheet max-height 60%; verbs listed in fixed order Summarize/Rewrite/Continue/Fix |
| OD-AI-003 generation preview | streamed preview card, method label (UX-47), Cancel, Insert/Replace/Discard | generating (streaming, cancel enabled) · done · cancelled (no residue) · error (ladder descent notice, rung-4 offer) | card never covers cursor line; Insert = primary button; Esc/back = Discard with confirm only if text non-empty |

Rules: only one generation at a time (second request cancels the first with a logged D-note); the preview card renders into a fixed-height scroll area (never grows into the toolbar); insertion applies as one grouped op — undo once returns exactly the pre-insert state (UX-06).

## 8.5 Files surfaces (OD-FILE-001 … 003)

| Screen | Purpose | States | Key redlines |
|---|---|---|---|
| OD-FILE-001 versions | snapshot list (kind, time, size), preview (read-only), restore | empty (education line) · list · previewing · restoring (progress ≤ 30 s, UX-07) · restore-confirm (warns current will be snapshotted first) | kind chips color+label (UX-41); restore primary action disabled during preview render |
| OD-FILE-002 import | file pick (SAF) → sniff → preview (fidelity note, UX-45) → open | picking · sniffing · preview-ready · refused (reason, F-056) · too-large warn (> 50 MB) | refusal card names format + missing feature; never imports without preview step |
| OD-FILE-003 export sheet | format list with fidelity badges (§18.2), filename edit, SAF create, progress | ready · writing · done (share/open actions) · failed (reason, UX-18) | fidelity badges same visual system as conversion notes; filename sanitized (no path chars) |

## 8.6 Settings surfaces (OD-SET-001 … 004)

Settings root lists four groups — Appearance (themes §6.3, accent), Editor (font family/size, autosave interval display, spell-check toggle), Files (backup toggle + SAF folder, storage accounting F-064), About/diagnostics (F-089). Rules: every setting persists instantly (no save button anywhere); diagnostics self-test (UX-34) runs the integrity suite (manifest self-check, pack SHAs, journal integrity, storage stats) and finishes with a copyable local report — nothing leaves the device; "About" shows version, commit, and the repo URL as plain text (never link-fetched, §20.2).

## 6.7 Component inventory (the closed set of UI parts)

Every screen composes from exactly these parts — a new custom widget requires a D-nnn entry and this table's update:

| Component | Variants | States | Size contract |
|---|---|---|---|
| Button | filled · tonal · text | enabled · pressed · disabled (rare) | height 40/48 dp; label 15 sp medium |
| Icon button | bare · contained | same + selected (toggled) | 48×48 dp target, 24 dp glyph |
| Chip (filter/assist) | filter · assist · input | unselected · selected · error | height 32 dp; label 14 sp |
| Card (doc card) | standard · compact | default · pressed · selected (multi-select) | min-height 72 dp; radius l |
| List item | one-line · two-line | default · selected · drag-anchor | height 56/72 dp; leading 40 dp slot |
| App bar | standard · editor | default · scrolled (elevation) | height 56 dp (+insets) |
| Toolbar (selection) | horizontal scroll | visible · flipped · expanded (overflow sheet) | height 44 dp; buttons ≥ 44 dp |
| Sheet (modal) | standard · full (editor overflow) | hidden · half · expanded · dragging | radius sheet; grab handle 32×4 dp |
| FAB | single | default · extended (New doc) | 56 dp; bottom-right, above nav |
| Snackbar | action | visible · queued (one at a time) | bottom; 7 s default (trash undo contract) |
| Text field | single · multiline | default · focused · error (helper text) | min-height 48 dp; helper 12 sp |
| Tab row (editor categories) | fixed 4 | selected · unselected · disabled | height 48 dp; indicator 3 dp |
| Dialog | confirm · destructive | — | used only where sheets are too heavy (permanent delete, pack delete) |
| Preview card (AI) | streaming · done | generating · done · cancelled · error | max 60% height; method label line mandatory |

Do/don't (applies to every part): do respect token values only; don't add color outside ramps; do announce state changes to accessibility; don't animate anything over 250 ms; do support text scale 200%; don't introduce a second shadow elevation scale.

## 9.3 Focus-order specification method

Focus order is declared per screen in the registry (`a11y` column) and asserted by the audit (DQ-6). Declaration format: ordered node ids; Wildcard rows (list items) declare the pattern ("cards by recency"). The assertion walks with TalkBack semantics (not just `focusOrder`) on API 33/36: traversal must match visual order in both LTR and RTL, and no actionable node may be unreachable (orphan check). Custom views must register their virtual structure (`virtualViewCount`, child descriptions) — a custom view without a node contract fails review (§17.12).

## 9.4 Live-region and announcement rules

Announcements (polite): insert/restore done, export finished, generation completed, verification results. Never announced: typing echoes ( TalkBack reads composition itself), autosave (silent by law), decorative state. Assertive is reserved for data-safety events: storage-full chip, journal-repair notice. The announce list is enumerated in strings tests like errors are (no ad hoc `announceForAccessibility` in feature code — key-based only).

## 9.5 The design-review checklist (PR template, UI path)

1. Registry row exists; states match; frame named (DQ-3).
2. Tokens only — no literals (DQ-1); sizes per component table (§6.7).
3. Targets ≥ 48/44 dp (DQ-2); primary actions in bottom 40% (UX-42).
4. Contrast per theme verified in snapshot tests (DQ-4); 200% walk clean (DQ-5).
5. Focus order declared + walk clean (DQ-6, W).
6. Motion within budget; reduced-motion honored (DQ-7).
7. Empty/error/loading states implemented per registry (DQ-8).
8. Strings via keys; new strings en+hi+mr (P).
9. Announcements per §9.4 only.
10. Screenshots attached at default and 200% scale.

## 6.8 Theme contrast engineering (how the promise holds per theme)

Body text pairs surface/ink with a maintained luminance-distance contract: each theme defines `surface`, `surfaceAlt`, `ink`, `inkMuted` such that ink/surface ≥ 7:1, inkMuted/surface ≥ 4.5:1, and accent-on-surface ≥ 3:1 at glyph weights used. The snapshot gate (DQ-4) computes WCAG ratios per theme per pair from the *token values* (not screenshots of text) and fails CI on regression — theme additions must extend the table, not eyeball colors. High-contrast themes push to ≥ 10:1/7:1 and forbid inkMuted on action labels (all controls full-ink). Sepia/paper trade blue-light for warmth while keeping the same numeric contract (§21.4 budgets unchanged).

## 8.7 Motion spec per transition (the complete list)

| Transition | Spec |
|---|---|
| sheet enter/exit | 250 ms, slide+fade, radius sheet; exit 200 ms |
| toolbar appear/dismiss | 150 ms fade + 8 dp vertical slide |
| block drag settle | 200 ms; neighbors reflow with 180 ms stagger ≤ 3 items |
| page guide appear | 150 ms fade (compose mode only) |
| FAB → editor | shared-axis nothing: instant editor open (speed > flourish, UX-02) |
| search results stream | 100 ms item fade-in, top-staggered |
| theme change | 250 ms color cross-fade (activity recreation avoided) |
| AI streaming text | no animation (text appears as generated; card frame animates once) |
| reduced motion / battery saver | all of the above → 0 ms except opacity 100 ms |
