import unittest

from actor_policy import (
    ACTOR_WORKFLOW_FAMILIES,
    actor_retrieval_terms,
    allowed_workflow_families,
)
from nlp_features import (
    classify_actor,
    classify_intent,
    detect_commodity,
    is_personal_purchase_query,
)
from purchase_workflow import (
    department_answer_passes_guard,
    department_buyer_generation_directive,
    department_purchase_evidence,
    personal_purchase_scope_message,
    render_department_purchase_answer,
    render_vendor_bid_submission_answer,
)


class PurchaseWorkflowRegressionTests(unittest.TestCase):
    def test_purchase_splitting_gets_a_direct_prohibition_not_generic_workflow(self):
        answer = render_department_purchase_answer(
            "hinglish", query="Can we split a purchase into smaller orders?"
        ).lower()
        self.assertIn("split", answer)
        self.assertIn("nahi", answer)
        self.assertIn("avoid", answer)

    def test_software_and_amc_use_service_specific_profiles(self):
        software = render_department_purchase_answer(
            "hinglish", commodity="software",
            query="Department ko software license purchase karna hai. Kya process rahega?",
        ).lower()
        self.assertIn("licence model", software)
        self.assertIn("renewal", software)
        self.assertIn("data-security", software)

        amc = render_department_purchase_answer(
            "hinglish", commodity="amc_services",
            query="Department ko AC units ka AMC karana hai. Procedure kya hai?",
        ).lower()
        self.assertIn("service/sla scope", amc)
        self.assertIn("spares", amc)
        self.assertIn("service calls", amc)

    def _assert_department_buyer_query(self, query, commodity):
        actor = classify_actor(query)[0]
        intent = classify_intent(query)[0]
        self.assertEqual(actor, "department_buyer")
        self.assertEqual(intent, "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE")
        self.assertEqual(detect_commodity(query), commodity)

        allowed = allowed_workflow_families(actor)
        for family in (
            "need_assessment", "approvals", "specifications", "gem_procurement",
            "tender_creation", "evaluation", "purchase_order", "inspection", "payment",
        ):
            self.assertIn(family, allowed)
        for forbidden in ("registration", "dsc", "emd", "bid_submission"):
            self.assertNotIn(forbidden, allowed)

        retrieval = " ".join(actor_retrieval_terms(actor, intent, commodity)).lower()
        self.assertIn("government department purchase", retrieval)
        self.assertIn("gem procurement", retrieval)
        self.assertNotIn("vendor-side bid submission", retrieval)
        self.assertNotIn("asset register", retrieval)

        sources = [row["source"] for row in department_purchase_evidence(commodity)]
        self.assertIn("store purchase rule cg", sources)
        self.assertIn("GFRupdatedupto31012026", sources)
        self.assertIn("publicProManual-1755343081262-715558279", sources)

        answer = render_department_purchase_answer("hinglish", commodity=commodity)
        low = answer.lower()
        for expected in (
            "need assessment", "administrative approval", "financial sanction",
            "gem", "tender", "evaluation", "purchase order", "inspection", "payment",
        ):
            self.assertIn(expected, low)
        for forbidden in ("tenders > view", "respond to tender/nit", "add quotation"):
            self.assertNotIn(forbidden, low)
        return actor, sources, answer

    def test_unqualified_laptop_process_is_department_buyer(self):
        self._assert_department_buyer_query(
            "mujhe laptop kharidne ka process batao",
            "laptops_computers_it_equipment",
        )

    def test_department_needs_50_laptops(self):
        self._assert_department_buyer_query(
            "department ko 50 laptops purchase karne hain",
            "laptops_computers_it_equipment",
        )

    def test_printer_for_department_is_buyer_workflow(self):
        _, sources, answer = self._assert_department_buyer_query(
            "printer purchase karna hai department ke liye",
            "printers_office_equipment",
        )
        self.assertNotIn("Compilation of CVC Circulars and Guidelines", sources)
        self.assertIn("printer", answer.lower())

    def test_explicit_vendor_gets_only_vendor_workflow(self):
        query = "main vendor hoon bid kaise submit karun"
        actor = classify_actor(query)[0]
        intent = classify_intent(query)[0]
        self.assertEqual(actor, "vendor_bidder")
        self.assertEqual(intent, "BID_SUBMISSION")
        allowed = allowed_workflow_families(actor)
        for family in (
            "registration", "dsc", "emd", "bid_submission",
            "corrigendum_tracking", "auction_participation",
        ):
            self.assertIn(family, allowed)
        self.assertNotIn("need_assessment", allowed)
        retrieval = " ".join(actor_retrieval_terms(actor, intent, "unspecified"))
        self.assertIn("CHiPS Bid Submission Manual", retrieval)
        answer = render_vendor_bid_submission_answer().lower()
        for expected in ("vendor/bidder side", "dsc", "respond to tender/nit", "price bid"):
            self.assertIn(expected, answer)
        for forbidden in ("need assessment", "purchase indent", "purchase order"):
            self.assertNotIn(forbidden, answer)

    def test_submitted_bid_can_be_revised_only_before_deadline(self):
        answer = render_vendor_bid_submission_answer(
            "hinglish", "Meri submitted bid modify karke resubmit kaise karun?"
        )
        low = answer.lower()
        for expected in (
            "deadline se pehle", "last submitted bid", "technical documents",
            "price bid", "revised bid", "dobara submit", "acknowledgement",
        ):
            self.assertIn(expected, low)
        self.assertIn("deadline ke baad ye actions allowed nahi", low)
        self.assertNotIn("wait for", low)
        for forbidden in (
            "budget sanction", "departmental indent", "create the tender",
            "approve purchase order",
        ):
            self.assertNotIn(forbidden, low)

    def test_all_four_actor_policies_are_explicit(self):
        self.assertEqual(
            set(ACTOR_WORKFLOW_FAMILIES),
            {
                "department_buyer", "vendor_bidder",
                "department_operator", "general_information_user",
            },
        )

    def test_exact_hinglish_query_routes_to_department_procurement(self):
        query = "agar mujhe laptop kharidani hai departments k liye then what should i do next?"
        self.assertEqual(classify_actor(query)[0], "department_buyer")
        self.assertEqual(
            classify_intent(query)[0],
            "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE",
        )
        self.assertEqual(detect_commodity(query), "laptops_computers_it_equipment")

        answer = render_department_purchase_answer("hinglish")
        low = answer.lower()
        for expected in ("need assessment", "budget", "generic", "gem",
                         "vendors bid submit", "inspection", "asset/stock register"):
            self.assertIn(expected, low)
        self.assertNotIn("department ko bid submit", low)
        self.assertNotIn("dsc zaroori", low)
        self.assertIn("single tender normal option nahi", low)
        self.assertTrue(department_answer_passes_guard(answer))

    def test_explicit_vendor_wins_over_department_mention(self):
        query = "Main vendor hoon aur department ke laptop tender mein bid kaise submit karun?"
        self.assertEqual(classify_actor(query)[0], "vendor_bidder")
        self.assertEqual(classify_intent(query)[0], "BID_SUBMISSION")
        answer = render_vendor_bid_submission_answer().lower()
        self.assertIn("vendor/bidder side", answer)
        self.assertIn("dsc", answer)
        self.assertIn("respond to tender/nit", answer)
        self.assertIn("price bid", answer)

    def test_department_quantity_query_is_purchase_planning(self):
        query = "Department ko 50 laptops purchase karne hain."
        self.assertEqual(classify_actor(query)[0], "department_buyer")
        self.assertEqual(
            classify_intent(query)[0],
            "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE",
        )
        directive = department_buyer_generation_directive(detect_commodity(query)).lower()
        self.assertIn("never tell this department to submit a vendor bid", directive)
        self.assertNotIn("vendor registration instructions", directive)

    def test_personal_purchase_is_not_government_workflow(self):
        query = "Mujhe apne personal use ke liye laptop kharidna hai."
        self.assertEqual(classify_actor(query)[0], "general_information_user")
        self.assertTrue(is_personal_purchase_query(query))
        self.assertIn("personal-use", personal_purchase_scope_message().lower())

    def test_brand_specific_laptop_query_gets_cvc_guardrail(self):
        query = "Can our department buy only Dell laptops?"
        self.assertEqual(classify_actor(query)[0], "department_buyer")
        answer = render_department_purchase_answer("en", brand_question=True).lower()
        self.assertIn("functional", answer)
        self.assertIn("performance-based", answer)
        self.assertIn("technical reasons", answer)
        self.assertIn("competent approval", answer)
        self.assertIn("rate reasonableness", answer)
        sources = {row["source"] for row in department_purchase_evidence()}
        self.assertIn("Compilation of CVC Circulars and Guidelines", sources)

    def test_deterministic_buyer_answer_cites_only_selected_sources(self):
        selected = ("store purchase rule cg.pdf", "publicProManual-1755343081262-715558279.pdf")

        answer = render_department_purchase_answer(
            "en", source_refs=selected
        )

        self.assertIn("Chhattisgarh Store Purchase Rules", answer)
        self.assertIn("Manual for Procurement of Goods 2024", answer)
        self.assertNotIn("General Financial Rules", answer)
        self.assertNotIn("CVC Circulars", answer)
        self.assertNotIn("page 187", answer)


if __name__ == "__main__":
    unittest.main()
