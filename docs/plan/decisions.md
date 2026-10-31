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

### D-001 — Resolve contradictory auto-balance example
- Date / phase: 31 Oct 2026 / G1
- Binding sections that could be affected: §7.2.1, §17.1.4, §20.6, Appendix B B-15
- Options considered: a) return `25` for `(2+3` as repeated in the examples; b) close the unmatched parenthesis and return the arithmetic result `5`.
- Decision: b) implement normal auto-balancing: `(2+3` becomes `(2+3)` and evaluates to `5`. The spec's repeated expected value `25` contradicts the grammar and its stated meaning (“auto-balance”). This discrepancy is flagged for owner clarification; no expression-specific special case is added.
- Consequence / revisit-if: adjust the calculator if the owner confirms an intentional nonstandard rule.

*(Future decisions are appended; never rewrite prior entries.)*
