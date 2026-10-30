# Appendix E — UX microcopy dictionary (normative strings v1, en-IN)

Copy rules: sentence case; no exclamation marks; no emoji; "phone" not "device" in user copy; numbers humanized. The strings table below is generated into `core/designsystem/strings.csv`; a lint test asserts feature code references keys, never literals (TC-SYS-strings).

| Key | String |
|---|---|
| hub.firstRun.privacy.title | Your data stays on this phone |
| hub.firstRun.privacy.body | MySpace One has no internet permission. Nothing you do here leaves this phone. |
| hub.firstRun.start.body | Everything works offline. Start with Calculator, or import music and files from your storage. |
| hub.search.hint | Search notes, scans, events, files, music… |
| hub.recovered | Recovered — tap to reopen |
| calc.history.empty | Solved calculations appear here. |
| calc.history.clear.confirm | Clear history? Pinned cards are kept. |
| calc.memory.empty | Memory is empty. Select a number and tap MAdd. |
| calc.err.divideByZero | Cannot divide by zero |
| calc.err.domain | Outside domain (e.g., log of a negative number) |
| calc.err.syntax | Can't calculate this yet — check the highlighted part |
| calc.err.tooLong | Expression is too long |
| calc.err.overflow | Result is too large to display |
| notes.empty | Notes you write are saved on this phone automatically. |
| notes.trash.snackbar | Note moved to trash |
| notes.trash.undo | Undo |
| notes.trash.empty.confirm | Empty trash now? Items are deleted permanently. |
| notes.ai.missing | Install the Essentials pack in Diagnostics to use AI actions. |
| notes.ai.running | Working… |
| notes.ai.applied | AI result applied — Undo restores your original text |
| scan.ocr.missing | OCR needs the Essentials pack. Capture and export still work. |
| scan.import.title | Import image or PDF |
| scan.dup | Page 2 looks like page 1 |
| cal.alarm.exactNotice | Reminders may be a few minutes late because exact alarms are restricted. |
| cal.ics.simplified | Recurrence simplified from this calendar file |
| files.saf.revoked | Access removed — tap to re-grant this folder |
| files.lowStorage | Storage is low — recordings and scans may fail. |
| music.unplayable | Can't play this file |
| music.sleep.set | Sleep timer set — playback will stop gently |
| rec.permission.body | Audio is stored on this phone only. Nothing is uploaded — MySpace One has no internet permission. |
| rec.paused.byCall | Paused — phone call took the microphone |
| rec.incomplete | Recording stopped early — saved up to here |
| diag.selftest.pass | All 6 checks passed |
| diag.selftest.failBody | %1$d of 6 checks failed |
| diag.share.preview.title | This is exactly what will be shared |
| settings.about.provenance | Built from commit %1$s · %2$s |
| backup.create.passphraseWarn | If you forget this passphrase, the backup cannot be opened — by anyone. |
| generic.error.storage | Couldn't save — storage is full |
| generic.done | Done |

# Appendix F — Error catalogue (AppError → user message + action)

| Error class | Trigger examples | User message | Action |
|---|---|---|---|
| Storage.Full | write fails ENOSPC | generic.error.storage | Open Files (Clean up) |
| Storage.SafRevoked | grant dead | files.saf.revoked | Re-grant |
| Storage.Corrupt | quick_check fail | Database needs attention | Open Diagnostics |
| Input.Syntax | parser | calc.err.syntax | Edit expression |
| Input.Domain | evaluator | calc.err.domain | Edit expression |
| Input.DivZero | evaluator | calc.err.divideByZero | Edit expression |
| Input.TooLong | 512 cap | calc.err.tooLong | Shorten expression |
| Policy.AlarmDenied | exact alarms revoked | cal.alarm.exactNotice | Open reminder settings |
| Policy.MediaDenied | read-media denied | music import card | Grant / pick folder |
| Model.PackMissing | capability w/o pack | feature-specific "needs pack" | Open Diagnostics |
| Model.PackCorrupt | hash mismatch | Pack disabled — file damaged | Re-import pack |
| Model.Budget | wall/mem cap hit | basic result shown | (fallback applied silently, provenance recorded) |
| Backup.BadPassphrase | GCM tag fail | Passphrase doesn't match this backup | Try again |
| Backup.BadArchive | schema/guards | This backup can't be opened by this version | Check version / Docs |
| Internal.Unexpected | catch-all | Something went wrong — details in Diagnostics | Open Diagnostics |

# Appendix G — Model pack format (normative)

```
<pack-id>-<version>.mspack (zip, deflate)
  pack.json          # manifest, UTF-8
  models/…           # model files exactly as manifested
  LICENSE            # full license text
```

```json
{
  "id": "essentials",
  "version": "1.2.0",
  "minApp": "3.13.0",
  "minTier": "C",
  "signature": "ed25519:base64…",
  "models": [
    {"file": "models/det.onnx", "sha256": "…", "runtime": "onnx",
     "inputs": {"image": [1,3,960,960]}, "notes": "DBNet-lite"},
    {"file": "models/rec.onnx", "sha256": "…", "runtime": "onnx"},
    {"file": "models/minilm.int8.onnx", "sha256": "…", "runtime": "onnx"}
  ]
}
```

