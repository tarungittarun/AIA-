import unittest

from myspace_user_qa import (
    CALCULATOR_CASES,
    DEFAULT_PACKAGE,
    EXPECTED_VERSION,
    PINNED_APK_SHA256,
    PINNED_GUIDE_SHA256,
    STANDALONE_PACKAGE,
    case_insensitive_match,
    compact,
)


class UserQaContractTests(unittest.TestCase):
    def test_release_hashes_and_version_codes_are_pinned(self):
        self.assertEqual(
            PINNED_APK_SHA256[DEFAULT_PACKAGE],
            "f3257177dc098cf62f54a6f77df526195323d36b23ed5a69f9ff07ddf96b45fb",
        )
        self.assertEqual(
            PINNED_APK_SHA256[STANDALONE_PACKAGE],
            "99c65435e455e241dd3eb65ea6494abcabf2099f5024f6a82c6cf8a621a6bf6b",
        )
        self.assertEqual(PINNED_GUIDE_SHA256,
                         "d494cf934f12f0c5b1e77da2254d026438d1c10d233c9b53e4620beb7014db92")
        self.assertEqual(EXPECTED_VERSION[DEFAULT_PACKAGE], ("3.12.35", 72))
        self.assertEqual(EXPECTED_VERSION[STANDALONE_PACKAGE], ("1.0.33", 34))

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


if __name__ == "__main__":
    unittest.main()
