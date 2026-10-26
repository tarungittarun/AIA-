"""Unit checks for the calculator UI harness; these do not need an emulator."""
from __future__ import annotations

import io
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from unittest.mock import patch

from calculator_e2e import AndroidUi, CalculatorQa


class AndroidUiHarnessTests(unittest.TestCase):
    def test_zero_key_tap_ignores_the_editable_display_copy(self) -> None:
        root = ET.fromstring(
            '<hierarchy>'
            '<node text="0" bounds="[15,100][45,140]" clickable="true" '
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

    def test_history_failure_closes_the_sheet_before_next_case(self) -> None:
        class FakeDevice:
            close_history_if_open = AndroidUi.close_history_if_open

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
