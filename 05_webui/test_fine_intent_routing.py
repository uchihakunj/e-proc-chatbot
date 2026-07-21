import json
import unittest
from dataclasses import dataclass
from pathlib import Path

from actor_boundary import detect_response_language, language_is_consistent
from fine_intent_policy import (
    CHIPS_CORRIGENDUM_MANUAL,
    POLICIES,
    build_fine_intent_fallback,
    classify_fine_intent,
    detect_answer_mode,
    fine_intent_answer_guard,
    generation_directive,
    has_exact_answer_contract,
    intent_sources_are_sufficient,
    render_fine_intent_fallback,
    retrieval_terms_for_intent,
    requires_deterministic_policy_answer,
    route_for_intent,
    route_for_query,
    source_family,
)
from nlp_features import classify_actor, classify_intent, detect_commodity


@dataclass(frozen=True)
class FineCase:
    number: int
    language: str
    query: str
    actor: str
    intent: str
    stage: str
    preferred_family: str


BASE_CASES = (
    (1, "vendor_bidder", "emd_payment", "emd_payment", "emd_online_payment_manual",
     "I need to pay Rs 50,000 EMD by 15 June 2026. How do I do it?",
     "Mujhe 15 June 2026 tak Rs 50,000 EMD payment karna hai. Kaise karun?",
     "मुझे 15 जून 2026 तक 50,000 रुपये EMD जमा करना है। कैसे करूं?"),
    (2, "vendor_bidder", "emd_payment_failure", "emd_payment_failure", "emd_online_payment_manual",
     "My EMD payment failed but money was debited.",
     "Mera EMD payment fail ho gaya lekin paisa debit ho gaya.",
     "मेरा EMD भुगतान विफल हो गया लेकिन पैसा कट गया।"),
    (3, "vendor_bidder", "emd_refund_unsuccessful_bidder", "emd_refund_unsuccessful", "emd_refund_notice_unsuccessful",
     "When will an unsuccessful bidder receive the EMD refund?",
     "Unsuccessful bidder ko EMD refund kab milega?",
     "असफल bidder को EMD refund कब मिलेगा?"),
    (4, "vendor_bidder", "emd_refund_l1_bidder", "emd_refund_l1", "procurement_manual_l1_security",
     "What happens to the L1 bidder's EMD?",
     "L1 bidder ki EMD ka kya hota hai?",
     "L1 bidder की EMD का क्या होता है?"),
    (5, "general_information_user", "emd_exemption", "eligibility", "current_procurement_rules",
     "Can an MSE get EMD exemption?",
     "Kya MSE ko EMD exemption mil sakti hai?",
     "क्या MSE को EMD में छूट मिल सकती है?"),
    (6, "department_buyer", "gem_direct_purchase_rule", "method_selection", "chhattisgarh_store_purchase_rules",
     "Can a department purchase directly from GeM?",
     "Kya department GeM se direct purchase kar sakta hai?",
     "क्या विभाग GeM से सीधे खरीद कर सकता है?"),
    (7, "general_information_user", "gem_direct_purchase_rule", "method_selection", "chhattisgarh_store_purchase_rules",
     "What is GeM direct purchase?",
     "GeM direct purchase kya hai?",
     "GeM direct purchase क्या है?"),
    (8, "general_information_user", "gem_reverse_auction", "gem_reverse_auction", "gem_rules",
     "When should GeM bidding or reverse auction be used?",
     "GeM bidding ya reverse auction kab use karna chahiye?",
     "GeM bidding या reverse auction कब उपयोग करना चाहिए?"),
    (9, "department_buyer", "gem_department_purchase_process", "gem_procurement", "chhattisgarh_store_purchase_rules",
     "The department wants to purchase a printer from GeM.",
     "Department ko GeM se printer purchase karna hai.",
     "विभाग को GeM से printer खरीदना है।"),
    (10, "vendor_bidder", "vendor_registration", "registration", "vendor_registration_new_supplier",
     "How do I register as a vendor?",
     "Main vendor registration kaise karun?",
     "मैं विक्रेता पंजीकरण कैसे करूं?"),
    (11, "vendor_bidder", "vendor_registration_documents", "registration_documents", "vendor_registration_documents",
     "What documents are required for new supplier registration?",
     "New supplier registration ke liye kaunse documents chahiye?",
     "New supplier registration के लिए कौन से दस्तावेज चाहिए?"),
    (12, "vendor_bidder", "dsc_mapping", "dsc_mapping", "vendor_dsc_mapping",
     "How do I map my renewed DSC?",
     "Renewed DSC ko portal par map kaise karun?",
     "नवीनीकृत DSC को portal पर map कैसे करूं?"),
    (13, "vendor_bidder", "password_recovery", "password_recovery", "vendor_password_recovery",
     "I forgot my vendor password.",
     "Main vendor password bhool gaya. Reset kaise karun?",
     "मैं vendor password भूल गया। Reset कैसे करूं?"),
    (14, "vendor_bidder", "vendor_registration", "registration", "vendor_registration_new_supplier",
     "I am a foreign vendor. How do I register?",
     "Main foreign vendor hoon. Registration kaise karun?",
     "मैं foreign vendor हूं। Registration कैसे करूं?"),
    (15, "department_operator", "corrigendum_portal_steps", "corrigendum_portal", "chips_corrigendum_manual",
     "How does a department issue a corrigendum on the portal?",
     "Department portal par corrigendum kaise issue kare?",
     "विभाग portal पर corrigendum कैसे जारी करे?"),
    (16, "general_information_user", "corrigendum_policy", "corrigendum_policy", "current_procurement_rules",
     "What is the legal purpose of a corrigendum?",
     "Corrigendum ka legal purpose kya hai?",
     "Corrigendum का कानूनी उद्देश्य क्या है?"),
    (17, "vendor_bidder", "bid_deletion_after_corrigendum", "bid_after_corrigendum", "bid_submission_manual",
     "Will my submitted bid be deleted after a corrigendum?",
     "Corrigendum ke baad meri submitted bid delete hogi kya?",
     "Corrigendum के बाद मेरी submitted Bid हट जाएगी क्या?"),
    (18, "vendor_bidder", "bidder_corrigendum_tracking", "corrigendum_tracking", "bid_submission_manual",
     "As a bidder, how do I check a corrigendum?",
     "Bidder ke roop mein corrigendum kaise check karun?",
     "Bidder के रूप में corrigendum कैसे check करूं?"),
    (19, "department_buyer", "procurement_planning", "procurement_planning", "chhattisgarh_store_purchase_rules",
     "The department needs to purchase 50 laptops.",
     "Department ko 50 laptops purchase karne hain.",
     "विभाग को 50 laptop खरीदने हैं।"),
    (20, "department_buyer", "specification_preparation", "specification_preparation", "procurement_manual_specifications",
     "How should technical specifications for laptops be prepared?",
     "Laptop ki technical specifications kaise prepare karein?",
     "Laptop की technical specifications कैसे तैयार करें?"),
    (21, "department_buyer", "bid_evaluation", "bid_evaluation", "procurement_manual_evaluation",
     "How does the department evaluate bids?",
     "Department bids ka evaluation kaise karta hai?",
     "विभाग Bids का मूल्यांकन कैसे करता है?"),
    (22, "department_buyer", "inspection_and_acceptance", "inspection_and_acceptance", "procurement_manual_inspection",
     "What happens after the purchase order?",
     "Purchase Order ke baad department kya karta hai?",
     "Purchase Order के बाद विभाग क्या करता है?"),
)


CASES = tuple(
    FineCase(number, language, query, actor, intent, stage, preferred)
    for number, actor, intent, stage, preferred, en, hinglish, hi in BASE_CASES
    for language, query in (("en", en), ("hinglish", hinglish), ("hi", hi))
)


