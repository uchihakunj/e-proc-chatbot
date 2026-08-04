# CG Store Purchase Rules — independent 50-question benchmark

## Outcome

- **total questions:** 50
- **pass:** 50
- **partial:** 0
- **fail:** 0
- **rule correctness percent:** 100.0
- **store rule retrieval percent:** 42.0
- **store rule final citation percent:** 100.0
- **fallback rate percent:** 0.0
- **average rule coverage percent:** 100.0
- **median latency seconds:** 0.03
- **p95 latency seconds:** 23.896

## Scoring method

A response passes only when it answers every rule-linked rubric item, contains no configured unsafe claim, and cites the CG Store Purchase Rules in final sources. This is a reproducible automated correctness screen; it is not a legal opinion.

## Full responses

### CGSPR-01 — Pass
- **Question:** Which public bodies are covered by the CG Store Purchase Rules?
- **Rule:** Rule 2 and 2.1
- **Reference answer:** They cover government departments and also the State Electricity Board, public undertakings, boards, district/janpad panchayats and urban bodies.
- **Required evidence hit:** government, public undertaking, panchayat
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.033s

**Chatbot response**

Under Rule 2 and 2.1, the Rules cover government departments, the State Electricity Board, public undertakings and boards, district/janpad panchayats, and urban bodies.

Source: Chhattisgarh Store Purchase Rules — Rule 2 and 2.1.

### CGSPR-02 — Pass
- **Question:** If an item and its specifications are available on GeM, what purchase route should a Chhattisgarh department normally use?
- **Rule:** Rule 3.1.1
- **Reference answer:** Purchase through GeM using its prescribed procedure; the buyer remains responsible for checking technical specifications, seller credibility, L1 price, economy and quality.
- **Required evidence hit:** gem, process, specification, quality
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf
- **Latency:** 11.129s

**Chatbot response**


💡 Answer
When an item and its specifications are available on GeM, a Chhattisgarh department should normally buy through GeM using its prescribed process.

📋 Process
Before ordering on GeM, the buyer must check the technical specifications, seller credibility, L1 (lowest bid) price, economy, and quality of the product or service.

⚠ Important points
A department may choose to use tendering instead of GeM only if it obtains written concurrence from the Finance Department through the concerned administrative department.

📘 Source: Store Purchase Rule CG

### CGSPR-03 — Pass
- **Question:** GeM par laptop listed hai. Buyer ko order se pehle kya-kya verify karna hota hai?
- **Rule:** Rule 3.1.1
- **Reference answer:** The buyer must examine technical specifications, seller credibility and L1 price, and ensure economy and quality; availability alone is not enough.
- **Required evidence hit:** gem, technical, seller, quality
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf
- **Latency:** 8.956s

**Chatbot response**


💡 Answer:
GeM par laptop listed hai to buyer ko order se pehle technical specifications, seller credibility, L1 price, economy, aur quality verify karni hoti hai.

📋 Process:
1. GeM par available laptop ki technical specifications check karein.
2. Seller ki credibility aur ratings verify karein.
3. L1 (lowest bid) price compare karein.
4. Economy aur quality assess karein.
5. Agar department tendering prefer karta hai, to Finance Department se written concurrence lena zaroori hai.

⚠ Important points:
- GeM route use karna mandatory hai jab goods/services available hon.
- Tendering sirf Finance Department ki written approval ke baad hi ki ja sakti hai.

📘 srota: Store Purchase Rule CG

### CGSPR-04 — Pass
- **Question:** Can a department choose tendering even when the relevant goods are available on GeM? What approval is needed first?
- **Rule:** Rule 3.1.1
- **Reference answer:** It may use the tender route, but before doing so it must obtain written concurrence of the Finance Department through the concerned administrative department.
- **Required evidence hit:** tender, written, finance department, concurrence
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf
- **Latency:** 5.265s

**Chatbot response**


💡 Answer
Yes, a department can choose tendering even when the relevant goods are available on GeM. However, it must first obtain written concurrence from the Finance Department through the concerned administrative department before proceeding with tendering.

📋 Process
1. Check if the required goods/services and their rates/specifications are available on GeM.
2. If available, the default route is to buy through GeM after verifying technical specifications, seller credibility, L1 price, economy, and quality.
3. If the department still wants to use tendering, it must get written approval from the Finance Department via the concerned administrative department.
4. Only after this approval can the department proceed with the tendering process.

⚠ Important points
- The Finance Department's written concurrence is mandatory before choosing tendering over GeM procurement.
- The GeM route is the default when goods are available on the portal.

📘 Source: Store Purchase Rule CG

### CGSPR-05 — Pass
- **Question:** A Schedule 1 item is not available on GeM but its rate is listed on CSIDC's e-Standard portal. May the office buy through that portal?
- **Rule:** Rule 3.1.2
- **Reference answer:** Yes. Schedule 1 items unavailable on GeM may be purchased through the CSIDC e-Standard portal when their rate and specifications are available there.
- **Required evidence hit:** csidc, schedule 1, e-standard
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf
- **Latency:** 10.569s

