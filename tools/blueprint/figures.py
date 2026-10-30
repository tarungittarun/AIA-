#!/usr/bin/env python3
"""Generates all figures (diagrams, wireframes, cover art) for the blueprint.

Run:  .venv/bin/python tools/blueprint/figures.py
Out:  docs/blueprint/figures/*.png
"""
import os
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Circle, Wedge, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "docs", "blueprint", "figures")
os.makedirs(OUT, exist_ok=True)

INK = "#0F172A"; SLATE = "#334155"; MUTE = "#64748B"; TEAL = "#0F766E"
TEAL_L = "#CCFBF1"; TEAL_DARK = "#115E59"; AMBER = "#B45309"; AMBER_L = "#FEF3C7"; LIGHT = "#E2E8F0"
FILL = "#F1F5F9"; LINE = "#94A3B8"; DARK = "#0B1220"; WHITE = "#FFFFFF"
BLUE = "#1D4ED8"; BLUE_L = "#DBEAFE"; ROSE = "#BE123C"; ROSE_L = "#FFE4E6"
VIOLET = "#6D28D9"; VIOLET_L = "#EDE9FE"

plt.rcParams["font.family"] = "DejaVu Sans"


def newfig(w, h, bg=WHITE):
    fig, ax = plt.subplots(figsize=(w, h), dpi=170)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100 * h / w)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, title, lines=(), fc=FILL, ec=LINE, tc=INK, ts=10, fs=8,
        title_weight="bold", lw=1.1, radius=1.2, align="center"):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0,rounding_size=%s" % radius,
                 fc=fc, ec=ec, lw=lw, zorder=3))
    cy = y + h - 1.9
    if align == "center":
        ax.text(x + w / 2, cy, title, ha="center", va="center", fontsize=ts,
                fontweight=title_weight, color=tc, zorder=4)
        yy = cy - 2.6
        for ln in lines:
            ax.text(x + w / 2, yy, ln, ha="center", va="center", fontsize=fs,
                    color=SLATE, zorder=4)
            yy -= 2.5
    else:
        ax.text(x + 1.6, cy, title, ha="left", va="center", fontsize=ts,
                fontweight=title_weight, color=tc, zorder=4)
        yy = cy - 2.8
        for ln in lines:
            ax.text(x + 1.6, yy, ln, ha="left", va="center", fontsize=fs,
                    color=SLATE, zorder=4)
            yy -= 2.6


def arrow(ax, x1, y1, x2, y2, color=TEAL, lw=1.6, style="-|>", ms=13, con="arc3,rad=0"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                 mutation_scale=ms, color=color, lw=lw, connectionstyle=con, zorder=2))


def hexagon(ax, cx, cy, r, fc, ec="none", lw=0, alpha=1, zorder=1, rot=0):
    pts = [(cx + r * math.cos(math.radians(60 * k + rot)),
            cy + r * math.sin(math.radians(60 * k + rot))) for k in range(6)]
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=zorder))


def legend_note(ax, x, y, text, color=MUTE, fs=8.2, ha="left"):
    ax.text(x, y, text, fontsize=fs, color=color, ha=ha, va="center", style="italic")


# ----------------------------------------------------------- 1. cover art --
def fig_cover():
    fig, ax = plt.subplots(figsize=(8.27, 11.69), dpi=200)
    fig.patch.set_facecolor(DARK); ax.set_facecolor(DARK)
    W, H = 100, 141.2
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    # dot grid
    for gx in range(4, 100, 6):
        for gy in range(4, 141, 6):
            ax.add_patch(Circle((gx, gy), 0.13, fc="#1E293B", ec="none", zorder=1))
    # honeycomb cluster bottom-right
    r = 7.2
    dx = r * 1.732; dy = r * 1.5
    centers = [(70, 18), (70 + dx, 18 + dy), (70 - dx, 18 + dy), (70, 18 + 2 * dy),
               (70 + dx, 18 - dy), (70 + 2 * dx, 18), (70 - dx, 18 - dy),
               (70 - 2 * dx, 18), (70 + dx, 18 + 3 * dy), (70 - dx, 18 + 3 * dy)]
    alphas = [0.95, 0.55, 0.40, 0.70, 0.30, 0.22, 0.30, 0.18, 0.30, 0.20]
    cols = ["#0F766E", "#115E59", "#134E4A", "#14B8A6", "#0D3B38", "#0D3B38",
            "#115E59", "#0D3B38", "#134E4A", "#0D3B38"]
    for (cx, cy), a, c in zip(centers, alphas, cols):
        hexagon(ax, cx, cy, r - 0.35, c, alpha=a, zorder=2)
    # center emblem hex with calc glyph
    hexagon(ax, 70, 18 + dy, r - 2.4, "#134E4A", ec="#5EEAD4", lw=2.2, alpha=1, zorder=5)
    ax.text(70, 18 + dy, "1+2", color="#5EEAD4", fontsize=17, fontweight="bold",
            ha="center", va="center", zorder=6)
    # faint glow arc
    ax.add_patch(Wedge((70, 20), 42, 15, 75, width=0.7, fc="#14B8A6", alpha=0.35, zorder=2))
    ax.text(4, 136, "MYSPACE ONE", color="#5EEAD4", fontsize=15, fontweight="bold",
            ha="left", va="center", zorder=6)
    ax.plot([4, 30], [133.6, 133.6], color="#14B8A6", lw=1.6, zorder=6)
    fig.savefig(os.path.join(OUT, "cover.png"), bbox_inches=None, pad_inches=0)
    plt.close(fig)


# ------------------------------------------------------- 2. module map ----
def fig_modules():
    fig, ax = newfig(10.4, 6.0)
    H = 100 * 6.0 / 10.4
    cx, cy = 50, H / 2 + 4
    hexagon(ax, cx, cy, 15.5, TEAL_L, ec=TEAL, lw=2.0, zorder=2)
    hexagon(ax, cx, cy, 13.2, WHITE, ec=TEAL, lw=1.0, zorder=3)
    ax.text(cx, cy + 2.2, "MySpace One", ha="center", fontsize=13.5, fontweight="bold", color=INK, zorder=5)
    ax.text(cx, cy - 1.6, "one app · one home", ha="center", fontsize=8.6, color=MUTE, zorder=5)
    ax.text(cx, cy - 4.6, "app.space.one", ha="center", fontsize=8.0, color=TEAL, zorder=5,
            family="DejaVu Sans Mono")
    mods = [
        ("Calculator", "basic · scientific · history", -1),
        ("MyCalc flavor", "standalone calculator build", 0),
        ("Notes", "rich text · search · AI summary", 1),
        ("Scanner", "camera · OCR → text/notes", 2),
        ("Calendar", "events · reminders · ICS", 3),
        ("Files", "private + SAF · analyzer", 4),
        ("Music", "offline player · queue", 5),
        ("Recorder", "audio · markers · transcript", 6),
        ("Diagnostics", "logs · health · model packs", 7),
    ]
    import numpy as np
    for i, (t, s, k) in enumerate(mods):
        ang = math.pi / 2 - i * (2 * math.pi / len(mods)) - 0.28
        mx = cx + 36 * math.cos(ang); my = cy + 25.5 * math.sin(ang)
        box(ax, mx - 12.5, my - 5.4, 25, 10.8, t, (s,), fc=WHITE, ec=SLATE, ts=9.6, fs=7.6)
        arrow(ax, cx + 15 * math.cos(ang), cy + 12 * math.sin(ang),
              mx - 11 * math.cos(ang), my - 4 * math.sin(ang), color=LINE, lw=1.2, ms=9)
    box(ax, 8, 1.6, 84, 8.6, "On-device AI layer — OCR · speech-to-text · TTS · embeddings · small LLM assistant",
        ("all models local · optional side-loaded packs · zero network sockets in app code",
         "AI assists features; every feature fully usable with AI disabled or absent"),
        fc=DARK, ec=TEAL, tc="#E2E8F0", ts=9.4, fs=7.6)
    for lx in (14, 34, 54, 74, 90):
        arrow(ax, lx, 10.4, lx, 12.6, color=TEAL, lw=1.3, ms=9)
    legend_note(ax, 8.5, H - 2.4, "Combined-app product map: eight user modules around one hub, one shared AI layer, no cloud services.")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig-module-map.png"), bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------- 3. layered architecture --