Rules: unknown manifest fields are ignored (forward compat); `signature` verified against the baked-in public key when present (owner-distributed packs are signed); import = hash-verify all files → atomic move → registry transaction; the pack manager displays id, version, total size, tier, and per-model purpose labels; load-time re-verify per §16.8. Rejection reasons surface verbatim from the guard that fired (size, hash, schema, tier).

# Appendix H — Gesture and control-equivalence map

Every gesture (X: no gesture-only features) with its visible control twin:

| Gesture | Where | Equivalent control |
|---|---|---|
| Swipe down on expression | Calculator | History button |
| Hold-then-slide on text | Calculator selection | (no twin: long-press + selection handles serve same result; B2 is an enhancement) |
| Swipe between months | Calendar | ‹ › buttons |
| Drag sheet handle | All sheets | Tap outside / back |
| Swipe-to-delete rows | Notes list, playlists | Row overflow → Delete |
| Long-press module icon | Hub | App shortcuts menu |
| Swipe MiniPlayer down | Global | Player close button |
| Drag selection handles | Calculator | Cut/Copy boundaries via re-long-press |

Keyboard (hardware, tablets): all screens honor Tab order, Enter activates focused control, Esc = back; calculator accepts hardware digits/operators (still no IME popup).

# Appendix I — Release runbook (operator steps)

1. Freeze: merge the release branch `release/v3.13.0`; version bump commit.
2. Tag `v3.13.0` → release lane runs: reproducible double-build, L5 campaign, docs regen.
3. Verify pre-flight §25.4 checklist output (all green; blocked register reviewed).
4. Owner walkthrough §32 steps 1–9; collect ACCEPTED (or defects → fix loop).
5. Publish: GitHub Release with bundle §25.5; attach APK SHAs to RELEASE-NOTES.
6. Post: announce per §26 (owner channels); defect ledger triage session; backlog v1.1 seeded from P2 + new findings; G8 report.
Rollback policy: apps are install-over; a broken release is superseded by the next patched build (no server to roll back — another benefit of the model).

# Appendix J — Owner constraint register (conversation-derived)

The owner's standing instructions, mapped to normative sections (traceability of *why*):

| Owner instruction (paraphrase) | Where enforced |
|---|---|
| App must work locally, on device, no sign-in, no internet | §1.2 P1/P2, §1.3 C1/C2, §14.2 |
| No ads | §1.3 C3, F-034, §24.4 dependency audit |
| Combined all features into one app | §1.1, §2.1, Part II |
| Main priority = easy UX and compatibility | §4 principles, §3.2 tiers, §7.12 responsive |
| Prepare from scratch to fully tested working APK | S-criteria, G1–G7 lifecycle |
| Doc must include UI, features, usability, architecture, methodology, model integration, on-device AI | Parts II, III, IV, V, VII |
| All stages and cycles of the app | Part I→XI structure; G0–G8 |
| 200 pages | this document |
| Calculator only focus in QA (historical) | §22.1 scope rule |
| Publisher success ≠ passing result (historical lesson) | §15.8(3), §22.5 |
| BLOCKED ≠ FAIL; no defect inference from blocked gestures (historical) | §15.6, §20.1, §21.2 |
| Preserve historical reports; don't rewrite | §26/§29 ledger preservation; Part X maintenance |
| One evidence-rich link with screenshots/provenance | §22.5, §25.5 |
| Max 30 jobs, ≤ 3 parallel runners | §1.3 C8, §24 |
| Compare with official Google Calculator only (no AOSP substitute) | §22.6 |

# Appendix K — Fixture inventory (generated, seeded)

| Fixture set | Count | Generator notes |
|---|---|---|
| OCR images | 40 | printed+handprint Latin, 3 size classes, jitter affines, invoice-style subset |
| ASR clips | 20 | synthetic speech 5–30 s, clean/noisy mixes, reference transcripts |
| Note corpus | 200 | Markdown+NoteDoc pairs incl. checklists, headings, unicode, long docs |
| RRULE corpus | 200 | Appendix C anchors + randomized laws, DST cases |
| Music files | 6 | tones with complete metadata incl. edge tags |
| Backups | 12 | v1 real-manager outputs + 2 malicious-pattern archives |
| Model packs | 3 | well-formed, bad-hash, oversized |
| Eval kit | 40+20 | OCR images + notes with rubric answers (§16.8) |
| Perf corpora | 1 | 10k-note DB seed, 5k-track library seed |

# Appendix L — Agent working templates

Task (task-graph row) — see §15.3 for fields. Defect entry:

```markdown
### D-<n> — <title>
- Found by: TC-… / manual / review
- Severity: S1..S4 · Status: New
- Repro: steps (exact), environment, seed
- Evidence: reports/evidence/… paths
- Spec delta needed: §… (yes/no)
- Fix commit: <sha> · Verified by: TC-… re-run (date)
```

Decision ledger entry:

```markdown
### D-<n> — <question>
- Date / phase
- Binding sections that could be affected: §…
- Options considered: a) … b) …
- Decision: …
- Consequence / revisit-if: …
```

Daily agent log (per session):

```markdown
## Session <id> — date
- Phase: G… · Tasks touched: …
- Commits: …
- Tests: … (evidence paths)
- Blockers opened/closed: …
- Next: first open task in dependency order
```

<!-- pagebreak -->
