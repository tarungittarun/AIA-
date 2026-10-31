@PART: PART II — EXPERIENCE DESIGN
@PARTDESC: The product as a person will meet it: principles, navigation, the shared design system, and the complete module-by-module interaction specification. Wireframes here are normative for structure and behavior; visual styling is normative only through the tokens of Chapter 6.

Design is where combined apps usually fail: eight tools duct-taped into one binary feel like eight apps in a trench coat. This part prevents that by defining one set of principles, one navigation model, one design system, and then specifying every screen so that no module invents its own patterns.

# Chapter 4 — Experience principles

## 4.1 The eight principles

| # | Principle | Meaning in practice | Testable consequence |
|---|---|---|---|
| X1 | **Two taps to anything** | From cold start, every module screen is reachable in ≤ 2 taps | Nav audit test TC-NAV-001 |
| X2 | **Thumb-first** | Primary actions live in the bottom third; keypads and FABs are ≥ 48 dp targets | A11y + touch-target checks TC-A11Y-002 |
| X3 | **One visual language** | Color, type, elevation and motion come only from tokens (§6.2); no module-local palettes | Screenshot diff + lint rule against hardcoded colors |
| X4 | **Content over chrome** | Bars and borders shrink; content (expression, note text, waveform) is the screen | Design review checklist §18.4 |
| X5 | **Forgiving everywhere** | Undo before confirm; selection before action; destructive actions are always reversible or trash-ed for 30 days | TC-UX-undo-* cases |
| X6 | **Offline is invisible** | No offline banners, no retry buttons, no sync spinners — there is nothing to be online *to* | Copy audit: strings catalog contains no network vocabulary |
| X7 | **AI is an accelerant, never a gate** | Every AI affordance has a manual equivalent; AI absence changes speed, not capability | TC-AI-fallback-* cases |
| X8 | **Respect the system** | Theme, font scale, reduced-motion, locale and ringer follow OS settings instantly | TC-SYS-* cases |

## 4.2 Emotional design goals