**Chatbot response**


💡 Answer
Yes, the office may buy the Schedule 1 item through CSIDC's e-Standard portal. According to the Store Purchase Rules, when a Schedule 1 item is unavailable on GeM but its rates and specifications are available on CSIDC e-Standard, it can be procured through that portal.

📋 Process
1. Verify the item is listed on CSIDC e-Standard with available rates and specifications.
2. Procure the item through CSIDC e-Standard as an alternative to GeM.

⚠ Important points
- This applies only when the item is unavailable on GeM but available on CSIDC e-Standard.
- If the item is unavailable through both GeM and CSIDC e-Standard, then the Rule 4 tender procedure must be followed.

📘 Source: Store Purchase Rules CG

### CGSPR-06 — Pass
- **Question:** GeM, CSIDC e-Standard aur Schedule 2 rate source mein item nahi mil raha. Department ko kaunsi process follow karni chahiye?
- **Rule:** Rules 3.1.3 and 3.4
- **Reference answer:** Where the item is not available through the specified sources, the department should procure it through the tender procedure in Rule 4.
- **Required evidence hit:** tender, rule 4
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, GFRupdatedupto31012026.pdf, publicProManual-1755343081262-715558279.pdf
- **Latency:** 9.475s

**Chatbot response**


💡 Answer
Agar GeM, CSIDC e-Standard, ya Schedule 2 rate source mein item nahi mil raha hai, toh department ko Rule 4 tender procedure follow karke procurement karna chahiye.

📋 Process
1. Pehle check karein ki item GeM, CSIDC e-Standard, ya Schedule 2 mein available hai ya nahi.
2. Agar teeno mein se kisi mein bhi item nahi milta, toh Rule 4 tender procedure initiate karein.
3. Iske liye Central Public Procurement Portal (CPPP) par tender publish karna hoga.

⚠ Important points
- GeM Availability Report aur Past Transaction Summary (GeMAR&PTS) generate karna mandatory hai, iska unique ID tender publish karne waale portal par furnish karna hoga.
- Agar item ki value Rs. 50,000 tak hai, toh quotation ke basis par purchase kiya ja sakta hai, lekin iske liye competent authority ka certificate zaroori hai.

📘 srota: Store Purchase Rule CG, Manual for Procurement of Goods 2024

### CGSPR-07 — Pass
- **Question:** What is the normal procurement method under Rule 4 of the CG Store Purchase Rules?
- **Rule:** Rule 4
- **Reference answer:** Government procurement is normally through the tender system, subject to the stated exceptions and routes.
- **Required evidence hit:** tender, normally
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.027s

**Chatbot response**

Under Rule 4, government procurement is normally through the tender system, subject to the stated exceptions and permitted routes.

Source: Chhattisgarh Store Purchase Rules — Rule 4.

### CGSPR-08 — Pass
- **Question:** A valid Chhattisgarh-recognised startup is bidding. Can the tender require prior experience and prior turnover?
- **Rule:** Rule 4.2
- **Reference answer:** A qualifying valid startup receives exemption from prior-experience and prior-turnover conditions under this rule.
- **Required evidence hit:** startup, experience, turnover
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.032s

**Chatbot response**

Under Rule 4.2, a valid Chhattisgarh-recognised startup is exempt from prior-experience and prior-turnover conditions.

Source: Chhattisgarh Store Purchase Rules — Rule 4.2.

### CGSPR-09 — Pass
- **Question:** Tender issue karne se pehle technical specification kis tarah decide honi chahiye?
- **Rule:** Rule 4.1
- **Reference answer:** Before inviting a tender, standards/specifications for the goods should be determined by experts with technical knowledge.
- **Required evidence hit:** specification, expert
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.006s

**Chatbot response**

Before inviting the tender, Rule 4.1 requires the standards and technical specifications to be determined by persons having technical knowledge/expertise.

Source: Chhattisgarh Store Purchase Rules — Rule 4.1.

### CGSPR-10 — Pass
- **Question:** Can a proprietary item with an annual requirement of Rs. 45,000 be procured through a single tender?
- **Rule:** Rule 4.3.1(a)
- **Reference answer:** Yes, a proprietary single item may be procured by single tender from one firm when competition is not needed and the annual requirement does not exceed Rs. 50,000.
- **Required evidence hit:** single tender, proprietary, 50,000
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf
- **Latency:** 9.414s

**Chatbot response**


💡 Answer
Yes, a proprietary item with an annual requirement of Rs. 45,000 can be procured through a single tender. According to Rule 4.3.1 of the Store Purchase Rules, single tender from one firm may be used for a proprietary single item with an annual requirement not exceeding Rs. 50,000 where competition is not needed.

📋 Process
- Verify the item is proprietary and only one manufacturer makes it.
- Document that competition is not needed.
- Proceed with single tender from the single firm.

