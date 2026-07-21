import json
import unittest
from dataclasses import dataclass
from pathlib import Path

from actor_boundary import (
    build_fallback_envelope,
    department_operator_evidence,
    detect_response_language,
    final_workflow_family,
    language_is_consistent,
    prohibited_workflow_leaks,
    render_fallback_for_envelope,
    selected_document_families,
)
from actor_policy import actor_retrieval_terms, allowed_workflow_families
from nlp_features import classify_actor, classify_intent, detect_commodity


@dataclass(frozen=True)
class AuditCase:
    category: str
    query: str
    actor: str
    intent: str
    language: str
    workflow: str
    commodity: str = "unspecified"


CASES = (
    # A. Department buyer: goods, services, emergencies, GeM and tender methods.
    AuditCase("buyer_laptop", "We need to purchase laptops for our department.", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "en", "need_assessment", "laptops_computers_it_equipment"),
    AuditCase("buyer_laptop", "mujhe laptop kharidne ka process batao", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "hinglish", "need_assessment", "laptops_computers_it_equipment"),
    AuditCase("buyer_laptop", "विभाग के लिए लैपटॉप खरीदने की प्रक्रिया बताएं", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "hi", "need_assessment", "laptops_computers_it_equipment"),
    AuditCase("buyer_printer", "Our department needs to purchase 50 printers.", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "en", "need_assessment", "printers_office_equipment"),
    AuditCase("buyer_printer", "printer purchase karna hai department ke liye", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "hinglish", "need_assessment", "printers_office_equipment"),
    AuditCase("buyer_furniture", "How should our office procure furniture?", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "en", "need_assessment", "furniture"),
    AuditCase("buyer_furniture", "hamare office ke liye kursiyan kharidni hain", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "hinglish", "need_assessment", "furniture"),
    AuditCase("buyer_vehicle", "Government department needs to purchase a vehicle", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "en", "need_assessment", "vehicle"),
    AuditCase("buyer_vehicle", "विभाग के लिए वाहन खरीदना है", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "hi", "need_assessment", "vehicle"),
    AuditCase("buyer_software", "Our department wants to procure accounting software", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "en", "need_assessment", "software"),
    AuditCase("buyer_software", "department ke liye software licence chahiye", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "hinglish", "need_assessment", "software"),
    AuditCase("buyer_amc", "We need AMC for department computers", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "en", "need_assessment", "laptops_computers_it_equipment"),
    AuditCase("buyer_amc", "office ke AC ka AMC karana hai", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "hinglish", "need_assessment", "amc_services"),
    AuditCase("buyer_emergency", "Department needs emergency purchase for flood relief", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "en", "approvals", "emergency_goods"),
    AuditCase("buyer_emergency", "आपातकालीन स्थिति में विभाग खरीद कैसे करे?", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "hi", "approvals", "unspecified"),
    AuditCase("buyer_direct_gem", "Can our department purchase directly from GeM?", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "en", "gem_procurement"),
    AuditCase("buyer_direct_gem", "department GeM se direct purchase kaise kare", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "hinglish", "gem_procurement"),
    AuditCase("buyer_open_tender", "Our department needs to initiate an open tender for furniture", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "en", "tender_creation", "furniture"),
    AuditCase("buyer_limited_tender", "hamare vibhag ko limited tender se furniture kharidna hai", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "hinglish", "tender_creation", "furniture"),
    AuditCase("buyer_ambiguous", "Laptop procurement ka next step kya hai?", "department_buyer", "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE", "hinglish", "need_assessment", "laptops_computers_it_equipment"),

    # B. Vendor/bidder: registration through eligibility, including implicit actor wording.
    AuditCase("vendor_registration", "How do I register as a vendor?", "vendor_bidder", "VENDOR_REGISTRATION", "en", "registration"),
    AuditCase("vendor_registration", "main supplier hoon registration kaise karun", "vendor_bidder", "VENDOR_REGISTRATION", "hinglish", "registration"),
    AuditCase("vendor_registration", "मैं विक्रेता के रूप में पंजीकरण कैसे करूं?", "vendor_bidder", "VENDOR_REGISTRATION", "hi", "registration"),
    AuditCase("vendor_dsc", "How does a bidder set up DSC?", "vendor_bidder", "DSC", "en", "dsc"),
    AuditCase("vendor_dsc", "vendor hoon DSC token kaise register karun", "vendor_bidder", "DSC", "hinglish", "dsc"),
    AuditCase("vendor_emd_payment", "How do I pay EMD for my bid?", "vendor_bidder", "EMD_PAYMENT", "en", "emd"),
    AuditCase("vendor_emd_payment", "mujhe EMD payment kaise karna hai as a bidder", "vendor_bidder", "EMD_PAYMENT", "hinglish", "emd"),
    AuditCase("vendor_emd_refund", "My bid was unsuccessful; how do I get EMD refund?", "vendor_bidder", "EMD_REFUND", "en", "emd"),
    AuditCase("vendor_emd_refund", "vendor ka EMD refund kab milega", "vendor_bidder", "EMD_REFUND", "hinglish", "emd"),
    AuditCase("vendor_emd_refund", "What is the EMD refund process?", "vendor_bidder", "EMD_REFUND", "en", "emd"),
    AuditCase("vendor_bid_submission", "How can I submit my bid as a vendor?", "vendor_bidder", "BID_SUBMISSION", "en", "bid_submission"),
    AuditCase("vendor_bid_submission", "main vendor hoon bid kaise submit karun", "vendor_bidder", "BID_SUBMISSION", "hinglish", "bid_submission"),
    AuditCase("vendor_bid_submission", "मैं इस Tender में Bid कैसे जमा करूं?", "vendor_bidder", "BID_SUBMISSION", "hi", "bid_submission"),
    AuditCase("vendor_corrigendum", "As a bidder how do I track a corrigendum?", "vendor_bidder", "CORRIGENDUM_TRACKING", "en", "corrigendum_tracking"),
    AuditCase("vendor_corrigendum", "tender me amendment aaye to vendor kya kare", "vendor_bidder", "CORRIGENDUM_TRACKING", "hinglish", "corrigendum_tracking"),
    AuditCase("vendor_corrigendum", "एक bidder corrigendum को portal पर कैसे check करे?", "vendor_bidder", "CORRIGENDUM_TRACKING", "hi", "corrigendum_tracking"),
    AuditCase("vendor_auction", "How can my company participate in reverse auction?", "vendor_bidder", "AUCTION", "en", "auction_participation"),
    AuditCase("vendor_auction", "vendor auction mein kaise participate kare", "vendor_bidder", "AUCTION", "hinglish", "auction_participation"),
    AuditCase("vendor_eligibility", "Am I eligible to bid for this tender as a supplier?", "vendor_bidder", "TENDER_ELIGIBILITY", "en", "bid_submission"),
    AuditCase("vendor_eligibility", "bidder ke liye tender eligibility kya hai", "vendor_bidder", "TENDER_ELIGIBILITY", "hinglish", "bid_submission"),

    # C. Department operator: portal-side transaction verbs must outrank bidder words.
    AuditCase("operator_create", "How do I create a tender on the department portal?", "department_operator", "TENDER_CREATION", "en", "tender_creation"),
    AuditCase("operator_create", "department admin tender kaise banaye", "department_operator", "TENDER_CREATION", "hinglish", "tender_creation"),
    AuditCase("operator_create", "Department operator portal par tender create aur publish kaise kare?", "department_operator", "TENDER_CREATION", "hinglish", "tender_creation"),
    AuditCase("operator_publish", "Publish the department tender on the portal", "department_operator", "TENDER_PUBLICATION", "en", "tender_publication"),
    AuditCase("operator_publish", "portal operator tender publish kaise kare", "department_operator", "TENDER_PUBLICATION", "hinglish", "tender_publication"),
    AuditCase("operator_corrigendum", "How should the tender owner issue a corrigendum?", "department_operator", "CORRIGENDUM_MANAGEMENT", "en", "corrigendum_management"),
    AuditCase("operator_corrigendum", "department admin ko corrigendum issue karna hai", "department_operator", "CORRIGENDUM_MANAGEMENT", "hinglish", "corrigendum_management"),
    AuditCase("operator_bid_opening", "How does the department open the technical bid?", "department_operator", "BID_OPENING", "en", "bid_opening"),
    AuditCase("operator_bid_opening", "bid opening process for procurement operator", "department_operator", "BID_OPENING", "en", "bid_opening"),
    AuditCase("operator_emd_refund", "How should the department process bidders EMD refunds?", "department_operator", "OPERATOR_EMD_REFUND", "en", "emd_refund_or_remittance"),
    AuditCase("operator_emd_refund", "department operator EMD refund process kare", "department_operator", "OPERATOR_EMD_REFUND", "hinglish", "emd_refund_or_remittance"),
    AuditCase("operator_offline", "How can department admin upload an offline tender?", "department_operator", "OFFLINE_TENDER_UPLOAD", "en", "portal_administration"),
    AuditCase("operator_offline", "offline tender portal par upload kaise kare operator", "department_operator", "OFFLINE_TENDER_UPLOAD", "hinglish", "portal_administration"),

    # D. General information: definitions remain informational and non-operational.
    AuditCase("general_methods", "What are the different government procurement methods?", "general_information_user", "PROCUREMENT_METHODS", "en", "procurement_methods"),
    AuditCase("general_methods", "छत्तीसगढ़ में सरकारी खरीद के तरीके क्या हैं?", "general_information_user", "PROCUREMENT_METHODS", "hi", "procurement_methods"),
    AuditCase("general_comparison", "What is the difference between GeM and e-procurement portal?", "general_information_user", "GEM_EPROC_COMPARISON", "en", "document_explanation"),
    AuditCase("general_comparison", "GeM aur e-procurement portal mein kya antar hai?", "general_information_user", "GEM_EPROC_COMPARISON", "hinglish", "document_explanation"),
    AuditCase("general_limited", "What is limited tender?", "general_information_user", "LIMITED_TENDER_DEFINITION", "en", "definitions"),
    AuditCase("general_limited", "limited tender kya hota hai?", "general_information_user", "LIMITED_TENDER_DEFINITION", "hinglish", "definitions"),
    AuditCase("general_single", "What is single tender?", "general_information_user", "SINGLE_TENDER_DEFINITION", "en", "definitions"),
    AuditCase("general_single", "single tender का अर्थ क्या है?", "general_information_user", "SINGLE_TENDER_DEFINITION", "hi", "definitions"),
    AuditCase("general_emd", "What is EMD?", "general_information_user", "EMD_GENERAL", "en", "definitions"),
    AuditCase("general_emd", "EMD kya hai?", "general_information_user", "EMD_GENERAL", "hinglish", "definitions"),
    AuditCase("general_ambiguous", "How is a tender published in general?", "general_information_user", "TENDER_PUBLICATION", "en", "document_explanation"),
    AuditCase("general_ambiguous", "Corrigendum ka general meaning batao", "general_information_user", "UNKNOWN", "hinglish", "document_explanation"),
)