def fig_architecture():
    fig, ax = newfig(10.6, 6.4)
    H = 100 * 6.4 / 10.6
    bands = [
        ("UI — Jetpack Compose", ["Calculator screens", "Notes", "Scanner", "Calendar", "Files", "Music", "Recorder", "Diagnostics", "Hub / Home"], "#E0F2FE", "#0369A1"),
        ("Feature — state + use-cases", ["ViewModels", "navigation", "permission flows", "feature contracts"], TEAL_L, TEAL),
        ("Core domain", ["calc engine (exact + fast path)", "notes rich-text model", "recurrence engine", "search index", "media controllers"], VIOLET_L, VIOLET),
        ("Data", ["Room DB (+FTS)", "DataStore prefs", "SAF documents", "MediaStore", "encrypted exports"], BLUE_L, BLUE),
        ("AI runtime", ["ONNX Runtime Mobile", "TFLite", "whisper.cpp (JNI)", "MediaPipe LLM", "system TTS"], AMBER_L, AMBER),
        ("Android platform", ["CameraX", "AudioRecord", "Media3", "AlarmManager", "WorkManager", "Keystore"], FILL, SLATE),
    ]
    y = H - 3
    bh = (H - 12) / len(bands)
    for name, items, fc, ec in bands:
        box(ax, 4, y - bh + 1.4, 79, bh - 2.2, name, tuple(items), fc=fc, ec=ec, ts=10.5, fs=7.7)
        y -= bh
    box(ax, 86, H - 3 - bh + 1.4, 12, 2 * bh - 4.4, "Design\ntokens\n+ a11y", (), fc=WHITE, ec=SLATE, ts=8.6)
    box(ax, 86, H - 3 - 3 * bh + 1.4, 12, 2 * bh - 4.4, "Diagnostics\n+ local logs\n(offline)", (), fc=WHITE, ec=SLATE, ts=8.6)
    box(ax, 86, H - 3 - 5 * bh + 1.4, 12, 2 * bh - 4.4, "Tests:\nunit · UI ·\ndevice QA", (), fc=WHITE, ec=SLATE, ts=8.6)
    for i in range(5):
        arrow(ax, 43.5, H - 3 - (i + 1) * bh + 1.6, 43.5, H - 3 - (i + 1) * bh - 0.6, color=SLATE, lw=1.4, ms=10)
    legend_note(ax, 4, 2.0, "Unidirectional dependencies: each layer may only call the layer directly below it. The AI runtime is a leaf — no feature code inside it.")
    fig.savefig(os.path.join(OUT, "fig-architecture.png"), bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------ 4. navigation map --
def fig_navigation():
    fig, ax = newfig(10.6, 5.6)
    H = 100 * 5.6 / 10.6
    hub = (50, H / 2 + 1)
    box(ax, hub[0] - 13, hub[1] - 5, 26, 10, "Hub — Home", ("module grid · search · continue",),
        fc=TEAL_L, ec=TEAL, ts=10.5, fs=7.6)
    nodes = [
        ("Calculator", ("keypad · scientific", "history · memory"), (8, H - 12)),
        ("Notes", ("list · editor", "search · AI actions"), (8, H / 2 - 1)),
        ("Scanner", ("camera · OCR", "export → Notes"), (8, 4)),
        ("Calendar", ("month · agenda", "reminders"), (37, H - 12)),
        ("Files", ("internal + SAF", "storage analyzer"), (37, 4)),
        ("Music", ("library · queue", "now playing"), (66, H - 12)),
        ("Recorder", ("record · markers", "transcribe (opt)"), (66, 4)),
        ("Diagnostics", ("health · logs", "model packs"), (87, H / 2 - 1)),
        ("Settings", ("themes · a11y", "backup · about"), (87, H - 12)),
        ("MyCalc entry", ("flavor: standalone", "calc-only home"), (37, H / 2 - 1)),
    ]
    for t, lines, (x, y) in nodes:
        box(ax, x - 9.5, y - 5.4, 19, 11.2, t, lines, fc=WHITE, ec=SLATE, ts=8.8, fs=7.2)
        arrow(ax, hub[0], hub[1], x, y + (5.6 if y > hub[1] else -5.6), color=LINE, lw=1.1, ms=9)
    arrow(ax, 17.5, H / 2 - 1, 27.5, H / 2 - 1, color=AMBER, lw=1.4)
    legend_note(ax, 4, 1.6, "Every screen is reachable in ≤ 2 taps from the Hub. Back always returns to the previous screen; state survives process death.")
    fig.savefig(os.path.join(OUT, "fig-navigation.png"), bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------- wireframe helpers --
def phone(ax, x, y, w, h, title=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=2.6",
                 fc=WHITE, ec=INK, lw=2.0, zorder=3))
    ax.add_patch(FancyBboxPatch((x + w * 0.36, y + h - 2.1), w * 0.28, 0.9,
                 boxstyle="round,pad=0,rounding_size=0.45", fc=INK, ec="none", zorder=4))
    if title:
        ax.text(x + w / 2, y + h + 1.8, title, ha="center", fontsize=9.6,
                fontweight="bold", color=SLATE, zorder=6)


def ui_appbar(ax, x, y, w, title, right=()):
    ax.add_patch(Rectangle((x + 0.8, y), w - 1.6, 5.2, fc=TEAL, ec="none", zorder=4))
    ax.text(x + 2.4, y + 2.6, title, fontsize=8.6, color=WHITE, fontweight="bold",
            va="center", zorder=5)
    for k, r in enumerate(right):
        ax.text(x + w - 2.2 - k * 5.4, y + 2.6, r, fontsize=7.4, color=WHITE,
                va="center", ha="center", zorder=5)


def ui_key(ax, x, y, w, h, label, fc=WHITE, tc=INK, fs=9, ec=LIGHT, op="+"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8",
                 fc=fc, ec=ec, lw=0.8, zorder=5))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold", zorder=6)


