# MySpace One — Figma mirror (design ↔ code)

The Figma file **mirrors** this repository; the repository is the law
(see blueprint §6.13). This README is the linking registry required by
the docs-drift gate.

## File
- File name: `MySpace One DS`
- File key: `(owner fills in — paste the Figma file key here)`
- Variables source: generated from `tools/tokens-export.py`
  (`tokens.csv` → `tokens.figma.json`, Tokens-Studio compatible).

## Page map
| Figma page | Contents | Blueprint anchor |
|---|---|---|
| 00 Foundations | color/type/effect/grid styles, Variables (Light/Dark) | §6.2, §6.7 |
| 01 Components | `DS/*` component library + variants | §6.4, §6.8 |
| 02 Hub … 09 Diagnostics | screens × states, light+dark | §6.14 registry |
| 10 Prototype flows | J-01…J-10 prototypes | §9.12, Appendix R |
| 11 Archive | deprecated frames (never deleted) | ledger |

## Rules
1. One-way sync: repo → Figma. Figma-only visual changes are invalid;
   they ride a `tokens.csv` / component PR.
2. Frame names follow `<MODULE>-<nnn> <Screen> <State>` and are registered
   in `docs/blueprint/ui-screens.csv` (generated from §6.14).
3. Component descriptions carry the code anchor (`core/designsystem/…`)
   and the binding blueprint § refs.
4. Prototype step names equal harness step names (J-01…J-10).
5. Agent access: read-only token optional (§6.13 policy). No token →
   the blueprint alone is the source of truth; it is complete by design.
