"""Regression tests for production benchmark scoring and evidence retention."""

from __future__ import annotations

import unittest

from run_benchmark import is_generic_fallback, score_answer, serialize_context_result


class BenchmarkScoringTests(unittest.TestCase):
    def test_concept_rich_generic_fallback_cannot_pass_factual_scoring(self):
        row = {
            "expected_fine_intent": "procurement_planning",
            "procedural": True,
        }
        answer = (
            "I could not find a sufficiently reliable section. Original question: laptop purchase. "
            "Need, specification, approval, GeM, tender and purchase order."
        )

        scored = score_answer(row, answer)

        self.assertTrue(scored["fallback_used"])
        self.assertFalse(scored["answer_factual_correctness"])
        self.assertFalse(scored["procedural_completeness"])

    def test_grounded_nonfallback_answer_can_pass(self):
        row = {
            "expected_fine_intent": "emd_definition",
            "procedural": False,
        }
        answer = "EMD means Earnest Money Deposit and is bid security submitted with a bid."

        scored = score_answer(row, answer)

        self.assertFalse(is_generic_fallback(answer))
        self.assertTrue(scored["answer_factual_correctness"])
        self.assertTrue(scored["procedural_completeness"])

    def test_exact_two_of_three_concepts_passes_boundary(self):
        row = {
            "expected_fine_intent": "tender_method_definition",
            "procedural": False,
        }
        answer = "An Open Tender is advertised publicly so eligible bidders can compete."

        scored = score_answer(row, answer)

        self.assertEqual(scored["concept_coverage"], 0.667)
        self.assertTrue(scored["answer_factual_correctness"])

    def test_single_tender_definition_accepts_offer_and_single_source_wording(self):
        row = {
            "expected_fine_intent": "tender_method_definition",
            "procedural": False,
        }
        answer = (
            "A Single Tender is a tender method in which an offer is invited "
            "from one identified source, with recorded justification."
        )

        scored = score_answer(row, answer)

        self.assertEqual(scored["concept_coverage"], 1.0)
        self.assertTrue(scored["answer_factual_correctness"])

    def test_context_trace_keeps_scores_location_and_text(self):
        raw = {
            "source": "store_purchase_rules.pdf",
            "page_number": 12,
            "section": "Rule 4",
            "score": 0.91,
            "semantic_score": 0.83,
            "authority_score": 0.95,
            "text": "Relevant procurement rule text.",
            "ignored_internal_field": "not persisted",
        }

        record = serialize_context_result(raw, 3)

        self.assertEqual(record["rank"], 3)
        self.assertEqual(record["page_number"], 12)
        self.assertEqual(record["semantic_score"], 0.83)
        self.assertEqual(record["authority_score"], 0.95)
        self.assertEqual(record["text"], "Relevant procurement rule text.")
        self.assertNotIn("ignored_internal_field", record)


if __name__ == "__main__":
    unittest.main()
