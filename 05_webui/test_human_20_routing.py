"""Regression coverage for the human-style benchmark's routing expectations."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from fine_intent_policy import (
    canonical_source_contract_sources,
    classify_fine_intent,
    requires_deterministic_policy_answer,
)
from nlp_features import classify_actor, classify_intent, correct_typos, detect_commodity


DATASET = (
    Path(__file__).resolve().parents[1] / "eval" / "human_20" / "dataset.json"
)


class HumanTwentyRoutingTests(unittest.TestCase):
    def test_all_human_queries_keep_expected_actor_and_fine_intent(self):
        rows = json.loads(DATASET.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 20)
        for row in rows:
            with self.subTest(query_id=row["id"]):
                normalized_query, _ = correct_typos(row["query"])
                actor, _ = classify_actor(normalized_query)
                coarse, _ = classify_intent(normalized_query)
                fine, confidence = classify_fine_intent(
                    normalized_query, actor, coarse, detect_commodity(normalized_query)
                )
                self.assertEqual(actor, row["expected_actor"])
                self.assertEqual(fine, row["expected_fine_intent"])
                self.assertGreaterEqual(confidence, 0.8)

    def test_safety_contract_paraphrases_keep_their_intent_and_direct_route(self):
        cases = (
            ("Floods damaged our office equipment. Can we replace it immediately?", "procurement_method_selection"),
            ("Can we specify only Dell laptops because they must work with our existing setup?", "specification_preparation"),
            ("My renewed DSC must replace the old certificate on the portal. What should I do?", "dsc_mapping"),
            ("How does the department initiate EMD refunds for unsuccessful bidders?", "emd_remittance_to_department"),
            ("Before joining a forward e auction, what should a bidder verify?", "auction_participation"),
            ("Where do I upload the BOQ and final Financial Bid for this tender?", "bid_submission_portal_steps"),
            ("As a bid opener, what is the safe way to open Technical Bids?", "bid_opening_portal_steps"),
            ("What DSC and registration steps apply to a foreign supplier bidding in CG?", "vendor_registration"),
        )
        for query, expected_intent in cases:
            with self.subTest(query=query):
                normalized_query, _ = correct_typos(query)
                actor, _ = classify_actor(normalized_query)
                coarse, _ = classify_intent(normalized_query)
                fine, confidence = classify_fine_intent(
                    normalized_query, actor, coarse, detect_commodity(normalized_query)
                )
                self.assertEqual(fine, expected_intent)
                self.assertGreaterEqual(confidence, 0.8)
                self.assertTrue(requires_deterministic_policy_answer(normalized_query, fine))

    def test_general_safety_contracts_cover_unseen_meaning_equivalents(self):
        cases = (
            ("The installed systems are compatible with only one OEM make. May we restrict the specification?", "specification_preparation"),
            ("Our DSC expired and the replacement certificate needs to be selected on the portal.", "dsc_mapping"),
            ("The department needs an urgent procurement route after fire damage to essential equipment.", "procurement_method_selection"),
            ("Where should I enter and upload the quoted amounts for the Financial Bid?", "bid_submission_portal_steps"),
            ("A foreign bidder needs a digital certificate and portal enrolment before participating.", "vendor_registration"),
        )
        for query, intent in cases:
            with self.subTest(query=query):
                self.assertTrue(requires_deterministic_policy_answer(query, intent))

    def test_general_source_contracts_choose_the_governing_source_family(self):
        cases = (
            ("A fire damaged essential equipment and the department needs emergency procurement.", "store purchase rule cg"),
            ("What should we prepare before deciding between GeM and a Tender?", "store purchase rule cg"),
            ("What AMC scope should be ready before procurement?", "store purchase rule cg"),
            ("Does startup status remove EMD for a Tender bid?", "CHiPS_Bid_Submission_Manual_English"),
            ("When should the department use GeM versus the State e-Procurement portal?", "store purchase rule cg"),
        )
        for query, expected_source in cases:
            with self.subTest(query=query):
                sources = canonical_source_contract_sources(query, "unused")
                self.assertIn(expected_source, sources)


if __name__ == "__main__":
    unittest.main()
