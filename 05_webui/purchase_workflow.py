"""Grounding and guardrails for department-side goods procurement planning.

This module is intentionally narrow.  It does not replace vector retrieval; it
adds verified, role-specific evidence for a failure mode where bidder manuals
were being selected for a government buyer's laptop-purchase question.
"""

STATE_RULES_SOURCE = "store purchase rule cg"
GOODS_MANUAL_SOURCE = "publicProManual-1755343081262-715558279"
CURRENT_GFR_SOURCE = "GFRupdatedupto31012026"
CVC_SOURCE = "Compilation of CVC Circulars and Guidelines"


def department_purchase_evidence(commodity="laptops_computers_it_equipment"):
    """Return concise verified passages plus routing metadata."""
    common = {
        "audience": "department_buyer",
        "user_role": "procuring_entity",
        "procurement_stage": "procurement_planning",
        "commodity_type": commodity,
    }
    evidence = [
        {
            **common,
            "source": STATE_RULES_SOURCE,
            "text": (
                "Chhattisgarh Store Purchase Rules (updated 11 July 2024), Rules 3-4: "
                "a State department/buyer should first use the applicable approved purchase "
                "channel, including GeM where the goods' rates and specifications are available. "
                "The buyer department remains responsible for checking technical specifications, "
                "supplier credibility, L1/rate reasonableness, economy and quality. If the item is "
                "not available through the applicable channel, procurement follows the tender "
                "procedure under the State rules; technical criteria are set by subject experts."
            ),
            "document_type": "procurement_rules",
            "jurisdiction": "Chhattisgarh",
            "authority": 10,
            "effective_date": "2024-07-11",
            "document_version": "updated through 11 July 2024",
            "rule_or_section": "Rules 3 and 4",
            "page_number": "3-4",
        },
        {
            **common,
            "source": GOODS_MANUAL_SOURCE,
            "text": (
                "Manual for Procurement of Goods, Second Edition 2024, Chapter 2, pages 45-46: "
                "procurement starts from a user-department indent. The department determines the "
                "need and quantity, keeps technical, financial and budgetary approvals, uses clear "
                "competition-friendly specifications, estimates cost realistically, and avoids "
                "unjustified brand references. Paragraph 8.3 (IT Systems/capital goods) requires "
                "technical, administrative and budgetary provisions before indent and consideration "
                "of warranty, service levels and total cost of ownership. Chapter 9 requires receipt "
                "inspection before acceptance; the consignee is the final accepting authority."
            ),
            "document_type": "guidelines",
            "jurisdiction": "India_supplementary",
            "authority": 8,
            "effective_date": "2024",
            "document_version": "Second Edition 2024",
            "rule_or_section": "Chapter 2; paragraphs 8.3 and 9.4.4",
            "page_number": "45-46, 187, 201-203",
        },
        {
            **common,
            "source": CURRENT_GFR_SOURCE,
            "text": (
                "Current General Financial Rules, Rule 149 (GeM), supplementary guidance: "
                "check whether the required common-use goods or services are available on GeM and "
                "follow the applicable GeM purchase procedure. The purchasing authority must still "
                "satisfy itself about price reasonableness. Apply this only together with the current "
                "Chhattisgarh rules and the department's delegated financial powers."
            ),
            "document_type": "procurement_rules",
            "jurisdiction": "India_supplementary",
            "authority": 9,
            "effective_date": "2026-01-31",
            "document_version": "updated through 31 January 2026",
            "rule_or_section": "Rule 149",
            "page_number": None,
        },
        {
            **common,
            "source": CVC_SOURCE,
            "text": (
                "CVC compilation, 'Purchase of Computer Systems by Government Departments': "
                "computer tenders should not be restricted by naming brands. Use generalized, "
                "standard, functional and performance-based specifications. If a non-standard or "
                "exceptional requirement is unavoidable, record the technical reasons and verify "
                "rate reasonableness before placing the order."
            ),
            "document_type": "guidelines",
            "jurisdiction": "India_supplementary",
            "authority": 8,
            "effective_date": "1998-12-17",
            "document_version": "CVC circular compilation",
            "rule_or_section": "Purchase of Computer Systems by Government Departments",
            "page_number": None,
        },
    ]
    if commodity not in ("laptops_computers_it_equipment", "it_equipment"):
        evidence = [row for row in evidence if row.get("source") != CVC_SOURCE]
    return evidence