The app should feel like a well-made pocket tool: quiet, precise, dependable. Concretely: animations run 150–250 ms with standard easing and are disabled under system reduced-motion; haptics are subtle and configurable (a "Haptics: On" toggle in calculator settings exists because the owner's reference devices expose it); empty states teach with one sentence and one action, never marketing copy; error messages say what happened, what it means for the data (never "your data may be lost" unless true), and one recovery step.

## 4.3 What the experience must never do

- Never show a spinner on a local operation that completes in < 100 ms; skeleton loaders are reserved for large indexes (first Files scan, first library import).
- Never interrupt with a dialog except for: record-confirmation privacy notice (first mic use), uninstall-risk warning on encrypted backup, and genuine irreversibility (e.g., emptying trash).
- Never ask for a permission at launch; permissions are requested at the moment of first use, with a one-line reason (§14.7).
- Never autoplay sound (music resumes only by explicit play; recorder previews are muted until tapped).

## 4.4 Principle conflict resolution (worked cases)

1. *X1 (two taps) vs X8 (respect system)*: predictive back may add a system animation — allowed; it does not add taps.
2. *X5 (forgiving) vs storage cost*: undo/trash retained 30 days then purged — forgiveness is time-boxed, disclosed at delete.
3. *X7 (AI optional) vs convenience*: semantic search silently downgrades to FTS — convenience loses; capability parity wins.
4. *X3 (one language) vs calculator themes*: themes are token sets, not bespoke styling — theming stays inside the system.
5. *P4 (fast) vs features*: effects default None on Tier C — features stay, cost defaults to zero.

# Chapter 5 — Information architecture and navigation

## 5.1 The hub model

MySpace One is a **hub** with eight module spokes plus Settings. The hub is a real screen with its own value (search, continue-where-you-left, pinned items), not a launcher of icons. The calculator-only flavor (`mycalc`) replaces the hub with the calculator as home and hides all other spokes — same codebase, flavor-selected navigation graph (§23.4).

![Combined-app product map: eight modules around one hub, one shared on-device AI layer.](figures/fig-module-map.png)

## 5.2 Navigation graph

![Normative navigation graph: hub, modules, settings, and the MyCalc flavor entry.](figures/fig-navigation.png)

Navigation rules:

1. Back always pops the back stack; the system back gesture and the in-app back are equivalent. The hub is the root; back from hub backgrounds the app (standard behavior).
2. State survives process death: every screen's scroll position, selection, draft note text and calculator expression are saved via `SavedStateHandle` + DataStore within 500 ms of change (§12.6).
3. Deep links are internal only (`myspace://note/42`) for in-app navigation and shortcuts; there is no `https://` app-link surface because there is no web.
4. Long-press on a hub module icon offers a shortcut to that module's primary action (new note, new recording, scan, open calculator) — implemented as app shortcuts, which work offline.

## 5.3 Hub screen specification

The hub contains, top to bottom:

1. **Search field** — one query across everything: notes (FTS + semantic when the pack is installed), scans (OCR text), events, files, songs, recordings, transcripts, and calculator history. Results are grouped by module with module-accent icons; opening a result deep-links into the module screen. (The field lives on the hub only — rule X1 keeps module reachability through the grid, not duplicated search bars.)
2. **Continue row**: the last-open module with its state thumbnail ("Draft — Field survey notes", "Recording 00:41 paused").
3. **Module grid**: eight cells, fixed order (Calculator, Notes, Scanner, Calendar, Files, Music, Recorder, Diagnostics), each with name + one-line status ("2 events today", "62% free", "3 new scans").
4. **Pinned strip**: user-pinned notes/events/playlists as horizontal cards.
5. Bottom: **Settings** gear (also in overflow) and a **New** quick-fab whose target follows the last-used module.

Empty-first-run: the hub shows a single card "Everything works offline. Start with Calculator, or import music and files from your storage." plus a one-time (dismissable) privacy card: "MySpace One has no internet permission. Nothing you do here leaves this phone."

## 5.4 Cross-module object flows

These flows are specified as first-class user journeys (J-nnn, §9) and tested end-to-end:

- Scanner → Notes (OCR text becomes note body or attachment).
- Recorder → Notes (transcript/summary appended as a linked note).
- Calculator → anywhere (copy result; share sheet via system, works offline).
- Calendar ↔ Files (ICS import/export).
- Notes ↔ Files (attach, export, backup).
- Music ↔ Files (folder import, playlist export M3U).
- Diagnostics → Files (log bundle export, user-initiated only).

## 5.5 Hub search behavior detail

- **Debounce & budgets**: 120 ms keystroke debounce; per-source budget 25 ms to first page; total first paint ≤ 120 ms on 10k-note corpus (budget §23.6); results stream in as sources complete (fixed module order preserved).
- **Matching**: FTS with prefix matching on the last token (`calc` matches `calculator`); FTS query sanitized (quotes escaped, operators stripped); file/song/artist matches are substring-insensitive casefold; event matches on title+note; recordings match on filename + transcript when present; calculator history matches expression prefix and result string.
- **Ranking**: within a module — exact > prefix > substring > fuzzy (FTS rank for notes); across modules the fixed order (Notes, Events, Files, Scans, Music, Recordings, Calculator) with per-module result caps (5, expandable "See all in Notes").
- **Zero-state**: recent searches (10, DataStore, clearable) and per-module quick links; no network suggestions ever.
- **Semantic (pack)**: cosine top-50 merged per §12.5; tagged "related" visually distinct from exact matches; disabled silently at Tier C battery saver with a provenance row in Diagnostics (§16.7).
- **A11y**: results are an announceable list; opening a result announces the module context first.

## 5.6 Hub region inventory (normative rows)

| # | Region | Content | Behavior |
|---|---|---|---|
| R1 | Status bar blend | system | edge-to-edge, scrim-free (surface color) |
| R2 | Greeting row | "Good morning" + date; tap = nothing (decorative but labeled) | changes by clock; announces date via a11y |
| R3 | Search field | hint + mic (pack) | §5.5 behaviors; focus ring token |
| R4 | Continue row | last module card: icon, name, state line | tap resumes exactly; long-press clears entry |
| R5 | Module grid | 8 cells, 2×4 phone / 1×8+ tablet | cell = icon, name, status line; ripple token |
| R6 | Pinned strip | horizontal cards (notes/events/playlists) | hidden when nothing pinned |
| R7 | New FAB | target = last-used module's create action | long-press = action menu across modules |
| R8 | Bottom bar | none (design choice: no bottom nav — grid is home) | — |
| R9 | Overflow | Settings, About | top-right kebab |
| R10 | First-run layer | privacy + start cards | dismiss persists (F-046) |

## 5.7 Ranking worked examples (fixtures mirrored in TC-HUB-006)

| Query | Corpus state | Expected order (top 5) |
|---|---|---|
| `rent` | note "Rent reminder 27th", event "Rent", file `rent-agreement.pdf`, song "Rent song" | event (exact title, sooner date), note (title exact), file (name), song (exact but Music rank lower), — |
| `1,23,456` | history has `3+123456 = 1,23,459` and note with `123456` | calculator history card first (exact result match), then note |
| `invoice` | scan OCR text contains "INVOICE #118"; file `invoice-118.png` | scan (OCR match), file |
| `laptop advice` | note "Purchase guidance for computing" (semantic pack on) | FTS empty → semantic hit tagged "related" |
| `rec` | recording "REC-2026-10-27", note "recording ideas" | note (prefix title), recording (filename) |

## 5.8 Continue-row state line catalogue

| Last module | State line format | Example |
|---|---|---|
| Calculator | `Expression "3+4×2" · caret 5` | resumes exactly incl. selection |
| Notes | `Draft — <title or "Untitled">` | cursor position restored |
| Scanner | `<n> pages in review` | review reopened |
| Calendar | `Viewing <month>` / `Editing <event>` | screen + selection |
| Files | `<folder> · <selection?>` | path + selection |
| Music | `<track> · <position>` | miniplayer state |
| Recorder | `Recording 00:12` / `Review <name>` | FGS state honest |
| Diagnostics/Settings | last subpage | — |

# Chapter 6 — Design system

## 6.1 System overview

The design system is a Gradle module `core/designsystem` containing tokens, theme, typography, components, motion specs, and icon set. Modules depend on it and on nothing visual else. Every reusable component ships with Roborazzi screenshot tests (§20.4) and an accessibility smoke test.

## 6.2 Design tokens

Tokens are Kotlin constants generated from a single source table (checked in as `designsystem/tokens.csv`), so documentation, code and tests share one truth. Core palette (light / dark):

| Token | Light | Dark | Used for |
|---|---|---|---|
| `color/background` | `#FAFBFC` | `#0B1220` | Screen background |
| `color/surface` | `#FFFFFF` | `#111C2E` | Cards, sheets |
| `color/onSurface` | `#0F172A` | `#E4EAF2` | Primary text |
| `color/onSurfaceMuted` | `#5B6B7E` | `#94A3B8` | Secondary text |
| `color/primary` | `#0F766E` | `#2DD4BF` | Bars, FAB, selection, live accents |
| `color/onPrimary` | `#FFFFFF` | `#062F2C` | Text on primary |
| `color/liveAnswer` | `#B45309` | `#FBBF24` | Calculator live answer (LED-amber in dark) |
| `color/equalsKey` | `#FDE68A` | `#FBBF24` | The `=` key |
| `color/danger` | `#BE123C` | `#FDA4AF` | Delete confirm, destructive |
| `color/caret` | `#0F172A` | `#FFFFFF` | Expression caret (exact 2 dp bar) |
| `shape/keyRadius` | 16 dp | 16 dp | Keypad keys, key shape options override |
| `elevation/sheet` | 8 dp | 8 dp | History/memory/effects sheets |
| `motion/standard` | 200 ms | 200 ms | Enter/exit, 150 ms for taps |
| `type/display` | 34/40 `SemiBold` | same | Calculator result |
| `type/body` | 15/22 `Regular` | same | Note bodies |
| `space/unit` | 4 dp grid | — | All spacing multiples |

Calculator-specific theming goes beyond global tokens: **Key theme** (eight options — `MySpace settings` (follows app theme), `Graphite`, `Ocean`, `Sunset`, `Mint`, `Rose`, `Lemon`, `Iris`) and **Key shape** (`Circle`, `Squircle`, `Pill`, `Rounded square`, `No shape`) are user settings (§17.7); switching re-resolves colors immediately with a 200 ms crossfade (guide behavior H4). A theme change must produce a measurable pixel difference on the keypad region (the owner's acceptance harness used a ≥ 10% region-diff threshold; we adopt the same, TC-ONE-C-023).

## 6.3 Typography and iconography

Font: **Roboto Flex** (variable) bundled in the APK; monospace contexts (expression field, file paths, logs) use **JetBrains Mono**. Sizes scale with `fontScale` up to 2.0; keypads are exempt from scaling beyond 1.3 (keys would overflow) but compensate with larger touch targets. Icons: Material Symbols Outlined, subset by R8; module accent glyphs are simple, two-tone; the launcher icon is a teal honeycomb hex with a subtle calculator glyph (cover art motif), provided in all densities + adaptive-icon layers.

## 6.4 Components inventory

The system ships these shared components (each with screenshot tests):

- `AppTopBar` (title, overflow, optional bottom-progress), `BottomSheet` (drag-handle, snap points, back-gesture aware), `Fab`, `EmptyState(icon, title, hint, action)`, `ErrorState(retry-less: message + action)`, `SearchField`, `ResultRow`, `KeyPad` + `CalcKey` (theme/shape aware), `ExpressionField` (caret + live answer, §7.2), `SelectionPill` (Cut/Copy/MAdd/MUse/Paste), `Waveform` (recorder), `MiniPlayer`, `CalendarMonthGrid`, `FileRow`, `StorageDonut`, `ConfirmSheet` (for destructive), `AiActionRow` (ornamented, always secondary-styled), `Toast` replacement (in-app snackbar with action, never system toast from background threads — a past lesson from the owner's harness: toasts crashing background instrumentation threads, §15.8 note).

## 6.5 Motion

Standard: enter = fade+8 dp slide up 200 ms; exit = fade 150 ms; sheet = slide from bottom 250 ms with 0.8 overshoot damping; keypad press = scale 0.97 on down, 120 ms; theme change = crossfade 200 ms; calculator result change = none (instant; results never animate — the number is the UI). All motion respects `Settings.Global.ANIMATOR_DURATION_SCALE` and removes entirely under reduced-motion.

| Interaction | Spec |
|---|---|
| Screen enter | fade + 8 dp slide-up, 200 ms, standard easing |
| Screen exit | fade 150 ms |
| Sheet enter/exit | 250 ms slide, overshoot damping 0.8 |
| Key press | scale 0.97 on down; release 120 ms |
| Selection pill | 150 ms scale-in at press point, shadow settle |
| Live answer change | none (instant) |
| Result on `=` | instant swap + effects (optional) |
| Theme change | 200 ms crossfade, no layout shift |
| FAB extend/retract | 200 ms width morph |
| List reorder (queue/memory) | 180 ms settle, lift shadow 8 dp |
| All motion | killed under reduced-motion or animator scale 0 |

## 6.6 Accessibility contract (system-wide)

1. Every interactive element ≥ 48×48 dp; keypad keys ≥ 44×44 dp visual with 48 dp touch bounds.
2. Content descriptions on all icons; decorative images excluded from the a11y tree.
3. TalkBack announces calculator keys as their action ("7", "plus", "equals"); the expression field announces full expression + caret context ("3 plus 4, caret after 4, live answer 7").
4. Contrast: text ≥ 4.5:1, large text ≥ 3:1, key glyphs ≥ 3:1 against their key fill — verified per key theme in a token unit test (no screenshot needed).
5. Touch exploration: no gesture-only features; every gesture has a visible control twin (e.g., history swipe-down ↔ history button).
6. Focus order is logical (top-to-bottom, left-to-right); dialogs trap focus and restore on dismiss.

## 6.7 Type scale and spacing tokens (complete)

| Token | Value | Used for |
|---|---|---|
| `type/displayMono` | 30/36 JetBrainsMono SemiBold | Calculator expression |
| `type/display` | 34/40 SemiBold | Calculator result/history result |
| `type/titleL` | 22/28 SemiBold | Screen titles |
| `type/titleM` | 18/24 SemiBold | Sheet titles, card titles |
| `type/titleS` | 15/20 Medium | List row titles |
| `type/body` | 15/22 Regular | Note body, prose |
| `type/bodyS` | 13/18 Regular | Secondary rows, chips |
| `type/caption` | 11/14 Regular | Timestamps, provenance footnotes |
| `type/key` | 22/24 Medium (caps at 1.3× scale) | Keypad glyphs |
| `space/xs` | 4 dp | Icon-to-label, chip padding |
| `space/s` | 8 dp | intra-group |
| `space/m` | 12 dp | list gutters |
| `space/l` | 16 dp | screen margins |
| `space/xl` | 24 dp | section separation |
| `space/sheet` | 20 dp | sheet horizontal padding |
| `radius/s` | 8 dp | chips, small cards |
| `radius/m` | 16 dp | cards, keys |
| `radius/l` | 24 dp | sheets |
| `elevation/1..3` | 1/4/8 dp | card/bar/sheet |

Every token exists in code as a named constant; a unit test asserts the Kotlin token table matches `tokens.csv` (TC-SYS-tokens), and screenshots reference tokens only — a hardcoded `Color(0x…)` in feature modules is a detekt error (§18.1).

## 6.8 Component behavior specifications (normative digest)

| Component | Props/variants | States | Rules |
|---|---|---|---|
| `AppTopBar` | title, nav icon, actions[], large bool | default/scrolled (elevation 4 dp) | title truncates with ellipsis at 1 line; overflow = max 6 items + "More" |
| `BottomSheet` | snapPoints, dismissable | expanding/settled/dragging | drag handle 32×4 dp; back gesture dismisses; content scrollable; scrim 40% |
| `Fab` | icon, text? | normal/extended | 56 dp (extended 56 h, min 120 w); never overlaps content scroll edge without inset handling |
| `EmptyState` | icon, title, hint, action | — | icon muted 40%; action is the only colored element |
| `ErrorState` | title, detail, action | — | no retry if retry cannot succeed (policy errors → action = "Open Diagnostics") |
| `SearchField` | hint, query, onQuery | empty/filled/active | clear ("×") appears when non-empty; mic entry only when Speech pack installed |
| `KeyPad` | pad(basic/sci), theme, shape | — | keys 48 dp min touch; haptic hook; press scale 0.97/120 ms; equals emphasized |
| `ExpressionField` | expr, caret, liveAnswer, selection | empty/text/selection/caret-menu | caret 2 dp × line-height; selection highlight token; pill positioned above field when room else below; autoscroll keeps caret visible |
| `SelectionPill` | actions[] | shown/dismissed | shadow 8 dp; never covers selection; announced as menu with item count |
| `Waveform` | amplitudes, playing | idle/recording/paused | 20 fps max; paused freezes + dims 40% |
| `MiniPlayer` | track, playing, progress | collapsed/expanded | 64 dp; tap opens player; swipe-down hides for session |
| `ConfirmSheet` | title, detail, confirmLabel, danger | — | destructive confirm is danger-colored and never the initial focus |
| `AiActionRow` | actions[] | ready/running/disabled(missing pack) | running shows cancel; disabled shows reason inline |
| `StorageDonut` | segments[] | — | max 6 segments; center label = free %; a11y = textual summary |
| `CalendarMonthGrid` | month, selected, dots | — | 7-col grid; week starts per locale; today token-filled circle |

## 6.9 Key-theme palettes (normative values)

Each theme defines key fill / key glyph / operator-key fill / function-key fill for light and dark; `MySpace settings` follows the app theme using core tokens. Contrast pairs are validated programmatically (TC-A11Y-contrast-01). Values are sRGB hex.

| Theme | Mode | Key fill | Glyph | Operator key | Function key |
|---|---|---|---|---|---|
| Graphite | light | `#F1F3F5` | `#212529` | `#E3E6E8` | `#E9EBED` |
| Graphite | dark | `#2B2F33` | `#E8EAED` | `#343A3F` | `#303539` |
| Ocean | light | `#E7F0FA` | `#0B3D66` | `#D2E4F5` | `#DCEAF7` |
| Ocean | dark | `#16324A` | `#D6E9FA` | `#1B3D5A` | `#193855` |
| Sunset | light | `#FDEEE2` | `#7A2E0C` | `#F9DFC8` | `#FBE6D6` |
| Sunset | dark | `#4A2413` | `#FFE3CC` | `#542A15` | `#4F2713` |
| Mint | light | `#E6F6EF` | `#0B5137` | `#D2EFE1` | `#DCF3E8` |
| Mint | dark | `#14402E` | `#D8F3E6` | `#194A36` | `#174532` |
| Rose | light | `#FDE9EE` | `#831843` | `#F9D4DD` | `#FBDDE5` |
| Rose | dark | `#4C1D33` | `#FBD5E0` | `#57223A` | `#521F36` |
| Lemon | light | `#FBF3D9` | `#6B5509` | `#F6E9BC` | `#F9EECB` |
| Lemon | dark | `#423A12` | `#FBF0C4` | `#4A4116` | `#453D14` |
| Iris | light | `#EFEAFB` | `#3D2B7D` | `#E2D9F7` | `#E8E1F9` |
| Iris | dark | `#2E2354` | `#E6DEF9` | `#352A60` | `#312658` |

`=` key always renders `equalsKey` amber token in every theme (recognizability over theming); theme change applies without recreating the pad (Compose recomposition only, crossfade §6.5).

## 6.10 Key shapes (normative geometry)

| Shape | Corner radius | Notes |
|---|---|---|
| Circle | height/2 (fully round) | glyph centered; touch bounds stay rectangular |
| Squircle | 40% superellipse | default-adjacent smooth |
| Pill | 100 dp x-radius | wide operator keys look capsule |
| Rounded square | 16 dp | default |
| No shape | 0 dp | sharp; grid lines 1 dp token border for definition |

## 6.11 Illustration and empty-state art style

Empty states use one 2 dp-stroke line illustration (48–64 dp) drawn with tokens only: the motif is the honeycomb hex — calculator shows a hex with `1+2`, notes a hex with a folded corner, scanner hex corners, calendar a hex ring, files hex stack, music a hex note, recorder a hex wave, diagnostics a hex pulse. No mascots, no gradients, no stock art — the icon set stays inside the vector budget (≤ 40 KB total). Illustrations ship in the design-system module with their own goldens.

Design is where combined apps usually fail: eight tools duct-taped into one binary feel like eight apps in a trench coat. This part prevents that by defining one set of principles, one navigation model, one design system, and then specifying every screen so that no module invents its own patterns.
