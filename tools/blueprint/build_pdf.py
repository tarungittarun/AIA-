#!/usr/bin/env python3
"""MySpace One — Application Development Blueprint.

Builds a print-quality PDF from a directory of constrained-markdown chapter
files. Supports: parts (@PART:), chapters (#), sections (##/###/####),
paragraphs, inline bold/italic/code, bullet + numbered lists (nested),
pipe tables, fenced code blocks, blockquotes, figures (![caption](path)),
hard page breaks (<!-- pagebreak -->) and horizontal rules (---).

Usage:
  python3 build_pdf.py --content <content-dir> --out <pdf-path> [--title ...]
"""
import argparse
import hashlib
import os
import re
import sys

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Flowable, HRFlowable,
                                Image, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer,
                                Table, TableStyle, XPreformatted)
from reportlab.platypus.tableofcontents import TableOfContents

# ---------------------------------------------------------------- palette --
INK = colors.HexColor("#0F172A")
SLATE = colors.HexColor("#334155")
MUTE = colors.HexColor("#5B6B7E")
TEAL = colors.HexColor("#0F766E")
TEAL_DARK = colors.HexColor("#115E59")
AMBER = colors.HexColor("#B45309")
LINE = colors.HexColor("#C7D0DC")
ROW = colors.HexColor("#F4F7FA")
DARKBG = colors.HexColor("#0B1220")
CODEBG = colors.HexColor("#F3F6F9")
CODEBORDER = colors.HexColor("#D7DEE7")
QUOTE = colors.HexColor("#EEF4F3")

PAGE_W, PAGE_H = A4
M_L, M_R, M_T, M_B = 1.9 * cm, 1.9 * cm, 2.0 * cm, 1.9 * cm
AVAIL = PAGE_W - M_L - M_R


