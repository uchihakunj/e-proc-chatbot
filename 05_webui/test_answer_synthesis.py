import unittest

from answer_synthesis import build_answer_synthesis_directive, determine_answer_shape


class AnswerSynthesisTests(unittest.TestCase):
    def test_decision_question_answers_decision_first(self):
        plan = build_answer_synthesis_directive(
            "Our office needs 30 laptops. How should we decide whether to use GeM or Tender?",
            "department_buyer", "procurement_method_selection",
            "laptops_computers_it_equipment", "decision_checklist",
        )
        self.assertEqual(plan.answer_shape, "decision")
        self.assertIn("first paragraph must answer the decision", plan.directive)
        self.assertIn("Do not invent a threshold", plan.directive)

    def test_comparison_question_starts_with_comparison(self):
        plan = build_answer_synthesis_directive(
            "GeM aur e-Procurement portal mein difference kya hai?",
            "general_information_user", "gem_eproc_comparison", "unspecified",
            "comparison_table",
        )
        self.assertEqual(plan.answer_shape, "comparison")
        self.assertIn("Markdown comparison table", plan.directive)
        self.assertIn("Do not begin with a generic procurement lifecycle", plan.directive)

    def test_department_process_starts_at_need(self):
        plan = build_answer_synthesis_directive(
            "Office stationery purchase ka process batao.",
            "department_buyer", "procurement_planning", "office_stationery", "process_steps",
        )
        self.assertEqual(plan.answer_shape, "department_workflow")
        self.assertIn("need identification", plan.directive)

    def test_narrow_question_does_not_receive_full_lifecycle(self):
        plan = build_answer_synthesis_directive(
            "Lowest bidder ko hi contract milta hai kya?",
            "department_buyer", "bid_evaluation", "unspecified", "policy_explanation",
        )
        self.assertEqual(plan.answer_shape, "decision")
        self.assertNotIn("need identification and requirement definition", plan.directive)

    def test_commodity_detail_requires_context_support(self):
        plan = build_answer_synthesis_directive(
            "Office ke liye AC AMC karwana hai.",
            "department_buyer", "procurement_planning", "amc_services", "process_steps",
        )
        self.assertIn("only when the supplied Context supports", plan.directive)
        self.assertIn("Do not invent warranties, SLAs, licence terms", plan.directive)

    def test_method_selection_does_not_assume_tender(self):
        plan = build_answer_synthesis_directive(
            "Office ke liye projector kharidna hai.",
            "department_buyer", "procurement_method_selection", "projector", "decision_checklist",
        )
        self.assertIn("Do not declare Tender, GeM, Direct Purchase", plan.directive)
        self.assertIn("not by itself a tender decision", plan.directive)

    def test_bid_evaluation_never_says_highest_bidder_wins(self):
        plan = build_answer_synthesis_directive(
            "Lowest bidder ko hi contract milta hai kya?",
            "department_buyer", "bid_evaluation", "unspecified", "policy_explanation",
        )
        self.assertIn("Never state that the highest bidder wins", plan.directive)

    def test_post_order_payment_is_not_reduced_to_bg(self):
        plan = build_answer_synthesis_directive(
            "Payment release se pehle kya verify karna hota hai?",
            "department_buyer", "purchase_order", "unspecified", "award_steps",
        )
        self.assertIn("do not reduce the answer to Bank Guarantee verification", plan.directive)

    def test_directive_removes_retrieval_artifacts_without_adding_facts(self):
        plan = build_answer_synthesis_directive(
            "What is Limited Tender?", "general_information_user",
            "tender_method_definition", "unspecified", "definition",
        )
        self.assertIn("Ignore retrieval artefacts", plan.directive)
        self.assertIn("Do not reproduce raw OCR", plan.directive)
        self.assertIn("Do not invent a policy rationale", plan.directive)

    def test_definition_is_compact_and_has_no_process_section(self):
        plan = build_answer_synthesis_directive(
            "What is EMD?", "general_information_user", "emd_definition",
            "unspecified", "definition",
        )
        self.assertIn("one concise paragraph", plan.directive)
        self.assertIn("Do not add a Process section", plan.directive)

    def test_definition_excludes_unasked_tender_mechanics(self):
        plan = build_answer_synthesis_directive(
            "What is Limited Tender?", "general_information_user",
            "tender_method_definition", "unspecified", "definition",
        )
        self.assertIn("quotation-opening details", plan.directive)
        self.assertIn("supplier-registration steps", plan.directive)

    def test_payment_check_is_not_reduced_to_bg(self):
        plan = build_answer_synthesis_directive(
            "Payment release se pehle kya verify karna hota hai?", "department_buyer",
            "payment_and_asset_entry", "unspecified", "payment_checklist",
        )
        self.assertIn("invoice/bill", plan.directive)
        self.assertIn("Do not answer with Bank Guarantee", plan.directive)

    def test_definition_does_not_expand_to_workflow(self):
        self.assertEqual(
            determine_answer_shape("Single Tender ka matlab simple language mein batao.",
                                   "general_information_user", "tender_method_definition"),
            "definition",
        )


if __name__ == "__main__":
    unittest.main()
