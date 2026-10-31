# OneDoc × Figma — contract (blueprint §7)

**Repo-first, one-way sync.** `design/onedoc-figma/tokens.json` is the single source of truth for every color, size, radius, spacing and duration. The Figma file **"OneDoc Design System"** mirrors it: page *Foundations* publishes styles named `od/<group>/<step>` from these tokens; page *Screens* holds one frame per row of the screen registry.

## File structure

| Figma page | Contents | Mirror of |
|---|---|---|
| Foundations | color/text/effect/grid styles + core components (buttons, chips, cards, toolbar, sheet, list item, FAB, app bar) | `tokens.json` |
| Screens | frames named `OD-<AREA>-<nnn> <name>`, sectioned by area; every registry `states` entry exists as a variant | `docs/onedoc/blueprint/ui-screens.csv` |

## How the agent uses it (no account required)

1. Build from `ui-screens.csv` (screen id, frame, entry, exit, states, redline) + `tokens.json` (values). The CSV is complete for v1.0 — Figma access is never a blocker.
2. Frame naming is the join key: `OD-EDIT-002` in Figma ⇄ registry row ⇄ `odEdit002` in code.
3. Optional owner token (repo secret `FIGMA_TOKEN`) enables a nightly registry-drift check (list frames vs CSV). Without it, DQ-3 at the design-QA gate (§9.2) catches drift on merge.
4. Owner edits flow back as `design: <frame-or-token>` PRs; the DQ-1…DQ-8 checklist gates every UI change.

## Registry

`docs/onedoc/blueprint/ui-screens.csv` — one row per screen: `screen_id, name, figma_frame, area, entry, exit, states, redline, test_ids`. Regenerated with the blueprint; hand-edits forbidden.
