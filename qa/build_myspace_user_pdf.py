#!/usr/bin/env python3
"""Build a user-facing APK QA PDF from original GitHub Actions evidence."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
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

SOURCE_COMMIT = "a09e52f2c3f141bfc2d3a95f667a38fcac08b54a"
GUIDE_SHA256 = "a3d0b131c7beb99f8bc12712eebf8c01e5a8873de7996a23f943905768578fc4"
MYSPACE_SHA256 = "7ae98fd05c25554c3b90c32fbc2aeda789c25d0551fab81d071e804106a2a2ad"
MYCALC_SHA256 = "09b1dc8f91ac249643cb92aa74670fdd2db8430af6c0b8c7052d8e906efcf1d4"
GUIDE_URL = "https://github.com/tarungittarun/TicTic/blob/a09e52f2c3f141bfc2d3a95f667a38fcac08b54a/TEST-GUIDE.md"
MYSPACE_URL = "https://github.com/tarungittarun/TicTic/raw/a09e52f2c3f141bfc2d3a95f667a38fcac08b54a/artifacts/MySpace-v3.12.39-76-lite-dist.apk"
MYCALC_URL = "https://github.com/tarungittarun/TicTic/raw/a09e52f2c3f141bfc2d3a95f667a38fcac08b54a/artifacts/MyCalc-v1.0.37-38.apk"
TESTS_RUN_URL = "https://github.com/tarungittarun/TicTic/actions/runs/40504883690"
ANDROID_CI_RUN_URL = "https://github.com/tarungittarun/TicTic/actions/runs/40504883668"

NAVY = colors.HexColor("#18345d")
BLUE = colors.HexColor("#1d5fa7")
PALE = colors.HexColor("#eef4fc")
INK = colors.HexColor("#202a38")
MUTED = colors.HexColor("#5b687a")
GRID = colors.HexColor("#d5deea")
GREEN = colors.HexColor("#146b42")
RED = colors.HexColor("#9f2924")
AMBER = colors.HexColor("#875600")
WHITE = colors.white

STATUS_COLORS = {
    "PASS": GREEN,
    "FAIL": RED,
    "ERROR": RED,
    "BLOCKED": AMBER,
    "NOT RUN": MUTED,
}


class ReportError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True).replace("\n", "<br/>")


def count_status(rows: list[dict[str, Any]]) -> Counter[str]:
    return Counter(str(row.get("status", "NOT RUN")).upper() for row in rows)


def status_badge(status: str, style: ParagraphStyle) -> Paragraph:
    color = STATUS_COLORS.get(status.upper(), MUTED)
    return Paragraph(f'<font color="{color.hexval()}"><b>{esc(status.upper())}</b></font>', style)


def setup_styles() -> tuple[dict[str, ParagraphStyle], str, str]:
    regular, bold = "Helvetica", "Helvetica-Bold"
    candidates = [
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
        (Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"), Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf")),
    ]
    for normal_path, bold_path in candidates:
        if normal_path.exists() and bold_path.exists():
            pdfmetrics.registerFont(TTFont("UserQA-Regular", str(normal_path)))
            pdfmetrics.registerFont(TTFont("UserQA-Bold", str(bold_path)))
            regular, bold = "UserQA-Regular", "UserQA-Bold"
            break
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("UserQATitle", parent=base["Title"], fontName=bold, fontSize=23, leading=28, textColor=NAVY, alignment=TA_LEFT, spaceAfter=8),
        "subtitle": ParagraphStyle("UserQASubtitle", parent=base["Normal"], fontName=regular, fontSize=10.5, leading=15, textColor=MUTED, spaceAfter=8),
        "h1": ParagraphStyle("UserQAH1", parent=base["Heading1"], fontName=bold, fontSize=15, leading=19, textColor=NAVY, spaceBefore=8, spaceAfter=6),
        "h2": ParagraphStyle("UserQAH2", parent=base["Heading2"], fontName=bold, fontSize=10.5, leading=13, textColor=BLUE, spaceBefore=6, spaceAfter=4),
        "body": ParagraphStyle("UserQABody", parent=base["BodyText"], fontName=regular, fontSize=8.5, leading=12, textColor=INK, spaceAfter=5),
        "small": ParagraphStyle("UserQASmall", parent=base["BodyText"], fontName=regular, fontSize=7.2, leading=9.5, textColor=INK, spaceAfter=2),
        "tiny": ParagraphStyle("UserQATiny", parent=base["BodyText"], fontName=regular, fontSize=6.2, leading=8, textColor=INK, spaceAfter=1),
        "table": ParagraphStyle("UserQATable", parent=base["BodyText"], fontName=regular, fontSize=6.7, leading=8.7, textColor=INK, spaceAfter=0),
        "table_head": ParagraphStyle("UserQATableHead", parent=base["BodyText"], fontName=bold, fontSize=6.9, leading=8.5, textColor=WHITE, spaceAfter=0),
        "caption": ParagraphStyle("UserQACaption", parent=base["BodyText"], fontName=regular, fontSize=8, leading=11, textColor=MUTED, alignment=TA_CENTER, spaceBefore=5),
        "callout": ParagraphStyle("UserQACallout", parent=base["BodyText"], fontName=regular, fontSize=9, leading=13, textColor=INK, spaceAfter=0),
        "mono": ParagraphStyle("UserQAMono", parent=base["Code"], fontName="Courier", fontSize=6.4, leading=8, textColor=INK),
        "center": ParagraphStyle("UserQACenter", parent=base["BodyText"], fontName=bold, fontSize=8, leading=10, textColor=NAVY, alignment=TA_CENTER),
    }
    return styles, regular, bold


def para(text: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(esc(text), style)


def table(rows: list[list[Any]], widths: list[float], styles: dict[str, ParagraphStyle], *, header: bool = True, repeat_rows: int = 1) -> Table:
    cooked: list[list[Any]] = []
    for row_index, row in enumerate(rows):
        cooked_row: list[Any] = []
        for value in row:
            if isinstance(value, (Paragraph, Image)):
                cooked_row.append(value)
            else:
                cooked_row.append(para(value, styles["table_head"] if header and row_index == 0 else styles["table"]))
        cooked.append(cooked_row)
    t = Table(cooked, colWidths=widths, repeatRows=repeat_rows if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    for index in range(1 if header else 0, len(rows)):
        if index % 2 == (1 if header else 0):
            commands.append(("BACKGROUND", (0, index), (-1, index), colors.HexColor("#f8fafc")))
    t.setStyle(TableStyle(commands))
    return t


def card_table(cards: list[tuple[str, str, str]], styles: dict[str, ParagraphStyle], width: float) -> Table:
    data = []
    row = []
    for heading, value, note in cards:
        cell = Table([
            [Paragraph(f'<font color="{MUTED.hexval()}"><b>{esc(heading.upper())}</b></font>', styles["tiny"])],
            [Paragraph(f'<font color="{NAVY.hexval()}"><b>{esc(value)}</b></font>', ParagraphStyle("card-value", parent=styles["body"], fontSize=12, leading=15))],
            [para(note, styles["tiny"])],
        ], colWidths=[(width - 12) / 4])
        cell.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE), ("BOX", (0, 0), (-1, -1), 0.6, GRID), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        row.append(cell)
        if len(row) == 4:
            data.append(row)
            row = []
    if row:
        while len(row) < 4:
            row.append("")
        data.append(row)
    t = Table(data, colWidths=[width / 4] * 4, hAlign="LEFT")
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return t


def load_reports(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    files = sorted(root.rglob("user-journey-results.json"))
    if not files:
        raise ReportError(f"No user-journey-results.json found under {root}")
    reports: list[tuple[Path, dict[str, Any]]] = []
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("source", {}).get("commit") != SOURCE_COMMIT:
            raise ReportError(f"Unexpected upstream commit in {path}")
        if data.get("source", {}).get("guide_sha256") != GUIDE_SHA256:
            raise ReportError(f"Guide hash mismatch in {path}")
        artifact = data.get("artifact", {})
        package = artifact.get("package")
        expected_identity = {
            "app.space.one": ("3.12.39", 76, "MySpace-v3.12.39-76-lite-dist.apk", MYSPACE_SHA256),
            "app.space.calc": ("1.0.37", 38, "MyCalc-v1.0.37-38.apk", MYCALC_SHA256),
        }
        if package not in expected_identity:
            raise ReportError(f"Unexpected APK package in {path}: {package!r}")
        version_name, version_code, filename, expected_sha = expected_identity[package]
        if artifact.get("sha256") != expected_sha:
            raise ReportError(f"Unexpected APK SHA-256 in {path}: {artifact.get('sha256')}")
        if artifact.get("version_name") != version_name or artifact.get("version_code") != version_code:
            raise ReportError(f"Installed package version mismatch in {path}: {artifact.get('version_name')} ({artifact.get('version_code')})")
        if artifact.get("file") != filename:
            raise ReportError(f"Unexpected APK filename in {path}: {artifact.get('file')!r}")
        reports.append((path, data))
    return reports


def select_results(reports: list[tuple[Path, dict[str, Any]]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    myspace_calc: list[dict[str, Any]] = []
    mycalc_calc: list[dict[str, Any]] = []
    user_rows: list[dict[str, Any]] = []
    for path, data in reports:
        suite = data.get("suite")
        package = data.get("artifact", {}).get("package")
        if suite == "myspace-core":
            myspace_calc = list(data.get("calculator_results", []))
        elif suite == "myspace-features":
            seen = {row.get("id") for row in myspace_calc}
            myspace_calc.extend(row for row in data.get("calculator_results", []) if row.get("id") not in seen)
        elif suite == "mycalc":
            mycalc_calc = data.get("calculator_results", [])
        for row in data.get("user_results", []):
            item = dict(row)
            item["package"] = package
            item["suite"] = suite
            item["source_dir"] = str(path.parent)
            user_rows.append(item)
    return myspace_calc, mycalc_calc, user_rows


def status_counts_text(rows: list[dict[str, Any]]) -> str:
    counts = count_status(rows)
    order = ("PASS", "FAIL", "ERROR", "BLOCKED", "NOT RUN")
    return " · ".join(f"{counts[s]} {s}" for s in order if counts.get(s)) or "No results"


def make_page_callbacks(source_run: str):
    def draw(canvas, doc):
        canvas.saveState()
        page = canvas.getPageNumber()
        width, height = A4
        if page > 1:
            canvas.setStrokeColor(GRID)
            canvas.setLineWidth(0.5)
            canvas.line(17 * mm, height - 14 * mm, width - 17 * mm, height - 14 * mm)
            canvas.setFont("Helvetica-Bold", 7)
            canvas.setFillColor(NAVY)
            canvas.drawString(17 * mm, height - 11 * mm, "CALCULATOR-FOCUSED APK QA")
            canvas.setFont("Helvetica", 7)
            canvas.setFillColor(MUTED)
            canvas.drawRightString(width - 17 * mm, height - 11 * mm, f"Source run {source_run}")
            canvas.line(17 * mm, 13 * mm, width - 17 * mm, 13 * mm)
            canvas.setFont("Helvetica", 7)
            canvas.drawString(17 * mm, 9 * mm, "Direct release-APK evidence; source-CI labeled separately")
            canvas.drawRightString(width - 17 * mm, 9 * mm, f"Page {page}")
        canvas.restoreState()
    return draw


def locate_image(report: tuple[Path, dict[str, Any]], filename: str) -> Path | None:
    base = report[0].parent
    matches = list(base.rglob(filename))
    return sorted(matches)[0] if matches else None


def permission_observation(report: tuple[Path, dict[str, Any]]) -> tuple[dict[str, Any] | None, str]:
    result = next((row for row in report[1].get("calculator_results", [])
                   if row.get("id") == "TC-CALC-012"), None)
    dump_path = locate_image(report, "tc-calc-012-package-dump.txt")
    if not result:
        return None, "TC-CALC-012 did not produce a per-case result; the guide's permission statement is unverified."
    if not dump_path:
        return result, f"TC-CALC-012 status={result.get('status')}; its PackageManager dump was not found in this artifact."

    lines = dump_path.read_text(encoding="utf-8", errors="replace").splitlines()
    requested: list[str] = []
    for index, line in enumerate(lines):
        if line.strip().casefold() != "requested permissions:":
            continue
        indent = len(line) - len(line.lstrip())
        for entry in lines[index + 1:]:
            if not entry.strip():
                continue
            entry_indent = len(entry) - len(entry.lstrip())
            if entry_indent <= indent:
                break
            value = entry.strip()
            if value.casefold() not in {"none", "<none>"}:
                requested.append(value)
        break

    protection = sorted(set(re.findall(r"prot=([^\s,]+)", "\n".join(lines))))
    runtime_header = next((i for i, line in enumerate(lines)
                           if line.strip().casefold() == "runtime permissions:"), None)
    runtime_entries: list[str] = []
    if runtime_header is not None:
        indent = len(lines[runtime_header]) - len(lines[runtime_header].lstrip())
        for entry in lines[runtime_header + 1:]:
            if not entry.strip():
                continue
            entry_indent = len(entry) - len(entry.lstrip())
            if entry_indent <= indent:
                break
            runtime_entries.append(entry.strip())
        runtime = "empty" if not runtime_entries else "; ".join(runtime_entries[:8])
    else:
        runtime = "not reported as a separate section in the captured dump"

    requested_text = "; ".join(requested) if requested else "none listed"
    protection_text = "; ".join(protection) if protection else "not identified in captured dump"
    summary = (
        f"TC-CALC-012 {result.get('status')}: requested={requested_text}; "
        f"protection level(s)={protection_text}; runtime section={runtime}. "
        "This is PackageManager manifest/package evidence; the screen flow did not test a system permission prompt."
    )
    return result, summary


def embed_image(path: Path, caption: str, styles: dict[str, ParagraphStyle], max_width: float, max_height: float) -> list[Any]:
    image_reader = ImageReader(str(path))
    width, height = image_reader.getSize()
    scale = min(max_width / width, max_height / height)
    image = Image(str(path), width=width * scale, height=height * scale, hAlign="CENTER")
    return [image, Paragraph(esc(caption), styles["caption"]), Spacer(1, 5)]


def publish_evidence(reports: list[tuple[Path, dict[str, Any]]], destination: Path) -> tuple[list[dict[str, Any]], list[Path]]:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    images: list[Path] = []
    for index, (result_path, data) in enumerate(reports, start=1):
        suite = re.sub(r"[^a-z0-9_-]+", "-", str(data.get("suite", "suite")).lower())
        app = "myspace" if data.get("artifact", {}).get("package") == "app.space.one" else "mycalc"
        base = result_path.parent
        for src in sorted(base.rglob("*")):
            if not src.is_file() or src.suffix.lower() not in {".png", ".xml", ".json", ".md", ".txt", ".log"}:
                continue
            relative = src.relative_to(base)
            safe = re.sub(r"[^A-Za-z0-9._-]+", "-", relative.as_posix()).strip("-")
            target = destination / "raw" / f"{index}-{suite}" / safe
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            file_hash = sha256(target)
            manifest.append({
                "suite": suite,
                "app": app,
                "source_relative_path": relative.as_posix(),
                "published_path": target.relative_to(destination).as_posix(),
                "bytes": target.stat().st_size,
                "sha256": file_hash,
            })
            if target.suffix.lower() == ".png":
                images.append(target)
    manifest_path = destination / "evidence-manifest.json"
    manifest_path.write_text(json.dumps({"source_commit": SOURCE_COMMIT, "files": manifest}, indent=2) + "\n", encoding="utf-8")
    inputs = {
        "guide": {"url": GUIDE_URL, "sha256": GUIDE_SHA256},
        "source_commit": SOURCE_COMMIT,
        "myspace_apk": {"url": MYSPACE_URL, "sha256": MYSPACE_SHA256},
        "mycalc_apk": {"url": MYCALC_URL, "sha256": MYCALC_SHA256},
    }
    (destination / "pinned-inputs.json").write_text(json.dumps(inputs, indent=2) + "\n", encoding="utf-8")
    return manifest, images


def build(args: argparse.Namespace) -> None:
    root = args.artifact_root
    reports = load_reports(root)
    by_suite = {data.get("suite"): (path, data) for path, data in reports}
    for required in ("myspace-core", "myspace-features", "mycalc"):
        if required not in by_suite:
            raise ReportError(f"Missing required suite evidence: {required}")
    myspace_calc, mycalc_calc, user_rows = select_results(reports)
    manifest, published_images = publish_evidence(reports, args.evidence_output)
    styles, _, _ = setup_styles()
    page_width, page_height = A4
    available_width = page_width - 34 * mm
    image_width = available_width - 10 * mm
    image_height = page_height - 56 * mm

    user_counts = count_status(user_rows)
    myspace_counts = count_status(myspace_calc)
    mycalc_counts = count_status(mycalc_calc)
    myspace_data = by_suite["myspace-core"][1]
    mycalc_data = by_suite["mycalc"][1]
    device = "Android 14 / API 34 emulator"
    total_screens = sum(1 for path in published_images if path.suffix.lower() == ".png")
    source_run = str(args.source_run_id)

    doc = SimpleDocTemplate(
        str(args.output), pagesize=A4, rightMargin=17 * mm, leftMargin=17 * mm,
        topMargin=19 * mm, bottomMargin=18 * mm,
        title="MySpace 3.12.39 / MyCalc 1.0.37 calculator-focused APK QA",
        author="Arena Agent Mode QA",
        subject="Direct black-box Android APK testing with original screenshots and provenance",
    )
    story: list[Any] = []
    story.append(Paragraph("MySpace 3.12.39 (76)<br/>Standalone MyCalc 1.0.37 (38)", styles["title"]))
    story.append(Paragraph("Calculator-only Android APK QA · direct user journeys, findings, and coverage boundaries", styles["subtitle"]))
    story.append(Paragraph(f"<b>REPORT DATE:</b> 27 OCTOBER 2026&nbsp;&nbsp; | &nbsp;&nbsp;<b>DEVICE:</b> {device}&nbsp;&nbsp; | &nbsp;&nbsp;<b>DIRECT RUN:</b> {esc(source_run)}", styles["small"]))
    story.append(Spacer(1, 5))

    cards = [
        ("MySpace calculator", status_counts_text(myspace_calc), f"{len(myspace_calc)} selected direct APK cases"),
        ("MyCalc calculator", status_counts_text(mycalc_calc), f"{len(mycalc_calc)} selected direct APK cases"),
        ("Calculator UI flows", status_counts_text(user_rows), f"{len(user_rows)} calculator-only probes across 3 jobs"),
        ("Screenshots", str(total_screens), "original emulator PNGs preserved; selected screens embedded below"),
    ]
    story.append(card_table(cards, styles, available_width))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Executive readout", styles["h1"]))
    story.append(Paragraph(
        "This report stays on the <b>calculator UI</b>: entering and editing expressions, trying selection and clipboard actions, storing/using memory, replaying history, and changing calculator options such as key shape, effects, and theme. It does not test Notes, Scanner, Calendar, or other MySpace apps. Every direct finding is tied to the APK SHA-256, pinned guide snapshot, Android Actions run, and saved screenshot/UI hierarchy. Where a floating control is absent from Android's accessibility tree, the test uses screenshot OCR or labels the probe BLOCKED rather than inventing a failure.", styles["body"]
    ))
    story.append(Paragraph(
        "<b>Interpretation rule:</b> PASS/FAIL are direct assertions against the installed binaries. BLOCKED means the emulator or accessibility surface prevented a fair assertion. NOT RUN means no direct APK test was attempted. Upstream source-CI successes or failures are reported separately and never converted into APK outcomes.", styles["body"]
    ))
    story.append(Paragraph("Build identity and provenance", styles["h1"]))
    identity_rows = [
        ["Artifact", "Package / version", "Size", "SHA-256"],
        ["MySpace-v3.12.39-76-lite-dist.apk", "app.space.one · 3.12.39 (76)", f"{myspace_data['artifact'].get('size_bytes', 0):,} bytes", MYSPACE_SHA256],
        ["MyCalc-v1.0.37-38.apk", "app.space.calc · 1.0.37 (38)", f"{mycalc_data['artifact'].get('size_bytes', 0):,} bytes", MYCALC_SHA256],
        ["TEST-GUIDE.md", f"source commit {SOURCE_COMMIT}", "13,555 bytes", GUIDE_SHA256],
    ]
    story.append(table(identity_rows, [54 * mm, 42 * mm, 24 * mm, available_width - 120 * mm], styles))
    story.append(Paragraph(
        "<b>Version alignment:</b> The guide copy pasted into chat is headed MySpace 3.12.23 (60) / MyCalc 1.0.21 (22), older than the supplied MySpace APK. To avoid cross-release claims, this run uses the matching guide at the pinned source commit above, headed MySpace 3.12.39 (76) / MyCalc 1.0.37 (38).",
        styles["small"],
    ))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        f"<b>Guide:</b> <link href='{GUIDE_URL}' color='{BLUE.hexval()}'>pinned A–H user test guide</link><br/>"
        f"<b>MySpace APK:</b> <link href='{MYSPACE_URL}' color='{BLUE.hexval()}'>download exact tested binary</link><br/>"
        f"<b>Standalone MyCalc APK:</b> <link href='{MYCALC_URL}' color='{BLUE.hexval()}'>download exact tested binary</link><br/>"
        f"<b>Direct user-journey run:</b> <link href='https://github.com/tarungittarun/AIA-/actions/runs/{source_run}' color='{BLUE.hexval()}'>open run {source_run} and original job artifacts</link>", styles["small"]
    ))
    story.append(Paragraph(
        "Both APKs and the guide were SHA-256 verified in Actions before installation; APK ZIP-integrity checks passed. Device PackageManager version identity was recorded in the per-shard JSON. The user-journey workflow used three Android emulator jobs (max-parallel 3), within the requested 30-job ceiling.", styles["body"]
    ))

    story.append(PageBreak())
    story.append(Paragraph("1. Direct calculator results", styles["h1"]))
    story.append(Paragraph("MySpace · app.space.one · 3.12.39 (76)", styles["h2"]))
    rows = [["Case", "Status", "Expected", "Observed / user-visible note"]]
    for row in myspace_calc:
        rows.append([row.get("id", ""), status_badge(str(row.get("status", "")), styles["table"]), row.get("expected", ""), f"{row.get('actual', '')}\n{row.get('comment', '')}"])
    story.append(table(rows, [20 * mm, 18 * mm, 39 * mm, available_width - 77 * mm], styles))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Standalone MyCalc · app.space.calc · 1.0.37 (38)", styles["h2"]))
    rows = [["Case", "Status", "Expected", "Observed / user-visible note"]]
    for row in mycalc_calc:
        rows.append([row.get("id", ""), status_badge(str(row.get("status", "")), styles["table"]), row.get("expected", ""), f"{row.get('actual', '')}\n{row.get('comment', '')}"])
    story.append(table(rows, [20 * mm, 18 * mm, 39 * mm, available_width - 77 * mm], styles))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "The APK suite includes arithmetic, scientific-key, history persistence/replay and the two retained blind boundary probes. The official Google Calculator comparison is not a pass unless its official package is installed; no AOSP substitute is used. For MyCalc, TC-CALC-012 reports the installed package's requested-permission list; see the detailed note below.", styles["small"]
    ))

    story.append(PageBreak())
    story.append(Paragraph("2. Calculator-only journeys and observations", styles["h1"]))
    story.append(Paragraph(
        "These tests are driven through UIAutomator/adb taps and touchscreen gestures on the installed calculator APKs. Floating selection and caret toolbars are inspected from screenshots because the Android accessibility tree can omit them. Screenshots and UI hierarchy XML remain in the evidence bundle; source-CI results are not counted as APK outcomes.", styles["body"]
    ))
    for title, suite in (("MySpace calculator input/editing", "myspace-core"), ("MySpace calculator memory/customization", "myspace-features"), ("Standalone MyCalc calculator", "mycalc")):
        group = [row for row in user_rows if row.get("suite") == suite]
        if not group:
            continue
        story.append(Paragraph(title, styles["h2"]))
        rows = [["Guide", "Status", "User action", "Observed / limitation"]]
        for row in group:
            observed = str(row.get("actual", ""))
            comment = str(row.get("comment", ""))
            rows.append([
                row.get("guide_section", ""),
                status_badge(str(row.get("status", "")), styles["table"]),
                row.get("title", ""),
                (observed + "\n" + comment).strip(),
            ])
        story.append(table(rows, [17 * mm, 17 * mm, 47 * mm, available_width - 81 * mm], styles))
        story.append(Spacer(1, 5))

    story.append(PageBreak())
    story.append(Paragraph("3. Calculator-guide coverage: what this run proves", styles["h1"]))
    coverage = [
        ["Guide", "Direct calculator evidence", "Boundary / not claimed"],
        ["B · Editing/memory", "Long-press selection is screenshot-OCR checked; in-calculator copy/paste and cut are attempted; AC clear, tap-to-release plus caret insertion, mid-number insertion, caret menu, and both selected-value replacement and empty-caret MUse are probed.", "B2 continuous hold-then-drag is blocked if adb cannot reproduce the app's custom hold gesture. Handle dragging, all margins, scroll arbitration, and external-app paste are not claimed unless their rows pass."],
        ["C · Expression", "No-keyboard check, key-shape and key-theme pickers, calculator entry/editing, percent and scientific-key examples are reported from installed APK actions.", "Pixel-level caret blink, exact LED colors, whole-line autoscroll, every bracket/cursor edge case, and exhaustive verification of all eight key-theme choices are not certified."],
        ["D · Calculator", "Selected D1–D9 behavior, history replay, arithmetic and scientific cases are exercised on the installed binaries; observed values are in the result tables.", "D10 timing/race and an official Google Calculator comparison are not claimed as passes; no AOSP substitute is used."],
        ["E · History/effects", "History persistence/replay, calculator memory list, overflow actions, and opening/selecting an Effects option are probed.", "Memory reordering and frame-by-frame animation behavior are not claimed unless explicitly observed in the run."],
        ["F · Standalone", "The standalone MyCalc binary is directly launched and its calculator flows are tested; its requested permissions come from the installed PackageManager dump.", "The guide's literal zero-requested-permissions wording is checked separately from dangerous/runtime permission prompts."],
        ["H · Theme/caret", "Light and Dark selections are applied through calculator-related settings; stable app-screen pixels are compared and both screenshots retained. The expression may reset while navigating settings.", "Exact theme palette, caret color, and instant ink re-resolution are not pixel-certified by this broad visual comparison."],
    ]
    story.append(table(coverage, [31 * mm, 72 * mm, available_width - 103 * mm], styles))
    story.append(Spacer(1, 7))
    story.append(Paragraph(
        "<b>Ads:</b> The label scan is limited to sampled calculator screens. A clean visible-text scan is not a network-level, whole-app or third-party SDK audit; this report does not make a broader ad-free certification.", styles["body"]
    ))
    story.append(Paragraph(
        "<b>Source-CI context (separate evidence):</b> At the pinned source commit, the upstream <link href='{0}' color='{1}'>Tests workflow</link> completed with a failure in its UI emulator end-to-end job; its source-contract and JVM unit/end-to-end jobs passed. The <link href='{2}' color='{1}'>Android CI workflow</link> succeeded for Python source contracts and the debug build. These are source-level results—not direct tests of the distributed APKs—and are not counted as APK outcomes.".format(TESTS_RUN_URL, BLUE.hexval(), ANDROID_CI_RUN_URL), styles["body"]
    ))

    story.append(PageBreak())
    story.append(Paragraph("4. Detailed defect / risk notes", styles["h1"]))
    failed_calc = [row for row in myspace_calc + mycalc_calc if str(row.get("status", "")).upper() in {"FAIL", "ERROR"}]
    failed_user = [row for row in user_rows if str(row.get("status", "")).upper() in {"FAIL", "ERROR"}]
    if not failed_calc and not failed_user:
        story.append(Paragraph("No direct FAIL/ERROR was reported by the selected probes. This is a bounded user-flow smoke result, not a release certification; see the explicit untested coverage boundaries.", styles["body"]))
    for row in failed_calc:
        title = f"{row.get('id', 'Calculator case')} · {row.get('title', '')} · {row.get('status', '')}"
        actual = row.get("actual", "")
        comment = row.get("comment", "")
        story.append(KeepTogether([
            Paragraph(esc(title), styles["h2"]),
            Paragraph(f"<b>Expected:</b> {esc(row.get('expected', ''))}<br/><b>Observed:</b> {esc(actual)}<br/><b>QA interpretation:</b> {esc(comment)}", styles["body"]),
        ]))
    for row in failed_user:
        story.append(KeepTogether([
            Paragraph(esc(f"{row.get('id', '')} · {row.get('title', '')} · {row.get('status', '')}"), styles["h2"]),
            Paragraph(f"<b>Expected:</b> {esc(row.get('expected', ''))}<br/><b>Observed:</b> {esc(row.get('actual', ''))}<br/><b>QA note:</b> {esc(row.get('comment', ''))}", styles["body"]),
        ]))
    story.append(Paragraph("MyCalc permission wording", styles["h2"]))
    permission_result, permission_text = permission_observation(by_suite["mycalc"])
    if permission_result:
        permission_status = str(permission_result.get("status", "NOT RUN")).upper()
        if permission_status == "FAIL":
            permission_interpretation = "The literal “zero requested permissions” claim conflicts with the installed APK's PackageManager list."
        elif permission_status == "PASS":
            permission_interpretation = "The strict zero-requested-permissions claim matched the PackageManager result for this APK."
        else:
            permission_interpretation = "The zero-permissions claim was not conclusively resolved by this run."
        story.append(Paragraph(
            f"<b>TC-CALC-012:</b> <font color=\"{STATUS_COLORS.get(permission_status, MUTED).hexval()}\"><b>{esc(permission_status)}</b></font><br/>"
            f"<b>Direct dump interpretation:</b> {esc(permission_text)}<br/>"
            f"<b>Guide claim:</b> {esc(permission_interpretation)} Runtime prompt behavior was not exercised by this PackageManager audit; the test does not infer that any listed permission is dangerous.", styles["body"]
        ))
    else:
        story.append(Paragraph("TC-CALC-012 was not present in the MyCalc case output; the permission claim remains unverified in this run.", styles["body"]))
    story.append(Paragraph("Important environment boundary", styles["h2"]))
    story.append(Paragraph(
        "Android 14 emulator input and accessibility exposure can differ from a physical touch. BLOCKED/ERROR is not treated as a confirmed product defect without a clear app-controlled failure; an unexecuted guide step stays untested. This report intentionally excludes Notes, Scanner, and all other non-calculator app workflows. Runner logcat is supplemental evidence, not a substitute for product behavior; no external app/share target is used.", styles["body"]
    ))

    priority_files = [
        ("myspace-core", "user-b1.png", "B1 · selection toolbar, verified from screenshot OCR"),
        ("myspace-core", "user-b2.png", "B2 · hold-then-drag result / emulator limitation"),
        ("myspace-core", "user-b4.png", "B4 · in-calculator copy/paste"),
        ("myspace-core", "user-b5.png", "B5 · cut then type"),
        ("myspace-core", "user-b6.png", "B6 · tap inside selection to release it and insert at the caret"),
        ("myspace-core", "user-b9.png", "B9 · mid-number caret insertion"),
        ("myspace-core", "user-b11.png", "B11 · empty-box caret menu"),
        ("myspace-core", "h1-light-theme.png", "H1 · Light theme screenshot"),
        ("myspace-core", "h2-dark-theme.png", "H2 · Dark theme screenshot"),
        ("myspace-core", "user-c10.png", "C10 · key-shape picker"),
        ("myspace-features", "user-b12.png", "B12 · MAdd then selected-operand MUse result"),
        ("myspace-features", "user-b12-caret.png", "B12 · empty-caret MUse insertion result"),
        ("myspace-features", "user-b12-caret-menu.png", "B12 · caret menu exposes MUse and Paste"),
        ("myspace-features", "user-c11-key-theme-rose.png", "C11 · calculator after selecting the Rose key theme"),
        ("myspace-features", "user-e3-memory.png", "E3 · calculator memory list"),
        ("myspace-features", "user-e4.png", "E4 · effects picker and selection"),
        ("myspace-features", "user-c11.png", "C11 · key-theme selection outcome"),
        ("mycalc", "user-f-header.png", "F · standalone MyCalc screen"),
        ("mycalc", "user-b1.png", "MyCalc · selection toolbar, verified from screenshot OCR"),
        ("mycalc", "user-b9.png", "MyCalc · OCR-targeted mid-number insertion"),
        ("mycalc", "h1-light-theme.png", "MyCalc · Light theme screenshot"),
        ("mycalc", "h2-dark-theme.png", "MyCalc · Dark theme screenshot"),
        ("mycalc", "user-b12.png", "MyCalc · MAdd/MUse round-trip"),
        ("mycalc", "user-e3-memory.png", "MyCalc · memory list"),
        ("mycalc", "tc-calc-012-package-dump.txt", "MyCalc · PackageManager permission dump"),
        ("myspace-core", "tc-calc-008-target.png", "MySpace · chained precision case"),
        ("myspace-core", "tc-calc-009-target.png", "MySpace · exponent continuation case"),
        ("myspace-core", "tc-calc-011-replay-result.png", "MySpace · grouped history replay"),
    ]
    image_specs: list[tuple[Path, str]] = []
    for suite, filename, caption in priority_files:
        source_report = by_suite.get(suite)
        if not source_report:
            continue
        source = locate_image(source_report, filename)
        if source and source.suffix.lower() == ".png":
            # Publish paths are prefixed by suite index; match the copied file by suffix.
            matches = [path for path in published_images if filename in path.name and suite in str(path.parent)]
            image_path = matches[0] if matches else None
            if image_path:
                image_specs.append((image_path, caption))
        elif source and filename.endswith(".txt"):
            raw_text = source.read_text(encoding="utf-8", errors="replace")
            story.append(PageBreak())
            story.append(Paragraph(caption, styles["h1"]))
            story.append(Paragraph("Extract from the original runtime artifact; complete dump is in the published evidence folder.", styles["body"]))
            story.append(Preformatted(raw_text[:9500], styles["mono"]))

    if image_specs:
        story.append(PageBreak())
        story.append(Paragraph("5. Original screenshot evidence", styles["h1"]))
        story.append(Paragraph(f"{len(published_images)} original PNGs were copied from this Actions run's artifacts. The selected screens below are embedded directly; the evidence manifest includes SHA-256 hashes for screenshots, hierarchies and JSON files.", styles["body"]))
        for index, (image_path, caption) in enumerate(image_specs):
            if index:
                story.append(PageBreak())
            story.extend(embed_image(image_path, caption + f" · SHA-256 {sha256(image_path)}", styles, image_width, image_height))

    story.append(PageBreak())
    story.append(Paragraph("6. Machine-evidence manifest and reproducibility", styles["h1"]))
    story.append(Paragraph(
        f"The published sidecar folder contains {len(reports)} per-job user journey JSON reports, their calculator-case JSON outputs, markdown summaries, original screenshots, UI hierarchy XML, and an evidence-manifest.json with byte sizes and SHA-256 hashes. Use the single PDF link for the readable report; the linked GitHub run and report-folder sidecars provide raw rerun proof.", styles["body"]
    ))
    manifest_rows = [["Suite", "App", "Evidence files", "Screenshots"]]
    for path, data in reports:
        suite = str(data.get("suite", ""))
        app_name = "MySpace" if data.get("artifact", {}).get("package") == "app.space.one" else "MyCalc"
        files = [row for row in manifest if row.get("suite") == suite]
        pngs = [row for row in files if row.get("published_path", "").lower().endswith(".png")]
        manifest_rows.append([suite, app_name, str(len(files)), str(len(pngs))])
    story.append(table(manifest_rows, [48 * mm, 33 * mm, 35 * mm, available_width - 116 * mm], styles))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Method:</b> three API 34 emulator shards, screenshot capture after user actions, visible UI labels and hierarchy evidence where available, per-case JSON outputs, exact binary SHA verification, and a pinned guide/source commit. The app's source tests are useful corroboration only; this report's PASS/FAIL statuses come from direct installed APK interactions.", styles["body"]
    ))

    callback = make_page_callbacks(source_run)
    doc.build(story, onFirstPage=callback, onLaterPages=callback)
    print(f"Built {args.output} ({args.output.stat().st_size:,} bytes)")
    print(f"Copied {len(manifest)} evidence files, including {len(published_images)} original screenshots to {args.evidence_output}")
    print(f"Direct calculator totals: MySpace {status_counts_text(myspace_calc)}; MyCalc {status_counts_text(mycalc_calc)}")
    print(f"User journey totals: {status_counts_text(user_rows)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    parser.add_argument("--source-run-id", required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        build(args)
    except Exception as exc:
        raise SystemExit(f"PDF build failed: {type(exc).__name__}: {exc}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
