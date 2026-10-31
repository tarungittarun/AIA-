# Appendix P — Strings dictionary (normative, en; hi/mr mirror keys)

Rules: sentence case; no exclamation marks; no emoji; "document" not "file" for user content; numbers humanized; every string is a key in `core/designsystem/strings.csv` — feature code references keys, never literals (lint-enforced; TC-SET-004).

## P.1 Core actions

| Key | String |
|---|---|
| action.new.doc | New document |
| action.save.version | Save version |
| action.export | Export |
| action.share | Share |
| action.rename | Rename |
| action.duplicate | Duplicate |
| action.star / action.unstar | Star / Unstar |
| action.move.trash | Move to trash |
| action.restore | Restore |
| action.delete.forever | Delete forever |
| action.undo / action.redo | Undo / Redo |
| action.find.replace | Find and replace |
| action.save.template | Save as template |
| action.print | Print |

## P.2 Editor

| Key | String |
|---|---|
| editor.tab.text / insert / ai / format | Text · Insert · AI · Format |
| editor.count | {words} words · {chars} characters |
| editor.find.count | {n} of {total} |
| editor.replace.all.confirm | Replace {n} matches? A version is saved first. |
| editor.link.hint | Paste or type a link |
| editor.image.alt.hint | Describe this image (helps screen readers) |
| editor.composing.protected | — (no string: composition is silent, L5) |

## P.3 AI surfaces

| Key | String |
|---|---|
| ai.summarize / rewrite / continue / fix | Summarize · Rewrite · Continue writing · Fix grammar |
| ai.method.llm | On-device gemma-2B |
| ai.method.extractive | On-device extractive summary |
| ai.method.system | Android speech service |
| ai.insert / discard / replace | Insert · Discard · Replace |
| ai.cancel | Stop |
| ai.unavailable.pack | Needs the {pack} pack — install it from Assistant. |
| ai.unavailable.ram | {model} needs {need} GB RAM — this device has {have}. |
| ai.unavailable.tier | {feature} needs a stronger phone than this one. |
| ai.descended | Switched to the lighter on-device method (thermal). |
| pack.install | Install pack |
| pack.verify.fail | Verification failed. Expected {expected}, found {found}. |
| pack.license | License: {spdx} |

## P.4 Files and errors (canonical §18.8 set + these)

| Key | String |
|---|---|
| export.pdf / odoc / md / txt / html / docx | Export as PDF / OneDoc / Markdown / Text / HTML / Word |
| fidelity.F0/F1/F2/F3 | Not supported / Best effort / Subset lossless / Lossless |
| import.refused.{reason} | per taxonomy §18.8 |
| trash.retention | Deleted documents are kept 30 days. {days} left. |
| version.auto/manual/pre_edit | Auto · Manual · Before change |
| restore.done | Restored. Your previous text is saved as a version. |
| backup.prompt.pass | Set a passphrase to encrypt your backup |

## P.5 First run and about

| Key | String |
|---|---|
| welcome.title | Your words, your phone. |
| welcome.body | OneDoc works fully offline. No account, no ads, no tracking. |
| welcome.cta | Start writing |
| about.selftest | Run self-test |
| about.selftest.done | All checks passed ({n}) in {s} s |
| about.storage | Documents {docs} · Versions {ver} · Packs {packs} |

(Complete key list ships as CSV; this appendix pins voice and the strings that gate-acceptance reads aloud.)
