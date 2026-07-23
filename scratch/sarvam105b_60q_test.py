"""
Sarvam-105b Procurement Chatbot — 60-Question Test Suite (CG e-Procurement)
Tests 20 English, 20 Hindi, 20 Hinglish questions.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os, json, time, re
import httpx
from datetime import datetime
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────
SARVAM_API_KEY  = "sk_fw0t2lcb_pKKcB5MpH17E52wHq8irTrnm"
SARVAM_MODEL    = "sarvam-105b"
SARVAM_URL      = "https://api.sarvam.ai/v1/chat/completions"
OUTPUT_DIR      = Path(__file__).parent.parent / "reports"
OUTPUT_DIR.mkdir(exist_ok=True)

SYSTEM_PROMPT = """You are an expert procurement assistant for the Government of Chhattisgarh, India.

You have deep knowledge of:
- General Financial Rules (GFR) 2017 — especially Rules 147-176 on procurement
- GeM (Government e-Marketplace) guidelines and purchase thresholds
- Chhattisgarh Public Procurement Rules 2018 (CPPR 2018) / Store Purchase Rules (Rule 3.1.1 etc.)
- CHiPS (Chhattisgarh Infotech Promotion Society) e-procurement portal procedures
- Tender types: Open Tender (ATE), Limited Tender Enquiry (LTE), Request for Quotation (RFQ), Single Tender, Two-bid system
- EMD, performance security, AMC, maker-checker division of roles, DSC mapping

