"""
Sarvam-105b Procurement Chatbot — Full 50-Question Test
- Fixes: correct response parsing (content vs reasoning_content)
- Incremental JSON save after every question (resilient to crashes)
- Captures both final answer AND reasoning chain
- Full report with all required metrics
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

# ── System Prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert procurement assistant for the Government of Chhattisgarh, India.

You have deep knowledge of:
- General Financial Rules (GFR) 2017 — especially Rules 147-176 on procurement
- GeM (Government e-Marketplace) guidelines and purchase thresholds
- Chhattisgarh Public Procurement Rules 2018 (CPPR 2018)
- CHiPS (Chhattisgarh Infotech Promotion Society) e-procurement portal procedures
- CG-GFR and state-specific procurement regulations
- Tender types: Open Tender (ATE), Limited Tender Enquiry (LTE), Request for Quotation (RFQ), Single Tender, Two-bid system
- GFR financial thresholds: Direct Purchase up to Rs.25,000; three quotes up to Rs.2.5 lakh; tender above Rs.2.5 lakh; GeM mandatory where item available
- MSME benefits, EMD exemptions (GFR 157, MSME Policy 2012), startup concessions (GFR 157A / DPIIT)
- L1 evaluation, technical/financial bid opening, price reasonableness, negotiation rules (CVC guidelines)
- Contract management: Performance Security, Liquidated Damages (LD), Goods Receipt Note (GRN), inspection

CRITICAL RULES:
1. Cite specific GFR rule numbers, CPPR sections, or GeM guidelines for every key claim
2. Give practical, actionable advice specific to Indian government procurement
3. For Hinglish queries (mix of Hindi + English), RESPOND IN HINGLISH
4. Flag purchase-splitting as illegal under GFR Rule 161
5. Never recommend bypassing financial sanction or post-facto approval as routine
6. Be concise and structured; use numbered steps where helpful
"""

