import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from procurement_grounding import (
    STORE_RULES_FRIENDLY_NAME,
    chhattisgarh_procurement_methods_context,
    is_chhattisgarh_procurement_methods_query,
    render_chhattisgarh_procurement_methods_answer,
)


class ProcurementGroundingTests(unittest.TestCase):
    def test_matches_reported_query_and_common_state_spellings(self):
        queries = (
            "In chhatisgarh, what are different ways of govt. procurement?",
            "What methods of government procurement are used in Chhattisgarh?",
            "CG me govt procurement ke alag tarike kya hain?",
            "छत्तीसगढ़ में सरकारी खरीद के कौन से तरीके हैं?",
        )
        for query in queries:
            with self.subTest(query=query):
                self.assertTrue(is_chhattisgarh_procurement_methods_query(query))

    def test_does_not_hijack_generic_or_portal_tender_type_queries(self):
        queries = (
            "What are the types of tender?",
            "What are the modes of procurement under GFR?",
            "How do I submit a bid in Chhattisgarh?",
        )
        for query in queries:
            with self.subTest(query=query):
                self.assertFalse(is_chhattisgarh_procurement_methods_query(query))

    def test_context_separates_channels_from_methods(self):
        context = chhattisgarh_procurement_methods_context(
            "In Chhattisgarh, what are the different ways of government procurement?"
        )
        self.assertIsNotNone(context)
        for required in (
            "procurement channels",
            "single tender",
            "limited tender",
            "open tender",
            "Direct Purchase",
            "Inter-departmental procurement",
            "11 July 2024",
        ):
            self.assertIn(required, context)
        self.assertIn("11 July 2024", STORE_RULES_FRIENDLY_NAME)

    def test_deterministic_answer_uses_requested_language_and_no_placeholder(self):
        query = "In chhatisgarh, what are different ways of govt. procurement?"
        english = render_chhattisgarh_procurement_methods_answer(query, "en")
        self.assertIn("💡 Answer", english)
        self.assertIn("Tender procurement", english)
        self.assertIn("📘 Source:", english)
        self.assertNotIn("not applicable", english.lower())

        hindi = render_chhattisgarh_procurement_methods_answer(
            "छत्तीसगढ़ में सरकारी खरीद के कौन से तरीके हैं?", "hi"
        )
        self.assertIn("💡 उत्तर", hindi)
        self.assertIn("📘 स्रोत:", hindi)


if __name__ == "__main__":
    unittest.main()
