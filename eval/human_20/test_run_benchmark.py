from __future__ import annotations

import unittest

from run_benchmark import (
    _extract_json_object,
    build_judge_prompt,
    chunk_evidence_coverage,
    literal_keyword_coverage,
    source_coverage,
)


class HumanBenchmarkScoringTests(unittest.TestCase):
    def test_source_coverage_is_document_recall_not_substring_guessing(self):
        score = source_coverage(
            ["CHiPS_Bid_Submission_Manual_English.pdf", "Online_EMD_Refund_Notice.pdf"],
            ["CHiPS_Bid_Submission_Manual_English.pdf"],
        )
        self.assertEqual(score["coverage"], 0.5)
        self.assertEqual(score["matched_expected_sources"], ["chips_bid_submission_manual_english.pdf"])

    def test_chunk_evidence_accepts_any_term_in_a_reviewer_group(self):
        score = chunk_evidence_coverage(
            [["Financial Bid", "BOQ"], ["DSC", "signed"]],
            [{"text": "Enter the BOQ values and sign using the DSC."}],
        )
        self.assertEqual(score["coverage"], 1.0)

    def test_literal_keyword_coverage_reports_missing_concepts(self):
        score = literal_keyword_coverage("Use GeM and obtain approval.", ["GeM", "approval", "tender"])
        self.assertEqual(score["coverage"], 0.667)
        self.assertEqual(score["missing_keywords"], ["tender"])

    def test_reference_aware_judge_keeps_dimensions_and_derives_pass_from_score(self):
        result = _extract_json_object(
            '{"overall_score": 4, "pass": false, "dimensions": '
            '{"factual_grounding": 5, "material_completeness": 4, '
            '"workflow_safety": 5, "helpfulness": 4}, "reason": "Equivalent wording."}'
        )
        self.assertEqual(result["score"], 4.0)
        self.assertTrue(result["pass"])
        self.assertFalse(result["model_pass"])
        self.assertEqual(result["dimensions"]["factual_grounding"], 5.0)

    def test_judge_prompts_allow_paraphrase_and_separate_reference_free_scope(self):
        reference_free = build_judge_prompt("What is EMD?", "It is bid security.", None)
        reference_aware = build_judge_prompt(
            "What is EMD?", "It is bid security.", "EMD is bid security returned under the applicable process."
        )
        self.assertIn("accurate paraphrases", reference_free)
        self.assertIn("Do not claim to verify factual grounding", reference_free)
        self.assertIn("do not copy a placeholder", reference_free)
        self.assertIn("factual_grounding", reference_aware)
        self.assertIn("reference defines the material facts", reference_aware)


if __name__ == "__main__":
    unittest.main()
