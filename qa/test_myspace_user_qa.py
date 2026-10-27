import unittest

from myspace_user_qa import (
    CALCULATOR_CASES,
    DEFAULT_PACKAGE,
    EXPECTED_VERSION,
    PINNED_APK_SHA256,
    PINNED_GUIDE_SHA256,
    PINNED_SOURCE_COMMIT,
    STANDALONE_PACKAGE,
    UserQa,
    case_insensitive_match,
    compact,
)


class UserQaContractTests(unittest.TestCase):
    def test_release_hashes_and_version_codes_are_pinned(self):
        self.assertEqual(
            PINNED_APK_SHA256[DEFAULT_PACKAGE],
            "7ae98fd05c25554c3b90c32fbc2aeda789c25d0551fab81d071e804106a2a2ad",
        )
        self.assertEqual(
            PINNED_APK_SHA256[STANDALONE_PACKAGE],
            "09b1dc8f91ac249643cb92aa74670fdd2db8430af6c0b8c7052d8e906efcf1d4",
        )
        self.assertEqual(PINNED_GUIDE_SHA256,
                         "a3d0b131c7beb99f8bc12712eebf8c01e5a8873de7996a23f943905768578fc4")
        self.assertEqual(PINNED_SOURCE_COMMIT, "a09e52f2c3f141bfc2d3a95f667a38fcac08b54a")
        self.assertEqual(EXPECTED_VERSION[DEFAULT_PACKAGE], ("3.12.39", 76))
        self.assertEqual(EXPECTED_VERSION[STANDALONE_PACKAGE], ("1.0.37", 38))

    def test_core_case_set_covers_all_myspace_calculator_ids(self):
        self.assertEqual(CALCULATOR_CASES[DEFAULT_PACKAGE],
                         {f"TC-CALC-{number:03d}" for number in range(1, 12)})

    def test_standalone_case_set_includes_permission_audit_but_not_google_comparison(self):
        self.assertEqual(
            CALCULATOR_CASES[STANDALONE_PACKAGE],
            {*(f"TC-CALC-{number:03d}" for number in range(1, 10)),
             "TC-CALC-011", "TC-CALC-012"},
        )
        self.assertNotIn("TC-CALC-010", CALCULATOR_CASES[STANDALONE_PACKAGE])

    def test_display_normalization_ignores_grouping_spaces_and_minus_glyph(self):
        self.assertEqual(compact("1,23,456 + 1"), "123456+1")
        self.assertEqual(compact("− 0.5"), "-0.5")

    def test_label_match_is_case_insensitive_and_accepts_a_substring(self):
        self.assertEqual(case_insensitive_match(["New note", "Calendar"], ["Note"]), "New note")
        self.assertIsNone(case_insensitive_match(["Settings"], ["Scanner"]))

    def test_floating_toolbar_ocr_matches_split_memory_action_and_returns_bounds(self):
        words = [
            {"text": "M", "left": 20, "top": 100, "width": 9, "height": 12, "line": (1, 1, 1)},
            {"text": "Add", "left": 30, "top": 100, "width": 23, "height": 12, "line": (1, 1, 1)},
            {"text": "Copy", "left": 70, "top": 100, "width": 28, "height": 12, "line": (1, 1, 1)},
        ]
        self.assertTrue(UserQa._ocr_has(words, "MAdd"))
        self.assertEqual(UserQa._ocr_group(words, "MAdd"), (20, 100, 53, 112))
        self.assertTrue(UserQa._ocr_has(words, "Copy"))

    def test_ocr_groups_expression_tokens_for_precision_taps(self):
        words = [
            {"text": "3", "left": 170, "top": 150, "width": 24, "height": 44, "line": (1, 1, 1)},
            {"text": "+", "left": 200, "top": 160, "width": 20, "height": 30, "line": (1, 1, 1)},
            {"text": "4", "left": 225, "top": 150, "width": 25, "height": 44, "line": (1, 1, 1)},
        ]
        self.assertEqual(UserQa._ocr_group(words, "3+4"), (170, 150, 250, 194))

    def test_ocr_never_joins_toolbar_words_across_lines(self):
        words = [
            {"text": "M", "left": 20, "top": 100, "width": 9, "height": 12, "line": (1, 1, 1)},
            {"text": "Add", "left": 20, "top": 120, "width": 23, "height": 12, "line": (1, 1, 2)},
        ]
        self.assertFalse(UserQa._ocr_has(words, "MAdd"))


if __name__ == "__main__":
    unittest.main()
