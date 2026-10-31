# Decision ledger — MySpace One (append-only, §15.7)

Rules:
1. Every choice **not dictated by the blueprint** gets an entry here before the code lands.
2. Entries are never edited or deleted; revisiting a decision = a new entry that supersedes it.
3. Each entry names the blueprint sections it *could* have affected.
4. The G7 review walks this file top to bottom — it is how the owner audits an autonomous build.

Entry format:

```markdown
### D-<n> — <question>
- Date / phase:
- Binding sections that could be affected: §…
- Options considered: a) … b) …
- Decision:
- Consequence / revisit-if:
```

---

### D-000 — EXAMPLE ENTRY (format illustration only — do not count as a decision)
- Date / phase: 31 Oct 2026 / draft
- Binding sections that could be affected: §23.5
- Options considered: a) add library X now b) wait for G1 catalog freeze
- Decision: b) wait
- Consequence / revisit-if: revisit only if a G1 task is blocked without X

---

*(No live decisions yet. First entries expected during G1 — e.g., exact CI runner image
pins, wrapper version confirmation against §23.1, any tool the sandbox lacks.)*
