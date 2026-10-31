#!/usr/bin/env python3
"""OneDoc — blueprint figures. Writes PNGs to docs/onedoc/blueprint/figures/."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from blueprint.figures import (WHITE, FILL, LINE, INK, TEAL, SLATE,
                               MUTE, LIGHT, AMBER, AMBER_L, BLUE, BLUE_L,
                               newfig, box, arrow, legend_note)
DARKBG = "#0B1220"
GREEN = "#0F766E"; GREEN_L = "#ECFDF5"; RED = "#BE123C"; RED_L = "#FFE4E6"

OUT = os.path.join(os.path.dirname(os.path.dirname(_HERE)),
                   "docs", "onedoc", "blueprint", "figures")


def _ensure_out():
    os.makedirs(OUT, exist_ok=True)


def _nf(w, h, bg=WHITE):
    """Adapter: old newfig returns (fig, ax); we just need fig (ax via gca)."""
    fig, _ax = newfig(w, h, bg)
    return fig


def save(fig, name):
    _ensure_out()
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print("wrote", name)


# ------------------------------------------------------------------ cover --
def fig_cover():
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor(DARKBG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 141); ax.axis("off")
    for i, y in enumerate((126, 123, 120)):
        ax.add_patch(FancyBboxPatch((8, y), 84, 0.7, boxstyle="round,pad=0.1",
                     fc="#134E4A" if i else TEAL, ec="none"))
    ax.text(50, 132, "ONEDOC", ha="center", fontsize=44, color="white",
            fontweight="bold", family="DejaVu Sans")
    ax.text(50, 117, "Application Development Blueprint", ha="center",
            fontsize=19, color="#5EEAD4")
    ax.text(50, 111.5, "The offline document studio — write, format, scan, and think\n"
                       "without an account, a network, or a subscription",
            ha="center", fontsize=11.5, color="#CBD5E1", linespacing=1.6)
    ax.text(50, 100, "v1.0  ·  build contract for an autonomous AI developer",
            ha="center", fontsize=10.5, color="#94A3B8", style="italic")
    chips = [("100% offline", "#0F766E"), ("No sign-in", "#334155"),
             ("No ads", "#334155"), ("On-device AI", "#0F766E"),
             ("Android 8.0+", "#334155")]
    x = 10
    for label, c in chips:
        w = 3.2 + 1.55 * len(label)
        ax.add_patch(FancyBboxPatch((x, 92), w, 5, boxstyle="round,pad=0.45",
                     fc=c, ec="#1E293B", lw=1))
        ax.text(x + w / 2, 94.5, label, ha="center", va="center", fontsize=9,
                color="white", fontweight="bold")
        x += w + 2.2
    rows = [
        ("I", "Charter, users, scope"), ("II", "Requirements F-001…F-090, UX criteria"),
        ("III", "Design language, screens, Figma workflow"),
        ("IV", "Architecture, data, concurrency"),
        ("V", "Document model and the editor engine"),
        ("VI", "Features: text, structure, objects, tools"),
        ("VII", "Files, formats, import/export fidelity"),
        ("VIII", "On-device AI: OCR, dictation, assistant"),
        ("IX", "Security and privacy"), ("X", "Quality methodology and gates"),
        ("XI", "Build and delivery"), ("XII", "Way of working for the agent"),
    ]
    y = 82
    for num, t in rows:
        ax.add_patch(FancyBboxPatch((10, y - 1.6), 6.5, 4.4, boxstyle="round,pad=0.2",
                     fc="#1E293B", ec="none"))
        ax.text(13.2, y + 0.6, num, ha="center", va="center", fontsize=9.5,
                color=TEAL, fontweight="bold")
        ax.text(19.5, y + 0.55, t, ha="left", va="center", fontsize=10.3, color="#E2E8F0")
        y -= 6.4
    ax.text(50, 6.5, "tarungittarun / AIA-  ·  app.onedoc  ·  target: one fully tested APK",
            ha="center", fontsize=9, color="#64748B")
    save(fig, "cover.png")


# ------------------------------------------------------- product & screens --
def fig_product_map():
    fig = _nf(12.4, 6.6)
    hub = FancyBboxPatch((44, 38), 12, 20, boxstyle="round,pad=0.5", fc="#0F172A", ec=TEAL, lw=2)
    ax = plt.gca(); ax.add_patch(hub)
    ax.text(50, 51.5, "OneDoc", ha="center", fontsize=12.5, color="#5EEAD4", fontweight="bold")
    ax.text(50, 46.5, "Home\nlibrary", ha="center", fontsize=9, color="#CBD5E1", linespacing=1.4)
    sats = [
        (14, 72, "Editor", "blocks · marks\nundo/redo", "#1E293B"),
        (38, 72, "Templates", "letters · reports\nnotes · CV", "#1E293B"),
        (62, 72, "Scan to doc", "camera → OCR\ninsertable text", "#1E293B"),
        (86, 72, "Assistant", "summarize · rewrite\ncontinue · dictate", "#1E293B"),
        (14, 18, "Files & versions", "autosave · history\nrestore · backup", "#1E293B"),
        (38, 18, "Import / export", "md · txt · html\npdf · docx", "#1E293B"),
        (62, 18, "Search", "full-text + semantic\nacross library", "#1E293B"),
        (86, 18, "Read & listen", "reader mode\nsystem TTS", "#1E293B"),
    ]
    for x, y, t, b, c in sats:
        box(ax, x - 9, y - 7, 18, 13, t, b.split("\n"), fc=c, ts=10)
        arrow(ax, 50 if x == 50 else x, 38 if y < 40 else 58 if y > 60 else 48,
              x, y - 7.4 if y > 60 else y + 6.2)
    ax.text(50, 3.5, "Every arrow is a function call inside one offline process — no network anywhere.",
            ha="center", fontsize=9.5, color=MUTE, style="italic")
    save(fig, "fig-product-map.png")


def fig_home_wireframe():
    fig = _nf(7.6, 8.2)
    ax = plt.gca(); ax.set_xlim(0, 100); ax.set_ylim(0, 108); ax.axis("off")
    ax.add_patch(FancyBboxPatch((4, 4), 74, 100, boxstyle="round,pad=1.2", fc=WHITE, ec=INK, lw=1.6))
    ax.add_patch(FancyBboxPatch((4, 92), 74, 12, boxstyle="round,pad=1.2", fc="#0F172A", ec="none"))
    ax.text(10, 98, "OneDoc", fontsize=12, color="white", fontweight="bold", va="center")
    ax.text(72, 98, "search", fontsize=8.5, color="#5EEAD4", ha="right", va="center")
    ax.add_patch(FancyBboxPatch((10, 83), 62, 6, boxstyle="round,pad=0.6", fc="#F1F5F9", ec=LINE))
    ax.text(14, 86, "Search documents…", fontsize=8.5, color=MUTE, va="center")
    for i, (lbl, w) in enumerate((("All", 9), ("Starred", 13), ("Recent", 13), ("Trash", 10))):
        x = 10 + sum(w2 + 2 for _, w2 in (("All", 9), ("Starred", 13), ("Recent", 13))[:i])
        fc = "#0F766E" if i == 0 else "#F1F5F9"
        tc = "white" if i == 0 else INK
        ax.add_patch(FancyBboxPatch((x, 75), w, 5.4, boxstyle="round,pad=0.5", fc=fc, ec=LINE))
        ax.text(x + w / 2, 77.7, lbl, fontsize=8, color=tc, ha="center", va="center")
    cards = [("Project Phoenix proposal.doc", "1,842 words · edited 2 h ago", True),
             ("Q3 expense notes.md", "312 words · edited yesterday", False),
             ("Grandma's recipes.odoc", "96 words · edited Mon", False),
             ("Lease review — scan + markup", "2 pages · OCR source · Fri", False)]
    y = 66
    for name, meta, star in cards:
        ax.add_patch(FancyBboxPatch((10, y - 9), 62, 10.6, boxstyle="round,pad=0.5",
                     fc=WHITE, ec=LINE, lw=1.1))
        ax.text(13, y + 0.4, name, fontsize=8.8, color=INK, fontweight="bold", va="center")
        ax.text(13, y - 3.4, meta, fontsize=7.4, color=MUTE, va="center")
        ax.text(69, y - 1.2, "*" if star else "", fontsize=13, color=AMBER,
                ha="center", va="center")
        y -= 12.6
    ax.add_patch(FancyBboxPatch((61, 8), 13, 13, boxstyle="circle,pad=0.4", fc="#0F766E", ec="none"))
    ax.text(67.5, 14.5, "+", fontsize=20, color="white", ha="center", va="center")
    ax.text(67.5, 4.6, "New doc", fontsize=7.5, color=MUTE, ha="center")
    for i, (lbl, ic) in enumerate((("Docs", "="), ("Templates", "%"), ("Assistant", "A"), ("Settings", "S"))):
        x = 10 + i * 15.5
        ax.text(x + 5, 20.5, ic, fontsize=10, color=TEAL if i == 0 else MUTE, ha="center")
        ax.text(x + 5, 15.5, lbl, fontsize=6.8, color=INK if i == 0 else MUTE, ha="center")
    legend_note(plt.gca(), 4, 0.5, "Documents library (screen OD-HOME-001): search, filter chips, doc cards, FAB, bottom nav.")
    save(fig, "fig-home-wireframe.png")


def fig_editor_wireframe():
    fig = _nf(8.0, 8.2)
    ax = plt.gca(); ax.set_xlim(0, 100); ax.set_ylim(0, 108); ax.axis("off")
    ax.add_patch(FancyBboxPatch((6, 4), 76, 100, boxstyle="round,pad=1.2", fc=WHITE, ec=INK, lw=1.6))
    ax.add_patch(FancyBboxPatch((6, 93), 76, 11, boxstyle="round,pad=1.2", fc="#0F172A", ec="none"))
    ax.text(11, 98.5, "<", fontsize=11, color="#5EEAD4", va="center")
    ax.text(17, 98.5, "Project Phoenix proposal", fontsize=9.5, color="white",
            fontweight="bold", va="center")
    ax.text(76, 98.5, "A  T  :", fontsize=9, color="#CBD5E1", ha="right", va="center")
    for y0, h in ((78, 12), (64, 12), (49, 13)):
        ax.add_patch(FancyBboxPatch((10, y0), 68, h, boxstyle="round,pad=0.3",
                     fc="#FFFFFF", ec="#E2E8F0", lw=0.8))
    ax.text(13, 85.2, "Quarterly Business Review", fontsize=10.5, color=INK, fontweight="bold")
    ax.text(13, 80.4, "Prepared by A. Rivera  ·  Draft 3", fontsize=7.6, color=MUTE)
    ax.text(13, 72.4, "Revenue grew 14% quarter over quarter, driven", fontsize=8.2, color=INK)
    ax.text(13, 69.2, "primarily by enterprise renewals and the new", fontsize=8.2, color=INK)
    ax.add_patch(FancyBboxPatch((13, 64.7), 61, 3.0, boxstyle="round,pad=0.2", fc="#CFFAFE", ec="none"))
    ax.text(14.2, 66.2, "self-serve motion. Churn remained flat at 1.8%.", fontsize=8.2, color=INK)
    for i, t in enumerate(("•  Enterprise renewals +22%", "•  Self-serve signups +9%",
                           "•  Churn flat at 1.8%")):
        ax.text(15, 58.6 - i * 4.2, t, fontsize=8, color=INK)
    ax.add_patch(FancyBboxPatch((12, 41.5), 64, 5.6, boxstyle="round,pad=0.3",
                 fc="#F8FAFC", ec="#94A3B8", lw=1.1))
    for i, (lbl, w) in enumerate((("B", 5), ("I", 5), ("U", 5), ("S", 5), ("H1", 8),
                                  ("list", 10), ("align", 10), ("link", 9))):
        x = 13 + sum(w2 + 1.2 for _, w2 in (("B", 5), ("I", 5), ("U", 5), ("S", 5),
                                            ("H1", 8), ("list", 10), ("align", 10))[:i])
        ax.add_patch(FancyBboxPatch((x, 42.4), w, 3.8, boxstyle="round,pad=0.25",
                     fc="#0F766E" if i == 0 else WHITE, ec=LINE))
        ax.text(x + w / 2, 44.3, lbl, fontsize=7, ha="center", va="center",
                color="white" if i == 0 else INK)
    ax.add_patch(FancyBboxPatch((12, 34.5), 64, 4.8, boxstyle="round,pad=0.4", fc="#F1F5F9", ec=LINE))
    ax.text(14, 36.9, "Text  ·  Insert  ·  AI  ·  Format", fontsize=8, color=INK, va="center")
    ax.add_patch(FancyBboxPatch((10, 24), 68, 8.2, boxstyle="round,pad=0.4", fc="#E2E8F0", ec="none"))
    ax.text(44, 28.6, "dictate   |   summarize   |   rewrite   |   continue", fontsize=8,
            color="#0F172A", ha="center", va="center")
    ax.text(44, 25.8, "Assistant row — offline models only", fontsize=6.6, color=MUTE,
            ha="center", va="center")
    legend_note(plt.gca(), 6, 0.8, "Editor (OD-EDIT-001): page canvas, floating selection toolbar, tab row, assistant row.")
    save(fig, "fig-editor-wireframe.png")


def fig_figma_workflow():
    fig = _nf(12.6, 6.2)
    ax = plt.gca()
    cols = [
        (6, "1 · tokens.json", ["design/figma/tokens.json is the", "single source of truth: color,", "type, radius, spacing, motion", "— versioned in the repo"], "#0F172A"),
        (29, "2 · Figma library", ["OneDoc Design System file:", "styles + components published", "from tokens; frames named", "OD-<AREA>-<nnn>"], "#1E293B"),
        (52, "3 · sync & review", ["Owner edits in Figma;", "agent exports deltas via CSV", "registry; changes land as", "reviewed token PRs"], "#1E293B"),
        (75, "4 · design QA gate", ["DQ-1…DQ-8 checks (§9.2):", "token parity, frame names,", "hit sizes, contrast, states —", "blocking for UI tasks"], "#134E4A"),
    ]
    for x, t, lines, c in cols:
        box(ax, x, 30, 20, 34, t, lines, fc=c, ts=10.5)
        if x < 70:
            arrow(ax, x + 20.4, 47, x + 22.6, 47)
    ax.add_patch(FancyBboxPatch((6, 8), 89, 14, boxstyle="round,pad=0.5", fc="#F8FAFC", ec=LINE))
    ax.text(50, 17.5, "Registry: docs/onedoc/blueprint/ui-screens.csv — one row per screen: id, Figma frame, entry, exit, states",
            ha="center", fontsize=9.3, color=INK)
    ax.text(50, 12, "The agent never invents UI: if a frame or token is missing, the task is BLOCKED until the registry gains a row.",
            ha="center", fontsize=8.8, color=RED)
    ax.text(50, 72, "Figma is the design mirror; the repo is the design source.", ha="center",
            fontsize=11, color=INK, fontweight="bold")
    save(fig, "fig-figma-workflow.png")


def fig_architecture():
    fig = _nf(12.6, 7.2)
    ax = plt.gca()
    box(ax, 4, 78, 92, 16, "app  (navigation, theme, DI graph, home, settings)",
        ["feature-editor · feature-home · feature-templates · feature-scan · feature-assistant · feature-search"], fc="#0F172A", ts=10.5)
    libs = [("core-model", "Document, Block, Mark\nschemas + migrations"),
            ("core-editor", "operations, undo, IME\nbridge, layout metrics"),
            ("core-storage", "Room, .odoc container,\nversions, journal"),
            ("core-io", "md/html/txt/pdf/docx\nreaders+writers"),
            ("core-ai", "pack manager, OCR, ASR,\nLLM runtime, embeddings"),
            ("core-search", "FTS5 + vector index,\nranking")]
    for i, (t, b) in enumerate(libs):
        x = 4 + i * 15.6
        box(ax, x, 50, 14.4, 20, t, b.split("\n"), fc="#1E293B", ts=8.6)
        arrow(ax, x + 7.2, 70.5, x + 7.2, 77.4)
    box(ax, 4, 30, 44.5, 13, "Android platform", ["Views/RecyclerView · Room/SQLite · Print framework · PdfDocument · SAF · Keystore"], fc="#F8FAFC", ts=9.5)
    box(ax, 51.5, 30, 44.5, 13, "Runtime rules", ["single process · no network sockets · all AI on-device · main thread never blocked >16 ms"], fc="#F8FAFC", ts=9.5)
    box(ax, 4, 6, 92, 17, "verification", ["JVM unit tests (model, io, search)  ·  Robolectric editor tests  ·  instrumentation on API 26/33/35/36 emulators",
        "GitHub Actions direct-APK QA: build → install → drive → assert → report PDF (≤3 runners, ≤30 jobs)"], fc="#134E4A", ts=9.5)
    save(fig, "fig-architecture.png")


def fig_docmodel():
    fig = _nf(12.6, 6.8)
    ax = plt.gca()
    box(ax, 4, 58, 40, 34, "document.json (single source of truth)",
        ['{ "schema": 3, "docId": "d_9f2c",',
         '  "blocks": [ { "id": "b01", "type": "h1",',
         '      "text": "Quarterly Review" },',
         '    { "id": "b02", "type": "para",',
         '      "text": "Revenue grew 14%...",',
         '      "marks": [ {"type":"strong","s":0,"e":7} ] },',
         '    { "id": "b03", "type": "list", "ordered": false,',
         '      "items": [ {"text": "Renewals +22%"} ] } ],',
         '  "meta": { "title": "…", "wordCount": 1842 } }'], fc="#0F172A", ts=7.6)
    kinds = [("para", "plain paragraph"), ("h1…h3", "heading levels"), ("list", "bulleted / numbered / check"),
             ("quote", "blockquote"), ("code", "monospace block"), ("table", "rows × cells, marks inside"),
             ("image", "asset ref + caption"), ("divider", "horizontal rule"), ("toc", "generated from headings")]
    for i, (t, b) in enumerate(kinds):
        y = 76 - i * 8.6
        box(ax, 52, y - 3.2, 12, 7.2, t, [], fc="#1E293B", ts=8.4)
        ax.text(66, y + 0.4, b, fontsize=8.4, color=INK, va="center")
    ax.text(58, 88, "Block kinds (closed set — adding one is a schema migration)", fontsize=9.5,
            color=INK, fontweight="bold")
    box(ax, 52, 6, 44, 16, "invariants", ["every block has a stable id (b##)",
        "marks are non-overlapping per type after normalize()", "order of blocks = document order; no holes",
        "text is stored as UTF-16 code units, indexed like Java strings"], fc="#F8FAFC", ts=8.6)
    arrow(ax, 44.4, 75, 51.6, 75)
    save(fig, "fig-docmodel.png")


def fig_erd():
    fig = _nf(12.6, 6.6)
    ax = plt.gca()
    def ent(x, y, w, name, fields, fc=WHITE):
        box(ax, x, y, w, 6 + 3.4 * len(fields), name, [], fc="#0F172A", ts=9.5)
        for i, f in enumerate(fields):
            ax.text(x + 1.6, y + 1.6 + (len(fields) - 1 - i) * 3.4, f, fontsize=7.9, color="#E2E8F0", va="center")
    ent(4, 42, 27, "documents", ["id TEXT PK", "title TEXT", "updatedAt INTEGER", "wordCount INTEGER", "starred INTEGER", "deletedAt INTEGER?"])
    ent(38, 46, 27, "versions", ["id TEXT PK", "docId FK", "createdAt INTEGER", "kind: auto|manual|pre_edit", "blob BLOB (zipped json)"])
    ent(72, 42, 24, "assets", ["id TEXT PK", "docId FK", "kind: image|file", "path TEXT", "sha256 TEXT"])
    ent(4, 6, 27, "docs_fts (FTS5)", ["title, plainText", "→ docId row mapping"])
    ent(38, 8, 27, "vectors", ["docId, blockId", "embedding BLOB f32", "model: minilm-l6-v1"])
    ent(72, 10, 24, "meta / kv", ["schemaVersion", "settings", "aiPacks registry"])
    arrow(ax, 31.4, 55, 37.6, 55); arrow(ax, 65.4, 55, 71.6, 55)
    arrow(ax, 17.6, 41.6, 17.6, 22); arrow(ax, 51.4, 45.6, 51.4, 25.6)
    legend_note(plt.gca(), 4, 1.5, "Room schema v3. Full text in FTS5; embeddings only for docs where AI pack is installed (graceful absence).")
    save(fig, "fig-erd.png")


def fig_formats():
    fig = _nf(12.6, 6.4)
    ax = plt.gca()
    rows = [
        ("Markdown .md", "in+out", "F2", "headings/lists/bold/italic/links/code; tables → pipe tables"),
        ("Plain text .txt", "in+out", "F1", "text only; block structure flattened"),
        ("HTML .html", "in+out", "F2", "semantic subset: h1-3, p, ul/ol, table, img, strong/em/u/a"),
        ("PDF .pdf (export)", "out", "F3", "paginated via Print framework; fonts embedded; selectable text"),
        ("DOCX .docx (export)", "out", "F2", "OOXML subset writer: styles, lists, tables, images"),
        ("DOCX .docx (import)", "in", "F1", "best-effort reader: text + basic marks; unsupported → F0 note"),
        ("OneDoc .odoc", "in+out", "F3", "native zip container: document.json + assets + meta — lossless"),
    ]
    ax.text(4, 92, "Format matrix and declared fidelity levels", fontsize=11.5, color=INK, fontweight="bold")
    hdr = ("Format", "Dir", "Level", "Covered subset")
    xs = (4, 34, 42, 50)
    ws = (28, 6, 6, 46)
    for x, w, h in zip(xs, ws, hdr):
        ax.add_patch(FancyBboxPatch((x, 80), w, 8, boxstyle="round,pad=0.2", fc="#0F172A", ec="none"))
        ax.text(x + 1.4, 84, h, fontsize=9, color="white", fontweight="bold", va="center")
    y = 72
    for name, d, lvl, sub in rows:
        fc = "#ECFDF5" if lvl == "F3" else ("#F8FAFC" if lvl == "F2" else "#FFF7ED")
        ax.add_patch(FancyBboxPatch((4, y - 6), 92, 7.4, boxstyle="round,pad=0.15", fc=fc, ec=LINE))
        ax.text(5.4, y - 2.2, name, fontsize=8.6, color=INK, fontweight="bold", va="center")
        ax.text(34.5, y - 2.2, d, fontsize=8.6, color=INK, va="center")
        ax.text(43, y - 2.2, lvl, fontsize=8.6, color="#0F766E", fontweight="bold", va="center")
        ax.text(51.4, y - 2.2, sub, fontsize=8, color=SLATE, va="center")
        y -= 9.2
    ax.text(4, 2.5, "F3 lossless · F2 lossless for the covered subset, others degrade with a conversion note · F1 best-effort text · F0 unsupported (refused with reason)",
            fontsize=8.2, color=MUTE)
    save(fig, "fig-formats.png")


def fig_ai_stack():
    fig = _nf(12.6, 6.8)
    ax = plt.gca()
    mods = [("OCR", "scan-to-doc", "DBNet-lite det\n+ CRNN int8 rec\n~18 MB pack"),
            ("Dictation", "speech to text", "whisper.cpp\nint8 streaming\n~42 MB pack"),
            ("Assistant", "summar · rewrite\ncontinue · fix", "gemma-2B Q4\nTier A only\n~1.4 GB pack"),
            ("Semantic search", "meaning across docs", "MiniLM-L6\nint8 embeddings\n~23 MB pack"),
            ("Read aloud", "listen to docs", "system TTS\nno pack needed\nalways present")]
    for i, (t, sub, b) in enumerate(mods):
        x = 3 + i * 19.4
        c = "#134E4A" if i < 4 else "#1E293B"
        box(ax, x, 52, 18, 30, t, b.split("\n"), fc=c, ts=9.8)
        ax.text(x + 9, 86.5, sub, ha="center", fontsize=7.8, color=MUTE)
    box(ax, 3, 30, 55.5, 15, "pack manager", ["side-loaded .odpack zips · SHA-256 verified at import and at every load",
        "manifest: model files + license + minRamMb + tier · never downloaded by the app"], fc="#F8FAFC", ts=8.8)
    box(ax, 62, 30, 35, 15, "device tiers", ["A: ≥8 GB RAM → all packs · B: 4–8 GB → OCR/ASR/embed",
        "C: <4 GB → OCR lite, system TTS only (ladder §24.5)"], fc="#F8FAFC", ts=8.8)
    box(ax, 3, 6, 94, 17, "assistant row in the editor", ["buttons appear only for installed+verified packs; long-press shows why a capability is off (which tier, which pack)",
        "generation is cancellable, streamed token-by-token into a preview card; Insert always explicit — the model never edits the document silently"], fc="#0F172A", ts=9.2)
    arrow(ax, 30, 45, 30, 51.4); arrow(ax, 79, 45, 79, 51.4)
    save(fig, "fig-ai-stack.png")


def fig_ai_ladder():
    fig = _nf(12.2, 5.8)
    ax = plt.gca()
    steps = [("1 · capability requested", "user taps Summarize", "#0F172A"),
             ("2 · pack check", "installed? SHA ok? RAM ok?", "#134E4A"),
             ("3 · best on-device model", "gemma-2B Q4 on Tier A", "#0F766E"),
             ("4 · lighter model", "extractive summary (no LLM)", "#1E293B"),
             ("5 · system service", "Android SpeechRecognizer for dictation", "#1E293B"),
             ("6 · graceful off", "control hidden with reason — never an error dialog", "#334155")]
    for i, (t, b, c) in enumerate(steps):
        y = 80 - i * 14
        box(ax, 6, y - 5, 88, 10.5, t, [b], fc=c, ts=9.6)
        if i < 5:
            arrow(ax, 50, y - 5.4, 50, y - 8.8)
    legend_note(plt.gca(), 6, 0.5, "Every AI feature descends exactly one ladder; the step taken is logged in the diagnostics screen (no network, no crash).")
    save(fig, "fig-ai-ladder.png")


def fig_versioning():
    fig = _nf(12.4, 5.6)
    ax = plt.gca()
    ax.annotate("", xy=(94, 40), xytext=(6, 40),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=2))
    ax.text(50, 47, "one document's life", ha="center", fontsize=10.5, color=INK, fontweight="bold")
    events = [(10, "typed", "keystrokes hit\nBlockEditText", "#0F172A"),
              (28, "journal", "op appended to\njournal (WAL) <5 ms", "#1E293B"),
              (46, "autosave", "debounce 800 ms\nmodel→Room txn", "#0F766E"),
              (64, "snapshot", "kind=auto every\n5 min or 50 ops", "#134E4A"),
              (82, "restore point", "kind=pre_edit on\ngenerate/replace-all", "#334155")]
    for x, t, b, c in events:
        ax.add_patch(Circle((x, 40), 1.7, fc=c, ec="white", lw=1.4, zorder=3))
        box(ax, x - 7, 52, 14, 15, t, b.split("\n"), fc=c, ts=8.8)
    box(ax, 6, 6, 40, 16, "versions screen", ["list with size + time + kind;",
        "preview any version read-only; Restore writes kind=pre_edit", "snapshot of current and swaps content — never destroys"], fc="#F8FAFC", ts=8.6)
    box(ax, 52, 6, 42, 16, "crash rule (Law L3)", ["journal replays forward after kill -9;",
        "RPO ≤ 2 s of typing; verified by TC-STATE-0xx kill tests"], fc="#FFF7ED", ts=8.6)
    save(fig, "fig-versioning.png")


def fig_testing():
    fig = _nf(12.6, 6.6)
    ax = plt.gca()
    box(ax, 4, 74, 40, 20, "layer 1 · JVM", ["core-model, core-io, core-search:", "property tests for marks/undo;", "golden files for exporters"], fc="#0F172A", ts=9.6)
    box(ax, 4, 48, 40, 20, "layer 2 · Robolectric", ["editor ops on real span code paths;", "IME composition simulation;", "journal replay kill tests"], fc="#1E293B", ts=9.6)
    box(ax, 4, 22, 40, 20, "layer 3 · instrumentation", ["API 26/33/35/36 emulators;", "typing latency, a11y traversal,", "Export-Import round-trips"], fc="#134E4A", ts=9.6)
    box(ax, 50, 48, 46, 46, "layer 4 · direct-APK QA (the proof)", [
        "GitHub Actions builds release APK → apkanalyzer",
        "manifest gate (no INTERNET) → installs on emulator",
        "→ drives real UI (uiautomator) → per-case",
        "PASS/FAIL/BLOCKED → evidence PDF with screenshots",
        "", "· publisher job runs if: always()",
        "· a green publisher is NOT a passing QA result",
        "· BLOCKED = environment prevented a fair assertion;",
        "  never inferred as product failure"], fc="#134E4A", ts=9.2)
    box(ax, 50, 22, 46, 20, "budgets enforced in CI", ["≤3 parallel runners · ≤30 jobs/run ·",
        "typing P95 <50 ms · cold start <1.2 s Tier B ·",
        "APK ≤ 25 MB without AI packs"], fc="#F8FAFC", ts=9.2)
    arrow(ax, 24, 73.6, 24, 68.6); arrow(ax, 24, 47.6, 24, 42.6)
    arrow(ax, 44.4, 32, 49.6, 40)
    save(fig, "fig-testing.png")


def fig_gates():
    fig = _nf(12.6, 4.6)
    ax = plt.gca()
    ax.annotate("", xy=(95, 55), xytext=(5, 55), arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.2))
    gates = [("G0", "charter accepted"), ("G1", "toolchain + shell"), ("G2", "model + storage"),
             ("G3", "editor core"), ("G4", "rich features"), ("G5", "formats/IO"),
             ("G6", "on-device AI"), ("G7", "quality pass"), ("G8", "release")]
    for i, (g, t) in enumerate(gates):
        x = 8 + i * 10.4
        ax.add_patch(Circle((x, 55), 2.2, fc="#0F766E" if i else "#0F172A", ec="white", lw=1.6, zorder=3))
        ax.text(x, 55, g, ha="center", va="center", fontsize=8, color="white", fontweight="bold", zorder=4)
        ax.text(x, 44.5, t, ha="center", fontsize=7.3, color=SLATE)
        ax.text(x, 66.5, "accept" if i == 0 else "DoD App. D", ha="center", fontsize=6.8, color=MUTE)
    legend_note(plt.gca(), 5, 18, "A gate closes only with its Definition-of-Done checked and evidence committed to reports/gates/. No gate skips; G0 closes only by owner acceptance.")
    save(fig, "fig-gates.png")


def fig_defects():
    fig = _nf(12.2, 5.4)
    ax = plt.gca()
    flow = [("found", "repro case id\n+ build SHA", "#0F172A"),
            ("triaged", "S1 crash/loss\nS2 wrong result\nS3 polish", "#B45309"),
            ("fixed", "unit or\ninstrumentation test\nadded first", "#0F766E"),
            ("verified on APK", "direct-APK run\nPASS evidence", "#134E4A"),
            ("closed", "defect log row\n+ release note", "#334155")]
    for i, (t, b, c) in enumerate(flow):
        x = 3 + i * 19.6
        box(ax, x, 42, 17.5, 24, t, b.split("\n"), fc=c, ts=9.4)
        if i < 4:
            arrow(ax, x + 17.9, 54, x + 19.2, 54)
    box(ax, 3, 8, 44, 24, "BLOCKED doctrine (carried from v3.12.x)", [
        "BLOCKED = emulator/a11y/input prevented a fair assertion.",
        "Never a product verdict. Logged with reason + environment;",
        "re-triaged every cycle; never counted as PASS."], fc="#FFF7ED", ts=8.8)
    box(ax, 53, 8, 44, 24, "severity wins over schedule", [
        "S1 data loss/crash: release blocker, always.",
        "No 'known issue' framing in release notes without",
        "owner sign-off. Tracker: reports/onedoc-defect-tracker.md"], fc="#F8FAFC", ts=8.8)
    save(fig, "fig-defects.png")


def fig_tokens():
    fig = _nf(12.6, 5.8)
    ax = plt.gca()
    ramps = [("ink", ["#0F172A", "#1E293B", "#334155", "#64748B"]),
             ("teal", ["#134E4A", "#0F766E", "#14B8A6", "#5EEAD4"]),
             ("amber", ["#92400E", "#D97706", "#F59E0B", "#FDE68A"]),
             ("paper", ["#FFFFFF", "#F8FAFC", "#F1F5F9", "#E2E8F0"])]
    for r, (name, cols) in enumerate(ramps):
        for i, c in enumerate(cols):
            ax.add_patch(FancyBboxPatch((4 + r * 24, 62 - i * 8), 20, 7,
                         boxstyle="round,pad=0.2", fc=c, ec=LINE))
            ax.text(14 + r * 24, 58.5 - i * 8, c, ha="center", va="center", fontsize=7.6,
                    color="white" if i < 2 else INK)
        ax.text(14 + r * 24, 96, name, ha="center", fontsize=9.6, color=INK, fontweight="bold")
    box(ax, 4, 6, 44, 30, "typography (Inter · system fallback)", [
        "display 28/34 bold · title 22/28 · h1 20/26 · h2 17/24",
        "body 15/22 (editor default) · caption 12/16 · code 13/18",
        "editor body min 14 sp; a11y scaling to 200% must not clip"], fc="#F8FAFC", ts=8.8)
    box(ax, 52, 6, 44, 30, "shape · space · motion", [
        "radius: s 8 · m 12 · l 16 · sheet 28 dp",
        "space grid 4 dp: 4/8/12/16/24/32",
        "motion: 150 ms enter · 200 ms move · 250 ms sheet;",
        "haptics: tick on mark toggle, confirm on insert"], fc="#F8FAFC", ts=8.8)
    save(fig, "fig-tokens.png")


def fig_navigation():
    fig = _nf(12.2, 5.6)
    ax = plt.gca()
    box(ax, 42, 40, 16, 16, "home", ["library"], fc="#0F172A", ts=10)
    tops = [("templates", 8, 72), ("assistant", 30, 78), ("settings", 72, 78)]
    for t, x, y in tops:
        box(ax, x, y - 5, 18, 11, t, [], fc="#1E293B", ts=9.4)
        arrow(ax, 50, 56.4, x + 9 if x < 50 else x, y + 6.4)
    box(ax, 8, 8, 22, 13, "editor", ["full-screen, owns back"], fc="#134E4A", ts=9.6)
    box(ax, 39, 8, 22, 13, "search results", ["snippet + count"], fc="#1E293B", ts=9.2)
    box(ax, 70, 8, 22, 13, "sheets", ["export · versions · info"], fc="#1E293B", ts=8.8)
    arrow(ax, 46, 39.6, 22, 21.4)
    arrow(ax, 52, 39.6, 50, 21.4)
    arrow(ax, 55, 44, 71, 21.4)
    ax.add_patch(FancyBboxPatch((6, 25.5), 88, 7, boxstyle="round,pad=0.3", fc="#F8FAFC", ec=LINE))
    ax.text(50, 29, "rules N1–N5 (§3.2): back always sane · editor has no bottom nav · search deep-links to the hit block · every screen ≤ 2 taps from home",
            ha="center", va="center", fontsize=8.4, color=INK)
    legend_note(ax := plt.gca(), 6, 1, "Navigation graph (normative). Dashed behaviors are system-driven; all arrows are in-app, offline.")
    save(fig, "fig-navigation.png")


def main():
    fig_cover(); fig_product_map(); fig_home_wireframe(); fig_editor_wireframe()
    fig_figma_workflow(); fig_architecture(); fig_docmodel(); fig_erd()
    fig_formats(); fig_ai_stack(); fig_ai_ladder(); fig_versioning()
    fig_testing(); fig_gates(); fig_defects(); fig_tokens(); fig_navigation()


if __name__ == "__main__":
    main()
