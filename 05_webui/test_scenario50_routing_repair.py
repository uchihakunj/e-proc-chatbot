import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from actor_policy import classify_procurement_actor
from fine_intent_policy import (
    canonical_source_contract_query, canonical_source_contract_sources,
    classify_fine_intent, detect_answer_mode,
)


class Scenario50RoutingRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).parents[1] / "eval" / "scenario_50" / "dataset.json"
        cls.rows = json.loads(path.read_text(encoding="utf-8"))

    def test_frozen_actor_and_intent_routes(self):
        for row in self.rows:
            with self.subTest(id=row["id"]):
                actor, confidence = classify_procurement_actor(row["query"])
                intent, intent_confidence = classify_fine_intent(row["query"], actor, "")
                self.assertEqual(actor, row["expected_actor"])
                self.assertEqual(intent, row["expected_fine_intent"])
                self.assertGreater(confidence, 0.0)
                self.assertGreater(intent_confidence, 0.0)

    def test_high_risk_answer_modes(self):
        expected = {
            4: "policy_conditions", 6: "direct_answer", 9: "restriction_or_prohibition",
            15: "policy_conditions", 21: "direct_answer", 25: "restriction_or_prohibition",
            41: "specific_portal_step", 44: "direct_answer", 46: "specific_portal_step",
            49: "specific_portal_step", 50: "specific_portal_step",
        }
        for row in self.rows:
            if row["id"] not in expected:
                continue
            actor, _ = classify_procurement_actor(row["query"])
            intent, _ = classify_fine_intent(row["query"], actor, "")
            with self.subTest(id=row["id"]):
                self.assertEqual(detect_answer_mode(row["query"], intent), expected[row["id"]])

    def test_source_contracts_name_authoritative_files(self):
        checks = {
            6: "publicpromanual",
            10: "storepurchaserulecg",
            46: "emdchallanpayment",
            47: "edgebrowsersetup",
            48: "manualofflinetenders",
        }
        for row in self.rows:
            if row["id"] not in checks:
                continue
            actor, _ = classify_procurement_actor(row["query"])
            intent, _ = classify_fine_intent(row["query"], actor, "")
            with self.subTest(id=row["id"]):
                self.assertTrue(canonical_source_contract_query(row["query"], intent))
                joined = "".join(canonical_source_contract_sources(row["query"], intent)).lower()
                self.assertIn(checks[row["id"]], "".join(ch for ch in joined if ch.isalnum()))


if __name__ == "__main__":
    unittest.main()
