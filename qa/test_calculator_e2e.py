"""Unit checks for the calculator UI harness; these do not need an emulator."""
from __future__ import annotations

import io
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from unittest.mock import patch

from calculator_e2e import (
    AndroidUi,
    CALCULATOR_TEST_IDS,
    DEFAULT_PACKAGE,
    EXPECTED_APK_SHA256_BY_PACKAGE,
    STANDALONE_PACKAGE,
    CalculatorQa,
    QaError,
)


class AndroidUiHarnessTests(unittest.TestCase):
    def test_scientific_notation_parser_error_is_a_product_failure(self) -> None:
        class ErrorDevice:
            normalize_expression = staticmethod(AndroidUi.normalize_expression)

            def __init__(self) -> None:
                self.display_calls = 0

            def close_history_if_open(self) -> None:
                pass

            def ensure_scientific_panel(self) -> None:
                pass

            def tap_label(self, label: str) -> None:
                pass

            def press_sequence(self, keys: list[str]) -> None:
                pass

            def expression_visible(self, expected: str) -> bool:
                return expected == "10^15"

            def key(self, key: str) -> None:
                pass

            def display_texts(self) -> list[str]:
                self.display_calls += 1
                if self.display_calls == 1:
                    return ["1e+15"]
                return ["1e+15+1", "Error"]

            def expression_suffix_visible(self, suffix: str) -> bool:
                return suffix == "+1"

            def screenshot(self, name: str) -> str:
                return name

        qa = object.__new__(CalculatorQa)
        qa.device = ErrorDevice()
        qa.results = []
        with redirect_stdout(io.StringIO()), patch("calculator_e2e.time.sleep", return_value=None):
            qa.run_exponent_chain()

        self.assertEqual(qa.results[0]["status"], "FAIL")
        self.assertIn("Error", qa.results[0]["actual"])

    def test_exact_myspace_and_standalone_apk_hashes_are_pinned(self) -> None:
        self.assertEqual(
            EXPECTED_APK_SHA256_BY_PACKAGE[DEFAULT_PACKAGE],
            "629442fc1d54508690f8c75664ea8be7611fef14a74f4edcf6f2bd1cab40068d",
        )
        self.assertEqual(
            EXPECTED_APK_SHA256_BY_PACKAGE[STANDALONE_PACKAGE],
            "342f51bdbb12539f44971fc945d427714ac8cf74bf01a7fa8fccf02660e1f3fa",
        )

    def test_zero_key_tap_ignores_the_editable_display_copy(self) -> None:
        root = ET.fromstring(
            '<hierarchy>'
            '<node text="0" bounds="[15,100][45,140]" clickable="true" '
            'visible-to-user="true" class="android.widget.EditText" />'
            '<node text="0" bounds="[15,400][45,440]" clickable="true" '
            'visible-to-user="true" class="android.widget.EditText" />'
            '<node text="0" bounds="[15,700][45,740]" clickable="true" '
            'visible-to-user="true" class="android.widget.TextView" />'
            '</hierarchy>'
        )
        ui = object.__new__(AndroidUi)
        ui._last_tree = root
        ui._ocr_mode = False
        ui._height = 854
        ui._width = 480
        ui.label = "target"
        tapped: list[tuple[str, ...]] = []
        ui.adb = lambda *args, **kwargs: tapped.append(args) or ""

        with patch("calculator_e2e.time.sleep", return_value=None):
            ui.tap_label("0")

        self.assertEqual(tapped, [("shell", "input", "tap", "30", "720")])

    def test_zero_key_waits_for_the_typed_expression_to_change(self) -> None:
        ui = object.__new__(AndroidUi)
        ui.tap_label = lambda label, **kwargs: ["CALCULATOR", "sin(3)"]
        ui.display_texts = lambda: ["CALCULATOR", "sin(30)"]

        ui.key("0")
        self.assertEqual(ui.display_texts()[-1], "sin(30)")

    def test_dump_retries_standard_hierarchy_when_compressed_file_is_empty(self) -> None:
        ui = object.__new__(AndroidUi)
        ui._last_tree = None
        ui._ocr_mode = False
        ui.ui_method = "uiautomator-compressed"
        calls: list[tuple[str, ...]] = []
        valid_xml = '<hierarchy><node text="Calculator" bounds="[0,0][200,80]" /></hierarchy>'

        def adb(*args: str, **kwargs: object) -> str:
            calls.append(args)
            if args[:3] == ("exec-out", "cat", "/sdcard/window-compressed.xml"):
                return ""
            if args[:3] == ("exec-out", "cat", "/sdcard/window-standard.xml"):
                return valid_xml
            return "UI hierarchy dumped"

        ui.adb = adb
        with patch("calculator_e2e.time.sleep", return_value=None), redirect_stdout(io.StringIO()):
            tree = ui.dump()

        self.assertEqual(tree.tag, "hierarchy")
        self.assertEqual(ui.ui_method, "uiautomator-standard")
        self.assertIn(("shell", "uiautomator", "dump", "/sdcard/window-standard.xml"), calls)

    def test_system_anr_recovery_reboots_and_waits_for_installed_package(self) -> None:
        ui = object.__new__(AndroidUi)
        ui._last_tree = ET.Element("stale-hierarchy")
        ui._ocr_mode = True
        ui._scientific_open = True
        ui.ui_method = "screenshot-ocr-fallback"
        calls: list[tuple[str, ...]] = []

        def adb(*args: str, **kwargs: object) -> str:
            calls.append(args)
            if args == ("shell", "getprop", "sys.boot_completed"):
                return "1\n"
            if args == ("shell", "cmd", "package", "list", "packages"):
                return "package:app.space.one\n"
            return ""

        ui.adb = adb
        with patch("calculator_e2e.time.sleep", return_value=None), redirect_stdout(io.StringIO()):
            ui._reboot_after_system_anr("app.space.one")

        self.assertIn(("reboot",), calls)
        self.assertIn(("wait-for-device",), calls)
        self.assertIsNone(ui._last_tree)
        self.assertFalse(ui._ocr_mode)
        self.assertFalse(ui._scientific_open)
        self.assertIn(("shell", "cmd", "package", "list", "packages"), calls)

    def test_navigation_reboots_once_after_three_unresolved_system_anr_waits(self) -> None:
        class FakeDevice:
            navigate_to_calculator = AndroidUi.navigate_to_calculator
            _is_anr_dialog = staticmethod(AndroidUi._is_anr_dialog)

            def __init__(self) -> None:
                self.rebooted = False
                self.launches = 0
                self.wait_taps = 0

            def launch(self, package: str) -> None:
                self.launches += 1

            def is_calculator_screen(self) -> bool:
                return self.rebooted and self.launches == 2

            def labels(self) -> list[str]:
                return ["Process system isn't responding", "Wait", "Close app"]

            def tap_label(self, label: str, **kwargs: object) -> None:
                self.wait_taps += 1

            def _reboot_after_system_anr(self, package: str) -> None:
                self.rebooted = True

        device = FakeDevice()
        with patch("calculator_e2e.time.sleep", return_value=None):
            device.navigate_to_calculator("app.space.one")

        self.assertTrue(device.rebooted)
        self.assertEqual(device.wait_taps, 3)
        self.assertEqual(device.launches, 2)

    def test_case_plan_is_sharded_and_google_job_runs_target_baseline(self) -> None:
        qa = object.__new__(CalculatorQa)
        qa.case_ids = {"TC-CALC-010"}
        self.assertEqual(qa.case_plan(), {"TC-CALC-001", "TC-CALC-010"})

        qa.case_ids = {"TC-CALC-008"}
        self.assertEqual(qa.case_plan(), {"TC-CALC-008"})

        qa.case_ids = None
        self.assertEqual(qa.case_plan(), set(CALCULATOR_TEST_IDS))

    def test_history_result_matcher_accepts_equals_prefix_and_zero_padding(self) -> None:
        self.assertTrue(CalculatorQa._history_result_visible(["= 2"], "2"))
        self.assertTrue(CalculatorQa._history_result_visible(["2"], "2"))
        self.assertTrue(CalculatorQa._history_result_visible(["= 2.00"], "2"))
        self.assertFalse(CalculatorQa._history_result_visible(["= 2.1"], "2"))
        self.assertFalse(CalculatorQa._history_result_visible(["= 12"], "2"))

    def test_expression_matching_ignores_spacing_but_not_missing_digits(self) -> None:
        root = ET.fromstring(
            '<hierarchy><node text="0.1 + 0.2" bounds="[20,100][300,150]" '
            'clickable="false" visible-to-user="true" '
            'class="android.widget.EditText" /></hierarchy>'
        )
        ui = object.__new__(AndroidUi)
        ui._last_tree = root
        ui._ocr_mode = False
        ui._height = 854
        ui._width = 480
        ui.display_texts = lambda: ["0.1 + 0.2"]

        self.assertTrue(ui.expression_visible("0.1+0.2"))
        self.assertFalse(ui.expression_visible(".1+0.2"))

    def test_google_package_scan_error_is_reported_without_aborting(self) -> None:
        class BrokenAdb:
            def adb(self, *args: str, **kwargs: object) -> str:
                raise TimeoutError("package scan timeout")

        qa = object.__new__(CalculatorQa)
        qa.device = BrokenAdb()
        qa.reference = {
            "requested": "Google Calculator (com.google.android.calculator)",
            "status": "NOT_CHECKED",
            "package": None,
            "note": "",
        }
        qa.installed_packages = set()
        qa.results = []

        with redirect_stdout(io.StringIO()):
            qa.check_google_reference()

        self.assertEqual(qa.reference["status"], "PACKAGE_SCAN_ERROR")
        self.assertEqual(qa.results[0]["id"], "TC-CALC-010")
        self.assertEqual(qa.results[0]["status"], "ERROR")

    def test_history_failure_closes_the_sheet_before_next_case(self) -> None:
        class FakeDevice:
            close_history_if_open = AndroidUi.close_history_if_open
            normalize_expression = staticmethod(AndroidUi.normalize_expression)

            def __init__(self) -> None:
                self.history_open = False
                self.taps: list[str] = []

            def labels(self) -> list[str]:
                if self.history_open:
                    return ["History", "Close history", "older calculation", "2"]
                return ["Calculator", "AC"]

            def tap_label(self, label: str, **kwargs: object) -> None:
                self.taps.append(label)
                if label == "History":
                    self.history_open = True
                elif label == "Close history":
                    self.history_open = False

            def ensure_basic_panel(self) -> None:
                pass

            def press_sequence(self, keys: list[str]) -> None:
                pass

            def display_texts(self) -> list[str]:
                return ["2"]

            def expression_visible(self, expected: str) -> bool:
                return expected == "1+1"

            def key(self, key: str) -> None:
                pass

            def result_visible(self, expected: str) -> bool:
                return expected == "2"

            def force_stop(self, package: str) -> None:
                pass

            def navigate_to_calculator(self, package: str) -> None:
                pass

            def screenshot(self, filename: str) -> str:
                return filename

        device = FakeDevice()
        qa = object.__new__(CalculatorQa)
        qa.device = device
        qa.package = "app.space.one"
        qa.results = []

        with patch("calculator_e2e.time.sleep", return_value=None), redirect_stdout(io.StringIO()):
            qa.run_history()

        self.assertEqual(qa.results[0]["status"], "FAIL")
        self.assertIn("Close history", device.taps)
        self.assertFalse(device.history_open)


if __name__ == "__main__":
    unittest.main()