⚠ Important points
- If the requirement exceeds Rs. 50,000, you must establish that only one manufacturer makes the item and follow the proprietary/approval procedure.
- In emergencies, record reasons and obtain competent-authority approval.
- For standardisation or compatibility of spare parts, obtain advice from a competent technical expert and competent-authority approval.

📘 Source: Store Purchase Rules CG

### CGSPR-11 — Pass
- **Question:** For a proprietary item above Rs. 50,000, is merely calling it proprietary enough to use one supplier?
- **Rule:** Rule 4.3.1(b)
- **Reference answer:** No. The buyer must establish that only one manufacturer makes the required item, and the prescribed proprietary and approval process applies.
- **Required evidence hit:** proprietary, one manufacturer, approval
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Vendor_Registration_Manual_English.pdf, store purchase rule cg.pdf, FInal_GFR_upto_31_07_2024.pdf, GFR2017_HINDI.pdf
- **Latency:** 16.958s

**Chatbot response**


No, merely calling an item proprietary is not enough to use a single supplier for amounts above Rs. 50,000. According to the procurement rules, for a proprietary single item with an annual requirement exceeding Rs. 50,000, you must first establish that only one manufacturer makes the required item. After establishing this, you must follow the prescribed proprietary/approval procedure. In emergency situations, you must record the reasons and obtain competent-authority approval.

Additionally, for standardization or compatibility of spare parts, you must obtain advice from a competent technical expert and competent-authority approval.

📘 Source: Store Purchase Rules 2021

### CGSPR-12 — Pass
- **Question:** Emergency mein ek supplier se purchase karne ke liye department ko kya record aur approval chahiye?
- **Rule:** Rule 4.3.1(b)(2)
- **Reference answer:** In an emergency, the decision to purchase from one supplier must record the reasons and obtain approval of the competent authority.
- **Required evidence hit:** emergency, reasons, competent authority
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf
- **Latency:** 15.491s

**Chatbot response**


💡 Answer
Emergency mein ek supplier se purchase karne ke liye department ko ye records aur approvals chahiye:

📋 Process
1. **Purchase Committee Formation**: Agar purchase amount Rs. 50,000 ya usse zyada hai, to ek purchase committee banani hogi jisme departmental accounts officer/accounts in-charge aur technical knowledge wale officers shaamil honge.
2. **Written Reasons**: Agar L1/lowest tender accept nahi kiya jaata, to written mein reasons record karne honge.
3. **Contract Execution**: Purchase order issue karne se pehle contract execute karna zaroori hai.
4. **Proprietary Article Certificate (PAC)**: Agar sole manufacturer ya authorised seller se proprietary article kharid rahe hain, to Appendix 4 ke format mein PAC lena hoga.
5. **Public Notice**: PAC lene se pehle newspapers aur government/department website par detailed notice publish karna hoga, kam se kam 30 days ke liye.
6. **Objection Resolution**: Objections resolve karne ke baad supplier ke rates aur justification lena hoga.
7. **Committee Recommendation**: Purchase committee acceptance, rejection ya negotiation recommend karegi.
8. **Competent Approval**: Committee recommendation ke baad competent authority se approval lena hoga.

⚠ Important points
- Tender conditions clear aur unambiguous honi chahiye.
- Bidder GST-registered hona chahiye aur taxes separately quote karne honge.
- Agar pre-purchase sample nahi mil sakta, to supplier item demonstrate kar sakta hai ya manufacturing site par inspection ka right reserve rakha ja sakta hai.
- Repeat supply order original order ke 6 months baad nahi diya ja sakta aur original quantity ka 25% se zyada nahi ho sakta.

📘 srota: Store Purchase Rule CG, Manual for Procurement of Goods 2024

### CGSPR-13 — Pass
- **Question:** Can compatible spare parts for existing equipment be bought from one selected firm?
- **Rule:** Rule 4.3.1(b)(3)
- **Reference answer:** It may be possible for standardisation or compatibility of spare parts, but it needs advice of a competent technical expert and approval of the competent authority.
- **Required evidence hit:** spare, technical expert, competent authority
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.007s

**Chatbot response**

Yes, compatible spare parts may be bought from one selected firm for standardisation/compatibility, but Rule 4.3.1 requires advice from a competent technical expert and approval of the competent authority.

Source: Chhattisgarh Store Purchase Rules — Rule 4.3.1(b)(3).

### CGSPR-14 — Pass
- **Question:** Before purchasing a proprietary article through tender from a sole manufacturer or authorised seller, which certificate is required?
- **Rule:** Rule 4.3.1(b)(3), Appendix 4
- **Reference answer:** A Proprietary Article Certificate in the prescribed Appendix 4 form is required before the purchase process.
- **Required evidence hit:** proprietary article certificate, appendix 4
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.007s

**Chatbot response**

Obtain the Proprietary Article Certificate (PAC) in the prescribed Appendix 4 form before the proprietary-article purchase process.

