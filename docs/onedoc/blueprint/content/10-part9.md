@PART: PART IX — SECURITY AND PRIVACY
@PARTDESC: The threat model, structural no-network proofs, storage encryption, clipboard and asset hygiene, the security suite. OneDoc's privacy story is one sentence because its architecture makes it true.

# Chapter 20 — Security and privacy

## 20.1 Threat model (one device, one user)

Adversaries: (a) network attackers — moot by architecture, proven anyway; (b) other apps on the device reading OneDoc's files — mitigated by app-private storage + encryption-at-rest; (c) malicious input files — the real threat: crafted HTML/DOCX/odoc payloads; (d) physical access to an unlocked phone — out of scope beyond app-private storage; (e) OneDoc itself exfiltrating — impossible by construction, proven by manifest + runtime probes. Not in threat model: device root, screen recording, system-level compromise (documented non-goals).

## 20.2 Structural no-network (C1, C2, C3)

Layered proofs, each independently tested:

1. **Manifest gate:** no `INTERNET`, no `ACCESS_NETWORK_STATE` in the merged release manifest — CI fails the build otherwise (§22.4). Note the consequence honored throughout the codebase: without `INTERNET`, *no* library can open a socket that succeeds; even a hostile dependency is sandboxed by the platform.
2. **Dependency deny-list** (§10.3) with resolution-graph audit on every build.
3. **Runtime probe:** direct-APK QA installs the release APK on an emulator with no network and exercises every flow (all journeys + all AI flows); TC-SEC-P-03 asserts zero socket syscalls (strace-backed logcat check) and zero `UnknownHost`-class attempts.
4. **String/asset scan:** release APK contains no URLs outside license files and the About screen's repo link (allow-listed, plain text, never fetched).

## 20.3 Storage

Documents, versions, assets: app-private internal storage; Keystore AES-256-GCM directory encryption where a lock-screen credential exists (§11.5). Backups: passphrase-encrypted zips in user-chosen SAF locations. Cache: export/share temp files are written to cache, handed via FileProvider (grant-per-URI, read-only), and deleted after share cancel/completion (`FileProvider` path hygiene tested by TC-SEC-IO-02). Logs: diagnostics are in-memory ring buffer, 200 lines, never written to world-readable storage, never leave the device.

## 20.4 Input hygiene

Clipboard: OneDoc reads clipboard only on explicit paste; never reads it in background; Android 13+ clipboard-access toast is therefore never triggered spuriously (TC-SEC-P-04). Images: EXIF GPS and serial stripped on import (§17.2). HTML import: whitelist tokenizer; event handlers, `javascript:` URIs, external resource references are structurally impossible to preserve (TC-SEC-IO-01). DOCX/odoc: zip-bomb guard (entry count + ratio caps), path-traversal guard on entry names, entity-expansion caps. Audio (dictation): in-memory only, dropped after insert; no dump even in debug builds.

## 20.5 Permissions ledger

The complete permission set of release `app.onedoc`: `CAMERA` (scan), `RECORD_AUDIO` (dictation), `READ_MEDIA_IMAGES`/`READ_MEDIA_VISUAL_USER_SELECTED` (image insert), `VIBRATE` (haptics), `POST_NOTIFICATIONS` (export progress only, F-031 guarantees, UX-31). Nothing else. Each permission is requested at feature first-use (UX-32), each maps to a catalogue row (SEC area), and the manifest test asserts this exact set — an added permission fails CI.

## 20.6 The security suite (TC-SEC-*)

| Suite | Cases | Proof |
|---|---|---|
| TC-SEC-P-* | privacy probes: network silence, notification silence, clipboard hygiene | direct-APK runs |
| TC-SEC-IO-* | hostile files: script-laden HTML, zip-bomb odoc, traversal-name pack, oversized DOCX | JVM + instrumentation |
| TC-SEC-ST-* | storage: FileProvider grants, cache cleanup, encryption-at-rest smoke (keystore present) | instrumentation |
| TC-SEC-PK-* | packs: wrong SHA, tampered zip, path-traversal entry name | JVM + instrumentation |

Security defects are S1 by definition (§25.3). The suite is part of G7 and re-runs on every release candidate.

## 20.7 Build and dependency integrity

Reproducibility posture: pinned Gradle wrapper + version catalog; dependency lockfiles committed (`gradle.lockfile` per configuration); `--refresh-dependencies` forbidden in CI (cache-only builds prove lock completeness). Checksum verification: Gradle verifies artifact hashes against lockfile entries; a mismatched or new transitive dependency fails the build rather than joining quietly. The dependency inventory (SBOM-lite: name/version/sha256 list generated at build) is attached to the provenance bundle (§28.2) so every APK can answer "what's inside you" without network lookups. R8 keep rules are owned in-repo and tested by the release smoke (reflection seams listed, not discovered).
