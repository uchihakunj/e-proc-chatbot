import unittest

from answer_claim_guard import answer_claim_violations, requires_buffered_claim_validation


class AnswerClaimGuardTests(unittest.TestCase):
    def test_payment_question_rejects_bg_only_answer(self):
        answer = "Payment release se pehle Bank Guarantee issuing bank se verify karein."
        self.assertIn("payment_reduced_to_bg_only", answer_claim_violations(
            "Payment release se pehle kya verify karna hota hai?", answer))

    def test_payment_question_rejects_acceptance_word_without_payment_evidence(self):
        answer = "Bank Guarantee acceptance se pehle issuing bank se verify karein."
        self.assertIn("payment_reduced_to_bg_only", answer_claim_violations(
            "Payment release se pehle kya verify karna hota hai?", answer,
            "payment_and_asset_entry"))

    def test_definition_rejects_unasked_tender_workflow(self):
        answer = "💡 Answer\nLimited Tender definition.\n\n📋 Process\nQuotation prescribed form mein submit karein."
        self.assertIn("definition_expanded_into_unasked_workflow", answer_claim_violations(
            "What is Limited Tender?", answer, "tender_method_definition"))

    def test_tender_timeline_is_not_treated_as_a_simple_definition(self):
        question = "Limited Tender ke first, second aur third invitation ke minimum timelines kya hain?"
        self.assertFalse(requires_buffered_claim_validation(question, "tender_method_definition"))
        self.assertEqual((), answer_claim_violations(
            question, "15, 10 aur 5 days ke timelines apply hote hain.", "tender_method_definition"))

    def test_l1_question_rejects_highest_bidder_claim(self):
        self.assertIn("l1_answer_mentions_highest_bidder", answer_claim_violations(
            "Lowest bidder ko hi contract milta hai kya?", "Highest bidder may be selected."))

    def test_generic_projector_question_rejects_unasked_thresholds(self):
        self.assertIn("generic_commodity_answer_invented_value_workflow", answer_claim_violations(
            "Office ke liye projector kharidna hai.", "₹50,000 ke baad EMD aur Purchase Committee mandatory hai."))

    def test_specific_amount_question_is_not_rejected_for_amount(self):
        self.assertEqual((), answer_claim_violations(
            "Office ke liye ₹4 lakh ka furniture kharidna hai.", "₹4 lakh ke liye applicable rule check karein."))

    def test_budget_question_rejects_vendor_action_and_invented_threshold(self):
        answer = "Rs. 5 lakh se kam direct purchase karein; GeM portal par registration aur bid submission karein."
        issues = answer_claim_violations("Budget approve ho gaya hai. Ab next step kya hai?", answer)
        self.assertIn("budget_question_leaked_vendor_workflow", issues)
        self.assertIn("budget_question_invented_threshold", issues)

    def test_department_printer_question_rejects_unasked_emd(self):
        self.assertIn("generic_commodity_answer_invented_value_workflow", answer_claim_violations(
            "Department ko printer kharidna hai. Process kya hai?", "EMD collect karein aur tender issue karein."))

    def test_only_high_risk_shapes_are_buffered(self):
        self.assertTrue(requires_buffered_claim_validation(
            "Payment release se pehle kya verify karna hota hai?", "unknown"))
        self.assertFalse(requires_buffered_claim_validation(
            "Vendor registration kaise karein?", "vendor_registration"))


if __name__ == "__main__":
    unittest.main()
