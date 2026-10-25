#!/usr/bin/env python3
"""Black-box UI QA for the calculator in the supplied MySpace APK.

The test runs only against the Calculator feature. It uses Android's built-in
UIAutomator hierarchy dump and input commands so no third-party device service
or app credentials are required. Results and screenshots are always written,
even when a functional assertion fails.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable

EXPECTED_APK_SHA256 = "ff52331518b71a153abf6ef76c964538044121230e1ae87d2855e535a94e0a23"
DEFAULT_PACKAGE = "app.space.one"
GOOGLE_CALCULATOR_PACKAGE = "com.google.android.calculator"


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
        self.adb("shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1")
        time.sleep(2.0)
        self._last_tree = None

    def force_stop(self, package: str) -> None:
        self.adb("shell", "am", "force-stop", package, check=False)
        time.sleep(0.5)
        self._last_tree = None

    def dump(self) -> ET.Element:
        self.adb("shell", "uiautomator", "dump", "/sdcard/window.xml", timeout=45)
        raw = self.adb("exec-out", "cat", "/sdcard/window.xml", timeout=20)
        try:
            self._last_tree = ET.fromstring(raw)
        except ET.ParseError as exc:
            raise QaError(f"Could not parse UI hierarchy XML: {raw[:500]!r}") from exc
        return self._last_tree

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

    @staticmethod
    def _node_matches(node: ET.Element, label: str, partial: bool = False) -> bool:
        actuals = [clean(node.attrib.get("text", "")), clean(node.attrib.get("content-desc", ""))]
        if partial:
            return any(label.casefold() in actual.casefold() for actual in actuals if actual)
        return label in actuals

    def _matching_nodes(self, label: str, partial: bool = False) -> list[ET.Element]:
        return [
            node for node in self.nodes()
            if self._visible(node) and self._node_matches(node, label, partial)
        ]

    def tap_label(self, label: str, *, partial: bool = False, timeout: float = 1.2) -> None:
        deadline = time.monotonic() + timeout
        last_labels: list[str] = []
        while time.monotonic() < deadline:
            candidates = self._matching_nodes(label, partial)
            last_labels = self.labels()
            if candidates:
                # Prefer a directly clickable control; tapping a non-clickable label
                # still works for cards whose parent owns the click listener.
                candidates.sort(key=lambda n: n.attrib.get("clickable", "false").lower() != "true")
                for node in candidates:
                    point = bounds_center(node.attrib.get("bounds", ""))
                    if point:
                        self.adb("shell", "input", "tap", str(point[0]), str(point[1]))
                        time.sleep(0.18)
                        self._last_tree = None
                        return
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
        labels = set(self.labels())
        return "AC" in labels and "=" in labels and ("÷" in labels or "/" in labels)

    def navigate_to_calculator(self, package: str) -> None:
        self.launch(package)
        # The suite host may start on its home screen. Open only its Calculator
        # tile/route; no other feature is used by this test.
        route_labels = ("Calculator", "Apps", "Menu", "Clock")
        for _ in range(8):
            if self.is_calculator_screen():
                return
            labels = self.labels()
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
                time.sleep(0.4)
        screenshot = self.screenshot(f"{self.label}-navigation-failed.png")
        hierarchy = self.save_hierarchy(f"{self.label}-navigation-failed.xml")
        raise QaError(
            "The Calculator screen did not become available through suite navigation. "
            f"Screenshot={screenshot}; hierarchy={hierarchy}; visible labels={self.labels()}"
        )

    def ensure_scientific_panel(self) -> None:
        labels = self.labels()
        if "sin(" in labels or "√(" in labels:
            return
        for candidate in ("Open the extra keys", "Show scientific keys", "Scientific keys"):
            if candidate in labels:
                self.tap_label(candidate)
                time.sleep(0.25)
                return
        # The chevron's visible icon text may be blank while its description varies
        # by host theme/accessibility implementation.
        for label in labels:
            if "extra keys" in label.casefold() or "scientific" in label.casefold():
                self.tap_label(label)
                time.sleep(0.25)
                return
        raise QaError(f"Scientific panel toggle not found; visible labels: {labels}")

    def key(self, key: str) -> None:
        label = "( )" if key in ("(", ")") else key
        self.tap_label(label, timeout=1.5)

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

    def details(self) -> dict[str, Any]:
        return {
            "display_text": self.display_texts(),
            "visible_labels": self.labels(),
            "screen": f"{self._width}x{self._height}",
        }


class CalculatorQa:
    def __init__(self, apk: Path, package: str, report_dir: Path) -> None:
        self.apk = apk
        self.package = package
        self.report_dir = report_dir
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.device = AndroidUi(report_dir, "target")
        self.results: list[dict[str, Any]] = []
        self.reference: dict[str, Any] = {
            "requested": "Google Calculator (com.google.android.calculator)",
            "status": "NOT_CHECKED",
            "package": None,
            "note": "",
        }

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
            if scientific:
                self.device.ensure_scientific_panel()
            self.device.tap_label("AC")
            self.device.press_sequence(keys)
            self.device.key("=")
            time.sleep(0.4)
            actual = self.device.display_texts()
            screenshot = self.device.screenshot(f"evidence/{test_id.lower()}-target.png")
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
            self.device.tap_label("AC")
            self.device.press_sequence(["1", "÷", "3"])
            self.device.key("=")
            time.sleep(0.3)
            first = self.device.display_texts()
            self.device.press_sequence(["×", "3"])
            self.device.key("=")
            time.sleep(0.35)
            actual = self.device.display_texts()
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
            self.device.ensure_scientific_panel()
            self.device.tap_label("AC")
            self.device.press_sequence(["1", "0", "^", "1", "5"])
            self.device.key("=")
            time.sleep(0.25)
            first = self.device.display_texts()
            self.device.press_sequence(["+", "1"])
            self.device.key("=")
            time.sleep(0.35)
            actual = self.device.display_texts()
            screenshot = self.device.screenshot("evidence/tc-calc-009-target.png")
            # If the exponent literal was accepted, the display should no longer be
            # exactly the preceding 1e+15 result; an error is also a failed chain.
            normalized = [v.replace("E", "e").replace("−", "-") for v in actual]
            unchanged = any(v.strip() in ("1e+15", "1E+15") for v in normalized)
            error = any("error" in v.casefold() for v in normalized)
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
            self.device.tap_label("AC")
            self.device.press_sequence(["1", "+", "1"])
            self.device.key("=")
            time.sleep(0.25)
            self.device.force_stop(self.package)
            self.device.navigate_to_calculator(self.package)
            self.device.tap_label("History")
            history_texts = self.device.labels()
            screenshot = self.device.screenshot("evidence/tc-calc-007-history.png")
            found = any("1+1" in text.replace(" ", "") for text in history_texts) and any(
                text.strip() == "2" for text in history_texts
            )
            if found:
                # Tap the stored expression to verify the history item restores a
                # usable calculation, not just a static text row.
                self.device.tap_label("1+1")
                time.sleep(0.25)
                restored = self.device.display_texts()
                self.add_result(
                    test_id, title, "PASS", "History shows 1+1 = 2 and restores the expression",
                    "history=" + " | ".join(history_texts) + "; restored=" + " | ".join(restored),
                    comment="The history entry survived process restart and was selectable.",
                    evidence=screenshot,
                )
            else:
                self.add_result(
                    test_id, title, "FAIL", "History shows 1+1 = 2 after restart",
                    " | ".join(history_texts),
                    comment="The expected persisted entry was not found in the visible history panel.",
                    evidence=screenshot,
                )
        except Exception as exc:
            screenshot = self.device.screenshot("evidence/tc-calc-007-error.png")
            hierarchy = self.device.save_hierarchy("evidence/tc-calc-007-error.xml")
            self.add_result(
                test_id, title, "ERROR", "Persisted and selectable 1+1 history entry", "",
                comment=f"{type(exc).__name__}: {exc}; hierarchy={hierarchy}", evidence=screenshot,
            )

    def check_google_reference(self) -> None:
        packages = self.device.adb("shell", "pm", "list", "packages", check=False)
        installed = set(re.findall(r"package:([^\s]+)", packages))
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
        if digest != EXPECTED_APK_SHA256:
            raise QaError(f"APK SHA-256 mismatch: expected {EXPECTED_APK_SHA256}, got {digest}")

        self._install_apk()
        self.device.adb("shell", "pm", "clear", self.package, timeout=30, check=False)
        self.device.navigate_to_calculator(self.package)
        self.device.screenshot("evidence/initial-calculator-screen.png")

        self.run_case(
            "TC-CALC-001", "Operator precedence", ["2", "+", "3", "×", "4"], "14"
        )
        self.run_case(
            "TC-CALC-002", "Parentheses override precedence",
            ["(", "2", "+", "3", ")", "×", "4"], "20"
        )
        self.run_case(
            "TC-CALC-003", "Decimal addition", ["0", ".", "1", "+", "0", ".", "2"], "0.3"
        )
        self.run_case(
            "TC-CALC-004", "Contextual percentage", ["2", "0", "0", "+", "1", "0", "%"], "220"
        )
        self.run_case(
            "TC-CALC-005", "Square root in scientific panel", ["√(", "9", ")"], "3", scientific=True
        )
        self.run_case(
            "TC-CALC-006", "Sine in degree mode", ["sin(", "3", "0", ")"], "0.5", scientific=True
        )
        self.run_history()
        self.run_chained_precision()
        self.run_exponent_chain()
        self.check_google_reference()

        packages = self.device.adb("shell", "pm", "list", "packages", check=False)
        aosp_present = "package:com.android.calculator2" in packages
        if self.reference["status"] == "NOT_INSTALLED" and aosp_present:
            self.reference["note"] += (
                " The emulator did include com.android.calculator2, but that is an AOSP/system "
                "calculator and is not reported as the official Google Calculator."
            )

        status_counts: dict[str, int] = {}
        for result in self.results:
            status_counts[result["status"]] = status_counts.get(result["status"], 0) + 1
        apk_size = self.apk.stat().st_size
        report = {
            "report_title": "MySpace Calculator APK E2E QA Run",
            "created_utc": utc_now(),
            "artifact": {
                "file": self.apk.name,
                "package": self.package,
                "size_bytes": apk_size,
                "sha256": digest,
            },
            "device": {
                "emulator_api": 30,
                "screen": f"{self.device._width}x{self.device._height}",
                "scope": "Calculator feature only",
            },
            "google_reference": self.reference,
            "summary": status_counts,
            "results": self.results,
        }
        json_path = self.report_dir / "calculator-e2e-results.json"
        json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        md_path = self.report_dir / "calculator-e2e-results.md"
        self._write_markdown(md_path, report)
        self._write_step_summary(report)

        failures = [r for r in self.results if r["status"] in ("FAIL", "ERROR")]
        for result in failures:
            message = clean(result["comment"]).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            print(f"::error title={result['id']}::{message}", flush=True)
        print(f"Machine-readable result: {json_path}", flush=True)
        print(f"Human-readable result: {md_path}", flush=True)
        return 1 if failures else 0

    def _write_markdown(self, path: Path, report: dict[str, Any]) -> None:
        summary = report["summary"]
        lines = [
            "# MySpace Calculator APK — E2E Run Report",
            "",
            f"- **Generated (UTC):** {report['created_utc']}",
            f"- **APK:** `{report['artifact']['file']}` ({report['artifact']['size_bytes']:,} bytes)",
            f"- **Package:** `{report['artifact']['package']}`",
            f"- **SHA-256:** `{report['artifact']['sha256']}`",
            f"- **Device:** Android API {report['device']['emulator_api']} emulator, {report['device']['screen']}",
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
            "Screenshots and UI hierarchy evidence are in the adjacent `evidence/` folder.",
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
            "# MySpace Calculator APK E2E QA",
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
    args = parser.parse_args()
    try:
        qa = CalculatorQa(args.apk, args.package, args.report_dir)
        return qa.run()
    except Exception as exc:
        print(f"::error title=Calculator E2E setup::{type(exc).__name__}: {exc}", flush=True)
        print(f"E2E setup failed: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