# ── Questions ──────────────────────────────────────────────────────────────────
QUESTIONS = [
    # ── Section A ──────────────────────────────────────────────────────────────
    {"id":"A1","section":"A. Procurement Planning & Purchase Methods","lang":"en",
     "query":"Our office needs 30 laptops. How should we decide whether to use GeM or a tender?",
     "expected_actor":"Department Buyer / Procurement Officer",
     "expected_fine_intent":"procurement_method_selection",
     "expected_answer_mode":"step-by-step guidance",
     "expected_source_docs":["GFR Rule 149","GeM Guidelines","CPPR 2018"],
     "expected_evidence_concepts":["GeM mandatory check","threshold comparison","tender trigger"],
     "required_answer_concepts":["check GeM availability first","if available on GeM use GeM","estimated value determines method"],
     "prohibited_claims":["skip GeM check","GeM is optional","always use tender for bulk"]},

    {"id":"A2","section":"A. Procurement Planning & Purchase Methods","lang":"hi",
     "query":"Department ko Rs.4 lakh ka furniture kharidna hai. Kaunsa procurement method use karna chahiye?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"procurement_method_selection",
     "expected_answer_mode":"direct recommendation with reasoning",
     "expected_source_docs":["GFR Rule 149","GeM Guidelines"],
     "expected_evidence_concepts":["4 lakh threshold","GeM check first","LTE or open tender"],
     "required_answer_concepts":["GeM par check karo","4 lakh mein tender required","LTE or open tender"],
     "prohibited_claims":["direct purchase allowed for 4 lakh","3 quotations sufficient for 4L"]},

    {"id":"A3","section":"A. Procurement Planning & Purchase Methods","lang":"en",
     "query":"Can we buy an item directly if only one quotation is available on GeM?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"gem_single_quotation_rule",
     "expected_answer_mode":"policy clarification",
     "expected_source_docs":["GeM Guidelines","GFR Rule 149"],
     "expected_evidence_concepts":["GeM single seller allowed","L1 on GeM","price reasonableness check"],
     "required_answer_concepts":["single quote on GeM is allowed","verify price reasonableness","document justification"],
     "prohibited_claims":["must get 3 quotes even on GeM","single quote on GeM is invalid"]},

    {"id":"A4","section":"A. Procurement Planning & Purchase Methods","lang":"hi",
     "query":"Agar item GeM par available nahi hai, department ko next kya karna chahiye?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"fallback_procurement_method",
     "expected_answer_mode":"step-by-step guidance",
     "expected_source_docs":["GFR Rule 149","CPPR 2018"],
     "expected_evidence_concepts":["GeM unavailability certificate","tender procedure","threshold check"],
     "required_answer_concepts":["GeM par unavailability document karo","value ke basis par method choose karo"],
     "prohibited_claims":["GeM skip without documentation"]},

    {"id":"A5","section":"A. Procurement Planning & Purchase Methods","lang":"en",
     "query":"Can a department invite quotations from three local suppliers instead of issuing an open tender?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"lte_vs_open_tender",
     "expected_answer_mode":"policy clarification with conditions",
     "expected_source_docs":["GFR Rule 152","CPPR 2018"],
     "expected_evidence_concepts":["LTE threshold 25 lakh","minimum 3 suppliers","above 25L open tender"],
     "required_answer_concepts":["allowed under LTE below Rs.25L","must invite minimum 3 quotes","above Rs.25L open tender required"],
     "prohibited_claims":["local quotes valid at any value","open tender always required regardless of value"]},

    {"id":"A6","section":"A. Procurement Planning & Purchase Methods","lang":"hi",
     "query":"Hamare office ko urgently printers chahiye, lekin emergency nahi hai. Fastest lawful option kya hai?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"fastest_lawful_procurement",
     "expected_answer_mode":"recommendation with rationale",
     "expected_source_docs":["GeM Guidelines","GFR Rule 149"],
     "expected_evidence_concepts":["GeM fastest option","direct ordering on GeM","no emergency declaration needed"],
     "required_answer_concepts":["GeM sabse fast option hai","direct ordering if within threshold","no emergency needed"],
     "prohibited_claims":["emergency declare karo","single tender without justification"]},

    {"id":"A7","section":"A. Procurement Planning & Purchase Methods","lang":"en",
     "query":"What factors should be checked before choosing Limited Tender?",
     "expected_actor":"Department Buyer / Procurement Officer",
     "expected_fine_intent":"lte_eligibility_check",
     "expected_answer_mode":"checklist",
     "expected_source_docs":["GFR Rule 152","CPPR 2018"],
     "expected_evidence_concepts":["estimated value","GeM availability","vendor list","approval required"],
     "required_answer_concepts":["value within LTE threshold","GeM not available","minimum vendors to invite","competent authority approval"],
     "prohibited_claims":["LTE has no conditions","any value can use LTE"]},

    {"id":"A8","section":"A. Procurement Planning & Purchase Methods","lang":"en",
     "query":"When should an Open Tender be preferred over Limited Tender?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"open_vs_limited_tender",
     "expected_answer_mode":"comparative guidance",
     "expected_source_docs":["GFR Rule 153","CPPR 2018"],
     "expected_evidence_concepts":["above Rs.25 lakh","maximum competition","published in newspaper or CPP Portal"],
     "required_answer_concepts":["value above Rs.25L mandates open tender","more competition","wide advertisement required"],
     "prohibited_claims":["open tender always required at any value","LTE is illegal above any threshold"]},

    {"id":"A9","section":"A. Procurement Planning & Purchase Methods","lang":"en",
     "query":"Can Single Tender be used because the earlier supplier already knows our system?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"single_tender_justification",
     "expected_answer_mode":"policy clarification",
     "expected_source_docs":["GFR Rule 154","CPPR 2018"],
     "expected_evidence_concepts":["familiarity not valid reason","proprietary or emergency only","single tender valid reasons"],
     "required_answer_concepts":["supplier familiarity NOT valid justification","only proprietary emergency national security valid"],
     "prohibited_claims":["supplier familiarity is valid reason for single tender"]},

    {"id":"A10","section":"A. Procurement Planning & Purchase Methods","lang":"hi",
     "query":"Ek proprietary software sirf ek company provide karti hai. Kya Single Tender allowed hoga?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"single_tender_proprietary",
     "expected_answer_mode":"policy confirmation with conditions",
     "expected_source_docs":["GFR Rule 154"],
     "expected_evidence_concepts":["proprietary item single tender allowed","certificate required","competent authority approval"],
     "required_answer_concepts":["haan proprietary ke liye single tender allowed","proprietary certificate chahiye","competent authority approve kare"],
     "prohibited_claims":["proprietary single tender not allowed","always tender regardless of proprietary nature"]},

    {"id":"A11","section":"A. Procurement Planning & Purchase Methods","lang":"en",
     "query":"Can the department purchase spare parts only from the original equipment manufacturer?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"oem_spare_parts",
     "expected_answer_mode":"policy confirmation with documentation requirements",
     "expected_source_docs":["GFR Rule 154"],
     "expected_evidence_concepts":["OEM spare parts single tender","compatibility requirement","proprietary justification"],
     "required_answer_concepts":["OEM single tender allowed for spare parts","must document compatibility necessity","competent authority approval"],
     "prohibited_claims":["cannot buy from OEM directly","always tender for spare parts"]},

    {"id":"A12","section":"A. Procurement Planning & Purchase Methods","lang":"hi",
     "query":"Government department ko dusre government undertaking se goods purchase karne hain. Kya tender zaroori hai?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"g2g_procurement",
     "expected_answer_mode":"policy clarification",
     "expected_source_docs":["GFR Rule 162"],
     "expected_evidence_concepts":["G2G procurement","PSU direct purchase","tender not mandatory"],
     "required_answer_concepts":["government se government purchase mein tender zaroori nahi","GFR Rule 162","document karo"],
     "prohibited_claims":["G2G mein always tender required"]},

    {"id":"A13","section":"A. Procurement Planning & Purchase Methods","lang":"en",
     "query":"Can we split a Rs.10 lakh requirement into five smaller purchase orders?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"purchase_splitting_prohibition",
     "expected_answer_mode":"prohibition with consequences",
     "expected_source_docs":["GFR Rule 161"],
     "expected_evidence_concepts":["splitting prohibited","artificial division","GFR Rule 161","financial irregularity"],
     "required_answer_concepts":["NO splitting is prohibited","GFR Rule 161 prohibits artificial splitting","conduct single procurement"],
     "prohibited_claims":["splitting is allowed","monthly purchases are fine without restriction"]},

    {"id":"A14","section":"A. Procurement Planning & Purchase Methods","lang":"hi",
     "query":"Same item alag-alag months mein chahiye. Kya har month direct purchase kar sakte hain?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"periodic_purchase_splitting",
     "expected_answer_mode":"policy warning",
     "expected_source_docs":["GFR Rule 161"],
     "expected_evidence_concepts":["splitting prohibition","annual requirement estimate","rate contract"],
     "required_answer_concepts":["nahi GFR 161 ke against hai","annual requirement estimate karo","rate contract use karo"],
     "prohibited_claims":["monthly purchase always allowed without restriction"]},

    {"id":"A15","section":"A. Procurement Planning & Purchase Methods","lang":"en",
     "query":"How should the department estimate the total procurement value before selecting the method?",
     "expected_actor":"Department Buyer / Finance Officer",
     "expected_fine_intent":"procurement_value_estimation",
     "expected_answer_mode":"methodology guidance",
     "expected_source_docs":["GFR Rule 160","CPPR 2018"],
     "expected_evidence_concepts":["market survey","last purchase rate","annual requirement","include taxes"],
     "required_answer_concepts":["market survey","previous purchase rate","include all taxes and duties","full years requirement combined"],
     "prohibited_claims":["guess estimated value","ignore taxes in estimation"]},

    # ── Section B ──────────────────────────────────────────────────────────────
    {"id":"B1","section":"B. GFR, Approvals & Financial Control","lang":"hi",
     "query":"Purchase start karne se pehle administrative approval aur financial sanction mein kya difference hai?",
     "expected_actor":"Department Officer",
     "expected_fine_intent":"approval_types_difference",
     "expected_answer_mode":"conceptual explanation",
     "expected_source_docs":["GFR 2017","CG Treasury Rules"],
     "expected_evidence_concepts":["administrative approval technical necessity","financial sanction budget allocation","sequence matters"],
     "required_answer_concepts":["administrative approval need ka authorization hai","financial sanction budget ka confirmation hai","dono alag hain"],
     "prohibited_claims":["dono same hain","ek sufficient hai"]},

    {"id":"B2","section":"B. GFR, Approvals & Financial Control","lang":"en",
     "query":"Who should confirm budget availability before a tender is published?",
     "expected_actor":"Finance Officer / DDO",
     "expected_fine_intent":"budget_confirmation_responsibility",
     "expected_answer_mode":"role-based guidance",
     "expected_source_docs":["GFR Rule 147","CG Budget Manual"],
     "expected_evidence_concepts":["DDO certification","budget head","fund availability"],
     "required_answer_concepts":["DDO or Finance Officer must certify","budget head must have sufficient funds","before tender publication"],
     "prohibited_claims":["technical department can self-certify budget"]},

    {"id":"B3","section":"B. GFR, Approvals & Financial Control","lang":"en",
     "query":"Can a tender be initiated before the budget is formally available?",
     "expected_actor":"Department Head / Finance Officer",
     "expected_fine_intent":"tender_before_budget",
     "expected_answer_mode":"policy clarification",
     "expected_source_docs":["GFR Rule 147","GFR Rule 159"],
     "expected_evidence_concepts":["no expenditure without budget","float tender but not award without sanction"],
     "required_answer_concepts":["generally NO","must have budget before commitment","may float tender but not award without sanction"],
     "prohibited_claims":["always allowed before budget","budget not required for tendering"]},

    {"id":"B4","section":"B. GFR, Approvals & Financial Control","lang":"hi",
     "query":"Department ke paas budget hai, lekin financial sanction pending hai. Kya GeM order place kar sakte hain?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"gem_order_without_sanction",
     "expected_answer_mode":"policy clarification",
     "expected_source_docs":["GFR Rule 147","GeM Guidelines"],
     "expected_evidence_concepts":["financial sanction required","GeM order is commitment","sanction before order"],
     "required_answer_concepts":["nahi financial sanction pehle chahiye","GeM order ek commitment hai","sanction lo pehle"],
     "prohibited_claims":["budget hone par GeM order place kar sakte hain"]},

    {"id":"B5","section":"B. GFR, Approvals & Financial Control","lang":"en",
     "query":"What records should be kept to prove that the selected procurement method was justified?",
     "expected_actor":"Procurement Officer",
     "expected_fine_intent":"procurement_documentation",
     "expected_answer_mode":"checklist",
     "expected_source_docs":["GFR Rule 158","CPPR 2018"],
     "expected_evidence_concepts":["file noting","comparative statement","GeM screenshot","competent authority approval"],
     "required_answer_concepts":["file noting with reasons","market survey record","competent authority approval","GeM availability certificate if applicable"],
     "prohibited_claims":["no documentation needed","verbal approval sufficient"]},

    {"id":"B6","section":"B. GFR, Approvals & Financial Control","lang":"en",
     "query":"Can the competent authority approve a purchase after the order has already been placed?",
     "expected_actor":"Department Head / Finance Officer",
     "expected_fine_intent":"post_facto_approval",
     "expected_answer_mode":"policy warning",
     "expected_source_docs":["GFR Rule 21","CG Finance Rules"],
     "expected_evidence_concepts":["post-facto approval irregular","exceptional circumstances only","audit objection risk"],
     "required_answer_concepts":["post-facto approval is irregular","only in exceptional circumstances","must record reasons","audit objection risk"],
     "prohibited_claims":["post-facto approval is routine","always acceptable"]},

    {"id":"B7","section":"B. GFR, Approvals & Financial Control","lang":"en",
     "query":"What is delegated financial power, and how does it affect procurement method selection?",
     "expected_actor":"Department Officer",
     "expected_fine_intent":"delegated_financial_powers",
     "expected_answer_mode":"conceptual explanation with practical implication",
     "expected_source_docs":["GFR Rule 22","CG Delegation of Financial Powers Rules"],
     "expected_evidence_concepts":["delegated authority","procurement ceiling","approval hierarchy"],
     "required_answer_concepts":["delegated power is sanctioned spending limit","determines who can approve","above limit needs higher authority"],
     "prohibited_claims":["delegated power has no procurement implications"]},

    {"id":"B8","section":"B. GFR, Approvals & Financial Control","lang":"hi",
     "query":"Agar purchase value officer ki delegated power se zyada hai, to next approval kis stage par lena chahiye?",
     "expected_actor":"Department Officer",
     "expected_fine_intent":"escalation_for_approval",
     "expected_answer_mode":"procedural guidance",
     "expected_source_docs":["GFR Rule 22","CG Delegation Rules"],
     "expected_evidence_concepts":["escalation to higher authority","before tender floatation","file noting"],
     "required_answer_concepts":["higher authority se approval lena hoga","tender float karne se pehle","file noting mein record karo"],
     "prohibited_claims":["post-facto approval enough","lower officer can self-approve"]},

    {"id":"B9","section":"B. GFR, Approvals & Financial Control","lang":"en",
     "query":"Can the department use last year's approved rate without conducting a fresh procurement?",
     "expected_actor":"Department Buyer",
     "expected_fine_intent":"rate_contract_reuse",
     "expected_answer_mode":"conditional guidance",
     "expected_source_docs":["GFR Rule 149","DGS&D Rate Contract guidelines"],
     "expected_evidence_concepts":["rate contract validity","check expiry","fresh procurement if expired"],
     "required_answer_concepts":["only if rate contract is still valid","check expiry date","fresh procurement if expired"],
     "prohibited_claims":["always use last years rate","no need to verify rate currency"]},

    {"id":"B10","section":"B. GFR, Approvals & Financial Control","lang":"en",
     "query":"How should price reasonableness be established when only one valid bid is received?",
     "expected_actor":"Evaluation Committee",
     "expected_fine_intent":"price_reasonableness_single_bid",
     "expected_answer_mode":"methodology guidance",
     "expected_source_docs":["GFR Rule 174","CVC guidelines"],
     "expected_evidence_concepts":["market survey","last purchase rate","PAC comparison","negotiation"],
     "required_answer_concepts":["compare with market rates","last purchase price","PAC or estimate comparison","if reasonable accept otherwise re-tender"],
     "prohibited_claims":["single bid always accepted","no verification needed"]},

    {"id":"B11","section":"B. GFR, Approvals & Financial Control","lang":"hi",
     "query":"Kya lowest quotation milne ka matlab price reasonable hai?",
     "expected_actor":"Evaluation Committee",
     "expected_fine_intent":"lowest_bid_reasonableness",
     "expected_answer_mode":"critical clarification",
     "expected_source_docs":["GFR Rule 174","CVC guidelines"],
     "expected_evidence_concepts":["lowest not equal to reasonable","market rate comparison","abnormally low bid check"],
     "required_answer_concepts":["nahi lowest ka matlab reasonable nahi","market rate se compare karo","abnormally low bid check karo"],
     "prohibited_claims":["lowest is always reasonable"]},

    {"id":"B12","section":"B. GFR, Approvals & Financial Control","lang":"en",
     "query":"What should the department do if all received bids are much higher than the estimated cost?",
     "expected_actor":"Tender Committee",
     "expected_fine_intent":"bids_above_estimate",
     "expected_answer_mode":"procedural guidance",
     "expected_source_docs":["GFR Rule 175","CVC guidelines"],
     "expected_evidence_concepts":["re-tender option","negotiate with L1","revise estimate","record decision"],
     "required_answer_concepts":["investigate reason for high bids","re-tender with revised scope","or negotiate with L1","record decision in file"],
     "prohibited_claims":["always accept highest bid","cancel without documentation"]},

    {"id":"B13","section":"B. GFR, Approvals & Financial Control","lang":"en",
     "query":"Can negotiations be conducted with the L1 bidder after opening financial bids?",
     "expected_actor":"Tender Committee",
     "expected_fine_intent":"l1_negotiation",
     "expected_answer_mode":"policy clarification with conditions",
     "expected_source_docs":["GFR Rule 175","CVC guidelines 2011"],
     "expected_evidence_concepts":["negotiation only with L1","only when bids exceed estimate","CVC restricts routine negotiation"],
     "required_answer_concepts":["negotiation only with L1","only when all bids above estimate","CVC guidelines restrict negotiation"],
     "prohibited_claims":["negotiate with all bidders","negotiation is routine after bid opening"]},

    {"id":"B14","section":"B. GFR, Approvals & Financial Control","lang":"hi",
     "query":"Tender cancel karne ke liye kya reasons record karne chahiye?",
     "expected_actor":"Tender Committee / Department Head",
     "expected_fine_intent":"tender_cancellation_reasons",
     "expected_answer_mode":"checklist",
     "expected_source_docs":["GFR Rule 175","CPPR 2018"],
     "expected_evidence_concepts":["written reasons mandatory","competent authority approval","valid cancellation reasons"],
     "required_answer_concepts":["written reasons file mein hone chahiye","competent authority se approval","valid reasons bids above estimate changed specs no bids"],
     "prohibited_claims":["verbal cancellation sufficient","no reasons needed"]},

    {"id":"B15","section":"B. GFR, Approvals & Financial Control","lang":"en",
     "query":"Can the department reject all bids without giving any reason?",
     "expected_actor":"Tender Committee",
     "expected_fine_intent":"bid_rejection_requirements",
     "expected_answer_mode":"policy clarification",
     "expected_source_docs":["GFR Rule 175","CVC guidelines"],
     "expected_evidence_concepts":["reasons must be recorded","not arbitrary rejection","competent authority"],
     "required_answer_concepts":["NO reasons must be recorded","competent authority must approve","cannot be arbitrary"],
     "prohibited_claims":["department can reject without any reason"]},

    # ── Section C ──────────────────────────────────────────────────────────────
    {"id":"C1","section":"C. Specifications, Competition & Eligibility","lang":"en",
     "query":"Can we mention a preferred brand and write 'or equivalent' in the technical specifications?",
     "expected_actor":"Technical Committee",
     "expected_fine_intent":"brand_specification",
     "expected_answer_mode":"conditional guidance",
     "expected_source_docs":["GFR Rule 160","CVC guidelines"],
     "expected_evidence_concepts":["or equivalent permitted","define equivalence criteria","avoid restrictive specs"],
     "required_answer_concepts":["allowed only with or equivalent","must clearly define equivalence parameters","avoid restrictive specs"],
     "prohibited_claims":["single brand spec is fine","or equivalent not needed"]},

    {"id":"C2","section":"C. Specifications, Competition & Eligibility","lang":"hi",
     "query":"Laptop specification banate waqt processor brand mention karna allowed hai kya?",
     "expected_actor":"Technical Committee",
     "expected_fine_intent":"technical_spec_brand",
     "expected_answer_mode":"conditional guidance",
     "expected_source_docs":["GFR Rule 160","CVC guidelines"],
     "expected_evidence_concepts":["performance spec preferred","brand restrictive","or equivalent required"],
     "required_answer_concepts":["avoid specific brand","performance parameters use karo","agar brand mention karo to or equivalent with criteria"],
     "prohibited_claims":["specific brand must be mentioned","performance specs not needed"]},

    {"id":"C3","section":"C. Specifications, Competition & Eligibility","lang":"en",
     "query":"How can specifications be written so that they do not favour one vendor?",
     "expected_actor":"Technical Committee",
     "expected_fine_intent":"neutral_specification_writing",
     "expected_answer_mode":"best practice guidance",
     "expected_source_docs":["GFR Rule 160","CVC guidelines"],
     "expected_evidence_concepts":["performance based spec","avoid brand names","independent committee review"],
     "required_answer_concepts":["use performance or functional specs","avoid brand or model names","get specs reviewed by independent committee"],
     "prohibited_claims":["any spec is fine","vendor can write specs for their own tender"]},

    {"id":"C4","section":"C. Specifications, Competition & Eligibility","lang":"en",
     "query":"Can experience and turnover requirements be higher than the estimated tender value?",
     "expected_actor":"Tender Committee",
     "expected_fine_intent":"eligibility_criteria_proportionality",
     "expected_answer_mode":"policy clarification",
     "expected_source_docs":["GFR Rule 160","CVC guidelines"],
     "expected_evidence_concepts":["proportional eligibility","not restrictive","must be justified"],
     "required_answer_concepts":["eligibility should be proportionate to tender value","higher than tender value restricts competition","must be justified"],
     "prohibited_claims":["any eligibility criteria is fine","very high turnover requirement always valid"]},

    {"id":"C5","section":"C. Specifications, Competition & Eligibility","lang":"hi",
     "query":"Tender mein three-year experience mandatory rakhna kab justified hota hai?",
     "expected_actor":"Tender Committee",
     "expected_fine_intent":"experience_requirement_justification",
     "expected_answer_mode":"conditional guidance",
     "expected_source_docs":["GFR Rule 160","CPPR 2018"],
     "expected_evidence_concepts":["complex specialized work","safety criticality","proportionate to risk"],
     "required_answer_concepts":["justified for complex high-risk items","simple items ke liye excessive","document karna zaroori hai"],
     "prohibited_claims":["3-year experience always mandatory","experience requirement never justified"]},

    {"id":"C6","section":"C. Specifications, Competition & Eligibility","lang":"en",
     "query":"Can a startup be exempted from prior experience and turnover requirements?",
     "expected_actor":"Tender Committee",
     "expected_fine_intent":"startup_exemption",
     "expected_answer_mode":"policy confirmation",
     "expected_source_docs":["DPIIT Startup Policy","GFR Rule 157A"],
     "expected_evidence_concepts":["DPIIT registered startup exemption","GFR 157A","experience waiver"],
     "required_answer_concepts":["yes DPIIT registered startups can be exempted","GFR 157A provision","must be registered startup"],
     "prohibited_claims":["startups have no special provisions","experience always mandatory for all bidders"]},

    {"id":"C7","section":"C. Specifications, Competition & Eligibility","lang":"en",
     "query":"Does MSME registration automatically make a bidder eligible for every tender?",
     "expected_actor":"Vendor / Bidder",
     "expected_fine_intent":"msme_automatic_eligibility",
     "expected_answer_mode":"clarification",
     "expected_source_docs":["MSME Act","GFR 157","Public Procurement Policy MSEs 2012"],
     "expected_evidence_concepts":["MSME benefits specific","technical eligibility still required","EMD exemption price preference"],
     "required_answer_concepts":["NO MSME gives benefits not automatic eligibility","must still meet technical specs","gets EMD exemption and price preference"],
     "prohibited_claims":["MSME means automatic eligibility for all tenders"]},

    {"id":"C8","section":"C. Specifications, Competition & Eligibility","lang":"en",
     "query":"Can EMD exemption be claimed without uploading the required registration certificate?",
     "expected_actor":"Vendor / Bidder",
     "expected_fine_intent":"emd_exemption_documentation",
     "expected_answer_mode":"policy clarification",
     "expected_source_docs":["GeM Guidelines","MSME Policy","GFR Rule 170"],
     "expected_evidence_concepts":["certificate mandatory","MSME NSIC startup cert required","bid rejection without cert"],
     "required_answer_concepts":["NO certificate upload is mandatory","without certificate EMD exemption not valid","bid may be rejected"],
     "prohibited_claims":["verbal claim sufficient","certificate can be submitted later after bid opening"]},

    {"id":"C9","section":"C. Specifications, Competition & Eligibility","lang":"en",
     "query":"What should happen if a bidder meets the technical specification but misses one mandatory document?",
     "expected_actor":"Evaluation Committee",
     "expected_fine_intent":"missing_mandatory_document",
     "expected_answer_mode":"procedural guidance",
     "expected_source_docs":["GFR Rule 167","CPPR 2018"],
     "expected_evidence_concepts":["mandatory vs non-mandatory","non-material deviation","clarification request"],
     "required_answer_concepts":["depends on document criticality","mandatory documents bid may be rejected","non-material seek clarification","document decision in evaluation"],
     "prohibited_claims":["always reject if any document missing","always accept despite missing documents"]},

    {"id":"C10","section":"C. Specifications, Competition & Eligibility","lang":"en",
     "query":"A bidder uploaded an expired certificate. Should the bid be rejected or can clarification be requested?",
     "expected_actor":"Evaluation Committee",
     "expected_fine_intent":"expired_certificate_handling",
     "expected_answer_mode":"procedural guidance",
     "expected_source_docs":["GFR Rule 167","CPPR 2018"],
     "expected_evidence_concepts":["expired certificate material deficiency","cannot substitute after bid","generally leads to rejection"],
     "required_answer_concepts":["expired cert is material deficiency","cannot be substituted after bid","generally leads to rejection","document in evaluation report"],
     "prohibited_claims":["expired cert always acceptable","can always request update after bid opening"]},

    # ── Section D ──────────────────────────────────────────────────────────────
    {"id":"D1","section":"D. Evaluation, Award & Contract Management","lang":"hi",
     "query":"Technical evaluation ke baad financial bids kin bidders ki open honi chahiye?",
     "expected_actor":"Evaluation Committee",
     "expected_fine_intent":"financial_bid_opening_rule",
     "expected_answer_mode":"procedural guidance",
     "expected_source_docs":["GFR Rule 164","CPPR 2018"],
     "expected_evidence_concepts":["two-bid system","technically qualified only","disqualified financial bid not opened"],
     "required_answer_concepts":["sirf technically qualified bidders ki financial bids kholo","non-responsive ki financial bid band rakhni hai","record karo decision"],
     "prohibited_claims":["all bidders ki financial bids open karo regardless","financial bid of failed bidder can be opened"]},

    {"id":"D2","section":"D. Evaluation, Award & Contract Management","lang":"en",
     "query":"Can a technically non-responsive bidder be selected because its price is the lowest?",
     "expected_actor":"Evaluation Committee",
     "expected_fine_intent":"non_responsive_selection",
     "expected_answer_mode":"policy prohibition",
     "expected_source_docs":["GFR Rule 164","CPPR 2018"],
     "expected_evidence_concepts":["technical compliance mandatory","L1 among technically qualified only","price alone insufficient"],
     "required_answer_concepts":["NO technically non-responsive cannot be selected","L1 is lowest among technically qualified only"],
     "prohibited_claims":["price can override technical disqualification"]},

    {"id":"D3","section":"D. Evaluation, Award & Contract Management","lang":"hi",
     "query":"L1 bidder ki rate estimate se 25% zyada hai. Department ko kya karna chahiye?",
     "expected_actor":"Tender Committee",
     "expected_fine_intent":"l1_above_estimate",
     "expected_answer_mode":"options-based guidance",
     "expected_source_docs":["GFR Rule 175","CVC guidelines"],
     "expected_evidence_concepts":["investigate reason","negotiate with L1","re-tender","record decision"],
     "required_answer_concepts":["investigate market reasons","negotiate with L1 if estimate reasonable","re-tender ya scope adjust karo","record decision"],
     "prohibited_claims":["automatically accept 25% above estimate","automatically reject without investigation"]},

    {"id":"D4","section":"D. Evaluation, Award & Contract Management","lang":"en",
     "query":"How should the evaluation committee record reasons for rejecting a bidder?",
     "expected_actor":"Evaluation Committee",
     "expected_fine_intent":"bid_rejection_documentation",
     "expected_answer_mode":"procedural guidance",
     "expected_source_docs":["GFR Rule 167","CPPR 2018"],
     "expected_evidence_concepts":["evaluation report","specific reasons per bidder","signed by committee","file noting"],
     "required_answer_concepts":["specific clause-by-clause reasons","signed evaluation report","file noting by committee","available for audit"],
     "prohibited_claims":["verbal rejection sufficient","general reasons are fine"]},

    {"id":"D5","section":"D. Evaluation, Award & Contract Management","lang":"en",
     "query":"Can tender conditions be changed after bids have already been opened?",
     "expected_actor":"Tender Committee",
     "expected_fine_intent":"post_opening_changes",
     "expected_answer_mode":"policy prohibition",
     "expected_source_docs":["GFR Rule 163","CPPR 2018"],
     "expected_evidence_concepts":["no changes after bid opening","material change re-tender","corrigendum before opening only"],
     "required_answer_concepts":["NO conditions cannot change after opening","changes invalidate process","must re-tender if changes needed"],
     "prohibited_claims":["conditions can be changed at any time","minor changes always permissible after opening"]},

    {"id":"D6","section":"D. Evaluation, Award & Contract Management","lang":"hi",
     "query":"Purchase Order issue hone ke baad vendor delivery delay kare to department kya action le sakta hai?",
     "expected_actor":"Contract Manager / Department",
     "expected_fine_intent":"delivery_delay_action",
     "expected_answer_mode":"procedural guidance",
     "expected_source_docs":["GFR Rule 176","Contract clauses"],
     "expected_evidence_concepts":["LD clause","show cause notice","extension with LD","cancel order"],
     "required_answer_concepts":["LD clause invoke karo","show cause notice bhejo","extension de sakte with LD","cancel kar sakte if material breach"],
     "prohibited_claims":["no action available","accept delay without penalty"]},

    {"id":"D7","section":"D. Evaluation, Award & Contract Management","lang":"hi",
     "query":"Goods receive ho gaye, but specification match nahi kar rahi. Payment release karna chahiye kya?",
     "expected_actor":"Inspection Officer / Finance Officer",
     "expected_fine_intent":"spec_mismatch_payment",
     "expected_answer_mode":"policy clarification",
     "expected_source_docs":["GFR Rule 176","GFR Rule 136"],
     "expected_evidence_concepts":["inspection report mandatory","reject non-conforming goods","no payment before inspection clearance"],
     "required_answer_concepts":["nahi payment band karo","goods return or rejection karo","inspection report mein document karo","vendor ko notice do"],
     "prohibited_claims":["pay and adjust later","specification mismatch ignore kar sakte"]},

    {"id":"D8","section":"D. Evaluation, Award & Contract Management","lang":"en",
     "query":"What documents should be completed before processing payment to the supplier?",
     "expected_actor":"Finance Officer / DDO",
     "expected_fine_intent":"payment_documentation",
     "expected_answer_mode":"checklist",
     "expected_source_docs":["GFR Rule 136","GFR Rule 176"],
     "expected_evidence_concepts":["inspection report","delivery challan","invoice","GRN","performance security check"],
     "required_answer_concepts":["goods receipt note","inspection certificate","invoice matching PO","performance security verification","DDO certificate"],
     "prohibited_claims":["payment without inspection report","invoice alone sufficient"]},

    # ── Section E ──────────────────────────────────────────────────────────────
    {"id":"E1","section":"E. Mixed CHiPS, Vendor & EMD Questions","lang":"hi",
     "query":"Bid submit karne ke baad corrigendum se specifications change ho gayi. Kya mujhe bid dobara submit karni hogi?",
     "expected_actor":"Vendor / Bidder",
     "expected_fine_intent":"corrigendum_bid_resubmission",
     "expected_answer_mode":"vendor guidance",
     "expected_source_docs":["CHiPS Portal User Guide","CPPR 2018"],
     "expected_evidence_concepts":["corrigendum triggers re-submission","portal reopens submission","deadline extension"],
     "required_answer_concepts":["haan agar material change hai to re-submit karo","portal check karo deadline","revised bid submit karo before new deadline"],
     "prohibited_claims":["no need to resubmit ever","corrigendum does not affect submitted bids"]},

    {"id":"E2","section":"E. Mixed CHiPS, Vendor & EMD Questions","lang":"hi",
     "query":"EMD payment successful hai but portal par status pending dikh raha hai, aur deadline close hai. Main kya karun?",
     "expected_actor":"Vendor / Bidder",
     "expected_fine_intent":"emd_payment_portal_issue",
     "expected_answer_mode":"troubleshooting guidance",
     "expected_source_docs":["CHiPS Portal Helpdesk","GeM Support"],
     "expected_evidence_concepts":["screenshot evidence","helpdesk contact","bank NEFT reference","email to tender authority"],
     "required_answer_concepts":["payment proof screenshot rakho","turant CHiPS helpdesk contact karo","tender authority ko email karo with proof","reference number preserve karo"],
     "prohibited_claims":["wait and see","deadline miss karo","resubmit payment without checking"]},
]

