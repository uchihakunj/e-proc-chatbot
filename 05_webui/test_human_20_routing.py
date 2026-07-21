"""Regression coverage for the human-style benchmark's routing expectations."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from fine_intent_policy import classify_fine_intent
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


if __name__ == "__main__":
    unittest.main()