def register_fonts():
    try:
        import matplotlib
        mdir = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
    except Exception:
        mdir = ""
    sysdir = "/usr/share/fonts/truetype/dejavu"

    def find(name):
        for d in (mdir, sysdir):
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
        raise FileNotFoundError("font not found: " + name)

    pdfmetrics.registerFont(TTFont("DVS", find("DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DVS-Bold", find("DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DVS-Oblique", find("DejaVuSans-Oblique.ttf")))
    pdfmetrics.registerFont(TTFont("DVS-BoldOblique", find("DejaVuSans-BoldOblique.ttf")))
    pdfmetrics.registerFont(TTFont("DVMono", find("DejaVuSansMono.ttf")))
    pdfmetrics.registerFont(TTFont("DVMono-Bold", find("DejaVuSansMono-Bold.ttf")))
    registerFontFamily("DVS", normal="DVS", bold="DVS-Bold",
                       italic="DVS-Oblique", boldItalic="DVS-BoldOblique")
    registerFontFamily("DVMono", normal="DVMono", bold="DVMono-Bold",
                       italic="DVMono", boldItalic="DVMono-Bold")


# ----------------------------------------------------------------- styles --
def build_styles():
    s = {}
    s["body"] = ParagraphStyle("body", fontName="DVS", fontSize=10.1, leading=14.9,
                               textColor=INK, alignment=TA_JUSTIFY, spaceAfter=5)
    s["lead"] = ParagraphStyle("lead", parent=s["body"], fontSize=10.9, leading=16.4,
                               textColor=SLATE, spaceAfter=7)
    s["h1"] = ParagraphStyle("h1", fontName="DVS-Bold", fontSize=17.5, leading=22,
                             textColor=TEAL_DARK, spaceBefore=2, spaceAfter=4)
    s["h2"] = ParagraphStyle("h2", fontName="DVS-Bold", fontSize=12.6, leading=16.5,
                             textColor=INK, spaceBefore=13, spaceAfter=4, keepWithNext=1)
    s["h3"] = ParagraphStyle("h3", fontName="DVS-Bold", fontSize=10.8, leading=14.5,
                             textColor=SLATE, spaceBefore=10, spaceAfter=3, keepWithNext=1)
    s["h4"] = ParagraphStyle("h4", fontName="DVS-BoldOblique", fontSize=9.9, leading=13.5,
                             textColor=SLATE, spaceBefore=8, spaceAfter=2, keepWithNext=1)
    for lvl in range(4):
        s["bl%d" % lvl] = ParagraphStyle(
            "bl%d" % lvl, parent=s["body"], alignment=TA_LEFT, leftIndent=26 + 13 * lvl,
            bulletIndent=12 + 13 * lvl, spaceAfter=2.2)
    s["quote"] = ParagraphStyle("quote", parent=s["body"], alignment=TA_LEFT,
                                backColor=QUOTE, borderColor=TEAL, borderWidth=0,
                                borderPadding=(5, 8, 5, 8), leftIndent=8,
                                textColor=SLATE, spaceBefore=4, spaceAfter=7)
    s["code"] = ParagraphStyle("code", fontName="DVMono", fontSize=7.6, leading=10.0,
                               textColor=INK, backColor=CODEBG, borderColor=CODEBORDER,
                               borderWidth=0.6, borderPadding=(6, 8, 6, 8),
                               spaceBefore=5, spaceAfter=8, alignment=TA_LEFT)
    s["caption"] = ParagraphStyle("caption", fontName="DVS-Oblique", fontSize=8.6,
                                  leading=11.8, textColor=MUTE, alignment=TA_CENTER,
                                  spaceBefore=3, spaceAfter=10)
    s["cell"] = ParagraphStyle("cell", fontName="DVS", fontSize=8.35, leading=10.9,
                               textColor=INK, alignment=TA_LEFT)
    s["cellhead"] = ParagraphStyle("cellhead", fontName="DVS-Bold", fontSize=8.35,
                                   leading=10.9, textColor=colors.white, alignment=TA_LEFT)
    s["part_kicker"] = ParagraphStyle("part_kicker", fontName="DVS-Bold", fontSize=11,
                                      leading=15, textColor=AMBER, spaceAfter=10)
    s["part_title"] = ParagraphStyle("part_title", fontName="DVS-Bold", fontSize=23,
                                     leading=28, textColor=INK, spaceAfter=10)
    s["part_desc"] = ParagraphStyle("part_desc", fontName="DVS", fontSize=10.6,
                                    leading=15.5, textColor=SLATE)
    s["toc_h"] = ParagraphStyle("toc_h", fontName="DVS-Bold", fontSize=15, leading=19,
                                textColor=TEAL_DARK, spaceBefore=4, spaceAfter=8)
    s["cover_kicker"] = ParagraphStyle("cover_kicker", fontName="DVS-Bold", fontSize=10.5,
                                       leading=15, textColor=colors.HexColor("#5EEAD4"))
    s["cover_title"] = ParagraphStyle("cover_title", fontName="DVS-Bold", fontSize=36,
                                      leading=42, textColor=colors.white)
    s["cover_sub"] = ParagraphStyle("cover_sub", fontName="DVS", fontSize=11.5,
                                    leading=17, textColor=colors.HexColor("#CBD5E1"))
    s["cover_meta"] = ParagraphStyle("cover_meta", fontName="DVS", fontSize=9,
                                     leading=13.5, textColor=colors.HexColor("#94A3B8"))
    toc = []
    spec = [("toc0", "DVS-Bold", 10.3, INK, 10, 0),
            ("toc1", "DVS", 9.4, SLATE, 3, 12),
            ("toc2", "DVS", 8.7, MUTE, 2, 26)]
    for name, fn, fs, tc, sb, ind in spec:
        toc.append(ParagraphStyle(name, fontName=fn, fontSize=fs, leading=fs + 4.2,
                                  textColor=tc, spaceBefore=sb, leftIndent=ind))
    s["toc"] = toc
    return s


# ------------------------------------------------------------ inline text --
def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(t):
    """Escape + convert **bold**, *italic*, `code` in one string.

    Code spans are stashed first so their content (which may contain
    asterisks, e.g. deny-list patterns) never feeds bold/italic matching.
    """
    t = esc(t)
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return "\x00%d\x00" % (len(spans) - 1)

    t = re.sub(r"`([^`]+)`", stash, t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<i>\1</i>", t)

    def unstash(m):
        return ('<font face="DVMono" size="8.1" color="#0F766E">%s</font>'
                % spans[int(m.group(1))])

    return re.sub("\x00(\\d+)\x00", unstash, t)


def wrap_code(text, width=94):
    out = []
    for line in text.rstrip("\n").split("\n"):
        while len(line) > width:
            out.append(line[:width])
            line = "    " + line[width:]
        out.append(line)
    return "\n".join(out)


# ------------------------------------------------------------- flowables --
class Rule(HRFlowable):
    def __init__(self, **kw):
        super().__init__(thickness=0.7, color=LINE, spaceBefore=2, spaceAfter=8, **kw)


def make_table(rows, styles):
    n = max(len(r) for r in rows)
    rows = [r + [""] * (n - len(r)) for r in rows]
    weights = []
    for i in range(n):
        w = max(min(len(r[i]), 42) for r in rows)
        weights.append(max(w, 5) + 4)
    tot = float(sum(weights))
    widths = [AVAIL * w / tot for w in weights]
    data = []
    for ri, r in enumerate(rows):
        st = styles["cellhead"] if ri == 0 else styles["cell"]
        data.append([Paragraph(inline(c), st) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1, splitByRow=1, hAlign="LEFT")
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
    ]
    for ri in range(1, len(rows)):
        if ri % 2 == 0:
            cmds.append(("BACKGROUND", (0, ri), (-1, ri), ROW))
    t.setStyle(TableStyle(cmds))
    return t


def make_figure(path, caption, styles, fig_no):
    img = PILImage.open(path)
    w, h = img.size
    max_w, max_h = AVAIL, 16.2 * cm
    scale = min(max_w / w, max_h / h, (13.6 * cm) / w if False else 10)
    scale = min(max_w / w, max_h / h)
    dw, dh = w * scale, h * scale
    flo = Image(path, width=dw, height=dh)
    flo.hAlign = "CENTER"
    cap = Paragraph("<b>Figure %d.</b>  %s" % (fig_no, inline(caption)), styles["caption"])
    return KeepTogether([Spacer(1, 4), flo, cap])


# ------------------------------------------------------------ doc template --
class BlueprintDoc(BaseDocTemplate):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._last_lvl = -1
        self.fig_no = 0

    def afterFlowable(self, flowable):
        toc = getattr(flowable, "_toc", None)
        if not toc:
            return
        level, text, key = toc
        try:
            self.canv.bookmarkPage(key)
            eff = min(level, self._last_lvl + 1)
            self.canv.addOutlineEntry(text, key, level=eff, closed=(eff <= 1))
            self._last_lvl = eff
        except Exception:
            pass
        self.notify("TOCEntry", (level, text, self.page, key))


def footer(canv, doc):
    canv.saveState()
    canv.setStrokeColor(LINE)
    canv.setLineWidth(0.6)
    canv.line(M_L, 1.42 * cm, PAGE_W - M_R, 1.42 * cm)
    canv.setFont("DVS", 7.1)
    canv.setFillColor(MUTE)
    canv.drawString(M_L, 1.02 * cm,
                    "MySpace One · Application Development Blueprint · v1.0 · offline-first / on-device / no sign-in")
    canv.drawRightString(PAGE_W - M_R, 1.02 * cm, "Page %d" % doc.page)
    canv.restoreState()


def cover_bg(canv, doc):
    canv.saveState()
    art = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "blueprint", "figures", "cover.png")
    if os.path.exists(art):
        canv.drawImage(art, 0, 0, PAGE_W, PAGE_H)
    else:
        canv.setFillColor(DARKBG)
        canv.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canv.restoreState()


# ------------------------------------------------------------------ parser --
PART_RE = re.compile(r"^@PART:\s*(.+)$")
PARTDESC_RE = re.compile(r"^@PARTDESC:\s*(.+)$")
FIG_RE = re.compile(r"^!\[(.*?)\]\((.+?)\)\s*$")
PB_RE = re.compile(r"^<!--\s*pagebreak\s*-->\s*$")


def parse_md(path, styles, doc, story, state):
    figdir = os.path.dirname(os.path.abspath(path))
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    from reportlab.platypus import PageBreak as _PB

    def brk():
        """Append a page break unless the story already ends with one."""
        if not (story and isinstance(story[-1], _PB)):
            story.append(PageBreak())


    i, n = 0, len(lines)
    para, quote = [], []
    after_part = state.get("after_part", False)

    def flush_para():
        if para:
            st = styles["lead"] if para[0].startswith("@LEAD ") else styles["body"]
            txt = " ".join(para)
            if txt.startswith("@LEAD "):
                txt = txt[6:]
            story.append(Paragraph(inline(txt), st))
            del para[:]

    def flush_quote():
        if quote:
            body = "<br/>".join(inline(q) for q in quote)
            story.append(Paragraph(body, styles["quote"]))
            del quote[:]

    while i < n:
        raw = lines[i]
        line = raw.rstrip()

        if PB_RE.match(line):
            flush_para(); flush_quote()
            story.append(PageBreak()); i += 1; continue

        m = PART_RE.match(line)
        if m and i == 0 or (m and not lines[i - 1].strip()):
            flush_para(); flush_quote()
            title = m.group(1)
            key = "bm-part-" + hashlib.md5(title.encode()).hexdigest()[:10]
            kick, rest = title, ""
            if " — " in title:
                kick, rest = title.split(" — ", 1)
            block = [Paragraph(esc(kick), styles["part_kicker"])]
            if rest:
                block.append(Paragraph(esc(rest), styles["part_title"]))
            desc = ""
            if i + 1 < n and PARTDESC_RE.match(lines[i + 1].strip()):
                desc = PARTDESC_RE.match(lines[i + 1].strip()).group(1)
                i += 1
            if desc:
                block += [Spacer(1, 6), Rule(), Paragraph(inline(desc), styles["part_desc"])]
            block.append(PageBreak())
            head = Paragraph(esc(kick), styles["part_kicker"])
            head._toc = (0, kick + (" — " + rest if rest else ""), key)
            brk()
            story.append(Spacer(1, 5.2 * cm))
            story.append(head)
            story.extend(block[1:])
            state["after_part"] = True
            after_part = True
            i += 1
            continue

        m = FIG_RE.match(line.strip())
        if m:
            flush_para(); flush_quote()
            cap, rel = m.group(1), m.group(2)
            p = os.path.join(figdir, rel)
            if not os.path.exists(p):
                raise FileNotFoundError("figure missing: %s (referenced in %s)" % (p, path))
            doc.fig_no += 1
            story.append(make_figure(p, cap, styles, doc.fig_no))
            i += 1; continue

        if line.startswith("```"):
            flush_para(); flush_quote()
            i += 1
            code = []
            while i < n and not lines[i].startswith("```"):
                code.append(lines[i]); i += 1
            i += 1
            story.append(XPreformatted(esc(wrap_code("\n".join(code))), styles["code"]))
            continue

        if line.startswith("|"):
            flush_para(); flush_quote()
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c or "---") for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                story.append(make_table(rows, styles))
                story.append(Spacer(1, 6))
            continue

        if re.match(r"^#{1,4}\s", line):
            flush_para(); flush_quote()
            level = len(line) - len(line.lstrip("#"))
            text = line.lstrip("#").strip()
            if level == 1:
                key = "bm-ch-" + hashlib.md5(text.encode()).hexdigest()[:10]
                h = Paragraph(esc(text), styles["h1"])
                h._toc = (1, text, key)
                if not after_part:
                    brk()
                story.append(h)
                story.append(Rule())
                state["after_part"] = False
                after_part = False
            else:
                key = "bm-h%d-" % level + hashlib.md5(text.encode()).hexdigest()[:10]
                stl = {2: "h2", 3: "h3", 4: "h4"}[level]
                h = Paragraph(esc(text), styles[stl])
                if level <= 3:
                    h._toc = (level, text, key)
                story.append(h)
            i += 1; continue

        if line.strip() == "---":
            flush_para(); flush_quote()
            story.append(Rule()); i += 1; continue

        if line.startswith(">"):
            flush_para()
            quote.append(line.lstrip("> ").strip())
            i += 1; continue

        if re.match(r"^\s*[-*]\s+", line) and not line.strip().startswith("*\\"):
            flush_para(); flush_quote()
            indent = len(line) - len(line.lstrip())
            lvl = min(indent // 2, 3)
            content = re.sub(r"^\s*[-*]\s+", "", line)
            story.append(Paragraph(inline(content), styles["bl%d" % lvl],
                                   bulletText="•"))
            i += 1; continue

        mnum = re.match(r"^(\s*)(\d+)[.)]\s+(.*)$", line)
        if mnum:
            flush_para(); flush_quote()
            lvl = min(len(mnum.group(1)) // 2, 3)
            story.append(Paragraph(inline(mnum.group(3)), styles["bl%d" % lvl],
                                   bulletText=mnum.group(2) + "."))
            i += 1; continue

        if not line.strip():
            flush_para(); flush_quote()
            i += 1; continue

        para.append(line.strip())
        i += 1

    flush_para(); flush_quote()
    state["after_part"] = after_part


# ------------------------------------------------------------------- main --
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--doc-title", default="MySpace One · Application Development Blueprint")
    args = ap.parse_args()

    register_fonts()
    styles = build_styles()

    doc = BlueprintDoc(args.out, pagesize=A4, title=args.doc_title,
                       author="AI build agent program — prepared for repository tarungittarun/AIA-",
                       subject="Offline-first combined app development blueprint",
                       leftMargin=M_L, rightMargin=M_R, topMargin=M_T, bottomMargin=M_B)
    frame_cover = Frame(M_L, M_B, AVAIL, PAGE_H - M_T - M_B, id="cover")
    frame_body = Frame(M_L, M_B, AVAIL, PAGE_H - M_T - M_B, id="body")
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[frame_cover], onPage=cover_bg),
        PageTemplate(id="Body", frames=[frame_body], onPage=footer),
    ])

    story = []
    # ---- cover page ----
    story.append(Spacer(1, 3.1 * cm))
    story.append(Paragraph("APPLICATION DEVELOPMENT BLUEPRINT · WRITTEN FOR AN AI BUILD AGENT", styles["cover_kicker"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("MySpace One", styles["cover_title"]))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph(
        "One offline-first Android app — Calculator · Notes · Scanner · Calendar · Files · "
        "Music · Recorder · Diagnostics · On-device AI", styles["cover_sub"]))
    story.append(Spacer(1, 0.45 * cm))
    story.append(HRFlowable(width="62%", thickness=1.1, color=colors.HexColor("#14B8A6"),
                            hAlign="LEFT", spaceBefore=2, spaceAfter=10))
    story.append(Paragraph(
        "From an empty repository to a fully tested, signed, installable APK: requirements, "
        "experience design, architecture, on-device AI integration, agent methodology, "
        "testing, release engineering and maintenance — all stages and cycles, with "
        "machine-checkable acceptance criteria.", styles["cover_sub"]))
    story.append(Spacer(1, 6.2 * cm))
    meta = [
        ["Document", "MySpace One — combined-app development blueprint"],
        ["Version / status", "1.0 · approved for build execution"],
        ["Date", "31 October 2026"],
        ["Primary reader", "Autonomous AI build agent (secondary: human reviewers)"],
        ["Target platform", "Android 8.0+ · phones and tablets · no internet, no sign-in"],
        ["Deliverable", "Signed release APK + full evidence bundle + test reports"],
    ]
    t = Table([[Paragraph("<font color='#5EEAD4'><b>%s</b></font>" % esc(a), styles["cover_meta"]),
                Paragraph("<font color='#CBD5E1'>%s</font>" % esc(b), styles["cover_meta"])]
               for a, b in meta], colWidths=[3.6 * cm, 12.6 * cm], hAlign="LEFT")
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 1.6),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6)]))
    story.append(t)
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())

    # ---- table of contents ----
    story.append(Paragraph("Contents", styles["toc_h"]))
    toc = TableOfContents()
    toc.levelStyles = styles["toc"]
    toc.dotsMinLevel = 1
    story.append(toc)
    story.append(PageBreak())

    state = {"after_part": False}
    files = sorted(f for f in os.listdir(args.content) if f.endswith(".md"))
    if not files:
        sys.exit("no markdown content found in " + args.content)
    for f in files:
        parse_md(os.path.join(args.content, f), styles, doc, story, state)

    doc.multiBuild(story)

    from pypdf import PdfReader
    pages = len(PdfReader(args.out).pages)
    size = os.path.getsize(args.out)
    print("BUILD OK: %s — %d pages, %.2f MB" % (args.out, pages, size / 1e6))
    if pages < 200:
        print("WARNING: below 200-page target", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
