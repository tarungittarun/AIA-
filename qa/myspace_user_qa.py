#!/usr/bin/env python3
"""Black-box, user-facing QA for the pinned MySpace and standalone MyCalc APKs.

The existing calculator harness remains the source of calculator assertions;
this runner adds touch-driven selection, app navigation, key-shape/theme checks,
visible-screen captures, and a conservative ad-indicator sweep. All results are
from the installed distribution APK, not a source build.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
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
    DEFAULT_PACKAGE: "f3257177dc098cf62f54a6f77df526195323d36b23ed5a69f9ff07ddf96b45fb",
    STANDALONE_PACKAGE: "99c65435e455e241dd3eb65ea6494abcabf2099f5024f6a82c6cf8a621a6bf6b",
}
PINNED_GUIDE_SHA256 = "d494cf934f12f0c5b1e77da2254d026438d1c10d233c9b53e4620beb7014db92"
PINNED_SOURCE_COMMIT = "0727a2e3b9974d6df70153d76dc8e629e0a0b839"
EXPECTED_VERSION = {
    DEFAULT_PACKAGE: ("3.12.35", 72),
    STANDALONE_PACKAGE: ("1.0.33", 34),
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
        if suite not in {"myspace-core", "myspace-modules", "mycalc"}:
            raise ValueError(f"Unsupported suite: {suite}")
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
        elif self.suite == "myspace-modules":
            # A small working-calculator baseline before exercising the feature hub.
            case_ids = {"TC-CALC-001"}
        else:
            case_ids = CALCULATOR_CASES[STANDALONE_PACKAGE]

        calc_dir = self.report_dir / "calculator"
        self.qa = CalculatorQa(self.apk, self.package, calc_dir, case_ids=case_ids)
        # calculator_e2e.py keeps the prior release hashes as its defaults for
        # regression history. Apply the separately verified, immutable v3.12.35
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
        if version_name and version_name.group(1) != expected_name:
            raise QaError(f"Installed versionName mismatch: expected {expected_name}, got {version_name.group(1)}")
        if version_code and int(version_code.group(1)) != expected_code:
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

    def _enter_number(self, number: str = "123456") -> None:
        self.d.close_history_if_open()
        self.d.ensure_basic_panel()
        self.d.tap_label("AC")
        self.d.press_sequence(list(number))
        if compact(number) not in [compact(value) for value in self.d.display_texts()]:
            raise NotAvailable(f"The expression {number!r} was not visible after keypad entry: {self.d.display_texts()!r}")

    def _show_selection_menu(self) -> list[str]:
        self._enter_number()
        x, y = self._text_point(fraction_from_right=0.17)
        self._hold(x, y)
        labels = self.d.labels()
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
            labels = self._show_selection_menu()
            actions = [name for name in ("Copy", "Cut", "Select all", "MAdd", "MUse", "Paste")
                       if case_insensitive_match(labels, [name])]
            if len(actions) >= 2:
                return "PASS", "; ".join(actions), "A stationary long-press on the entered number exposed a selection/action menu; screenshot retained for visual review."
            return "FAIL", "; ".join(labels), "The expected selection action menu did not appear after a 650 ms hold on the typed number."
        self._case("B1", "B1", "Hold number to select and show actions", "Visible selection and Cut/Copy actions", b1)

        def b2() -> tuple[str, str, str]:
            self._enter_number()
            x1, y = self._text_point(fraction_from_right=0.32)
            x2, _ = self._text_point(fraction_from_right=0.10)
            self._swipe(x1, y, x2, y, 750)
            labels = self.d.labels()
            actions = [name for name in ("Copy", "Cut", "Select all") if case_insensitive_match(labels, [name])]
            if actions:
                return "PASS", "; ".join(actions), "A hold-then-drag on the expression left the selection action UI visible. Exact selected-character boundaries are retained in the screenshot, not inferred from source code."
            return "FAIL", "; ".join(labels), "No selection action UI was visible after the hold-then-drag gesture."
        self._case("B2", "B2", "Drag while holding to change the selected portion", "Selection changes during an uninterrupted hold-and-drag", b2)

        def b4() -> tuple[str, str, str]:
            labels = self._show_selection_menu()
            if not case_insensitive_match(labels, ["Copy"]):
                raise NotAvailable("Copy was not offered by the selection menu; clipboard round-trip was not attempted.")
            self.d.tap_label("Copy", timeout=2.0)
            self.d.tap_label("AC")
            bounds = self._editor_bounds()
            if bounds is None:
                raise NotAvailable("Expression box bounds were not exposed for Paste.")
            x1, y1, x2, y2 = bounds
            # Hold well left of the right-aligned expression to invoke the empty-box caret menu.
            x, y = x1 + max(12, min(36, (x2 - x1) // 12)), (y1 + y2) // 2
            self._hold(x, y)
            labels = self.d.labels()
            if not case_insensitive_match(labels, ["Paste"]):
                raise NotAvailable(f"Paste was not offered from the empty expression box: {labels!r}")
            self.d.tap_label("Paste", timeout=2.0)
            actual = self.d.display_texts()
            if any("123456" in compact(value) for value in actual):
                return "PASS", " | ".join(actual), "Copied text was pasted back through the app's user-visible caret menu. This confirms same-app clipboard round-trip, not an external Notes/Messages paste."
            return "FAIL", " | ".join(actual), "The copied number was not restored after selecting Paste from the expression-box menu."
        self._case("B4", "B4", "Copy then paste the selected digits", "Clipboard restores exactly 123456", b4)

        def b5() -> tuple[str, str, str]:
            labels = self._show_selection_menu()
            if not case_insensitive_match(labels, ["Cut"]):
                raise NotAvailable("Cut was not offered by the selection menu.")
            self.d.tap_label("Cut", timeout=2.0)
            self.d.key("7")
            actual = self.d.display_texts()
            if any(compact(value) == "7" for value in actual):
                return "PASS", " | ".join(actual), "Cut removed the held number and the next keypad digit became the expression."
            return "FAIL", " | ".join(actual), "After Cut and typing 7, the expected single-digit expression was not visible."
        self._case("B5", "B5", "Cut a held number and type into the gap", "Selection is removed; next digit is 7", b5)

        def b7() -> tuple[str, str, str]:
            labels = self._show_selection_menu()
            if not any(case_insensitive_match(labels, [name]) for name in ("Copy", "Cut", "Select all")):
                raise NotAvailable("No selection menu was exposed; AC-while-selected could not be attempted.")
            self.d.tap_label("AC")
            labels_after = self.d.labels()
            display = self.d.display_texts()
            menu_still_open = any(case_insensitive_match(labels_after, [name]) for name in ("Copy", "Cut", "Select all"))
            cleared = not any(compact(value) == "123456" for value in display)
            if cleared and not menu_still_open:
                return "PASS", "display=" + " | ".join(display) + "; menu cleared", "AC removed the held text and selection menu."
            return "FAIL", "display=" + " | ".join(display) + "; labels=" + " | ".join(labels_after), "AC did not visibly clear both the expression and selection menu."
        self._case("B7", "B7", "Clear a held selection with AC", "Held text and selection menu both clear", b7)

        def b9() -> tuple[str, str, str]:
            self._enter_number()
            x, y = self._text_point(fraction_from_right=0.48)
            self.d.adb("shell", "input", "tap", str(x), str(y))
            self._invalidate()
            self.d.key("9")
            display = self.d.display_texts()
            candidates = [compact(value) for value in display]
            inserted = next((value for value in candidates if "9" in value and value.replace("9", "", 1) == "123456"), None)
            if inserted and inserted.index("9") < len(inserted) - 1:
                return "PASS", " | ".join(display), "A tap within the visible number inserted 9 before the final character instead of appending at the end."
            return "FAIL", " | ".join(display), "The caret tap/key sequence did not produce an insertion inside 123456; see the saved screen and hierarchy."
        self._case("B9", "B9", "Tap inside a number and insert a digit", "9 is inserted at the caret, not appended", b9)

        def b11() -> tuple[str, str, str]:
            self.d.tap_label("AC")
            bounds = self._editor_bounds()
            if bounds is None:
                raise NotAvailable("Expression box bounds were not exposed.")
            x1, y1, x2, y2 = bounds
            x, y = x1 + max(12, min(36, (x2 - x1) // 12)), (y1 + y2) // 2
            self._hold(x, y)
            labels = self.d.labels()
            expected = [name for name in ("MUse", "Paste", "Select all") if case_insensitive_match(labels, [name])]
            if len(expected) >= 2:
                return "PASS", "; ".join(expected), "Holding the empty left side of the expression box exposed the caret-menu actions; screenshot retained for visual check that no operand was selected."
            if not expected and any("selection" in label.casefold() for label in labels):
                return "FAIL", " | ".join(labels), "The empty-box hold appears to have selected existing text instead of showing the caret menu."
            raise NotAvailable(f"Caret menu items were not exposed by UIAutomator/OCR: {labels!r}")
        self._case("B11", "B11", "Hold empty expression-box space for caret menu", "MUse, Paste and Select all; no operand selected", b11)

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
            labels = self.d.labels()
            menu_tap = self._try_tap(["More options", "More", "Menu"])
            if menu_tap is None:
                self.d.adb("shell", "input", "tap", str(self.d._width - 28), str(round(self.d._height * 0.13)))
                self._invalidate()
            labels = self.d.labels()
            effects = case_insensitive_match(labels, ["Effects"])
            memory = case_insensitive_match(labels, ["Memory"])
            other = [name for name in ("History", "Settings", "Help", "Theme") if case_insensitive_match(labels, [name])]
            if effects and (memory or len(other) >= 1):
                return "PASS", " | ".join(labels), "The overflow menu opened and exposed Effects plus calculator menu actions. This smoke check does not verify the exact item count or reorder behavior."
            return "FAIL", " | ".join(labels), "The overflow menu did not expose the expected Effects and menu actions."
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
                shape_entry = case_insensitive_match(self.d.labels(), ["Key shape", "Key shapes", "Button shape"])
            if not shape_entry:
                raise NotAvailable(f"Key shape entry was not visible in the menu: {self.d.labels()!r}")
            self.d.tap_label(shape_entry, partial=True, timeout=2.0)
            labels = self.d.labels()
            choices = [name for name in ("Circle", "Squircle", "Pill", "Rounded square", "No shape")
                       if case_insensitive_match(labels, [name])]
            if len(choices) < 4:
                return "FAIL", " | ".join(labels), f"The key-shape picker exposed only {len(choices)} of the five named shapes: {choices!r}."
            selected = self._try_tap(["Circle"])
            if not selected:
                return "FAIL", "; ".join(choices), "Circle was listed but could not be selected."
            return "PASS", "picker=" + "; ".join(choices) + "; selected=Circle", "The new picker exposed at least four named key silhouettes and accepted a Circle selection. Persistence and pixel-perfect geometry are not inferred from this one view."
        self._case("C10", "C10", "Open key-shape picker and select Circle", "Picker presents Circle/Squircle/Pill/Rounded square/No shape", c10)

        def h1_h2() -> tuple[str, str, str]:
            light_shot = self.d.report_dir / "evidence/h1-light-theme.png"
            dark_shot = self.d.report_dir / "evidence/h2-dark-theme.png"
            labels = self.d.labels()
            if self._try_tap(["Settings"]) is None:
                if self._try_tap(["More options", "More", "Menu"]) is None:
                    self.d.adb("shell", "input", "tap", str(self.d._width - 28), str(round(self.d._height * 0.13)))
                    self._invalidate()
                if self._try_tap(["Settings"]) is None:
                    raise NotAvailable(f"Settings entry was not visible: {self.d.labels()!r}")
            labels = self.d.labels()
            if self._try_tap(["Theme", "Appearance"]) is None:
                raise NotAvailable(f"Theme settings were not visible: {labels!r}")
            theme_labels = self.d.labels()
            if self._try_tap(["Light"]) is None:
                raise NotAvailable(f"Light theme option was not visible: {theme_labels!r}")
            time.sleep(0.4)
            light_path = self.d.screenshot(str(light_shot.relative_to(self.d.report_dir)))
            self.d._last_tree = None
            if self._try_tap(["Dark"]) is None:
                # Return to the theme choice page if tapping Light closes the dialog.
                if self._try_tap(["Settings"]) is not None and self._try_tap(["Theme", "Appearance"]) is not None:
                    self._invalidate()
                if self._try_tap(["Dark"]) is None:
                    raise NotAvailable(f"Dark theme option was not visible after selecting Light: {self.d.labels()!r}")
            time.sleep(0.4)
            dark_path = self.d.screenshot(str(dark_shot.relative_to(self.d.report_dir)))
            if not light_path or not dark_path:
                return "ERROR", "light screenshot=" + str(bool(light_path)) + "; dark screenshot=" + str(bool(dark_path)), "A theme transition was attempted but a required screenshot was not captured."
            light_digest = hashlib.sha256(light_shot.read_bytes()).hexdigest()
            dark_digest = hashlib.sha256(dark_shot.read_bytes()).hexdigest()
            if light_digest != dark_digest:
                return "PASS", f"Light screenshot SHA-256 {light_digest}; Dark screenshot SHA-256 {dark_digest}", "Both user-selectable theme options were reached and captured; screenshots differ. Review the embedded proof for exact color/caret claims."
            return "FAIL", "Light and Dark screenshot bytes were identical", "The screenshot did not change after selecting the alternate theme."
        self._case("H1-H2", "H1/H2", "Switch between Light and Dark themes", "Light and Dark options visibly change the app", h1_h2)

    def _open_apps_hub(self) -> list[str]:
        labels = self.d.labels()
        match = case_insensitive_match(labels, ["Apps"])
        if match is None:
            raise NotAvailable(f"Apps navigation control was not visible: {labels!r}")
        self.d.tap_label(match, timeout=2.0)
        time.sleep(0.4)
        self._invalidate()
        return self.d.labels()

    def _return_to_apps(self) -> None:
        labels = self.d.labels()
        apps = case_insensitive_match(labels, ["Apps"])
        if apps:
            self.d.tap_label(apps, timeout=2.0)
            self._invalidate()
            return
        self.d.adb("shell", "input", "keyevent", "4")
        self._invalidate()

    def _scroll_for_labels(self, candidates: Iterable[str]) -> str | None:
        for _ in range(4):
            labels = self.d.labels()
            found = case_insensitive_match(labels, candidates)
            if found:
                return found
            self._swipe(
                self.d._width // 2, round(self.d._height * 0.78),
                self.d._width // 2, round(self.d._height * 0.36), 400,
            )
        return case_insensitive_match(self.d.labels(), candidates)

    def run_app_surface_cases(self) -> None:
        def a2() -> tuple[str, str, str]:
            labels = self.d.labels()
            title = case_insensitive_match(labels, ["MySpace"])
            if not title:
                return "FAIL", " | ".join(labels), "The installed MySpace header title was not exposed on the calculator screen."
            return "PASS", " | ".join(labels), "The app header exposes the MySpace identity; the accompanying screenshot shows the installed app's user-visible mark. The launcher-drawer icon was not separately pixel-tested."
        self._case("A2", "A2", "Inspect MySpace header identity", "MySpace identity and mark are visible in the app header", a2)

        def hub() -> tuple[str, str, str]:
            labels = self._open_apps_hub()
            feature_names = ("Notes", "Calendar", "Music", "Recorder", "Scanner", "Files")
            visible = [name for name in feature_names if case_insensitive_match(labels, [name])]
            if len(visible) >= 2 and not self.d.is_calculator_screen():
                return "PASS", "feature entries=" + "; ".join(visible) + "; labels=" + " | ".join(labels), "The user-visible Apps destination exposed multiple guide features; their individual landing screens are reported separately."
            return "BLOCKED", "visible feature entries=" + "; ".join(visible) + "; labels=" + " | ".join(labels), "Apps navigation responded but the feature hub could not be distinguished from accessible labels; screenshot retained for review."
        self._case("G-HUB", "G", "Open the Apps hub", "Visible app destinations open from Apps", hub)

        def ad_scan() -> tuple[str, str, str]:
            labels = self.d.labels()
            ad_labels = [value for value in labels if re.search(r"\b(ad|advertisement|sponsored)\b", value, re.I)]
            if ad_labels:
                return "FAIL", "; ".join(ad_labels), "Ad-like labels were visible in the sampled app hub. This is a UI-label observation, not a network-traffic audit."
            return "PASS", f"Scanned {len(labels)} accessible labels; no ad/advertisement/sponsored label found", "No ad indicators appeared in the sampled Apps hub labels. This does not prove an app-wide or network-level ad audit."
        self._case("ADS-SAMPLE", "A/G", "Check sampled home surfaces for ad indicators", "No visible ad labels on sampled user screens", ad_scan)

        feature_aliases = [
            ("G-NOTES", "Notes", ["Notes", "Note"]),
            ("G-CALENDAR", "Calendar", ["Calendar"]),
            ("G-MUSIC", "Music", ["Music"]),
            ("G-RECORDER", "Recorder", ["Recorder", "Voice recorder"]),
            ("G-SCANNER", "Scanner", ["Scanner", "Scan"]),
            ("G-FILES", "Files", ["Files", "File manager"]),
        ]
        for case_id, feature, aliases in feature_aliases:
            def open_feature(case_id: str = case_id, feature: str = feature, aliases: list[str] = aliases) -> tuple[str, str, str]:
                self._return_to_apps()
                match = self._scroll_for_labels(aliases)
                if not match:
                    raise NotAvailable(f"{feature} entry was not exposed in the Apps hub after four screen scrolls.")
                before = self.d.labels()
                self.d.tap_label(match, partial=True, timeout=2.0)
                time.sleep(0.45)
                labels = self.d.labels()
                marker = case_insensitive_match(labels, aliases)
                screen_changed = set(labels) != set(before)
                still_calculator = self.d.is_calculator_screen()
                actual = "opened=" + match + "; screen changed=" + str(screen_changed) + "; calculator screen=" + str(still_calculator) + "; labels=" + " | ".join(labels)
                if marker and screen_changed and not still_calculator:
                    return "PASS", actual, "The feature landing screen opened from the Apps hub. Its deep workflow (e.g., reminders, recording, scanning or editing) is not inferred from opening it."
                return "BLOCKED", actual, "The tap did not produce a positively identifiable landing-screen transition; screenshot retained for visual review."
            self._case(case_id, "G", f"Open {feature} from Apps", f"User can reach the {feature} landing screen", open_feature)

        def diagnostics() -> tuple[str, str, str]:
            self._return_to_apps()
            settings = self._scroll_for_labels(["Settings"])
            if not settings:
                # Settings commonly lives in the calculator overflow rather than the hub.
                self.d.navigate_to_calculator(self.package)
                if self._try_tap(["More options", "More", "Menu"]) is None:
                    self.d.adb("shell", "input", "tap", str(self.d._width - 28), str(round(self.d._height * 0.13)))
                    self._invalidate()
                settings = case_insensitive_match(self.d.labels(), ["Settings"])
            if not settings:
                raise NotAvailable("Settings entry was not visible from Apps or the calculator overflow.")
            self.d.tap_label(settings, timeout=2.0)
            self._invalidate()
            diag = case_insensitive_match(self.d.labels(), ["Diagnostics"])
            if not diag:
                raise NotAvailable(f"Settings opened but Diagnostics was not visible: {self.d.labels()!r}")
            self.d.tap_label(diag, timeout=2.0)
            self._invalidate()
            labels = self.d.labels()
            if case_insensitive_match(labels, ["Diagnostics", "Log", "Share", "Export"]):
                return "PASS", " | ".join(labels), "The user navigated to Diagnostics. Local save/share behavior and log contents were not exercised."
            return "BLOCKED", " | ".join(labels), "Diagnostics destination opened but did not expose a recognizable action label."
        self._case("G-DIAGNOSTICS", "G", "Open Settings and Diagnostics", "Reach the log collector screen", diagnostics)

        def sampled_ad_sweep() -> tuple[str, str, str]:
            labels = self.d.labels()
            ad_labels = [value for value in labels if re.search(r"\b(ad|advertisement|sponsored)\b", value, re.I)]
            if ad_labels:
                return "FAIL", "; ".join(ad_labels), "Ad-like text was detected on the current feature screen."
            return "PASS", f"Scanned current screen: {len(labels)} accessible labels; no ad indicator", "No ad-like labels were visible on the final sampled feature screen; this is not a complete advertising/privacy audit."
        self._case("ADS-FEATURE", "A/G", "Sample a feature screen for ad indicators", "No ad labels on the sampled feature screen", sampled_ad_sweep)

    def run_standalone_cases(self) -> None:
        def header() -> tuple[str, str, str]:
            labels = self.d.labels()
            identity = case_insensitive_match(labels, ["MyCalc", "Standalone"])
            if identity:
                return "PASS", " | ".join(labels), "The installed standalone calculator identifies itself in the visible app header."
            return "BLOCKED", " | ".join(labels), "No accessible MyCalc/standalone label was exposed; screenshot retained."
        self._case("F-HEADER", "F", "Inspect standalone MyCalc identity", "MyCalc is visibly distinct as the standalone app", header)

        def ad_scan() -> tuple[str, str, str]:
            labels = self.d.labels()
            matches = [value for value in labels if re.search(r"\b(ad|advertisement|sponsored)\b", value, re.I)]
            if matches:
                return "FAIL", "; ".join(matches), "An ad-like label appeared on the sampled standalone calculator screen."
            return "PASS", f"Scanned {len(labels)} accessible labels; no ad indicator", "No ad label was found on the sampled standalone calculator screen; not a full network/app-wide audit."
        self._case("F-ADS", "F", "Sample standalone calculator for ad indicators", "No visible ad labels", ad_scan)

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

        # The existing calculator suite uses one device screen and direct keypad
        # taps; these probes continue from the same installed APK for true user
        # interaction rather than reopening a source-built app.
        if self.suite == "myspace-core":
            self.run_interaction_cases()
        elif self.suite == "myspace-modules":
            self.run_app_surface_cases()
        else:
            self.run_standalone_cases()
            # F says the same calculator is shipped standalone, so exercise the
            # same representative editing/theme journeys on that exact APK too.
            self.run_interaction_cases()

        diagnostics = self._capture_runtime_diagnostics()
        calc_counts = self.calculator_report.get("summary", {})
        user_counts: dict[str, int] = {}
        for row in self.results:
            status = row["status"]
            user_counts[status] = user_counts.get(status, 0) + 1
        metadata = {
            "report_title": "MySpace user-facing APK QA" if self.package == DEFAULT_PACKAGE else "Standalone MyCalc user-facing APK QA",
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
                "Feature-page opens are smoke checks, not proof that every deep workflow works.",
                "Ad checks scan visible text on sampled screens; they are not a network or whole-app ad audit.",
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
    parser.add_argument("--suite", choices=("myspace-core", "myspace-modules", "mycalc"), required=True)
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