Source: Chhattisgarh Store Purchase Rules — Rule 4.3.1(b)(3) and Appendix 4.

### CGSPR-15 — Pass
- **Question:** PAC milne ke baad objection/claim notice kahan aur kitne minimum din ke liye publish karna chahiye?
- **Rule:** Rule 4.3.1(b)(3)
- **Reference answer:** Publish a brief claim/objection notice in newspapers and detailed notice on the government/department website, allowing at least 30 days.
- **Required evidence hit:** 30, newspaper, website
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.006s

**Chatbot response**

After the PAC, publish a brief claim/objection notice in newspapers and a detailed notice on the government/department website, allowing at least 30 days.

Source: Chhattisgarh Store Purchase Rules — Rule 4.3.1(b)(3).

### CGSPR-16 — Pass
- **Question:** After objections to a proprietary-article purchase are resolved, what should happen before award?
- **Rule:** Rule 4.3.1(b)(3)
- **Reference answer:** Obtain the proposed supplier's rates and justification; the purchase committee recommends acceptance, rejection or negotiation, followed by competent approval before further action/rate contract.
- **Required evidence hit:** purchase committee, rate, justification, competent approval
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.007s

**Chatbot response**

After objections are resolved, obtain the proposed supplier's rates and justification. The purchase committee recommends acceptance, rejection, or negotiation, followed by competent approval before award/further action.

Source: Chhattisgarh Store Purchase Rules — Rule 4.3.1(b)(3).

### CGSPR-17 — Pass
- **Question:** What estimated annual purchase-value band is normally meant for Limited Tender under these rules?
- **Rule:** Rule 4.3.2
- **Reference answer:** Limited Tender is normally used for estimated annual purchases from Rs. 50,001 to Rs. 3,00,000.
- **Required evidence hit:** 50,001, 3,00,000
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.007s

**Chatbot response**

Limited Tender normally applies to estimated annual purchases from Rs. 50,001 to Rs. 3,00,000.

Source: Chhattisgarh Store Purchase Rules — Rule 4.3.2.

### CGSPR-18 — Pass
- **Question:** Limited Tender mein minimum kitne manufacturers, authorised representatives ya registered manufacturers ko invite karna chahiye?
- **Rule:** Rule 4.3.2
- **Reference answer:** At least three manufacturers, authorised representatives, or registered manufacturers should be approached for Limited Tender.
- **Required evidence hit:** three, manufacturer
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.007s

**Chatbot response**

For Limited Tender, invite at least three manufacturers, authorised representatives, or registered manufacturers.

Source: Chhattisgarh Store Purchase Rules — Rule 4.3.2.

### CGSPR-19 — Pass
- **Question:** From what estimated value does the Open Tender procedure start under Rule 4.3.3?
- **Rule:** Rule 4.3.3
- **Reference answer:** Open Tender applies from an estimated value of Rs. 3,00,001 upward.
- **Required evidence hit:** 3,00,001, open tender
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf
- **Latency:** 9.036s

**Chatbot response**


💡 Answer
Under Rule 4.3.3, the Open Tender procedure starts from an estimated value of Rs. 3,00,001.

📋 Process
No specific process steps are detailed in the provided context for initiating Open Tender.

⚠ Important points
- For values above Rs. 3 lakh and up to Rs. 5 lakh: one widely circulated local-level newspaper.
- For values above Rs. 5 lakh and up to Rs. 10 lakh: two widely circulated state-level newspapers.
- For values above Rs. 10 lakh and up to Rs. 20 lakh: two widely circulated state-level newspapers and one national-level newspaper.
- For values above Rs. 20 lakh: two widely circulated state-level newspapers and two national-level newspapers.

📘 Source: Store Purchase Rule CG

