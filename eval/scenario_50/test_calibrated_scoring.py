"""Regression tests for reviewer-rubric equivalence scoring."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE = Path(__file__).with_name("run_benchmark.py")
SPEC = importlib.util.spec_from_file_location("scenario_50_benchmark", MODULE)
BENCHMARK = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(BENCHMARK)


class CalibratedScoringTests(unittest.TestCase):
    def test_yes_no_rubric_accepts_hinglish_decision(self):
        hits, misses = BENCHMARK.semantic_concept_coverage(
            ["yes/no decision", "rule-based condition"],
            "Haan. Current rules permit the route only when the stated conditions and approval are met.",
        )
        self.assertEqual(hits, ["yes/no decision", "rule-based condition"])
        self.assertEqual(misses, [])

    def test_corrigendum_rubric_accepts_equivalent_language(self):
        hits, misses = BENCHMARK.semantic_concept_coverage(
            ["extension logic", "level playing field"],
            "For a material corrigendum, extend the deadline so bidders have an equal opportunity to respond.",
        )
        self.assertEqual(hits, ["extension logic", "level playing field"])
        self.assertEqual(misses, [])

    def test_literal_coverage_remains_strict_diagnostic(self):
        hits, misses = BENCHMARK.phrase_coverage(
            ["yes/no decision"], "Haan, the rule permits it subject to approval."
        )
        self.assertEqual(hits, [])
        self.assertEqual(misses, ["yes/no decision"])


if __name__ == "__main__":
    unittest.main()
