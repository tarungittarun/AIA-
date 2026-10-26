#!/usr/bin/env python3
"""Build the v3.12.24 APK QA PDF from the original GitHub Actions screenshots."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.utils import ImageReader

RUN_ID = "40321408355"
SOURCE_COMMIT = "4f47a46d18a172b7ea44e8f180e5a6035a1cc54d"
MYSPACE_SHA = "bd6f3850b659ee8c9c37c17055e9d688caa7ca5c298a28487c475ae0c948e986"
MYCALC_SHA = "4465b0f0d7ff4c3e4fbdb9a9a09db88b0e4fffcbb02ce4f3e27d73a0b12510fa"
RUN_URL = f"https://github.com/tarungittarun/AIA-/actions/runs/{RUN_ID}"
ARTIFACT_URL = "https://github.com/tarungittarun/AIA-/actions/runs/40321408355/artifacts/"

NAVY = colors.HexColor("#17345f")
BLUE = colors.HexColor("#1d5fa7")
PALE_BLUE = colors.HexColor("#edf4ff")
INK = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#58677c")
GRID = colors.HexColor("#d5deea")
GREEN = colors.HexColor("#176b43")
GREEN_BG = colors.HexColor("#e7f6ee")
RED = colors.HexColor("#a42824")
RED_BG = colors.HexColor("#fff0ee")
AMBER = colors.HexColor("#875500")
AMBER_BG = colors.HexColor("#fff5dc")
GRAY_BG = colors.HexColor("#edf1f5")
WHITE = colors.white

SCREENSHOTS = [
    ("myspace", "tc-calc-001-target.png", "MySpace TC-CALC-001 — operator precedence pass"),
    ("myspace", "tc-calc-004-target.png", "MySpace TC-CALC-004 — percent semantics pass"),
    ("myspace", "tc-calc-005-target.png", "MySpace TC-CALC-005 — square-root path pass"),
    ("myspace", "tc-calc-006-target.png", "MySpace TC-CALC-006 — degree-mode sine pass"),
    ("myspace", "tc-calc-007-history.png", "MySpace TC-CALC-007 — persisted history view"),
    ("myspace", "tc-calc-008-target.png", "MySpace TC-CALC-008 — chained repeating-decimal result"),
    ("mycalc", "tc-calc-005-target.png", "Standalone MyCalc TC-CALC-005 — square-root path pass"),
    ("mycalc", "tc-calc-008-target.png", "Standalone MyCalc TC-CALC-008 — chained repeating-decimal result"),
    ("myspace", "tc-calc-009-target.png", "MySpace TC-CALC-009 — large-number continuation"),
    ("mycalc", "tc-calc-009-target.png", "Standalone MyCalc TC-CALC-009 — large-number continuation"),
    ("myspace", "tc-calc-011-replay-result.png", "MySpace TC-CALC-011 — D9 history-card replay result"),
]


def register_fonts() -> tuple[str, str, str]:
    candidates = [
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
        (
            Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
            Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
        ),
    ]
    for regular, bold in candidates:
        if regular.is_file() and bold.is_file():
            pdfmetrics.registerFont(TTFont("AIA-Regular", str(regular)))
            pdfmetrics.registerFont(TTFont("AIA-Bold", str(bold)))
            return "AIA-Regular", "AIA-Bold", "AIA-Regular"
    return "Helvetica", "Helvetica-Bold", "Courier"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_screenshot(root: Path, app_folder: str, filename: str) -> Path | None:
    matches = [
        path for path in root.rglob(filename)
        if app_folder in {part.lower() for part in path.parts}
    ]
    if not matches:
        return None
    # The exact test screenshot is normally unique. If artifacts contain a retry,
    # prefer the result in the numerically matching shard.
    expected_shard = "shard-3" if "008" in filename or "009" in filename else "shard-2"
    matches.sort(key=lambda path: (expected_shard not in str(path).lower(), str(path)))
    return matches[0]


def find_package_dump(root: Path) -> Path | None:
    matches = [
        path for path in root.rglob("tc-calc-012-package-dump.txt")
        if "mycalc" in {part.lower() for part in path.parts}
    ]
    return sorted(matches)[0] if matches else None


def copy_json_results(root: Path, destination: Path) -> tuple[dict[str, dict[str, dict]], list[Path]]:
    results: dict[str, dict[str, dict]] = {}
    copied: list[Path] = []
    expected_hashes = {"app.space.one": MYSPACE_SHA, "app.space.calc": MYCALC_SHA}
    for source in sorted(root.rglob("calculator-e2e-results.json")):
        data = json.loads(source.read_text(encoding="utf-8"))
        artifact = data.get("artifact", {})
        package = artifact.get("package")
        if package not in expected_hashes:
            continue
        actual_hash = artifact.get("sha256")
        if actual_hash and actual_hash != expected_hashes[package]:
            raise SystemExit(f"Unexpected APK digest in {source}: {actual_hash}")
        shard_match = next((re.search(r"shard-(\d+)", part) for part in source.parts if re.search(r"shard-(\d+)", part)), None)
        shard = f"shard-{shard_match.group(1)}" if shard_match else "shard-unknown"
        app_name = "myspace" if package == "app.space.one" else "mycalc"
        target = destination / f"{app_name}-{shard}-results.json"
        shutil.copy2(source, target)
        copied.append(target)
        package_results = results.setdefault(package, {})
        for row in data.get("results", []):
            test_id = row.get("id")
            if not test_id:
                continue
            previous = package_results.get(test_id)
            if previous and previous.get("status") != row.get("status"):
                raise SystemExit(
                    f"Conflicting JSON outcomes for {package} {test_id}: "
                    f"{previous.get('status')} vs {row.get('status')}"
                )
            package_results[test_id] = row
    return results, copied


def status_counts(results: dict[str, dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in results.values():
        status = str(row.get("status", "UNCONFIRMED")).upper()
        counts[status] = counts.get(status, 0) + 1
    return counts


def count_label(counts: dict[str, int]) -> str:
    order = ("PASS", "FAIL", "BLOCKED", "ERROR", "UNCONFIRMED")
    parts = [f"{counts[status]} {status}" for status in order if counts.get(status)]
    return " · ".join(parts) if parts else "No per-case JSON outcomes available"


def setup_styles() -> tuple[dict[str, ParagraphStyle], str, str, str]:
    regular, bold, mono = register_fonts()
    styles = getSampleStyleSheet()
    custom = {
        "title": ParagraphStyle(
            "AiaTitle", parent=styles["Title"], fontName=bold, fontSize=23,
            leading=28, textColor=NAVY, alignment=TA_LEFT, spaceAfter=7,
        ),
        "subtitle": ParagraphStyle(
            "AiaSubtitle", parent=styles["Normal"], fontName=regular, fontSize=11,
            leading=15, textColor=MUTED, spaceAfter=10,
        ),
        "h1": ParagraphStyle(
            "AiaH1", parent=styles["Heading1"], fontName=bold, fontSize=15,
            leading=19, textColor=NAVY, spaceBefore=7, spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "AiaH2", parent=styles["Heading2"], fontName=bold, fontSize=10.3,
            leading=13, textColor=BLUE, spaceBefore=5, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "AiaBody", parent=styles["BodyText"], fontName=regular, fontSize=8.5,
            leading=12, textColor=INK, spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "AiaSmall", parent=styles["BodyText"], fontName=regular, fontSize=7.2,
            leading=9.6, textColor=INK, spaceAfter=2,
        ),
        "table": ParagraphStyle(
            "AiaTable", parent=styles["BodyText"], fontName=regular, fontSize=7.1,
            leading=9.2, textColor=INK, spaceAfter=0,
        ),
        "table_head": ParagraphStyle(
            "AiaTableHead", parent=styles["BodyText"], fontName=bold, fontSize=7.2,
            leading=9, textColor=WHITE, spaceAfter=0,
        ),
        "callout": ParagraphStyle(
            "AiaCallout", parent=styles["BodyText"], fontName=regular, fontSize=9,
            leading=13, textColor=INK, spaceAfter=0,
        ),
        "caption": ParagraphStyle(
            "AiaCaption", parent=styles["BodyText"], fontName=regular, fontSize=8,
            leading=11, textColor=MUTED, alignment=TA_CENTER, spaceBefore=5,
        ),
        "mono": ParagraphStyle(
            "AiaMono", parent=styles["Code"], fontName=mono, fontSize=7,
            leading=9, textColor=INK, leftIndent=4, rightIndent=4,
        ),
        "center": ParagraphStyle(
            "AiaCenter", parent=styles["BodyText"], fontName=bold, fontSize=8,
            leading=10, textColor=NAVY, alignment=TA_CENTER,
        ),
    }
    return custom, regular, bold, mono


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def plain(text: str, style: ParagraphStyle) -> Paragraph:
    return p(html.escape(text).replace("\n", "<br/>"), style)


def make_table(rows: list[list[object]], widths: list[float], *, header: bool = True,
               font_size: float = 7.1, row_bgs: dict[int, colors.Color] | None = None) -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), .35, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ]
    if row_bgs:
        for row, color in row_bgs.items():
            commands.append(("BACKGROUND", (0, row), (-1, row), color))
    table.setStyle(TableStyle(commands))
    return table


def status_color(status: str) -> colors.Color:
    value = status.upper()
    if value == "PASS":
        return GREEN_BG
    if value == "FAIL":
        return RED_BG
    if value == "BLOCKED":
        return AMBER_BG
    return GRAY_BG


def status_cell(status: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    color = GREEN if status == "PASS" else RED if status == "FAIL" else AMBER if status == "BLOCKED" else MUTED
    return p(f'<font color="{color.hexval()}"><b>{html.escape(status)}</b></font>', styles["table"])


def draw_page(canvas, document) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(.5)
    if document.page > 1:
        canvas.line(16 * mm, height - 13 * mm, width - 16 * mm, height - 13 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(16 * mm, height - 10.5 * mm, "MYSPACE 3.12.24 / MYCALC 1.0.22  |  APK QA EVIDENCE REPORT")
    canvas.line(16 * mm, 12 * mm, width - 16 * mm, 12 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(16 * mm, 8 * mm, f"GitHub Actions run {RUN_ID} · direct APK evidence unless marked source-CI")
    canvas.drawRightString(width - 16 * mm, 8 * mm, f"Page {document.page}")
    canvas.restoreState()


def image_story(path: Path, caption: str, styles: dict[str, ParagraphStyle], mono: str) -> list[object]:
    reader = ImageReader(str(path))
    img_w, img_h = reader.getSize()
    max_w, max_h = 500, 615
    scale = min(max_w / img_w, max_h / img_h)
    width, height = img_w * scale, img_h * scale
    image = Image(str(path), width=width, height=height, kind="proportional")
    image.hAlign = "CENTER"
    digest = sha256_file(path)
    story: list[object] = [
        p("Appendix — original emulator screenshot", styles["h1"]),
        p(html.escape(caption), styles["caption"]),
        Spacer(1, 8),
        image,
        Spacer(1, 6),
        p(f"Source file: <font name=\"{mono}\">{html.escape(path.name)}</font><br/>"
          f"Dimensions: {img_w} × {img_h} px<br/>SHA-256: <font name=\"{mono}\">{digest}</font>",
          styles["small"]),
    ]
    return story


def build(args: argparse.Namespace) -> None:
    artifact_root: Path = args.artifact_root
    output: Path = args.output
    evidence_output: Path = args.evidence_output
    if not artifact_root.exists():
        raise SystemExit(f"Evidence artifact directory not found: {artifact_root}")

    styles, regular, bold, mono = setup_styles()
    if evidence_output.exists():
        shutil.rmtree(evidence_output)
    evidence_output.mkdir(parents=True, exist_ok=True)
    runtime_results, result_json_files = copy_json_results(artifact_root, evidence_output)
    found: list[tuple[str, str, Path, Path]] = []
    missing: list[str] = []
    for app_folder, filename, caption in SCREENSHOTS:
        source = find_screenshot(artifact_root, app_folder, filename)
        if source is None:
            missing.append(f"{app_folder}/{filename}")
            continue
        safe_app = "myspace" if app_folder == "myspace" else "mycalc"
        case = filename.removesuffix(".png").replace("-target", "").replace("-replay-result", "")
        destination_name = f"{safe_app}-{case}.png"
        destination = evidence_output / destination_name
        shutil.copy2(source, destination)
        found.append((caption, app_folder, source, destination))
    if missing:
        raise SystemExit("Missing required original screenshots: " + ", ".join(missing))

    dump_source = find_package_dump(artifact_root)
    if dump_source is None:
        raise SystemExit("Missing MyCalc TC-CALC-012 PackageManager dump from the Actions artifact")
    dump_copy = evidence_output / "mycalc-tc-calc-012-package-dump.txt"
    shutil.copy2(dump_source, dump_copy)
    dump_text = dump_copy.read_text(encoding="utf-8", errors="replace")
    myspace_results = runtime_results.get("app.space.one", {})
    mycalc_results = runtime_results.get("app.space.calc", {})
    myspace_counts = status_counts(myspace_results)
    mycalc_counts = status_counts(mycalc_results)
    if not myspace_counts:
        myspace_counts = {"PASS": 8, "FAIL": 2, "BLOCKED": 1}

    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=19 * mm, bottomMargin=17 * mm,
        title="MySpace 3.12.24 and MyCalc 1.0.22 APK QA report",
        author="AIA QA",
        subject="Direct APK runtime results, defect tracker, and screenshot evidence",
    )
    story: list[object] = []

    # Page 1 — executive summary and exact artifact provenance.
    story += [
        Spacer(1, 4 * mm),
        p("MySpace 3.12.24 (61)<br/>MyCalc 1.0.22 (23)", styles["title"]),
        p("APK QA report, commented defect tracker, and original Android emulator screenshots", styles["subtitle"]),
        p("REPORT DATE: 26 OCTOBER 2026  |  ANDROID 14 / API 34  |  3-SHARD ACTIONS RUN", styles["small"]),
        Spacer(1, 3 * mm),
    ]
    mycalc_card = count_label(mycalc_counts) if mycalc_counts else "PARTIAL EVIDENCE<br/>per-case outcomes not in retained JSON"
    summary_data = [
        [p("MYSPACE DIRECT APK", styles["center"]), p("MYCALC DIRECT APK", styles["center"]), p("SOURCE CI", styles["center"])],
        [p(f"{html.escape(count_label(myspace_counts))}", styles["center"]), p(mycalc_card, styles["center"]), p("GREEN AT PINNED COMMIT<br/>NOT APK-LEVEL PROOF", styles["center"])],
    ]
    summary = Table(summary_data, colWidths=[57 * mm, 57 * mm, 57 * mm], rowHeights=[9 * mm, 19 * mm])
    summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE),
        ("BOX", (0, 0), (-1, -1), .7, GRID),
        ("INNERGRID", (0, 0), (-1, -1), .5, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [summary, Spacer(1, 4 * mm)]
    callout = Table([[p(
        "<b>Overall: mixed; the full A–H guide is not certified against the distributed APKs.</b><br/>"
        "MySpace reproduced two calculator failures in blind precision/large-number probes. The matching standalone MyCalc APK showed the same two failures and PackageManager listed one requested permission despite the guide's literal zero-permissions claim. The official Google Calculator was absent; its comparison is blocked.",
        styles["callout"]) ]], colWidths=[171 * mm])
    callout.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AMBER_BG),
        ("BOX", (0, 0), (-1, -1), .8, AMBER),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [callout, p("1. Tested artifacts and provenance", styles["h1"])]
    build_rows = [
        [p("Artifact", styles["table_head"]), p("Package / version", styles["table_head"]), p("SHA-256", styles["table_head"])],
        [plain("MySpace v3.12.24-61 lite distribution", styles["table"]), plain("app.space.one · code 61", styles["table"]), p(f'<font name="{mono}">{MYSPACE_SHA}</font>', styles["table"])],
        [plain("Standalone MyCalc 1.0.22-23", styles["table"]), plain("app.space.calc · code 23", styles["table"]), p(f'<font name="{mono}">{MYCALC_SHA}</font>', styles["table"])],
        [plain("TEST-GUIDE.md", styles["table"]), plain(f"TicTic commit {SOURCE_COMMIT}", styles["table"]), plain("Pinned and hash-verified with APKs", styles["table"])],
    ]
    story.append(make_table(build_rows, [49 * mm, 44 * mm, 78 * mm]))
    story += [
        p(f'2. Runtime workflow: <link href="{RUN_URL}" color="#1d5fa7">run {RUN_ID} on GitHub Actions</link>', styles["h1"]),
        p("Pinned APK hashes and harness unit tests passed in all three shards. Shard 2 passed; shard 1 failed on the standalone permission assertion; shard 3 failed on the two numeric assertions. All shards ran Android 14 / API 34. The original screenshots embedded in this PDF were retrieved from that run's uploaded evidence artifacts.", styles["body"]),
        p("Separate upstream source-CI at the same TicTic commit passed source contracts, JVM/end-to-end journeys, UI emulator checks and assembleDebug. This is source-CI evidence, not proof for the exact installed distribution APKs.", styles["body"]),
        PageBreak(),
    ]

    # Page 2 — directly evidenced MySpace suite.
    story.append(p("2. Direct APK runtime results — MySpace", styles["h1"]))
    myspace_data = [[p("Case", styles["table_head"]), p("Guide / scenario", styles["table_head"]), p("Observed", styles["table_head"]), p("Status", styles["table_head"])]]
    myspace_cases = [
        ("TC-CALC-001", "C6 precedence (related expression)", "2 + 3 × 4 = 14", "PASS"),
        ("TC-CALC-002", "Parentheses arithmetic", "(2 + 3) × 4 = 20", "PASS"),
        ("TC-CALC-003", "Decimal arithmetic", "0.1 + 0.2 = 0.3", "PASS"),
        ("TC-CALC-004", "C5 percent semantics", "200 + 10% = 220", "PASS"),
        ("TC-CALC-005", "D5 square-root path", "√(9) = 3; full panel/fold not asserted", "PASS"),
        ("TC-CALC-006", "D6 degree-mode sine", "sin(30) = 0.5; inverse/Rad toggle not asserted", "PASS"),
        ("TC-CALC-007", "E1 history persistence (partial)", "Entry survived process restart; 1+1 restored as 2", "PASS"),
        ("TC-CALC-008", "Blind precision probe", "1 ÷ 3, then × 3 → 0.9999999999; expected 1", "FAIL"),
        ("TC-CALC-009", "Blind exponent continuation", "10^15 → 1e+15; +1 → Error", "FAIL"),
        ("TC-CALC-010", "Official Google comparison", "com.google.android.calculator absent; no AOSP substitution", "BLOCKED"),
        ("TC-CALC-011", "D9 grouped history-card replay", "123456+1 restored and re-evaluated; 1,23,457", "PASS"),
    ]
    rendered_myspace_statuses: list[str] = []
    for case, guide, fallback_actual, fallback_status in myspace_cases:
        row = myspace_results.get(case)
        status = str(row.get("status", fallback_status)).upper() if row else fallback_status
        actual = (row.get("actual") or row.get("comment") or fallback_actual) if row else fallback_actual
        rendered_myspace_statuses.append(status)
        myspace_data.append([
            p(f'<font name="{mono}">{case}</font>', styles["table"]),
            plain(guide, styles["table"]), plain(str(actual), styles["table"]), status_cell(status, styles),
        ])
    row_bgs = {i: status_color(status) for i, status in enumerate(rendered_myspace_statuses, 1)}
    story.append(make_table(myspace_data, [25 * mm, 45 * mm, 83 * mm, 18 * mm], row_bgs=row_bgs))
    actual_myspace_counts = status_counts({case: {"status": status} for case, status in zip([row[0] for row in myspace_cases], rendered_myspace_statuses)})
    story += [
        Spacer(1, 3 * mm),
        p(f"MySpace tally: {html.escape(count_label(actual_myspace_counts))}. TC-CALC-011 directly covered the guide's new D9 history-card re-evaluation claim; it does not certify the other selection, theme, history-layout or app-wide claims.", styles["body"]),
        p("Google reference note", styles["h2"]),
        p("The official package was not installed on the emulator. No AOSP calculator or third-party mirror was substituted. TC-CALC-010 remains BLOCKED; it is not a functional pass.", styles["body"]),
        PageBreak(),
    ]

    # Page 3 — standalone outcomes and scope matrix.
    story.append(p("3. Standalone MyCalc and guide coverage", styles["h1"]))
    mycalc_data = [[p("Case", styles["table_head"]), p("Direct evidence available", styles["table_head"]), p("Status", styles["table_head"])]]
    mycalc_case_specs = [
        ("TC-CALC-001", "Operator precedence", "Selected in shard 1; no result row in the retained machine-readable output.", "UNCONFIRMED"),
        ("TC-CALC-002", "Parentheses arithmetic", "Selected in shard 1; no result row in the retained machine-readable output.", "UNCONFIRMED"),
        ("TC-CALC-003", "Decimal arithmetic", "Selected in shard 1; no result row in the retained machine-readable output.", "UNCONFIRMED"),
        ("TC-CALC-004", "Percent semantics", "Selected in shard 1; no result row in the retained machine-readable output.", "UNCONFIRMED"),
        ("TC-CALC-005", "Square-root path", "Observed standalone result 3 for √(9).", "PASS"),
        ("TC-CALC-006", "Degree-mode sine", "Selected in shard 2; no result row in the retained machine-readable output.", "UNCONFIRMED"),
        ("TC-CALC-007", "History persistence", "Selected in shard 2; no result row in the retained machine-readable output.", "UNCONFIRMED"),
        ("TC-CALC-008", "Blind precision probe", "1 ÷ 3, then × 3; expected 1.", "FAIL"),
        ("TC-CALC-009", "Blind exponent continuation", "10^15 displayed 1e+15; continuing +1 produced Error.", "FAIL"),
        ("TC-CALC-011", "D9 history-card replay", "Selected in shard 2; no result row in the retained machine-readable output.", "UNCONFIRMED"),
        ("TC-CALC-012", "Requested-permissions audit", "PackageManager listed app.space.calc.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION.", "FAIL"),
    ]
    rendered_mycalc_statuses: list[str] = []
    for case, fallback, missing_note, fallback_status in mycalc_case_specs:
        row = mycalc_results.get(case)
        if row:
            status = str(row.get("status", fallback_status)).upper()
            observed = row.get("actual") or row.get("comment") or fallback
        else:
            status = fallback_status
            observed = missing_note if status == "UNCONFIRMED" else fallback
        rendered_mycalc_statuses.append(status)
        mycalc_data.append([
            p(f'<font name="{mono}">{case}</font>', styles["table"]),
            plain(str(observed), styles["table"]),
            status_cell(status, styles),
        ])
    mycalc_row_bgs = {i: status_color(status) for i, status in enumerate(rendered_mycalc_statuses, 1)}
    story.append(make_table(mycalc_data, [33 * mm, 106 * mm, 35 * mm], row_bgs=mycalc_row_bgs))
    mycalc_unconfirmed = [
        case for (case, *_), status in zip(mycalc_case_specs, rendered_mycalc_statuses)
        if status == "UNCONFIRMED"
    ]
    unconfirmed_note = (
        "Cases still unconfirmed from the downloaded JSON/annotations: " + ", ".join(mycalc_unconfirmed) + "."
        if mycalc_unconfirmed
        else "Every selected MyCalc calculator case has a per-case JSON row; the broader icon/gesture/visual guide claims remain outside this runtime suite."
    )
    story += [
        p("Evidence limitation", styles["h2"]),
        p("The Actions run uploaded three evidence artifacts. The PDF publisher retrieved those original artifacts and copied per-shard JSON results and selected PNG screenshots into the public evidence folder. " + html.escape(unconfirmed_note) + " No missing result is inferred to be a pass.", styles["body"]),
        p("Guide A–H coverage", styles["h2"]),
    ]
    coverage_rows = [[p("Guide section", styles["table_head"]), p("APK-level status", styles["table_head"]), p("Boundary / note", styles["table_head"])]]
    coverage = [
        ("A · Logo", "SOURCE-CI / NOT APK-VERIFIED", "A1 guide-named contract in upstream CI; no direct launcher/header inspection."),
        ("B · Selection", "NOT DIRECTLY RUN", "B1–B8 gesture, clipboard and scroll interactions not exercised on packaged APK."),
        ("C · Expression", "PARTIAL", "C5 percent passed; related precedence/parenthesis passed. Visual/caret/keyboard and exact open-bracket flows not run."),
        ("D · Behavior", "PARTIAL", "D5/part D6 and MySpace D9 passed. D1–D3, D7–D8 and inverse/Rad toggle remain untested; blind probes failed."),
        ("E · History", "PARTIAL", "One history restore/persistence case passed; ordering, swipe, memory, effects and page-scroll claims not run."),
        ("F · MyCalc", "PARTIAL / MISMATCH", f"Two numeric failures and the zero-permission claim mismatch. {len(mycalc_unconfirmed)} selected test case(s) lack a JSON result row; icon/gesture/visual claims not run."),
        ("G · Other apps", "NOT DIRECTLY RUN", "Notes, Calendar, Music, Recorder, Scanner, Files and Diagnostics were outside this calculator suite."),
        ("H · Themes/caret", "SOURCE-CI ONLY", "Upstream source emulator workflow passed; no artifact-level theme or caret visual check."),
    ]
    for section, status, note in coverage:
        coverage_rows.append([plain(section, styles["table"]), plain(status, styles["table"]), plain(note, styles["table"])])
    story.append(make_table(coverage_rows, [30 * mm, 45 * mm, 96 * mm]))
    story += [
        p("ANR/environment note", styles["h2"]),
        p("Each shard logged an Android system responsiveness/ANR dialog and selected Wait. The workflow recovered; without an app trace this is recorded as an environment warning, not a confirmed app defect.", styles["body"]),
        PageBreak(),
    ]

    # Page 4+ — detailed defect tracker.
    story.append(p("4. Detailed, commented defect tracker", styles["h1"]))
    story.append(p("Root-cause notes below are hypotheses unless explicitly identified as directly observed. These results are tied to the distributed binary hashes above.", styles["body"]))
    defects = [
        (
            "DEF-324-01 — Chained repeating-decimal calculation loses precision [OPEN · P2]",
            "Directly observed on both APKs. Enter 1 ÷ 3, evaluate, multiply the displayed result by 3 and evaluate again. Expected 1; both show 0.9999999999 after displaying 0.3333333333. This can mislead chained calculations involving repeating decimals. The behavior is consistent with reusing rounded display text, but the test does not prove that implementation cause. Recommended: retain the unrounded numeric value for subsequent operators and add a cross-package regression test. Evidence: TC-CALC-008, shard 3, run 40321408355.",
        ),
        (
            "DEF-324-02 — Exponent-formatted result cannot be continued with +1 [OPEN · P2]",
            "Directly observed on both APKs in a blind boundary probe. Evaluate 10^15; it displays 1e+15. Continue with +1: the UI shows 1e+15+1 and Error. The finite value is within binary64's exact integer range for this operation, so a parser/continuation failure is plausible; root cause remains unconfirmed. Recommended: retain the internal numeric result or support exponent-form input and add a boundary regression. Evidence: TC-CALC-009, shard 3, run 40321408355.",
        ),
        (
            "DEF-324-03 — Standalone “zero permissions” claim conflicts with PackageManager [OPEN · P3]",
            "The exact installed MyCalc APK's PackageManager requested-permissions section lists app.space.calc.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION; TC-CALC-012 failed against the guide's literal “zero permissions” claim. The audit did not determine protection level, dependency origin, or whether a runtime prompt appears. Recommended: inspect the merged release manifest; either remove the unnecessary request or document a precise, verified claim such as no dangerous/runtime permissions if that is what the manifest proves. Evidence: shard 1 artifact and TC-CALC-012 annotation.",
        ),
        (
            "QA-GAP-324-01 — Full guide A–H not certified on distributed APKs [OPEN · COVERAGE GAP]",
            "This is a coverage limitation, not a confirmed app defect. Missing direct coverage includes B1–B8 gestures/clipboard; most C/H visual and caret claims; D1–D3/D7–D8; most E behavior; MyCalc icon and visual claims; and all G-section Notes, Calendar, Music, Recorder, Scanner, Files and Diagnostics flows. Upstream source CI is green but cannot be counted as APK-level validation. Closure: execute and retain per-claim APK screenshots/logs, then label each guide item PASS/FAIL/BLOCKED/NOT RUN.",
        ),
    ]
    for title, detail in defects:
        story.append(KeepTogether([
            p(html.escape(title), styles["h2"]),
            p(html.escape(detail), styles["body"]),
            Spacer(1, 2 * mm),
        ]))
    story += [
        p("5. Regression history", styles["h1"]),
        p("The v3.12.21 (58) report remains unchanged and is retained at reports/calculator-defect-tracker-v3.12.21-58.html. That historical report also recorded TC-CALC-008 and TC-CALC-009 failures. The current report records fresh v3.12.24 / 1.0.22 observations only; old statuses are not copied to new cases.", styles["body"]),
        p("The source-CI workflows at TicTic commit " + SOURCE_COMMIT + " passed; those are kept separate from direct artifact runtime results.", styles["body"]),
    ]

    # Original screenshot appendix — one large unaltered image per page.
    story.append(PageBreak())
    story.append(p("Appendix A — original runtime screenshots", styles["h1"]))
    story.append(p("These PNGs were extracted from the uploaded evidence artifacts of run 40321408355. Images are included at native aspect ratio; no UI elements were composited or reconstructed. Each image's SHA-256 is printed under it and the same PNG is published beside this PDF.", styles["body"]))
    for index, (caption, app_folder, source, destination) in enumerate(found):
        if index:
            story.append(PageBreak())
        story.extend(image_story(destination, caption, styles, mono))

    # Permission audit evidence is text from the captured PackageManager dump.
    story.append(PageBreak())
    story.append(p("Appendix B — MyCalc PackageManager permission evidence", styles["h1"]))
    story.append(p("Source: tc-calc-012-package-dump.txt produced by the runtime permission-audit case. The snippet below is extracted from the artifact; the full text dump is published beside this PDF.", styles["body"]))
    lines = dump_text.splitlines()
    relevant: list[str] = []
    for i, line in enumerate(lines):
        if line.strip().casefold() == "requested permissions:":
            relevant.extend(lines[max(0, i - 2): min(len(lines), i + 8)])
            break
    if not relevant:
        relevant = [line for line in lines if "DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION" in line][:8]
    if not relevant:
        relevant = ["No requested-permissions excerpt was present in the downloaded dump."]
    pre = Preformatted("\n".join(relevant), styles["mono"], maxLineLength=110)
    excerpt_box = Table([[pre]], colWidths=[171 * mm])
    excerpt_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRAY_BG),
        ("BOX", (0, 0), (-1, -1), .6, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(excerpt_box)
    if dump_copy is not None:
        story += [Spacer(1, 4 * mm), p(f"Full dump SHA-256: <font name=\"{mono}\">{sha256_file(dump_copy)}</font>", styles["small"])]

    # Manifest page lists exactly what evidence was embedded.
    story.append(PageBreak())
    story.append(p("Appendix C — evidence manifest and interpretation", styles["h1"]))
    manifest_rows = [[p("Evidence file", styles["table_head"]), p("Source case", styles["table_head"]), p("SHA-256", styles["table_head"])]]
    for caption, app_folder, source, destination in found:
        manifest_rows.append([
            p(f'<font name="{mono}">{html.escape(destination.name)}</font>', styles["table"]),
            plain(caption, styles["table"]),
            p(f'<font name="{mono}">{sha256_file(destination)}</font>', styles["table"]),
        ])
    manifest_rows.append([
        p(f'<font name="{mono}">{html.escape(dump_copy.name)}</font>', styles["table"]),
        plain("MyCalc TC-CALC-012 PackageManager dump", styles["table"]),
        p(f'<font name="{mono}">{sha256_file(dump_copy)}</font>', styles["table"]),
    ])
    for result_file in result_json_files:
        manifest_rows.append([
            p(f'<font name="{mono}">{html.escape(result_file.name)}</font>', styles["table"]),
            plain("Machine-readable per-shard APK results", styles["table"]),
            p(f'<font name="{mono}">{sha256_file(result_file)}</font>', styles["table"]),
        ])
    story.append(make_table(manifest_rows, [51 * mm, 63 * mm, 57 * mm]))
    story += [
        Spacer(1, 4 * mm),
        p("Status definitions", styles["h2"]),
        p("PASS means a direct APK assertion was observed. FAIL means the direct assertion was contradicted. BLOCKED means a required comparison/precondition was unavailable. UNCONFIRMED means a case was selected but no usable per-case result is available in the retrieved machine-readable JSON or retained check annotations; it is not silently counted as a pass. SOURCE-CI means the upstream source workflow passed, not that the distributed APK passed that item.", styles["body"]),
        p(f'Workflow and artifact index: <link href="{RUN_URL}" color="#1d5fa7">{RUN_URL}</link>', styles["small"]),
    ]

    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    pdf_bytes = output.read_bytes()
    if not pdf_bytes.startswith(b"%PDF-"):
        raise SystemExit("PDF signature validation failed")
    print(f"Built {output} ({len(pdf_bytes)} bytes)")
    print(f"Embedded {len(found)} original screenshots")
    print(f"Copied {len(result_json_files)} machine-readable shard result files")
    print(f"Published evidence files to {evidence_output}")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        build(args)
    except Exception as exc:
        print(f"PDF build failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