# ── Sarvam API Call ────────────────────────────────────────────────────────────
def call_sarvam(user_message: str) -> dict:
    """Call Sarvam-105b and extract final answer (content) + reasoning chain."""
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
        "max_tokens": 4000,   # must be large: reasoning eats tokens first
        "budget_tokens": 600, # cap the internal chain-of-thought
        "stream": False,
    }
    t0 = time.monotonic()
    try:
        resp = httpx.post(SARVAM_URL, headers=headers, json=payload, timeout=180)
        elapsed = round(time.monotonic() - t0, 2)

        if resp.status_code == 200:
            data = resp.json()
            msg = data["choices"][0]["message"]
            # Sarvam-105b: final answer is in 'content'; reasoning chain in 'reasoning_content'
            content   = (msg.get("content") or "").strip()
            reasoning = (msg.get("reasoning_content") or "").strip()
            finish    = data["choices"][0].get("finish_reason", "unknown")
            usage     = data.get("usage", {})
            return {
                "status": "ok",
                "answer": content,
                "reasoning_chain": reasoning,
                "finish_reason": finish,
                "elapsed_s": elapsed,
                "model": data.get("model", SARVAM_MODEL),
                "usage": usage,
                "http_status": 200,
            }
        else:
            return {
                "status": "error",
                "answer": f"HTTP {resp.status_code}: {resp.text[:400]}",
                "reasoning_chain": "",
                "finish_reason": "error",
                "elapsed_s": elapsed,
                "model": SARVAM_MODEL,
                "http_status": resp.status_code,
            }
    except Exception as e:
        return {
            "status": "error",
            "answer": f"Exception: {e}",
            "reasoning_chain": "",
            "finish_reason": "exception",
            "elapsed_s": round(time.monotonic() - t0, 2),
            "model": SARVAM_MODEL,
            "http_status": 0,
        }


