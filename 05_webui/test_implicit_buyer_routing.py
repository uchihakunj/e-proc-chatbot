import unittest

from nlp_features import classify_actor, classify_intent, detect_commodity
from fine_intent_policy import classify_fine_intent


class ImplicitBuyerRoutingTests(unittest.TestCase):
    def assert_route(self, question, expected_intent):
        actor, confidence = classify_actor(question)
        coarse, _ = classify_intent(question)
        intent, intent_confidence = classify_fine_intent(
            question, actor, coarse, detect_commodity(question)
        )
        self.assertEqual("department_buyer", actor)
        self.assertGreaterEqual(confidence, 0.8)
        self.assertEqual(expected_intent, intent)
        self.assertGreaterEqual(intent_confidence, 0.9)

    def test_budget_approved_is_department_approval_workflow(self):
        self.assert_route("Budget approve ho gaya hai. Ab next step kya hai?", "approval_and_budget")

    def test_payment_release_is_department_payment_workflow(self):
        self.assert_route("Payment release se pehle kya verify karna hota hai?", "payment_and_asset_entry")

    def test_projector_is_a_recognised_department_commodity(self):
        self.assertEqual(
            "projector", detect_commodity("Office ke liye projector kharidna hai.")
        )

    def test_stationery_is_a_recognised_department_commodity(self):
        self.assertEqual(
            "stationery_office_supplies",
            detect_commodity("Department ko stationery kharidni hai."),
        )


if __name__ == "__main__":
    unittest.main()
