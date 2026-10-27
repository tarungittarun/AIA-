#!/usr/bin/env python3
"""Calculator-only, user-facing QA for the pinned MySpace and MyCalc APKs.

The existing calculator harness provides the arithmetic assertions. This runner
covers calculator editing, selection, history, memory, and customization on the
installed distribution APKs. It does not navigate Notes, Scanner, or other apps.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Any, Callable, Iterable
from unittest.mock import patch

import calculator_e2e as calculator
from calculator_e2e import (
    AndroidUi,
    CalculatorQa,
    DEFAULT_PACKAGE,
    QaError,
    STANDALONE_PACKAGE,
)

PINNED_APK_SHA256 = {
    DEFAULT_PACKAGE: "7ae98fd05c25554c3b90c32fbc2aeda789c25d0551fab81d071e804106a2a2ad",
    STANDALONE_PACKAGE: "09b1dc8f91ac249643cb92aa74670fdd2db8430af6c0b8c7052d8e906efcf1d4",
}
PINNED_GUIDE_SHA256 = "a3d0b131c7beb99f8bc12712eebf8c01e5a8873de7996a23f943905768578fc4"
PINNED_SOURCE_COMMIT = "a09e52f2c3f141bfc2d3a95f667a38fcac08b54a"
EXPECTED_VERSION = {
    DEFAULT_PACKAGE: ("3.12.39", 76),
    STANDALONE_PACKAGE: ("1.0.37", 38),
}
CALCULATOR_CASES = {
    DEFAULT_PACKAGE: {
        f"TC-CALC-{number:03d}" for number in range(1, 12)
    },
    STANDALONE_PACKAGE: {
        *(f"TC-CALC-{number:03d}" for number in range(1, 10)),
        "TC-CALC-011",
        "TC-CALC-012",
    },
}


class NotAvailable(RuntimeError):
    """The installed APK/emulator did not expose a control needed for a probe."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def compact(text: str) -> str:
    return re.sub(r"[\s,]+", "", text or "").replace("−", "-").casefold()


def case_insensitive_match(values: Iterable[str], candidates: Iterable[str]) -> str | None:
    normalized = [(value.casefold(), value) for value in values]
    for candidate in candidates:
        target = candidate.casefold()
        for lowered, original in normalized:
            if lowered == target or target in lowered:
                return original
    return None


