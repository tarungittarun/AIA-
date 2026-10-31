# Colophon and revision history

## Document provenance

OneDoc Application Development Blueprint v1.0 — generated from the markdown sources in `docs/onedoc/blueprint/content/` by `tools/blueprint/build_pdf.py` (shared engine) with figures from `tools/onedoc/figures.py`. The PDF, the CSV registries, and the traceability tooling are regenerated together; the traceability check (`tools/onedoc/traceability.py --check --strict`) is the machine proof that feature, UX and case catalogues agree with each other.

| Revision | Date | Change |
|---|---|---|
| 1.0 | 2026-10-31 | Initial complete build contract: Parts I–XII, Appendices A–H, 18 figures, 90 features, 50 UX criteria, ~150-case catalogue |

## The one-paragraph summary (for the owner)

OneDoc is a fully offline document studio for Android 8+: a Docs-class block editor with tables, images, templates, versions and honest file fidelity; on-device AI (scan-to-text, dictation, a writing assistant, semantic search, read-aloud) that installs only as owner-side-loaded, SHA-verified packs and hides itself gracefully where hardware can't run it; no account, no internet permission, no ads, no telemetry — the privacy story is architectural, not promised. The blueprint is written for an autonomous AI developer: every feature maps to test cases, every law has a proof, every gate has a definition of done, and the final deliverable is a signed APK plus an evidence PDF whose every claim traces to a machine-verified run.