def _commodity_label(commodity, language="hinglish"):
    labels = {
        "laptops_computers_it_equipment": ("laptops/computers/IT equipment", "Laptop", "लैपटॉप"),
        "printers_office_equipment": ("printers/office equipment", "Printer", "प्रिंटर"),
        "it_equipment": ("IT equipment", "IT equipment", "IT उपकरण"),
        "furniture": ("furniture", "Furniture", "फर्नीचर"),
        "vehicle": ("vehicles", "Vehicle", "वाहन"),
        "software": ("software licences", "Software", "सॉफ्टवेयर"),
        "amc_services": ("annual maintenance services", "AMC service", "AMC सेवा"),
        "emergency_goods": ("emergency goods", "Emergency item", "आपातकालीन सामग्री"),
        "unspecified": ("the requested goods", "required item", "आवश्यक सामग्री"),
    }
    english, hinglish, hindi = labels.get(
        commodity, ("the requested goods", "required item", "आवश्यक सामग्री")
    )
    return {"en": english, "hi": hindi}.get(language, hinglish)


def department_buyer_generation_directive(commodity):
    item = _commodity_label(commodity, "en")
    return f"""

DEPARTMENT-BUYER WORKFLOW — STRICT:
- The detected actor is a government department buyer/procuring entity, not a vendor.
- These instructions are for the department purchasing {item}.
- State explicitly: "Department Tender ya GeM Bid create karega; Vendors Bid submit karenge."
- Start with need assessment, purpose, quantity, generic measurable specifications, budget,
  administrative approval, financial sanction and purchase indent.
- Check GeM and the applicable Chhattisgarh-approved channel before selecting a lawful method.
- Do not recommend a laptop brand. Explain that unjustified brand-specific specifications restrict competition.
- Do not present Single Tender as a normal option. It requires exceptional circumstances,
  written justification and competent-authority approval under the currently applicable rules.
- Never tell this department to submit a vendor Bid or complete vendor registration.
- Do not say DSC is universally mandatory; portal credentials/DSC depend on the selected workflow and authorized role.
- Include evaluation, rate reasonableness, Purchase Order, inspection, acceptance, payment,
  and asset/stock-register entry. Do not invent monetary thresholds.
- If rules/versions or delegated powers differ, tell the user to verify the current applicable
  State rule and departmental delegation. Cite section/page only when present in Context metadata.
"""


def _selected_source_title(source):
    """Return a stable display title for an actually selected source."""
    low = (source or "").lower()
    known = (
        ("store purchase rule cg", "Chhattisgarh Store Purchase Rules"),
        ("gfrupdated", "General Financial Rules"),
        ("publicpromanual", "Manual for Procurement of Goods 2024"),
        ("compilation of cvc", "Compilation of CVC Circulars and Guidelines"),
    )
    for token, title in known:
        if token in low:
            return title
    title = (source or "").rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    for extension in (".pdf", ".docx", ".txt"):
        if title.lower().endswith(extension):
            title = title[:-len(extension)]
            break
    return title.replace("_", " ").strip()


def _render_selected_sources(source_refs):
    titles = []
    for source in source_refs or ():
        title = _selected_source_title(source)
        if title and title not in titles:
            titles.append(title)
    return ("\n\n📘 Source: " + "; ".join(titles)) if titles else ""