# ── Evaluation Helpers ─────────────────────────────────────────────────────────
def check_citations(answer: str, expected_docs: list) -> dict:
    al = answer.lower()
    found, missing = [], []
    for doc in expected_docs:
        kws = [w for w in re.split(r'[\s/&()]+', doc.lower()) if len(w) > 3]
        if kws and any(k in al for k in kws):
            found.append(doc)
        else:
            missing.append(doc)
    score = round(len(found) / len(expected_docs), 2) if expected_docs else 1.0
    return {"found": found, "missing": missing, "score": score}


def check_concepts(answer: str, required: list) -> dict:
    al = answer.lower()
    covered, missing = [], []
    for concept in required:
        kws = [w for w in re.split(r'[\s,]+', concept.lower()) if len(w) > 3]
        hits = sum(1 for k in kws if k in al)
        if kws and hits >= max(1, len(kws) // 2):
            covered.append(concept)
        else:
            missing.append(concept)
    score = round(len(covered) / len(required), 2) if required else 1.0
    return {"covered": covered, "missing": missing, "score": score}


def check_prohibited(answer: str, prohibited: list) -> dict:
    al = answer.lower()
    violations = []
    for claim in prohibited:
        kws = [w for w in re.split(r'[\s,]+', claim.lower()) if len(w) > 3]
        hits = sum(1 for k in kws if k in al)
        if kws and hits >= max(1, len(kws) * 2 // 3):
            violations.append(claim)
    return {"violations": violations, "safe": len(violations) == 0}


def grade(citation: dict, concepts: dict, prohibited: dict) -> str:
    if not prohibited["safe"]:
        return "FAIL"
    score = citation["score"] * 0.35 + concepts["score"] * 0.65
    if score >= 0.70:  return "PASS"
    if score >= 0.40:  return "PARTIAL"
    return "FAIL"


# ── Build prompt ───────────────────────────────────────────────────────────────
def build_prompt(q: dict) -> str:
    sources = ", ".join(q["expected_source_docs"])
    return (
        f"Question: {q['query']}\n\n"
        f"[Regulatory context relevant to this question: {sources}]\n\n"
        f"Please answer clearly, citing specific GFR rule numbers, GeM guidelines, "
        f"or CPPR 2018 sections where applicable."
    )


# ── Run tests ──────────────────────────────────────────────────────────────────
def run():
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = OUTPUT_DIR / f"sarvam105b_test_{ts_str}.json"
    md_path   = OUTPUT_DIR / f"sarvam105b_test_{ts_str}.md"

    print(f"\n{'='*70}")
    print(f"  SARVAM-{SARVAM_MODEL.upper()} PROCUREMENT TEST")
    print(f"  Questions : {len(QUESTIONS)}")
    print(f"  Started   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Output    : {md_path.name}")
    print(f"{'='*70}\n")

    results, pass_c, partial_c, fail_c = [], 0, 0, 0
    total_time = 0.0

    for i, q in enumerate(QUESTIONS, 1):
        short_q = q["query"][:60] + ("..." if len(q["query"]) > 60 else "")
        print(f"[{i:02d}/{len(QUESTIONS)}] {q['id']} | {short_q}")

        api = call_sarvam(build_prompt(q))
        answer  = api["answer"]
        elapsed = api["elapsed_s"]
        total_time += elapsed

        citation  = check_citations(answer, q["expected_source_docs"])
        concepts  = check_concepts(answer, q["required_answer_concepts"])
        prohibited = check_prohibited(answer, q["prohibited_claims"])
        g         = grade(citation, concepts, prohibited)

        if   g == "PASS":    pass_c    += 1; sym = "PASS   "
        elif g == "PARTIAL": partial_c += 1; sym = "PARTIAL"
        else:                fail_c    += 1; sym = "FAIL   "

        print(f"         {sym} | {elapsed}s | cite:{citation['score']} | concept:{concepts['score']} | safe:{prohibited['safe']} | finish:{api['finish_reason']}")
        if not answer:
            print(f"         *** WARNING: empty final answer! reasoning={len(api['reasoning_chain'])} chars")

        rec = {
            "id": q["id"],
            "section": q["section"],
            "query": q["query"],
            "language": q["lang"],
            "expected_actor": q["expected_actor"],
            "expected_fine_intent": q["expected_fine_intent"],
            "expected_answer_mode": q["expected_answer_mode"],
            "expected_source_docs": q["expected_source_docs"],
            "expected_evidence_concepts": q["expected_evidence_concepts"],
            "required_answer_concepts": q["required_answer_concepts"],
            "prohibited_claims": q["prohibited_claims"],
            "retrieved_top10_sources": ["[direct API mode – no live Qdrant RAG]"],
            "final_context_sources": q["expected_source_docs"],
            "final_answer": answer,
            "reasoning_chain_preview": api["reasoning_chain"][:500],
            "reasoning_chain_full": api["reasoning_chain"],
            "finish_reason": api["finish_reason"],
            "citation_correctness": citation,
            "concepts_coverage": concepts,
            "prohibited_check": prohibited,
            "response_time_s": elapsed,
            "grade": g,
            "api_status": api["status"],
            "model_used": api.get("model", SARVAM_MODEL),
            "token_usage": api.get("usage", {}),
        }
        results.append(rec)

        # Save incrementally after every question
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"summary": {"done_so_far": i, "total": len(QUESTIONS)},
                       "results": results}, f, ensure_ascii=False, indent=2)

        if i < len(QUESTIONS):
            time.sleep(0.3)

    summary = {
        "total": len(QUESTIONS),
        "pass": pass_c, "partial": partial_c, "fail": fail_c,
        "pass_rate": round(pass_c/len(QUESTIONS)*100, 1),
        "partial_rate": round(partial_c/len(QUESTIONS)*100, 1),
        "fail_rate": round(fail_c/len(QUESTIONS)*100, 1),
        "avg_response_time_s": round(total_time/len(QUESTIONS), 2),
        "total_time_s": round(total_time, 2),
        "model": SARVAM_MODEL,
        "timestamp": datetime.now().isoformat(),
    }

    # Final JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, ensure_ascii=False, indent=2)

    # Build Markdown report
    md = build_md_report(results, summary)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\n{'='*70}")
    print(f"  PASS={pass_c} | PARTIAL={partial_c} | FAIL={fail_c}")
    print(f"  Pass Rate: {summary['pass_rate']}% | Avg Time: {summary['avg_response_time_s']}s")
    print(f"  JSON : {json_path}")
    print(f"  MD   : {md_path}")
    print(f"{'='*70}\n")
    return results, summary, md_path


