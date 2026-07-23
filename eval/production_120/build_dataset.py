"""Build the frozen 120-query production actor/routing benchmark."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).with_name("dataset.json")
ROWS: list[dict] = []


def add(bucket, language, query, actor, intent, topic, families, procedural=True):
    ROWS.append({
        "id": len(ROWS) + 1,
        "bucket": bucket,
        "language": language,
        "query": query,
        "expected_actor": actor,
        "expected_fine_intent": intent,
        "topic": topic,
        "expected_document_families": families,
        "procedural": procedural,
    })


B = "department_buyer"
V = "vendor_bidder"
O = "department_operator"
G = "general_information_user"

# Department buyer: 30 (12 English, 11 Hinglish, 7 Hindi)
add("department_buyer", "en", "Tell me the process to purchase laptops for our department.", B, "procurement_planning", "laptop procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("department_buyer", "en", "The department needs to purchase 50 laptops.", B, "procurement_planning", "laptop procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("department_buyer", "en", "We need printers for the government office; what should we do first?", B, "procurement_planning", "printer procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("department_buyer", "en", "What is the departmental process for buying office furniture?", B, "procurement_planning", "furniture procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("department_buyer", "en", "Our department must procure a vehicle. Explain the planning workflow.", B, "procurement_planning", "vehicle procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("department_buyer", "en", "How should a department procure 200 software licences?", B, "procurement_planning", "software procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("department_buyer", "en", "We need an annual maintenance contract for servers; give the procurement steps.", B, "procurement_planning", "AMC procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("department_buyer", "en", "Which purchase method should our department choose during an emergency?", B, "procurement_method_selection", "emergency purchase", ["chhattisgarh_store_purchase_rules", "current_procurement_rules"])
add("department_buyer", "en", "Can our department purchase a printer directly from GeM?", B, "gem_direct_purchase_rule", "direct GeM purchase", ["chhattisgarh_store_purchase_rules", "current_procurement_rules"], False)
add("department_buyer", "en", "How should we prepare unbiased technical specifications for laptops?", B, "specification_preparation", "technical specifications", ["procurement_manual", "cvc_guidance"])
add("department_buyer", "en", "What budget and administrative approvals are needed before a department purchase?", B, "approval_and_budget", "budget and approvals", ["procurement_manual", "chhattisgarh_store_purchase_rules"])
add("department_buyer", "en", "How should the department evaluate technical and financial bids?", B, "bid_evaluation", "evaluation", ["procurement_manual", "chhattisgarh_store_purchase_rules"])
add("department_buyer", "hinglish", "Department ke liye printer ki specifications kaise banayein?", B, "specification_preparation", "technical specifications", ["procurement_manual", "cvc_guidance"])
add("department_buyer", "hinglish", "Hamare office ko open tender se furniture lena hai, planning kya hogi?", B, "procurement_planning", "open tender", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("department_buyer", "hinglish", "Limited tender kab choose kare department buyer?", B, "procurement_method_selection", "limited tender", ["chhattisgarh_store_purchase_rules", "current_procurement_rules"], False)
add("department_buyer", "hinglish", "Bid evaluation ke baad purchase order issue karne ka process batao.", B, "purchase_order", "purchase order", ["procurement_manual", "chhattisgarh_store_purchase_rules"])
add("department_buyer", "hinglish", "PO ke baad maal ka inspection aur acceptance kaise karein?", B, "inspection_and_acceptance", "inspection and acceptance", ["procurement_manual"])
add("department_buyer", "hinglish", "Supplier ko payment aur asset register entry ka workflow kya hai?", B, "payment_and_asset_entry", "payment and asset entry", ["procurement_manual", "chhattisgarh_store_purchase_rules"])
add("department_buyer", "hinglish", "GeM par L1 purchase department kaise kare?", B, "gem_l1_purchase", "GeM", ["current_procurement_rules", "chhattisgarh_store_purchase_rules"], False)
add("department_buyer", "hinglish", "Department ko GeM bidding se computer kharidne hain, kya process hai?", B, "gem_department_purchase_process", "GeM", ["chhattisgarh_store_purchase_rules", "current_procurement_rules"])
add("department_buyer", "hinglish", "GeM reverse auction department kab use kare?", B, "gem_reverse_auction", "auction", ["current_procurement_rules", "procurement_manual"], False)
add("department_buyer", "hinglish", "Office k liye 100 kursiyan kharidni hain, next kya karna hai?", B, "procurement_planning", "furniture procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("department_buyer", "hinglish", "Software renewal AMC purchase karna hai department ke liye.", B, "procurement_planning", "AMC procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("department_buyer", "hi", "विभाग को 25 लैपटॉप खरीदने हैं। पूरी खरीद प्रक्रिया बताइए।", B, "procurement_planning", "laptop procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("department_buyer", "hi", "प्रिंटर की तकनीकी विनिर्देश निष्पक्ष रूप से कैसे तैयार करें?", B, "specification_preparation", "technical specifications", ["procurement_manual", "cvc_guidance"])
add("department_buyer", "hi", "विभागीय खरीद से पहले बजट और प्रशासनिक स्वीकृति कैसे लें?", B, "approval_and_budget", "budget and approvals", ["procurement_manual", "chhattisgarh_store_purchase_rules"])
add("department_buyer", "hi", "बोली मूल्यांकन के बाद क्रय आदेश जारी करने की प्रक्रिया क्या है?", B, "purchase_order", "purchase order", ["procurement_manual", "chhattisgarh_store_purchase_rules"])
add("department_buyer", "hi", "आपूर्ति मिलने पर निरीक्षण और स्वीकृति कैसे की जाए?", B, "inspection_and_acceptance", "inspection and acceptance", ["procurement_manual"])
add("department_buyer", "hi", "भुगतान के बाद स्टॉक और संपत्ति रजिस्टर में प्रविष्टि कैसे करें?", B, "payment_and_asset_entry", "payment and asset entry", ["procurement_manual", "chhattisgarh_store_purchase_rules"])
add("department_buyer", "hi", "आपातकाल में विभाग को तुरंत सामान खरीदना हो तो कौन सी विधि चुनें?", B, "procurement_method_selection", "emergency purchase", ["chhattisgarh_store_purchase_rules", "current_procurement_rules"])

# Vendor/bidder: 30 (11 English, 12 Hinglish, 7 Hindi)
add("vendor_bidder", "en", "How do I register as a new vendor on the portal?", V, "vendor_registration", "vendor registration", ["vendor_registration_manual"])
add("vendor_bidder", "en", "Which documents are required for new supplier registration?", V, "vendor_registration_documents", "vendor registration", ["vendor_registration_manual"])
add("vendor_bidder", "en", "Is there a vendor registration fee and how is it paid?", V, "vendor_registration_fee", "vendor registration", ["vendor_registration_manual"])
add("vendor_bidder", "en", "I forgot my vendor login password. How can I reset it?", V, "password_recovery", "vendor registration", ["vendor_registration_manual"])
add("vendor_bidder", "en", "As a bidder, how do I obtain a DSC?", V, "dsc_obtainment", "DSC", ["vendor_registration_manual", "bid_submission_manual"])
add("vendor_bidder", "en", "How do I map my renewed DSC on the e-procurement portal?", V, "dsc_mapping", "DSC", ["vendor_registration_manual", "bidder_guidelines"])
add("vendor_bidder", "en", "I need to pay Rs 50,000 EMD by 15 June 2026. How do I do it?", V, "emd_payment", "EMD payment", ["emd_online_payment_manual"])
add("vendor_bidder", "en", "My EMD payment failed but the amount was debited. What next?", V, "emd_payment_failure", "EMD payment", ["emd_online_payment_manual"])
add("vendor_bidder", "en", "When will an unsuccessful bidder receive the EMD refund?", V, "emd_refund_unsuccessful_bidder", "EMD refund", ["emd_refund_notice", "procurement_manual"], False)
add("vendor_bidder", "en", "How can I submit my technical and price bid online?", V, "bid_submission_portal_steps", "tender participation", ["bid_submission_manual"])
add("vendor_bidder", "en", "Am I eligible to participate in this government tender?", V, "tender_eligibility", "tender eligibility", ["bid_submission_manual", "bidder_guidelines"], False)
add("vendor_bidder", "hinglish", "Main vendor hoon, portal par register kaise karun?", V, "vendor_registration", "vendor registration", ["vendor_registration_manual"])
add("vendor_bidder", "hinglish", "Vendor registrtion ke liye kya dokuments lagenge?", V, "vendor_registration_documents", "vendor registration", ["vendor_registration_manual"])
add("vendor_bidder", "hinglish", "Mera vendor password bhool gaya, reset kaise hoga?", V, "password_recovery", "vendor registration", ["vendor_registration_manual"])
add("vendor_bidder", "hinglish", "Bidder DSC token ko portal se map kaise kare?", V, "dsc_mapping", "DSC", ["vendor_registration_manual", "bidder_guidelines"])
add("vendor_bidder", "hinglish", "Renewed DSC se login nahi ho raha, kya karun?", V, "dsc_login_problem", "DSC", ["vendor_registration_manual", "system_configuration"])
add("vendor_bidder", "hinglish", "EMD 2 lakh jama karni hai 30 July 2026 tak, steps batao.", V, "emd_payment", "EMD payment", ["emd_online_payment_manual"])
add("vendor_bidder", "hinglish", "Unsuccessful bidder ki EMD wapas kab aati hai?", V, "emd_refund_unsuccessful_bidder", "EMD refund", ["emd_refund_notice", "procurement_manual"], False)
add("vendor_bidder", "hinglish", "L1 bidder ki EMD ka kya hota hai?", V, "emd_refund_l1_bidder", "EMD refund", ["procurement_manual", "emd_refund_notice"], False)
add("vendor_bidder", "hinglish", "Tender me bid submit kaise karu?", V, "bid_submission_portal_steps", "tender participation", ["bid_submission_manual"])
add("vendor_bidder", "hinglish", "Submitted bid ko deadline se pehle modify aur resubmit kaise karein?", V, "bid_submission_portal_steps", "tender participation", ["bid_submission_manual"])
add("vendor_bidder", "hinglish", "Bidder corrigendum check kaha kare?", V, "bidder_corrigendum_tracking", "corrigendum", ["bid_submission_manual", "chips_corrigendum_manual"])
add("vendor_bidder", "hinglish", "Reverse auction mein vendor kaise participate kare?", V, "auction_participation", "auction", ["chips_auction_manual", "bid_submission_manual"])
add("vendor_bidder", "hi", "मैं नया विक्रेता हूँ। पोर्टल पर पंजीकरण कैसे करूँ?", V, "vendor_registration", "vendor registration", ["vendor_registration_manual"])
add("vendor_bidder", "hi", "बोलीदाता अपना डिजिटल हस्ताक्षर प्रमाणपत्र कैसे जोड़े?", V, "dsc_mapping", "DSC", ["vendor_registration_manual", "bidder_guidelines"])
add("vendor_bidder", "hi", "मुझे ईएमडी जमा करनी है। ऑनलाइन भुगतान प्रक्रिया बताइए।", V, "emd_payment", "EMD payment", ["emd_online_payment_manual"])
add("vendor_bidder", "hi", "असफल बोलीदाता की ईएमडी वापसी कैसे होती है?", V, "emd_refund_unsuccessful_bidder", "EMD refund", ["emd_refund_notice", "procurement_manual"])
add("vendor_bidder", "hi", "तकनीकी और मूल्य बोली ऑनलाइन कैसे जमा करें?", V, "bid_submission_portal_steps", "tender participation", ["bid_submission_manual"])
add("vendor_bidder", "hi", "शुद्धिपत्र आने पर मेरी जमा बोली का क्या होगा?", V, "bid_deletion_after_corrigendum", "corrigendum", ["chips_corrigendum_manual", "bid_submission_manual"], False)
add("vendor_bidder", "hi", "ई-नीलामी में बोलीदाता कैसे भाग ले?", V, "auction_participation", "auction", ["chips_auction_manual", "bid_submission_manual"])

# Department operator: 25 (9 English, 9 Hinglish, 7 Hindi)
add("department_operator", "en", "As department operator, how do I create a tender on the portal?", O, "tender_creation_portal_steps", "tender creation", ["department_tender_creation_manual"])
add("department_operator", "en", "How does the tender owner publish a completed tender?", O, "tender_publication_portal_steps", "tender publication", ["department_tender_creation_manual"])
add("department_operator", "en", "How does a department issue a corrigendum on the portal?", O, "corrigendum_portal_steps", "corrigendum", ["chips_corrigendum_manual"])
add("department_operator", "en", "Give the portal steps for issuing a Date Corrigendum.", O, "corrigendum_portal_steps", "corrigendum", ["chips_corrigendum_manual"])
add("department_operator", "en", "How does a tender owner issue an EMD/Bid Security Corrigendum?", O, "corrigendum_portal_steps", "corrigendum", ["chips_corrigendum_manual"])
add("department_operator", "en", "How should the bid opener open the technical bid online?", O, "bid_opening_portal_steps", "bid opening", ["department_tender_creation_manual", "procurement_manual"])
add("department_operator", "en", "How does the department operator open the price bid?", O, "bid_opening_portal_steps", "bid opening", ["department_tender_creation_manual", "procurement_manual"])
add("department_operator", "en", "How do department users process bidders' EMD refunds?", O, "emd_remittance_to_department", "EMD refund", ["emd_refund_notice"])
add("department_operator", "en", "How can an operator upload and publish an offline tender?", O, "tender_creation_portal_steps", "offline tender", ["department_tender_creation_manual"])
add("department_operator", "hinglish", "Tender owner portal par naya tender create kaise kare?", O, "tender_creation_portal_steps", "tender creation", ["department_tender_creation_manual"])
add("department_operator", "hinglish", "Department operator tender publish kaise kare?", O, "tender_publication_portal_steps", "tender publication", ["department_tender_creation_manual"])
add("department_operator", "hinglish", "Date corrigendum portal par issue karne ke steps?", O, "corrigendum_portal_steps", "corrigendum", ["chips_corrigendum_manual"])
add("department_operator", "hinglish", "Tender term corrigendum kaise jari kare department user?", O, "corrigendum_portal_steps", "corrigendum", ["chips_corrigendum_manual"])
add("department_operator", "hinglish", "Attachment corrigendum upload aur publish kaise hoga?", O, "corrigendum_portal_steps", "corrigendum", ["chips_corrigendum_manual"])
add("department_operator", "hinglish", "Required attachment corrigendum me bid deletion option kya kare?", O, "corrigendum_portal_steps", "corrigendum", ["chips_corrigendum_manual"])
add("department_operator", "hinglish", "Technical bid open karne ka operator workflow batao.", O, "bid_opening_portal_steps", "bid opening", ["department_tender_creation_manual", "procurement_manual"])
add("department_operator", "hinglish", "Department approver EMD refund process kaise complete kare?", O, "emd_remittance_to_department", "EMD refund", ["emd_refund_notice"])
add("department_operator", "hinglish", "Offline tendr portal pe upload kaise karna hai?", O, "tender_creation_portal_steps", "offline tender", ["department_tender_creation_manual"])
add("department_operator", "hi", "विभागीय ऑपरेटर पोर्टल पर निविदा कैसे बनाए?", O, "tender_creation_portal_steps", "tender creation", ["department_tender_creation_manual"])
add("department_operator", "hi", "निविदा स्वामी निविदा प्रकाशित कैसे करे?", O, "tender_publication_portal_steps", "tender publication", ["department_tender_creation_manual"])
add("department_operator", "hi", "विभागीय उपयोगकर्ता ईएमडी शुद्धिपत्र कैसे जारी करे?", O, "corrigendum_portal_steps", "corrigendum", ["chips_corrigendum_manual"])
add("department_operator", "hi", "आइटम शुद्धिपत्र जारी करने की पोर्टल प्रक्रिया बताइए।", O, "corrigendum_portal_steps", "corrigendum", ["chips_corrigendum_manual"])
add("department_operator", "hi", "तकनीकी बोली खोलने की ऑनलाइन प्रक्रिया क्या है?", O, "bid_opening_portal_steps", "bid opening", ["department_tender_creation_manual", "procurement_manual"])
add("department_operator", "hi", "विभाग असफल बोलीदाताओं की ईएमडी वापसी कैसे संसाधित करे?", O, "emd_remittance_to_department", "EMD refund", ["emd_refund_notice"])
add("department_operator", "hi", "ऑफलाइन निविदा को पोर्टल पर अपलोड और प्रकाशित कैसे करें?", O, "tender_creation_portal_steps", "offline tender", ["department_tender_creation_manual"])

# General information: 25 (9 English, 9 Hinglish, 7 Hindi)
add("general_information", "en", "In Chhattisgarh, what are the different ways of government procurement?", G, "procurement_methods_overview", "procurement methods", ["chhattisgarh_store_purchase_rules", "current_procurement_rules"], False)
add("general_information", "en", "What is GeM?", G, "gem_definition", "GeM", ["current_procurement_rules", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "en", "What is the difference between GeM and the Chhattisgarh e-Procurement portal?", G, "gem_eproc_comparison", "GeM", ["current_procurement_rules", "procurement_manual", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "en", "What is a limited tender?", G, "tender_method_definition", "limited tender", ["current_procurement_rules", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "en", "What is a single tender and when is it exceptional?", G, "tender_method_definition", "single tender", ["current_procurement_rules", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "en", "What does open tender mean?", G, "tender_method_definition", "open tender", ["current_procurement_rules", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "en", "What is EMD or bid security?", G, "emd_definition", "EMD", ["current_procurement_rules", "procurement_manual"], False)
add("general_information", "en", "Can an MSE claim exemption from EMD?", G, "emd_exemption", "EMD", ["current_procurement_rules", "procurement_manual"], False)
add("general_information", "en", "What do the Chhattisgarh Store Purchase Rules govern?", G, "procurement_methods_overview", "Store Purchase Rules", ["chhattisgarh_store_purchase_rules"], False)
add("general_information", "hinglish", "CG me govt procurement ke alag tarike kya hain?", G, "procurement_methods_overview", "procurement methods", ["chhattisgarh_store_purchase_rules", "current_procurement_rules"], False)
add("general_information", "hinglish", "GeM kya hota hai?", G, "gem_definition", "GeM", ["current_procurement_rules", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "hinglish", "GeM aur state e-procurement portal me fark batao.", G, "gem_eproc_comparison", "GeM", ["current_procurement_rules", "procurement_manual", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "hinglish", "Limited tender ka simple meaning kya hai?", G, "tender_method_definition", "limited tender", ["current_procurement_rules", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "hinglish", "Single tender kab allowed hota hai?", G, "tender_method_definition", "single tender", ["current_procurement_rules", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "hinglish", "Open tender sab vendors ke liye hota hai kya?", G, "tender_method_definition", "open tender", ["current_procurement_rules", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "hinglish", "EMD kya hai aur kyu li jati hai?", G, "emd_definition", "EMD", ["current_procurement_rules", "procurement_manual"], False)
add("general_information", "hinglish", "MSE ko EMD exemption milti hai kya?", G, "emd_exemption", "EMD", ["current_procurement_rules", "procurement_manual"], False)
add("general_information", "hinglish", "Store Purchase Rules CG kis purchase par apply hote hain?", G, "procurement_methods_overview", "Store Purchase Rules", ["chhattisgarh_store_purchase_rules"], False)
add("general_information", "hi", "छत्तीसगढ़ में सरकारी खरीद की अलग-अलग विधियाँ क्या हैं?", G, "procurement_methods_overview", "procurement methods", ["chhattisgarh_store_purchase_rules", "current_procurement_rules"], False)
add("general_information", "hi", "जेम क्या है?", G, "gem_definition", "GeM", ["current_procurement_rules", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "hi", "जेम और छत्तीसगढ़ ई-प्रोक्योरमेंट पोर्टल में क्या अंतर है?", G, "gem_eproc_comparison", "GeM", ["current_procurement_rules", "procurement_manual", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "hi", "सीमित निविदा क्या होती है?", G, "tender_method_definition", "limited tender", ["current_procurement_rules", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "hi", "एकल निविदा क्या है और इसका उपयोग कब होता है?", G, "tender_method_definition", "single tender", ["current_procurement_rules", "chhattisgarh_store_purchase_rules"], False)
add("general_information", "hi", "ईएमडी या बोली सुरक्षा का अर्थ क्या है?", G, "emd_definition", "EMD", ["current_procurement_rules", "procurement_manual"], False)
add("general_information", "hi", "शुद्धिपत्र का कानूनी उद्देश्य क्या है?", G, "corrigendum_policy", "corrigendum", ["current_procurement_rules", "procurement_manual"], False)

# Ambiguous or mixed-role: 10 (4 English, 4 Hinglish, 2 Hindi)
add("ambiguous_mixed_role", "en", "Tell me the laptop purchase process.", B, "procurement_planning", "laptop procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("ambiguous_mixed_role", "en", "What is the EMD process?", G, "emd_definition", "EMD", ["current_procurement_rules", "procurement_manual"], False)
add("ambiguous_mixed_role", "en", "Should I create a tender or submit a bid?", G, "mixed_role_clarification", "mixed role", ["procurement_manual", "bid_submission_manual"], False)
add("ambiguous_mixed_role", "en", "Corrigendum steps?", G, "corrigendum_policy", "corrigendum", ["current_procurement_rules", "procurement_manual"], False)
add("ambiguous_mixed_role", "hinglish", "Mujhe laptop kharidne ka process batao.", B, "procurement_planning", "laptop procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("ambiguous_mixed_role", "hinglish", "Tender banana hai ya bid bharni hai, kya karu?", G, "mixed_role_clarification", "mixed role", ["procurement_manual", "bid_submission_manual"], False)
add("ambiguous_mixed_role", "hinglish", "EMD ka process short me batao.", G, "emd_definition", "EMD", ["current_procurement_rules", "procurement_manual"], False)
add("ambiguous_mixed_role", "hinglish", "Corrigendum kaise hota hai?", G, "corrigendum_policy", "corrigendum", ["current_procurement_rules", "procurement_manual"], False)
add("ambiguous_mixed_role", "hi", "मुझे प्रिंटर खरीदने की प्रक्रिया बताइए।", B, "procurement_planning", "printer procurement", ["chhattisgarh_store_purchase_rules", "procurement_manual"])
add("ambiguous_mixed_role", "hi", "निविदा बनानी है या बोली जमा करनी है?", G, "mixed_role_clarification", "mixed role", ["procurement_manual", "bid_submission_manual"], False)


def validate():
    assert len(ROWS) == 120, len(ROWS)
    assert Counter(r["bucket"] for r in ROWS) == Counter({
        "department_buyer": 30,
        "vendor_bidder": 30,
        "department_operator": 25,
        "general_information": 25,
        "ambiguous_mixed_role": 10,
    })
    assert Counter(r["language"] for r in ROWS) == Counter({
        "en": 45, "hinglish": 45, "hi": 30,
    })
    assert len({r["query"].casefold() for r in ROWS}) == 120


if __name__ == "__main__":
    validate()
    OUT.write_text(json.dumps(ROWS, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(ROWS)} frozen benchmark rows to {OUT}")
    print("Buckets:", dict(Counter(r["bucket"] for r in ROWS)))
    print("Languages:", dict(Counter(r["language"] for r in ROWS)))