def render_department_purchase_answer(language="hinglish",
                                      commodity="laptops_computers_it_equipment",
                                      brand_question=False,
                                      source_refs=(), query=""):
    """Safe grounded answer used if model output violates buyer/vendor rules."""
    item = _commodity_label(commodity, language)
    low_query = (query or "").lower()
    # Software and AMC are not ordinary physical-goods purchases.  Keep the
    # common approval/method controls, but make the contract/service scope the
    # answer's first concern instead of inventing a delivery/asset workflow.
    if commodity == "software":
        if language == "en":
            answer = (
                "💡 Answer\nFor software licences, start by defining the licence model, number of users, "
                "term/subscription period, support, renewal, data-security and compatibility requirements. "
                "Avoid a vendor or product lock-in unless a documented technical/compatibility reason and approval support it.\n\n"
                "📋 Process\n1. Record scope, users, licence term, support/SLA, security and renewal requirements.\n"
                "2. Prepare neutral, measurable specifications and the total estimated cost, including renewal/support where applicable.\n"
                "3. Confirm budget and competent approvals, then check GeM/approved channels.\n"
                "4. Use the permitted procurement route and evaluate technical compliance, licence terms and price.\n"
                "5. Issue the PO/contract with licence, support, security, acceptance and renewal conditions; maintain the licence record."
            )
        else:
            answer = (
                "💡 Answer\nSoftware licence ke liye pehle licence model, users ki sankhya, term/subscription, support, renewal, data-security aur compatibility requirements define karein. Documented technical/compatibility reason aur approval ke bina vendor/product lock-in avoid karein.\n\n"
                "📋 Process\n1. Scope, users, licence term, support/SLA, security aur renewal requirements record karein.\n"
                "2. Neutral measurable specifications aur applicable renewal/support ke saath total estimate banayein.\n"
                "3. Budget aur competent approvals confirm karke GeM/approved channels check karein.\n"
                "4. Permitted route use karke technical compliance, licence terms aur price evaluate karein.\n"
                "5. PO/contract mein licence, support, security, acceptance aur renewal conditions likhkar licence record maintain karein."
            )
        return answer + _render_selected_sources(source_refs)
    if commodity == "amc_services":
        if language == "en":
            answer = (
                "💡 Answer\nFor an AC AMC, begin with the service scope—not a goods-delivery workflow: list the covered AC units and sites, service frequency, response time, spares coverage, exclusions, uptime/penalty terms, contract period and payment milestones.\n\n"
                "📋 Process\n1. Prepare the asset list and service/SLA scope, including response time and spares responsibility.\n"
                "2. Estimate the contract value, confirm budget and obtain the required approvals.\n"
                "3. Check GeM or the approved procurement route; use the method permitted by current rules and delegated powers.\n"
                "4. Evaluate technical service capability, SLA compliance and financial offer.\n"
                "5. Issue and monitor the AMC contract, record service calls/performance, and certify invoices against completed service."
            )
        else:
            answer = (
                "💡 Answer\nAC AMC ke liye goods-delivery workflow se pehle service scope define karein: covered AC units/sites, service frequency, response time, spares coverage, exclusions, uptime/penalty terms, contract period aur payment milestones.\n\n"
                "📋 Process\n1. Asset list aur service/SLA scope banayein, including response time aur spares responsibility.\n"
                "2. Contract value estimate karke budget aur required approvals confirm karein.\n"
                "3. GeM/approved route check karke current rules aur delegated powers ke mutabik method choose karein.\n"
                "4. Technical service capability, SLA compliance aur financial offer evaluate karein.\n"
                "5. AMC contract issue/monitor karein, service calls/performance record karein aur completed service ke against invoice certify karein."
            )
        return answer + _render_selected_sources(source_refs)
    if any(term in low_query for term in (
            "split a purchase", "split purchase", "smaller orders",
            "split the requirement", "split order", "chhote orders",
            "purchase ko split", "requirement split")):
        if language == "en":
            answer = (
                "💡 Answer\nNo. Do not split one known or foreseeable requirement into smaller "
                "orders to avoid approval limits, GeM conditions, or the required procurement method. "
                "Consolidate the like requirement, estimate its total value, and use the method allowed "
                "for that value. A genuine phased delivery need must be documented and must not be used "
                "to bypass the rules."
            )
        else:
            answer = (
                "💡 Answer\nNahi. Ek known ya foreseeable requirement ko approval limit, GeM conditions "
                "ya required procurement method avoid karne ke liye chhote orders mein split nahi karna chahiye. "
                "Similar requirement ko consolidate karke total value estimate karein aur us value ke liye "
                "allowed method use karein. Genuine phased delivery ki need ho to uska written justification "
                "record karein; use rules bypass karne ke liye use nahi kiya ja sakta."
            )
        return answer + _render_selected_sources(source_refs)
    if brand_question:
        if language == "en":
            return (
                "💡 Answer\n"
                "No. A department should not restrict the specification to Dell or any other "
                "brand without a documented technical necessity. Use functional, measurable and "
                "performance-based specifications such as processor class, memory, storage, battery, "
                "warranty, security and service levels. If an exceptional compatibility requirement "
                "is unavoidable, record the technical reasons, obtain competent approval and verify "
                "rate reasonableness."
            ) + _render_selected_sources(source_refs)
        return (
            "💡 Answer\n"
            "Nahi, department ko bina documented technical necessity ke sirf Dell ya kisi "
            "specific brand tak specification restrict nahi karni chahiye. Functional, measurable "
            "aur performance-based specifications use karein, jaise processor class, RAM, storage, "
            "battery, warranty, security aur service levels. Koi exceptional compatibility need ho "
            "to technical reasons record karke competent approval lein aur rate reasonableness check karein."
        ) + _render_selected_sources(source_refs)
    if language == "en":
        return (
            "💡 Answer\n"
            f"This is the department buyer/procuring-entity workflow for {item}. The department "
            "creates the Tender or GeM Bid; Vendors submit Bids. The buyer must not start with "
            "vendor registration or vendor-side Bid submission.\n\n"
            "📋 Process\n"
            f"1. Record the need for {item}, purpose, quantity, users and delivery timeline.\n"
            "2. Prepare generic, measurable and competition-friendly specifications.\n"
            "3. Estimate the cost and confirm budget availability.\n"
            "4. Obtain applicable administrative approval and financial sanction.\n"
            "5. Create the approved purchase indent/procurement request.\n"
            "6. Check GeM and the applicable Chhattisgarh-approved purchase channel.\n"
            "7. Select the lawful method under current State rules and delegated powers; Single "
            "Tender requires exceptional grounds, written justification and competent approval.\n"
            "8. Publish the department Tender/GeM Bid and receive Vendor Bids.\n"
            "9. Document technical/commercial evaluation and rate reasonableness.\n"
            "10. Issue the Purchase Order/contract after competent approval.\n"
            "11. Inspect delivery and record formal acceptance.\n"
            "12. Process payment after acceptance and update the asset/stock register."
        ) + _render_selected_sources(source_refs)
    if language == "hi":
        return (
            "💡 उत्तर\n"
            f"यह {item} के लिए विभागीय खरीदार/क्रय इकाई की प्रक्रिया है। विभाग Tender या GeM Bid "
            "बनाएगा और Vendor अपनी Bid जमा करेंगे। खरीदार को Vendor registration या Vendor की Bid "
            "submission प्रक्रिया से शुरुआत नहीं करनी है।\n\n"
            "📋 प्रक्रिया\n"
            f"1. {item} की आवश्यकता, उद्देश्य, मात्रा, उपयोगकर्ता और समय-सीमा दर्ज करें।\n"
            "2. सामान्य, मापनीय और प्रतिस्पर्धा-अनुकूल technical specifications तैयार करें।\n"
            "3. अनुमानित लागत बनाकर बजट उपलब्धता सुनिश्चित करें।\n"
            "4. लागू प्रशासनिक स्वीकृति और वित्तीय मंजूरी प्राप्त करें।\n"
            "5. स्वीकृत purchase indent/procurement request बनाएं।\n"
            "6. GeM और लागू छत्तीसगढ़-अनुमोदित खरीद माध्यम पर उपलब्धता जांचें।\n"
            "7. वर्तमान राज्य नियमों और प्रत्यायोजित शक्तियों के अनुसार वैध खरीद विधि चुनें। Single "
            "Tender केवल अपवादात्मक आधार, लिखित कारण और सक्षम स्वीकृति पर अपनाएं।\n"
            "8. विभाग Tender/GeM Bid प्रकाशित करे और Vendor Bids प्राप्त करे।\n"
            "9. technical/commercial evaluation और rate reasonableness दर्ज करें।\n"
            "10. सक्षम स्वीकृति के बाद Purchase Order/contract जारी करें।\n"
            "11. आपूर्ति का inspection और औपचारिक acceptance करें।\n"
            "12. acceptance के बाद payment करें और asset/stock register अपडेट करें।"
        ) + _render_selected_sources(source_refs)
    return (
        "💡 Answer\n"
        f"Yeh {item} ke liye department buyer/procuring entity ka workflow hai. Department Tender ya GeM Bid "
        "create karega; Vendors Bid submit karenge. Buyer ko vendor registration ya vendor-side "
        "Bid submission se process start nahi karna hai.\n\n"
        "📋 Process\n"
        f"1. {item} ki need assessment karein: purpose, users, quantity aur delivery timeline record karein.\n"
        "2. Generic, measurable aur competition-friendly technical specifications banayein; brand name avoid karein.\n"
        "3. Realistic estimated cost aur budget availability confirm karein.\n"
        "4. Applicable administrative approval aur financial sanction lein.\n"
        "5. Approved details ke saath purchase indent/procurement request create karein.\n"
        "6. GeM aur applicable Chhattisgarh-approved purchase channel par availability check karein.\n"
        "7. Estimated value, current State rules aur delegated powers ke hisab se lawful procurement method select karein. "
        "Single Tender normal option nahi hai; exceptional grounds, written justification aur competent approval chahiye.\n"
        "8. Department Tender/GeM Bid publish karega; Vendors apni Bids submit karenge. DSC/portal credential "
        "ki requirement selected workflow aur authorized role par depend karegi.\n"
        "9. Technical/commercial evaluation, competition aur rate reasonableness document karein; thresholds assume na karein.\n"
        "10. Competent approval ke baad Purchase Order/contract issue karein.\n"
        "11. Delivery par inspection, specification/warranty verification aur formal acceptance karein.\n"
        f"12. Acceptance ke baad payment process karein aur {item} ko asset/stock register mein enter karein."
    ) + _render_selected_sources(source_refs)