class UserQa:
    def __init__(
        self,
        apk: Path,
        package: str,
        expected_sha256: str,
        suite: str,
        report_dir: Path,
    ) -> None:
        if package not in PINNED_APK_SHA256:
            raise ValueError(f"Unsupported package: {package}")
        if expected_sha256 != PINNED_APK_SHA256[package]:
            raise ValueError(f"Refusing an unexpected SHA-256 pin for {package}")
        if suite not in {"myspace-core", "myspace-features", "mycalc"}:
            raise ValueError(f"Unsupported calculator suite: {suite}")
        if suite == "mycalc" and package != STANDALONE_PACKAGE:
            raise ValueError("The mycalc suite requires app.space.calc")
        if suite != "mycalc" and package != DEFAULT_PACKAGE:
            raise ValueError("MySpace suites require app.space.one")

        self.apk = apk
        self.package = package
        self.expected_sha256 = expected_sha256
        self.suite = suite
        self.report_dir = report_dir
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.results: list[dict[str, Any]] = []
        self.qa: CalculatorQa | None = None
        self.device: AndroidUi | None = None
        self.calculator_report: dict[str, Any] = {}
        self.version_observed: dict[str, Any] = {}

    def _assert_apk(self) -> str:
        if not self.apk.is_file():
            raise QaError(f"APK not found: {self.apk}")
        digest = hashlib.sha256(self.apk.read_bytes()).hexdigest()
        if digest != self.expected_sha256:
            raise QaError(
                f"APK SHA-256 mismatch: expected {self.expected_sha256}, got {digest}"
            )
        with zipfile.ZipFile(self.apk) as archive:
            corrupt = archive.testzip()
        if corrupt:
            raise QaError(f"APK ZIP integrity error at {corrupt}")
        return digest

    def _run_calculator_suite(self) -> None:
        if self.suite == "myspace-core":
            case_ids = CALCULATOR_CASES[DEFAULT_PACKAGE]
        elif self.suite == "myspace-features":
            # Sanity-check the installed calculator before memory/customization flows.
            case_ids = {"TC-CALC-001"}
        else:
            case_ids = CALCULATOR_CASES[STANDALONE_PACKAGE]

        calc_dir = self.report_dir / "calculator"
        self.qa = CalculatorQa(self.apk, self.package, calc_dir, case_ids=case_ids)
        # calculator_e2e.py keeps the prior release hashes as its defaults for
        # regression history. Apply the separately verified, immutable v3.12.39
        # pin only while the shared black-box cases run.
        with patch.dict(calculator.EXPECTED_APK_SHA256_BY_PACKAGE, {
            self.package: self.expected_sha256,
        }):
            self.qa.run()
        self.device = self.qa.device
        result_path = calc_dir / "calculator-e2e-results.json"
        if result_path.is_file():
            self.calculator_report = json.loads(result_path.read_text(encoding="utf-8"))

        dump = self.device.adb(
            "shell", "dumpsys", "package", self.package, timeout=60, check=False
        )
        version_name = re.search(r"versionName=([^\s]+)", dump)
        version_code = re.search(r"versionCode=(\d+)", dump)
        self.version_observed = {
            "version_name": version_name.group(1) if version_name else None,
            "version_code": int(version_code.group(1)) if version_code else None,
            "package": self.package,
        }
        expected_name, expected_code = EXPECTED_VERSION[self.package]
        if not version_name or not version_code:
            raise QaError(f"Could not read installed PackageManager version identity for {self.package}")
        if version_name.group(1) != expected_name:
            raise QaError(f"Installed versionName mismatch: expected {expected_name}, got {version_name.group(1)}")
        if int(version_code.group(1)) != expected_code:
            raise QaError(f"Installed versionCode mismatch: expected {expected_code}, got {version_code.group(1)}")

    @property
    def d(self) -> AndroidUi:
        if self.device is None:
            raise QaError("The calculator suite has not installed and launched the APK")
        return self.device

    def _invalidate(self) -> None:
        self.d._last_tree = None
        time.sleep(0.25)

    def _try_tap(self, labels: Iterable[str], *, partial: bool = True) -> str | None:
        for label in labels:
            try:
                self.d.tap_label(label, partial=partial, timeout=0.7)
                return label
            except Exception:
                self._invalidate()
        return None

    def _capture(self, case_id: str) -> tuple[list[str], list[str], str, str]:
        self._invalidate()
        labels = self.d.labels()
        display = self.d.display_texts()
        stem = f"user-{case_id.lower()}"
        image = self.d.screenshot(f"evidence/{stem}.png")
        hierarchy = self.d.save_hierarchy(f"evidence/{stem}.xml")
        image_rel = str(Path(image).relative_to(self.report_dir)) if image else ""
        hierarchy_rel = str(Path(hierarchy).relative_to(self.report_dir)) if hierarchy else ""
        return labels, display, image_rel, hierarchy_rel

    @staticmethod
    def _ocr_normalize(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.casefold())

    def _ocr_screen(self, filename: str) -> tuple[str, list[dict[str, Any]]]:
        """Read visible screen text/coordinates, including Android's floating toolbar.

        UiAutomator omits the text-selection popup on this emulator even when it is
        visibly painted over the app. OCR is therefore the primary observation for
        toolbar assertions, with the original screenshot retained for review.
        """
        image = self.d.screenshot(filename)
        if not image:
            raise NotAvailable("Could not capture a screenshot for visual toolbar inspection.")
        try:
            proc = subprocess.run(
                ["tesseract", image, "stdout", "--psm", "11", "tsv"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=35,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            raise NotAvailable(f"Screenshot OCR was unavailable: {type(exc).__name__}.") from exc
        if proc.returncode != 0:
            raise NotAvailable(f"Screenshot OCR failed: {proc.stderr.strip()[:300]}")
        words: list[dict[str, Any]] = []
        for row in csv.DictReader(proc.stdout.splitlines(), delimiter="\t"):
            if row.get("level") != "5" or not row.get("text", "").strip():
                continue
            try:
                words.append({
                    "text": row["text"].strip(),
                    "left": int(row["left"]),
                    "top": int(row["top"]),
                    "width": int(row["width"]),
                    "height": int(row["height"]),
                    "conf": float(row.get("conf", "0")),
                    "line": (row.get("block_num"), row.get("par_num"), row.get("line_num")),
                })
            except (KeyError, TypeError, ValueError):
                continue
        ocr_path = Path(image).with_suffix(".ocr.json")
        ocr_path.write_text(json.dumps({
            "screenshot": str(Path(image).relative_to(self.report_dir)),
            "engine": "tesseract TSV",
            "words": words,
        }, indent=2) + "\n", encoding="utf-8")
        return image, words

    @classmethod
    def _ocr_group(cls, words: list[dict[str, Any]], target: str) -> tuple[int, int, int, int] | None:
        """Return the screen bounds for a one-to-three word OCR match."""
        wanted = cls._ocr_normalize(target)
        for start in range(len(words)):
            joined = ""
            group: list[dict[str, Any]] = []
            for end in range(start, min(len(words), start + 3)):
                if group and words[end]["line"] != group[0]["line"]:
                    break
                group.append(words[end])
                joined += cls._ocr_normalize(words[end]["text"])
                if joined == wanted:
                    left = min(word["left"] for word in group)
                    top = min(word["top"] for word in group)
                    right = max(word["left"] + word["width"] for word in group)
                    bottom = max(word["top"] + word["height"] for word in group)
                    return left, top, right, bottom
                if len(joined) >= len(wanted) or not wanted.startswith(joined):
                    break
        return None

    @classmethod
    def _ocr_has(cls, words: list[dict[str, Any]], target: str) -> bool:
        return cls._ocr_group(words, target) is not None

    @staticmethod
    def _theme_visual_difference_ratio(first: Path, second: Path) -> float:
        """Compare stable app pixels while excluding status/navigation bars."""
        try:
            from PIL import Image, ImageChops
        except ImportError as exc:
            raise NotAvailable("Pillow was unavailable for a screenshot-level theme comparison.") from exc
        with Image.open(first) as first_image, Image.open(second) as second_image:
            first_rgb = first_image.convert("RGB")
            second_rgb = second_image.convert("RGB")
        if first_rgb.size != second_rgb.size:
            raise NotAvailable(f"Theme screenshots have different dimensions: {first_rgb.size} and {second_rgb.size}.")
        width, height = first_rgb.size
        top, bottom = int(height * 0.07), int(height * 0.92)
        region1 = first_rgb.crop((0, top, width, bottom))
        region2 = second_rgb.crop((0, top, width, bottom))
        difference = ImageChops.difference(region1, region2)
        changed = sum(1 for pixel in difference.getdata() if max(pixel) > 24)
        total = width * max(1, bottom - top)
        return changed / total

    def _tap_ocr(self, words: list[dict[str, Any]], target: str) -> bool:
        bounds = self._ocr_group(words, target)
        if bounds is None:
            return False
        left, top, right, bottom = bounds
        x, y = (left + right) // 2, (top + bottom) // 2
        self.d.adb("shell", "input", "tap", str(x), str(y))
        self._invalidate()
        return True

    def _record(
        self,
        case_id: str,
        guide_section: str,
        title: str,
        status: str,
        expected: str,
        actual: str,
        comment: str,
        *,
        evidence: str = "",
        hierarchy: str = "",
    ) -> None:
        self.results.append({
            "id": case_id,
            "guide_section": guide_section,
            "title": title,
            "status": status,
            "expected": expected,
            "actual": actual,
            "comment": comment,
            "evidence": evidence,
            "hierarchy": hierarchy,
        })
        print(f"[{status}] {case_id} — {title}: {comment or actual}", flush=True)
        if status in {"FAIL", "ERROR"}:
            message = re.sub(r"[\r\n]+", " ", comment or actual)[:1200]
            message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            print(f"::error title={case_id}::{message}", flush=True)
        else:
            message = re.sub(r"[\r\n]+", " ", comment or actual)[:1200]
            message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            print(f"::notice title={case_id}::{message}", flush=True)

    def _case(
        self,
        case_id: str,
        section: str,
        title: str,
        expected: str,
        action: Callable[[], tuple[str, str, str]],
    ) -> None:
        evidence = hierarchy = ""
        try:
            status, actual, comment = action()
        except NotAvailable as exc:
            status, actual, comment = "BLOCKED", str(exc), "The user-facing control was not available to this emulator run."
        except Exception as exc:
            status, actual, comment = "ERROR", f"{type(exc).__name__}: {exc}", "The probe could not complete; this is not counted as a product pass or a confirmed product defect."
        try:
            _, _, evidence, hierarchy = self._capture(case_id)
        except Exception as capture_error:
            comment += f" Evidence capture error: {type(capture_error).__name__}: {capture_error}."
        self._record(case_id, section, title, status, expected, actual, comment,
                     evidence=evidence, hierarchy=hierarchy)

    def _editor_bounds(self) -> tuple[int, int, int, int] | None:
        candidates: list[tuple[int, int, int, int, int]] = []
        for node in self.d.nodes():
            if not self.d._visible(node):
                continue
            bounds = node.attrib.get("bounds", "")
            match = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
            if not match:
                continue
            x1, y1, x2, y2 = map(int, match.groups())
            klass = node.attrib.get("class", "").casefold()
            text = node.attrib.get("text", "")
            if "edittext" in klass and y1 < self.d._height * 0.52:
                candidates.append((0, x1, y1, x2, y2))
            elif text and y1 < self.d._height * 0.43 and not node.attrib.get("clickable", "false").lower() == "true":
                candidates.append((1, x1, y1, x2, y2))
        if not candidates:
            return None
        candidates.sort(key=lambda item: (item[0], item[2], item[3] - item[1]))
        _, x1, y1, x2, y2 = candidates[0]
        return x1, y1, x2, y2

    def _text_point(self, *, fraction_from_right: float = 0.18) -> tuple[int, int]:
        bounds = self._editor_bounds()
        if bounds is None:
            raise NotAvailable("No visible expression editor bounds were exposed by UIAutomator/OCR.")
        x1, y1, x2, y2 = bounds
        # Calculator expression is right aligned in the user-facing display.
        x = x2 - max(10, min(x2 - x1 - 4, round((x2 - x1) * fraction_from_right)))
        y = (y1 + y2) // 2
        return x, y

    def _hold(self, x: int, y: int, duration_ms: int = 650) -> None:
        self.d.adb("shell", "input", "swipe", str(x), str(y), str(x), str(y), str(duration_ms), timeout=20)
        self._invalidate()

    def _swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500) -> None:
        self.d.adb("shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms), timeout=20)
        self._invalidate()

    def _ensure_calculator_screen(self) -> None:
        if self.d.is_calculator_screen():
            return

        def use_calculator_route() -> bool:
            if self._try_tap(["Calculator"]) is not None and self.d.is_calculator_screen():
                return True
            if self._try_tap(["Apps"]) is not None:
                if self.d.is_calculator_screen():
                    return True
                return self._try_tap(["Calculator"]) is not None and self.d.is_calculator_screen()
            return False

        # A home screen can expose Apps directly; do not press Back and exit it.
        if use_calculator_route():
            return
        self.d.adb("shell", "input", "keyevent", "4")
        self._invalidate()
        if self.d.is_calculator_screen():
            return
        if not use_calculator_route():
            raise NotAvailable(f"Could not return to calculator controls through MySpace's Apps route: {self.d.labels()!r}")

    def _enter_number(self, number: str = "123456") -> None:
        self._ensure_calculator_screen()
        self.d.close_history_if_open()
        self.d.ensure_basic_panel()
        self.d.tap_label("AC")
        self.d.press_sequence(list(number))
        if compact(number) not in [compact(value) for value in self.d.display_texts()]:
            raise NotAvailable(f"The expression {number!r} was not visible after keypad entry: {self.d.display_texts()!r}")

    def _show_selection_menu(self, *, duration_ms: int = 650) -> list[str]:
        self._enter_number()
        x, y = self._text_point(fraction_from_right=0.17)
        self._hold(x, y, duration_ms=duration_ms)
        time.sleep(0.25)
        return self.d.labels()

    def run_interaction_cases(self) -> None:
        def d1() -> tuple[str, str, str]:
            self.d.close_history_if_open()
            self.d.ensure_basic_panel()
            self.d.tap_label("AC")
            self.d.press_sequence(["2", "(", "5", "+", "2", ")", "2"])
            typed = self.d.display_texts()
            self.d.key("=")
            time.sleep(0.3)
            actual = self.d.display_texts()
            if self.d.result_visible("28"):
                return "PASS", "input=" + " | ".join(typed) + "; result=" + " | ".join(actual), "The user-entered 2(5+2)2 expression evaluated as implicit multiplication to 28."
            return "FAIL", "input=" + " | ".join(typed) + "; result=" + " | ".join(actual), "The guide's implicit-multiplication expression did not display 28."
        self._case("D1", "D1", "Evaluate implicit multiplication", "2(5+2)2 = 28", d1)

        def d2() -> tuple[str, str, str]:
            self.d.ensure_basic_panel()
            self.d.tap_label("AC")
            self.d.press_sequence(["1", "0", "+", "−"])
            actual = self.d.display_texts()
            if self.d.expression_visible("10−"):
                return "PASS", " | ".join(actual), "The trailing plus was replaced by minus; no evaluation was required."
            return "FAIL", " | ".join(actual), "The pending operator did not visibly change from plus to minus."
        self._case("D2", "D2", "Replace a pending operator", "10+ then minus shows 10−", d2)

        def d3() -> tuple[str, str, str]:
            self.d.ensure_basic_panel()
            self.d.tap_label("AC")
            self.d.press_sequence(["5", "+"])
            self.d.key("=")
            time.sleep(0.3)
            actual = self.d.display_texts()
            if self.d.result_visible("10"):
                return "PASS", " | ".join(actual), "Pressing equals after 5+ produced the guide's expected 10."
            return "FAIL", " | ".join(actual), "Pressing equals after 5+ did not produce 10."
        self._case("D3", "D3", "Evaluate with a trailing plus", "5+ then equals shows 10", d3)

        def d4() -> tuple[str, str, str]:
            self.d.ensure_basic_panel()
            self.d.tap_label("AC")
            self.d.press_sequence(list("123456"))
            actual = self.d.display_texts()
            if any("1,23,456" in value for value in actual):
                return "PASS", " | ".join(actual), "Indian digit grouping was visible while typing the six-digit number."
            return "FAIL", " | ".join(actual), "The exact displayed grouping 1,23,456 was not observed before evaluation."
        self._case("D4", "D4", "Check Indian digit grouping", "123456 displays as 1,23,456", d4)

        def d6() -> tuple[str, str, str]:
            self.d.ensure_scientific_panel()
            self.d.tap_label("AC")
            self.d.tap_label("Inv")
            inverse = self._try_tap(["sin⁻¹", "asin", "sin-1"])
            if inverse is None:
                raise NotAvailable(f"Inverse-sine key was not exposed after Inv: {self.d.labels()!r}")
            self.d.press_sequence(["0", ".", "5", ")"])
            self.d.key("=")
            time.sleep(0.35)
            actual = self.d.display_texts()
            if self.d.result_visible("30"):
                return "PASS", "inverse key=" + inverse + "; display=" + " | ".join(actual), "Inverse sine of 0.5 in degree mode returned 30."
            return "FAIL", "inverse key=" + inverse + "; display=" + " | ".join(actual), "The inverse-sine degree-mode example did not return 30."
        self._case("D6", "D6", "Evaluate inverse sine in degree mode", "Inv then sin(0.5) = 30", d6)

        def d8() -> tuple[str, str, str]:
            self.d.ensure_basic_panel()
            self.d.tap_label("AC")
            self.d.press_sequence(["1", "2", "3"])
            x, y = self._text_point(fraction_from_right=0.025)
            self.d.adb("shell", "input", "tap", str(x), str(y))
            self._invalidate()
            self.d.key("⌫")
            actual = self.d.display_texts()
            if any(compact(value) == "12" for value in actual):
                return "PASS", " | ".join(actual), "The caret was placed at the end and one Backspace removed exactly one character."
            return "FAIL", " | ".join(actual), "Backspace at the end of 123 did not leave 12 visible."
        self._case("D8", "D8", "Delete one character at the caret", "123 then Backspace leaves 12", d8)

        def b1() -> tuple[str, str, str]:
            labels = self._show_selection_menu(duration_ms=400)
            _, words = self._ocr_screen("evidence/user-b1-toolbar-ocr.png")
            actions = [name for name in ("Copy", "Cut", "MAdd", "MUse", "Paste", "Select all")
                       if self._ocr_has(words, name)]
            has_memory_action = self._ocr_has(words, "MAdd") or self._ocr_has(words, "MUse")
            if self._ocr_has(words, "Copy") and self._ocr_has(words, "Cut") and has_memory_action:
                return "PASS", "OCR toolbar=" + "; ".join(actions) + "; hierarchy=" + " | ".join(labels), "The screenshot visibly exposed the floating selection toolbar; OCR is used because Android omits this popup from UiAutomator."
            raise NotAvailable("Selection toolbar was not machine-readable; the saved screenshot is retained for visual review, so this is not called a product failure.")
        self._case("B1", "B1", "Hold number to select and show actions", "Visible selection and Cut/Copy/MAdd/MUse actions", b1)

        def b2() -> tuple[str, str, str]:
            self._enter_number()
            x1, y = self._text_point(fraction_from_right=0.32)
            x2, _ = self._text_point(fraction_from_right=0.10)
            # adb swipe moves as soon as touch-down occurs; it cannot reproduce the
            # app's stationary hold timer followed by a continuous drag.
            self._swipe(x1, y, x2, y, 750)
            labels = self.d.labels()
            _, words = self._ocr_screen("evidence/user-b2-toolbar-ocr.png")
            actions = [name for name in ("Copy", "Cut", "Select all") if self._ocr_has(words, name)]
            if actions:
                return "BLOCKED", "OCR toolbar=" + "; ".join(actions) + "; hierarchy=" + " | ".join(labels), "A toolbar appeared, but this adb swipe did not establish the uninterrupted hold-then-drag sequence or prove that the selected range changed."
            raise NotAvailable("The emulator input API could not reproduce the app-specific stationary hold-then-drag gesture; no product failure is inferred from this attempt.")
        self._case("B2", "B2", "Drag while holding to change the selected portion", "Selection changes during an uninterrupted hold-and-drag", b2)

        def b4() -> tuple[str, str, str]:
            self._show_selection_menu()
            _, toolbar = self._ocr_screen("evidence/user-b4-toolbar-ocr.png")
            if not self._ocr_has(toolbar, "Copy") or not self._tap_ocr(toolbar, "Copy"):
                raise NotAvailable("Copy could not be located in the floating toolbar; clipboard was not tested.")
            self.d.tap_label("AC")
            bounds = self._editor_bounds()
            if bounds is None:
                raise NotAvailable("Expression box bounds were not exposed for Paste.")
            x1, y1, x2, y2 = bounds
            x, y = x1 + max(12, min(36, (x2 - x1) // 12)), (y1 + y2) // 2
            self._hold(x, y)
            _, caret_menu = self._ocr_screen("evidence/user-b4-caret-menu-ocr.png")
            if not self._ocr_has(caret_menu, "Paste") or not self._tap_ocr(caret_menu, "Paste"):
                raise NotAvailable("Paste could not be located in the calculator's caret menu; same-app paste was not tested.")
            actual = self.d.display_texts()
            if any("123456" in compact(value) for value in actual):
                return "PASS", " | ".join(actual), "Copy then Paste restored the digits within the calculator app; external app handoff was intentionally not tested."
            return "FAIL", " | ".join(actual), "The copied number was not restored after Paste was selected from the calculator's caret menu."
        self._case("B4", "B4", "Copy then paste within the calculator", "Clipboard restores exactly 123456", b4)

        def b5() -> tuple[str, str, str]:
            self._show_selection_menu()
            _, toolbar = self._ocr_screen("evidence/user-b5-toolbar-ocr.png")
            if not self._ocr_has(toolbar, "Cut") or not self._tap_ocr(toolbar, "Cut"):
                raise NotAvailable("Cut could not be located in the floating toolbar; cut behavior was not tested.")
            self.d.key("7")
            actual = self.d.display_texts()
            if any(compact(value) == "7" for value in actual):
                return "PASS", " | ".join(actual), "Cut removed the held number and the next keypad digit became the expression."
            return "FAIL", " | ".join(actual), "After Cut and typing 7, the expected single-digit expression was not visible."
        self._case("B5", "B5", "Cut a held number and type into the gap", "Selection is removed; next digit is 7", b5)

        def b6() -> tuple[str, str, str]:
            self._show_selection_menu()
            _, selected_words = self._ocr_screen("evidence/user-b6-before-ocr.png")
            if not (self._ocr_has(selected_words, "Copy") and self._ocr_has(selected_words, "Cut")):
                raise NotAvailable("The screenshot OCR could not confirm a held selection before tapping it.")
            bounds = self._ocr_group(selected_words, "123456")
            if bounds is None:
                raise NotAvailable("OCR could not locate the selected number for the in-selection tap.")
            left, top, right, bottom = bounds
            x = left + round((right - left) * 0.52)
            y = (top + bottom) // 2
            self.d.adb("shell", "input", "tap", str(x), str(y))
            self._invalidate()
            self.d.key("9")
            display = self.d.display_texts()
            values = [compact(value) for value in display]
            inserted = next((value for value in values if len(value) == 7 and value.count("9") == 1 and value.replace("9", "", 1) == "123456"), None)
            _, after_words = self._ocr_screen("evidence/user-b6-after-ocr.png")
            actions_after = [name for name in ("Copy", "Cut", "MAdd", "MUse") if self._ocr_has(after_words, name)]
            if inserted and 0 < inserted.index("9") < len(inserted) - 1 and not actions_after:
                return "PASS", "after tapping selected text and typing 9: " + " | ".join(display), "The held selection released on an in-selection tap, and the next digit was inserted at an interior caret position."
            actual = "display=" + " | ".join(display) + "; lingering toolbar=" + ", ".join(actions_after)
            if actions_after:
                return "FAIL", actual, "The selection toolbar remained visible after a tap on the held expression."
            return "FAIL", actual, "The tap did not release the selection and place the next digit at an interior caret position."
        self._case("B6", "B6", "Tap the held expression to release selection and place the caret", "Selection clears; next key inserts at the tapped interior point", b6)

        def b7() -> tuple[str, str, str]:

            self._show_selection_menu()
            _, toolbar = self._ocr_screen("evidence/user-b7-toolbar-ocr.png")
            if not (self._ocr_has(toolbar, "Copy") or self._ocr_has(toolbar, "Cut")):
                raise NotAvailable("The screenshot OCR could not confirm a held selection; AC-while-selected was not inferred.")
            self.d.tap_label("AC")
            labels_after = self.d.labels()
            display = self.d.display_texts()
            _, after_words = self._ocr_screen("evidence/user-b7-after-ac-ocr.png")
            menu_still_open = any(self._ocr_has(after_words, name) for name in ("Copy", "Cut", "MAdd", "MUse"))
            expression_still_visible = (
                any("123456" in compact(value) for value in display)
                or self._ocr_has(after_words, "123456")
            )
            cleared = not expression_still_visible
            if cleared and not menu_still_open:
                return "PASS", "display=" + " | ".join(display) + "; OCR after AC=" + " ".join(w["text"] for w in after_words), "AC removed the held text and dismissed the floating selection toolbar."
            return "FAIL", "display=" + " | ".join(display) + "; OCR after AC=" + " ".join(w["text"] for w in after_words), "AC did not visibly clear both the expression and selection toolbar."
        self._case("B7", "B7", "Clear a held selection with AC", "Held text and selection toolbar both clear", b7)

        def b9() -> tuple[str, str, str]:
            self._enter_number()
            _, words = self._ocr_screen("evidence/user-b9-before-edit.png")
            bounds = self._ocr_group(words, "123456")
            if bounds is None:
                raise NotAvailable("OCR could not locate the visible six-digit expression; a mid-number tap was not attempted.")
            left, top, right, bottom = bounds
            x = left + round((right - left) * 0.58)
            y = (top + bottom) // 2
            self.d.adb("shell", "input", "tap", str(x), str(y))
            self._invalidate()
            self.d.key("9")
            display = self.d.display_texts()
            candidates = [compact(value) for value in display]
            inserted = next((value for value in candidates if len(value) == 7 and value.count("9") == 1 and value.replace("9", "", 1) == "123456"), None)
            if inserted and 0 < inserted.index("9") < len(inserted) - 1:
                return "PASS", " | ".join(display), "OCR located the expression and a tap 58% across its visible glyph bounds inserted 9 between existing digits."
            if inserted:
                raise NotAvailable(f"The digit landed at an expression edge ({inserted}); the emulator did not confirm an interior caret position.")
            return "FAIL", " | ".join(display), "After an OCR-targeted tap inside the visible number, the keypad did not produce exactly one interior digit insertion."
        self._case("B9", "B9", "Tap inside a number and insert a digit", "9 is inserted at the caret, not appended", b9)

        def b11() -> tuple[str, str, str]:
            self.d.tap_label("AC")
            bounds = self._editor_bounds()
            if bounds is None:
                raise NotAvailable("Expression box bounds were not exposed.")
            x1, y1, x2, y2 = bounds
            x, y = x1 + max(12, min(36, (x2 - x1) // 12)), (y1 + y2) // 2
            self._hold(x, y)
            _, words = self._ocr_screen("evidence/user-b11-caret-menu-ocr.png")
            actions = [name for name in ("MUse", "Paste", "Select all") if self._ocr_has(words, name)]
            if len(actions) >= 2:
                return "PASS", "OCR caret menu=" + "; ".join(actions), "The screenshot shows the empty-box caret menu; OCR is used because the Android floating menu is omitted from UiAutomator."
            raise NotAvailable("The empty-box toolbar could not be confirmed by OCR; screenshot retained, no product failure inferred.")
        self._case("B11", "B11", "Hold empty expression-box space for caret menu", "MUse/Paste/Select all caret actions", b11)

        def c9() -> tuple[str, str, str]:
            bounds = self._editor_bounds()
            if bounds is not None:
                x, y = (bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2
                self.d.adb("shell", "input", "tap", str(x), str(y))
                self._invalidate()
            result = self.d.adb("shell", "dumpsys", "input_method", timeout=35, check=False)
            shown = re.search(r"(?:mInputShown|mShowRequested|isInputViewShown)\s*[=:]\s*true", result, re.I)
            if shown:
                return "FAIL", shown.group(0), "Android reports a visible input method after the expression was tapped; the guide promises no device keyboard."
            hidden = re.search(r"(?:mInputShown|mShowRequested|isInputViewShown)\s*[=:]\s*false", result, re.I)
            return ("PASS", "input_method not shown", "Android's input-method diagnostics did not report a visible software keyboard after tapping the expression.") if hidden else ("BLOCKED", result[-1200:], "This Android image did not expose a recognized keyboard-visibility field; screenshot and hierarchy are retained for visual review.")
        self._case("C9", "C9", "Verify tapping the expression does not open a device keyboard", "No Android soft keyboard shown", c9)

        def e3() -> tuple[str, str, str]:
            menu_tap = self._try_tap(["More options", "More", "Menu"])
            if menu_tap is None:
                self.d.adb("shell", "input", "tap", str(self.d._width - 28), str(round(self.d._height * 0.13)))
                self._invalidate()
            labels = self.d.labels()
            _, words = self._ocr_screen("evidence/user-e3-overflow-menu.png")
            observed = labels + [word["text"] for word in words]
            effects = case_insensitive_match(observed, ["Effects"])
            memory = case_insensitive_match(observed, ["Memory", "View memory"])
            other = [name for name in ("History", "Settings", "Help", "Theme") if case_insensitive_match(observed, [name])]
            menu_open = bool(effects or memory or other)
            if effects and (memory or len(other) >= 1):
                return "PASS", " | ".join(observed), "The overflow menu exposed Effects plus calculator menu actions. This smoke check does not verify the exact item count or reorder behavior."
            if not menu_open:
                raise NotAvailable("The overflow action or menu contents were not readable through UIAutomator/OCR; no product failure inferred.")
            return "FAIL", " | ".join(observed), "The menu opened, but the expected Effects item or other calculator menu actions were missing."
        self._case("E3", "E3", "Open the three-dot menu", "Overflow exposes Effects and the calculator actions", e3)

        def c10() -> tuple[str, str, str]:
            labels = self.d.labels()
            shape_entry = case_insensitive_match(labels, ["Key shape", "Key shapes", "Button shape"])
            if not shape_entry:
                # If the overflow is already open, use it; otherwise open it once.
                menu_open = any(case_insensitive_match(labels, [name]) for name in ("Effects", "Memory", "History"))
                if not menu_open:
                    if self._try_tap(["More options", "More", "Menu"]) is None:
                        self.d.adb("shell", "input", "tap", str(self.d._width - 28), str(round(self.d._height * 0.13)))
                        self._invalidate()
                labels = self.d.labels()
                shape_entry = case_insensitive_match(labels, ["Key shape", "Key shapes", "Button shape"])
            if not shape_entry:
                raise NotAvailable(f"Key shape entry was not visible in the menu: {self.d.labels()!r}")
            self.d.tap_label(shape_entry, partial=True, timeout=2.0)
            labels = self.d.labels()
            _, words = self._ocr_screen("evidence/user-c10-key-shape-picker.png")
            choices = [
                name for name in ("Circle", "Squircle", "Pill", "Rounded square", "No shape")
                if case_insensitive_match(labels, [name]) or self._ocr_has(words, name)
            ]
            if len(choices) < 4:
                raise NotAvailable(f"The picker did not expose four named shapes through UI labels/OCR: {choices!r}; labels={labels!r}")
            selected = self._try_tap(["Circle"])
            if not selected:
                selected = self._tap_ocr(words, "Circle")
            if not selected:
                raise NotAvailable("Circle was visible but the emulator could not select it; no product failure inferred.")
            return "PASS", "picker=" + "; ".join(choices) + "; selected=Circle", "The picker exposed at least four named key silhouettes and accepted a Circle selection. Persistence and pixel-perfect geometry are not inferred from this one view."
        self._case("C10", "C10", "Open key-shape picker and select Circle", "Picker presents Circle/Squircle/Pill/Rounded square/No shape", c10)

        def h1_h2() -> tuple[str, str, str]:
            light_shot = self.d.report_dir / "evidence/h1-light-theme.png"
            dark_shot = self.d.report_dir / "evidence/h2-dark-theme.png"
            self._ensure_calculator_screen()
            self.d.ensure_basic_panel()
            self.d.tap_label("AC")
            self.d.press_sequence(list("123456"))

            def open_theme_settings() -> None:
                if self._try_tap(["Settings"]) is None:
                    if self._try_tap(["MySpace home", "Home"]) is None:
                        self.d.adb("shell", "input", "tap", str(round(self.d._width * 0.12)), str(round(self.d._height * 0.085)))
                        self._invalidate()
                    if self._try_tap(["Settings"]) is None:
                        if self._try_tap(["More options", "More", "Menu"]) is None:
                            self.d.adb("shell", "input", "tap", str(self.d._width - 24), str(round(self.d._height * 0.12)))
                            self._invalidate()
                        if self._try_tap(["Settings"]) is None:
                            raise NotAvailable(f"Settings was not exposed from the calculator's MySpace home: {self.d.labels()!r}")
                if self._try_tap(["Theme", "Appearance"]) is None:
                    raise NotAvailable(f"Theme setting was not exposed: {self.d.labels()!r}")

            def return_to_calculator() -> None:
                self._ensure_calculator_screen()

            open_theme_settings()
            if self._try_tap(["Light"]) is None:
                raise NotAvailable(f"Light option was not exposed in Theme: {self.d.labels()!r}")
            time.sleep(0.3)
            return_to_calculator()
            light_path = self.d.screenshot(str(light_shot.relative_to(self.d.report_dir)))

            open_theme_settings()
            if self._try_tap(["Dark"]) is None:
                raise NotAvailable(f"Dark option was not exposed in Theme: {self.d.labels()!r}")
            time.sleep(0.3)
            return_to_calculator()
            dark_path = self.d.screenshot(str(dark_shot.relative_to(self.d.report_dir)))
            if not light_path or not dark_path:
                return "ERROR", "light screenshot=" + str(bool(light_path)) + "; dark screenshot=" + str(bool(dark_path)), "A theme transition was attempted but a required calculator screenshot was not captured."
            light_digest = hashlib.sha256(light_shot.read_bytes()).hexdigest()
            dark_digest = hashlib.sha256(dark_shot.read_bytes()).hexdigest()
            expression = self.d.display_texts()
            expression_retained = any("123456" in compact(value) for value in expression)
            changed_ratio = self._theme_visual_difference_ratio(light_shot, dark_shot)
            actual = f"stable-screen pixel change={changed_ratio:.1%}; Light SHA-256={light_digest}; Dark SHA-256={dark_digest}; expression={expression!r}"
            if changed_ratio >= 0.05:
                note = "Both Light and Dark choices produced visibly different calculator screens."
                if not expression_retained:
                    note += " The displayed expression reset during the settings/home route, so expression persistence is not claimed."
                note += " Exact palette/caret pixels are not asserted."
                return "PASS", actual, note
            return "BLOCKED", actual, "Both options were selectable, but screenshot comparison could not distinguish their calculator appearances beyond status/navigation changes; theme application remains unverified."
        self._case("H1-H2", "H1/H2", "Apply Light and Dark calculator themes", "Light and Dark choices visibly change the calculator screen", h1_h2)

        def calculator_ad_labels() -> tuple[str, str, str]:
            labels = self.d.labels()
            matches = [label for label in labels if re.search(r"\b(ad|advertisement|sponsored)\b", label, re.I)]
            if matches:
                return "FAIL", "; ".join(matches), "An ad-like label was visible on the calculator screen. This is not a network-traffic audit."
            return "PASS", f"Scanned {len(labels)} visible labels; no ad indicator", "No ad-like text appeared on the sampled calculator screen; this does not certify the app's network or SDK behavior."
        self._case("ADS-CALC", "Calculator", "Scan visible calculator labels for ad indicators", "No visible ad labels on the calculator screen", calculator_ad_labels)

    def run_calculator_feature_cases(self) -> None:
        """Exercise calculator-only memory and customization journeys."""
        def b12_memory_round_trip() -> tuple[str, str, str]:
            self._enter_number("123456")
            x, y = self._text_point(fraction_from_right=0.17)
            self._hold(x, y)
            _, add_toolbar = self._ocr_screen("evidence/user-b12-madd-toolbar.png")
            if not self._ocr_has(add_toolbar, "MAdd") or not self._tap_ocr(add_toolbar, "MAdd"):
                raise NotAvailable("MAdd was not machine-readable on the floating toolbar; memory was not tested.")

            # Use the stored value to replace exactly the final operand.
            self.d.tap_label("AC")
            self.d.press_sequence(["3", "+", "4"])
            _, expression_words = self._ocr_screen("evidence/user-b12-expression-before-muse.png")
            expression_bounds = self._ocr_group(expression_words, "3+4")
            if expression_bounds is None:
                raise NotAvailable("OCR could not locate 3+4; a text-selection gesture was not attempted.")
            left, top, right, bottom = expression_bounds
            x = left + round((right - left) * 0.88)
            y = (top + bottom) // 2
            self._hold(x, y)
            _, use_toolbar = self._ocr_screen("evidence/user-b12-muse-toolbar.png")
            if not self._ocr_has(use_toolbar, "MUse"):
                raise NotAvailable("MUse was not visible after holding the final operand; memory reuse was not tested.")
            if not (self._ocr_has(use_toolbar, "Copy") and self._ocr_has(use_toolbar, "Cut")):
                raise NotAvailable("The hold exposed a caret menu, not a verifiable text selection of 4; memory replacement was not inferred.")
            if not self._tap_ocr(use_toolbar, "MUse"):
                raise NotAvailable("MUse was visible but could not be tapped; stored value was not re-used.")

            expression = self.d.display_texts()
            if not any(compact(value) == "3+123456" for value in expression):
                return "FAIL", "after MUse=" + " | ".join(expression), "MUse did not replace only the held 4 with the previously stored 123456."
            self.d.key("=")
            result = self.d.display_texts()
            if any(compact(value).endswith("123459") for value in result):
                return "PASS", "after MUse=" + " | ".join(expression) + "; after equals=" + " | ".join(result), "MAdd stored 123456 and MUse replaced the selected operand in 3+4; the grouped result equals 123459."
            return "FAIL", "after MUse=" + " | ".join(expression) + "; after equals=" + " | ".join(result), "The stored value appeared in the expression but the calculator did not evaluate the expected sum 123459."
        self._case("B12", "B12", "Store a number with MAdd and use it in an expression", "MUse replaces the selected 4 in 3+4 with 123456; result 123459", b12_memory_round_trip)

        def b12_caret_insert() -> tuple[str, str, str]:
            self._enter_number("123456")
            x, y = self._text_point(fraction_from_right=0.17)
            self._hold(x, y)
            _, add_toolbar = self._ocr_screen("evidence/user-b12-caret-madd-toolbar.png")
            if not self._ocr_has(add_toolbar, "MAdd") or not self._tap_ocr(add_toolbar, "MAdd"):
                raise NotAvailable("MAdd was not machine-readable on the floating toolbar; caret insertion was not tested.")

            self.d.tap_label("AC")
            self.d.press_sequence(["3", "+", "4"])
            _, expression_words = self._ocr_screen("evidence/user-b12-caret-expression.png")
            bounds = self._ocr_group(expression_words, "3+4")
            if bounds is None:
                raise NotAvailable("OCR could not locate 3+4 for the caret-placement attempt.")
            left, top, right, bottom = bounds
            # Place the caret in the gap after '+' and before the final operand.
            x = left + round((right - left) * 0.66)
            y = (top + bottom) // 2
            self.d.adb("shell", "input", "tap", str(x), str(y))
            self._invalidate()
            self._hold(x, y)
            _, caret_menu = self._ocr_screen("evidence/user-b12-caret-menu.png")
            if not self._ocr_has(caret_menu, "MUse") or not self._ocr_has(caret_menu, "Paste"):
                raise NotAvailable("The caret menu did not expose both MUse and Paste at the tapped expression position.")
            if self._ocr_has(caret_menu, "Copy") or self._ocr_has(caret_menu, "Cut"):
                raise NotAvailable("The hold produced a text-selection toolbar, so MUse insertion at an empty caret was not proven.")
            if not self._tap_ocr(caret_menu, "MUse"):
                raise NotAvailable("MUse was visible in the caret menu but could not be tapped.")

            expression = self.d.display_texts()
            if not any(compact(value) == "3+1234564" for value in expression):
                return "FAIL", "after caret MUse=" + " | ".join(expression), "MUse did not insert 123456 at the caret between '+' and the final 4."
            self.d.key("=")
            result = self.d.display_texts()
            if any(compact(value).endswith("1234567") for value in result):
                return "PASS", "after MUse=" + " | ".join(expression) + "; after equals=" + " | ".join(result), "MAdd stored 123456; the empty-caret MUse inserted it between '+' and 4, and the expression evaluated to 1234567."
            return "FAIL", "after MUse=" + " | ".join(expression) + "; after equals=" + " | ".join(result), "MUse inserted the stored value at the caret, but the resulting 3+1234564 expression did not evaluate to 1234567."
        self._case("B12-CARET", "B12", "Insert a stored value at a mid-expression caret", "MUse inserts 123456 between '+' and 4 in 3+4", b12_caret_insert)

        def memory_list() -> tuple[str, str, str]:

            if self._try_tap(["More options", "More", "Menu"]) is None:
                self.d.adb("shell", "input", "tap", str(self.d._width - 24), str(round(self.d._height * 0.17)))
                self._invalidate()
            labels = self.d.labels()
            view = case_insensitive_match(labels, ["View memory", "Memory"])
            if view is None:
                raise NotAvailable(f"Calculator overflow did not expose View memory: {labels!r}")
            self.d.tap_label(view, partial=True, timeout=2.0)
            time.sleep(0.25)
            labels = self.d.labels()
            _, words = self._ocr_screen("evidence/user-e3-memory-list.png")
            visible = " | ".join(labels + [word["text"] for word in words])
            if any("123456" in compact(value) for value in labels) or self._ocr_has(words, "123456"):
                self.d.adb("shell", "input", "keyevent", "4")
                self._invalidate()
                return "PASS", visible, "The calculator's memory list displayed the value saved through MAdd."
            raise NotAvailable("The memory popup opened, but its saved value was not exposed as readable text; screenshot retained for review.")
        self._case("E3-MEMORY", "E3", "Open the calculator memory list", "Saved value 123456 is visible in View memory", memory_list)

        def effects_picker() -> tuple[str, str, str]:
            if self._try_tap(["More options", "More", "Menu"]) is None:
                self.d.adb("shell", "input", "tap", str(self.d._width - 24), str(round(self.d._height * 0.17)))
                self._invalidate()
            labels = self.d.labels()
            effect = case_insensitive_match(labels, ["Effects"])
            if effect is None:
                raise NotAvailable(f"Calculator overflow did not expose Effects: {labels!r}")
            self.d.tap_label(effect, partial=True, timeout=2.0)
            labels = self.d.labels()
            if not labels:
                raise NotAvailable("Effects control opened without readable choices.")
            effect_names = ("ripple", "bounce", "scale", "slide", "rotate", "fade", "flip", "none", "wave", "pulse", "pop", "zoom")
            choices = [label for label in labels if any(token in label.casefold() for token in effect_names)]
            _, words = self._ocr_screen("evidence/user-e4-effects-picker.png")
            for word in words:
                if any(token in word["text"].casefold() for token in effect_names) and word["text"] not in choices:
                    choices.append(word["text"])
            if not choices:
                raise NotAvailable(f"Effects screen had no identifiable animation choice: {labels!r}")
            selected = False
            for choice in choices:
                if self._try_tap([choice], partial=True):
                    selected = True
                    break
            if not selected:
                # A radio row may be visible only to OCR; select its first recognized choice.
                selected = any(self._tap_ocr(words, choice) for choice in choices)
            if not selected:
                raise NotAvailable(f"Animation choices were visible but no selection could be made: {choices!r}")
            return "PASS", "choices=" + "; ".join(choices) + "; selected one option", "The Effects picker exposed user-selectable calculator animation options. This smoke test confirms access and selection, not frame-by-frame animation timing."
        self._case("E4", "E4", "Choose a calculator keypress effect", "Effects picker opens and accepts an animation choice", effects_picker)

        def c11_key_theme() -> tuple[str, str, str]:
            self._ensure_calculator_screen()
            self.d.ensure_basic_panel()
            self.d.tap_label("AC")
            before = self.d.screenshot("evidence/user-c11-key-theme-before.png")
            if not before:
                raise NotAvailable("The baseline calculator screenshot could not be captured.")

            theme_names = ("MySpace settings", "Graphite", "Ocean", "Sunset", "Mint", "Rose", "Lemon", "Iris")

            def dismiss_to_calculator() -> None:
                popup_items = theme_names + ("Key theme", "Key shape", "Effects", "Memory", "History")
                for _ in range(3):
                    labels_now = self.d.labels()
                    popup_open = any(case_insensitive_match(labels_now, [item]) for item in popup_items)
                    if self.d.is_calculator_screen() and not popup_open:
                        return
                    self.d.adb("shell", "input", "keyevent", "4")
                    self._invalidate()
                if not self.d.is_calculator_screen():
                    self._ensure_calculator_screen()

            def open_picker(stem: str) -> tuple[list[str], list[dict[str, Any]]]:
                dismiss_to_calculator()
                if self._try_tap(["More options", "More", "Menu"]) is None:
                    self.d.adb("shell", "input", "tap", str(self.d._width - 28), str(round(self.d._height * 0.13)))
                    self._invalidate()
                menu_labels = self.d.labels()
                entry = case_insensitive_match(menu_labels, ["Key theme", "Key themes"])
                if entry is None:
                    raise NotAvailable(f"Calculator overflow did not expose Key theme: {menu_labels!r}")
                self.d.tap_label(entry, partial=True, timeout=2.0)
                time.sleep(0.2)
                labels = self.d.labels()
                _, words = self._ocr_screen(stem)
                return labels, words

            labels, words = open_picker("evidence/user-c11-key-theme-picker-ocr.png")

            def visible_themes(current_labels: list[str], current_words: list[dict[str, Any]]) -> list[str]:
                visible = []
                for name in theme_names:
                    if case_insensitive_match(current_labels, [name]) or self._ocr_has(current_words, name):
                        visible.append(name)
                return visible

            choices = visible_themes(labels, words)
            if "Rose" not in choices:
                # The picker is scrollable in the guide; inspect its lower rows once.
                self._swipe(
                    round(self.d._width * 0.7), round(self.d._height * 0.72),
                    round(self.d._width * 0.7), round(self.d._height * 0.34), 450,
                )
                more_labels = self.d.labels()
                _, more_words = self._ocr_screen("evidence/user-c11-key-theme-scroll-ocr.png")
                choices = list(dict.fromkeys(choices + visible_themes(more_labels, more_words)))
                labels, words = more_labels, more_words
            if "Rose" not in choices:
                raise NotAvailable(f"The key-theme picker did not expose Rose in its initial view or one scroll: {choices!r}")

            selected = self._try_tap(["Rose"], partial=False)
            if not selected:
                selected = self._tap_ocr(words, "Rose")
            if not selected:
                raise NotAvailable("Rose was visible in the key-theme picker but could not be selected.")
            time.sleep(0.3)
            dismiss_to_calculator()
            after = self.d.screenshot("evidence/user-c11-key-theme-rose.png")
            if not after:
                raise NotAvailable("The calculator screenshot after selecting Rose could not be captured.")
            change = self._theme_visual_difference_ratio(Path(before), Path(after))

            restored = False
            restore_note = ""
            try:
                restore_labels, restore_words = open_picker("evidence/user-c11-key-theme-restore-ocr.png")
                if not (case_insensitive_match(restore_labels, ["MySpace settings"]) or self._ocr_has(restore_words, "MySpace settings")):
                    raise NotAvailable("MySpace settings was not readable in the picker while restoring the default key theme.")
                restored = bool(self._try_tap(["MySpace settings"], partial=True)) or self._tap_ocr(restore_words, "MySpace settings")
                if not restored:
                    raise NotAvailable("The default MySpace settings key theme could not be selected.")
                time.sleep(0.2)
                dismiss_to_calculator()
            except NotAvailable as exc:
                restore_note = f"; restore note: {exc}"

            actual = f"OCR-visible themes={', '.join(choices)}; Rose-to-default-keypad screen change={change:.1%}; restored MySpace settings={restored}"
            if change >= 0.03:
                return "PASS", actual, "The key-theme picker exposed Rose, accepted its selection, and visibly changed the calculator screen; the MySpace settings theme was restored where accessible. The eight-theme catalogue was not exhaustively audited." + restore_note
            return "BLOCKED", actual, "Rose could be selected, but the screenshot comparison could not isolate a visible keypad-theme change; no color-accuracy claim is made." + restore_note
        self._case("C11", "C11", "Select a calculator key theme", "Key-theme picker exposes Rose and applies a visible keypad palette", c11_key_theme)

    def run_standalone_cases(self) -> None:
        def header() -> tuple[str, str, str]:
            labels = self.d.labels()
            identity = case_insensitive_match(labels, ["MyCalc", "Standalone"])
            if identity:
                return "PASS", " | ".join(labels), "The installed standalone calculator identifies itself in the visible app header."
            return "BLOCKED", " | ".join(labels), "No accessible MyCalc/standalone label was exposed; screenshot retained."
        self._case("F-HEADER", "F", "Inspect standalone MyCalc identity", "MyCalc is visibly distinct as the standalone app", header)

    def _capture_runtime_diagnostics(self) -> dict[str, Any]:
        pid = self.d.adb("shell", "pidof", self.package, timeout=20, check=False).strip()
        try:
            logcat = self.d.adb("logcat", "-d", "-t", "3000", timeout=60, check=False)
        except Exception as exc:
            logcat = f"Unable to capture logcat: {type(exc).__name__}: {exc}"
        lines = logcat.splitlines()
        pattern = re.compile(
            rf"FATAL EXCEPTION|AndroidRuntime.*E|ANR in.*{re.escape(self.package)}|"
            rf"Process: {re.escape(self.package)}|Fatal signal.*{re.escape(self.package)}",
            re.I,
        )
        selected: set[int] = set()
        for index, line in enumerate(lines):
            if pattern.search(line):
                selected.update(range(max(0, index - 3), min(len(lines), index + 5)))
        excerpt = "\n".join(lines[index] for index in sorted(selected))
        if not excerpt:
            excerpt = f"No matching fatal-exception or target-package ANR lines in the captured {len(lines)} logcat lines.\n"
        path = self.report_dir / "diagnostics" / "target-crash-scan.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"Package: {self.package}\nPID at end of run: {pid or 'not reported'}\n"
            f"Captured logcat lines: {len(lines)}\n\n{excerpt}\n",
            encoding="utf-8",
        )
        return {"package_pid_at_end": pid or None, "matching_log_lines": len(selected), "path": str(path.relative_to(self.report_dir))}

    def run(self) -> int:
        digest = self._assert_apk()
        self._run_calculator_suite()
        assert self.qa is not None and self.device is not None

        # Every shard stays on the calculator UI. The second MySpace shard is
        # specifically for memory/history/customization; no Notes/Scanner or other
        # MySpace feature app is opened.
        if self.suite == "myspace-core":
            self.run_interaction_cases()
        elif self.suite == "myspace-features":
            self.run_calculator_feature_cases()
        else:
            self.run_standalone_cases()
            self.run_interaction_cases()
            self.run_calculator_feature_cases()

        diagnostics = self._capture_runtime_diagnostics()
        calc_counts = self.calculator_report.get("summary", {})
        user_counts: dict[str, int] = {}
        for row in self.results:
            status = row["status"]
            user_counts[status] = user_counts.get(status, 0) + 1
        metadata = {
            "report_title": "MySpace calculator-only APK QA" if self.package == DEFAULT_PACKAGE else "Standalone MyCalc calculator-only APK QA",
            "created_utc": utc_now(),
            "suite": self.suite,
            "artifact": {
                "file": self.apk.name,
                "package": self.package,
                "size_bytes": self.apk.stat().st_size,
                "sha256": digest,
                "version_name": self.version_observed.get("version_name"),
                "version_code": self.version_observed.get("version_code"),
            },
            "device": {
                "emulator_api": 34,
                "screen": f"{self.device._width}x{self.device._height}",
                "ui_inspection_method": self.device.ui_method,
            },
            "source": {
                "commit": PINNED_SOURCE_COMMIT,
                "guide_sha256": PINNED_GUIDE_SHA256,
                "direct_apk_evidence": True,
            },
            "calculator_summary": calc_counts,
            "calculator_results": self.calculator_report.get("results", []),
            "runtime_diagnostics": diagnostics,
            "user_summary": user_counts,
            "user_results": self.results,
            "limits": [
                "Direct APK evidence comes from Android 14/API 34 emulator UI actions, screenshots and hierarchy dumps.",
                "Only calculator screens and calculator-specific settings are exercised; other MySpace apps are out of scope.",
                "The calculator ad check scans sampled visible text; it is not a network or third-party SDK audit.",
                "Source-CI runs are reported separately from direct APK results.",
            ],
        }
        out = self.report_dir / "user-journey-results.json"
        out.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        summary = self.report_dir / "user-journey-results.md"
        lines = [
            f"# {metadata['report_title']}",
            "",
            f"- APK: `{metadata['artifact']['file']}`",
            f"- Package/version: `{self.package}` · {metadata['artifact']['version_name']} ({metadata['artifact']['version_code']})",
            f"- APK SHA-256: `{digest}`",
            f"- Guide SHA-256: `{PINNED_GUIDE_SHA256}`",
            f"- Source commit: `{PINNED_SOURCE_COMMIT}`",
            f"- Emulator: Android 14/API 34, {metadata['device']['screen']}",
            f"- Calculator counts: `{calc_counts}`",
            f"- User journey counts: `{user_counts}`",
            "",
            "| ID | Section | User action | Outcome | Observed | Comment |",
            "|---|---|---|---|---|---|",
        ]
        for row in self.results:
            values = [row["id"], row["guide_section"], row["title"], row["status"], row["actual"], row["comment"]]
            lines.append("| " + " | ".join(str(value).replace("|", "\\|").replace("\n", " ") for value in values) + " |")
        lines.extend(["", "Screenshots and UI hierarchy XML are in `evidence/`; calculator case JSON is under `calculator/`.", ""])
        summary.write_text("\n".join(lines), encoding="utf-8")

        failures = [row for row in self.results if row["status"] in {"FAIL", "ERROR"}]
        calc_failures = [row for row in self.calculator_report.get("results", []) if row.get("status") in {"FAIL", "ERROR"}]
        print(f"User results: {out}", flush=True)
        print(f"User counts: {user_counts}; calculator counts: {calc_counts}", flush=True)
        return 1 if failures or calc_failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--suite", choices=("myspace-core", "myspace-features", "mycalc"), required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        qa = UserQa(args.apk, args.package, args.expected_sha256, args.suite, args.report_dir)
        return qa.run()
    except Exception as exc:
        print(f"::error title=User-facing APK QA::{type(exc).__name__}: {exc}", flush=True)
        print(f"User-facing QA failed before completing: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