def ui_row(ax, x, y, w, h, text, icon="▤", fc=WHITE, fs=7.8, tc=INK, ec=LIGHT, iconc=TEAL):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.7",
                 fc=fc, ec=ec, lw=0.8, zorder=4))
    ax.text(x + 2.2, y + h / 2, icon, fontsize=fs + 1.5, color=iconc, va="center", zorder=5)
    ax.text(x + 6.2, y + h / 2, text, fontsize=fs, color=tc, va="center", zorder=5)


def ui_chip(ax, x, y, w, h, text, fc=AMBER_L, tc=AMBER, fs=7.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=%s" % (h / 2),
                 fc=fc, ec="none", zorder=6))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold", zorder=7)


def ui_bar(ax, x, y, w, h, label, pct=0.7, fc=FILL, barc=TEAL):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.5",
                 fc=fc, ec=LIGHT, lw=0.7, zorder=4))
    ax.add_patch(FancyBboxPatch((x + 0.5, y + 0.5), (w - 1) * pct, h - 1,
                 boxstyle="round,pad=0,rounding_size=0.4", fc=barc, ec="none", zorder=5))
    ax.text(x + w + 1.5, y + h / 2, label, fontsize=6.8, color=MUTE, va="center", zorder=5)


# ------------------------------------------------- 5. calculator screens --
def fig_calc():
    fig, ax = newfig(10.6, 5.9)
    H = 100 * 5.9 / 10.6
    # phone 1: basic calculator with selection UI
    x, y, w, h = 4, H - 42, 25, 40
    phone(ax, x, y, w, h, "Calculator · basic pad")
    ui_appbar(ax, x, y + h - 7.5, w, "Calculator", right=("⌂", "⋮"))
    ax.text(x + 1.8, y + h - 12.0, "3+4×(2+1)", fontsize=11.5, color=INK,
            family="DejaVu Sans Mono", zorder=5)
    ax.add_patch(Rectangle((x + 6.6, y + h - 12.9), 0.55, 1.5, fc=TEAL, ec="none", zorder=6))
    ax.text(x + w - 1.8, y + h - 16.2, "15", fontsize=15.5, color=AMBER, ha="right",
            fontweight="bold", zorder=5)
    ax.text(x + 1.8, y + h - 16.2, "live answer", fontsize=6.6, color=MUTE, zorder=5)
    keys = [["AC", "( )", "%", "÷"], ["7", "8", "9", "×"], ["4", "5", "6", "−"],
            ["1", "2", "3", "+"], ["0", ".", "⌫", "="]]
    gx, gy = x + 1.6, y + 1.8
    kw = (w - 3.2 - 0.6) / 4; kh = 4.35
    for r, row in enumerate(keys):
        for c, k in enumerate(row):
            fc = "#FDE68A" if k == "=" else (FILL if c == 3 else WHITE)
            tc = AMBER if k == "=" else (TEAL if c == 3 else INK)
            ui_key(ax, gx + c * (kw + 0.6), gy + (4 - r) * (kh + 0.6), kw, kh, k, fc=fc, tc=tc, fs=8.6)
    ui_chip(ax, x + 2.4, y + h - 21.6, w - 4.8, 3.2, "Cut   Copy   MAdd   MUse   Paste")
    ax.text(x + 1.6, y + h - 24.4, "selection pill on long-press (B1)", fontsize=6.4,
            color=MUTE, zorder=5, style="italic")
    # phone 2: scientific
    x2 = x + w + 8
    phone(ax, x2, y, w, h, "Scientific panel (swipe left / INV)")
    ui_appbar(ax, x2, y + h - 7.5, w, "Calculator", right=("⌂", "⋮"))
    sci = [["INV", "sin", "cos", "tan"], ["π", "e", "^", "√"], ["ln", "log", "!", "÷"],
           ["7", "8", "9", "×"], ["4", "5", "6", "−"], ["1", "2", "3", "+"],
           ["0", ".", "⌫", "="]]
    gy2 = y + 1.6; kh2 = (h - 10.5 - 7 * 0.5) / 7
    kw2 = (w - 3.2 - 0.6) / 4
    for r, row in enumerate(sci):
        for c, k in enumerate(row):
            fc = "#FDE68A" if k == "=" else (FILL if c == 3 else WHITE)
            tc = AMBER if k == "=" else (TEAL if c == 3 else INK)
            ui_key(ax, x2 + 1.6 + c * (kw2 + 0.6), gy2 + (6 - r) * (kh2 + 0.5), kw2, kh2, k, fc=fc, tc=tc, fs=7.6)
    # annotations
    box(ax, x2 + w + 5, H - 20, 28, 15, "Engine contract (§17)",
        ("exact rationals + DECIMAL128", "percent: 200+10% = 220", "implicit ×: 2(5+2) = 28", "chained ops use full precision"),
        fc=WHITE, ec=AMBER, ts=9.2, fs=7.6)
    box(ax, x2 + w + 5, H - 38, 28, 15, "Persistence (§12, §18)",
        ("history row on every ‘=’", "survives restart (TC-07)", "newest on top, replay card", "memory MAdd / MUse slots"),
        fc=WHITE, ec=AMBER, ts=9.2, fs=7.6)
    legend_note(ax, 4, 2.2, "Calculator UI: one pad, two panels; caret, live answer, selection pill and history are first-class, tested behaviors.")
    fig.savefig(os.path.join(OUT, "fig-calc-wireframe.png"), bbox_inches="tight")
    plt.close(fig)