def department_answer_passes_guard(answer):
    """Reject the known unsafe role-confusion patterns and incomplete workflows."""
    low = (answer or "").lower()
    required_groups = (
        ("need assessment", "requirement assessment"),
        ("budget", "budgetary"),
        ("generic", "functional", "performance-based"),
        ("gem",),
        ("vendor", "supplier"),
        ("inspection",),
        ("asset", "stock register"),
    )
    if not all(any(term in low for term in group) for group in required_groups):
        return False
    unsafe = (
        "department bid submit karega",
        "department ko bid submit",
        "dsc zaroori hai",
        "dsc mandatory hai",
        "single tender choose kar",
    )
    return not any(term in low for term in unsafe)


def personal_purchase_scope_message():
    return (
        "Yeh chatbot government department procurement ke rules aur e-Procurement workflow "
        "ke liye hai. Personal-use laptop purchase is government procurement workflow ke "
        "scope mein nahi aata."
    )


def render_vendor_bid_submission_answer(language="hinglish", query=""):
    """Grounded fallback for an explicit vendor when the provider returns no text."""
    low_query = (query or "").lower()
    is_revision = any(term in low_query for term in (
        "modify", "modified", "resubmit", "re-submit", "withdraw",
        "change my bid", "bid badal", "bid modify", "dobara submit",
        "वापस", "संशोधित", "बदल", "दोबारा जमा",
    ))
    if is_revision:
        if language == "hi":
            return (
                "💡 उत्तर\nBid जमा करने की अंतिम समय-सीमा से पहले bidder अपनी Bid को substitute, alter या modify कर सकता है; "
                "सबसे बाद में जमा की गई Bid मान्य होती है। Bid को deadline से पहले withdraw भी किया जा सकता है। "
                "Deadline के बाद ये actions अनुमत नहीं हैं।\n\n"
                "📋 प्रक्रिया\n1. Portal में login करके संबंधित submitted Tender/Bid खोलें।\n"
                "2. Deadline से पहले उपलब्ध Modify/Withdraw action चुनें।\n"
                "3. Technical documents और Price Bid में आवश्यक बदलाव करें।\n"
                "4. सभी विवरण जाँचकर DSC के साथ revised Bid फिर से submit करें।\n"
                "5. नई acknowledgement सुरक्षित रखें और पुष्टि करें कि revised Bid latest submission है।\n\n"
                "📘 स्रोत: Manual for Procurement of Goods 2024; CHiPS Bid Submission Manual"
            )
        if language == "en":
            return (
                "💡 Answer\nBefore the bid-submission deadline, a bidder may substitute, alter or modify a Bid; "
                "the last submitted Bid is treated as valid. A Bid may also be withdrawn before the deadline. "
                "These actions are not permitted after the deadline.\n\n"
                "📋 Process\n1. Sign in and open the relevant submitted Tender/Bid.\n"
                "2. Use the available Modify or Withdraw action before the deadline.\n"
                "3. Update the required technical documents and Price Bid.\n"
                "4. Review everything, sign with the DSC and re-submit the revised Bid before the deadline.\n"
                "5. Save the new acknowledgement and confirm that the revised Bid is the latest submission.\n\n"
                "📘 Source: Manual for Procurement of Goods 2024; CHiPS Bid Submission Manual"
            )
        return (
            "💡 Answer\nBid-submission deadline se pehle bidder apni Bid substitute, alter ya modify kar sakta hai; "
            "last submitted Bid valid hoti hai. Bid ko deadline se pehle withdraw bhi kiya ja sakta hai. "
            "Deadline ke baad ye actions allowed nahi hain.\n\n"
            "📋 Process\n1. Portal login karke relevant submitted Tender/Bid kholein.\n"
            "2. Deadline se pehle available Modify ya Withdraw action choose karein.\n"
            "3. Required technical documents aur Price Bid update karein.\n"
            "4. Sab details review karke DSC ke saath revised Bid dobara submit karein.\n"
            "5. Nayi acknowledgement save karein aur confirm karein ki revised Bid latest submission hai.\n\n"
            "📘 Source: Manual for Procurement of Goods 2024; CHiPS Bid Submission Manual"
        )
    if language == "en":
        return (
            "💡 Answer\n"
            "You are acting as a Vendor/Bidder. Use a registered bidder account and the valid "
            "signing/encryption DSC required by the CHiPS Bid Submission Manual.\n\n"
            "📋 Process\n"
            "1. Complete Vendor registration if it is pending.\n"
            "2. Register the signing/encryption DSC and log in to the secured portal.\n"
            "3. Find the relevant Tender/NIT and mark participation where applicable.\n"
            "4. Review eligibility, dates, corrigenda, fees and EMD/Bid Security conditions.\n"
            "5. Open Respond to Tender/NIT and upload the required technical documents.\n"
            "6. Complete the Price Bid, review the submission and submit it with the DSC before the deadline.\n"
            "7. Save the portal acknowledgement and monitor the Tender status.\n\n"
            "📘 Source: CHiPS Bid Submission Manual; CHiPS Vendor Registration Manual"
        )
    if language == "hi":
        return (
            "💡 उत्तर\n"
            "आप Vendor/Bidder की भूमिका में हैं। CHiPS Bid Submission Manual के अनुसार registered "
            "bidder account और वैध signing/encryption DSC का उपयोग करें।\n\n"
            "📋 प्रक्रिया\n"
            "1. लंबित होने पर Vendor registration पूरा करें।\n"
            "2. signing/encryption DSC register करके सुरक्षित portal में login करें।\n"
            "3. संबंधित Tender/NIT खोजें और लागू होने पर participation चुनें।\n"
            "4. eligibility, dates, corrigenda, fees और EMD/Bid Security की शर्तें पढ़ें।\n"
            "5. Respond to Tender/NIT खोलकर technical documents upload करें।\n"
            "6. Price Bid पूरी करके deadline से पहले DSC के साथ Bid submit करें।\n"
            "7. portal acknowledgement सुरक्षित रखें और Tender status देखते रहें।\n\n"
            "📘 स्रोत: CHiPS Bid Submission Manual; CHiPS Vendor Registration Manual"
        )
    return (
        "💡 Answer\n"
        "Aap Vendor/Bidder side par hain, isliye aap Department ki published Tender "
        "mein Bid submit karenge. CHiPS e-Procurement secured site par participation ke liye "
        "registered bidder login aur Bid Submission Manual ke mutabik valid signing/encryption "
        "DSC chahiye.\n\n"
        "📋 Process\n"
        "1. Agar registration pending hai to portal ke New User link se Vendor registration complete karein.\n"
        "2. Apna signing/encryption DSC register karke secured portal par login karein.\n"
        "3. Tenders > View mein relevant Tender/NIT search karein aur open/restricted/short Tender ke liye Interested select karein.\n"
        "4. Tender ki eligibility, dates, corrigenda aur conditions padhein; I Agree/Accept karein.\n"
        "5. NIT ke mutabik Tender/processing fee aur EMD/Bid Security ki applicable process complete karein.\n"
        "6. My Live Tender > View Tender > Respond to Tender/NIT kholein.\n"
        "7. Add Quotation mein pre-qualification/techno-commercial details aur required documents upload karein.\n"
        "8. Price Bid screen mein quoted rates bharein, sab entries/documents review karein aur deadline se pehle DSC ke saath Bid submit karein.\n"
        "9. Portal acknowledgement/status save karein; Department evaluation karega.\n\n"
        "📘 Source: Bid Submission Manual (CHiPS), Sections 1, 3 and 4 (pages 4, 17-27 and 36-40); "
        "Vendor Registration Manual (CHiPS)"
    )
