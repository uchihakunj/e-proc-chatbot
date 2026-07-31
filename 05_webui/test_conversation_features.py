"""Fast regression checks for semantic follow-up handling (no model required)."""
from __future__ import annotations

import unittest

from nlp_features import ConversationMemory, resolve_coreference, suggest_followups


class ConversationFeatureTests(unittest.TestCase):
    def test_threshold_followup_keeps_previous_question(self):
        resolved, applied = resolve_coreference(
            "aur agar 3 lakh se kam ho to?",
            "procurement rules (GFR)",
            "What are the open tender rules for a purchase above ₹3 lakh?",
        )
        self.assertTrue(applied)
        self.assertIn("3 lakh", resolved)
        self.assertIn("open tender", resolved.casefold())

    def test_pronoun_followup_is_self_contained(self):
        resolved, applied = resolve_coreference(
            "what about it?", "EMD refund", "When is EMD refunded?"
        )
        self.assertTrue(applied)
        self.assertIn("EMD refund", resolved)
        self.assertIn("When is EMD refunded", resolved)

    def test_self_contained_query_is_not_rewritten(self):
        query = "What documents are required for vendor registration?"
        resolved, applied = resolve_coreference(query, "EMD refund", "When is EMD refunded?")
        self.assertFalse(applied)
        self.assertEqual(query, resolved)

    def test_memory_retains_previous_question(self):
        memory = ConversationMemory()
        memory.record_turn("test", "What is open tender?", "RULES_GFR", "open tender", "answer")
        session = memory.get_session("test")
        resolved, applied = resolve_coreference("and below 3 lakh?", session.last_topic, session.turns[-1].query)
        self.assertTrue(applied)
        self.assertIn("open tender", resolved.casefold())

    def test_rules_followups_are_actionable(self):
        suggestions = suggest_followups("RULES_GFR", query="open tender above 3 lakh")
        self.assertEqual(len(suggestions), 3)
        self.assertTrue(any("GeM" in item for item in suggestions))


if __name__ == "__main__":
    unittest.main()