def fig_calc_panels():
    fig, ax = newfig(10.6, 3.6)
    H = 100 * 3.6 / 10.6
    # history sheet
    x, y, w, h = 4, H - 30, 28, 28
    phone(ax, x, y, w, h, "History sheet (newest on top)")
    ui_appbar(ax, x, y + h - 6.6, w, "History · 8", right=("✕",))
    rows = ["= 220      200+10%", "= 0.3      0.1+0.2", "= 20      (2+3)×4",
            "= 14      2+3×4", "= 10       5+5"]
    for k, rtext in enumerate(rows):
        ui_row(ax, x + 1.6, y + h - 11.6 - k * 3.4, w - 3.2, 2.9, rtext, icon="≡", fs=7.0)
    # memory sheet
    x2 = x + w + 8
    phone(ax, x2, y, w, h, "Memory popup (3-dot → Memory)")
    ui_appbar(ax, x2, y + h - 6.6, w, "Memory", right=("✕",))
    ui_row(ax, x2 + 1.6, y + h - 11.8, w - 3.2, 3.4, "1,23,456", icon="M", fs=8.2)
    for k, act in enumerate(["MUse — insert at caret", "MAdd — add to slot", "MC — clear slot"]):
        ui_chip(ax, x2 + 2.2, y + h - 17.4 - k * 4.0, w - 4.4, 3.0, act, fc=TEAL_L, tc=TEAL_DARK, fs=7.0)
    # theme picker
    x3 = x2 + w + 8
    phone(ax, x3, y, w, h, "Key theme picker (8 themes)")
    ui_appbar(ax, x3, y + h - 6.6, w, "Key theme", right=("✕",))
    themes = [("MySpace settings", TEAL), ("Graphite", SLATE), ("Ocean", BLUE),
              ("Sunset", "#EA580C"), ("Mint", "#059669"), ("Rose", "#E11D48"),
              ("Lemon", "#CA8A04"), ("Iris", VIOLET)]
    for k, (t, c) in enumerate(themes):
        col = k % 2; row = k // 2
        bx = x3 + 1.8 + col * (w / 2 - 1.2); by = y + h - 12.4 - row * 3.6
        ax.add_patch(FancyBboxPatch((bx, by), w / 2 - 2.4, 3.0,
                     boxstyle="round,pad=0,rounding_size=0.6", fc=WHITE, ec=LIGHT, lw=0.8, zorder=5))
        ax.add_patch(Circle((bx + 2.0, by + 1.5), 0.85, fc=c, ec="none", zorder=6))
        ax.text(bx + 3.6, by + 1.5, t, fontsize=5.6, color=INK, va="center", zorder=6)
    ui_chip(ax, x3 + 2.0, y + 2.0, w - 4, 3.0, "selected: Rose → keys repaint instantly", fs=6.4)
    legend_note(ax, 4, 2.0, "Secondary calculator surfaces: history replay, memory slots (MAdd/MUse), key themes — all specified as testable behaviors (TC-ONE-…).")
    fig.savefig(os.path.join(OUT, "fig-calc-panels.png"), bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------- 6. notes screens --
def fig_notes():
    fig, ax = newfig(10.6, 3.9)
    H = 100 * 3.9 / 10.6
    x, y, w, h = 4, H - 32, 27, 30
    phone(ax, x, y, w, h, "Notes — list")
    ui_appbar(ax, x, y + h - 7.0, w, "Notes", right=("◍", "⋮"))
    ui_row(ax, x + 1.6, y + h - 12.2, w - 3.2, 4.0, "Field survey notes", icon="▤")
    ui_row(ax, x + 1.6, y + h - 17.0, w - 3.2, 4.0, "Groceries (checklist)", icon="☑")
    ui_row(ax, x + 1.6, y + h - 21.8, w - 3.2, 4.0, "Meeting — 27 Oct", icon="▤")
    ui_row(ax, x + 1.6, y + h - 26.6, w - 3.2, 4.0, "Scan: receipt #118", icon="▦", iconc=BLUE)
    ui_key(ax, x + w - 8.5, y + 2.0, 6.4, 5.6, "+ ", fc=TEAL, tc=WHITE, fs=10, ec="none")
    x2 = x + w + 8
    phone(ax, x2, y, w, h, "Notes — editor")
    ui_appbar(ax, x2, y + h - 7.0, w, "Groceries", right=("✓", "⋮"))
    ax.text(x2 + 1.8, y + h - 11.6, "☑ Milk    ☑ Rice    ☐ Turmeric", fontsize=7.6,
            color=INK, family="DejaVu Sans Mono", zorder=5)
    ax.text(x2 + 1.8, y + h - 15.0, "**bold**, *italic*, — lists —", fontsize=7.2,
            color=MUTE, zorder=5)
    ax.add_patch(Rectangle((x2 + 1.8, y + h - 17.2), 24.6, 8.6, fc=FILL, ec=LIGHT,
                 lw=0.8, zorder=4))
    ax.text(x2 + 2.8, y + h - 18.6, "AI (on-device) ▸", fontsize=6.6, color=AMBER,
            fontweight="bold", zorder=5)
    ax.text(x2 + 2.8, y + h - 21.4, "Summarize · Rewrite · Checklist-ify · Find related",
            fontsize=6.4, color=SLATE, zorder=5)
    for k, t in enumerate(["B", "I", "H1", "•", "☑", "―"]):
        ui_key(ax, x2 + 1.6 + k * 4.2, y + 2.2, 3.6, 3.6, t, fc=FILL, fs=7.0)
    legend_note(ax, 4, 2.0, "Notes: plain-file-friendly rich text, full-text + semantic search, optional on-device AI actions that never modify a note without preview/undo.")
    fig.savefig(os.path.join(OUT, "fig-notes-wireframe.png"), bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------- 7. scanner screen --
def fig_scanner():
    fig, ax = newfig(10.6, 3.9)
    H = 100 * 3.9 / 10.6
    x, y, w, h = 4, H - 32, 27, 30
    phone(ax, x, y, w, h, "Scanner — viewfinder (CameraX)")
    ax.add_patch(Rectangle((x + 1.4, y + h - 27.6), w - 2.8, 19.4, fc="#0F172A", ec="none", zorder=4))
    for cx, cy, sx, sy in [(x + 3.0, y + h - 10.0, 1, 1), (x + w - 3.0, y + h - 10.0, -1, 1),
                           (x + 3.0, y + h - 25.8, 1, -1), (x + w - 3.0, y + h - 25.8, -1, -1)]:
        ax.plot([cx, cx + 2.2 * sx], [cy, cy], color="#5EEAD4", lw=2.2, zorder=6)
        ax.plot([cx, cx], [cy, cy + 2.2 * sy], color="#5EEAD4", lw=2.2, zorder=6)
    ax.text(x + w / 2, y + h - 17.8, "document", fontsize=7.4, color="#94A3B8",
            ha="center", zorder=5)
    for k, t in enumerate(["Scan", "Batch", "Import"]):
        ui_key(ax, x + 2.0 + k * 8.0, y + 2.0, 7.0, 3.8, t, fc=FILL, fs=7.2)
    x2 = x + w + 8
    phone(ax, x2, y, w, h, "Scan result — OCR card")
    ui_appbar(ax, x2, y + h - 7.0, w, "Scan · page 1", right=("✓", "⋮"))
    ax.add_patch(Rectangle((x2 + 1.6, y + h - 18.0), w - 3.2, 9.4, fc=FILL, ec=LIGHT, lw=0.8, zorder=4))
    ax.text(x2 + 2.6, y + h - 19.4, "recognized text", fontsize=6.4, color=MUTE, zorder=5)
    for k, ln in enumerate(["INVOICE #118", "2 × USB-C cable    1,350", "TOTAL                    1,350"]):
        ax.text(x2 + 2.6, y + h - 22.2 - k * 2.6, ln, fontsize=6.8, color=INK,
                family="DejaVu Sans Mono", zorder=5)
    for k, t in enumerate(["Copy", "→ Notes", "Re-OCR", "Delete"]):
        ui_key(ax, x2 + 1.6 + k * 6.2, y + 6.6, 5.6, 3.6, t, fc=TEAL_L, tc=TEAL_DARK, fs=6.4)
    ax.text(x2 + 1.6, y + 4.4, "OCR model runs on-device; image never leaves the phone",
            fontsize=6.0, color=MUTE, style="italic", zorder=5)
    legend_note(ax, 4, 2.0, "Scanner pipeline: CameraX capture → crop/rotate → on-device OCR (det+rec) → editable text card → Notes/Copy. Works fully offline.")
    fig.savefig(os.path.join(OUT, "fig-scanner-wireframe.png"), bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------- 8. calendar screen --
def fig_calendar():
    fig, ax = newfig(10.6, 3.9)
    H = 100 * 3.9 / 10.6
    x, y, w, h = 4, H - 32, 27, 30
    phone(ax, x, y, w, h, "Calendar — month + agenda")
    ui_appbar(ax, x, y + h - 7.0, w, "October 2026", right=("‹", "›", "⋮"))
    gx, gy = x + 1.6, y + h - 19.6
    cw = (w - 3.2) / 7
    for k, d in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
        ax.text(gx + k * cw + cw / 2, gy + 2.2, d, fontsize=6.4, color=MUTE, ha="center", zorder=5)
    import datetime
    first = datetime.date(2026, 10, 1).weekday()
    for day in range(1, 32):
        pos = first + day - 1
        r, c = divmod(pos, 7)
        cx0 = gx + c * cw; cy0 = gy - r * 3.0
        today = day == 31
        if today:
            ax.add_patch(Circle((cx0 + cw / 2, cy0 + 0.9), 1.15, fc=TEAL, ec="none", zorder=6))
        ax.text(cx0 + cw / 2, cy0 + 0.9, str(day), fontsize=6.2, ha="center",
                va="center", color=WHITE if today else INK, zorder=7)
        if day in (27, 12, 20):
            ax.add_patch(Circle((cx0 + cw / 2, cy0 - 0.7), 0.35, fc=AMBER, ec="none", zorder=6))
    ui_row(ax, x + 1.6, y + 2.2, w - 3.2, 3.0, "27 Oct · 13:36 — Rent reminder", icon="●", fs=6.6)
    x2 = x + w + 8
    phone(ax, x2, y, w, h, "Event editor")
    ui_appbar(ax, x2, y + h - 7.0, w, "New event", right=("✓", "✕"))
    for k, (t, v) in enumerate([("Title", "Rent reminder"), ("Date", "27 Oct 2026"),
                                ("Time", "13:36"), ("Repeat", "Monthly (RRULE)"),
                                ("Alert", "15 min before")]):
        ui_row(ax, x2 + 1.6, y + h - 13.2 - k * 4.2, w - 3.2, 3.6, v, icon="▸", fs=7.2)
        ax.text(x2 + 3.0, y + h - 13.2 - k * 4.2 + 3.6, t.upper(), fontsize=5.0,
                color=MUTE, zorder=5)
    ui_chip(ax, x2 + 1.6, y + 2.2, w - 3.2, 3.2, "Saves locally · exact alarm reminder · ICS export", fs=6.2)
    legend_note(ax, 4, 2.0, "Calendar: local-first events with recurrence (supported RRULE subset), exact-alarm reminders, ICS import/export through Files.")
    fig.savefig(os.path.join(OUT, "fig-calendar-wireframe.png"), bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------- 9. files screen --
def fig_files():
    fig, ax = newfig(10.6, 3.9)
    H = 100 * 3.9 / 10.6
    x, y, w, h = 4, H - 32, 27, 30
    phone(ax, x, y, w, h, "Files — browser")
    ui_appbar(ax, x, y + h - 7.0, w, "Files", right=("◍", "⋮"))
    ax.text(x + 1.8, y + h - 10.2, "MySpace One ▸ Notes attachments ▸", fontsize=6.4,
            color=TEAL, zorder=5, family="DejaVu Sans Mono")
    for k, (t, meta, ic) in enumerate([("receipt-118.png", "82 KB · OCR'd", "▦"),
                                       ("survey-notes.md", "3 KB", "▤"),
                                       ("recordings/", "12 items", "▸"),
                                       ("export-2026.zip", "1.1 MB · encrypted", "◼")]):
        ui_row(ax, x + 1.6, y + h - 15.6 - k * 4.0, w - 3.2, 3.6, "%s   ·   %s" % (t, meta), icon=ic, fs=7.0)
    for k, t in enumerate(["Sort", "New folder", "Move"]):
        ui_key(ax, x + 1.6 + k * 8.2, y + 2.0, 7.4, 3.6, t, fc=FILL, fs=6.8)
    x2 = x + w + 8
    phone(ax, x2, y, w, h, "Storage analyzer")
    ui_appbar(ax, x2, y + h - 7.0, w, "Storage", right=("✕",))
    cxr, cyr = x2 + w / 2, y + h - 14.5
    ax.add_patch(Wedge((cxr, cyr), 6.4, 0, 300, width=2.6, fc=TEAL, ec="none", zorder=5))
    ax.add_patch(Wedge((cxr, cyr), 6.4, 300, 336, width=2.6, fc=AMBER, ec="none", zorder=5))
    ax.add_patch(Wedge((cxr, cyr), 6.4, 336, 360, width=2.6, fc=LIGHT, ec="none", zorder=5))
    ax.text(cxr, cyr, "31%", fontsize=9, ha="center", va="center", fontweight="bold", color=INK, zorder=6)
    for k, (lab, c) in enumerate([("Scans 38%", TEAL), ("Audio 7%", AMBER), ("Free 62%", LIGHT)]):
        ax.add_patch(Circle((x2 + 4.5 + k * 8.0, y + h - 23.4), 0.8, fc=c, ec="none", zorder=5))
        ax.text(x2 + 6.0 + k * 8.0, y + h - 23.4, lab, fontsize=6.2, color=SLATE, va="center", zorder=5)
    for k, t in enumerate(["Clean scans", "Export report"]):
        ui_key(ax, x2 + 1.8 + k * 12.4, y + 3.0, 11.2, 3.8, t, fc=TEAL_L, tc=TEAL_DARK, fs=6.8)
    legend_note(ax, 4, 2.0, "Files: app-private storage plus user-granted SAF roots; storage analyzer computes sizes locally; exports are checksummed, optionally encrypted.")
    fig.savefig(os.path.join(OUT, "fig-files-wireframe.png"), bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------- 10. music screen --
def fig_music():
    fig, ax = newfig(10.6, 3.9)
    H = 100 * 3.9 / 10.6
    x, y, w, h = 4, H - 32, 27, 30
    phone(ax, x, y, w, h, "Music — library")
    ui_appbar(ax, x, y + h - 7.0, w, "Music", right=("◍", "⋮"))
    for k, t in enumerate(["Albums", "Artists", "Songs", "Folders", "Playlists"]):
        ui_chip(ax, x + 1.6 + k * 4.9, y + h - 10.4, 4.5, 2.8, t, fs=5.2,
                fc=TEAL_L if k == 2 else FILL, tc=TEAL_DARK if k == 2 else SLATE)
    for k, (t, m) in enumerate([("Morning drive", "8 songs · 26 min"),
                                ("Focus loop", "12 songs · 51 min"),
                                ("Road trip 2026", "23 songs · 94 min")]):
        ui_row(ax, x + 1.6, y + h - 15.4 - k * 4.4, w - 3.2, 3.8, t, icon="▶", fs=7.4)
        ax.text(x + 6.2, y + h - 17.4 - k * 4.4, m, fontsize=5.8, color=MUTE, zorder=5)
    x2 = x + w + 8
    phone(ax, x2, y, w, h, "Now playing")
    ax.add_patch(Rectangle((x2 + 2.4, y + h - 16.4), w - 4.8, 7.6, fc=FILL, ec=LIGHT, lw=0.8, zorder=4))
    ax.text(x2 + w / 2, y + h - 12.6, "♪ artwork", fontsize=7.6, color=MUTE, ha="center", zorder=5)
    ax.text(x2 + 2.4, y + h - 19.4, "Weightless — Marconi Union", fontsize=7.4, color=INK,
            fontweight="bold", zorder=5)
    ui_bar(ax, x2 + 2.4, y + h - 22.4, w - 7.4, 1.2, "1:12 / 8:06", pct=0.15)
    for k, t in enumerate(["◁◁", "▶", "▷▷"]):
        ui_key(ax, x2 + w / 2 - 6.4 + k * 4.6, y + 8.4, 4.0, 4.0, t, fc=TEAL if t == "▶" else FILL,
               tc=WHITE if t == "▶" else INK, fs=8.0)
    ui_chip(ax, x2 + 2.4, y + 3.6, w - 4.8, 3.0, "speed 1.0× · sleep timer off · gapless on", fs=6.2)
    legend_note(ax, 4, 2.0, "Music: MediaStore/Folder import, playlists, queue, playback speed, sleep timer; Media3 session integrates with headset controls — all offline.")
    fig.savefig(os.path.join(OUT, "fig-music-wireframe.png"), bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------- 11. recorder screen --
def fig_recorder():
    fig, ax = newfig(10.6, 3.9)
    H = 100 * 3.9 / 10.6
    x, y, w, h = 4, H - 32, 27, 30
    phone(ax, x, y, w, h, "Recorder — recording")
    ui_appbar(ax, x, y + h - 7.0, w, "Recorder", right=("✎",))
    ax.add_patch(Rectangle((x + 1.6, y + h - 18.2), w - 3.2, 9.4, fc=DARK, ec="none", zorder=4))
    import numpy as np
    rng = np.random.default_rng(7)
    tspace = np.linspace(0, w - 6, 60)
    wave = np.abs(np.sin(tspace * 1.3)) * rng.uniform(0.3, 1.0, 60) + 0.15
    for k in range(60):
        ax.plot([x + 3 + tspace[k], x + 3 + tspace[k]],
                [y + h - 13.5 - wave[k] * 3.6, y + h - 13.5 + wave[k] * 3.6],
                color="#2DD4BF", lw=1.0, zorder=5)
    ax.text(x + 2.6, y + h - 10.4, "00:41:27 ● REC", fontsize=7.4, color="#F87171",
            family="DejaVu Sans Mono", fontweight="bold", zorder=6)
    ui_row(ax, x + 1.6, y + h - 22.6, w - 3.2, 3.2, "Marker 00:12 — action item", icon="⚑", fs=6.8)
    ui_row(ax, x + 1.6, y + h - 26.2, w - 3.2, 3.2, "Marker 00:38 — question", icon="⚑", fs=6.8)
    for k, t in enumerate(["Pause", "Flag", "Done"]):
        ui_key(ax, x + 1.8 + k * 8.2, y + 2.2, 7.4, 3.8, t, fc=TEAL_L, tc=TEAL_DARK, fs=7.0)
    x2 = x + w + 8
    phone(ax, x2, y, w, h, "Saved recording (+ optional transcript)")
    ui_appbar(ax, x2, y + h - 7.0, w, "Standup 27 Oct", right=("⋮",))
    for k, (t, m) in enumerate([("audio.m4a", "41 min · AAC 96 kbps"),
                                ("markers", "2"),
                                ("transcript", "whisper-tiny · done"),
                                ("summary", "gemma-2B · 5 bullets")]):
        ui_row(ax, x2 + 1.6, y + h - 13.0 - k * 4.2, w - 3.2, 3.6, "%s  ·  %s" % (t, m), icon="▸", fs=6.8)
    ui_chip(ax, x2 + 1.6, y + 6.4, w - 3.2, 3.2, "Transcribe/summarize = optional on-device packs", fs=6.0)
    for k, t in enumerate(["Play", "Transcribe", "→ Notes"]):
        ui_key(ax, x2 + 1.6 + k * 8.2, y + 2.0, 7.4, 3.6, t, fc=FILL, fs=6.4)
    legend_note(ax, 4, 2.0, "Recorder: foreground-service capture with pause/resume and markers; transcription and summarization run only if the user installed the AI packs.")
    fig.savefig(os.path.join(OUT, "fig-recorder-wireframe.png"), bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------- 12. diagnostics screen --
def fig_diagnostics():
    fig, ax = newfig(10.6, 3.9)
    H = 100 * 3.9 / 10.6
    x, y, w, h = 4, H - 32, 27, 30
    phone(ax, x, y, w, h, "Diagnostics — health")
    ui_appbar(ax, x, y + h - 7.0, w, "Diagnostics", right=("⋮",))
    cards = [("Storage", "62% free · DB 4.2 MB", TEAL),
             ("Battery", "no wakelock abuse", AMBER),
             ("Database", "integrity OK · v7", BLUE),
             ("AI models", "2 packs installed", VIOLET)]
    for k, (t, s, c) in enumerate(cards):
        r, col = divmod(k, 2)
        bx = x + 1.6 + col * (w / 2 - 1.0); by = y + h - 14.4 - r * 6.2
        ax.add_patch(FancyBboxPatch((bx, by), w / 2 - 2.2, 5.4,
                     boxstyle="round,pad=0,rounding_size=0.8", fc=WHITE, ec=LIGHT, lw=0.9, zorder=5))
        ax.add_patch(Circle((bx + 2.0, by + 4.0), 0.75, fc=c, ec="none", zorder=6))
        ax.text(bx + 3.4, by + 4.0, t, fontsize=6.6, color=INK, fontweight="bold", va="center", zorder=6)
        ax.text(bx + 1.6, by + 1.8, s, fontsize=5.6, color=MUTE, zorder=6)
    for k, t in enumerate(["Run self-test", "Share log (user-initiated)"]):
        ui_key(ax, x + 1.6 + k * 12.4, y + 4.4, 11.4, 3.8, t, fc=FILL, fs=6.2)
    ax.text(x + 1.8, y + 2.4, "no telemetry · logs stay on device until you share them",
            fontsize=5.8, color=MUTE, style="italic", zorder=5)
    x2 = x + w + 8
    phone(ax, x2, y, w, h, "AI model packs")
    ui_appbar(ax, x2, y + h - 7.0, w, "Model packs", right=("✕",))
    packs = [("Essentials (OCR, labels, embeddings)", "installed · SHA ✓", TEAL),
             ("Speech (whisper-tiny int8)", "installed · SHA ✓", TEAL),
             ("Assistant (gemma-2B 4-bit)", "not installed · 1.6 GB", AMBER)]
    for k, (t, s, c) in enumerate(packs):
        ui_row(ax, x2 + 1.6, y + h - 13.4 - k * 5.2, w - 3.2, 4.4, t, icon="▣", fs=6.4)
        ax.text(x2 + 3.4, y + h - 15.4 - k * 5.2, s, fontsize=5.8, color=c, zorder=6)
    ax.text(x2 + 1.8, y + 6.4, "Install = import a pack file from Files.", fontsize=6.0,
            color=SLATE, zorder=5)
    ax.text(x2 + 1.8, y + 4.4, "Integrity: SHA-256 verified before use.", fontsize=6.0,
            color=SLATE, zorder=5)
    ui_key(ax, x2 + 1.8, y + 2.0, w - 3.6, 1.9, "", fc=FILL)
    legend_note(ax, 4, 2.0, "Diagnostics doubles as the model-pack manager: import, verify, enable/disable AI packs; self-test exercises engines and reports results locally.")
    fig.savefig(os.path.join(OUT, "fig-diagnostics-wireframe.png"), bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------- 13. ERD --
def fig_erd():
    fig, ax = newfig(10.8, 6.2)
    H = 100 * 6.2 / 10.8
    def ent(x, y, w, name, fields, fc=WHITE):
        hh = 4.6 + len(fields) * 2.05
        box(ax, x, y - hh, w, hh, name, tuple(fields), fc=fc, ec=SLATE, ts=8.6, fs=6.7, align="left")
        return (x, y - hh, w, hh)
    calc = ent(3, H - 2, 24, "CalcHistory", ["id PK", "expression TEXT", "result TEXT", "createdAt INTEGER", "pinned INTEGER"])
    mem = ent(3, H - 34, 24, "MemorySlot", ["id PK", "value TEXT", "label TEXT", "updatedAt"])
    note = ent(31, H - 2, 26, "Note", ["id PK", "title", "bodyJson", "updatedAt", "pinned", "tagsCsv"])
    notefts = ent(31, H - 26, 26, "NoteFts (FTS4)", ["rowid → Note", "title", "bodyText"], fc=TEAL_L)
    scan = ent(61, H - 2, 26, "ScanDoc", ["id PK", "pageUrisCsv", "ocrText", "createdAt", "noteId FK?"])
    event = ent(3, 24, 26, "CalEvent", ["id PK", "title", "startUtc", "endUtc", "rrule?", "reminderMin", "icsUid?"])
    track = ent(33, 24, 24, "Track", ["id PK", "mediaId", "title", "artist", "album", "durationMs", "uri"])
    playlist = ent(61, 24, 26, "Playlist", ["id PK", "name", "trackIdsCsv", "createdAt"])
    rec = ent(33, 2.5, 24, "Recording", ["id PK", "fileUri", "durationMs", "createdAt", "transcript?"])
    marker = ent(61, 2.5, 26, "RecordingMarker", ["id PK", "recordingId FK", "offsetMs", "label"])
    for a, b, lbl in [(calc, mem, "1:N"), (note, notefts, "1:1"), (note, scan, "1:N"),
                      (rec, marker, "1:N")]:
        ax.plot([a[0] + a[2] / 2, b[0] + b[2] / 2], [a[1], b[3]], color=LINE, lw=1.2, zorder=1)
        ax.text((a[0] + b[0]) / 2 + 6, (a[1] + b[3]) / 2, lbl, fontsize=6.4, color=MUTE, zorder=5)
    legend_note(ax, 3, H - 0.4, "Room schema v1 (§12). FTS4 mirrors Note text for instant offline search. All timestamps UTC epoch millis; user-facing formatting is locale-aware.")
    fig.savefig(os.path.join(OUT, "fig-erd.png"), bbox_inches="tight")
    plt.close(fig)


# -------------------------------------------------------- 14. AI stack ----
def fig_ai_stack():
    fig, ax = newfig(10.6, 6.0)
    H = 100 * 6.0 / 10.6
    box(ax, 3, H - 12, 62, 9, "Feature surfaces", ("Notes AI actions · Recorder transcript/summary · Scanner OCR · semantic search · smart calendar parse",),
        fc=TEAL_L, ec=TEAL, ts=9.6, fs=7.4)
    box(ax, 3, H - 26, 62, 11, "AI Orchestrator (in-process)",
        ("capability gate → device tier + pack presence", "work queue + cancel · thermal/battery guards", " timeouts, fallback ladder, result provenance"),
        fc=WHITE, ec=AMBER, ts=9.6, fs=7.4)
    arrow(ax, 34, H - 12.4, 34, H - 14.6, color=SLATE)
    runs = [("ONNX Runtime Mobile", "OCR det+rec · MiniLM int8"), ("TFLite (LiteRT)", "MobileNetV3 labels"),
            ("whisper.cpp JNI", "tiny/base int8 ASR"), ("MediaPipe LLM Inference", "gemma-2B-it 4-bit"),
            ("Android system TTS", "offline voice output")]
    y = H - 26
    for name, use in runs:
        y -= 8.6
        box(ax, 3, y, 40, 7.4, name, (use,), fc=FILL, ec=SLATE, ts=8.4, fs=7.0)
        arrow(ax, 24, y + 8.8, 24, y + 7.6, color=LINE, lw=1.1, ms=8)
    box(ax, 47, y - 1, 18, 8.6 + 7.4 * 4 + 2, "Model store", ("side-loaded packs", "SHA-256 manifest", "no download in app",),
        fc=DARK, ec=TEAL, tc="#E2E8F0", ts=9.0, fs=7.2)
    box(ax, 69, H - 16, 28, 13, "Device tiers", ("A ≥8 GB: full packs", "B 4–6 GB: essentials+ASR", "C 2–3 GB: essentials only",),
        fc=WHITE, ec=VIOLET, ts=8.8, fs=7.2)
    box(ax, 69, H - 32, 28, 13, "Hard guarantees", ("feature works w/o AI", "UI never blocks on model", "kill ≤ 250 ms on thermal", "0 network sockets",),
        fc=WHITE, ec=ROSE, ts=8.8, fs=7.2)
    box(ax, 69, H - 44, 28, 9, "Fallback ladder", ("LLM → extractive", "→ heuristic",), fc=WHITE, ec=AMBER, ts=8.8, fs=7.2)
    legend_note(ax, 3, 1.8, "AI is a leaf subsystem: features call the orchestrator; the orchestrator selects a runtime, enforces budgets, and degrades deterministically when packs are missing.")
    fig.savefig(os.path.join(OUT, "fig-ai-stack.png"), bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------ 15. SDLC gates ----
def fig_lifecycle():
    fig, ax = newfig(10.8, 4.6)
    H = 100 * 4.6 / 10.8
    phases = [
        ("G0", "Inception", "this blueprint\naccepted", TEAL),
        ("G1", "Bootstrap", "project builds\non CI", TEAL),
        ("G2", "Foundations", "design system +\ndata layer done", TEAL),
        ("G3", "Calculator", "TC-ONE-C-*\ngreen", AMBER),
        ("G4", "Modules", "notes→files→\ncal→media done", AMBER),
        ("G5", "On-device AI", "packs + fallbacks\nverified", VIOLET),
        ("G6", "Hardening", "a11y · perf ·\nsecurity pass", BLUE),
        ("G7", "Release", "signed APK +\nevidence bundle", ROSE),
        ("G8", "Operate", "update plan\n+ support", SLATE),
    ]
    n = len(phases)
    wseg = 96.0 / n
    for k, (g, name, art, c) in enumerate(phases):
        x = 2 + k * wseg
        box(ax, x, H * 0.44, wseg - 1.6, 12, "%s · %s" % (g, name), (), fc=c, ec=c, tc=WHITE, ts=8.2)
        box(ax, x, H * 0.16, wseg - 1.6, 12, "", (), fc=WHITE, ec=LINE)
        ax.text(x + (wseg - 1.6) / 2, H * 0.16 + 12 - 3.2, "exit:", fontsize=6.0, color=MUTE, ha="center")
        ax.text(x + (wseg - 1.6) / 2, H * 0.16 + 5.4, art, fontsize=6.2, color=SLATE, ha="center", va="center")
        if k:
            arrow(ax, x - 1.5, H * 0.50, x - 0.2, H * 0.50, color=SLATE, lw=1.4, ms=9)
    ax.text(2, H - 2.6, "Agent phase-gate lifecycle — a gate opens only when its exit criteria are demonstrated by committed artifacts (§15).",
            fontsize=7.6, color=MUTE, style="italic")
    ax.text(2, H - 5.6, "Iteration inside a phase follows: plan → implement → test → review → re-plan, with the task graph (§15.3) as the unit of work.",
            fontsize=7.6, color=MUTE, style="italic")
    fig.savefig(os.path.join(OUT, "fig-lifecycle.png"), bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------ 16. testing -------
def fig_testing():
    fig, ax = newfig(10.6, 4.8)
    H = 100 * 4.8 / 10.6
    ax.text(16, H - 3, "Test pyramid (share of cases)", fontsize=9.6, color=INK, fontweight="bold", ha="center")
    levels = [("Unit (JVM) — engines, parsers, repos", 62, TEAL),
              ("Integration (Robolectric) — DB, files, AI stubs", 20, "#0D9488"),
              ("Screenshot (Roborazzi) — design system + screens", 10, AMBER),
              ("Instrumented (device/emulator) — journeys", 6, BLUE),
              ("Black-box emulator QA — external harness (qa/)", 2, ROSE)]
    y = H - 8
    for name, pct, c in levels:
        wseg = 8 + pct * 0.52
        box(ax, 16 - wseg / 2, y - 4.6, wseg, 4.2, "%d%%  %s" % (pct, name.split(" — ")[0]), (),
            fc=c, ec=c, tc=WHITE, ts=7.4)
        ax.text(16 + wseg / 2 + 1.5, y - 2.5, name.split(" — ")[1], fontsize=6.6, color=SLATE, va="center")
        y -= 5.4
    ax.text(63, H - 3, "CI pipeline per pull request (3-runner cap)", fontsize=9.6, color=INK, fontweight="bold", ha="center")
    steps = ["commit / PR", "build + lint + detekt", "JVM unit + property tests", "Robolectric integration",
             "Roborazzi screenshots", "emulator matrix (API 26/33/35)", "black-box APK QA harness", "publish evidence + PDF"]
    y = H - 9
    for k, sname in enumerate(steps):
        box(ax, 52, y - 3.4, 24, 3.6, sname, (), fc=WHITE, ec=SLATE, tc=INK, ts=7.2)
        ax.text(78, y - 1.6, ["fast (<3 min)", "<8 min", "<6 min", "<6 min", "<4 min", "≤30 min", "≤40 min", "≤10 min"][k],
                fontsize=6.2, color=MUTE, va="center")
        if k < len(steps) - 1:
            arrow(ax, 64, y - 3.5, 64, y - 4.7, color=SLATE, lw=1.2, ms=8)
        y -= 4.7
    legend_note(ax, 2, 2.0, "Every layer produces artifacts this repository already consumes: results JSON, screenshots, evidence manifests (§18, §20).")
    fig.savefig(os.path.join(OUT, "fig-testing.png"), bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------- 17. defect flow -----
def fig_defects():
    fig, ax = newfig(10.4, 3.4)
    H = 100 * 3.4 / 10.4
    states = [("New", 4), ("Triaged", 20), ("In progress", 37), ("Fixed", 56), ("Verified", 71), ("Closed", 87)]
    for name, x in states:
        box(ax, x, H / 2 + 2, 11, 8, name, (), fc=TEAL_L, ec=TEAL, ts=8.8)
    for k in range(len(states) - 1):
        arrow(ax, states[k][1] + 11.2, H / 2 + 6, states[k + 1][1] - 0.4, H / 2 + 6, color=TEAL, lw=1.5)
    box(ax, 20, 2, 13, 7, "Blocked", ("needs device /", "decision"), fc=AMBER_L, ec=AMBER, ts=8.2, fs=6.4)
    box(ax, 45, 2, 13, 7, "Rejected", ("not a defect /", "won't fix (log)"), fc=ROSE_L, ec=ROSE, ts=8.2, fs=6.4)
    arrow(ax, 25, 9.4, 25, H / 2 + 1.6, color=AMBER, lw=1.2)
    arrow(ax, 56, 9.4, 51, H / 2 + 1.6, color=ROSE, lw=1.2)
    arrow(ax, 62, H / 2 + 1.4, 45, 8.8, color=ROSE, lw=1.2, con="arc3,rad=0.25")
    legend_note(ax, 4, H - 2.4, "Defect lifecycle (§20): severity S1–S4; every state transition records actor, evidence link and reason; ‘Verified’ requires a green re-run on the pinned APK.")
    fig.savefig(os.path.join(OUT, "fig-defect-flow.png"), bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------- 18. AI ladder --------
def fig_ai_ladder():
    fig, ax = newfig(10.4, 4.2)
    H = 100 * 4.2 / 10.4
    tiers = [
        ("Tier C · 2–3 GB RAM, API 26+", "Essentials pack only", "OCR + image labels + embeddings; extractive summary; system TTS", "#94A3B8"),
        ("Tier B · 4–6 GB RAM", "+ Speech pack", "whisper-tiny int8 transcription; ≤2 concurrent AI jobs", "#0D9488"),
        ("Tier A · ≥8 GB RAM, API 31+", "+ Assistant pack", "gemma-2B-it 4-bit for summarize/rewrite/parse; warm model ≤40 s idle then evict", TEAL),
    ]
    y = 4
    for name, pack, caps, c in tiers:
        box(ax, 4, y, 92, 11, name, (pack + "  ·  " + caps,), fc=WHITE, ec=c, ts=9.2, fs=7.4)
        y += 13.5
    arrow(ax, 8, 4, 8, y - 4, color=TEAL, lw=2.0)
    ax.text(11, 2.2, "capability increases upward — always a subset, never a requirement: every feature remains fully usable at Tier C with AI off",
            fontsize=7.4, color=MUTE, style="italic")
    fig.savefig(os.path.join(OUT, "fig-ai-ladder.png"), bbox_inches="tight")
    plt.close(fig)


def main():
    fig_cover()
    fig_modules()
    fig_architecture()
    fig_navigation()
    fig_calc()
    fig_calc_panels()
    fig_notes()
    fig_scanner()
    fig_calendar()
    fig_files()
    fig_music()
    fig_recorder()
    fig_diagnostics()
    fig_erd()
    fig_ai_stack()
    fig_lifecycle()
    fig_testing()
    fig_defects()
    fig_ai_ladder()
    print("figures written to", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