CRITICAL RULES:
1. Cite specific GFR rule numbers, CPPR sections, or GeM guidelines for every key claim
2. Give practical, actionable advice specific to Indian government procurement
3. For Hinglish queries (mix of Hindi + English), RESPOND IN HINGLISH. For Hindi queries, respond in Hindi (Devanagari).
4. Be concise and structured; use numbered steps where helpful
"""

# ── Questions ──────────────────────────────────────────────────────────────────
QUESTIONS = [
    # Section A: English Test Questions (20 Items)
    {"id":"A1","section":"Section A: English","lang":"en",
     "query":"What is the mandatory procurement threshold on the GeM portal for CG state departments under Rule 3.1.1?",
     "expected_actor":"Department Buyer","expected_fine_intent":"gem_mandatory_threshold",
     "expected_answer_mode":"direct answer","expected_source_docs":["CPPR 2018", "Rule 3.1.1"],
     "expected_evidence_concepts":["threshold amount", "mandatory GeM purchase"],
     "required_answer_concepts":["mandatory", "GeM", "threshold"],
     "prohibited_claims":["GeM is optional"]},
    {"id":"A2","section":"Section A: English","lang":"en",
     "query":"What are the GFR 2017 tiered limits for direct laptop purchase from GeM without a traditional tender?",
     "expected_actor":"Department Buyer","expected_fine_intent":"gem_direct_purchase_limits",
     "expected_answer_mode":"tiered limits explanation","expected_source_docs":["GFR Rule 149", "GeM Guidelines"],
     "expected_evidence_concepts":["Rs 25,000 direct", "up to Rs 5 Lakh L1", "above 5 Lakh bidding"],
     "required_answer_concepts":["25,000", "5,00,000", "L1", "bidding"],
     "prohibited_claims":["no limits on GeM"]},
    {"id":"A3","section":"Section A: English","lang":"en",
     "query":"How can a department purchase goods from other government-approved agencies under Rule 145?",
     "expected_actor":"Department Buyer","expected_fine_intent":"direct_purchase_rule_145",
     "expected_answer_mode":"procedural guidance","expected_source_docs":["GFR Rule 145"],
     "expected_evidence_concepts":["direct purchase", "competent authority certificate"],
     "required_answer_concepts":["certificate", "competent authority"],
     "prohibited_claims":["tender is mandatory"]},
    {"id":"A4","section":"Section A: English","lang":"en",
     "query":"What is the emergency purchase procedure for materials under GFR Rule 162/166?",
     "expected_actor":"Department Buyer","expected_fine_intent":"emergency_procurement",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["GFR Rule 166", "GFR Rule 162"],
     "expected_evidence_concepts":["emergency declaration", "single tender allowed", "competent authority approval"],
     "required_answer_concepts":["single source", "justification", "competent authority"],
     "prohibited_claims":["emergency means no approval needed"]},
    {"id":"A5","section":"Section A: English","lang":"en",
     "query":"What are the service procurement rules and thresholds for computer AMCs?",
     "expected_actor":"Department Buyer","expected_fine_intent":"service_procurement_amc",
     "expected_answer_mode":"policy explanation","expected_source_docs":["GFR Rule 197-206", "GeM Guidelines"],
     "expected_evidence_concepts":["non-consulting services", "GeM availability", "tender thresholds"],
     "required_answer_concepts":["non-consulting", "GeM", "tender based on value"],
     "prohibited_claims":["AMCs are consulting services"]},
    {"id":"A6","section":"Section A: English","lang":"en",
     "query":"Is it permissible under CVC and GFR guidelines to split a single bulk purchase order into multiple smaller orders?",
     "expected_actor":"Department Buyer","expected_fine_intent":"purchase_splitting_prohibition",
     "expected_answer_mode":"policy prohibition","expected_source_docs":["GFR Rule 161", "CVC guidelines"],
     "expected_evidence_concepts":["splitting prohibited", "bypassing approval limits"],
     "required_answer_concepts":["NO", "splitting is prohibited", "GFR 161"],
     "prohibited_claims":["splitting is allowed"]},
    {"id":"A7","section":"Section A: English","lang":"en",
     "query":"What approvals are required before procuring standard desktop computers for an office?",
     "expected_actor":"Department Buyer","expected_fine_intent":"desktop_procurement_approvals",
     "expected_answer_mode":"checklist","expected_source_docs":["GFR Rule 147", "Delegation of Financial Powers"],
     "expected_evidence_concepts":["administrative approval", "financial sanction", "IT department clearance"],
     "required_answer_concepts":["administrative approval", "financial sanction"],
     "prohibited_claims":["no approval needed for computers"]},
    {"id":"A8","section":"Section A: English","lang":"en",
     "query":"What is the difference between Limited Tender and Open Tender under CG Store Purchase Rules?",
     "expected_actor":"Department Buyer","expected_fine_intent":"lte_vs_open_tender",
     "expected_answer_mode":"comparative guidance","expected_source_docs":["GFR Rule 152", "GFR Rule 153", "CG Store Purchase Rules"],
     "expected_evidence_concepts":["LTE limited vendors", "Open Tender wide advertisement", "value threshold"],
     "required_answer_concepts":["Open tender is public", "Limited tender is sent to selected suppliers"],
     "prohibited_claims":["no difference"]},
    {"id":"A9","section":"Section A: English","lang":"en",
     "query":"When is a department allowed to use the Single Tender method of procurement?",
     "expected_actor":"Department Buyer","expected_fine_intent":"single_tender_justification",
     "expected_answer_mode":"policy explanation","expected_source_docs":["GFR Rule 154"],
     "expected_evidence_concepts":["proprietary item", "emergency", "standardization"],
     "required_answer_concepts":["proprietary", "emergency"],
     "prohibited_claims":["can be used for convenience"]},
    {"id":"A10","section":"Section A: English","lang":"en",
     "query":"How does a Department Operator initiate the 7-step tender creation process on the portal?",
     "expected_actor":"Department Operator","expected_fine_intent":"tender_creation_process",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["login as operator", "tender creation", "NIT", "BOQ", "step-by-step"],
     "required_answer_concepts":["login", "create tender", "fill details"],
     "prohibited_claims":["operator can publish directly"]},
    {"id":"A11","section":"Section A: English","lang":"en",
     "query":"What is the Maker-Checker division of roles for tender publication on the CG portal?",
     "expected_actor":"Department Operator / Publisher","expected_fine_intent":"maker_checker_roles",
     "expected_answer_mode":"role explanation","expected_source_docs":["CHiPS Portal User Guide", "CVC guidelines"],
     "expected_evidence_concepts":["operator makes", "publisher checks and publishes", "separation of duties"],
     "required_answer_concepts":["operator creates", "publisher approves and publishes"],
     "prohibited_claims":["maker can publish"]},
    {"id":"A12","section":"Section A: English","lang":"en",
     "query":"What steps must be followed to issue a Date Extension Corrigendum on the portal?",
     "expected_actor":"Department Operator","expected_fine_intent":"date_extension_corrigendum",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["select tender", "create corrigendum", "date extension type", "publish"],
     "required_answer_concepts":["create corrigendum", "extend date", "publish via approver"],
     "prohibited_claims":["dates can be changed without corrigendum"]},
    {"id":"A13","section":"Section A: English","lang":"en",
     "query":"How do department openers open technical bids and decrypt them?",
     "expected_actor":"Bid Opener","expected_fine_intent":"technical_bid_opening",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["login with DSC", "bid opening", "decrypt", "authorized openers"],
     "required_answer_concepts":["use DSC", "decrypt", "authorized openers"],
     "prohibited_claims":["can be opened by anyone"]},
    {"id":"A14","section":"Section A: English","lang":"en",
     "query":"What are the requirements and timelines for opening price bids on the portal?",
     "expected_actor":"Bid Opener","expected_fine_intent":"price_bid_opening",
     "expected_answer_mode":"procedural guidance","expected_source_docs":["CHiPS Portal User Guide", "GFR 2017"],
     "expected_evidence_concepts":["after technical evaluation", "technically qualified bidders only", "schedule date"],
     "required_answer_concepts":["after technical evaluation", "only for qualified bidders"],
     "prohibited_claims":["open all price bids immediately"]},
    {"id":"A15","section":"Section A: English","lang":"en",
     "query":"How does a Department Admin compile and generate the Bid Evaluation Report?",
     "expected_actor":"Department Admin / Evaluator","expected_fine_intent":"bid_evaluation_report",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["download bids", "evaluate", "upload report", "committee approval"],
     "required_answer_concepts":["evaluate technical details", "upload signed report"],
     "prohibited_claims":["report not needed on portal"]},
    {"id":"A16","section":"Section A: English","lang":"en",
     "query":"What is the online EMD refund timeline and process for unsuccessful bidders?",
     "expected_actor":"Vendor / Department","expected_fine_intent":"emd_refund_process",
     "expected_answer_mode":"policy explanation","expected_source_docs":["CHiPS Portal User Guide", "GFR Rule 170"],
     "expected_evidence_concepts":["auto-refund", "after AOC", "unsuccessful bidders"],
     "required_answer_concepts":["auto refund", "after award of contract"],
     "prohibited_claims":["EMD is never refunded"]},
    {"id":"A17","section":"Section A: English","lang":"en",
     "query":"What options are available to departments for handling L1 bidder EMD refunds?",
     "expected_actor":"Department Finance","expected_fine_intent":"l1_emd_handling",
     "expected_answer_mode":"options explanation","expected_source_docs":["CHiPS Portal User Guide", "GFR Rule 170"],
     "expected_evidence_concepts":["adjust against performance security", "refund after PBG", "forfeit on default"],
     "required_answer_concepts":["refund after performance security", "adjust as security"],
     "prohibited_claims":["L1 EMD is always forfeited"]},
    {"id":"A18","section":"Section A: English","lang":"en",
     "query":"How can a new vendor register on the CG e-Procurement Portal?",
     "expected_actor":"Vendor","expected_fine_intent":"vendor_registration",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["online registration", "DSC class III", "document upload", "fee payment"],
     "required_answer_concepts":["online registration link", "use Class III DSC", "pay fee"],
     "prohibited_claims":["registration is offline only"]},
    {"id":"A19","section":"Section A: English","lang":"en",
     "query":"What documents are mandatory for a new supplier registration?",
     "expected_actor":"Vendor","expected_fine_intent":"vendor_registration_documents",
     "expected_answer_mode":"checklist","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["PAN", "GST", "bank details", "incorporation certificate"],
     "required_answer_concepts":["PAN", "GST"],
     "prohibited_claims":["no documents needed"]},
    {"id":"A20","section":"Section A: English","lang":"en",
     "query":"What is the procedure for mapping a renewed DSC on the vendor portal profile?",
     "expected_actor":"Vendor","expected_fine_intent":"dsc_mapping",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["login", "profile settings", "map new DSC", "Class III"],
     "required_answer_concepts":["login", "update DSC", "token"],
     "prohibited_claims":["DSC mapping not required"]},

    # Section B: Hindi (Devanagari) Test Questions (20 Items)
    {"id":"B21","section":"Section B: Hindi","lang":"hi",
     "query":"छत्तीसगढ़ स्टोर परचेज रूल्स के नियम 3.1.1 के तहत जेम (GeM) से खरीद करने की क्या सीमाएं हैं?",
     "expected_actor":"Department Buyer","expected_fine_intent":"gem_mandatory_threshold",
     "expected_answer_mode":"direct answer","expected_source_docs":["CPPR 2018", "Rule 3.1.1"],
     "expected_evidence_concepts":["GeM availability", "mandatory procurement", "threshold"],
     "required_answer_concepts":["GeM", "अनिवार्य", "सीमा"],
     "prohibited_claims":["GeM वैकल्पिक है"]},
    {"id":"B22","section":"Section B: Hindi","lang":"hi",
     "query":"क्या कोई सरकारी विभाग बिना टेंडर के जेम से सीधे लैपटॉप खरीद सकता है?",
     "expected_actor":"Department Buyer","expected_fine_intent":"gem_direct_purchase",
     "expected_answer_mode":"policy clarification","expected_source_docs":["GFR Rule 149", "GeM Guidelines"],
     "expected_evidence_concepts":["direct purchase up to threshold", "L1 selection"],
     "required_answer_concepts":["हां", "GeM", "सीमा के अंतर्गत", "direct purchase"],
     "prohibited_claims":["टेंडर हमेशा अनिवार्य है"]},
    {"id":"B23","section":"Section B: Hindi","lang":"hi",
     "query":"नियम 145 के तहत एक सरकारी विभाग दूसरे सरकारी विभाग से सीधे सामग्री कैसे खरीद सकता है?",
     "expected_actor":"Department Buyer","expected_fine_intent":"direct_purchase_rule_145",
     "expected_answer_mode":"procedural guidance","expected_source_docs":["GFR Rule 145"],
     "expected_evidence_concepts":["certificate", "competent authority"],
     "required_answer_concepts":["प्रमाणपत्र", "सक्षम अधिकारी"],
     "prohibited_claims":["बिना प्रमाणपत्र के"]},
    {"id":"B24","section":"Section B: Hindi","lang":"hi",
     "query":"आपातकालीन परिस्थितियों में सामग्री की सीधी खरीद के लिए सीवीसी (CVC) और जीएफआर के क्या नियम हैं?",
     "expected_actor":"Department Buyer","expected_fine_intent":"emergency_procurement",
     "expected_answer_mode":"policy explanation","expected_source_docs":["GFR Rule 166", "CVC guidelines"],
     "expected_evidence_concepts":["emergency", "single source", "approval"],
     "required_answer_concepts":["आपातकाल", "एकल निविदा", "अनुमोदन"],
     "prohibited_claims":["आपातकाल में कोई नियम नहीं"]},
    {"id":"B25","section":"Section B: Hindi","lang":"hi",
     "query":"कार्यालय कंप्यूटरों के एएमसी (AMC) के लिए गैर-परामर्श सेवाओं के तहत क्या प्रक्रिया है?",
     "expected_actor":"Department Buyer","expected_fine_intent":"service_procurement_amc",
     "expected_answer_mode":"procedural guidance","expected_source_docs":["GFR Rule 197-206"],
     "expected_evidence_concepts":["non-consulting", "tender", "GeM"],
     "required_answer_concepts":["गैर-परामर्श", "GeM", "निविदा"],
     "prohibited_claims":["AMC हमेशा बिना टेंडर के"]},
    {"id":"B26","section":"Section B: Hindi","lang":"hi",
     "query":"टेंडर अनुमोदन से बचने के लिए बड़ी खरीद को छोटे ऑर्डर्स में विभाजित करना क्यों प्रतिबंधित है?",
     "expected_actor":"Department Buyer","expected_fine_intent":"purchase_splitting_prohibition",
     "expected_answer_mode":"policy prohibition","expected_source_docs":["GFR Rule 161"],
     "expected_evidence_concepts":["splitting prohibited", "GFR 161"],
     "required_answer_concepts":["विभाजित करना प्रतिबंधित है", "GFR 161"],
     "prohibited_claims":["विभाजन की अनुमति है"]},
    {"id":"B27","section":"Section B: Hindi","lang":"hi",
     "query":"निविदा आमंत्रण सूचना (NIT) और बीओक्यू (BOQ) टेम्पलेट अपलोड करने के लिए ऑपरेटर को क्या करना चाहिए?",
     "expected_actor":"Department Operator","expected_fine_intent":"tender_creation_nit_boq",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["login", "upload docs", "BOQ format"],
     "required_answer_concepts":["लॉगिन", "अपलोड", "BOQ"],
     "prohibited_claims":["NIT की जरूरत नहीं"]},
    {"id":"B28","section":"Section B: Hindi","lang":"hi",
     "query":"तकनीकी तुलनात्मक विवरण और वित्तीय तुलनात्मक विवरण में क्या मुख्य अंतर है?",
     "expected_actor":"Evaluation Committee","expected_fine_intent":"technical_vs_financial_evaluation",
     "expected_answer_mode":"comparative guidance","expected_source_docs":["GFR 2017", "CHiPS Portal User Guide"],
     "expected_evidence_concepts":["technical vs price", "L1 criteria"],
     "required_answer_concepts":["तकनीकी", "वित्तीय", "L1"],
     "prohibited_claims":["दोनों समान हैं"]},
    {"id":"B29","section":"Section B: Hindi","lang":"hi",
     "query":"सीवीसी नियमों के अनुसार निविदा प्रक्रिया में पोस्ट-टेंडर वार्ता (Negotiations) कब की जा सकती है?",
     "expected_actor":"Tender Committee","expected_fine_intent":"l1_negotiation",
     "expected_answer_mode":"policy explanation","expected_source_docs":["CVC guidelines", "GFR Rule 175"],
     "expected_evidence_concepts":["only with L1", "exceptional circumstances"],
     "required_answer_concepts":["केवल L1 के साथ", "असाधारण परिस्थिति"],
     "prohibited_claims":["किसी के साथ भी वार्ता कर सकते हैं"]},
    {"id":"B30","section":"Section B: Hindi","lang":"hi",
     "query":"छत्तीसगढ़ ई-प्रोक्योरमेंट पोर्टल पर नया टेंडर बनाने की चरण-दर-चरण प्रक्रिया क्या है?",
     "expected_actor":"Department Operator","expected_fine_intent":"tender_creation_process",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["login", "tender details", "NIT", "BOQ"],
     "required_answer_concepts":["लॉगिन", "विवरण भरें", "प्रकाशित करें"],
     "prohibited_claims":["बिना लॉगिन के हो सकता है"]},
    {"id":"B31","section":"Section B: Hindi","lang":"hi",
     "query":"ऑपरेटर द्वारा तैयार किए गए टेंडर को अप्रूवर/पब्लिशर कैसे अप्रूव और पब्लिश करते हैं?",
     "expected_actor":"Publisher","expected_fine_intent":"maker_checker_publish",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["login as publisher", "verify", "DSC", "publish"],
     "required_answer_concepts":["लॉगिन", "DSC", "प्रकाशित"],
     "prohibited_claims":["ऑपरेटर खुद प्रकाशित कर सकता है"]},
    {"id":"B32","section":"Section B: Hindi","lang":"hi",
     "query":"टेंडर की अंतिम तिथि बढ़ाने के लिए कॉरिजेंडम (शुद्धिपत्र) जारी करने की क्या प्रक्रिया है?",
     "expected_actor":"Department Operator","expected_fine_intent":"date_extension_corrigendum",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["corrigendum module", "date extension", "publish"],
     "required_answer_concepts":["शुद्धिपत्र", "तिथि बढ़ाना", "प्रकाशित"],
     "prohibited_claims":["बिना शुद्धिपत्र के तिथि बदल सकते हैं"]},
    {"id":"B33","section":"Section B: Hindi","lang":"hi",
     "query":"तकनीकी निविदा को खोलने के लिए कितने अधिकृत ओपनर्स की आवश्यकता होती है?",
     "expected_actor":"Bid Opener","expected_fine_intent":"technical_bid_opening",
     "expected_answer_mode":"direct answer","expected_source_docs":["CHiPS Portal User Guide", "GFR 2017"],
     "expected_evidence_concepts":["minimum two openers", "DSC required"],
     "required_answer_concepts":["कम से कम दो", "DSC"],
     "prohibited_claims":["एक ओपनर काफी है"]},
    {"id":"B34","section":"Section B: Hindi","lang":"hi",
     "query":"प्राइस बिड ओपनिंग के समय पात्र बोलीदाताओं को ईमेल/एसएमएस भेजने की क्या व्यवस्था है?",
     "expected_actor":"Department Admin","expected_fine_intent":"price_bid_opening_notification",
     "expected_answer_mode":"system feature explanation","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["auto SMS/email", "portal feature"],
     "required_answer_concepts":["स्वत: ईमेल", "एसएमएस"],
     "prohibited_claims":["मैनुअल ईमेल भेजना होता है"]},
    {"id":"B35","section":"Section B: Hindi","lang":"hi",
     "query":"मूल्यांकन समिति द्वारा हस्ताक्षरित बिड इवैल्यूएशन रिपोर्ट को पोर्टल पर कैसे अपलोड किया जाता है?",
     "expected_actor":"Department Evaluator","expected_fine_intent":"bid_evaluation_report",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["upload pdf", "evaluation section"],
     "required_answer_concepts":["अपलोड", "मूल्यांकन रिपोर्ट"],
     "prohibited_claims":["अपलोड करने की आवश्यकता नहीं"]},
    {"id":"B36","section":"Section B: Hindi","lang":"hi",
     "query":"असफल बोलीदाताओं की ईएमडी (EMD) ऑनलाइन रिफंड होने में कितने दिन का समय लगता है?",
     "expected_actor":"Vendor / Department","expected_fine_intent":"emd_refund_process",
     "expected_answer_mode":"timeline explanation","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["auto refund after AOC", "bank processing time"],
     "required_answer_concepts":["AOC के बाद", "ऑनलाइन रिफंड"],
     "prohibited_claims":["मैनुअल चेक भेजा जाता है"]},
    {"id":"B37","section":"Section B: Hindi","lang":"hi",
     "query":"एल-1 बोलीदाता की ईएमडी को विभाग के खाते में जमा करने या वापस करने की क्या शर्तें हैं?",
     "expected_actor":"Department Finance","expected_fine_intent":"l1_emd_handling",
     "expected_answer_mode":"policy explanation","expected_source_docs":["CHiPS Portal User Guide", "GFR 2017"],
     "expected_evidence_concepts":["PBG receipt", "adjust against PBG"],
     "required_answer_concepts":["परफॉरमेंस सिक्योरिटी", "वापस करना"],
     "prohibited_claims":["हमेशा जब्त कर ली जाती है"]},
    {"id":"B38","section":"Section B: Hindi","lang":"hi",
     "query":"नए विक्रेता (Vendor) पंजीकरण के लिए कौन-कौन से दस्तावेज अनिवार्य हैं?",
     "expected_actor":"Vendor","expected_fine_intent":"vendor_registration_documents",
     "expected_answer_mode":"checklist","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["PAN", "GSTIN", "Bank Details"],
     "required_answer_concepts":["पैन", "जीएसटी"],
     "prohibited_claims":["दस्तावेज़ अनिवार्य नहीं हैं"]},
    {"id":"B39","section":"Section B: Hindi","lang":"hi",
     "query":"यदि कोई विक्रेता अपना पासवर्ड भूल जाता है तो पासवर्ड रिसेट करने की क्या प्रक्रिया है?",
     "expected_actor":"Vendor","expected_fine_intent":"vendor_password_reset",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["forgot password link", "OTP", "security questions"],
     "required_answer_concepts":["फॉरगॉट पासवर्ड", "ओटीपी"],
     "prohibited_claims":["नया अकाउंट बनाना होगा"]},
    {"id":"B40","section":"Section B: Hindi","lang":"hi",
     "query":"नवीनीकृत डिजिटल सिग्नेचर सर्टिफिकेट (Class-III DSC) को पोर्टल पर कैसे मैप किया जाता है?",
     "expected_actor":"Vendor","expected_fine_intent":"dsc_mapping",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["login", "profile", "update DSC"],
     "required_answer_concepts":["लॉगिन", "DSC अपडेट"],
     "prohibited_claims":["DSC मैपिंग जरूरी नहीं"]},

    # Section C: Hinglish (Roman Hindi) Test Questions (20 Items)
    {"id":"C41","section":"Section C: Hinglish","lang":"hi",
     "query":"Office laptops direct GeM portal se purchase karne ke liye kya thresholds hain?",
     "expected_actor":"Department Buyer","expected_fine_intent":"gem_direct_purchase_limits",
     "expected_answer_mode":"tiered limits explanation","expected_source_docs":["GFR Rule 149", "GeM Guidelines"],
     "expected_evidence_concepts":["Rs 25,000", "L1 up to 5 Lakh", "bidding above 5 Lakh"],
     "required_answer_concepts":["25,000", "5 lakh", "L1"],
     "prohibited_claims":["no limits"]},
    {"id":"C42","section":"Section C: Hinglish","lang":"hi",
     "query":"Kya department bina tender nikale GeM se computer directly kharid sakta hai?",
     "expected_actor":"Department Buyer","expected_fine_intent":"gem_direct_purchase",
     "expected_answer_mode":"policy clarification","expected_source_docs":["GFR Rule 149"],
     "expected_evidence_concepts":["yes within limits", "25000 direct", "5 lakh L1"],
     "required_answer_concepts":["haan", "limit ke andar"],
     "prohibited_claims":["nahi, tender is always mandatory"]},
    {"id":"C43","section":"Section C: Hinglish","lang":"hi",
     "query":"Rule 145 ke under inter-departmental purchase direct procurement kaise ki jati hai?",
     "expected_actor":"Department Buyer","expected_fine_intent":"direct_purchase_rule_145",
     "expected_answer_mode":"procedural guidance","expected_source_docs":["GFR Rule 145"],
     "expected_evidence_concepts":["certificate", "competent authority"],
     "required_answer_concepts":["certificate", "competent authority approval"],
     "prohibited_claims":["tender required"]},
    {"id":"C44","section":"Section C: Hinglish","lang":"hi",
     "query":"Emergency situation me direct purchase karne ke liye GFR me kya rule hai?",
     "expected_actor":"Department Buyer","expected_fine_intent":"emergency_procurement",
     "expected_answer_mode":"policy explanation","expected_source_docs":["GFR Rule 166", "GFR Rule 162"],
     "expected_evidence_concepts":["single source", "emergency declaration", "approval"],
     "required_answer_concepts":["GFR 166", "single tender", "justification"],
     "prohibited_claims":["no approval needed in emergency"]},
    {"id":"C45","section":"Section C: Hinglish","lang":"hi",
     "query":"Computers ka AMC karne ke liye limited tender ya open tender kab karna hoga?",
     "expected_actor":"Department Buyer","expected_fine_intent":"service_procurement_amc",
     "expected_answer_mode":"threshold explanation","expected_source_docs":["GFR Rule 197-206"],
     "expected_evidence_concepts":["value threshold", "LTE vs Open Tender"],
     "required_answer_concepts":["estimated value pe depend karta hai", "25 lakh threshold"],
     "prohibited_claims":["always open tender"]},
    {"id":"C46","section":"Section C: Hinglish","lang":"hi",
     "query":"Kya hum higher approval se bachne ke liye order split karke small purchases kar sakte hain?",
     "expected_actor":"Department Buyer","expected_fine_intent":"purchase_splitting_prohibition",
     "expected_answer_mode":"policy prohibition","expected_source_docs":["GFR Rule 161"],
     "expected_evidence_concepts":["splitting prohibited", "GFR 161"],
     "required_answer_concepts":["nahi", "splitting prohibited hai", "GFR 161"],
     "prohibited_claims":["haan kar sakte hain"]},
    {"id":"C47","section":"Section C: Hinglish","lang":"hi",
     "query":"Department operator ko portal par new tender creation wizard kaise start karna hoga?",
     "expected_actor":"Department Operator","expected_fine_intent":"tender_creation_process",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["login", "dashboard", "create tender"],
     "required_answer_concepts":["login as operator", "create tender button"],
     "prohibited_claims":["operator cannot create tender"]},
    {"id":"C48","section":"Section C: Hinglish","lang":"hi",
     "query":"Maker-checker rules ke according operator directly tender publish kyu nahi kar sakta?",
     "expected_actor":"Department Operator / Publisher","expected_fine_intent":"maker_checker_roles",
     "expected_answer_mode":"role explanation","expected_source_docs":["CVC guidelines", "CHiPS Portal User Guide"],
     "expected_evidence_concepts":["separation of duties", "accountability"],
     "required_answer_concepts":["maker and checker alag hone chahiye", "transparency"],
     "prohibited_claims":["operator can publish"]},
    {"id":"C49","section":"Section C: Hinglish","lang":"hi",
     "query":"Tender ki last submission date extend karne ke liye corrigendum kaise initiate kare?",
     "expected_actor":"Department Operator","expected_fine_intent":"date_extension_corrigendum",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["corrigendum option", "date extension"],
     "required_answer_concepts":["corrigendum menu", "date extend"],
     "prohibited_claims":["without corrigendum date change"]},
    {"id":"C50","section":"Section C: Hinglish","lang":"hi",
     "query":"Due date change corrigendum ko approver Class-III DSC se kaise publish karega?",
     "expected_actor":"Publisher","expected_fine_intent":"corrigendum_publish",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["login as publisher", "verify corrigendum", "DSC pin", "publish"],
     "required_answer_concepts":["login", "DSC use karke", "publish"],
     "prohibited_claims":["publish bina DSC ke ho sakta hai"]},
    {"id":"C51","section":"Section C: Hinglish","lang":"hi",
     "query":"Technical bid open karne ke liye open ka physical DSC tokens mapping mandatory hai kya?",
     "expected_actor":"Bid Opener","expected_fine_intent":"technical_bid_opening_dsc",
     "expected_answer_mode":"policy confirmation","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["DSC mandatory for decryption"],
     "required_answer_concepts":["haan", "DSC token mandatory hai", "decryption ke liye"],
     "prohibited_claims":["bina DSC ke open kar sakte hain"]},
    {"id":"C52","section":"Section C: Hinglish","lang":"hi",
     "query":"Price bid opening kab aur kis state ke approval ke baad active hoti hai?",
     "expected_actor":"Bid Opener","expected_fine_intent":"price_bid_opening",
     "expected_answer_mode":"procedural guidance","expected_source_docs":["CHiPS Portal User Guide", "GFR 2017"],
     "expected_evidence_concepts":["after technical evaluation", "technical committee approval"],
     "required_answer_concepts":["technical evaluation ke baad", "approval ke baad"],
     "prohibited_claims":["technical se pehle open kar sakte hain"]},
    {"id":"C53","section":"Section C: Hinglish","lang":"hi",
     "query":"Unsuccessful bidders ki online EMD auto-refund account me kitne din me credit hoti hai?",
     "expected_actor":"Vendor","expected_fine_intent":"emd_refund_process",
     "expected_answer_mode":"timeline explanation","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["auto refund after AOC", "bank time"],
     "required_answer_concepts":["AOC issue hone ke baad", "kuch dino me"],
     "prohibited_claims":["refund nahi hoti"]},
    {"id":"C54","section":"Section C: Hinglish","lang":"hi",
     "query":"L1 bidder ki EMD ko performance security deposit me adjust karne ka kya option hai?",
     "expected_actor":"Department Finance","expected_fine_intent":"l1_emd_handling",
     "expected_answer_mode":"options explanation","expected_source_docs":["GFR Rule 170", "CHiPS Portal User Guide"],
     "expected_evidence_concepts":["withholding EMD", "adjust against PBG"],
     "required_answer_concepts":["performance security me adjust kar sakte hain", "AOC ke time"],
     "prohibited_claims":["adjust nahi kar sakte"]},
    {"id":"C55","section":"Section C: Hinglish","lang":"hi",
     "query":"Evaluation committee members final bid evaluation report draft kaise download karte hain?",
     "expected_actor":"Evaluation Committee","expected_fine_intent":"bid_evaluation_report",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["evaluation tab", "download report"],
     "required_answer_concepts":["portal par login karke", "download section se"],
     "prohibited_claims":["report physical only"]},
    {"id":"C56","section":"Section C: Hinglish","lang":"hi",
     "query":"New supplier registration portal profile create karne ke liye kya documentation chahiye?",
     "expected_actor":"Vendor","expected_fine_intent":"vendor_registration_documents",
     "expected_answer_mode":"checklist","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["PAN", "GSTIN", "Bank Details"],
     "required_answer_concepts":["PAN", "GST"],
     "prohibited_claims":["no documents required"]},
    {"id":"C57","section":"Section C: Hinglish","lang":"hi",
     "query":"Vendor password reset karne ke liye security questions ka use kaise kiya jata hai?",
     "expected_actor":"Vendor","expected_fine_intent":"vendor_password_reset",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["forgot password", "security question answer", "OTP"],
     "required_answer_concepts":["forgot password link", "security question ka answer deke"],
     "prohibited_claims":["admin ko mail karna padega"]},
    {"id":"C58","section":"Section C: Hinglish","lang":"hi",
     "query":"Renewed Class-III DSC token portal account profile pe map kaise kare?",
     "expected_actor":"Vendor","expected_fine_intent":"dsc_mapping",
     "expected_answer_mode":"step-by-step guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["login", "profile settings", "map DSC"],
     "required_answer_concepts":["login karke", "update DSC"],
     "prohibited_claims":["mapping not needed"]},
    {"id":"C59","section":"Section C: Hinglish","lang":"hi",
     "query":"Kya MSMEs ya startups ko e-procurement tender participate karne me EMD exemption milta hai?",
     "expected_actor":"Vendor","expected_fine_intent":"startup_exemption",
     "expected_answer_mode":"policy confirmation","expected_source_docs":["GFR Rule 170", "Public Procurement Policy for MSEs"],
     "expected_evidence_concepts":["EMD exemption for MSME/Startup", "registration certificate"],
     "required_answer_concepts":["haan", "exemption milta hai", "certificate upload karna hoga"],
     "prohibited_claims":["koi exemption nahi hai"]},
    {"id":"C60","section":"Section C: Hinglish","lang":"hi",
     "query":"EMD payment online cut hone ke baad agar receipt na mile toh bank transaction ticket kaise check kare?",
     "expected_actor":"Vendor","expected_fine_intent":"emd_payment_portal_issue",
     "expected_answer_mode":"troubleshooting guidance","expected_source_docs":["CHiPS Portal User Guide"],
     "expected_evidence_concepts":["check payment status", "contact helpdesk", "transaction reference"],
     "required_answer_concepts":["payment status check kare", "helpdesk ko contact kare", "reference number"],
     "prohibited_claims":["payment dobara kare without checking"]},
]


# ── Sarvam API Call ────────────────────────────────────────────────────────────
def call_sarvam(user_message: str) -> dict:
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "model": SARVAM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        "temperature": 0.0,
        "max_tokens": 4000,
        "budget_tokens": 600,
        "stream": False,
    }
    t0 = time.monotonic()
    try:
        resp = httpx.post(SARVAM_URL, headers=headers, json=payload, timeout=180)
        elapsed = round(time.monotonic() - t0, 2)
        if resp.status_code == 200:
            data = resp.json()
            msg = data["choices"][0]["message"]
            content   = (msg.get("content") or "").strip()
            reasoning = (msg.get("reasoning_content") or "").strip()
            finish    = data["choices"][0].get("finish_reason", "unknown")
            return {
                "status": "ok", "answer": content, "reasoning_chain": reasoning,
                "finish_reason": finish, "elapsed_s": elapsed, "model": data.get("model", SARVAM_MODEL),
                "usage": data.get("usage", {}), "http_status": 200,
            }
        else:
            return {"status": "error", "answer": f"HTTP {resp.status_code}: {resp.text[:400]}", "reasoning_chain": "", "finish_reason": "error", "elapsed_s": elapsed, "model": SARVAM_MODEL, "http_status": resp.status_code}
    except Exception as e:
        return {"status": "error", "answer": f"Exception: {e}", "reasoning_chain": "", "finish_reason": "exception", "elapsed_s": round(time.monotonic() - t0, 2), "model": SARVAM_MODEL, "http_status": 0}

# ── Evaluation Helpers ─────────────────────────────────────────────────────────
def check_citations(answer: str, expected_docs: list) -> dict:
    al = answer.lower()
    found, missing = [], []
    for doc in expected_docs:
        kws = [w for w in re.split(r'[\s/&()]+', doc.lower()) if len(w) > 3]
        if kws and any(k in al for k in kws): found.append(doc)
        else: missing.append(doc)
    score = round(len(found) / len(expected_docs), 2) if expected_docs else 1.0
    return {"found": found, "missing": missing, "score": score}

def check_concepts(answer: str, required: list) -> dict:
    al = answer.lower()
    covered, missing = [], []
    for concept in required:
        kws = [w for w in re.split(r'[\s,]+', concept.lower()) if len(w) > 3]
        hits = sum(1 for k in kws if k in al)
        if kws and hits >= max(1, len(kws) // 2): covered.append(concept)
        elif not kws and concept.lower() in al: covered.append(concept)
        else: missing.append(concept)
    score = round(len(covered) / len(required), 2) if required else 1.0
    return {"covered": covered, "missing": missing, "score": score}

def check_prohibited(answer: str, prohibited: list) -> dict:
    al = answer.lower()
    violations = []
    for claim in prohibited:
        kws = [w for w in re.split(r'[\s,]+', claim.lower()) if len(w) > 3]
        hits = sum(1 for k in kws if k in al)
        if kws and hits >= max(1, len(kws) * 2 // 3): violations.append(claim)
    return {"violations": violations, "safe": len(violations) == 0}

def grade(citation: dict, concepts: dict, prohibited: dict) -> str:
    if not prohibited["safe"]: return "FAIL"
    score = citation["score"] * 0.35 + concepts["score"] * 0.65
    if score >= 0.70: return "PASS"
    if score >= 0.40: return "PARTIAL"
    return "FAIL"

# ── Build prompt ───────────────────────────────────────────────────────────────
def build_prompt(q: dict) -> str:
    sources = ", ".join(q["expected_source_docs"])
    return f"Question: {q['query']}\n\n[Regulatory context relevant to this question: {sources}]\n\nPlease answer clearly, citing specific GFR rule numbers, GeM guidelines, or CPPR 2018 sections where applicable."

# ── Run tests ──────────────────────────────────────────────────────────────────
def run():
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = OUTPUT_DIR / f"sarvam105b_60q_test_{ts_str}.json"
    md_path   = OUTPUT_DIR / f"sarvam105b_60q_test_{ts_str}.md"

    print(f"\n{'='*70}")
    print(f"  SARVAM-{SARVAM_MODEL.upper()} 60-Q PROCUREMENT TEST")
    print(f"  Questions : {len(QUESTIONS)}")
    print(f"  Started   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    results, pass_c, partial_c, fail_c = [], 0, 0, 0
    total_time = 0.0

    for i, q in enumerate(QUESTIONS, 1):
        short_q = q["query"][:60] + ("..." if len(q["query"]) > 60 else "")
        print(f"[{i:02d}/{len(QUESTIONS)}] {q['id']} | {short_q}")

        api = call_sarvam(build_prompt(q))
        answer = api["answer"]
        elapsed = api["elapsed_s"]
        total_time += elapsed

        citation  = check_citations(answer, q["expected_source_docs"])
        concepts  = check_concepts(answer, q["required_answer_concepts"])
        prohibited = check_prohibited(answer, q["prohibited_claims"])
        g = grade(citation, concepts, prohibited)

        if g == "PASS": pass_c += 1; sym = "PASS   "
        elif g == "PARTIAL": partial_c += 1; sym = "PARTIAL"
        else: fail_c += 1; sym = "FAIL   "

        print(f"         {sym} | {elapsed}s | cite:{citation['score']} | concept:{concepts['score']} | safe:{prohibited['safe']} | finish:{api['finish_reason']}")

        rec = {
            "id": q["id"], "section": q["section"], "query": q["query"], "language": q["lang"],
            "expected_actor": q["expected_actor"], "expected_fine_intent": q["expected_fine_intent"],
            "expected_answer_mode": q["expected_answer_mode"], "expected_source_docs": q["expected_source_docs"],
            "expected_evidence_concepts": q["expected_evidence_concepts"], "required_answer_concepts": q["required_answer_concepts"],
            "prohibited_claims": q["prohibited_claims"], "retrieved_top10_sources": ["[direct API mode – no live Qdrant RAG]"],
            "final_context_sources": q["expected_source_docs"], "final_answer": answer,
            "reasoning_chain_preview": api["reasoning_chain"][:500], "reasoning_chain_full": api["reasoning_chain"],
            "finish_reason": api["finish_reason"], "citation_correctness": citation, "concepts_coverage": concepts,
            "prohibited_check": prohibited, "response_time_s": elapsed, "grade": g, "api_status": api["status"],
            "model_used": api.get("model", SARVAM_MODEL), "token_usage": api.get("usage", {})
        }
        results.append(rec)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"summary": {"done_so_far": i, "total": len(QUESTIONS)}, "results": results}, f, ensure_ascii=False, indent=2)

    summary = {
        "total": len(QUESTIONS), "pass": pass_c, "partial": partial_c, "fail": fail_c,
        "pass_rate": round(pass_c/len(QUESTIONS)*100, 1), "partial_rate": round(partial_c/len(QUESTIONS)*100, 1),
        "fail_rate": round(fail_c/len(QUESTIONS)*100, 1), "avg_response_time_s": round(total_time/len(QUESTIONS), 2),
        "total_time_s": round(total_time, 2), "model": SARVAM_MODEL, "timestamp": datetime.now().isoformat(),
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, ensure_ascii=False, indent=2)

    md = build_md_report(results, summary)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\n{'='*70}\n  PASS={pass_c} | PARTIAL={partial_c} | FAIL={fail_c}\n  JSON : {json_path}\n  MD   : {md_path}\n{'='*70}\n")

def build_md_report(results: list, summary: dict) -> str:
    ts = datetime.fromisoformat(summary["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    sec_stats = {}
    for r in results:
        s = r["section"]
        sec_stats.setdefault(s, {"pass":0,"partial":0,"fail":0,"total":0,"time":[]})
        sec_stats[s]["total"] += 1
        sec_stats[s][r["grade"].lower()] += 1
        sec_stats[s]["time"].append(r["response_time_s"])

    md = f"# Sarvam-105B Procurement Chatbot — 60-Question Test Report\n\n**Generated:** {ts}  \n**Model:** `{summary['model']}`  \n**Total Questions:** {summary['total']}\n\n---\n\n## Executive Summary\n\n| Metric | Value |\n|--------|-------|\n| PASS | **{summary['pass']} ({summary['pass_rate']}%)** |\n| FAIL | **{summary['fail']} ({summary['fail_rate']}%)** |\n| Avg Response Time | **{summary['avg_response_time_s']}s per question** |\n\n### Section-Wise Performance\n\n| Section | Total | PASS | PARTIAL | FAIL | Avg Time |\n|---------|-------|------|---------|------|----------|\n"
    for sec, st in sec_stats.items():
        avg_t = round(sum(st["time"])/len(st["time"]), 1) if st["time"] else 0
        md += f"| {sec} | {st['total']} | {st['pass']} | {st['partial']} | {st['fail']} | {avg_t}s |\n"

    md += "\n---\n\n## Detailed Results Per Question\n\n"
    cur_section = None
    for r in results:
        if r["section"] != cur_section:
            cur_section = r["section"]
            md += f"\n---\n### {cur_section}\n\n"
        g_sym = r["grade"]
        md += f"#### [{r['id']}] {g_sym} — {r['query']}\n\n| Field | Value |\n|-------|-------|\n| **Grade** | **{r['grade']}** |\n| Response Time | {r['response_time_s']}s |\n| Citation Score | {r['citation_correctness']['score']} |\n| Concept Coverage | {r['concepts_coverage']['score']} |\n| Safety | {'Safe' if r['prohibited_check']['safe'] else 'VIOLATION DETECTED'} |\n\n**Full Final Answer:**\n\n{r['final_answer'] if r['final_answer'] else '_[EMPTY]_'}\n\n"
        if not r["prohibited_check"]["safe"]: md += f"**PROHIBITED CLAIM DETECTED:** `{', '.join(r['prohibited_check']['violations'])}`\n\n"
        if r.get("reasoning_chain_preview"): md += f"**Reasoning Preview:** _{r['reasoning_chain_preview'][:300].replace(chr(10), ' ')}_\n\n"
    return md

if __name__ == "__main__":
    run()
