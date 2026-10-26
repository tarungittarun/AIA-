#!/usr/bin/env python3
"""Black-box UI QA for the pinned MySpace and standalone MyCalc APKs.

The test runs only against the Calculator feature. It prefers a compressed
UIAutomator hierarchy and adb input; if Android kills UiAutomation, screenshots
and Tesseract OCR provide a visual fallback. Results and evidence are saved.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable

DEFAULT_PACKAGE = "app.space.one"
STANDALONE_PACKAGE = "app.space.calc"
EXPECTED_APK_SHA256 = "629442fc1d54508690f8c75664ea8be7611fef14a74f4edcf6f2bd1cab40068d"
EXPECTED_APK_SHA256_BY_PACKAGE = {
    DEFAULT_PACKAGE: EXPECTED_APK_SHA256,
    STANDALONE_PACKAGE: "342f51bdbb12539f44971fc945d427714ac8cf74bf01a7fa8fccf02660e1f3fa",
}
GOOGLE_CALCULATOR_PACKAGE = "com.google.android.calculator"
CALCULATOR_TEST_IDS = tuple(f"TC-CALC-{number:03d}" for number in range(1, 11))

BASIC_GRID = {
    "AC": (0, 0), "( )": (0, 1), "%": (0, 2), "÷": (0, 3),
    "7": (1, 0), "8": (1, 1), "9": (1, 2), "×": (1, 3),
    "4": (2, 0), "5": (2, 1), "6": (2, 2), "−": (2, 3),
    "1": (3, 0), "2": (3, 1), "3": (3, 2), "+": (3, 3),
    "0": (4, 0), ".": (4, 1), "⌫": (4, 2), "=": (4, 3),
}
SCIENTIFIC_GRID = {
    "√(": (0, 0), "π": (0, 1), "^": (0, 2), "!": (0, 3),
    "Deg": (1, 0), "sin(": (1, 1), "cos(": (1, 2), "tan(": (1, 3),
    "Inv": (2, 0), "e": (2, 1), "ln(": (2, 2), "log(": (2, 3),
}


class QaError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def clean(value: str) -> str:
    return " ".join((value or "").replace("\u00a0", " ").split())


def bounds_center(bounds: str) -> tuple[int, int] | None:
    match = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds or "")
    if not match:
        return None
    x1, y1, x2, y2 = map(int, match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2


def bounds_bottom(bounds: str) -> int:
    match = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds or "")
    return int(match.group(4)) if match else 0


class AndroidUi:
    def __init__(self, report_dir: Path, label: str = "target") -> None:
        self.report_dir = report_dir
        self.label = label
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self._last_tree: ET.Element | None = None
        self._ocr_mode = False
        self._scientific_open = False
        self.ui_method = "uiautomator-compressed"
        self._width, self._height = self._screen_size()

    def adb(self, *args: str, timeout: int = 30, check: bool = True) -> str:
        proc = subprocess.run(
            ["adb", *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        if check and proc.returncode != 0:
            raise QaError(f"adb {' '.join(args)} failed ({proc.returncode}): {clean(proc.stdout)}")
        return proc.stdout

    def _screen_size(self) -> tuple[int, int]:
        output = self.adb("shell", "wm", "size", check=False)
        match = re.search(r"(\d+)x(\d+)", output)
        return (int(match.group(1)), int(match.group(2))) if match else (1080, 1920)

    def launch(self, package: str) -> None:
        try:
            self.adb(
                "shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1",
                timeout=180,
            )
        except subprocess.TimeoutExpired:
            # On software-accelerated emulators Monkey can outlive its adb shell
            # timeout even though the Activity launch has already been delivered.
            # Continue to inspect the UI; navigation assertions decide if launch worked.
            print(
                f"::warning title=Android app launch::Monkey launch timed out for {package}; "
                "continuing to inspect the device UI.",
                flush=True,
            )
        time.sleep(2.0)
        self._last_tree = None
        self._scientific_open = False

    def _reboot_after_system_anr(self, package: str) -> None:
        """Perform one bounded emulator reboot if Android's system process stays ANR."""
        print(
            "::warning title=System ANR recovery::The system process stayed unresponsive after "
            "three Wait retries; rebooting the test emulator once.",
            flush=True,
        )
        try:
            self.adb("reboot", timeout=20, check=False)
        except subprocess.TimeoutExpired:
            # `adb reboot` may drop the transport before its shell command exits.
            pass
        try:
            self.adb("wait-for-device", timeout=180)
        except Exception as error:
            raise QaError(f"Emulator did not reconnect after ANR recovery reboot: {error}") from error

        boot_deadline = time.monotonic() + 240
        while time.monotonic() < boot_deadline:
            try:
                if self.adb(
                    "shell", "getprop", "sys.boot_completed", timeout=15, check=False
                ).strip() == "1":
                    break
            except Exception:
                pass
            time.sleep(3.0)
        else:
            raise QaError("Emulator did not finish rebooting within 240 seconds after system ANR")

        package_deadline = time.monotonic() + 120
        package_line = f"package:{package}"
        while time.monotonic() < package_deadline:
            try:
                packages = self.adb(
                    "shell", "cmd", "package", "list", "packages", timeout=20, check=False
                )
                if package_line in packages.splitlines():
                    break
            except Exception:
                pass
            time.sleep(3.0)
        else:
            raise QaError(f"PackageManager did not report installed target package {package!r} after reboot")

        for setting in ("window_animation_scale", "transition_animation_scale", "animator_duration_scale"):
            self.adb("shell", "settings", "put", "global", setting, "0", check=False)
        self._last_tree = None
        self._ocr_mode = False
        self._scientific_open = False
        self.ui_method = "uiautomator-compressed"
        time.sleep(5.0)
        print(
            f"::notice title=System ANR recovery::Emulator rebooted; {package} remains installed.",
            flush=True,
        )

    def force_stop(self, package: str) -> None:
        self.adb("shell", "am", "force-stop", package, check=False)
        time.sleep(0.5)
        self._last_tree = None
        self._scientific_open = False

    def _capture_uiautomator_diagnostics(self, error: Exception) -> Path:
        details = [f"UI hierarchy failure: {type(error).__name__}: {error}"]
        probes = (
            ("screen size", ("shell", "wm", "size"), 15),
            ("activity state", ("shell", "dumpsys", "activity", "activities"), 45),
            ("system_server memory", ("shell", "dumpsys", "meminfo", "system_server"), 45),
            ("guest memory", ("shell", "cat", "/proc/meminfo"), 15),
            ("recent logcat", ("logcat", "-d", "-t", "400"), 45),
        )
        for title, args, timeout in probes:
            details.append(f"\n--- {title} ---")
            try:
                details.append(self.adb(*args, timeout=timeout, check=False))
            except Exception as probe_error:
                details.append(f"Diagnostic command failed: {type(probe_error).__name__}: {probe_error}")
        try:
            screenshot = self.screenshot(f"evidence/{self.label}-uiautomator-failure.png")
            details.append(f"\nScreenshot: {screenshot or 'capture failed'}")
        except Exception as screenshot_error:
            details.append(f"\nScreenshot failed: {type(screenshot_error).__name__}: {screenshot_error}")
        path = self.report_dir / f"{self.label}-uiautomator-diagnostics.txt"
        path.write_text("\n".join(details), encoding="utf-8")
        print(f"::notice title=UIAutomator diagnostics::Saved device state and logcat to {path}.", flush=True)
        return path

    def _ocr_tree(self) -> ET.Element:
        image = self.screenshot(f"evidence/{self.label}-ocr-current.png")
        if not image:
            raise QaError("adb screencap did not return a screenshot for OCR fallback")
        try:
            proc = subprocess.run(
                ["tesseract", image, "stdout", "--psm", "11", "tsv"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=45,
                check=False,
            )
        except FileNotFoundError as exc:
            raise QaError("Tesseract is not installed; screenshot OCR fallback is unavailable") from exc
        except subprocess.TimeoutExpired as exc:
            raise QaError("Tesseract screenshot OCR exceeded 45 seconds") from exc
        if proc.returncode != 0:
            raise QaError(f"Tesseract OCR failed ({proc.returncode}): {clean(proc.stderr)}")

        root = ET.Element("hierarchy", {"source": "screenshot-ocr"})
        try:
            rows = csv.DictReader(proc.stdout.splitlines(), delimiter="\t")
            for row in rows:
                if row.get("level") != "5":
                    continue
                text = clean(row.get("text", ""))
                if not text:
                    continue
                left, top = int(row["left"]), int(row["top"])
                width, height = int(row["width"]), int(row["height"])
                node = ET.SubElement(root, "node")
                node.attrib.update({
                    "text": text,
                    "bounds": f"[{left},{top}][{left + width},{top + height}]",
                    "clickable": "true" if top >= int(self._height * 0.40) else "false",
                    "visible-to-user": "true",
                    "class": "screenshot-ocr",
                })
        except (KeyError, TypeError, ValueError) as exc:
            raise QaError(f"Could not parse Tesseract TSV output: {clean(proc.stdout[:500])}") from exc
        if not list(root):
            raise QaError("Tesseract OCR returned no visible text")
        return root

    def _recover_hierarchy_with_ocr(self, error: Exception) -> ET.Element:
        diagnostic = self._capture_uiautomator_diagnostics(error)
        try:
            tree = self._ocr_tree()
        except Exception as ocr_error:
            raise QaError(
                f"UIAutomator failed ({error}); screenshot OCR also failed ({ocr_error}); "
                f"diagnostics={diagnostic}"
            ) from ocr_error
        self._ocr_mode = True
        self.ui_method = "screenshot-ocr-fallback"
        print(
            "::warning title=UI inspection fallback::UIAutomator failed; using screenshot OCR "
            f"for labels and visual checks. Device diagnostics: {diagnostic}",
            flush=True,
        )
        self._last_tree = tree
        return tree

    @staticmethod
    def _parse_hierarchy(raw: str, method: str) -> ET.Element:
        if not raw or not raw.strip():
            raise QaError(f"{method} returned an empty hierarchy file")
        try:
            tree = ET.fromstring(raw)
        except ET.ParseError as exc:
            raise QaError(f"{method} returned malformed hierarchy XML: {exc}") from exc
        if not any(node.tag == "node" for node in tree.iter()):
            raise QaError(f"{method} returned hierarchy XML without any UI nodes")
        return tree

    def dump(self) -> ET.Element:
        if self._last_tree is not None:
            return self._last_tree
        if self._ocr_mode:
            self._last_tree = self._ocr_tree()
            return self._last_tree

        attempts = (
            ("uiautomator-compressed", True, "/sdcard/window-compressed.xml"),
            ("uiautomator-standard", False, "/sdcard/window-standard.xml"),
            ("uiautomator-standard", False, "/sdcard/window-standard-retry.xml"),
        )
        errors: list[str] = []
        for index, (method, compressed, path) in enumerate(attempts):
            try:
                command = ["shell", "uiautomator", "dump"]
                if compressed:
                    command.append("--compressed")
                command.append(path)
                self.adb(*command, timeout=90)
                raw = self.adb("exec-out", "cat", path, timeout=30)
                tree = self._parse_hierarchy(raw, method)
                if index:
                    print(
                        "::warning title=UIAutomator::Compressed/previous hierarchy dump was "
                        "empty or malformed; a standard retry succeeded.",
                        flush=True,
                    )
                self.ui_method = method
                self._last_tree = tree
                return tree
            except Exception as error:
                errors.append(f"{method} attempt {index + 1}: {type(error).__name__}: {error}")
                self._last_tree = None
                if index < len(attempts) - 1:
                    # Allow UiAutomation/system UI to recover instead of
                    # hammering the service with immediate repeated dumps.
                    time.sleep(1.0 + index)

        return self._recover_hierarchy_with_ocr(QaError("; ".join(errors)))

    @staticmethod
    def _compact_label(value: str) -> str:
        return (clean(value).casefold().replace(" ", "")
                .replace("×", "x").replace("÷", "/")
                .replace("−", "-").replace("–", "-"))

    @classmethod
    def _label_equivalent(cls, actual: str, expected: str) -> bool:
        actual_value = cls._compact_label(actual)
        expected_value = cls._compact_label(expected)
        aliases = {
            "×": {"x", "*"}, "÷": {"/"}, "−": {"-"},
            "( )": {"()", "(", ")"}, "√(": {"√", "v("},
            "sin(": {"sin"}, "cos(": {"cos"}, "tan(": {"tan"},
            "ln(": {"ln"}, "log(": {"log"},
        }
        return actual_value == expected_value or actual_value in aliases.get(expected, set())

    def _grid_identity(self, text: str) -> tuple[str, int, int] | None:
        for label, (row, col) in BASIC_GRID.items():
            if self._label_equivalent(text, label):
                return "basic", row, col
        for label, (row, col) in SCIENTIFIC_GRID.items():
            if self._label_equivalent(text, label):
                return "scientific", row, col
        return None

    def _ocr_grid_observations(self) -> list[tuple[int, int, float, float]]:
        if not self._ocr_mode or self.label != "target" or self._last_tree is None:
            return []
        observations: list[tuple[int, int, float, float]] = []
        for node in self._last_tree.iter("node"):
            center = bounds_center(node.attrib.get("bounds", ""))
            if center is None or center[1] < int(self._height * 0.40):
                continue
            identity = self._grid_identity(node.attrib.get("text", ""))
            if identity is None:
                continue
            group, row, col = identity
            if group == "scientific":
                if not self._scientific_open:
                    continue
            elif self._scientific_open:
                row += 3
            observations.append((row, col, float(center[0]), float(center[1])))
        return observations

    @staticmethod
    def _fit_coordinate(points: list[tuple[int, float]], index: int, fallback: float) -> float:
        if not points:
            return fallback
        if len({key for key, _ in points}) < 2:
            return statistics.median(value for _, value in points)
        mean_x = statistics.mean(key for key, _ in points)
        mean_y = statistics.mean(value for _, value in points)
        denominator = sum((key - mean_x) ** 2 for key, _ in points)
        if not denominator:
            return fallback
        slope = sum((key - mean_x) * (value - mean_y) for key, value in points) / denominator
        return mean_y + slope * (index - mean_x)

    def _ocr_grid_point(self, label: str) -> tuple[int, int] | None:
        if not self._ocr_mode or self.label != "target":
            return None
        identity = self._grid_identity(label)
        if identity is None:
            return None
        group, row, col = identity
        if group == "scientific":
            if not self._scientific_open:
                return None
        elif self._scientific_open:
            row += 3
        observations = self._ocr_grid_observations()
        x_points = [(c, x) for _, c, x, _ in observations]
        y_points = [(r, y) for r, _, _, y in observations]
        x_fallback = self._width * (0.15 + col * 0.233)
        y_fallback = self._height * (0.50 + row * (0.10 if not self._scientific_open else 0.0625))
        x = self._fit_coordinate(x_points, col, x_fallback)
        y = self._fit_coordinate(y_points, row, y_fallback)
        return round(x), round(y)

    def _toggle_chevron_with_ocr(self) -> None:
        observations = self._ocr_grid_observations()
        x_points = [(col, x) for _, col, x, _ in observations]
        y_points = [(row, y) for row, _, _, y in observations]
        col0 = self._fit_coordinate(x_points, 0, self._width * 0.15)
        row0 = self._fit_coordinate(y_points, 0, self._height * 0.50)
        row1 = self._fit_coordinate(y_points, 1, row0 + self._height * 0.10)
        row_spacing = max(1.0, row1 - row0)
        col1 = self._fit_coordinate(x_points, 1, col0 + self._width * 0.233)
        col_spacing = max(1.0, col1 - col0)
        x = round(col0 - col_spacing * 0.22)
        y = round(row0 - row_spacing * 0.80)
        self.adb("shell", "input", "tap", str(x), str(y))
        self._scientific_open = True
        self._last_tree = None
        time.sleep(0.35)

    @staticmethod
    def _visible(node: ET.Element) -> bool:
        return node.attrib.get("visible-to-user", "true").lower() != "false"

    def nodes(self) -> list[ET.Element]:
        return list(self.dump().iter())

    def labels(self) -> list[str]:
        values: list[str] = []
        for node in self.nodes():
            if not self._visible(node):
                continue
            for key in ("text", "content-desc"):
                value = clean(node.attrib.get(key, ""))
                if value and value not in values:
                    values.append(value)
        return values

    @classmethod
    def _node_matches(cls, node: ET.Element, label: str, partial: bool = False) -> bool:
        actuals = [clean(node.attrib.get("text", "")), clean(node.attrib.get("content-desc", ""))]
        if partial:
            return any(label.casefold() in actual.casefold() for actual in actuals if actual)
        return any(cls._label_equivalent(actual, label) for actual in actuals if actual)

    def _matching_nodes(self, label: str, partial: bool = False) -> list[ET.Element]:
        return [
            node for node in self.nodes()
            if self._visible(node) and self._node_matches(node, label, partial)
        ]

    def tap_label(
        self,
        label: str,
        *,
        partial: bool = False,
        timeout: float = 1.2,
        capture_display: bool = False,
    ) -> list[str] | None:
        deadline = time.monotonic() + timeout
        last_labels: list[str] = []
        while time.monotonic() < deadline:
            candidates = self._matching_nodes(label, partial)
            if self._grid_identity(label):
                # Key labels can also appear in the editable display (notably "0"
                # immediately after AC). Restrict keypad taps to the lower control
                # region for both hierarchy and OCR trees.
                candidates = [
                    node for node in candidates
                    if (point := bounds_center(node.attrib.get("bounds", "")))
                    and point[1] >= int(self._height * 0.40)
                ]
            last_labels = self.labels()
            before = self.display_texts() if capture_display else None
            if candidates:
                # Prefer a directly clickable control; tapping a non-clickable label
                # still works for cards whose parent owns the click listener.
                candidates.sort(key=lambda n: (
                    n.attrib.get("clickable", "false").lower() != "true",
                    "edittext" in n.attrib.get("class", "").casefold(),
                    -((bounds_center(n.attrib.get("bounds", "")) or (0, 0))[1]),
                ))
                for node in candidates:
                    point = bounds_center(node.attrib.get("bounds", ""))
                    if point:
                        self.adb("shell", "input", "tap", str(point[0]), str(point[1]))
                        time.sleep(0.35)
                        self._last_tree = None
                        return before
            if self._ocr_mode:
                point = self._ocr_grid_point(label)
                if point:
                    self.adb("shell", "input", "tap", str(point[0]), str(point[1]))
                    time.sleep(0.35)
                    self._last_tree = None
                    return before
            self._last_tree = None
            time.sleep(0.15)
        raise QaError(f"Could not find tappable UI label {label!r}; visible labels: {last_labels}")

    def tap_first(self, labels: Iterable[str]) -> str:
        current = self.labels()
        for label in labels:
            if label in current:
                self.tap_label(label)
                return label
        raise QaError(f"None of the labels {list(labels)!r} is visible; visible labels: {current}")

    def screenshot(self, filename: str) -> str:
        path = self.report_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            ["adb", "exec-out", "screencap", "-p"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=20,
        )
        if proc.returncode == 0 and proc.stdout:
            path.write_bytes(proc.stdout)
            return str(path)
        return ""

    def save_hierarchy(self, filename: str) -> str:
        try:
            root = self.dump()
            path = self.report_dir / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))
            return str(path)
        except Exception:
            return ""

    def is_calculator_screen(self) -> bool:
        labels = self.labels()
        has_ac = any(self._label_equivalent(label, "AC") for label in labels)
        has_equals = any(self._label_equivalent(label, "=") for label in labels)
        has_operator = any(
            self._label_equivalent(actual, operator)
            for actual in labels for operator in ("÷", "×", "−", "+")
        )
        return has_ac and has_equals and has_operator

    @staticmethod
    def _is_anr_dialog(labels: Iterable[str]) -> bool:
        text = " ".join(labels).casefold()
        return "responding" in text and ("isn't" in text or "not responding" in text)

    def navigate_to_calculator(self, package: str) -> None:
        self.launch(package)
        # The suite host may start on its home screen. Open only its Calculator
        # tile/route; no other feature is used by this test.
        route_labels = ("Calculator", "Apps", "Menu", "Clock")
        anr_waits = 0
        rebooted_after_anr = False
        for _ in range(8):
            if self.is_calculator_screen():
                return
            labels = self.labels()
            if self._is_anr_dialog(labels):
                if anr_waits >= 3:
                    if rebooted_after_anr:
                        break
                    self._reboot_after_system_anr(package)
                    rebooted_after_anr = True
                    anr_waits = 0
                    self.launch(package)
                    continue
                if not any(label.casefold() == "wait" for label in labels):
                    break
                self.tap_label("Wait", timeout=2.0)
                anr_waits += 1
                print(
                    f"::warning title=Android system responsiveness::Detected an ANR dialog; "
                    f"selected Wait ({anr_waits}/3).",
                    flush=True,
                )
                time.sleep(8.0)
                continue
            tapped = False
            for label in route_labels:
                if label in labels:
                    self.tap_label(label)
                    tapped = True
                    time.sleep(0.45)
                    if self.is_calculator_screen():
                        return
                    break
            if not tapped:
                # Scroll the app picker/list once if the Calculator route is below
                # the initially visible area.
                self.adb(
                    "shell", "input", "swipe",
                    str(self._width // 2), str(int(self._height * 0.78)),
                    str(self._width // 2), str(int(self._height * 0.32)), "350",
                )
                self._last_tree = None
                time.sleep(0.4)
        screenshot = self.screenshot(f"{self.label}-navigation-failed.png")
        hierarchy = self.save_hierarchy(f"{self.label}-navigation-failed.xml")
        raise QaError(
            "The Calculator screen did not become available through suite navigation. "
            f"Screenshot={screenshot}; hierarchy={hierarchy}; visible labels={self.labels()}"
        )

    def ensure_basic_panel(self) -> None:
        labels = self.labels()
        close_labels = [
            label for label in labels
            if "close the extra keys" in label.casefold()
            or "close extra keys" in label.casefold()
        ]
        if close_labels:
            self.tap_label(close_labels[0])
            self._scientific_open = False
            time.sleep(0.35)
            return
        has_scientific_keys = any(
            self._label_equivalent(label, "sin(")
            or self._label_equivalent(label, "√(")
            for label in labels
        )
        if has_scientific_keys:
            if self._ocr_mode:
                self._scientific_open = True
                self._toggle_chevron_with_ocr()
                self._scientific_open = False
                return
            raise QaError(f"Scientific panel is open but its close control is missing: {labels}")
        self._scientific_open = False

    def ensure_scientific_panel(self) -> None:
        if self._scientific_open:
            return
        labels = self.labels()
        if any(self._label_equivalent(label, "sin(") for label in labels) or any(
            self._label_equivalent(label, "√(") for label in labels
        ):
            self._scientific_open = True
            return
        for candidate in ("Open the extra keys", "Show scientific keys", "Scientific keys"):
            if candidate in labels:
                self.tap_label(candidate)
                self._scientific_open = True
                time.sleep(0.25)
                return
        # The chevron's visible icon text may be blank while its description varies
        # by host theme/accessibility implementation.
        for label in labels:
            if "extra keys" in label.casefold() or "scientific" in label.casefold():
                self.tap_label(label)
                self._scientific_open = True
                time.sleep(0.25)
                return
        if self._ocr_mode:
            self._toggle_chevron_with_ocr()
            return
        raise QaError(f"Scientific panel toggle not found; visible labels: {labels}")

    def key(self, key: str) -> None:
        label = "( )" if key in ("(", ")") else key
        before = self.tap_label(label, timeout=1.5, capture_display=(key == "0"))
        if key != "0" or before is None:
            return

        # The screen's empty-expression placeholder is also "0", so that single
        # first-zero tap has no visible delta. Every later zero must change the
        # expression; wait briefly for the UI instead of silently proceeding when
        # the tap was ignored or hit a duplicate display label.
        displayed = [value for value in before if value.casefold() != "calculator"]
        if displayed in ([], ["0"]):
            return
        deadline = time.monotonic() + 1.5
        while time.monotonic() < deadline:
            after = self.display_texts()
            if after != before:
                return
            time.sleep(0.15)
        raise QaError(f"Key '0' did not change the visible expression; display remained {before!r}")

    def press_sequence(self, keys: Iterable[str]) -> None:
        for key in keys:
            self.key(key)

    def display_texts(self) -> list[str]:
        root = self.dump()
        values: list[tuple[int, str]] = []
        for node in root.iter():
            if not self._visible(node):
                continue
            text = clean(node.attrib.get("text", ""))
            if not text:
                continue
            klass = node.attrib.get("class", "")
            bounds = node.attrib.get("bounds", "")
            top = 0
            match = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
            if match:
                top = int(match.group(2))
            clickable = node.attrib.get("clickable", "false").lower() == "true"
            # Prefer the actual expression EditText and non-clickable text in the
            # display region. This excludes keypad digits from result assertions.
            if self._ocr_mode:
                is_display = not clickable and top < int(self._height * 0.43)
            else:
                is_display = "edittext" in klass.casefold() or (
                    not clickable and top < int(self._height * 0.58)
                )
            if is_display:
                values.append((top, text))
        ordered: list[str] = []
        for _, text in sorted(values):
            if text not in ordered:
                ordered.append(text)
        return ordered

    def result_visible(self, expected: str) -> bool:
        texts = self.display_texts()
        target = clean(expected)
        for text in texts:
            normalized = clean(text).replace("−", "-")
            if normalized == target or normalized == f"= {target}" or normalized.endswith(f"= {target}"):
                return True
        return False

    @staticmethod
    def normalize_expression(text: str) -> str:
        return re.sub(r"\s+", "", clean(text)).replace("−", "-")

    def expression_visible(self, expected: str) -> bool:
        target = self.normalize_expression(expected)
        return any(self.normalize_expression(text) == target for text in self.display_texts())

    def expression_suffix_visible(self, suffix: str) -> bool:
        target = self.normalize_expression(suffix)
        return any(
            self.normalize_expression(text).endswith(target)
            for text in self.display_texts()
        )

    def close_history_if_open(self) -> None:
        labels = self.labels()
        if "Close history" in labels:
            self.tap_label("Close history", timeout=2.0)
            time.sleep(0.35)

    def details(self) -> dict[str, Any]:
        return {
            "display_text": self.display_texts(),
            "visible_labels": self.labels(),
            "screen": f"{self._width}x{self._height}",
            "ui_inspection_method": self.ui_method,
        }


class CalculatorQa:
    def __init__(
        self,
        apk: Path,
        package: str,
        report_dir: Path,
        case_ids: set[str] | None = None,
    ) -> None:
        self.apk = apk
        self.package = package
        self.report_dir = report_dir
        self.report_dir.mkdir(parents=True, exist_ok=True)
        if case_ids is not None:
            unknown = case_ids - set(CALCULATOR_TEST_IDS)
            if unknown:
                raise QaError(f"Unknown calculator test IDs: {sorted(unknown)}")
            if not case_ids:
                raise QaError("At least one calculator test ID must be selected")
        self.case_ids = set(case_ids) if case_ids is not None else None
        self.device = AndroidUi(report_dir, "target")
        self.results: list[dict[str, Any]] = []
        self.reference: dict[str, Any] = {
            "requested": "Google Calculator (com.google.android.calculator)",
            "status": "NOT_CHECKED",
            "package": None,
            "note": "",
        }
        self.installed_packages: set[str] = set()

    def case_plan(self) -> set[str]:
        """Return this shard's IDs, adding TC-CALC-001 as the TC-010 comparator baseline."""
        selected = set(CALCULATOR_TEST_IDS) if self.case_ids is None else set(self.case_ids)
        if "TC-CALC-010" in selected:
            selected.add("TC-CALC-001")
        return selected

    @staticmethod
    def _history_result_visible(labels: Iterable[str], expected: str) -> bool:
        expected_text = clean(expected)
        for label in labels:
            result = clean(label)
            if result.startswith("="):
                result = result[1:].strip()
            if result == expected_text:
                return True
            decimal_suffix = result.removeprefix(expected_text + ".")
            if decimal_suffix and set(decimal_suffix) == {"0"}:
                return True
        return False

    def add_result(
        self,
        test_id: str,
        title: str,
        status: str,
        expected: str = "",
        actual: str = "",
        comment: str = "",
        evidence: str = "",
    ) -> None:
        row = {
            "id": test_id,
            "title": title,
            "status": status,
            "expected": expected,
            "actual": actual,
            "comment": comment,
            "evidence": evidence,
        }
        self.results.append(row)
        print(f"[{status}] {test_id} — {title}: {comment or actual or expected}", flush=True)
        # Keep each case outcome visible in GitHub's check annotations, even if
        # downloading the large evidence artifact later fails.
        notice = clean(
            f"{status}; expected={expected}; actual={actual}; comment={comment}"
        )[:1200]
        notice = notice.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::notice title={test_id}::{notice}", flush=True)

    def run_case(
        self,
        test_id: str,
        title: str,
        keys: list[str],
        expected: str,
        *,
        scientific: bool = False,
        defect: str | None = None,
    ) -> None:
        screenshot = ""
        try:
            self.device.close_history_if_open()
            if scientific:
                self.device.ensure_scientific_panel()
            else:
                self.device.ensure_basic_panel()
            self.device.tap_label("AC")
            self.device.press_sequence(keys)
            expected_expression = "".join(keys)
            typed = self.device.display_texts()
            if not self.device.expression_visible(expected_expression):
                screenshot = self.device.screenshot(f"evidence/{test_id.lower()}-input-mismatch.png")
                self.add_result(
                    test_id, title, "ERROR",
                    f"Input expression {expected_expression!r}, then result {expected!r}",
                    " | ".join(typed),
                    comment=(
                        "Input precondition failed: the visible expression did not match the "
                        "key sequence, so the calculation was not evaluated. This is an input/UI "
                        "automation finding, not a confirmed arithmetic defect."
                    ),
                    evidence=screenshot,
                )
                return
            self.device.key("=")
            time.sleep(0.4)
            actual = self.device.display_texts()
            screenshot = self.device.screenshot(f"evidence/{test_id.lower()}-target.png")
            expected_normalized = self.device.normalize_expression(expected_expression)
            if any(
                self.device.normalize_expression(value) == expected_normalized
                for value in actual
            ):
                self.add_result(
                    test_id, title, "ERROR",
                    f"Committed result {expected!r} for {expected_expression!r}",
                    " | ".join(actual),
                    comment=(
                        "Equals did not commit the calculation: the input expression is still visible. "
                        "A matching '= result' preview is not counted as a completed evaluation."
                    ),
                    evidence=screenshot,
                )
                return
            if self.device.result_visible(expected):
                self.add_result(
                    test_id, title, "PASS", expected,
                    " | ".join(actual),
                    comment="Observed result matched the expected calculator value.",
                    evidence=screenshot,
                )
            else:
                comment = f"Expected {expected!r}; visible display values were {actual!r}."
                if defect:
                    comment += f" Candidate defect: {defect}."
                self.add_result(
                    test_id, title, "FAIL", expected,
                    " | ".join(actual), comment=comment, evidence=screenshot,
                )
        except Exception as exc:  # Continue collecting independent evidence after a failure.
            screenshot = screenshot or self.device.screenshot(f"evidence/{test_id.lower()}-error.png")
            hierarchy = self.device.save_hierarchy(f"evidence/{test_id.lower()}-error.xml")
            self.add_result(
                test_id, title, "ERROR", expected, "",
                comment=f"{type(exc).__name__}: {exc}; hierarchy={hierarchy}",
                evidence=screenshot,
            )

    def run_chained_precision(self) -> None:
        test_id = "TC-CALC-008"
        title = "Chained calculations retain unrounded precision"
        try:
            self.device.close_history_if_open()
            self.device.ensure_basic_panel()
            self.device.tap_label("AC")
            self.device.press_sequence(["1", "÷", "3"])
            if not self.device.expression_visible("1÷3"):
                raise QaError(
                    f"Input precondition failed for 1÷3; display={self.device.display_texts()!r}"
                )
            self.device.key("=")
            time.sleep(0.3)
            first = self.device.display_texts()
            if any(
                self.device.normalize_expression(value)
                == self.device.normalize_expression("1÷3")
                for value in first
            ):
                raise QaError(f"First equals did not commit 1÷3; display={first!r}")
            self.device.press_sequence(["×", "3"])
            if not self.device.expression_suffix_visible("×3"):
                raise QaError(
                    f"Continuation input ×3 was not visible; first result={first!r}; "
                    f"display={self.device.display_texts()!r}"
                )
            self.device.key("=")
            time.sleep(0.35)
            actual = self.device.display_texts()
            if any(self.device.normalize_expression(value).endswith("×3") for value in actual):
                raise QaError(f"Second equals did not commit the ×3 continuation; display={actual!r}")
            screenshot = self.device.screenshot("evidence/tc-calc-008-target.png")
            # The numerical contract is exact here: (1 / 3) * 3 equals 1.
            if self.device.result_visible("1"):
                self.add_result(
                    test_id, title, "PASS", "1", " | ".join(actual),
                    comment="The result remained exact through the equals-then-operator flow.",
                    evidence=screenshot,
                )
            else:
                self.add_result(
                    test_id, title, "FAIL", "1", " | ".join(actual),
                    comment=(
                        "After 1 ÷ 3 =, the UI result was " + repr(first)
                        + "; multiplying by 3 did not return 1. This is consistent with "
                        "the screen feeding its rounded display string back into the next expression."
                    ),
                    evidence=screenshot,
                )
        except Exception as exc:
            screenshot = self.device.screenshot("evidence/tc-calc-008-error.png")
            hierarchy = self.device.save_hierarchy("evidence/tc-calc-008-error.xml")
            self.add_result(
                test_id, title, "ERROR", "1", "",
                comment=f"{type(exc).__name__}: {exc}; hierarchy={hierarchy}", evidence=screenshot,
            )

    def run_exponent_chain(self) -> None:
        test_id = "TC-CALC-009"
        title = "Scientific-notation result can be used in the next expression"
        try:
            self.device.close_history_if_open()
            self.device.ensure_scientific_panel()
            self.device.tap_label("AC")
            self.device.press_sequence(["1", "0", "^", "1", "5"])
            if not self.device.expression_visible("10^15"):
                raise QaError(
                    f"Input precondition failed for 10^15; display={self.device.display_texts()!r}"
                )
            self.device.key("=")
            time.sleep(0.25)
            first = self.device.display_texts()
            if any(
                self.device.normalize_expression(value)
                == self.device.normalize_expression("10^15")
                for value in first
            ):
                raise QaError(f"Equals did not commit 10^15; display={first!r}")
            self.device.press_sequence(["+", "1"])
            if not self.device.expression_suffix_visible("+1"):
                raise QaError(
                    f"Continuation input +1 was not visible after 10^15; "
                    f"first result={first!r}; display={self.device.display_texts()!r}"
                )
            self.device.key("=")
            time.sleep(0.35)
            actual = self.device.display_texts()
            normalized = [v.replace("E", "e").replace("−", "-") for v in actual]
            visible_error = any("error" in v.casefold() for v in normalized)
            if (
                any(self.device.normalize_expression(value).endswith("+1") for value in actual)
                and not visible_error
            ):
                raise QaError(f"Equals did not commit the +1 continuation; display={actual!r}")
            screenshot = self.device.screenshot("evidence/tc-calc-009-target.png")
            # If the exponent literal was accepted, the display should no longer be
            # exactly the preceding 1e+15 result; an error is also a failed chain.
            unchanged = any(v.strip() in ("1e+15", "1E+15") for v in normalized)
            error = visible_error
            if not unchanged and not error:
                self.add_result(
                    test_id, title, "PASS", "10^15 + 1 is evaluated after the displayed 1e+15 result",
                    " | ".join(actual),
                    comment="The scientific-notation result was accepted as the next expression's operand.",
                    evidence=screenshot,
                )
            else:
                self.add_result(
                    test_id, title, "FAIL", "Continue from 1e+15 without Error",
                    " | ".join(actual),
                    comment=(
                        f"Initial 10^15 display was {first!r}; adding +1 left an unchanged exponent result "
                        "or produced Error. This is consistent with exponent-formatted display text not "
                        "being accepted as a numeric literal by the expression validator/parser."
                    ),
                    evidence=screenshot,
                )
        except Exception as exc:
            screenshot = self.device.screenshot("evidence/tc-calc-009-error.png")
            hierarchy = self.device.save_hierarchy("evidence/tc-calc-009-error.xml")
            self.add_result(
                test_id, title, "ERROR", "Continue from 1e+15", "",
                comment=f"{type(exc).__name__}: {exc}; hierarchy={hierarchy}", evidence=screenshot,
            )

    def run_history(self) -> None:
        test_id = "TC-CALC-007"
        title = "History persists after activity restart and can restore an expression"
        try:
            self.device.close_history_if_open()
            self.device.ensure_basic_panel()
            self.device.tap_label("AC")
            self.device.press_sequence(["1", "+", "1"])
            typed = self.device.display_texts()
            if not self.device.expression_visible("1+1"):
                screenshot = self.device.screenshot("evidence/tc-calc-007-input-mismatch.png")
                self.add_result(
                    test_id, title, "ERROR", "Enter 1+1 = 2, then persist and restore it",
                    " | ".join(typed),
                    comment=(
                        "Input precondition failed before equals: visible expression was not 1+1, "
                        "so history durability was not evaluated. This is not a confirmed product defect."
                    ),
                    evidence=screenshot,
                )
                return
            self.device.key("=")
            # SharedPreferences.apply() updates memory immediately and flushes to
            # disk asynchronously. Allow the slow, software-rendered ATD enough
            # time to finish that write before deliberately killing the process.
            time.sleep(1.5)
            before_restart = self.device.display_texts()
            input_expression = self.device.normalize_expression("1+1")
            expression_still_visible = any(
                self.device.normalize_expression(value) == input_expression
                for value in before_restart
            )
            if not self.device.result_visible("2") or expression_still_visible:
                screenshot = self.device.screenshot("evidence/tc-calc-007-before-restart.png")
                self.add_result(
                    test_id, title, "ERROR", "Committed 1+1 = 2 before process restart",
                    " | ".join(before_restart),
                    comment=(
                        "Equals did not visibly commit the result: the input expression remained in "
                        "the editor (the '= 2' line may only be a live preview). History persistence "
                        "was not evaluated; check equals-key delivery before diagnosing history."
                    ),
                    evidence=screenshot,
                )
                return
            self.device.force_stop(self.package)
            self.device.navigate_to_calculator(self.package)
            time.sleep(0.75)
            self.device.tap_label("History")
            time.sleep(0.45)
            history_texts = self.device.labels()
            screenshot = self.device.screenshot("evidence/tc-calc-007-history.png")
            found = (
                any("1+1" in text.replace(" ", "") for text in history_texts)
                and self._history_result_visible(history_texts, "2")
            )
            if found:
                # Tap the stored expression to verify the history item restores a
                # usable expression, not just a static text row.
                self.device.tap_label("1+1")
                time.sleep(0.35)
                restored = self.device.display_texts()
                if self.device.expression_visible("1+1"):
                    self.add_result(
                        test_id, title, "PASS", "History shows 1+1 = 2 and restores the expression",
                        "history=" + " | ".join(history_texts) + "; restored=" + " | ".join(restored),
                        comment="The history entry survived process restart and restored its expression.",
                        evidence=screenshot,
                    )
                else:
                    self.add_result(
                        test_id, title, "FAIL", "History restores the 1+1 expression",
                        "history=" + " | ".join(history_texts) + "; restored=" + " | ".join(restored),
                        comment="The persisted 1+1 = 2 entry was visible but did not restore its expression.",
                        evidence=screenshot,
                    )
            else:
                self.add_result(
                    test_id, title, "FAIL", "History shows 1+1 = 2 after restart",
                    " | ".join(history_texts),
                    comment=(
                        "The expected entry was not found after restart. Before restart the display was "
                        f"{before_restart!r}; visible history labels were {history_texts!r}."
                    ),
                    evidence=screenshot,
                )
        except Exception as exc:
            screenshot = self.device.screenshot("evidence/tc-calc-007-error.png")
            hierarchy = self.device.save_hierarchy("evidence/tc-calc-007-error.xml")
            self.add_result(
                test_id, title, "ERROR", "Persisted and selectable 1+1 history entry", "",
                comment=f"{type(exc).__name__}: {exc}; hierarchy={hierarchy}", evidence=screenshot,
            )
        finally:
            # A history assertion failure must not strand later calculator tests
            # on the sheet where the keypad is hidden.
            try:
                self.device.close_history_if_open()
            except Exception as close_error:
                print(
                    f"::warning title=History cleanup::Could not close History sheet: "
                    f"{type(close_error).__name__}: {close_error}",
                    flush=True,
                )

    def check_google_reference(self) -> None:
        try:
            packages = self.device.adb(
                "shell", "pm", "list", "packages", timeout=60, check=False
            )
        except Exception as exc:
            self.reference.update({
                "status": "PACKAGE_SCAN_ERROR",
                "package": None,
                "note": f"Could not inspect emulator packages: {type(exc).__name__}: {exc}",
            })
            self.add_result(
                "TC-CALC-010", "Live comparison with official Google Calculator", "ERROR",
                "Check for com.google.android.calculator and compare live results",
                "Package scan raised an error",
                comment=self.reference["note"],
            )
            return

        installed = set(re.findall(r"package:([^\s]+)", packages))
        self.installed_packages = installed
        if not installed:
            self.reference.update({
                "status": "PACKAGE_SCAN_ERROR",
                "package": None,
                "note": f"Package scan returned no package records: {clean(packages)[:500]!r}",
            })
            self.add_result(
                "TC-CALC-010", "Live comparison with official Google Calculator", "ERROR",
                "Check for com.google.android.calculator and compare live results",
                clean(packages)[:500] or "No package records returned",
                comment=self.reference["note"],
            )
            return

        if GOOGLE_CALCULATOR_PACKAGE not in installed:
            self.reference.update({
                "status": "NOT_INSTALLED",
                "package": None,
                "note": (
                    "The official Google Calculator package was not present in the emulator image. "
                    "No third-party APK mirror was used. Functional assertions therefore use the "
                    "documented arithmetic expectations; this is not a live side-by-side Google comparison."
                ),
            })
            self.add_result(
                "TC-CALC-010", "Live comparison with official Google Calculator", "BLOCKED",
                "Same expressions run in com.google.android.calculator",
                "Official package not installed",
                comment=self.reference["note"],
            )
            return

        ref = AndroidUi(self.report_dir, "google-reference")
        try:
            ref.launch(GOOGLE_CALCULATOR_PACKAGE)
            ref.tap_first(("AC", "C"))
            ref.press_sequence(["2", "+", "3", "×", "4"])
            if not ref.expression_visible("2+3×4"):
                raise QaError(
                    f"Google reference input mismatch; display={ref.display_texts()!r}"
                )
            ref.key("=")
            time.sleep(0.4)
            actual = ref.display_texts()
            screenshot = ref.screenshot("evidence/tc-calc-010-google-reference.png")
            google_matches = ref.result_visible("14")
            target_case = next((row for row in self.results if row["id"] == "TC-CALC-001"), None)
            target_matches = bool(target_case and target_case["status"] == "PASS")
            passed = google_matches and target_matches
            self.reference.update({
                "status": "DIRECT_COMPARE_PASS" if passed else "DIRECT_COMPARE_MISMATCH",
                "package": GOOGLE_CALCULATOR_PACKAGE,
                "note": (
                    "Official package was installed; the same precedence case was run live in both apps. "
                    f"Google matched 14={google_matches}; MySpace matched 14={target_matches}."
                ),
            })
            self.add_result(
                "TC-CALC-010", "Live comparison with official Google Calculator",
                "PASS" if passed else "FAIL", "Both apps display 2 + 3 × 4 = 14",
                "Google: " + " | ".join(actual) + "; MySpace: "
                + (target_case["actual"] if target_case else "target result not captured"),
                comment=self.reference["note"], evidence=screenshot,
            )
        except Exception as exc:
            self.reference.update({
                "status": "INSTALLED_BUT_UNVERIFIED",
                "package": GOOGLE_CALCULATOR_PACKAGE,
                "note": f"Package exists, but UI comparison could not be completed: {type(exc).__name__}: {exc}",
            })
            self.add_result(
                "TC-CALC-010", "Live comparison with official Google Calculator", "ERROR",
                "2 + 3 × 4 = 14", "",
                comment=self.reference["note"],
            )

    def _capture_install_diagnostics(self, attempt: int, error: Exception) -> Path:
        lines = [f"APK install attempt {attempt} failed: {type(error).__name__}: {error}"]
        probes = (
            ("adb get-state", ("get-state",), 15),
            ("boot completed", ("shell", "getprop", "sys.boot_completed"), 15),
            ("PackageManager package list", ("shell", "cmd", "package", "list", "packages"), 15),
            ("recent logcat", ("logcat", "-d", "-t", "1000"), 45),
        )
        for title, args, timeout in probes:
            lines.append(f"\n--- {title} ---")
            try:
                lines.append(self.device.adb(*args, timeout=timeout, check=False))
            except Exception as probe_error:
                lines.append(f"Diagnostic command failed: {type(probe_error).__name__}: {probe_error}")
        path = self.report_dir / f"apk-install-attempt-{attempt}-diagnostics.txt"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def _install_apk(self) -> None:
        last_error: Exception | None = None
        for attempt in range(1, 3):
            try:
                self.device.adb(
                    "install", "--no-streaming", "-r", str(self.apk), timeout=600
                )
                print("::notice title=APK installation::The exact calculator APK installed successfully.", flush=True)
                return
            except Exception as error:
                last_error = error
                diagnostic_path = self._capture_install_diagnostics(attempt, error)
                print(
                    f"::warning title=APK installation attempt {attempt}::Install failed; "
                    f"emulator diagnostics saved to {diagnostic_path}.",
                    flush=True,
                )
                if attempt == 2:
                    break

                # ADB can lose the PackageManager binder while the emulator is
                # under load. Confirm that it responds again before one retry.
                for probe in range(1, 13):
                    try:
                        packages = self.device.adb(
                            "shell", "cmd", "package", "list", "packages",
                            timeout=15, check=False,
                        )
                    except Exception:
                        packages = ""
                    if any(line.startswith("package:") for line in packages.splitlines()):
                        print(
                            f"::notice title=Android package manager recovered::"
                            f"PackageManager responded before install retry {probe}.",
                            flush=True,
                        )
                        break
                    time.sleep(5)
                time.sleep(5)

        raise QaError(f"APK installation failed after two attempts: {last_error}") from last_error

    def run(self) -> int:
        if not self.apk.is_file():
            raise QaError(f"APK not found: {self.apk}")
        digest = hashlib.sha256(self.apk.read_bytes()).hexdigest()
        expected_digest = EXPECTED_APK_SHA256_BY_PACKAGE.get(self.package)
        if expected_digest is None:
            raise QaError(f"No pinned APK hash is configured for package {self.package}")
        if digest != expected_digest:
            raise QaError(f"APK SHA-256 mismatch for {self.package}: expected {expected_digest}, got {digest}")

        self._install_apk()
        # Let Android finish post-install package bookkeeping before app launch; this
        # software-emulator runner has surfaced a system ANR immediately after install.
        time.sleep(15.0)
        self.device.adb("shell", "pm", "clear", self.package, timeout=30, check=False)
        self.device.navigate_to_calculator(self.package)
        self.device.screenshot("evidence/initial-calculator-screen.png")

        selected = self.case_plan()
        if "TC-CALC-001" in selected:
            self.run_case(
                "TC-CALC-001", "Operator precedence", ["2", "+", "3", "×", "4"], "14"
            )
        if "TC-CALC-002" in selected:
            self.run_case(
                "TC-CALC-002", "Parentheses override precedence",
                ["(", "2", "+", "3", ")", "×", "4"], "20"
            )
        if "TC-CALC-003" in selected:
            self.run_case(
                "TC-CALC-003", "Decimal addition", ["0", ".", "1", "+", "0", ".", "2"], "0.3"
            )
        if "TC-CALC-004" in selected:
            self.run_case(
                "TC-CALC-004", "Contextual percentage", ["2", "0", "0", "+", "1", "0", "%"], "220"
            )
        if "TC-CALC-005" in selected:
            self.run_case(
                "TC-CALC-005", "Square root in scientific panel", ["√(", "9", ")"], "3", scientific=True
            )
        if "TC-CALC-006" in selected:
            self.run_case(
                "TC-CALC-006", "Sine in degree mode", ["sin(", "3", "0", ")"], "0.5", scientific=True
            )
        if "TC-CALC-007" in selected:
            self.run_history()
        if "TC-CALC-008" in selected:
            self.run_chained_precision()
        if "TC-CALC-009" in selected:
            self.run_exponent_chain()
        if "TC-CALC-010" in selected:
            self.check_google_reference()

        aosp_present = "com.android.calculator2" in self.installed_packages
        if self.reference["status"] == "NOT_INSTALLED" and aosp_present:
            self.reference["note"] += (
                " The emulator did include com.android.calculator2, but that is an AOSP/system "
                "calculator and is not reported as the official Google Calculator."
            )

        status_counts: dict[str, int] = {}
        for result in self.results:
            status_counts[result["status"]] = status_counts.get(result["status"], 0) + 1
        apk_size = self.apk.stat().st_size
        app_label = "MySpace" if self.package == DEFAULT_PACKAGE else "Standalone MyCalc"
        report = {
            "report_title": f"{app_label} Calculator APK E2E QA Run",
            "created_utc": utc_now(),
            "artifact": {
                "file": self.apk.name,
                "package": self.package,
                "size_bytes": apk_size,
                "sha256": digest,
            },
            "device": {
                "emulator_api": int(os.environ.get("ANDROID_API", "34")),
                "screen": f"{self.device._width}x{self.device._height}",
                "ui_inspection_method": self.device.ui_method,
                "scope": "Calculator feature only",
            },
            "google_reference": self.reference,
            "selected_test_ids": sorted(self.case_plan()),
            "summary": status_counts,
            "results": self.results,
        }
        json_path = self.report_dir / "calculator-e2e-results.json"
        json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        md_path = self.report_dir / "calculator-e2e-results.md"
        self._write_markdown(md_path, report)
        self._write_step_summary(report)

        failures = [r for r in self.results if r["status"] in ("FAIL", "ERROR")]
        summary_notice = ", ".join(
            f"{status}={count}" for status, count in sorted(status_counts.items())
        ) or "no test results"
        case_summary = ", ".join(
            f"{result['id']}={result['status']}" for result in self.results
        ) or "no case results"
        summary_notice = clean(
            f"{summary_notice}; Google reference={self.reference['status']}; "
            f"cases: {case_summary}"
        ).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(
            f"::notice title={self.package} calculator QA summary::{summary_notice}",
            flush=True,
        )
        for result in failures:
            message = clean(result["comment"]).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            print(f"::error title={result['id']}::{message}", flush=True)
        print(f"Machine-readable result: {json_path}", flush=True)
        print(f"Human-readable result: {md_path}", flush=True)
        return 1 if failures else 0

    def _write_markdown(self, path: Path, report: dict[str, Any]) -> None:
        summary = report["summary"]
        lines = [
            f"# {report['report_title']}",
            "",
            f"- **Generated (UTC):** {report['created_utc']}",
            f"- **APK:** `{report['artifact']['file']}` ({report['artifact']['size_bytes']:,} bytes)",
            f"- **Package:** `{report['artifact']['package']}`",
            f"- **SHA-256:** `{report['artifact']['sha256']}`",
            f"- **Device:** Android API {report['device']['emulator_api']} emulator, {report['device']['screen']}",
            f"- **UI inspection:** {report['device']['ui_inspection_method']}",
            "- **Scope:** Calculator feature only",
            f"- **Google reference:** {self.reference['status']} — {self.reference['note']}",
            "",
            "## Result summary",
            "",
            "| Status | Count |",
            "|---|---:|",
        ]
        for status in ("PASS", "FAIL", "ERROR", "BLOCKED"):
            lines.append(f"| {status} | {summary.get(status, 0)} |")
        lines.extend(["", "## Test cases", "", "| ID | Test | Status | Expected | Actual / comment |", "|---|---|---|---|---|"])
        for row in report["results"]:
            comment = row["comment"] or row["actual"]
            for source, target in (("|", "\\|"), ("\n", "<br>")):
                comment = comment.replace(source, target)
            lines.append(
                f"| {row['id']} | {row['title']} | **{row['status']}** | "
                f"{row['expected']} | {comment}"
            )
        lines.extend([
            "",
            "Screenshots and UI hierarchy or OCR evidence are in the adjacent `evidence/` folder.",
            "A BLOCKED Google comparison is not treated as a calculator functional pass.",
            "",
        ])
        path.write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _write_step_summary(report: dict[str, Any]) -> None:
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if not summary_path:
            return
        summary = report["summary"]
        lines = [
            f"# {report['report_title']}",
            "",
            f"APK SHA-256: `{report['artifact']['sha256']}`  ",
            f"Google reference: **{report['google_reference']['status']}** — {report['google_reference']['note']}",
            "",
            "| ID | Test | Status | Notes |",
            "|---|---|---|---|",
        ]
        for row in report["results"]:
            note = (row["comment"] or row["actual"]).replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {row['id']} | {row['title']} | **{row['status']}** | {note} |")
        lines.extend(["", f"Counts: {summary}", ""])
        with open(summary_path, "a", encoding="utf-8") as stream:
            stream.write("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--package", default=DEFAULT_PACKAGE)
    parser.add_argument("--report-dir", type=Path, default=Path("reports/e2e"))
    parser.add_argument(
        "--cases",
        help="Comma-separated TC-CALC-001..010 IDs; omit to run the full calculator suite",
    )
    args = parser.parse_args()
    try:
        case_ids = None
        if args.cases is not None:
            case_ids = {item.strip().upper() for item in args.cases.split(",") if item.strip()}
        qa = CalculatorQa(args.apk, args.package, args.report_dir, case_ids=case_ids)
        return qa.run()
    except Exception as exc:
        print(f"::error title=Calculator E2E setup::{type(exc).__name__}: {exc}", flush=True)
        print(f"E2E setup failed: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