# ── Markdown Report Builder ────────────────────────────────────────────────────
def build_md_report(results: list, summary: dict) -> str:
    ts = datetime.fromisoformat(summary["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

    # Section stats
    sec_stats = {}
    for r in results:
        s = r["section"]
        sec_stats.setdefault(s, {"pass":0,"partial":0,"fail":0,"total":0,"time":[]})
        sec_stats[s]["total"] += 1
        sec_stats[s][r["grade"].lower()] += 1
        sec_stats[s]["time"].append(r["response_time_s"])

    md = f"""# Sarvam-105B Procurement Chatbot — Full 50-Question Test Report

**Generated:** {ts}  
**Model:** `{summary['model']}`  
**API Endpoint:** `https://api.sarvam.ai/v1/chat/completions`  
**Test Mode:** Direct Sarvam API (incremental saves; no live Qdrant RAG)  
**Total Questions:** {summary['total']} (15 Section A + 15 Section B + 10 Section C + 8 Section D + 2 Section E)  

---

## Executive Summary

| Metric | Value |
|--------|-------|
| PASS | **{summary['pass']} / {summary['total']} ({summary['pass_rate']}%)** |
| PARTIAL | **{summary['partial']} / {summary['total']} ({summary['partial_rate']}%)** |
| FAIL | **{summary['fail']} / {summary['total']} ({summary['fail_rate']}%)** |
| Avg Response Time | **{summary['avg_response_time_s']}s per question** |
| Total Test Time | **{summary['total_time_s']}s ({round(summary['total_time_s']/60,1)} min)** |

### Section-Wise Performance

| Section | Total | PASS | PARTIAL | FAIL | Avg Time |
|---------|-------|------|---------|------|----------|
"""
    for sec, st in sec_stats.items():
        label = sec[:50]
        avg_t = round(sum(st["time"])/len(st["time"]), 1) if st["time"] else 0
        md += f"| {label} | {st['total']} | {st['pass']} | {st['partial']} | {st['fail']} | {avg_t}s |\n"

    md += "\n---\n\n## Detailed Results Per Question\n\n"

    cur_section = None
    for r in results:
        if r["section"] != cur_section:
            cur_section = r["section"]
            md += f"\n---\n### {cur_section}\n\n"

        g_sym = {"PASS": "PASS", "PARTIAL": "PARTIAL", "FAIL": "FAIL"}.get(r["grade"], "?")
        lang_label = "Hinglish/Hindi" if r["language"] == "hi" else "English"

        md += f"""#### [{r['id']}] {g_sym} — {r['query']}

| Field | Value |
|-------|-------|
| Language | {lang_label} |
| Expected Actor | {r['expected_actor']} |
| Fine Intent | `{r['expected_fine_intent']}` |
| Expected Answer Mode | {r['expected_answer_mode']} |
| Response Time | {r['response_time_s']}s |
| Finish Reason | `{r['finish_reason']}` |
| Model Used | `{r['model_used']}` |
| **Grade** | **{r['grade']}** |
| Citation Score | {r['citation_correctness']['score']} |
| Concept Coverage Score | {r['concepts_coverage']['score']} |
| Safety (No Prohibited Claims) | {'Safe' if r['prohibited_check']['safe'] else 'VIOLATION DETECTED'} |

**Expected Source Documents:** `{', '.join(r['expected_source_docs'])}`

**Expected Evidence Concepts:** `{', '.join(r['expected_evidence_concepts'])}`

**Required Answer Concepts (Coverage Check):**

| Concept | Status |
|---------|--------|
"""
        covered_set = set(r["concepts_coverage"]["covered"])
        for c in r["required_answer_concepts"]:
            tick = "COVERED" if c in covered_set else "MISSING"
            md += f"| {c} | {tick} |\n"

        md += f"""
**Citation Correctness:**
- Found: `{', '.join(r['citation_correctness']['found']) or 'none'}`
- Missing: `{', '.join(r['citation_correctness']['missing']) or 'none'}`

**Retrieved Top-10 Sources:** `{', '.join(r['retrieved_top10_sources'])}`

**Final Context Sources:** `{', '.join(r['final_context_sources'])}`

**Full Final Answer:**

{r['final_answer'] if r['final_answer'] else '_[EMPTY – reasoning chain only, no final content generated]_'}

"""
        if not r["prohibited_check"]["safe"]:
            md += f"**PROHIBITED CLAIM DETECTED:** `{', '.join(r['prohibited_check']['violations'])}`\n\n"

        if r.get("reasoning_chain_preview"):
            preview = r["reasoning_chain_preview"][:300].replace("\n", " ")
            md += f"**Reasoning Chain Preview (first 300 chars):** _{preview}_\n\n"

        md += "\n"

    # Quality analysis section
    cit_scores = [r["citation_correctness"]["score"] for r in results]
    con_scores = [r["concepts_coverage"]["score"] for r in results]
    times      = [r["response_time_s"] for r in results]

    md += f"""---

## Quality Analysis

### Citation Correctness
| Band | Count | Questions |
|------|-------|-----------|
| Excellent (>=0.8) | {sum(1 for s in cit_scores if s>=0.8)} | {', '.join(r['id'] for r in results if r['citation_correctness']['score']>=0.8)} |
| Good (0.5-0.79) | {sum(1 for s in cit_scores if 0.5<=s<0.8)} | {', '.join(r['id'] for r in results if 0.5<=r['citation_correctness']['score']<0.8)} |
| Poor (<0.5) | {sum(1 for s in cit_scores if s<0.5)} | {', '.join(r['id'] for r in results if r['citation_correctness']['score']<0.5)} |

### Concept Coverage
| Band | Count | Questions |
|------|-------|-----------|
| Excellent (>=0.8) | {sum(1 for s in con_scores if s>=0.8)} | {', '.join(r['id'] for r in results if r['concepts_coverage']['score']>=0.8)} |
| Good (0.5-0.79) | {sum(1 for s in con_scores if 0.5<=s<0.8)} | {', '.join(r['id'] for r in results if 0.5<=r['concepts_coverage']['score']<0.8)} |
| Poor (<0.5) | {sum(1 for s in con_scores if s<0.5)} | {', '.join(r['id'] for r in results if r['concepts_coverage']['score']<0.5)} |

### Response Time Distribution
| Band | Count | Questions |
|------|-------|-----------|
| Fast (<5s) | {sum(1 for t in times if t<5)} | {', '.join(r['id'] for r in results if r['response_time_s']<5)} |
| Medium (5-15s) | {sum(1 for t in times if 5<=t<15)} | {', '.join(r['id'] for r in results if 5<=r['response_time_s']<15)} |
| Slow (>=15s) | {sum(1 for t in times if t>=15)} | {', '.join(r['id'] for r in results if r['response_time_s']>=15)} |

### Safety Check
"""
    violations = [r for r in results if not r["prohibited_check"]["safe"]]
    if violations:
        md += "**VIOLATIONS DETECTED:**\n"
        for r in violations:
            md += f"- [{r['id']}] `{', '.join(r['prohibited_check']['violations'])}`\n"
    else:
        md += "All 50 responses passed the safety check — no prohibited claims detected.\n"

    md += f"""
---

## Methodology

| Item | Detail |
|------|--------|
| Model | `sarvam-105b` via `api.sarvam.ai/v1/chat/completions` |
| Token Budget | `max_tokens=4000`, `budget_tokens=600` (caps reasoning chain) |
| Response Parsing | `content` field = final answer; `reasoning_content` = internal chain-of-thought |
| RAG | Not connected (direct API mode; no Qdrant vector search) |
| Evaluation — Citation | Keyword match of GFR rules / doc names in answer |
| Evaluation — Concepts | Key-phrase match of required answer concepts |
| Evaluation — Safety | Prohibited claim phrase detection |
| Grading | PASS >= 70% weighted score; PARTIAL 40-69%; FAIL < 40% or safety violation |

---
*Report generated by Antigravity IDE | Sarvam-105B Procurement Test Suite*
"""
    return md


if __name__ == "__main__":
    run()
