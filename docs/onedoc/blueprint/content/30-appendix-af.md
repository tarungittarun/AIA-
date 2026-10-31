# Appendix AF — Complete en strings deck (v1.0, 110 keys)

The canonical table; `core/designsystem/strings.csv` is generated from it (and from the hi/mr deck, Appendix AD). Lint: feature code references keys only.

| Key | en |
|---|---|
| action.new.doc | New document |
| action.save.version | Save version |
| action.export | Export |
| action.share | Share |
| action.rename | Rename |
| action.duplicate | Duplicate |
| action.star | Star |
| action.unstar | Unstar |
| action.move.trash | Move to trash |
| action.restore | Restore |
| action.delete.forever | Delete forever |
| action.undo | Undo |
| action.redo | Redo |
| action.find.replace | Find and replace |
| action.insert | Insert |
| action.print | Print |
| action.save.template | Save as template |
| action.select.all | Select all |
| action.clear.marks | Clear formatting |
| editor.tab.text | Text |
| editor.tab.insert | Insert |
| editor.tab.ai | AI |
| editor.tab.format | Format |
| editor.count | {words} words · {chars} characters |
| editor.find.hint | Find in document |
| editor.find.count | {n} of {total} |
| editor.replace.hint | Replace with |
| editor.replace.all.confirm | Replace {n} matches? A version is saved first. |
| editor.link.hint | Paste or type a link |
| editor.image.alt.hint | Describe this image (helps screen readers) |
| editor.image.alt.skip | Skip for now |
| editor.composing.protected |  |
| ai.summarize | Summarize |
| ai.rewrite | Rewrite |
| ai.continue | Continue writing |
| ai.fix | Fix grammar |
| ai.rewrite.polish | Polish |
| ai.rewrite.formal | Formal |
| ai.rewrite.casual | Casual |
| ai.method.llm | On-device gemma-2B |
| ai.method.extractive | On-device extractive summary |
| ai.method.system | Android speech service |
| ai.insert | Insert |
| ai.discard | Discard |
| ai.replace | Replace |
| ai.cancel | Stop |
| ai.unavailable.pack | Needs the {pack} pack — install it from Assistant. |
| ai.unavailable.ram | {model} needs {need} GB RAM — this device has {have}. |
| ai.unavailable.tier | {feature} needs a stronger phone than this one. |
| ai.unavailable.tts | No speech service on this device. |
| ai.descended | Switched to the lighter on-device method (thermal). |
| ai.timed.out | That took too long. Try the lighter method? |
| pack.install | Install pack |
| pack.delete | Delete pack |
| pack.verify.fail | Verification failed. Expected {expected}, found {found}. |
| pack.license | License: {spdx} |
| pack.tier.req | Needs a Tier {tier} device (this is Tier {have}). |
| export.pdf | Export as PDF |
| export.odoc | Export as OneDoc (.odoc) |
| export.md | Export as Markdown |
| export.txt | Export as text |
| export.html | Export as HTML |
| export.docx | Export as Word (.docx) |
| fidelity.F0 | Not supported |
| fidelity.F1 | Best effort |
| fidelity.F2 | Subset lossless |
| fidelity.F3 | Lossless |
| import.refused.format | {fmt} isn't supported. Supported: odoc, md, txt, html, docx. |
| import.refused.corrupt | This file is damaged ({why}). OneDoc won't risk opening it. |
| import.refused.size | That file is over 50 MB — too big for a phone to convert safely. |
| import.refused.binary | That looks like a binary file, not a document. |
| import.note.prefix | Imported as {fmt} — {level}. |
| export.denied.folder | OneDoc can't write to that folder. Pick a different location. |
| export.retrying | Writing was interrupted. Retrying… |
| err.disk.full | Storage is full. Free some space — OneDoc will retry. |
| err.storage.retry | Storage hiccup. Retrying… |
| err.doc.repair | This document needed a small repair. Your text is safe. |
| err.doc.newer | This document was made by a newer OneDoc. |
| err.something.broke | Something went wrong. Your text is safe. |
| err.upgrade.repair | Finishing an update to your library… |
| trash.retention | Deleted documents are kept 30 days. {days} left. |
| version.auto | Auto |
| version.manual | Manual |
| version.pre_edit | Before change |
| restore.done | Restored. Your previous text is saved as a version. |
| backup.prompt.pass | Set a passphrase to encrypt your backup |
| backup.enabled | Weekly encrypted backup |
| storage.usage | Documents {docs} · Versions {ver} · Packs {packs} |
| perm.mic.why | OneDoc uses the microphone only while you dictate. Nothing is saved or sent. |
| perm.camera.why | OneDoc uses the camera only to scan pages into text. |
| welcome.title | Your words, your phone. |
| welcome.body | OneDoc works fully offline. No account, no ads, no tracking. |
| welcome.cta | Start writing |
| about.selftest | Run self-test |
| about.selftest.done | All checks passed ({n}) in {s} s |
| about.version | Version {name} ({code}) · build {sha} |
| about.repo | Source: github.com/tarungittarun/AIA- |
| announce.export.done | Export finished |
| announce.restore.done | Restore finished |
| announce.gen.done | Assistant finished |
| announce.verify.done | Pack verification finished |
| hc.storage.full | Storage almost full — OneDoc is keeping your text in memory. |
| hc.journal.repair | OneDoc repaired this document after an interruption. Details in Diagnostics. |
| scan.no.pack | OCR needs the ocr-en pack. For now you can save the page image. |
| scan.low.yield | Not much text found. Retake with better light? |
| search.related | Related |
| search.results.hint | Search documents |
| tpl.use | Use template |
| tpl.save.as | Saved to your templates |
| img.deleted.used | This image is used. Delete it from the page first. |

# Appendix AI — Post-release 30/60/90 sketch (owner-facing, not scheduled work)

**Day 30:** first maintenance release candidate if tracker holds S2+ fixes; locale deck review with owner; battery/thermal field data from owner's device (diagnostics export, manual share).
**Day 60:** v1.1 shelf review — D-R102/103/104 graduate by owner decision or wait; pack ecosystem check (any pack format drift from runtime updates).
**Day 90:** dependency refresh audit (pinned bumps, deny-list re-run, SBOM diff), full-matrix re-run on the current release artifact (proof the promise still holds on a stale binary — the strongest offline claim OneDoc can make).