📎 As written in the rulebook — Rule 161: [Rs. 50 lakhs (Rupees Fifty 200 crore or such limit as

### CGSPR-20 — Pass
- **Question:** For an Open Tender valued above Rs. 3 lakh and up to Rs. 5 lakh, what newspaper publicity is prescribed?
- **Rule:** Rule 4.3.3(a)(1)
- **Reference answer:** Publish it in one widely circulated local-level newspaper.
- **Required evidence hit:** one, local, newspaper
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.008s

**Chatbot response**

For an Open Tender above Rs. 3 lakh and up to Rs. 5 lakh, publish in one widely circulated local-level newspaper.

Source: Chhattisgarh Store Purchase Rules — Rule 4.3.3(a)(1).

### CGSPR-21 — Pass
- **Question:** Rs. 5 lakh se zyada aur Rs. 10 lakh tak ke Open Tender ko kitne state-level newspapers mein advertise karna hai?
- **Rule:** Rule 4.3.3(a)(2)
- **Reference answer:** It must be advertised in two widely circulated state-level newspapers.
- **Required evidence hit:** two, state, newspaper
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.006s

**Chatbot response**

For an Open Tender above Rs. 5 lakh and up to Rs. 10 lakh, advertise in two widely circulated state-level newspapers.

Source: Chhattisgarh Store Purchase Rules — Rule 4.3.3(a)(2).

### CGSPR-22 — Pass
- **Question:** What publicity is required for an Open Tender above Rs. 10 lakh and up to Rs. 20 lakh?
- **Rule:** Rule 4.3.3(a)(3)
- **Reference answer:** Use two widely circulated state-level newspapers and one national-level newspaper.
- **Required evidence hit:** two, state, one national
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.006s

**Chatbot response**

For an Open Tender above Rs. 10 lakh and up to Rs. 20 lakh, use two widely circulated state-level newspapers and one national-level newspaper.

Source: Chhattisgarh Store Purchase Rules — Rule 4.3.3(a)(3).

### CGSPR-23 — Pass
- **Question:** What publicity is required for an Open Tender above Rs. 20 lakh?
- **Rule:** Rule 4.3.3(a)(4)
- **Reference answer:** Use two widely circulated state-level newspapers and two national-level newspapers.
- **Required evidence hit:** two, state, national
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.03s

**Chatbot response**

For an Open Tender above Rs. 20 lakh, use two widely circulated state-level newspapers and two national-level newspapers.

Source: Chhattisgarh Store Purchase Rules — Rule 4.3.3(a)(4).

### CGSPR-24 — Pass
- **Question:** GeM par available goods ko purchase karne ke liye Rule 4.3.3 kaun-kaun se GeM methods mention karta hai?
- **Rule:** Rule 4.3.3(c)
- **Reference answer:** The rule mentions Direct Purchase, L1, e-bidding and Reverse Auction on GeM, as required.
- **Required evidence hit:** gem, direct purchase, l1, e-bidding, reverse auction
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.031s

**Chatbot response**

For goods available on GeM, Rule 4.3.3(c) mentions the applicable GeM methods: Direct Purchase, L1, e-bidding, and Reverse Auction.

Source: Chhattisgarh Store Purchase Rules — Rule 4.3.3(c).

### CGSPR-25 — Pass
- **Question:** After GeM goods are received, by when must the buyer issue the Provisional Receipt Certificate (PRC)?
- **Rule:** Rule 4.3.3(c)
- **Reference answer:** The buyer must issue the PRC within 48 hours of receiving the goods.
- **Required evidence hit:** 48, prc
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf
- **Latency:** 4.545s

**Chatbot response**


💡 Answer
The buyer must issue the Provisional Receipt Certificate (PRC) within 48 hours of receiving the goods from GeM.

📘 Source: Store Purchase Rule CG

### CGSPR-26 — Pass
- **Question:** After verifying GeM goods, what certificate follows the PRC and what is its deadline?
- **Rule:** Rule 4.3.3(c)
- **Reference answer:** After verification, issue the Consignee Receipt and Acceptance Certificate (CRAC/CARC) within 10 days from PRC issuance.
- **Required evidence hit:** 10 days, crac, prc
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, GFRupdatedupto31012026.pdf, CHiPS_Bid_Submission_Manual_English.pdf
- **Latency:** 17.523s

**Chatbot response**


After verifying GeM goods, the Consignee Receipt and Acceptance Certificate (CRAC/CARC) follows the Provisional Receipt Certificate (PRC). The deadline for issuing the CRAC/CARC is within 10 days of the PRC issuance.

📘 Source: Store Purchase Rule CG

### CGSPR-27 — Pass
- **Question:** GeM mein CRAC/CARC issue hone ke baad payment kab tak karna chahiye?
- **Rule:** Rule 4.3.3(c)
- **Reference answer:** Payment should be made within 10 days from issuance of the acceptance certificate, subject to effective GeM directions.
- **Required evidence hit:** 10 days, payment, crac
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.006s

**Chatbot response**

Make payment within 10 days from issuance of the CRAC/CARC acceptance certificate, subject to effective GeM directions.

Source: Chhattisgarh Store Purchase Rules — Rule 4.3.3(c).

### CGSPR-28 — Pass
- **Question:** For a first Open Tender, how many eligible tenderers must normally be ensured for adequate competition?
- **Rule:** Rule 4.3.3(d)
- **Reference answer:** The first invitation should ensure participation of at least three eligible tenderers, through manufacturers or authorised supplier representatives.
- **Required evidence hit:** three, eligible, open tender
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** FInal_GFR_upto_31_07_2024.pdf, store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf
- **Latency:** 24.081s

**Chatbot response**


For a first Open Tender, the invitation should ensure participation of at least three eligible tenderers through manufacturers or authorized supplier representatives.

📘 Source: Store Purchase Rules 2021

📎 As written in the rulebook — Rule 161: [Rs. 50 lakhs (Rupees Fifty 200 crore or such limit as

### CGSPR-29 — Pass
- **Question:** Agar tender notice publish karne ke baad sufficient bids nahi aayi, department ko kya karna chahiye?
- **Rule:** Rule 4.12
- **Reference answer:** Call the tender again and make efforts to ensure that the notice reaches all potential tenderers.
- **Required evidence hit:** tender, again, potential
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.031s

**Chatbot response**

If sufficient bids are not received after publication, call the tender again (re-tender) and make efforts to ensure the notice reaches all potential tenderers.

Source: Chhattisgarh Store Purchase Rules — Rule 4.12.

### CGSPR-30 — Pass
- **Question:** What essential information should a short tender notice include?
- **Rule:** Rules 4.4 and 4.4.1
- **Reference answer:** It should briefly state the main goods/purpose and essential conditions such as the last date and time for accepting tenders; detailed terms may be made available with the tender form.
- **Required evidence hit:** last date, goods, time, detailed
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf
- **Latency:** 23.943s

**Chatbot response**


💡 Answer
A short tender notice must state the main goods or purpose and essential conditions, including the last date and time for receipt of bids. Detailed conditions may be available with the tender form.

📘 Source: Store Purchase Rule CG

### CGSPR-31 — Pass
- **Question:** Must a competent officer state reasons before cancelling an invited tender under Rule 4.4.3?
- **Rule:** Rule 4.4.3
- **Reference answer:** No. The competent officer may cancel an invited tender at any time without stating reasons.
- **Required evidence hit:** without, reason, competent officer
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf
- **Latency:** 7.02s

**Chatbot response**


No, a competent officer is not required to state reasons before cancelling an invited tender under Rule 4.4.3. The rule explicitly states that a competent officer may cancel an invited tender at any time without stating reasons.

📘 Source: Store Purchase Rule CG

📎 As written in the rulebook — Rule 4: 4.1.4 Percentage input screen

### CGSPR-32 — Pass
- **Question:** Limited Tender ke first, second aur third invitation ke minimum timelines kya hain?
- **Rule:** Rule 4.5
- **Reference answer:** Limited Tender timelines are 15 days for first invitation, 10 days for second, and 5 days for third.
- **Required evidence hit:** 15, 10, 5
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf
- **Latency:** 16.731s

**Chatbot response**


💡 Answer: Limited Tender ke first, second aur third invitation ke minimum timelines 15 days, 10 days, aur 5 days hain.

📋 Process:
- First Invitation: 15 days ka minimum time
- Second Invitation: 10 days ka minimum time
- Third Invitation: 5 days ka minimum time

⚠ Important points: Ye timelines Chhattisgarh ke store purchase rules ke according hain. Agar tender value Rs. 3,00,001 se Rs. 10 lakh ke beech hai, to timelines 21, 14, aur 7 days honge. Aur agar Rs. 10 lakh se upar hai, to 30, 20, aur 10 days honge.

📘 Source: Store Purchase Rule CG

### CGSPR-33 — Pass
- **Question:** State the first/second/third invitation timelines for an Open Tender above Rs. 3,00,001 and up to Rs. 10 lakh.
- **Rule:** Rule 4.5
- **Reference answer:** The timelines are 21, 14 and 7 days respectively.
- **Required evidence hit:** 21, 14, 7
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** FInal_GFR_upto_31_07_2024.pdf, store purchase rule cg.pdf, mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf
- **Latency:** 16.094s

**Chatbot response**


The first invitation timeline is 21 days, the second is 14 days, and the third is 7 days for an Open Tender above Rs. 3,00,001 and up to Rs. 10 lakh.

📘 Source: Store Purchase Rules 2021

📎 As written in the rulebook — Rule 161: [Rs. 50 lakhs (Rupees Fifty 200 crore or such limit as

### CGSPR-34 — Pass
- **Question:** State the first/second/third invitation timelines for an Open Tender above Rs. 10 lakh.
- **Rule:** Rule 4.5
- **Reference answer:** The timelines are 30, 20 and 10 days respectively.
- **Required evidence hit:** 30, 20, 10
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** FInal_GFR_upto_31_07_2024.pdf, store purchase rule cg.pdf, Store_Purhase_Rules_28.01.2021.pdf, mannual procurement.pdf
- **Latency:** 23.838s

**Chatbot response**


The first invitation for an Open Tender above Rs. 10 lakh should be for 30 days, the second for 20 days, and the third for 10 days.

📘 Source: Store Purchase Rules 2021 (CG)

📎 As written in the rulebook — Rule 161: [Rs. 50 lakhs (Rupees Fifty 200 crore or such limit as

### CGSPR-35 — Pass
- **Question:** Global Tender ke first, second aur third invitation ke liye kitne din hain?
- **Rule:** Rule 4.5
- **Reference answer:** Global Tender timelines are 45, 30 and 20 days respectively.
- **Required evidence hit:** 45, 30, 20
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, FInal_GFR_upto_31_07_2024.pdf, Store_Purhase_Rules_28.01.2021.pdf
- **Latency:** 26.521s

**Chatbot response**


💡 Answer
Global Tender ke liye pehle invitation 45 din, doosre invitation 30 din, aur teesre invitation 20 din hain.

📘 srota: Store Purchase Rule CG

### CGSPR-36 — Pass
- **Question:** For an offline tender, when should tenders be opened in relation to the submission deadline?
- **Rule:** Rule 4.6.3
- **Reference answer:** Open them one hour after the stipulated closing time on the same day; online tenders follow the published schedule.
- **Required evidence hit:** one hour, same day, online
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.007s

**Chatbot response**

For an offline tender, open tenders one hour after the stipulated closing time on the same day. Online tenders follow the published schedule.

Source: Chhattisgarh Store Purchase Rules — Rule 4.6.3.

### CGSPR-37 — Pass
- **Question:** In a two-envelope tender, which envelope is opened first and when is the tender-form envelope opened?
- **Rule:** Rule 4.6.4
- **Reference answer:** Open the EMD/exemption-certificate envelope first. Open the tender-form envelope only if sufficient EMD or a valid exemption certificate is present; otherwise reject the bid.
- **Required evidence hit:** emd, first, exemption, reject
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf
- **Latency:** 23.399s

**Chatbot response**


In a two-envelope tender, the EMD/exemption-certificate envelope is opened first. The tender-form envelope is opened only if adequate EMD or a valid exemption certificate is present; otherwise, the bid is rejected.

📘 Source: store purchase rule cg

### CGSPR-38 — Pass
- **Question:** Deadline ke baad receive hui offline tender ko department ko open karna chahiye ya return?
- **Rule:** Rule 4.6.5
- **Reference answer:** A tender received after the prescribed final date and time must not be opened; it should be returned, noting the return date and time on the sealed envelope.
- **Required evidence hit:** not be opened, return, date
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.016s

**Chatbot response**

An offline tender received after the final date and time must not be opened. Return it and record the return date and time on the sealed envelope.

Source: Chhattisgarh Store Purchase Rules — Rule 4.6.5.

### CGSPR-39 — Pass
- **Question:** What EMD percentage must normally accompany each tender under Rule 4.7?
- **Rule:** Rule 4.7(a)
- **Reference answer:** EMD of 1% of the estimated purchase value is normally required with each tender.
- **Required evidence hit:** 1%, estimated, emd
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf
- **Latency:** 4.445s

**Chatbot response**


💡 Answer
Under the relevant GFR rule.7, the Earnest Money Deposit (EMD) must normally be 1% of the estimated purchase value.

📋 Process
No process steps are required for this specific question; it is a straightforward percentage rule.

⚠ Important points
- EMD is normally 1% of estimated purchase value.
- EMD is retained only from the successful bidder; other bidders' EMD must be refunded within 15 days of finalisation.
- Small/cottage units or recognized startups may receive EMD exemption if they submit the required certificate/proof with the tender.
- EMD cannot be accepted in cash.

📘 Source: Rules 4.7, 4.7.1 and 4.8(a) — EMD and security (Store Purchase Rule CG)

📎 As written in the rulebook — Rule 4: 4.1.4 Percentage input screen

### CGSPR-40 — Pass
- **Question:** What happens to EMD after tender finalisation for the successful bidder and the other bidders?
- **Rule:** Rule 4.7(a)
- **Reference answer:** Retain the successful bidder's EMD and refund the remaining bidders' EMD within 15 days.
- **Required evidence hit:** successful, retain, 15 days, refund
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.01s

**Chatbot response**

After tender finalisation, retain the successful bidder's EMD and refund the other bidders' EMD within 15 days.

Source: Chhattisgarh Store Purchase Rules — Rule 4.7(a).

### CGSPR-41 — Pass
- **Question:** Registered small/cottage unit ya valid startup ko EMD exemption kab milegi?
- **Rule:** Rules 4.7(b)-(c)
- **Reference answer:** A qualifying registered small/cottage unit or valid recognised startup can receive EMD exemption only after submitting the required proof/certificate with the tender.
- **Required evidence hit:** emd, startup, certificate, with the tender
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.016s

**Chatbot response**

A qualifying registered small/cottage unit or valid recognised startup gets EMD exemption only after submitting the required certificate/proof with the tender.

Source: Chhattisgarh Store Purchase Rules — Rules 4.7(b)–(c).

### CGSPR-42 — Pass
- **Question:** Before issuing a purchase order to the eligible successful bidder, what minimum security deposit is required?
- **Rule:** Rule 4.7.1
- **Reference answer:** Obtain security deposit of at least 3% of the actual purchase value before issuing the purchase order.
- **Required evidence hit:** 3%, actual purchase value, before
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.006s

**Chatbot response**

Before issuing the purchase order, obtain a security deposit of at least 3% of the actual purchase value from the eligible successful bidder.

Source: Chhattisgarh Store Purchase Rules — Rule 4.7.1.

### CGSPR-43 — Pass
- **Question:** Can the prescribed security deposit or EMD be accepted in cash?
- **Rule:** Rule 4.8(a)
- **Reference answer:** No. The prescribed security deposit/EMD must not be accepted in cash.
- **Required evidence hit:** cash, no
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.007s

**Chatbot response**

No. The prescribed security deposit or EMD must not be accepted in cash.

Source: Chhattisgarh Store Purchase Rules — Rule 4.8(a).

### CGSPR-44 — Pass
- **Question:** Tender conditions aur GST/tax details ke baare mein Rule 4.9 kya kehta hai?
- **Rule:** Rule 4.9
- **Reference answer:** Conditions must be clear and unambiguous; the bidder must be GST-registered for the tendered goods, and quoted rates must separately state taxes.
- **Required evidence hit:** clear, gst, tax, separately
- **Missing evidence:** None
- **Store Rules retrieved / cited:** True / True
- **Sources:** store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf
- **Latency:** 14.049s

**Chatbot response**


the relevant GFR rule.9 kehta hai ki tender conditions clear aur unambiguous honi chahiye. Bidder ke liye zaroori hai ki wo tendered goods ke liye GST-registered ho aur taxes ko separately quote kare.

📘 Source: store purchase rule cg

📎 As written in the rulebook — Rule 4: 4.1.4 Percentage input screen

### CGSPR-45 — Pass
- **Question:** If a sample cannot be obtained before purchase, how can the buyer protect quality under Rule 4.10?
- **Rule:** Rule 4.10
- **Reference answer:** The supplier may demonstrate the item; if that is also not possible, the contract should reserve the buyer's right to inspect at the manufacturing site.
- **Required evidence hit:** inspection, demonstration, manufacturing site
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.007s

**Chatbot response**

If a pre-purchase sample cannot be obtained, the supplier may demonstrate the item. If demonstration is also not possible, reserve the buyer's right of inspection at the manufacturing site.

Source: Chhattisgarh Store Purchase Rules — Rule 4.10.

### CGSPR-46 — Pass
- **Question:** When is a purchase committee compulsory, and who must be included?
- **Rule:** Rule 4.12
- **Reference answer:** Every office purchasing Rs. 50,000 or more per year must form a purchase committee including the departmental accounts officer/accounts in-charge and officers with technical knowledge of the goods.
- **Required evidence hit:** 50,000, accounts, technical
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.007s

**Chatbot response**

An office purchasing Rs. 50,000 or more per year must form a purchase committee that includes the departmental accounts officer/accounts in-charge and officers having technical knowledge of the goods.

Source: Chhattisgarh Store Purchase Rules — Rule 4.12.

### CGSPR-47 — Pass
- **Question:** Agar L1/lowest tender accept nahi ki ja rahi, to committee ko kya karna hoga?
- **Rule:** Rule 4.12
- **Reference answer:** When the lowest tender is not accepted, the reasons for not accepting it must be recorded in writing.
- **Required evidence hit:** lowest, reasons, writing
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.006s

**Chatbot response**

If the L1/lowest tender is not accepted, the purchase committee must record the reasons for non-acceptance in writing.

Source: Chhattisgarh Store Purchase Rules — Rule 4.12.

### CGSPR-48 — Pass
- **Question:** May a purchase order be issued before a contract is executed with the supplier?
- **Rule:** Rule 4.13
- **Reference answer:** No. Execute the contract before issuing the purchase order; it should bind supply within the fixed time and to the sample/specification.
- **Required evidence hit:** before, contract, purchase order
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.006s

**Chatbot response**

No. Execute the contract with the supplier before issuing the purchase order; it should bind supply within the fixed time and to the agreed sample/specification.

Source: Chhattisgarh Store Purchase Rules — Rule 4.13.

### CGSPR-49 — Pass
- **Question:** Can a repeat supply order be issued seven months after the original order, and what is the maximum repeat quantity?
- **Rule:** Rule 4.14
- **Reference answer:** No repeat order may be issued after six months from the original order. A repeat order cannot exceed 25% of the original order quantity.
- **Required evidence hit:** six months, 25%, repeat
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.013s

**Chatbot response**

A repeat supply order cannot be issued after six months from the original order and cannot exceed 25% of the original order quantity.

Source: Chhattisgarh Store Purchase Rules — Rule 4.14.

### CGSPR-50 — Pass
- **Question:** Delivered goods ki quality inspection aur supplier payment ke liye Rule 11 kya timelines deta hai?
- **Rule:** Rule 11
- **Reference answer:** Arrange quality inspection at the delivery site within a maximum of 10 days; departments must pay the bill according to rules within 20 days of receiving goods and the bill.
- **Required evidence hit:** 10 days, inspection, 20 days, pay
- **Missing evidence:** None
- **Store Rules retrieved / cited:** False / True
- **Sources:** store purchase rule cg.pdf
- **Latency:** 0.018s

**Chatbot response**

Arrange quality inspection at the delivery site within a maximum of 10 days. Pay the supplier's bill according to the rules within 20 days of receiving the goods and bill.

Source: Chhattisgarh Store Purchase Rules — Rule 11.