def fine_intent_audit_records():
    records = []
    for case in CASES:
        actor, actor_confidence = classify_actor(case.query)
        coarse_intent, _ = classify_intent(case.query)
        commodity = detect_commodity(case.query)
        intent, confidence = classify_fine_intent(case.query, actor, coarse_intent, commodity)
        route = route_for_intent(intent)
        records.append({
            "number": case.number,
            "query": case.query,
            "language": detect_response_language(case.query),
            "actor": actor,
            "actor_confidence": actor_confidence,
            "structured_intent": intent,
            "intent_confidence": confidence,
            "preferred_document_families": list(route.preferred_families),
            "supporting_document_families": list(route.supporting_families),
            "excluded_document_families": list(route.excluded_families),
            "required_workflow_stage": route.required_stage,
            "answer_structure": route.answer_structure,
            "fallback_type": route.fallback_type,
        })
    return records


class FineIntentRoutingTests(unittest.TestCase):
    def test_frozen_production_120_fine_intent_regressions(self):
        dataset_path = (
            Path(__file__).resolve().parents[1]
            / "eval" / "production_120" / "dataset.json"
        )
        rows = json.loads(dataset_path.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 120)
        for row in rows:
            with self.subTest(id=row["id"], query=row["query"]):
                actor, _ = classify_actor(row["query"])
                coarse, _ = classify_intent(row["query"])
                intent, confidence = classify_fine_intent(
                    row["query"], actor, coarse, detect_commodity(row["query"])
                )
                self.assertEqual(actor, row["expected_actor"])
                self.assertEqual(intent, row["expected_fine_intent"])
                self.assertGreater(confidence, 0)
                route = route_for_intent(intent)
                self.assertIn(actor, route.expected_actors)

    def test_general_method_overview_and_gem_portal_comparison_are_explicit(self):
        cases = (
            ("In Chhattisgarh, what are the different ways of government procurement?",
             "procurement_methods_overview", "methods_table"),
            ("GeM aur state e-procurement portal mein kya difference hai?",
             "gem_eproc_comparison", "comparison_table"),
        )
        for query, expected, structure in cases:
            actor, _ = classify_actor(query)
            coarse, _ = classify_intent(query)
            intent, confidence = classify_fine_intent(
                query, actor, coarse, detect_commodity(query)
            )
            self.assertEqual(actor, "general_information_user")
            self.assertEqual(intent, expected)
            self.assertGreater(confidence, 0.9)
            self.assertEqual(route_for_intent(intent).answer_structure, structure)

    def test_procurement_methods_overview_lists_routes_not_registration(self):
        cases = (
            "In Chhattisgarh, what are different ways of government procurement?",
            "Chhattisgarh government procurement kaise hoti hai?",
            "What are the procurement methods available to departments?",
        )
        for question in cases:
            with self.subTest(question=question):
                actor, _ = classify_actor(question); coarse, _ = classify_intent(question)
                intent, _ = classify_fine_intent(question, actor, coarse, detect_commodity(question))
                self.assertEqual(intent, "procurement_methods_overview")
                self.assertEqual(detect_answer_mode(question, intent), "overview_list")
                answer = render_fine_intent_fallback(build_fine_intent_fallback(
                    question, actor, intent, "en", "unspecified", "Chhattisgarh",
                    "grounded_deterministic", ("store purchase rule cg.pdf", "GFRupdatedupto31012026.pdf"),
                )).lower()
                for route in ("gem procurement", "tender procurement", "direct purchase", "inter-departmental", "emergency"):
                    self.assertIn(route, answer)
                self.assertIn("channels/platforms", answer)
                self.assertIn("not a procurement method", answer)

    def test_phrase_variants_reach_tender_and_post_order_stages(self):
        cases = (
            ("लिमिटेड टेंडर क्या होता है?", "general_information_user",
             "tender_method_definition"),
            ("What happens after the department issues a purchase order?",
             "department_buyer", "inspection_and_acceptance"),
            ("What should a department do once its purchase order has been issued?",
             "department_buyer", "inspection_and_acceptance"),
            ("Department operator portal par tender create aur publish kaise kare?",
             "department_operator", "tender_creation_portal_steps"),
        )
        for query, expected_actor, expected_intent in cases:
            actor, _ = classify_actor(query)
            coarse, _ = classify_intent(query)
            intent, _ = classify_fine_intent(query, actor, coarse, detect_commodity(query))
            self.assertEqual(actor, expected_actor)
            self.assertEqual(intent, expected_intent)

    def test_uat_decision_policy_and_date_extension_regressions(self):
        cases = (
            ("Department ko 100 chairs kharidni hain. Tender karna padega ya direct purchase ho sakti hai?",
             "department_buyer", "procurement_method_selection"),
            ("Emergency situation mein department purchase kaise kare?",
             "department_buyer", "procurement_method_selection"),
            ("Can we specify Dell laptops only?",
             "department_buyer", "specification_preparation"),
            ("Department ko 20 desktop computers urgently chahiye. Kya options hain?",
             "department_buyer", "procurement_method_selection"),
            ("Lowest bidder select karna compulsory hai kya?",
             "department_buyer", "bid_evaluation"),
            ("Tender ki last date extend karni hai. Kya process hai?",
             "department_operator", "corrigendum_portal_steps"),
        )
        for query, expected_actor, expected_intent in cases:
            with self.subTest(query=query):
                actor, _ = classify_actor(query)
                coarse, _ = classify_intent(query)
                intent, confidence = classify_fine_intent(
                    query, actor, coarse, detect_commodity(query)
                )
                self.assertEqual(actor, expected_actor)
                self.assertEqual(intent, expected_intent)
                self.assertGreater(confidence, 0.9)

    def test_gem_versus_tender_decision_is_not_routed_to_gem_lifecycle(self):
        cases = (
            ("Our office needs 30 laptops. How should we decide whether to use GeM or a tender?", "en"),
            ("Office ke liye 30 laptops chahiye. GeM ya Tender kaise decide karein?", "hinglish"),
            ("कार्यालय के लिए 30 laptops चाहिए। GeM या Tender का निर्णय कैसे करें?", "hi"),
        )
        for question, language in cases:
            with self.subTest(question=question):
                actor, _ = classify_actor(question)
                coarse, _ = classify_intent(question)
                intent, confidence = classify_fine_intent(
                    question, actor, coarse, detect_commodity(question)
                )
                self.assertEqual(actor, "department_buyer")
                self.assertEqual(intent, "procurement_method_selection")
                self.assertGreater(confidence, 0.9)
                self.assertEqual(detect_answer_mode(question, intent), "method_decision")
                answer = render_fine_intent_fallback(build_fine_intent_fallback(
                    question, actor, intent, language, "laptop", "Chhattisgarh",
                    "grounded_deterministic", ("store purchase rule cg.pdf",),
                ))
                self.assertIn("GeM", answer)
                self.assertIn("Tender", answer)
                self.assertNotIn("create and publish the GeM Bid", answer)
                self.assertNotIn("GeM Bid create/publish", answer)
                self.assertEqual(fine_intent_answer_guard(intent, answer, question), (True, ()))

    def test_value_based_method_selection_answers_the_method_decision_first(self):
        question = "Department ko ₹4 lakh ka furniture kharidna hai. Kaunsa procurement method use karna chahiye?"
        actor, _ = classify_actor(question)
        coarse, _ = classify_intent(question)
        intent, confidence = classify_fine_intent(
            question, actor, coarse, detect_commodity(question)
        )
        self.assertEqual(actor, "department_buyer")
        self.assertEqual(intent, "procurement_method_selection")
        self.assertGreater(confidence, 0.8)
        self.assertEqual(detect_answer_mode(question, intent), "method_decision")
        answer = render_fine_intent_fallback(build_fine_intent_fallback(
            question, actor, intent, "hinglish", "furniture", "Chhattisgarh",
            "grounded_deterministic", ("store purchase rule cg.pdf",),
        ))
        self.assertIn("₹4 lakh ki value", answer.lower())
        self.assertIn("GeM", answer)
        self.assertIn("Tender", answer)
        self.assertNotIn("GeM Bid create/publish", answer)
        self.assertEqual(fine_intent_answer_guard(intent, answer, question), (True, ()))

    def test_single_gem_quotation_does_not_default_to_direct_purchase(self):
        question = "Can we buy an item directly if only one quotation is available on GeM?"
        actor, _ = classify_actor(question)
        coarse, _ = classify_intent(question)
        intent, confidence = classify_fine_intent(
            question, actor, coarse, detect_commodity(question)
        )
        self.assertEqual(actor, "department_buyer")
        self.assertEqual(intent, "gem_direct_purchase_rule")
        self.assertGreater(confidence, 0.9)
        answer = render_fine_intent_fallback(build_fine_intent_fallback(
            question, actor, intent, "en", "unspecified", "Chhattisgarh",
            "grounded_deterministic", ("store purchase rule cg.pdf",),
        ))
        self.assertIn("No—not merely because only one quotation", answer)
        self.assertIn("does not by itself establish", answer)
        self.assertIn("price reasonableness", answer)
        self.assertNotIn("L1 price", answer)
        self.assertEqual(fine_intent_answer_guard(intent, answer, question), (True, ()))

    def test_gem_item_unavailable_routes_to_the_next_lawful_method(self):
        question = "Agar item GeM par available nahi hai, department ko next kya karna chahiye?"
        actor, _ = classify_actor(question)
        coarse, _ = classify_intent(question)
        intent, confidence = classify_fine_intent(
            question, actor, coarse, detect_commodity(question)
        )
        self.assertEqual(actor, "department_buyer")
        self.assertEqual(intent, "procurement_method_selection")
        self.assertGreater(confidence, 0.9)
        self.assertEqual(detect_answer_mode(question, intent), "method_decision")
        answer = render_fine_intent_fallback(build_fine_intent_fallback(
            question, actor, intent, "hinglish", "unspecified", "Chhattisgarh",
            "grounded_deterministic", ("store purchase rule cg.pdf",),
        ))
        self.assertIn("unavailable GeM listing par purchase proceed na karein", answer)
        self.assertIn("Tender ya doosra permitted procurement route", answer)
        self.assertNotIn("GeM Bid create/publish", answer)
        self.assertEqual(fine_intent_answer_guard(intent, answer, question), (True, ()))

    def test_three_local_quotations_do_not_replace_open_tender_by_convenience(self):
        question = "Can a department invite quotations from three local suppliers instead of issuing an open tender?"
        actor, _ = classify_actor(question)
        coarse, _ = classify_intent(question)
        intent, confidence = classify_fine_intent(
            question, actor, coarse, detect_commodity(question)
        )
        self.assertEqual(actor, "department_buyer")
        self.assertEqual(intent, "procurement_method_selection")
        self.assertGreater(confidence, 0.9)
        self.assertEqual(detect_answer_mode(question, intent), "method_decision")
        answer = render_fine_intent_fallback(build_fine_intent_fallback(
            question, actor, intent, "en", "unspecified", "Chhattisgarh",
            "grounded_deterministic", ("store purchase rule cg.pdf",),
        ))
        self.assertIn("not merely because three local suppliers", answer)
        self.assertIn("not a convenience-based substitute for an Open Tender", answer)
        self.assertNotIn("full lifecycle", answer.lower())
        self.assertEqual(fine_intent_answer_guard(intent, answer, question), (True, ()))

    def test_urgent_but_not_emergency_uses_a_fast_lawful_option(self):
        question = "Hamare office ko urgently printers chahiye, lekin emergency nahi hai. Fastest lawful option kya hai?"
        actor, _ = classify_actor(question)
        coarse, _ = classify_intent(question)
        intent, confidence = classify_fine_intent(
            question, actor, coarse, detect_commodity(question)
        )
        self.assertEqual(actor, "department_buyer")
        self.assertEqual(intent, "procurement_method_selection")
        self.assertGreater(confidence, 0.9)
        answer = render_fine_intent_fallback(build_fine_intent_fallback(
            question, actor, intent, "hinglish", "printer", "Chhattisgarh",
            "grounded_deterministic", ("store purchase rule cg.pdf",),
        ))
        self.assertIn("Urgency ko emergency procurement exception na samjhein", answer)
        self.assertIn("Single Tender choose na karein", answer)
        self.assertNotIn("asset/stock entry", answer)
        self.assertEqual(fine_intent_answer_guard(intent, answer, question), (True, ()))

    def test_open_tender_preference_uses_the_safe_open_limited_comparison(self):
        question = "When should an Open Tender be preferred over Limited Tender?"
        actor, _ = classify_actor(question)
        coarse, _ = classify_intent(question)
        intent, confidence = classify_fine_intent(
            question, actor, coarse, detect_commodity(question)
        )
        self.assertEqual(actor, "general_information_user")
        self.assertEqual(intent, "tender_method_definition")
        self.assertGreater(confidence, 0.9)
        self.assertEqual(detect_answer_mode(question, intent), "comparison")
        answer = render_fine_intent_fallback(build_fine_intent_fallback(
            question, actor, intent, "en", "unspecified", "Chhattisgarh",
            "grounded_deterministic", ("GFRupdatedupto31012026.pdf",),
        ))
        self.assertIn("All eligible bidders", answer)
        self.assertIn("restricted competition", answer.lower())
        self.assertNotIn("200 crore", answer)
        self.assertEqual(fine_intent_answer_guard(intent, answer, question), (True, ()))

    def test_previous_supplier_familiarity_is_not_a_single_tender_ground(self):
        question = "Can Single Tender be used because the earlier supplier already knows our system?"
        actor, _ = classify_actor(question)
        coarse, _ = classify_intent(question)
        intent, confidence = classify_fine_intent(
            question, actor, coarse, detect_commodity(question)
        )
        self.assertEqual(actor, "department_buyer")
        self.assertEqual(intent, "tender_method_definition")
        self.assertGreater(confidence, 0.9)
        self.assertEqual(detect_answer_mode(question, intent), "policy_conditions")
        answer = render_fine_intent_fallback(build_fine_intent_fallback(
            question, actor, intent, "en", "unspecified", "Chhattisgarh",
            "grounded_deterministic", ("GFRupdatedupto31012026.pdf",),
        ))
        self.assertIn("not a convenience route", answer)
        self.assertIn("written justification", answer)
        self.assertNotIn("earlier supplier", answer.lower())
        self.assertEqual(fine_intent_answer_guard(intent, answer, question), (True, ()))

    def test_oem_spares_requires_a_justified_single_source_ground(self):
        question = "Can the department purchase spare parts only from the original equipment manufacturer?"
        actor, _ = classify_actor(question)
        coarse, _ = classify_intent(question)
        intent, _ = classify_fine_intent(question, actor, coarse, detect_commodity(question))
        self.assertEqual(intent, "procurement_method_selection")
        self.assertEqual(detect_answer_mode(question, intent), "oem_spares_policy")
        answer = render_fine_intent_fallback(build_fine_intent_fallback(
            question, actor, intent, "en", "unspecified", "Chhattisgarh", "grounded_deterministic",
            ("store purchase rule cg.pdf",),
        ))
        self.assertIn("Not automatically", answer)
        self.assertIn("technical justification", answer)
        self.assertNotIn("Tender or GeM Bid", answer)

    def test_pending_financial_sanction_blocks_a_gem_order(self):
        question = "Department ke paas budget hai, lekin financial sanction pending hai. Kya GeM order place kar sakte hain?"
        actor, _ = classify_actor(question); coarse, _ = classify_intent(question)
        intent, _ = classify_fine_intent(question, actor, coarse, detect_commodity(question))
        self.assertEqual(intent, "approval_and_budget")
        self.assertEqual(detect_answer_mode(question, intent), "sanction_gate")
        answer = render_fine_intent_fallback(build_fine_intent_fallback(question, actor, intent, "hinglish", "unspecified", "Chhattisgarh", "grounded_deterministic", ("store purchase rule cg.pdf",)))
        self.assertIn("GeM order place na karein", answer)

    def test_multiline_method_selection_answers_are_decision_first(self):
        cases = (
            "Department\nko 100 chairs\nkharidni hain.\nTender karna\npadega ya\ndirect\npurchase ho\nsakti hai?",
            "We need to\nbuy office\nfurniture. Which\nprocurement method\nshould we\nuse?",
        )
        for question in cases:
            with self.subTest(question=question):
                language = "hinglish" if "chairs" in question else "en"
                actor, _ = classify_actor(question)
                coarse, _ = classify_intent(question)
                intent, _ = classify_fine_intent(
                    question, actor, coarse, detect_commodity(question)
                )
                self.assertEqual(intent, "procurement_method_selection")
                answer = render_fine_intent_fallback(build_fine_intent_fallback(
                    question, "department_buyer", "procurement_method_selection",
                    language, "furniture", "Chhattisgarh", "grounded_deterministic",
                ))
                self.assertIn("GeM", answer)
                self.assertIn("estimated value", answer.lower())
                self.assertNotIn("Select Limited Tender only", answer)
                self.assertNotIn("Limited Tender tabhi choose", answer)

    def test_remaining_uat_routing_regressions(self):
        """Keep the narrow natural-language cases that failed the live UAT routed."""
        cases = (
            ("Can one government department purchase goods from another government department?",
             "general_information_user", "procurement_methods_overview"),
            ("Can a startup participate in tenders?",
             "general_information_user", "tender_eligibility"),
            ("Foreign company tender mein participate kaise kare?",
             "vendor_bidder", "vendor_registration"),
            ("Technical bid aur financial bid mein kya difference hai?",
             "general_information_user", "general_bid_information"),
            ("Bid deadline ke baad bid edit kar sakte hain kya?",
             "vendor_bidder", "bid_submission_portal_steps"),
        )
        for query, expected_actor, expected_intent in cases:
            with self.subTest(query=query):
                actor, _ = classify_actor(query)
                coarse, _ = classify_intent(query)
                intent, confidence = classify_fine_intent(
                    query, actor, coarse, detect_commodity(query)
                )
                self.assertEqual(actor, expected_actor)
                self.assertEqual(intent, expected_intent)
                self.assertGreater(confidence, 0.9)

        self.assertIn("general_information_user", route_for_intent("tender_eligibility").expected_actors)
        self.assertEqual(route_for_intent("general_bid_information").answer_structure, "comparison_table")

    def test_startup_and_foreign_company_fallbacks_do_not_use_domestic_steps(self):
        startup = render_fine_intent_fallback(build_fine_intent_fallback(
            "Can a startup participate in tenders?", "general_information_user",
            "tender_eligibility", "en", "unspecified", "Chhattisgarh",
            "context_validation_rejected", ("CHiPS_Bid_Submission_Manual_English.pdf",),
        ))
        self.assertIn("startup may participate", startup.lower())
        self.assertIn("Tender's eligibility", startup)
        self.assertNotIn("sufficiently reliable section", startup.lower())

        foreign = render_fine_intent_fallback(build_fine_intent_fallback(
            "Foreign company tender mein participate kaise kare?", "vendor_bidder",
            "vendor_registration", "hinglish", "unspecified", "Chhattisgarh",
            "grounded_deterministic", ("CHiPS_Vendor_Registration_Manual_English.pdf",),
        ))
        self.assertIn("Foreign company", foreign)
        self.assertNotIn("Naya domestic supplier", foreign)

    def test_corpus_has_all_required_queries_in_three_languages(self):
        self.assertEqual(len(CASES), 66)
        self.assertEqual({case.number for case in CASES}, set(range(1, 23)))
        for number in range(1, 23):
            self.assertEqual({c.language for c in CASES if c.number == number}, {"en", "hi", "hinglish"})

    def test_actor_fine_intent_language_and_stage(self):
        for case in CASES:
            with self.subTest(number=case.number, language=case.language, query=case.query):
                actor, _ = classify_actor(case.query)
                coarse, _ = classify_intent(case.query)
                commodity = detect_commodity(case.query)
                intent, confidence = classify_fine_intent(case.query, actor, coarse, commodity)
                self.assertEqual(actor, case.actor)
                self.assertEqual(intent, case.intent)
                self.assertGreater(confidence, 0.7)
                self.assertEqual(detect_response_language(case.query), case.language)
                route = route_for_intent(intent)
                self.assertIn(actor, route.expected_actors)
                self.assertEqual(route.required_stage, case.stage)
                self.assertIn(case.preferred_family, route.preferred_families)

    def test_document_policy_is_separated(self):
        for case in CASES:
            with self.subTest(number=case.number, language=case.language):
                route = route_for_intent(case.intent)
                self.assertTrue(route.preferred_families)
                self.assertFalse(set(route.preferred_families) & set(route.excluded_families))
        self.assertIn("emd_refund_notice", POLICIES["emd_payment"].excluded_families)
        self.assertIn("l1_emd_flow", POLICIES["emd_refund_unsuccessful_bidder"].excluded_families)
        self.assertIn("foreign_vendor_section", POLICIES["vendor_registration"].excluded_families)
        self.assertIn("vendor_bid_submission_manual", POLICIES["gem_direct_purchase_rule"].excluded_families)

    def test_new_actor_specific_routes_have_evidence_contracts_and_guards(self):
        cases = {
            "bid_submission_portal_steps": ("vendor_bidder", "CHiPS_Bid_Submission_Manual_English", "Submit the Bid on the portal."),
            "tender_eligibility": ("vendor_bidder", "Guidelines_To_Bidders_EPS_v1.6", "Check Tender eligibility before the Bid."),
            "auction_participation": ("vendor_bidder", "AuctionManual_FA", "Participate in the Auction as a bidder."),
            "tender_publication_portal_steps": ("department_operator", "Manual_Offline_Tenders_v.1.0", "Publish the Tender on the portal."),
            "bid_opening_portal_steps": ("department_operator", "Manual_Offline_Tenders_v.1.0", "Open the technical Bid on the portal."),
        }
        for intent, (actor, source, safe_answer) in cases.items():
            with self.subTest(intent=intent):
                route = route_for_intent(intent)
                self.assertIn(actor, route.expected_actors)
                self.assertTrue(route.preferred_families)
                self.assertTrue(intent_sources_are_sufficient(route, (source,)))
                self.assertEqual(fine_intent_answer_guard(intent, safe_answer), (True, ()))

        mixed = route_for_intent("mixed_role_clarification")
        self.assertEqual(mixed.expected_actors, ("general_information_user",))
        directive = generation_directive(mixed)
        self.assertIn("Ask one concise clarifying question", directive)
        self.assertIn("Do not provide either operational workflow", directive)
        passed, issues = fine_intent_answer_guard(
            "mixed_role_clarification",
            "You should submit the Bid by following these steps.",
        )
        self.assertFalse(passed)
        self.assertTrue(issues)

    def test_forward_auction_uses_the_selected_auction_manual_workflow(self):
        question = "I have been invited to a forward e-auction. What should I check before placing a bid?"
        state = build_fine_intent_fallback(
            question, "vendor_bidder", "auction_participation", "en",
            "unspecified", "Chhattisgarh", "grounded_deterministic",
            ("AuctionManual_FA.pdf",),
        )
        answer = render_fine_intent_fallback(state)
        self.assertIn("Forward Auction", answer)
        self.assertIn("valid DSC", answer)
        self.assertIn("View/Respond to RFX", answer)
        self.assertIn("opening price", answer.lower())
        self.assertIn("minimum bid-change", answer.lower())
        self.assertIn("submit", answer.lower())
        self.assertIn("AuctionManual FA", answer)
        self.assertEqual(
            fine_intent_answer_guard("auction_participation", answer, question),
            (True, ()),
        )

    def test_tender_creation_preparation_question_gets_a_checklist_not_upload_steps(self):
        question = "I am the department operator. What do I need ready before creating a tender in the portal?"
        self.assertEqual(
            detect_answer_mode(question, "tender_creation_portal_steps"),
            "preparation_checklist",
        )
        state = build_fine_intent_fallback(
            question, "department_operator", "tender_creation_portal_steps", "en",
            "unspecified", "Chhattisgarh", "grounded_deterministic",
            ("Manual_Offline_Tenders_v.1.0.pdf", "publicProManual-1755343081262-715558279.pdf"),
        )
        answer = render_fine_intent_fallback(state)
        for term in ("approved requirement", "technical specifications", "evaluation conditions",
                     "Tender schedule", "Tender attachments", "Tender Creator", "DSC"):
            self.assertIn(term, answer)
        self.assertIn("does not establish a universal online-Tender screen sequence", answer)
        self.assertEqual(
            fine_intent_answer_guard("tender_creation_portal_steps", answer, question),
            (True, ()),
        )

    def test_post_deadline_bid_edit_answer_is_direct_in_three_languages(self):
        cases = (
            ("I submitted my bid, but noticed a wrong rate after the bid deadline. Can I edit it?",
             "en", "must not alter or modify"),
            ("Bid submit kar di thi, lekin deadline ke baad rate galat dikha. Kya edit kar sakta hoon?",
             "hinglish", "alter ya modify nahi kar sakta"),
            ("मैंने Bid जमा कर दी थी, लेकिन समय सीमा के बाद rate गलत दिखा। क्या मैं इसे बदल सकता हूँ?",
             "hi", "परिवर्तन या संशोधन नहीं कर सकता"),
        )
        for question, language, expected_text in cases:
            with self.subTest(language=language):
                self.assertEqual(
                    detect_answer_mode(question, "bid_submission_portal_steps"),
                    "restriction_or_prohibition",
                )
                self.assertTrue(has_exact_answer_contract(question, "bid_submission_portal_steps"))
                answer = render_fine_intent_fallback(build_fine_intent_fallback(
                    question, "vendor_bidder", "bid_submission_portal_steps", language,
                    "unspecified", "Chhattisgarh", "grounded_deterministic",
                    ("CHiPS_Bid_Submission_Manual_English.pdf",),
                ))
                self.assertIn(expected_text, answer)
                self.assertNotIn("reliable section available nahi hua", answer)
                self.assertNotIn("sufficiently reliable section", answer)
                self.assertEqual(
                    fine_intent_answer_guard("bid_submission_portal_steps", answer, question),
                    (True, ()),
                )

    def test_fallback_preserves_exact_fine_intent_and_language(self):
        for reason in ("sarvam_timeout", "empty_generation", "retrieval_low_confidence", "workflow_guard_rejected"):
            for case in CASES:
                with self.subTest(reason=reason, number=case.number, language=case.language):
                    state = build_fine_intent_fallback(
                        case.query, case.actor, case.intent, case.language,
                        detect_commodity(case.query), "Chhattisgarh", reason,
                    )
                    self.assertEqual(state.original_question, case.query)
                    self.assertEqual(state.intent, case.intent)
                    self.assertEqual(state.actor, case.actor)
                    self.assertEqual(state.language, case.language)
                    self.assertEqual(state.procurement_stage, case.stage)
                    answer = render_fine_intent_fallback(state)
                    self.assertTrue(language_is_consistent(case.language, answer))

    def test_mandatory_cross_workflow_guards(self):
        unsafe = {
            "emd_payment": "Pay the challan and then follow the EMD refund process for unsuccessful bidders.",
            "emd_refund_unsuccessful_bidder": "The L1 bidder waits until performance security is submitted.",
            "gem_direct_purchase_rule": "Start with laptop need assessment and update the asset register.",
            "corrigendum_policy": "Click the menu and follow the portal screenshot.",
            "bidder_corrigendum_tracking": "Department admin must issue the corrigendum.",
            "emd_remittance_to_department": (
                "The Department Admin processes the EMD refund after online contract approval and "
                "receipt of the Performance Bank Guarantee."
            ),
        }
        for intent, answer in unsafe.items():
            with self.subTest(intent=intent):
                question = (
                    "How do department users process bidders' EMD refunds?"
                    if intent == "emd_remittance_to_department" else ""
                )
                passed, leaks = fine_intent_answer_guard(intent, answer, question)
                self.assertFalse(passed)
                self.assertTrue(leaks)

        safe = {
            "emd_payment": "Use the portal challan to make the EMD payment.",
            "emd_refund_unsuccessful_bidder": "The unsuccessful bidder receives the EMD refund after the applicable stage.",
            "gem_direct_purchase_rule": "GeM direct purchase is governed by the applicable rule.",
            "vendor_registration": "A new supplier uses Vendor registration to register on the portal.",
            "bid_evaluation": "The department performs technical Bid evaluation before commercial evaluation.",
        }
        for intent, answer in safe.items():
            with self.subTest(intent=intent, safe=True):
                self.assertEqual(fine_intent_answer_guard(intent, answer), (True, ()))

    def test_ordinary_and_foreign_vendor_registration_terms_are_separated(self):
        ordinary = " ".join(retrieval_terms_for_intent("vendor_registration", BASE_CASES[9][5])).lower()
        foreign = " ".join(retrieval_terms_for_intent("vendor_registration", BASE_CASES[13][5])).lower()
        self.assertIn("normal domestic vendor", ordinary)
        self.assertNotIn("foreign vendor", ordinary)
        self.assertIn("foreign vendor", foreign)
        ordinary_route = route_for_query("vendor_registration", BASE_CASES[9][5])
        foreign_route = route_for_query("vendor_registration", BASE_CASES[13][5])
        self.assertIn("foreign_vendor_section", ordinary_route.excluded_families)
        self.assertIn("foreign_vendor_registration", foreign_route.preferred_families)
        self.assertNotIn("foreign_vendor_section", foreign_route.excluded_families)

    def test_missing_required_manual_forces_controlled_fallback(self):
        route = route_for_intent("corrigendum_portal_steps")
        self.assertFalse(intent_sources_are_sufficient(
            route,
            ("publicProManual-1755343081262-715558279", "Manual_Offline_Tenders_v.1.0"),
        ))
        self.assertTrue(intent_sources_are_sufficient(route, (CHIPS_CORRIGENDUM_MANUAL,)))

    def test_supporting_source_is_sufficient_for_non_strict_route(self):
        route = route_for_intent("emd_refund_l1_bidder")
        self.assertTrue(intent_sources_are_sufficient(route, ("Online_EMD_Refund_Notice",)))

    def test_current_gfr_filename_variants_share_one_document_family(self):
        self.assertEqual(
            source_family("FInal_GFR_upto_31_07_2024.pdf"),
            "current_procurement_rules",
        )
        self.assertEqual(source_family("GFR2017_HINDI.pdf"), "current_procurement_rules")

    def test_generation_directive_exposes_separation_and_query_constraints(self):
        emd = generation_directive(route_for_intent("emd_payment"))
        self.assertIn("unsuccessful bidder", emd)
        self.assertIn("Never replace a value stated by the user", emd)
        gem = generation_directive(route_for_intent("gem_direct_purchase_rule"))
        self.assertIn("asset register", gem)

    def test_emd_answer_guard_preserves_user_amount_date_and_flow(self):
        question = "I need to pay Rs 50,000 EMD by 15 June 2026. How do I do it?"
        safe = "Pay Rs 50,000 EMD through the challan before 15 June 2026."
        self.assertEqual(fine_intent_answer_guard("emd_payment", safe, question), (True, ()))
        unsafe = ("Pay Rs 10,000 EMD through the challan. If it fails, the amount will be "
                  "refunded. Verify the tender for Rs 50,000 by 15 June 2026.")
        passed, issues = fine_intent_answer_guard("emd_payment", unsafe, question)
        self.assertFalse(passed)
        self.assertIn("manual_example_amount_substituted", issues)

        incidental_return = (
            "Pay Rs 50,000 EMD through the challan before 15 June 2026. "
            "If bank credit fails, the debited amount may be refunded."
        )
        self.assertEqual(
            fine_intent_answer_guard("emd_payment", incidental_return, question),
            (True, ()),
        )

    def test_grounded_draft_failure_uses_intent_specific_safe_answer(self):
        emd_state = build_fine_intent_fallback(
            "Pay Rs 50,000 EMD by 15 June 2026", "vendor_bidder", "emd_payment",
            "en", "unspecified", "Chhattisgarh", "workflow_guard_rejected",
        )
        emd_answer = render_fine_intent_fallback(emd_state)
        self.assertIn("Rs 50,000", emd_answer)
        self.assertIn("15 June 2026", emd_answer)
        self.assertEqual(
            fine_intent_answer_guard("emd_payment", emd_answer, emd_state.original_question),
            (True, ()),
        )
        hinglish_emd_state = build_fine_intent_fallback(
            "EMD 2 lakh jama karni hai 30 July 2026 tak, steps batao.",
            "vendor_bidder", "emd_payment", "hinglish", "unspecified",
            "Chhattisgarh", "workflow_guard_rejected",
            ("EMD_CHALLAN_PAYMENT_V1.0.pdf",),
        )
        hinglish_emd = render_fine_intent_fallback(hinglish_emd_state)
        self.assertIn("2 lakh", hinglish_emd)
        self.assertIn("30 July 2026", hinglish_emd)
        self.assertIn("payment status Successful", hinglish_emd)
        self.assertNotIn("reliable section", hinglish_emd)
        gem_state = build_fine_intent_fallback(
            "Can a department purchase directly from GeM?", "department_buyer",
            "gem_direct_purchase_rule", "en", "unspecified", "Chhattisgarh",
            "language_guard_rejected",
        )
        gem_answer = render_fine_intent_fallback(gem_state)
        self.assertEqual(fine_intent_answer_guard("gem_direct_purchase_rule", gem_answer), (True, ()))

        comparison_state = build_fine_intent_fallback(
            "GeM aur state e-procurement portal mein kya difference hai?",
            "general_information_user", "gem_eproc_comparison", "hinglish",
            "unspecified", "Chhattisgarh", "sarvam_timeout",
        )
        comparison_answer = render_fine_intent_fallback(comparison_state)
        self.assertTrue(language_is_consistent("hinglish", comparison_answer))
        self.assertEqual(
            fine_intent_answer_guard("gem_eproc_comparison", comparison_answer),
            (True, ()),
        )

        inspection_state = build_fine_intent_fallback(
            "What should a department do once its purchase order has been issued?",
            "department_buyer", "inspection_and_acceptance", "en",
            "unspecified", "Chhattisgarh", "sarvam_timeout",
        )
        inspection_answer = render_fine_intent_fallback(inspection_state)
        self.assertTrue(language_is_consistent("en", inspection_answer))
        self.assertEqual(
            fine_intent_answer_guard("inspection_and_acceptance", inspection_answer),
            (True, ()),
        )

        refund_state = build_fine_intent_fallback(
            "What is EMD refund process?", "vendor_bidder",
            "emd_refund_unsuccessful_bidder", "en", "unspecified",
            "Chhattisgarh", "grounded_deterministic",
            ("Online_EMD_Refund_Notice.pdf",),
        )
        refund_answer = render_fine_intent_fallback(refund_state)
        self.assertIn("Department Approver", refund_answer)
        self.assertIn("EMD Refund Guidelines (CHiPS)", refund_answer)
        self.assertEqual(
            fine_intent_answer_guard(
                "emd_refund_unsuccessful_bidder", refund_answer
            ),
            (True, ()),
        )

        registration_state = build_fine_intent_fallback(
            "How do I register as a vendor?", "vendor_bidder",
            "vendor_registration", "en", "unspecified", "Chhattisgarh",
            "grounded_deterministic",
            ("CHiPS_Vendor_Registration_Manual_English.pdf",),
        )
        registration_answer = render_fine_intent_fallback(registration_state)
        self.assertIn("New Supplier Registration", registration_answer)
        self.assertIn("PAN", registration_answer)
        self.assertNotIn("Indian Embassy", registration_answer)
        self.assertIn("e-Procurement portal", registration_answer)
        self.assertNotIn("CHiPS e-Procurement portal", registration_answer)
        self.assertIn("Vendor Registration Manual (CHiPS)", registration_answer)

        operator_state = build_fine_intent_fallback(
            "How does a department issue a corrigendum on the portal?",
            "department_operator", "corrigendum_portal_steps", "en",
            "unspecified", "Chhattisgarh", "grounded_deterministic",
            (CHIPS_CORRIGENDUM_MANUAL,),
        )
        operator_answer = render_fine_intent_fallback(operator_state)
        self.assertIn("Publish All Corrigendum/Addendum", operator_answer)
        self.assertIn("mandatorily delete", operator_answer)
        self.assertIn("Corrigendum Issuance Manual (CHiPS)", operator_answer)
        self.assertNotIn("register as a vendor", operator_answer.lower())

        deletion_state = build_fine_intent_fallback(
            "Will my submitted bid be deleted after a corrigendum?",
            "vendor_bidder", "bid_deletion_after_corrigendum", "en",
            "unspecified", "Chhattisgarh", "grounded_deterministic",
            (CHIPS_CORRIGENDUM_MANUAL,),
        )
        deletion_answer = render_fine_intent_fallback(deletion_state)
        self.assertIn("EMD/Bid Security or Item Corrigendum", deletion_answer)
        self.assertIn("fresh attachments", deletion_answer)
        self.assertIn("Corrigendum Issuance Manual (CHiPS)", deletion_answer)

        operator_refund_state = build_fine_intent_fallback(
            "How does a department operator process bidders' EMD refunds?",
            "department_operator", "emd_remittance_to_department", "en",
            "unspecified", "Chhattisgarh", "workflow_guard_rejected",
            ("Online_EMD_Refund_Notice.pdf",),
        )
        operator_refund_answer = render_fine_intent_fallback(operator_refund_state)
        self.assertIn("Department Admin", operator_refund_answer)
        self.assertIn("Department Approver", operator_refund_answer)
        self.assertIn("registered bank account", operator_refund_answer)
        self.assertIn("EMD Refund Guidelines (CHiPS)", operator_refund_answer)
        self.assertEqual(
            fine_intent_answer_guard(
                "emd_remittance_to_department", operator_refund_answer
            ),
            (True, ()),
        )

        mixed_state = build_fine_intent_fallback(
            "Should I create the tender and submit the bid myself?",
            "general_information_user", "mixed_role_clarification", "en",
            "unspecified", "Chhattisgarh", "workflow_guard_rejected",
        )
        mixed_answer = render_fine_intent_fallback(mixed_state)
        self.assertIn("Which role", mixed_answer)
        self.assertNotIn("1.", mixed_answer)
        self.assertEqual(
            fine_intent_answer_guard("mixed_role_clarification", mixed_answer),
            (True, ()),
        )

        gem_definition_state = build_fine_intent_fallback(
            "जेम क्या है?", "general_information_user", "gem_definition", "hi",
            "unspecified", "Chhattisgarh", "sarvam_timeout",
            ("store purchase rule cg.pdf",),
        )
        gem_definition_answer = render_fine_intent_fallback(gem_definition_state)
        self.assertTrue(language_is_consistent("hi", gem_definition_answer))
        self.assertIn("Government e-Marketplace", gem_definition_answer)
        self.assertIn("Chhattisgarh Store Purchase Rules", gem_definition_answer)
        self.assertEqual(
            fine_intent_answer_guard("gem_definition", gem_definition_answer),
            (True, ()),
        )

        tender_creation_state = build_fine_intent_fallback(
            "विभागीय ऑपरेटर पोर्टल पर निविदा कैसे बनाए?",
            "department_operator", "tender_creation_portal_steps", "hi",
            "unspecified", "Chhattisgarh", "sarvam_timeout",
            ("Manual_Offline_Tenders_v.1.0.pdf",),
        )
        tender_creation_answer = render_fine_intent_fallback(tender_creation_state)
        self.assertTrue(language_is_consistent("hi", tender_creation_answer))
        self.assertIn("Offline Tender", tender_creation_answer)
        self.assertIn("Manual Tender Header Detail", tender_creation_answer)
        self.assertIn("Offline Tender Upload Manual (CHiPS)", tender_creation_answer)
        self.assertEqual(
            fine_intent_answer_guard(
                "tender_creation_portal_steps", tender_creation_answer
            ),
            (True, ()),
        )

    def test_required_chips_corrigendum_manual_is_present_in_corpus(self):
        chunk_root = Path(__file__).resolve().parents[1] / "03_chunking" / "output"
        sources = {path.name.rsplit("_chunk_", 1)[0] for path in chunk_root.glob("*_chunk_*.txt")}
        self.assertIn(CHIPS_CORRIGENDUM_MANUAL, sources)

    def test_remaining_high_impact_intents_have_grounded_deterministic_answers(self):
        cases = (
            ("procurement_method_selection", "en",
             "What method applies to an emergency purchase?", "written justification"),
            ("procurement_method_selection", "hinglish",
             "100 chairs ke liye direct purchase ya tender?", "estimated value"),
            ("procurement_method_selection", "hinglish",
             "Desktop urgently chahiye; kya Single Tender karein?", "urgency"),
            ("bid_evaluation", "hinglish",
             "Lowest bidder select karna compulsory hai kya?", "automatically"),
            ("approval_and_budget", "en",
             "What budget approval is needed before purchase?", "estimated cost"),
            ("specification_preparation", "hinglish",
             "Laptop specifications kaise prepare karein?", "brand-specific"),
            ("purchase_order", "hinglish",
             "Purchase order kaise issue karein?", "po terms"),
            ("payment_and_asset_entry", "hinglish",
             "Payment aur asset entry kaise karein?", "asset/stock register"),
            ("gem_department_purchase_process", "en",
             "The department wants to purchase a printer from GeM.", "department is the buyer"),
            ("dsc_mapping", "en",
             "How do I map my renewed DSC?", "registration/mapping"),
            ("procurement_methods_overview", "en",
             "What do Store Purchase Rules govern?", "procurement/purchase"),
            ("corrigendum_policy", "hinglish",
             "Corrigendum ka legal purpose kya hai?", "legal amendment"),
            ("emd_refund_l1_bidder", "hinglish",
             "L1 bidder ki EMD ka kya hota hai?", "performance bank guarantee"),
            ("emd_exemption", "hinglish",
             "MSE ko EMD exemption milti hai kya?", "mse procurement policy"),
            ("emd_payment_failure", "en",
             "My EMD payment failed but the amount was debited. What next?", "beneficiary account"),
            ("vendor_registration_documents", "hinglish",
             "Vendor registration ke liye kya documents lagenge?", "pan card information"),
            ("tender_publication_portal_steps", "en",
             "How does the tender owner publish a completed tender?", "manual tender header detail"),
        )
        for intent, language, question, expected in cases:
            with self.subTest(intent=intent):
                state = build_fine_intent_fallback(
                    question, route_for_intent(intent).expected_actors[0], intent,
                    language, "unspecified", "Chhattisgarh",
                    "grounded_deterministic", ("publicProManual.pdf",),
                )
                answer = render_fine_intent_fallback(state)
                self.assertIn(expected, answer.lower())
                self.assertNotIn("sufficiently reliable section", answer.lower())
                self.assertTrue(language_is_consistent(language, answer))
                self.assertEqual(
                    fine_intent_answer_guard(intent, answer, question),
                    (True, ()),
                )

    def test_inspection_answer_is_an_actionable_numbered_workflow(self):
        state = build_fine_intent_fallback(
            "PO ke baad maal ka inspection aur acceptance kaise karein?",
            "department_buyer", "inspection_and_acceptance", "hinglish",
            "unspecified", "Chhattisgarh", "grounded_deterministic",
            ("publicProManual-1755343081262-715558279.pdf",),
        )
        answer = render_fine_intent_fallback(state)
        self.assertIn("📋 Process\n1.", answer)
        self.assertIn("formal acceptance", answer.lower())
        self.assertIn("stock/asset register", answer.lower())
        self.assertEqual(
            fine_intent_answer_guard("inspection_and_acceptance", answer),
            (True, ()),
        )

    def test_manual_uat_specificity_regressions_use_grounded_direct_answers(self):
        cases = (
            ("Vendor registration approve hone mein kitna time lagta hai?",
             "vendor_bidder", "vendor_registration_approval_time", "fixed approval time"),
            ("DSC kaise obtain karun?", "vendor_bidder", "dsc_obtainment",
             "licensed certifying authority"),
            ("Tender eligibility criteria kaise check karun?", "vendor_bidder",
             "tender_eligibility", "eligibility clause"),
            ("Technical bid aur financial bid mein kya difference hai?",
             "general_information_user", "general_bid_information", "financial/price bid"),
            ("Technical bids kaise open karte hain?", "department_operator",
             "bid_opening_portal_steps", "scheduled opening time"),
        )
        for question, actor, intent, expected in cases:
            with self.subTest(question=question):
                self.assertEqual(classify_actor(question)[0], actor)
                coarse, _ = classify_intent(question)
                detected, _ = classify_fine_intent(question, actor, coarse, "unspecified")
                self.assertEqual(detected, intent)
                state = build_fine_intent_fallback(
                    question, actor, intent, "en", "unspecified", "Chhattisgarh",
                    "grounded_deterministic", ("CHiPS_Vendor_Registration_Manual_English.pdf",),
                )
                self.assertIn(expected, render_fine_intent_fallback(state).lower())

    def test_exact_answer_contracts_keep_narrow_questions_narrow(self):
        """Regression tests for the ten source-audited synthesis failures."""
        cases = (
            ("What is the difference between Open Tender and Limited Tender?",
             "general_information_user", "tender_method_definition", "comparison",
             ("all eligible bidders", "restricted"), ("procurement lifecycle",)),
            ("When is Single Tender allowed?",
             "general_information_user", "tender_method_definition", "policy_conditions",
             ("exceptional", "written justification", "competent-authority"), ()),
            ("Can one government department purchase goods from another government department?",
             "general_information_user", "procurement_methods_overview", "yes_no_policy",
             ("yes", "original rates"), ("single tender",)),
            ("Can a department split a purchase into smaller orders?",
             "department_buyer", "procurement_planning", "restriction_or_prohibition",
             ("must not artificially split", "consolidated requirement"), ("vendor registration",)),
            ("DSC kaise obtain karun?",
             "vendor_bidder", "dsc_obtainment", "specific_portal_step",
             ("licensed certifying authority", "domestic vendor"), ("foreign-vendor",)),
            ("Tender eligibility criteria kaise check karun?",
             "vendor_bidder", "tender_eligibility", "specific_portal_step",
             ("eligibility clause", "emd/exemption"), ("submit the bid",)),
            ("Vendor registration approve hone mein kitna time lagta hai?",
             "vendor_bidder", "vendor_registration_approval_time", "timeline_or_sla",
             ("does not state a fixed approval time", "helpdesk"), ("1-2 days",)),
            ("Bid deadline ke baad bid edit kar sakte hain kya?",
             "vendor_bidder", "bid_submission_portal_steps", "restriction_or_prohibition",
             ("no", "must not alter or modify"), ("re-submit", "modify or withdraw action")),
            ("Technical bid submit ho gayi hai. Financial bid kaise submit karun?",
             "vendor_bidder", "bid_submission_portal_steps", "specific_portal_step",
             ("financial bid", "boq", "dsc", "acknowledgement"), ("vendor registration dobara",)),
            ("Department admin bid evaluation report kaise generate kare?",
             "department_operator", "bid_evaluation", "specific_portal_step",
             ("verify", "invent"), ("click",)),
        )
        for question, expected_actor, expected_intent, expected_mode, required, forbidden in cases:
            with self.subTest(question=question):
                actor, _ = classify_actor(question)
                coarse, _ = classify_intent(question)
                intent, _ = classify_fine_intent(question, actor, coarse, "unspecified")
                self.assertEqual(actor, expected_actor)
                self.assertEqual(intent, expected_intent)
                self.assertEqual(detect_answer_mode(question, intent), expected_mode)
                self.assertTrue(has_exact_answer_contract(question, intent))
                answer = render_fine_intent_fallback(build_fine_intent_fallback(
                    question, actor, intent, "en", "unspecified", "Chhattisgarh",
                    "grounded_deterministic", ("store purchase rule cg.pdf",),
                )).lower()
                for term in required:
                    self.assertIn(term, answer)
                for term in forbidden:
                    self.assertNotIn(term, answer)
                self.assertEqual(
                    fine_intent_answer_guard(intent, answer, question), (True, ())
                )

    def test_remaining_source_audit_answers_are_specific(self):
        startup = render_fine_intent_fallback(build_fine_intent_fallback(
            "Can a startup participate in tenders?", "general_information_user",
            "tender_eligibility", "en", "unspecified", "Chhattisgarh",
            "grounded_deterministic", ("store purchase rule cg.pdf",),
        )).lower()
        self.assertIn("relaxation", startup)
        self.assertIn("does not automatically waive", startup)

        foreign = render_fine_intent_fallback(build_fine_intent_fallback(
            "Foreign company tender mein participate kaise kare?", "vendor_bidder",
            "vendor_registration", "en", "unspecified", "Chhattisgarh",
            "grounded_deterministic", ("CHiPS_Vendor_Registration_Manual_English.pdf",),
        )).lower()
        self.assertIn("indian embassy", foreign)
        self.assertIn("licensed ca", foreign)

        date_extension = render_fine_intent_fallback(build_fine_intent_fallback(
            "Tender ki last date extend karni hai. Kya process hai?", "department_operator",
            "corrigendum_portal_steps", "hinglish", "unspecified", "Chhattisgarh",
            "grounded_deterministic", (CHIPS_CORRIGENDUM_MANUAL,),
        )).lower()
        self.assertIn("date corrigendum", date_extension)
        self.assertIn("revised", date_extension)
        self.assertNotIn("mandatorily delete", date_extension)

    def test_latency_fallbacks_answer_remaining_narrow_decisions_first(self):
        """A Sarvam timeout must still return the decision the user asked for."""
        cases = (
            (
                "What is EMD?", "general_information_user", "emd_definition", "en",
                ("seriousness", "specific tender", "not a procurement method"),
            ),
            (
                "How should the department estimate the total procurement value before selecting the method?",
                "department_buyer", "procurement_planning", "en",
                ("whole foreseeable requirement", "consolidated estimate", "do not divide"),
            ),
            (
                "Same item alag-alag months mein chahiye. Kya har month direct purchase kar sakte hain?",
                "department_buyer", "procurement_planning", "hinglish",
                ("reasonably foreseeable", "separate purchase", "method justification"),
            ),
            (
                "What is delegated financial power, and how does it affect procurement method selection?",
                "department_buyer", "approval_and_budget", "en",
                ("spending and approval authority", "consolidated estimate", "competent authority"),
            ),
            (
                "Kya lowest quotation milne ka matlab price reasonable hai?",
                "department_buyer", "bid_evaluation", "hinglish",
                ("sirf lowest quotation", "market information", "eligibility"),
            ),
            (
                "What should the department do if all received bids are much higher than the estimated cost?",
                "department_buyer", "bid_evaluation", "en",
                ("do not award automatically", "recheck the estimate", "do not invent"),
            ),
            (
                "Can negotiations be conducted with the L1 bidder after opening financial bids?",
                "department_buyer", "bid_evaluation", "en",
                ("as a routine step", "specific tender conditions", "transparency"),
            ),
            (
                "Tender cancel karne ke liye kya reasons record karne chahiye?",
                "department_buyer", "tender_creation_policy", "hinglish",
                ("procurement-relevant reasons", "reasoned note", "competent authority"),
            ),
        )
        for question, actor, intent, language, required_terms in cases:
            with self.subTest(question=question):
                answer = render_fine_intent_fallback(build_fine_intent_fallback(
                    question, actor, intent, language, "unspecified", "Chhattisgarh",
                    "sarvam_timeout", ("store purchase rule cg.pdf",),
                )).lower()
                for term in required_terms:
                    self.assertIn(term, answer)
                self.assertTrue(language_is_consistent(language, answer))

    def test_attached_live_failure_phrasings_use_direct_policy_answers(self):
        """Natural Hinglish phrasing must not fall through to an unknown answer."""
        cases = (
            (
                "Kya ₹5 lakh ke purchase ko 2–3 parts mein split kar sakte hain?",
                "procurement_planning", "hinglish", ("artificially", "consolidated requirement"),
            ),
            (
                "Same item ko alag-alag dates par purchase karna allowed hai kya?",
                "procurement_planning", "hinglish", ("reasonably foreseeable", "method justification"),
            ),
            (
                "Agar department ko monthly requirement hai to kaise purchase karein?",
                "procurement_planning", "hinglish", ("reasonably foreseeable", "together plan"),
            ),
            (
                "Vendor delivery delay kare to kya action liya ja sakta hai?",
                "purchase_order", "hinglish", ("delivery schedule", "competent approval", "payment release"),
            ),
            (
                "Price high hone par tender cancel kar sakte hain kya?",
                "tender_creation_policy", "hinglish", ("automatic reason", "price reasonableness", "percentage rule"),
            ),
            (
                "Kya lowest bidder ko hi select karna mandatory hota hai?",
                "bid_evaluation", "hinglish", ("automatically select", "technical responsiveness", "competent approval"),
            ),
        )
        for question, expected_intent, language, required_terms in cases:
            with self.subTest(question=question):
                actor, _ = classify_actor(question)
                coarse, _ = classify_intent(question)
                intent, confidence = classify_fine_intent(
                    question, actor, coarse, detect_commodity(question)
                )
                self.assertEqual(intent, expected_intent)
                self.assertGreater(confidence, 0.9)
                self.assertTrue(requires_deterministic_policy_answer(question, intent))
                answer = render_fine_intent_fallback(build_fine_intent_fallback(
                    question, actor, intent, language, "unspecified", "Chhattisgarh",
                    "grounded_deterministic", ("store purchase rule cg.pdf",),
                )).lower()
                for term in required_terms:
                    self.assertIn(term, answer)
                self.assertNotIn("reliable section available", answer)

    def test_d9_and_e10_include_source_supported_answer_contents(self):
        d9 = render_fine_intent_fallback(build_fine_intent_fallback(
            "Technical bid submit ho gayi hai. Financial bid kaise submit karun?",
            "vendor_bidder", "bid_submission_portal_steps", "hinglish", "unspecified",
            "Chhattisgarh", "grounded_deterministic", ("CHiPS_Bid_Submission_Manual_English",),
        )).lower()
        for term in ("financial bid", "boq", "validate", "dsc", "acknowledgement"):
            self.assertIn(term, d9)

        e10 = render_fine_intent_fallback(build_fine_intent_fallback(
            "Department admin bid evaluation report kaise generate kare?",
            "department_operator", "bid_evaluation", "hinglish", "unspecified",
            "Chhattisgarh", "grounded_deterministic", ("publicProManual-1755343081262-715558279",),
        )).lower()
        for term in ("bid-opening record", "rejection reasons", "rate-reasonableness", "approval record"):
            self.assertIn(term, e10)
        self.assertIn("verify", e10)


if __name__ == "__main__":
    unittest.main()
