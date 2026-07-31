"""Source-backed deterministic answers for exact CG Store Rules clauses.

These are deliberately narrow: each branch corresponds to a verified clause
in the regenerated State Rules corpus and returns ``None`` for ambiguous or
unrelated procurement questions.  This avoids generation/API failures turning
an exact statutory value or timeline into an unsafe answer.
"""
from __future__ import annotations


def direct_cg_store_rule_answer(query: str) -> str | None:
    q = (query or "").casefold()
    def has(*terms: str) -> bool:
        return any(term in q for term in terms)

    # Rule 2 / Rule 4 / 4.1 / 4.2
    if has("public bodies", "covered by the cg", "covered by the chhattisgarh"):
        return "Under Rule 2 and 2.1, the Rules cover government departments, the State Electricity Board, public undertakings and boards, district/janpad panchayats, and urban bodies.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 2 and 2.1."
    if has("startup") and has("experience", "turnover"):
        return "Under Rule 4.2, a valid Chhattisgarh-recognised startup is exempt from prior-experience and prior-turnover conditions.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.2."
    if has("technical specification", "technical specifications") and has("tender", "tender issue", "inviting"):
        return "Before inviting the tender, Rule 4.1 requires the standards and technical specifications to be determined by persons having technical knowledge/expertise.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.1."
    if has("normal procurement method", "normal method under rule 4"):
        return "Under Rule 4, government procurement is normally through the tender system, subject to the stated exceptions and permitted routes.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4."
    if ((has("3 lakh", "three lakh", "तीन लाख") and has("kam", "कम", "below", "under", "less"))
            or has("tender 3 lakh se kam", "3 lakh se kam tender", "3 lakh ke neeche")):
        return (
            "Agar CG Store Purchase Rules ke context mein tender value Rs. 3 lakh se kam hai, to value-band ke hisaab se route choose karein:\n\n"
            "- **Rs. 50,001 se Rs. 3,00,000 tak:** Rule 4.3.2 ka **Limited Tender** use hota hai. Kam se kam 3 manufacturers, authorised representatives, ya registered manufacturers ko invite karein.\n"
            "- **Rs. 50,000 tak:** Rule 4.3.1 ke permitted **Single Tender** exceptions hi apply honge, jaise proprietary item, emergency, ya compatibility/standardisation; reasons, PAC/technical advice aur competent approval jahan prescribed ho, record karein.\n"
            "- **GeM par item available ho:** pehle Rule 3.1.1 ke mutabik GeM ki prescribed process follow karein; sirf amount dekhkar tender route na choose karein.\n\n"
            "Ek hi requirement ko threshold avoid karne ke liye chhote orders mein split nahi karna chahiye.\n\n"
            "Source: Chhattisgarh Store Purchase Rules — Rules 3.1.1, 4.3.1 and 4.3.2."
        )

    # Rule 4.3.1: single tender and PAC.
    if has("compatible spare", "spare parts") and has("one selected", "one firm", "one supplier"):
        return "Yes, compatible spare parts may be bought from one selected firm for standardisation/compatibility, but Rule 4.3.1 requires advice from a competent technical expert and approval of the competent authority.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.1(b)(3)."
    if has("after objections", "objections to a proprietary"):
        return "After objections are resolved, obtain the proposed supplier's rates and justification. The purchase committee recommends acceptance, rejection, or negotiation, followed by competent approval before award/further action.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.1(b)(3)."
    if has("objection", "claim notice") and has("pac", "proprietary"):
        return "After the PAC, publish a brief claim/objection notice in newspapers and a detailed notice on the government/department website, allowing at least 30 days.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.1(b)(3)."
    if has("proprietary article", "pac") and has("certificate", "sole manufacturer", "authorised seller"):
        return "Obtain the Proprietary Article Certificate (PAC) in the prescribed Appendix 4 form before the proprietary-article purchase process.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.1(b)(3) and Appendix 4."

    # Rule 4.3.2 and 4.3.3 values/publicity.
    if has("open tender") and has("niyam", "rules", "what are", "kya kya", "what rules") and not has("above", "up to", "lakh", "publicity", "newspaper"):
        return (
            "CG Store Purchase Rules mein Open Tender ke main niyam yeh hain:\n\n"
            "1. **Rule 4.3.3 — applicability:** estimated value Rs. 3,00,001 ya usse zyada ho to Open Tender apply hota hai.\n"
            "2. **Publicity:** Rs. 3–5 lakh: 1 local-level newspaper; Rs. 5–10 lakh: 2 state-level newspapers; Rs. 10–20 lakh: 2 state-level + 1 national newspaper; Rs. 20 lakh se zyada: 2 state-level + 2 national newspapers.\n"
            "3. **Competition:** first Open Tender mein kam se kam 3 eligible tenderers ki participation ensure karne ka effort hona chahiye (Rule 4.3.3(d)).\n"
            "4. **Timelines (Rule 4.5):** Rs. 3,00,001 se Rs. 10 lakh tak first/second/third invitation ke liye 21/14/7 days; Rs. 10 lakh se upar 30/20/10 days.\n"
            "5. **Specifications and notice:** tender se pehle technically knowledgeable persons specifications set karein (Rule 4.1); short notice mein goods/purpose aur last date/time ho (Rules 4.4–4.4.1).\n"
            "6. **Bids and security:** offline bids same day closing ke ek ghante baad open hoti hain; late bid open nahi hoti aur return hoti hai (Rules 4.6.3–4.6.5). EMD normally estimated value ka 1% hai (Rule 4.7).\n"
            "7. **Award:** eligible successful bidder se actual purchase value ka minimum 3% security deposit PO se pehle lein; contract execute karne ke baad hi purchase order issue karein (Rules 4.7.1 and 4.13).\n\n"
            "Source: Chhattisgarh Store Purchase Rules — Rules 4, 4.1, 4.3.3, 4.4, 4.5, 4.6, 4.7, 4.7.1 and 4.13."
        )
    if has("limited tender") and has("manufacturer", "authorised representative", "registered manufacturer"):
        return "For Limited Tender, invite at least three manufacturers, authorised representatives, or registered manufacturers.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.2."
    if has("limited tender") and has("value band", "annual purchase-value", "estimated annual"):
        return "Limited Tender normally applies to estimated annual purchases from Rs. 50,001 to Rs. 3,00,000.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.2."
    if has("5 lakh se zyada", "above rs. 5 lakh") and has("10 lakh", "rs. 10 lakh") and has("newspaper", "advertise", "advertisement"):
        return "For an Open Tender above Rs. 5 lakh and up to Rs. 10 lakh, advertise in two widely circulated state-level newspapers.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.3(a)(2)."
    if has("above rs. 10 lakh", "above 10 lakh") and has("20 lakh") and has("publicity", "newspaper", "advertise"):
        return "For an Open Tender above Rs. 10 lakh and up to Rs. 20 lakh, use two widely circulated state-level newspapers and one national-level newspaper.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.3(a)(3)."
    if has("above rs. 20 lakh", "above 20 lakh") and has("publicity", "newspaper"):
        return "For an Open Tender above Rs. 20 lakh, use two widely circulated state-level newspapers and two national-level newspapers.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.3(a)(4)."
    if has("above rs. 3 lakh", "above 3 lakh") and has("5 lakh") and has("newspaper", "publicity"):
        return "For an Open Tender above Rs. 3 lakh and up to Rs. 5 lakh, publish in one widely circulated local-level newspaper.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.3(a)(1)."

    # Rule 4.3.3(c): GeM, PRC, CRAC and payment. Keep this before generic GeM routes.
    if has("provisional receipt", "prc") and has("48", "forty-eight", "within"):
        return "Issue the Provisional Receipt Certificate (PRC) within 48 hours of receiving the GeM goods.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.3(c)."
    if has("crac", "carc", "acceptance certificate") and has("payment", "pay"):
        return "Make payment within 10 days from issuance of the CRAC/CARC acceptance certificate, subject to effective GeM directions.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.3(c)."
    if has("crac", "carc", "acceptance certificate") and has("prc", "provisional receipt"):
        return "After verification, issue the Consignee Receipt and Acceptance Certificate (CRAC/CARC) within 10 days from issuance of the PRC.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.3(c)."
    if has("gem methods", "kaun-kaun se gem methods") or (has("gem par available", "goods available on gem") and has("direct purchase", "l1", "reverse auction", "e-bidding", "e bidding")):
        return "For goods available on GeM, Rule 4.3.3(c) mentions the applicable GeM methods: Direct Purchase, L1, e-bidding, and Reverse Auction.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.3.3(c)."

    # Rule 4.6 through 4.8.
    if has("deadline ke baad", "after the prescribed final date", "late tender") and has("offline", "return", "open"):
        return "An offline tender received after the final date and time must not be opened. Return it and record the return date and time on the sealed envelope.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.6.5."
    if has("offline tender") and has("opened", "open") and has("submission deadline", "closing time"):
        return "For an offline tender, open tenders one hour after the stipulated closing time on the same day. Online tenders follow the published schedule.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.6.3."
    if has("two-envelope", "two envelope") and has("emd", "exemption"):
        return "Open the EMD/exemption-certificate envelope first. Open the tender-form envelope only when sufficient EMD or a valid exemption certificate is present; otherwise reject the bid.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.6.4."
    if has("after tender finalisation", "after tender finalization") and has("emd"):
        return "After tender finalisation, retain the successful bidder's EMD and refund the other bidders' EMD within 15 days.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.7(a)."
    if has("small/cottage", "small/cottage unit", "emd exemption") and has("startup", "certificate", "proof", "tender"):
        return "A qualifying registered small/cottage unit or valid recognised startup gets EMD exemption only after submitting the required certificate/proof with the tender.\n\nSource: Chhattisgarh Store Purchase Rules — Rules 4.7(b)–(c)."
    if has("security deposit") and has("cash", "accepted in cash"):
        return "No. The prescribed security deposit or EMD must not be accepted in cash.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.8(a)."
    if has("security deposit") and has("purchase order", "before issuing", "minimum"):
        return "Before issuing the purchase order, obtain a security deposit of at least 3% of the actual purchase value from the eligible successful bidder.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.7.1."

    # Rules 4.9 to 4.14 and Rule 11.
    if has("sample") and has("quality", "inspection", "manufacturing"):
        return "If a pre-purchase sample cannot be obtained, the supplier may demonstrate the item. If demonstration is also not possible, reserve the buyer's right of inspection at the manufacturing site.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.10."
    if has("l1/lowest", "l1", "lowest tender") and has("accept", "not accept"):
        return "If the L1/lowest tender is not accepted, the purchase committee must record the reasons for non-acceptance in writing.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.12."
    if has("sufficient bids", "sufficient bids nahi", "sufficient bids not") and has("tender notice", "publish"):
        return "If sufficient bids are not received after publication, call the tender again (re-tender) and make efforts to ensure the notice reaches all potential tenderers.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.12."
    if has("purchase committee") and has("50,000", "50,000 or more", "compulsory"):
        return "An office purchasing Rs. 50,000 or more per year must form a purchase committee that includes the departmental accounts officer/accounts in-charge and officers having technical knowledge of the goods.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.12."
    if has("purchase order") and has("contract", "agreement") and has("before", "may"):
        return "No. Execute the contract with the supplier before issuing the purchase order; it should bind supply within the fixed time and to the agreed sample/specification.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.13."
    if has("repeat supply", "repeat order"):
        return "A repeat supply order cannot be issued after six months from the original order and cannot exceed 25% of the original order quantity.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 4.14."
    if has("quality inspection", "delivered goods") and has("payment", "supplier payment", "bill"):
        return "Arrange quality inspection at the delivery site within a maximum of 10 days. Pay the supplier's bill according to the rules within 20 days of receiving the goods and bill.\n\nSource: Chhattisgarh Store Purchase Rules — Rule 11."
    return None
