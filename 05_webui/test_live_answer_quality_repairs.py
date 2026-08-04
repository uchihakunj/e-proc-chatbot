"""Regression coverage for live natural-language answer-quality failures."""

import unittest

from actor_policy import classify_procurement_actor
from fine_intent_policy import (
    build_fine_intent_fallback,
    classify_fine_intent,
    render_fine_intent_fallback,
    requires_deterministic_policy_answer,
)


class LiveAnswerQualityRepairTests(unittest.TestCase):
    def _answer(self, question, actor, intent):
        state = build_fine_intent_fallback(
            question, actor, intent, "en", "unspecified", "Chhattisgarh",
            "grounded_deterministic", ("store purchase rule cg.pdf",),
        )
        return render_fine_intent_fallback(state).lower()

    def test_gem_unavailable_uses_next_lawful_route_not_a_refusal(self):
        question = "Agar item GeM par available nahi hai to next kya karna chahiye?"
        actor, _ = classify_procurement_actor(question)
        intent, _ = classify_fine_intent(question, actor, "", "unspecified")
        self.assertEqual((actor, intent), ("department_buyer", "procurement_method_selection"))
        self.assertTrue(requires_deterministic_policy_answer(question, intent))
        answer = self._answer(question, actor, intent)
        self.assertIn("not available on gem", answer)
        self.assertIn("permitted", answer)
        self.assertNotIn("uploaded documents do not explicitly", answer)

    def test_value_stated_furniture_question_is_a_decision_not_a_refusal(self):
        question = "Department ko 4 lakh ka furniture kharidna hai. Kaunsa procurement method use karna chahiye?"
        actor, _ = classify_procurement_actor(question)
        intent, _ = classify_fine_intent(question, actor, "", "furniture")
        self.assertEqual((actor, intent), ("department_buyer", "procurement_method_selection"))
        self.assertTrue(requires_deterministic_policy_answer(question, intent))
        answer = self._answer(question, actor, intent)
        self.assertIn("does not automatically decide", answer)
        self.assertIn("do not split", answer)
        self.assertNotRegex(answer, r"\b(?:25,000|50,000|5 lakh)\b")

    def test_open_vs_limited_does_not_mix_thresholds(self):
        question = "Can we use Limited Tender instead of Open Tender?"
        actor, _ = classify_procurement_actor(question)
        intent, _ = classify_fine_intent(question, actor, "", "unspecified")
        self.assertEqual(intent, "tender_method_definition")
        self.assertTrue(requires_deterministic_policy_answer(question, intent))
        answer = self._answer(question, actor, intent)
        self.assertIn("not be used merely", answer)
        self.assertIn("threshold", answer)
        self.assertNotRegex(answer, r"\b50\s*(lakh|,?000)")

    def test_urgent_purchase_is_a_department_method_decision(self):
        question = "urgent purchase ka kya option hai"
        actor, _ = classify_procurement_actor(question)
        intent, _ = classify_fine_intent(question, actor, "", "unspecified")
        self.assertEqual((actor, intent), ("department_buyer", "procurement_method_selection"))
        answer = self._answer(question, actor, intent)
        self.assertIn("does not make a purchase an emergency", answer)
        self.assertNotIn("25,000", answer)

    def test_corrigendum_follow_up_is_bidder_workflow(self):
        question = "corrigendum aane ke baad kya karna hota hai"
        actor, _ = classify_procurement_actor(question)
        intent, _ = classify_fine_intent(question, actor, "", "unspecified")
        self.assertEqual((actor, intent), ("vendor_bidder", "bidder_corrigendum_tracking"))
        self.assertTrue(requires_deterministic_policy_answer(question, intent))
        answer = self._answer(question, actor, intent)
        self.assertIn("as a bidder", answer)
        self.assertIn("do not issue or publish", answer)

    def test_date_extension_uses_only_department_corrigendum_steps(self):
        question = "Tender ki last date extend karni hai. Kya process hai?"
        actor, _ = classify_procurement_actor(question)
        intent, _ = classify_fine_intent(question, actor, "", "unspecified")
        self.assertEqual((actor, intent), ("department_operator", "corrigendum_portal_steps"))
        self.assertTrue(requires_deterministic_policy_answer(question, intent))
        answer = self._answer(question, actor, intent)
        self.assertIn("date corrigendum", answer)
        self.assertNotIn("resubmit", answer)

    def test_generic_printer_workflow_excludes_exception_route(self):
        question = "Printer purchase department ke liye process batao."
        actor, _ = classify_procurement_actor(question)
        intent, _ = classify_fine_intent(question, actor, "", "printers_office_equipment")
        self.assertEqual((actor, intent), ("department_buyer", "procurement_planning"))
        answer = self._answer(question, actor, intent)
        self.assertIn("start by documenting", answer)
        self.assertNotIn("30-day", answer)
        self.assertIn("do not assume a proprietary", answer)


if __name__ == "__main__":
    unittest.main()