def audit_records():
    rows = []
    for case in CASES:
        actor, confidence = classify_actor(case.query)
        intent, _ = classify_intent(case.query)
        language = detect_response_language(case.query)
        commodity = detect_commodity(case.query)
        envelope = build_fallback_envelope(
            case.query, actor, intent, commodity, language, "empty_generation"
        )
        answer = render_fallback_for_envelope(envelope)
        rows.append({
            "category": case.category,
            "query": case.query,
            "expected_actor": case.actor,
            "detected_actor": actor,
            "actor_confidence": confidence,
            "detected_intent": intent,
            "detected_language": language,
            "selected_document_families": list(selected_document_families(actor, intent, commodity)),
            "final_workflow_family": final_workflow_family(actor, intent, case.query),
            "prohibited_leakage": list(prohibited_workflow_leaks(actor, answer)),
        })
    return rows


class ActorBoundaryAuditTests(unittest.TestCase):
    def test_uat_implicit_actor_regressions(self):
        """Natural operational phrasing must resolve an actor before retrieval."""
        cases = (
            ("DSC kaise obtain karun?", "vendor_bidder"),
            ("Technical bids kaise open karte hain?", "department_operator"),
            ("Bid deadline ke baad bid edit kar sakte hain kya?", "vendor_bidder"),
            ("Tender ki last date extend karni hai. Kya process hai?", "department_operator"),
            ("Corrigendum upload karne ke baad bidders ko kya karna hota hai?", "vendor_bidder"),
            ("Laptop procurement ke liye kya approval chahiye?", "department_buyer"),
            ("100 chairs kharidni hain, direct purchase ho sakti hai?", "department_buyer"),
            # The remaining actor failures observed in the 51-question UAT.
            ("Before purchasing computers, what approvals are required?", "department_buyer"),
            ("Can we specify Dell laptops only?", "department_buyer"),
            ("Can we split a purchase into smaller orders?", "department_buyer"),
            ("Bid evaluation kaise hoti hai?", "department_buyer"),
            ("Lowest bidder select karna compulsory hai kya?", "department_buyer"),
            ("Inspection aur acceptance process kya hota hai?", "department_buyer"),
            ("Foreign company tender mein participate kaise kare?", "vendor_bidder"),
            ("Can one government department purchase goods from another government department?",
             "general_information_user"),
        )
        for query, expected_actor in cases:
            with self.subTest(query=query):
                actor, confidence = classify_actor(query)
                self.assertEqual(actor, expected_actor)
                self.assertGreater(confidence, 0)
                fallback = render_fallback_for_envelope(build_fallback_envelope(
                    query, actor, "UNKNOWN", "unspecified", "hinglish", "empty_generation"
                ))
                self.assertEqual(prohibited_workflow_leaks(actor, fallback), ())

    def test_set3_actor_boundary_regressions(self):
        """Production Set-3 wording must retain its intended actor boundary."""
        cases = (
            ("Can we buy an item directly if only one quotation is available on GeM?", "department_buyer"),
            ("Can Single Tender be used because the earlier supplier already knows our system?", "department_buyer"),
            ("Ek proprietary software sirf ek company provide karti hai. Kya Single Tender allowed hoga?", "department_buyer"),
            ("Government department ko dusre government undertaking se goods purchase karne hain. Kya tender zaroori hai?", "general_information_user"),
            ("Can we split a ₹10 lakh requirement into five smaller purchase orders?", "department_buyer"),
            ("Purchase start karne se pehle administrative approval aur financial sanction mein kya difference hai?", "department_buyer"),
            ("Who should confirm budget availability before a tender is published?", "department_buyer"),
            ("Can a tender be initiated before the budget is formally available?", "department_buyer"),
            ("Kya lowest quotation milne ka matlab price reasonable hai?", "general_information_user"),
            ("Technical evaluation ke baad financial bids kin bidders ki open honi chahiye?", "department_operator"),
        )
        for query, expected_actor in cases:
            with self.subTest(query=query):
                actor, confidence = classify_actor(query)
                self.assertEqual(actor, expected_actor)
                self.assertGreater(confidence, 0)

    def test_frozen_production_120_actor_regressions(self):
        dataset_path = (
            Path(__file__).resolve().parents[1]
            / "eval" / "production_120" / "dataset.json"
        )
        rows = json.loads(dataset_path.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 120)
        for row in rows:
            with self.subTest(id=row["id"], query=row["query"]):
                actor, confidence = classify_actor(row["query"])
                self.assertEqual(actor, row["expected_actor"])
                self.assertGreater(confidence, 0)

    def test_audit_has_broad_coverage(self):
        self.assertGreaterEqual(len(CASES), 40)
        for prefix, minimum in (("buyer_", 10), ("vendor_", 8), ("operator_", 6), ("general_", 5)):
            self.assertGreaterEqual(len({c.category for c in CASES if c.category.startswith(prefix)}), minimum)
        self.assertTrue(any(c.language == "hi" for c in CASES))
        self.assertTrue(any(c.language == "hinglish" for c in CASES))
        self.assertTrue(any(c.language == "en" for c in CASES))

    def test_actor_and_intent_consistency(self):
        for case in CASES:
            with self.subTest(query=case.query):
                actor, confidence = classify_actor(case.query)
                self.assertEqual(actor, case.actor)
                self.assertGreater(confidence, 0)
                self.assertEqual(classify_intent(case.query)[0], case.intent)
                self.assertEqual(detect_commodity(case.query), case.commodity)

    def test_workflow_family_consistency(self):
        for case in CASES:
            with self.subTest(query=case.query):
                workflow = final_workflow_family(case.actor, case.intent, case.query)
                self.assertEqual(workflow, case.workflow)
                self.assertIn(workflow, allowed_workflow_families(case.actor))

    def test_language_consistency(self):
        for case in CASES:
            with self.subTest(query=case.query):
                language = detect_response_language(case.query)
                self.assertEqual(language, case.language)
                envelope = build_fallback_envelope(
                    case.query, case.actor, case.intent, case.commodity,
                    language, "empty_generation"
                )
                self.assertTrue(language_is_consistent(language, render_fallback_for_envelope(envelope)))

    def test_retrieval_family_consistency(self):
        forbidden = {
            "department_buyer": ("vendor_registration", "bid_submission_manual", "auction_manual"),
            "vendor_bidder": ("department_tender", "goods_procurement", "store_purchase"),
            "department_operator": ("vendor_registration", "goods_procurement", "personal"),
            "general_information_user": ("department_tender_creation", "vendor_registration"),
        }
        for case in CASES:
            with self.subTest(query=case.query):
                families = selected_document_families(case.actor, case.intent, case.commodity)
                self.assertTrue(families)
                joined = " ".join(families).lower()
                for token in forbidden[case.actor]:
                    self.assertNotIn(token, joined)
                terms = " ".join(actor_retrieval_terms(case.actor, case.intent, case.commodity)).lower()
                if case.actor == "department_buyer":
                    self.assertNotIn("vendor-side bid submission", terms)
                elif case.actor == "vendor_bidder":
                    self.assertNotIn("budgetary sanction", terms)
                elif case.actor == "department_operator":
                    self.assertNotIn("vendor registration", terms)
                    if case.intent != "OFFLINE_TENDER_UPLOAD":
                        evidence = department_operator_evidence(case.intent)
                        self.assertTrue(evidence)
                        self.assertTrue(all(row["audience"] == "department_operator" for row in evidence))

    def test_fallback_consistency_for_timeout_empty_and_low_confidence(self):
        for reason in ("sarvam_timeout", "empty_generation", "retrieval_low_confidence"):
            for case in CASES:
                with self.subTest(reason=reason, query=case.query):
                    envelope = build_fallback_envelope(
                        case.query, case.actor, case.intent, case.commodity,
                        case.language, reason
                    )
                    self.assertEqual(envelope.original_question, case.query)
                    self.assertEqual(envelope.actor, case.actor)
                    self.assertEqual(envelope.intent, case.intent)
                    self.assertEqual(envelope.commodity, case.commodity)
                    self.assertEqual(envelope.language, case.language)
                    self.assertEqual(envelope.reason, reason)
                    answer = render_fallback_for_envelope(envelope)
                    self.assertTrue(answer.strip())
                    self.assertTrue(language_is_consistent(case.language, answer))
                    self.assertEqual(prohibited_workflow_leaks(case.actor, answer), ())


if __name__ == "__main__":
    unittest.main()
