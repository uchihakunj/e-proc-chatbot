import unittest
from dataclasses import dataclass

from context_selection import pack_context, select_context_results
from fine_intent_policy import route_for_intent


@dataclass
class Point:
    payload: dict


def result(source, text, score):
    return {"point": Point({"source": source, "text": text}), "score": score}


class ContextSelectionTests(unittest.TestCase):
    def test_prefers_authoritative_route_sources_and_diversifies_documents(self):
        route = route_for_intent("gem_direct_purchase_rule")
        rows = [
            result("Bid_Submission_Manual", "Vendor bid submission instructions.", .99),
            result("store purchase rule cg", "State procurement rule for GeM.", .72),
            result("GFRupdatedupto31012026", "Current GFR GeM condition.", .70),
            result("store purchase rule cg", "Second state-rule passage.", .68),
        ]
        selected = select_context_results(rows, route, "Can a department purchase directly from GeM?")
        self.assertEqual([item["point"].payload["source"] for item in selected[:2]], [
            "store purchase rule cg", "GFRupdatedupto31012026",
        ])

    def test_drops_disposal_only_distractor_for_new_purchase_question(self):
        route = route_for_intent("procurement_method_selection")
        rows = [
            result("FInal_GFR_upto_31_07_2024", "Surplus obsolete unserviceable goods with residual value must be disposed of by public auction.", .99),
            result("store purchase rule cg", "Select the applicable procurement route after approvals.", .60),
        ]
        selected = select_context_results(rows, route, "Department ko 4 lakh ka furniture kharidna hai")
        self.assertEqual([item["point"].payload["source"] for item in selected], ["store purchase rule cg"])

    def test_citations_are_exactly_the_documents_sent_in_context(self):
        route = route_for_intent("gem_direct_purchase_rule")
        rows = [
            result("store purchase rule cg", "State rule.", .9),
            result("GFRupdatedupto31012026", "Current GFR.", .8),
        ]
        text, citations, selected = pack_context(
            rows, route, "Can a department purchase directly from GeM?",
            lambda value: value, lambda source: f"Friendly {source}",
            char_budget=1000, per_chunk_cap=1000,
        )
        self.assertEqual(citations, ["Friendly store purchase rule cg", "Friendly GFRupdatedupto31012026"])
        self.assertEqual(len(selected), 2)
        self.assertIn("[Source 1: Friendly store purchase rule cg]", text)
        self.assertLessEqual(len(text), 1000)


if __name__ == "__main__":
    unittest.main()
