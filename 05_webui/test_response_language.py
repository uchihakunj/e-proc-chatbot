"""Regression tests for server-side response language normalization."""

import re
import unittest

from actor_boundary import devanagari_to_roman, language_is_consistent


class ResponseLanguageTests(unittest.TestCase):
    def test_devanagari_answer_becomes_roman_hinglish(self):
        answer = "विभाग GeM पर वस्तु की उपलब्धता जांचे।"

        normalized = devanagari_to_roman(answer)

        self.assertFalse(re.search(r"[\u0900-\u097f]", normalized))
        self.assertIn("GeM", normalized)
        self.assertTrue(language_is_consistent("hinglish", normalized))

    def test_english_and_technical_terms_are_unchanged(self):
        answer = "EMD, Tender, Bid and DSC"
        self.assertEqual(devanagari_to_roman(answer), answer)


if __name__ == "__main__":
    unittest.main()
