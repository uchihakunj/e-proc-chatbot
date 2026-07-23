# Chhattisgarh e-Procurement Chatbot — Full Response Report

This report contains the complete answer returned by the live production backend for every UAT prompt, together with the expected and detected actor/intent, retrieved document families, cited source documents, and response time.

**Earlier frozen UAT scoring result:** 51 Pass / 0 Partial / 0 Fail.  
**This capture:** complete response text collected after the latest multiline procurement-method repair.

## A. Store purchase rules

### A1. Our department needs to buy 50 laptops. What should we do first?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | procurement_planning |
| Detected intent | procurement_planning |
| Retrieved document families | chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, cvc_guidance, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, procurement_manual, procurement_manual, current_procurement_rules, current_procurement_rules, other, procurement_manual |
| Source documents used | store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf |
| Response time | 2.768 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
This is the department buyer/procuring-entity workflow for laptops/computers/IT equipment. The department creates the Tender or GeM Bid; Vendors submit Bids. The buyer must not start with vendor registration or vendor-side Bid submission.

📋 Process
1. Record the need for laptops/computers/IT equipment, purpose, quantity, users and delivery timeline.
2. Prepare generic, measurable and competition-friendly specifications.
3. Estimate the cost and confirm budget availability.
4. Obtain applicable administrative approval and financial sanction.
5. Create the approved purchase indent/procurement request.
6. Check GeM and the applicable Chhattisgarh-approved purchase channel.
7. Select the lawful method under current State rules and delegated powers; Single Tender requires exceptional grounds, written justification and competent approval.
8. Publish the department Tender/GeM Bid and receive Vendor Bids.
9. Document technical/commercial evaluation and rate reasonableness.
10. Issue the Purchase Order/contract after competent approval.
11. Inspect delivery and record formal acceptance.
12. Process payment after acceptance and update the asset/stock register.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024
```

### A2. Can our department purchase laptops directly from GeM?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | gem_direct_purchase_rule |
| Detected intent | gem_direct_purchase_rule |
| Retrieved document families | chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, cvc_guidance, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, other, procurement_manual, current_procurement_rules, procurement_manual |
| Source documents used | store purchase rule cg.pdf, GFRupdatedupto31012026.pdf |
| Response time | 2.592 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Yes. A department may procure through GeM when the item or service is available there and the applicable Chhattisgarh Store Purchase Rules and current GeM/GFR provisions permit it. However, 'Direct Purchase' is one GeM method, not an automatic method for every value.

The department should apply the current monetary threshold and conditions to choose among Direct Purchase, L1 purchase, bidding, or reverse auction, obtain the required approval, and record price reasonableness. This answer does not add vendor bid-submission or post-purchase asset-accounting steps.

📘 Source: Chhattisgarh Store Purchase Rules; General Financial Rules
```

### A3. We need to buy office furniture. Which procurement method should we use?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | procurement_method_selection |
| Detected intent | procurement_method_selection |
| Retrieved document families | chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, procurement_manual, current_procurement_rules, current_procurement_rules, procurement_manual, current_procurement_rules, other |
| Source documents used | store purchase rule cg.pdf, GFRupdatedupto31012026.pdf |
| Response time | 2.631 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Do not choose one procurement method by convenience. First prepare the consolidated requirement, specifications and estimated value; check whether suitable goods are available on GeM; then apply the current Chhattisgarh rules, delegated powers and required approval. Use direct purchase, bidding, Limited Tender or Open Tender only where those conditions permit it.

📋 Process
1. Record the full requirement, specifications and estimated value.
2. Check GeM/other approved channels for suitable items.
3. Apply the applicable rules and delegated powers to select the permitted route.
4. Do not split the requirement to use a different method.
5. Record the method justification and approval before proceeding.

📘 Source: Chhattisgarh Store Purchase Rules; General Financial Rules
```

### A4. What is the difference between Open Tender and Limited Tender?

| Field | Value |
|---|---|
| Expected actor | general_information_user |
| Detected actor | general_information_user |
| Expected intent | tender_method_definition |
| Detected intent | tender_method_definition |
| Retrieved document families | current_procurement_rules, current_procurement_rules, other, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, other, procurement_manual, procurement_manual, other, current_procurement_rules |
| Source documents used | store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf |
| Response time | 2.280 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Limited Tender: A Limited Tender invites bids from a restricted list of capable or registered suppliers instead of advertising the opportunity to every bidder. It may be used only where the applicable procurement rules permit it; the procuring entity should record the basis for selecting this method and invite adequate competition.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024
```

### A5. When is Single Tender allowed?

| Field | Value |
|---|---|
| Expected actor | general_information_user |
| Detected actor | general_information_user |
| Expected intent | tender_method_definition |
| Detected intent | tender_method_definition |
| Retrieved document families | current_procurement_rules, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, procurement_manual, other, other, current_procurement_rules, procurement_manual, current_procurement_rules |
| Source documents used | store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf |
| Response time | 1.495 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Single Tender: A Single Tender seeks an offer from one identified source. It is an exceptional method, not the normal route, and requires the circumstances allowed by the applicable rules, written justification, and competent-authority approval.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024
```

### A6. Department ko 100 chairs kharidni hain. Tender karna padega ya direct purchase ho sakti hai?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | procurement_method_selection |
| Detected intent | procurement_method_selection |
| Retrieved document families | chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, current_procurement_rules, current_procurement_rules, other, other |
| Source documents used | store purchase rule cg.pdf, GFRupdatedupto31012026.pdf |
| Response time | 2.607 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Direct purchase ya Tender convenience se decide nahi hota. Pehle estimated value, GeM par item/service availability, current rules aur delegated powers check karein. In conditions se jo method permit ho wahi choose karein aur justification/approval record karein.

📋 Process
1. Consolidated requirement aur estimate record karein.
2. GeM par item availability check karein.
3. Applicable value/rule conditions ke mutabik direct purchase, bidding ya Tender method choose karein.
4. Different method use karne ke liye requirement split na karein.
5. Aage badhne se pehle approval aur method justification file par rakhein.

📘 Source: Chhattisgarh Store Purchase Rules; General Financial Rules
```

### A7. Can one government department purchase goods from another government department?

| Field | Value |
|---|---|
| Expected actor | general_information_user |
| Detected actor | general_information_user |
| Expected intent | procurement_methods_overview |
| Detected intent | procurement_methods_overview |
| Retrieved document families | chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, procurement_manual, current_procurement_rules, current_procurement_rules, procurement_manual, current_procurement_rules, current_procurement_rules |
| Source documents used | store purchase rule cg.pdf |
| Response time | 2.890 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
The Chhattisgarh Store Purchase Rules govern government procurement/purchase of stores, goods and applicable services by covered State departments and offices. They address approved channels such as GeM, Tender methods including Single/Limited/Open Tender, permitted direct or inter-departmental purchase, and controls over specifications, competition, evaluation and award.

📘 Source: Chhattisgarh Store Purchase Rules
```

### A8. Emergency situation mein department purchase kaise kare?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | procurement_method_selection |
| Detected intent | procurement_method_selection |
| Retrieved document families | chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, current_procurement_rules, current_procurement_rules, procurement_manual, current_procurement_rules, current_procurement_rules, other |
| Source documents used | store purchase rule cg.pdf |
| Response time | 2.337 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Emergency hone se Single Tender ya direct purchase automatically allowed nahi hota. Current Chhattisgarh rules aur delegated powers ke under method choose karein.

📋 Process
1. Need, urgency aur delay ka effect record karein.
2. GeM aur applicable approved purchase channel check karein.
3. Dekhein normal competition practical hai ya nahi.
4. Exceptional Single Tender/direct method zaroori ho to written justification record karke competent-authority approval lein.
5. Method decision, rate reasonableness aur approval file par rakhein.

📘 Source: Chhattisgarh Store Purchase Rules
```

### A9. Before purchasing computers, what approvals are required?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | approval_and_budget |
| Detected intent | approval_and_budget |
| Retrieved document families | chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, procurement_manual, procurement_manual, current_procurement_rules, current_procurement_rules, other, other |
| Source documents used | store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf |
| Response time | 2.468 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Before procurement, the department should establish the need, realistic estimate, available budget and the competent approvals applicable to its delegated powers.

📋 Process
1. Record the requirement and estimated cost.
2. Confirm budget availability under the correct head.
3. Obtain administrative approval for the requirement.
4. Obtain expenditure/financial sanction from the competent authority.
5. Place the approvals with the purchase indent before starting GeM or Tender action.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024
```

### A10. Purchase order issue hone ke baad next process kya hota hai?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | inspection_and_acceptance |
| Detected intent | inspection_and_acceptance |
| Retrieved document families | chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, procurement_manual, procurement_manual, other, cvc_guidance, cvc_guidance, other, other, procurement_manual, procurement_manual, procurement_manual |
| Source documents used | publicProManual-1755343081262-715558279.pdf |
| Response time | 2.122 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Purchase Order issue hone ke baad department delivery ko PO aur contract conditions ke against inspect karke formal acceptance record kare.

📋 Process
1. Delivered quantity, specifications, warranty aur condition ko PO se match karein.
2. Shortage, damage ya deviation ko inspection record mein note karein.
3. Non-compliant supply ke liye supplier se rectification ya replacement karayein.
4. Compliant supply ki receipt aur formal acceptance record banayein.
5. Acceptance aur required invoice/supporting documents ke baad payment process karke item ko stock/asset register mein enter karein.

📘 Source: Manual for Procurement of Goods 2024
```

### A11. In Chhattisgarh, what are different ways of government procurement?

| Field | Value |
|---|---|
| Expected actor | general_information_user |
| Detected actor | general_information_user |
| Expected intent | procurement_methods_overview |
| Detected intent | procurement_methods_overview |
| Retrieved document families | chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules |
| Source documents used | store purchase rule cg.pdf |
| Response time | 3.241 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Chhattisgarh government procurement can use the following routes and methods:

| Procurement route | Methods / use |
|---|---|
| GeM | Direct Purchase, L1, e-bidding and Reverse Auction |
| Tender procurement | Single Tender, Limited Tender and Open Tender |
| Foreign purchase/import | May include a Global Tender, subject to prescribed conditions and approvals |
| Permitted direct purchase | From specified government departments, undertakings or eligible bodies |
| Inter-departmental procurement | Purchase by one government department/undertaking from another |
| Special/emergency procurement | For natural-disaster or law-and-order emergencies |

GeM and the state e-Procurement portal are procurement channels; Single, Limited and Open Tender are tender methods.

📘 Source: Chhattisgarh Store Purchase Rules (updated 11 July 2024)
```

## B. Department buyer workflow

### B1. Mujhe department ke liye printer kharidna hai. Process batao.

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | procurement_planning |
| Detected intent | procurement_planning |
| Retrieved document families | chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, procurement_manual, procurement_manual, current_procurement_rules, current_procurement_rules, other, other, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules |
| Source documents used | store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf |
| Response time | 2.697 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Yeh Printer ke liye department buyer/procuring entity ka workflow hai. Department Tender ya GeM Bid create karega; Vendors Bid submit karenge. Buyer ko vendor registration ya vendor-side Bid submission se process start nahi karna hai.

📋 Process
1. Printer ki need assessment karein: purpose, users, quantity aur delivery timeline record karein.
2. Generic, measurable aur competition-friendly technical specifications banayein; brand name avoid karein.
3. Realistic estimated cost aur budget availability confirm karein.
4. Applicable administrative approval aur financial sanction lein.
5. Approved details ke saath purchase indent/procurement request create karein.
6. GeM aur applicable Chhattisgarh-approved purchase channel par availability check karein.
7. Estimated value, current State rules aur delegated powers ke hisab se lawful procurement method select karein. Single Tender normal option nahi hai; exceptional grounds, written justification aur competent approval chahiye.
8. Department Tender/GeM Bid publish karega; Vendors apni Bids submit karenge. DSC/portal credential ki requirement selected workflow aur authorized role par depend karegi.
9. Technical/commercial evaluation, competition aur rate reasonableness document karein; thresholds assume na karein.
10. Competent approval ke baad Purchase Order/contract issue karein.
11. Delivery par inspection, specification/warranty verification aur formal acceptance karein.
12. Acceptance ke baad payment process karein aur Printer ko asset/stock register mein enter karein.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024
```

### B2. Department ko software license purchase karna hai. Kya process rahega?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | procurement_planning |
| Detected intent | procurement_planning |
| Retrieved document families | chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, procurement_manual, procurement_manual, current_procurement_rules, current_procurement_rules, other, other, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules |
| Source documents used | store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf |
| Response time | 2.843 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Yeh Software ke liye department buyer/procuring entity ka workflow hai. Department Tender ya GeM Bid create karega; Vendors Bid submit karenge. Buyer ko vendor registration ya vendor-side Bid submission se process start nahi karna hai.

📋 Process
1. Software ki need assessment karein: purpose, users, quantity aur delivery timeline record karein.
2. Generic, measurable aur competition-friendly technical specifications banayein; brand name avoid karein.
3. Realistic estimated cost aur budget availability confirm karein.
4. Applicable administrative approval aur financial sanction lein.
5. Approved details ke saath purchase indent/procurement request create karein.
6. GeM aur applicable Chhattisgarh-approved purchase channel par availability check karein.
7. Estimated value, current State rules aur delegated powers ke hisab se lawful procurement method select karein. Single Tender normal option nahi hai; exceptional grounds, written justification aur competent approval chahiye.
8. Department Tender/GeM Bid publish karega; Vendors apni Bids submit karenge. DSC/portal credential ki requirement selected workflow aur authorized role par depend karegi.
9. Technical/commercial evaluation, competition aur rate reasonableness document karein; thresholds assume na karein.
10. Competent approval ke baad Purchase Order/contract issue karein.
11. Delivery par inspection, specification/warranty verification aur formal acceptance karein.
12. Acceptance ke baad payment process karein aur Software ko asset/stock register mein enter karein.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024
```

### B3. How should technical specifications for laptops be prepared?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | specification_preparation |
| Detected intent | specification_preparation |
| Retrieved document families | procurement_manual, procurement_manual, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, cvc_guidance, cvc_guidance, current_procurement_rules, current_procurement_rules, procurement_manual, procurement_manual |
| Source documents used | publicProManual-1755343081262-715558279.pdf, Compilation of CVC Circulars and Guidelines.pdf |
| Response time | 2.395 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Prepare generic, measurable and competition-friendly specifications based on the department's functional and performance need. Avoid a brand or model unless the rules permit it with recorded technical justification and an equivalent provision.

📋 Process
1. Define the required function, capacity, quality and operating environment.
2. State measurable performance, safety and compatibility parameters.
3. Use applicable standards and define tests, inspection and acceptance criteria.
4. Avoid restrictive brand-specific features that reduce competition.
5. Have the specifications reviewed by the user/technical committee before approval.

📘 Source: Manual for Procurement of Goods 2024; Compilation of CVC Circulars and Guidelines
```

### B4. Can we specify Dell laptops only?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | specification_preparation |
| Detected intent | specification_preparation |
| Retrieved document families | procurement_manual, procurement_manual, cvc_guidance, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, cvc_guidance, current_procurement_rules, current_procurement_rules, procurement_manual, procurement_manual |
| Source documents used | publicProManual-1755343081262-715558279.pdf, Compilation of CVC Circulars and Guidelines.pdf |
| Response time | 2.405 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Prepare generic, measurable and competition-friendly specifications based on the department's functional and performance need. Avoid a brand or model unless the rules permit it with recorded technical justification and an equivalent provision.

📋 Process
1. Define the required function, capacity, quality and operating environment.
2. State measurable performance, safety and compatibility parameters.
3. Use applicable standards and define tests, inspection and acceptance criteria.
4. Avoid restrictive brand-specific features that reduce competition.
5. Have the specifications reviewed by the user/technical committee before approval.

📘 Source: Manual for Procurement of Goods 2024; Compilation of CVC Circulars and Guidelines
```

### B5. Department ko AC units ka AMC karana hai. Procedure kya hai?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | procurement_planning |
| Detected intent | procurement_planning |
| Retrieved document families | chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, procurement_manual, procurement_manual, other, current_procurement_rules, current_procurement_rules, other, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules |
| Source documents used | store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf |
| Response time | 2.662 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Yeh AMC service ke liye department buyer/procuring entity ka workflow hai. Department Tender ya GeM Bid create karega; Vendors Bid submit karenge. Buyer ko vendor registration ya vendor-side Bid submission se process start nahi karna hai.

📋 Process
1. AMC service ki need assessment karein: purpose, users, quantity aur delivery timeline record karein.
2. Generic, measurable aur competition-friendly technical specifications banayein; brand name avoid karein.
3. Realistic estimated cost aur budget availability confirm karein.
4. Applicable administrative approval aur financial sanction lein.
5. Approved details ke saath purchase indent/procurement request create karein.
6. GeM aur applicable Chhattisgarh-approved purchase channel par availability check karein.
7. Estimated value, current State rules aur delegated powers ke hisab se lawful procurement method select karein. Single Tender normal option nahi hai; exceptional grounds, written justification aur competent approval chahiye.
8. Department Tender/GeM Bid publish karega; Vendors apni Bids submit karenge. DSC/portal credential ki requirement selected workflow aur authorized role par depend karegi.
9. Technical/commercial evaluation, competition aur rate reasonableness document karein; thresholds assume na karein.
10. Competent approval ke baad Purchase Order/contract issue karein.
11. Delivery par inspection, specification/warranty verification aur formal acceptance karein.
12. Acceptance ke baad payment process karein aur AMC service ko asset/stock register mein enter karein.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024
```

### B6. Can we split a purchase into smaller orders?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | procurement_planning |
| Detected intent | procurement_planning |
| Retrieved document families | chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, current_procurement_rules, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, procurement_manual, procurement_manual, current_procurement_rules, other, other, current_procurement_rules, current_procurement_rules |
| Source documents used | store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf |
| Response time | 2.915 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
This is the department buyer/procuring-entity workflow for the requested goods. The department creates the Tender or GeM Bid; Vendors submit Bids. The buyer must not start with vendor registration or vendor-side Bid submission.

📋 Process
1. Record the need for the requested goods, purpose, quantity, users and delivery timeline.
2. Prepare generic, measurable and competition-friendly specifications.
3. Estimate the cost and confirm budget availability.
4. Obtain applicable administrative approval and financial sanction.
5. Create the approved purchase indent/procurement request.
6. Check GeM and the applicable Chhattisgarh-approved purchase channel.
7. Select the lawful method under current State rules and delegated powers; Single Tender requires exceptional grounds, written justification and competent approval.
8. Publish the department Tender/GeM Bid and receive Vendor Bids.
9. Document technical/commercial evaluation and rate reasonableness.
10. Issue the Purchase Order/contract after competent approval.
11. Inspect delivery and record formal acceptance.
12. Process payment after acceptance and update the asset/stock register.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024
```

### B7. Department ko 20 desktop computers urgently chahiye. Kya options hain?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | procurement_method_selection |
| Detected intent | procurement_method_selection |
| Retrieved document families | chhattisgarh_store_purchase_rules, current_procurement_rules, procurement_manual, cvc_guidance, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, current_procurement_rules, current_procurement_rules, procurement_manual, current_procurement_rules, current_procurement_rules, other |
| Source documents used | store purchase rule cg.pdf, GFRupdatedupto31012026.pdf |
| Response time | 2.797 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Urgency ko emergency procurement exception na samjhein. Pehle need, budget aur approvals confirm karein; phir applicable rules, estimated value aur GeM availability ke mutabik lawful Tender/GeM method choose karein. Sirf urgency ke basis par Single Tender choose na karein.

📋 Process
1. Requirement, delivery deadline aur urgency ka reason record karein.
2. GeM aur normal applicable procurement route check karein.
3. Value, item availability aur current rules ke mutabik method choose karein.
4. Exceptional route tabhi use karein jab written justification aur competent approval ho.
5. Method decision aur rate-reasonableness record file par rakhein.

📘 Source: Chhattisgarh Store Purchase Rules; General Financial Rules
```

### B8. Bid evaluation kaise hoti hai?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | bid_evaluation |
| Detected intent | bid_evaluation |
| Retrieved document families | chhattisgarh_store_purchase_rules, procurement_manual, procurement_manual, current_procurement_rules, current_procurement_rules, current_procurement_rules, procurement_manual, other, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules |
| Source documents used | store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf |
| Response time | 2.539 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Bids ko published Tender criteria ke against evaluate karein: pehle eligibility, technical responsiveness, required documents aur compliance; financial bids ko Tender conditions ke mutabik evaluate karein. Sirf lowest quoted bidder automatically winner nahi hota—proposed awardee eligible, responsive aur technically acceptable bhi hona chahiye.

📋 Process
1. Bid opening record karke eligibility aur required submissions verify karein.
2. Technical specifications, Tender conditions aur compliance check karein.
3. Published criteria ke mutabik technically responsive bids identify karein.
4. Applicable case mein sirf eligible/responsive bidders ki financial bids evaluate karein.
5. Evaluated bids rank karke reasons record karein aur award se pehle competent approval lein.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024
```

### B9. Lowest bidder select karna compulsory hai kya?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | bid_evaluation |
| Detected intent | bid_evaluation |
| Retrieved document families | chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules, procurement_manual, procurement_manual, current_procurement_rules, current_procurement_rules, other, other, chhattisgarh_store_purchase_rules |
| Source documents used | store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf |
| Response time | 2.566 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Bids ko published Tender criteria ke against evaluate karein: pehle eligibility, technical responsiveness, required documents aur compliance; financial bids ko Tender conditions ke mutabik evaluate karein. Sirf lowest quoted bidder automatically winner nahi hota—proposed awardee eligible, responsive aur technically acceptable bhi hona chahiye.

📋 Process
1. Bid opening record karke eligibility aur required submissions verify karein.
2. Technical specifications, Tender conditions aur compliance check karein.
3. Published criteria ke mutabik technically responsive bids identify karein.
4. Applicable case mein sirf eligible/responsive bidders ki financial bids evaluate karein.
5. Evaluated bids rank karke reasons record karein aur award se pehle competent approval lein.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024
```

### B10. Inspection aur acceptance process kya hota hai?

| Field | Value |
|---|---|
| Expected actor | department_buyer |
| Detected actor | department_buyer |
| Expected intent | inspection_and_acceptance |
| Detected intent | inspection_and_acceptance |
| Retrieved document families | procurement_manual, procurement_manual, other, cvc_guidance, cvc_guidance, other, other, procurement_manual, procurement_manual, procurement_manual |
| Source documents used | publicProManual-1755343081262-715558279.pdf |
| Response time | 2.180 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Purchase Order issue hone ke baad department delivery ko PO aur contract conditions ke against inspect karke formal acceptance record kare.

📋 Process
1. Delivered quantity, specifications, warranty aur condition ko PO se match karein.
2. Shortage, damage ya deviation ko inspection record mein note karein.
3. Non-compliant supply ke liye supplier se rectification ya replacement karayein.
4. Compliant supply ki receipt aur formal acceptance record banayein.
5. Acceptance aur required invoice/supporting documents ke baad payment process karke item ko stock/asset register mein enter karein.

📘 Source: Manual for Procurement of Goods 2024
```

## C. Vendor registration & participation

### C1. How do I register as a vendor?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | vendor_registration |
| Detected intent | vendor_registration |
| Retrieved document families | vendor_registration_manual, vendor_registration_manual, department_tender_creation_manual, chips_auction_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual, emd_refund_notice, vendor_registration_manual |
| Source documents used | CHiPS_Vendor_Registration_Manual_English.pdf |
| Response time | 1.614 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
A new domestic supplier registers through the CHiPS e-Procurement portal's New Supplier Registration workflow.

📋 Process
1. Select New Supplier Registration on the portal.
2. Enter the supplier's PAN details.
3. Upload the CRN certificate where the applicable vendor class requires it.
4. Create the preferred login code and enter the business/contact details.
5. Review and submit the registration, then complete the valid DSC mapping required for authenticated portal transactions.

📘 Source: Vendor Registration Manual (CHiPS)
```

### C2. New supplier registration ke liye kaunse documents chahiye?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | vendor_registration_documents |
| Detected intent | vendor_registration_documents |
| Retrieved document families | vendor_registration_manual, vendor_registration_manual, department_tender_creation_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual, emd_online_payment_manual, emd_refund_notice |
| Source documents used | CHiPS_Vendor_Registration_Manual_English.pdf |
| Response time | 1.603 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
New domestic supplier ke liye required registration documents/details PAN Card information, Vendor Class A, B, C ya D hone par scanned CRN Certificate, preferred login code aur bidding ke liye business coordinates hain.

📋 Process
1. PAN Card information ready rakhein.
2. Applicable ho to Vendor Class A–D ka CRN Certificate scan rakhein.
3. Preferred login code choose karein.
4. Authorised-signatory, contact, bank, vendor-business aur partner details entry ke liye ready rakhein.
5. New Supplier Registration mein details enter karke validation ke baad save/continue karein.

📘 Source: Vendor Registration Manual (CHiPS)
```

### C3. Vendor password bhool gaya hoon. Kya karun?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | password_recovery |
| Detected intent | password_recovery |
| Retrieved document families | vendor_registration_manual, vendor_registration_manual, chips_corrigendum_manual, chips_corrigendum_manual, faq, faq, bid_submission_manual, bid_submission_manual, vendor_registration_manual |
| Source documents used | CHiPS_Vendor_Registration_Manual_English.pdf |
| Response time | 3.660 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text

💡 AnswerVendor password bhool gaya hai to aap ye steps follow kar sakte hain:1. CHiPS portal par login karein2. "Forgot Password" ya "Reset Password" option dhundhein3. Apna registered email ID enter karein4. Reset link receive karke password set karein5. Login karke registration process complete karein

📋 Process1. CHiPS portal par jao2. Login section mein "Forgot Password" par click karein3. Apna email ID enter karein4. Email mein mile reset link par click karein5. Naya password set karein6. Login karke registration complete karein

📘 Source: CHiPS_Vendor_Registration_Manual_English.pdfCHiPS_Vendor_Registration_Manual_English.pdf se liya gaya hai.
```

### C4. DSC kaise obtain karun?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | dsc_obtainment |
| Detected intent | dsc_obtainment |
| Retrieved document families | vendor_registration_manual, vendor_registration_manual, bid_submission_manual, bid_submission_manual, department_tender_creation_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual |
| Source documents used | CHiPS_Vendor_Registration_Manual_English.pdf, CHiPS_Bid_Submission_Manual_English.pdf |
| Response time | 3.128 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text

💡 AnswerDSC (Digital Signature Certificate) obtain karne ke liye, foreign vendors ko Indian embassy se Class II ya III digital certificate ke liye apply karna hoga. Iske liye Organization/Enterprise ka certified true copy document chahiye, jaise ki Company Secretary, Director, ya Partner ka Certificate of Incorporation, Memorandum and Articles of Association, Registered Partnership Deed, ya valid Business License. DSC Class II ya Class III (Signing & Encryption) ka hona zaroori hai.

📋 Process1. Foreign vendor ko Indian embassy se contact karna hoga.2. Organization/Enterprise ka certified true copy document submit karna hoga.3. Embassay se Class II ya III digital certificate ke liye apply karna hoga.4. DSC Class II ya Class III (Signing & Encryption) ka certificate mil jayega.

📘 Source: CHiPS_Vendor_Registration_Manual_English.pdf, CHiPS_Bid_Submission_Manual_English.pdf.
```

### C5. Renewed DSC ko portal par map kaise karun?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | dsc_mapping |
| Detected intent | dsc_mapping |
| Retrieved document families | vendor_registration_manual, vendor_registration_manual, vendor_registration_manual, bid_submission_manual, bid_submission_manual, department_tender_creation_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual, vendor_registration_manual, vendor_registration_manual |
| Source documents used | CHiPS_Vendor_Registration_Manual_English.pdf |
| Response time | 1.438 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Bid submit karne se pehle valid DSC ko registered bidder account ke saath map/register karein.

📋 Process
1. DSC token drivers aur required portal signing utility install karein.
2. Valid signing/encryption DSC insert karke registered bidder account se login karein.
3. DSC registration/mapping option kholkar correct certificate select karein.
4. Prompt par authenticate/sign karke mapping submit karein.
5. Portal par DSC registered confirmation check karein; renewed/replaced DSC ko Bid se pehle dobara map karein.

📘 Source: Vendor Registration Manual (CHiPS)
```

### C6. Can a startup participate in tenders?

| Field | Value |
|---|---|
| Expected actor | general_information_user |
| Detected actor | general_information_user |
| Expected intent | tender_eligibility |
| Detected intent | tender_eligibility |
| Retrieved document families | bid_submission_manual, bid_submission_manual, vendor_registration_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual, emd_refund_notice, emd_online_payment_manual, bid_submission_manual, bid_submission_manual |
| Source documents used | CHiPS_Bid_Submission_Manual_English.pdf |
| Response time | 2.773 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text

💡 AnswerYes, a startup can participate in tenders. The documents specify that in an Open Tender, both existing and new vendors (which includes startups) are allowed to participate. However, new vendors, including startups, must first register in the e-Procurement system to be eligible for bidding.

📋 Process1. Register as a new vendor in the e-Procurement system.2. Ensure all required documents and credentials are uploaded.3. Participate in the Open Tender process.

📘 Source: CHiPS_Bid_Submission_Manual_English.pdf
```

### C7. Foreign company tender mein participate kaise kare?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | vendor_registration |
| Detected intent | vendor_registration |
| Retrieved document families | vendor_registration_manual, vendor_registration_manual, department_tender_creation_manual, chips_auction_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_refund_notice, emd_online_payment_manual, vendor_registration_manual, vendor_registration_manual |
| Source documents used | CHiPS_Vendor_Registration_Manual_English.pdf |
| Response time | 1.783 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Foreign company ke liye domestic New Supplier Registration steps ko automatically applicable na maanein. Pehle specific Tender mein foreign-bidder participation, eligibility, required documents, currency aur registration/DSC instructions check karein. Tender mein permission aur portal procedure clearly stated ho tabhi uske mutabik aage badhein.

📘 Source: Vendor Registration Manual (CHiPS)
```

### C8. Technical bid aur financial bid mein kya difference hai?

| Field | Value |
|---|---|
| Expected actor | general_information_user |
| Detected actor | general_information_user |
| Expected intent | general_bid_information |
| Detected intent | general_bid_information |
| Retrieved document families | procurement_manual, procurement_manual, bid_submission_manual, chips_corrigendum_manual, emd_online_payment_manual, emd_online_payment_manual, other, other, procurement_manual, procurement_manual |
| Source documents used | publicProManual-1755343081262-715558279.pdf, CHiPS_Bid_Submission_Manual_English.pdf |
| Response time | 4.360 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text

💡 AnswerTechnical bid aur financial bid mein main difference hai ki technical bid mein aap apne product ya service ki technical details, quality, aur specifications batate hain, jabki financial bid mein aap apni price ya cost ka detail dete hain. Technical bid se yeh pata chalta hai ki aapka solution technically kitna sahi hai, aur financial bid se yeh pata chalta hai ki aapki price kitni competitive hai.

📋 Process1. Pehle aap technical bid prepare karte hain jismein aapke product ki details, quality, aur technical specifications hoti hain.2. Phir aap financial bid prepare karte hain jismein aapki price, payment terms, aur financial details hoti hain.3. Dono bids ko alag-alag submit karna hota hai, technical bid pehle open hoti hai aur uske baad financial bid open hoti hai.

📘 Source: CHiPS_Bid_Submission_Manual_English.pdf

Note: Yeh information public procurement process ke according hai. Agar aapko koi specific tender ke baare mein jaankari chahiye to official CHiPS website ya contact kar sakte hain.
```

### C9. Tender eligibility criteria kaise check karun?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | tender_eligibility |
| Detected intent | tender_eligibility |
| Retrieved document families | bid_submission_manual, bid_submission_manual, vendor_registration_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual, emd_refund_notice, emd_online_payment_manual, bid_submission_manual, bid_submission_manual |
| Source documents used | CHiPS_Bid_Submission_Manual_English.pdf |
| Response time | 4.699 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text

💡 AnswerTender eligibility criteria check karne ke liye, aapko CHiPS portal par login karna hoga aur tender details dekhni hongi. Agar aapko restricted tender mein participate karna hai, toh vendor category (Class A, B, C, D, E, ya F) aapki eligibility decide karti hai. Short tender mein techno-commercial aur price bid dono ek saath open hote hain. System administrator internet failure ya technical issues ke case mein timeline extend kar sakta hai.

📋 Process1. CHiPS e-Procurement portal par login karein.2. Tender section mein jaakar eligibility criteria check karein.3. Agar restricted tender hai, toh apni vendor category verify karein.4. Short tender ke liye techno-commercial aur price bid dono prepare karein.5. Agar portal mein koi issue hai, toh system admin se timeline extension ke liye request karein.

📘 Source: CHiPS_Bid_Submission_Manual_English.pdf, Supplier Manual, Regional & Language Format Settings.
```

### C10. Vendor registration approve hone mein kitna time lagta hai?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | vendor_registration |
| Detected intent | vendor_registration |
| Retrieved document families | vendor_registration_manual, vendor_registration_manual, department_tender_creation_manual, chips_auction_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual, emd_online_payment_manual, vendor_registration_manual, vendor_registration_manual |
| Source documents used | CHiPS_Vendor_Registration_Manual_English.pdf |
| Response time | 1.702 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Naya domestic supplier CHiPS e-Procurement portal ke New Supplier Registration workflow se register karta hai.

📋 Process
1. Portal par New Supplier Registration select karein.
2. Supplier ka PAN detail enter karein.
3. Applicable Vendor Class mein zaroori ho to CRN certificate upload karein.
4. Preferred login code banayein aur business/contact details fill karein.
5. Details review karke registration submit karein aur authenticated portal transactions ke liye required valid DSC mapping complete karein.

📘 Source: Vendor Registration Manual (CHiPS)
```

## D. EMD & bid submission

### D1. I need to pay ?50,000 EMD by 15 June 2026. How do I do it?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | emd_payment |
| Detected intent | emd_payment |
| Retrieved document families | emd_online_payment_manual, emd_online_payment_manual, bid_submission_manual, department_tender_creation_manual, vendor_registration_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual, emd_online_payment_manual, emd_online_payment_manual |
| Source documents used | EMD_CHALLAN_PAYMENT_V1.0.pdf |
| Response time | 1.903 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Use the amount and deadline in the specific tender: the tender-specified amount, payable by 15 June 2026. Values visible in manual screenshots are examples and must not replace the tender value.

Process
1. Open the relevant tender in the e-Procurement portal and select its payment option.
2. Select EMD/Bid Security and enter the tender-specified amount.
3. Use only the payment mode enabled for that tender, complete the transaction, and do not leave the page until the portal returns a status.
4. Confirm that the payment status is successful before submitting the bid. If the portal shows a different amount or mode, stop and verify the tender notice or contact the department.

📘 Source: EMD CHALLAN PAYMENT V1.0
```

### D2. EMD payment fail ho gaya but paisa debit ho gaya. Kya karun?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | emd_payment_failure |
| Detected intent | emd_payment_failure |
| Retrieved document families | emd_online_payment_manual, emd_online_payment_manual, chips_corrigendum_manual, chips_corrigendum_manual, faq, bid_submission_manual, department_tender_creation_manual, bid_submission_manual, emd_online_payment_manual |
| Source documents used | EMD_CHALLAN_PAYMENT_V1.0.pdf |
| Response time | 2.225 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Agar EMD/Bid Security eChallan payment fail hone ke baad amount debit ho gaya aur Tender ki Bid Due Date tak beneficiary account mein credit nahi hota, payment source account mein return ho sakta hai aur Bid unpaid ya reject treat ho sakti hai. Screenshot ki amount/date use na karein; specific Tender control karta hai.

📋 Process
1. Relevant Tender mein transaction aur EMD/Bid Security payment status check karein.
2. Credited amount aur time ko us Tender ki current Bid Due Date se compare karein.
3. Same challan ko kisi doosre Tender ke liye re-use na karein.
4. Status Successful na ho ya credit beneficiary tak na pahunche to receipt/reference preserve karke Bid submit karne se pehle Tender ke official payment-support route ka use karein.

📘 Source: EMD CHALLAN PAYMENT V1.0
```

### D3. EMD refund kab milega?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | emd_refund_unsuccessful_bidder |
| Detected intent | emd_refund_unsuccessful_bidder |
| Retrieved document families | emd_refund_notice, emd_refund_notice, procurement_manual, procurement_manual, chips_corrigendum_manual, chips_corrigendum_manual, bid_submission_manual, department_tender_creation_manual, emd_refund_notice |
| Source documents used | Online_EMD_Refund_Notice.pdf |
| Response time | 1.718 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Unsuccessful bidder ki EMD refund process applicable Bid opening/evaluation stage ke baad Department Admin initiate karta hai.

📋 Process
1. Department Admin eligible unsuccessful bidder ki EMD select kare.
2. Department Approver refund verify karke approve kare.
3. e-Procurement system approved refund instruction bank ko bheje.
4. Amount bidder ke registered bank account mein credit hone ke baad portal status check karein.

📘 Source: EMD Refund Guidelines (CHiPS)
```

### D4. L1 bidder ki EMD ka kya hota hai?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | emd_refund_l1_bidder |
| Detected intent | emd_refund_l1_bidder |
| Retrieved document families | procurement_manual, procurement_manual, emd_refund_notice, other, current_procurement_rules, current_procurement_rules, current_procurement_rules, current_procurement_rules, procurement_manual, procurement_manual |
| Source documents used | publicProManual-1755343081262-715558279.pdf |
| Response time | 2.306 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
L1/successful bidder ki EMD unsuccessful-bidder refund flow se process nahi hoti. Tender Owner/Department Admin online contract create aur approve hone ke baad EMD Department ko remit kar sakta hai, ya required Performance Bank Guarantee receive hone aur online contract approve hone par L1 bidder ke registered bank account mein refund initiate kar sakta hai.

📘 Source: Manual for Procurement of Goods 2024
```

### D5. Kya MSME ko EMD exemption mil sakta hai?

| Field | Value |
|---|---|
| Expected actor | general_information_user |
| Detected actor | general_information_user |
| Expected intent | emd_exemption |
| Detected intent | emd_exemption |
| Retrieved document families | current_procurement_rules, procurement_manual, chhattisgarh_store_purchase_rules, current_procurement_rules, current_procurement_rules, current_procurement_rules, current_procurement_rules, other |
| Source documents used | GFRupdatedupto31012026.pdf, publicProManual-1755343081262-715558279.pdf |
| Response time | 2.243 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Haan. Applicable GFR provision ke under MSE Procurement Policy ke covered Micro and Small Enterprises (MSEs), ya Central Purchase Organisation ya concerned Ministry/Department ke saath registered MSEs ko Bid Security/EMD se exemption milti hai. Exemption claim karne se pehle Tender notice ki eligibility aur required proof verify karein.

📘 Source: General Financial Rules; Manual for Procurement of Goods 2024
```

### D6. Bid submit karne ka complete process batao.

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | bid_submission_portal_steps |
| Detected intent | bid_submission_portal_steps |
| Retrieved document families | bid_submission_manual, bid_submission_manual, chips_corrigendum_manual, chips_corrigendum_manual, vendor_registration_manual, emd_refund_notice, vendor_registration_manual, emd_online_payment_manual, bid_submission_manual, bid_submission_manual |
| Source documents used | CHiPS_Bid_Submission_Manual_English.pdf |
| Response time | 1.592 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Aap Vendor/Bidder side par hain, isliye aap Department ki published Tender mein Bid submit karenge. CHiPS e-Procurement secured site par participation ke liye registered bidder login aur Bid Submission Manual ke mutabik valid signing/encryption DSC chahiye.

📋 Process
1. Agar registration pending hai to portal ke New User link se Vendor registration complete karein.
2. Apna signing/encryption DSC register karke secured portal par login karein.
3. Tenders > View mein relevant Tender/NIT search karein aur open/restricted/short Tender ke liye Interested select karein.
4. Tender ki eligibility, dates, corrigenda aur conditions padhein; I Agree/Accept karein.
5. NIT ke mutabik Tender/processing fee aur EMD/Bid Security ki applicable process complete karein.
6. My Live Tender > View Tender > Respond to Tender/NIT kholein.
7. Add Quotation mein pre-qualification/techno-commercial details aur required documents upload karein.
8. Price Bid screen mein quoted rates bharein, sab entries/documents review karein aur deadline se pehle DSC ke saath Bid submit karein.
9. Portal acknowledgement/status save karein; Department evaluation karega.

📘 Source: Bid Submission Manual (CHiPS), Sections 1, 3 and 4 (pages 4, 17-27 and 36-40); Vendor Registration Manual (CHiPS)
```

### D7. Can I modify my bid after submission?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | bid_submission_portal_steps |
| Detected intent | bid_submission_portal_steps |
| Retrieved document families | bid_submission_manual, bid_submission_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual, emd_online_payment_manual, chips_auction_manual, emd_refund_notice, bid_submission_manual |
| Source documents used | CHiPS_Bid_Submission_Manual_English.pdf |
| Response time | 1.618 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Before the bid-submission deadline, a bidder may substitute, alter or modify a Bid; the last submitted Bid is treated as valid. A Bid may also be withdrawn before the deadline. These actions are not permitted after the deadline.

📋 Process
1. Sign in and open the relevant submitted Tender/Bid.
2. Use the available Modify or Withdraw action before the deadline.
3. Update the required technical documents and Price Bid.
4. Review everything, sign with the DSC and re-submit the revised Bid before the deadline.
5. Save the new acknowledgement and confirm that the revised Bid is the latest submission.

📘 Source: Manual for Procurement of Goods 2024; CHiPS Bid Submission Manual
```

### D8. Bid deadline ke baad bid edit kar sakte hain kya?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | bid_submission_portal_steps |
| Detected intent | bid_submission_portal_steps |
| Retrieved document families | bid_submission_manual, bid_submission_manual, bid_submission_manual, bid_submission_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_refund_notice, vendor_registration_manual, emd_online_payment_manual, vendor_registration_manual, bid_submission_manual, bid_submission_manual |
| Source documents used | CHiPS_Bid_Submission_Manual_English.pdf |
| Response time | 2.115 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Aap Vendor/Bidder side par hain, isliye aap Department ki published Tender mein Bid submit karenge. CHiPS e-Procurement secured site par participation ke liye registered bidder login aur Bid Submission Manual ke mutabik valid signing/encryption DSC chahiye.

📋 Process
1. Agar registration pending hai to portal ke New User link se Vendor registration complete karein.
2. Apna signing/encryption DSC register karke secured portal par login karein.
3. Tenders > View mein relevant Tender/NIT search karein aur open/restricted/short Tender ke liye Interested select karein.
4. Tender ki eligibility, dates, corrigenda aur conditions padhein; I Agree/Accept karein.
5. NIT ke mutabik Tender/processing fee aur EMD/Bid Security ki applicable process complete karein.
6. My Live Tender > View Tender > Respond to Tender/NIT kholein.
7. Add Quotation mein pre-qualification/techno-commercial details aur required documents upload karein.
8. Price Bid screen mein quoted rates bharein, sab entries/documents review karein aur deadline se pehle DSC ke saath Bid submit karein.
9. Portal acknowledgement/status save karein; Department evaluation karega.

📘 Source: Bid Submission Manual (CHiPS), Sections 1, 3 and 4 (pages 4, 17-27 and 36-40); Vendor Registration Manual (CHiPS)
```

### D9. Technical bid submit ho gayi hai. Financial bid kaise submit karun?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | bid_submission_portal_steps |
| Detected intent | bid_submission_portal_steps |
| Retrieved document families | bid_submission_manual, bid_submission_manual, vendor_registration_manual, vendor_registration_manual, chips_auction_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_refund_notice, bid_submission_manual, bid_submission_manual |
| Source documents used | CHiPS_Bid_Submission_Manual_English.pdf |
| Response time | 2.358 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Aap Vendor/Bidder side par hain, isliye aap Department ki published Tender mein Bid submit karenge. CHiPS e-Procurement secured site par participation ke liye registered bidder login aur Bid Submission Manual ke mutabik valid signing/encryption DSC chahiye.

📋 Process
1. Agar registration pending hai to portal ke New User link se Vendor registration complete karein.
2. Apna signing/encryption DSC register karke secured portal par login karein.
3. Tenders > View mein relevant Tender/NIT search karein aur open/restricted/short Tender ke liye Interested select karein.
4. Tender ki eligibility, dates, corrigenda aur conditions padhein; I Agree/Accept karein.
5. NIT ke mutabik Tender/processing fee aur EMD/Bid Security ki applicable process complete karein.
6. My Live Tender > View Tender > Respond to Tender/NIT kholein.
7. Add Quotation mein pre-qualification/techno-commercial details aur required documents upload karein.
8. Price Bid screen mein quoted rates bharein, sab entries/documents review karein aur deadline se pehle DSC ke saath Bid submit karein.
9. Portal acknowledgement/status save karein; Department evaluation karega.

📘 Source: Bid Submission Manual (CHiPS), Sections 1, 3 and 4 (pages 4, 17-27 and 36-40); Vendor Registration Manual (CHiPS)
```

### D10. How do I participate in an e-auction?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | auction_participation |
| Detected intent | auction_participation |
| Retrieved document families | chips_auction_manual, chips_auction_manual, vendor_registration_manual, bid_submission_manual, bid_submission_manual, emd_online_payment_manual, vendor_registration_manual, chips_corrigendum_manual, chips_corrigendum_manual |
| Source documents used | AuctionManual_FA.pdf |
| Response time | 4.560 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text

💡 AnswerTo participate in an e-auction, you must first log in to the Chhattisgarh E-Procurement portal using your user-id, password, and Digital Signature Certificate (DSC). After logging in, right-click on the "Auction" tab and open it in a new tab/window. If the auction engine prompts, use the old password "Password@123" to change it. Then, select the specific auction from the dashboard and click on "View/Respond to RFX." You must quote a bid above the opening price and a multiple of the minimum bid change price; if no opening price exists, consider it as '0'. During the auction, you can only view the H1 price and your ranking. The auction page auto-refreshes every minute with updated bidding status. After the auction concludes, the results are displayed on the same page.

📋 Process1. Log in to the portal with user-id, password, and DSC.2. Right-click on the "Auction" tab and open it in a new tab/window.3. If prompted, change the password using the old password "Password@123".4. Select the relevant auction and click on "View/Respond to RFX."5. Submit a bid above the opening price and a multiple of the minimum bid change price (consider opening price as '0' if none).6. During the auction, only H1 price and ranking are visible.7. The page auto-refreshes every minute with updated bidding status.8. After the auction ends, view the results on the same page.

📘 Source: e-Auction Manual (FA)Source: AuctionManual_FA.pdf
```

## E. Department operator / portal operations

### E1. How do I create a tender on the portal?

| Field | Value |
|---|---|
| Expected actor | department_operator |
| Detected actor | department_operator |
| Expected intent | tender_creation_portal_steps |
| Detected intent | tender_creation_portal_steps |
| Retrieved document families | procurement_manual, department_tender_creation_manual, chips_corrigendum_manual, emd_online_payment_manual, chips_corrigendum_manual, procurement_manual, emd_refund_notice, emd_online_payment_manual, other, department_tender_creation_manual |
| Source documents used | Manual_Offline_Tenders_v.1.0.pdf, publicProManual-1755343081262-715558279.pdf |
| Response time | 1.884 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
The available CHiPS manual specifically covers uploading Manual/Offline Tender details.

📋 Process
1. Sign in as an authorised department Tender Creator.
2. Open Offline Tender under the Tender(s) menu.
3. In Manual Tender Header Detail, enter the bid parts, NIT reference, tender call number, description, PAC, office/division, and bid dates.
4. Save the details; then complete the applicable attachments, required bidder documents, and payment details before continuing through the authorised DSC/workflow.

This manual is for offline/manual tender upload. If the portal has a separate module for normal online Tender creation, follow that module's official manual.

📘 Source: Offline Tender Upload Manual (CHiPS); Manual for Procurement of Goods 2024
```

### E2. Department operator tender publish kaise kare?

| Field | Value |
|---|---|
| Expected actor | department_operator |
| Detected actor | department_operator |
| Expected intent | tender_publication_portal_steps |
| Detected intent | tender_publication_portal_steps |
| Retrieved document families | procurement_manual, department_tender_creation_manual, procurement_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual, emd_online_payment_manual, other, cvc_guidance, department_tender_creation_manual |
| Source documents used | Manual_Offline_Tenders_v.1.0.pdf, publicProManual-1755343081262-715558279.pdf |
| Response time | 2.110 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Tender Owner completed Tender/NIT, dates, documents aur approvals check karne ke baad hi publish kare. Available CHiPS manual offline Tender record prepare/save karna support karta hai; Advance Search ko publication step nahi batata.

📋 Process
1. Authorised Tender Creator/Department account se login karke Tender(s) > Offline Tender kholein.
2. NIT reference, Bid parts, description, PAC aur Bid dates sahit Manual Tender Header Detail verify karke save karein.
3. Required Tender attachments, bidder-document requirements aur applicable payment/evaluation details add karke save karein.
4. Completed Tender ko approved NIT se review karke dates aur attachments final confirm karein.
5. Authorised portal workflow se completed Tender route/publish karein aur designated portal par published Tender visible hona verify karein.
6. Publication acknowledgement aur approved Tender record preserve karein.

📘 Source: Offline Tender Upload Manual (CHiPS); Manual for Procurement of Goods 2024
```

### E3. Offline tender upload kaise karte hain?

| Field | Value |
|---|---|
| Expected actor | department_operator |
| Detected actor | department_operator |
| Expected intent | tender_creation_portal_steps |
| Detected intent | tender_creation_portal_steps |
| Retrieved document families | department_tender_creation_manual, department_tender_creation_manual, procurement_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual, emd_online_payment_manual, other, other, department_tender_creation_manual |
| Source documents used | Manual_Offline_Tenders_v.1.0.pdf |
| Response time | 2.084 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Available CHiPS manual specifically Manual/Offline Tender details upload karne ka process cover karta hai.

📋 Process
1. Authorised department operator Tender Creator ke roop mein login kare.
2. Tender(s) menu mein Offline Tender open kare.
3. Manual Tender Header Detail mein bid parts, NIT reference, tender call number, description, PAC, office/division aur bid dates fill kare.
4. Details Save kare; phir applicable tabs mein attachments, required bidder documents aur payment details complete karke authorised DSC/workflow se aage badhe.

Yeh manual offline/manual tender upload ke liye hai. Normal online Tender creation ka alag portal module ho to uska official manual follow karein.

📘 Source: Offline Tender Upload Manual (CHiPS)
```

### E4. Technical bids kaise open karte hain?

| Field | Value |
|---|---|
| Expected actor | department_operator |
| Detected actor | department_operator |
| Expected intent | bid_opening_portal_steps |
| Detected intent | bid_opening_portal_steps |
| Retrieved document families | department_tender_creation_manual, procurement_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual, emd_online_payment_manual, cvc_guidance, other, department_tender_creation_manual |
| Source documents used | Manual_Offline_Tenders_v.1.0.pdf, publicProManual-1755343081262-715558279.pdf |
| Response time | 3.918 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text

💡 AnswerTechnical bids open karne ke liye, Department Admin ko e-Procurement portal par login karna padta hai. Phir, unhe 'Tender' module mein jaana hoga aur specific tender select karna hoga. Uske baad, 'Technical Bid' ya 'PQ Bid' section mein jaakar, unhe bid open karne ka option dikhega. Department Admin ko bid open karne se pehle sabhi technical details aur compliance documents check karne chahiye.

📋 Process1. e-Procurement portal par login karein.2. 'Tender' module mein jaayen.3. Jis tender ka technical bid open karna hai, use select karein.4. 'Technical Bid' ya 'PQ Bid' section mein jaayen.5. Bid open karne ke liye option select karein.6. Sabhi technical details aur compliance documents verify karein.7. Bid open karne ki process complete karein.

📘 Source: Manual_Offline_Tenders_v.1.0.pdf, publicProManual-1755343081262-715558279.pdf

Note: Yeh process CHiPS system ke andar ek internal procedure hai.
```

### E5. Price bid opening process kya hai?

| Field | Value |
|---|---|
| Expected actor | department_operator |
| Detected actor | department_operator |
| Expected intent | bid_opening_portal_steps |
| Detected intent | bid_opening_portal_steps |
| Retrieved document families | procurement_manual, procurement_manual, procurement_manual, department_tender_creation_manual, chips_corrigendum_manual, chips_corrigendum_manual, emd_online_payment_manual, emd_online_payment_manual, other, procurement_manual, procurement_manual |
| Source documents used | publicProManual-1755343081262-715558279.pdf |
| Response time | 3.988 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text

💡 AnswerPrice bid opening process mein techno-commercial aur price bids online open kiye jaate hain. System scrutiny reports aur price comparative statement generate karta hai, aur bid openers in reports ko download karke sign karte hain. Price bids tabhi open hote hain jab technical shortlisting complete ho jaati hai.

📋 Process1. Techno-commercial aur price bids online open kiye jaate hain.2. System scrutiny reports aur price comparative statement generate karta hai.3. Bid openers reports download karke sign karte hain.4. Technical shortlisting ke baad hi price bids open hote hain.

📘 Source: Manual for Procurement of Goods 2024, Appendix 3CHiPS Manual (English)Manual for Procurement of Goods 2024Appendix 3: authorised bid openers open the techno-commercial and price bids online.The system generates scrutiny reports and a price comparative statement; the bid openers download and sign the reports for further processing.Price bids are opened only after technical shortlisting.
```

### E6. How does a department issue a corrigendum?

| Field | Value |
|---|---|
| Expected actor | department_operator |
| Detected actor | department_operator |
| Expected intent | corrigendum_portal_steps |
| Detected intent | corrigendum_portal_steps |
| Retrieved document families | procurement_manual, chips_corrigendum_manual, chips_corrigendum_manual, procurement_manual, department_tender_creation_manual, emd_online_payment_manual, emd_refund_notice, emd_refund_notice, emd_online_payment_manual, chips_corrigendum_manual, chips_corrigendum_manual |
| Source documents used | CHiPS_Corrigendum_Issuance_Manual.pdf |
| Response time | 2.077 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
The Department User opens the relevant Tender, prepares the required Corrigendum, verifies its Bid-deletion effect, and publishes it through the approval workflow.

📋 Process
1. Sign in with authorised credentials, search the Tender, select its RFQ/Tender code, and open Go to RFQ.
2. Select Header, Date, EMD/Bid Security, Tender Term, Attachment, Required Attachment, or Item Corrigendum as applicable.
3. Enter the changes, then Submit/Save and Close. For attachments, browse, DSC-sign, upload, and attach the document; for items, update and upload the prescribed BOQ.
4. Select Publish All Corrigendum/Addendum and verify the components and Bid-deletion setting. EMD/Bid Security and Item Corrigenda mandatorily delete an existing Bid.
5. Select Publish; choose the approver, enter remarks, attach a file if required, select Initiate, and confirm with the authorised DSC.
6. The approver opens Detail in the Workflow Inbox, reviews it, and approves with remarks/DSC.
7. Verify the workflow-approved and Corrigendum-published-successfully status.

📘 Source: Corrigendum Issuance Manual (CHiPS)
```

### E7. Tender ki last date extend karni hai. Kya process hai?

| Field | Value |
|---|---|
| Expected actor | department_operator |
| Detected actor | department_operator |
| Expected intent | corrigendum_portal_steps |
| Detected intent | corrigendum_portal_steps |
| Retrieved document families | bid_submission_manual, bid_submission_manual, chips_corrigendum_manual, chips_corrigendum_manual, procurement_manual, department_tender_creation_manual, emd_online_payment_manual, emd_online_payment_manual, cvc_guidance, other, chips_corrigendum_manual, chips_corrigendum_manual |
| Source documents used | CHiPS_Corrigendum_Issuance_Manual.pdf |
| Response time | 2.051 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Department User relevant Tender open karke required Corrigendum banata hai, Bid-deletion effect verify karta hai aur approval workflow se publish karta hai.

📋 Process
1. Authorised credentials se login karke Tender search karein, RFQ/Tender code select karein aur Go to RFQ kholein.
2. Required type select karein: Header, Date, EMD/Bid Security, Tender Term, Attachment, Required Attachment ya Item Corrigendum.
3. Changes fill karke Submit/Save aur Close karein. Attachment ke liye document browse, DSC-sign, upload aur Attach karein; Item ke liye prescribed BOQ update karke upload karein.
4. Publish All Corrigendum/Addendum par components aur Bid-deletion setting verify karein. EMD/Bid Security aur Item Corrigendum existing Bid ko mandatorily delete karte hain.
5. Publish karein; approver, remarks aur attachment fill karke Initiate karein aur authorised DSC select karein.
6. Approver Workflow Inbox mein Detail open karke review, remarks/DSC ke saath Approve kare.
7. Workflow approved aur Corrigendum published successfully status verify karein.

📘 Source: Corrigendum Issuance Manual (CHiPS)
```

### E8. EMD refund process department operator kaise initiate kare?

| Field | Value |
|---|---|
| Expected actor | department_operator |
| Detected actor | department_operator |
| Expected intent | emd_remittance_to_department |
| Detected intent | emd_remittance_to_department |
| Retrieved document families | emd_refund_notice, emd_refund_notice, bid_submission_manual, department_tender_creation_manual, bid_submission_manual, vendor_registration_manual, chips_auction_manual, vendor_registration_manual |
| Source documents used | Online_EMD_Refund_Notice.pdf |
| Response time | 1.614 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Unsuccessful bidder ki EMD refund process applicable Bid opening/evaluation stage ke baad department process karta hai.

📋 Process
1. Department Admin eligible unsuccessful bidder ki EMD refund/remittance initiate kare.
2. Department Approver details aur eligibility verify karke approve kare.
3. Approval ke baad e-Procurement system bank ko refund instruction bhejta hai.
4. Amount bidder ke registered bank account mein credit hota hai; Department Admin MIS/portal status mein completion verify kare. Department approval ke baad credit normally 1–2 din le sakta hai.

📘 Source: EMD Refund Guidelines (CHiPS)
```

### E9. Corrigendum upload karne ke baad bidders ko kya karna hota hai?

| Field | Value |
|---|---|
| Expected actor | vendor_bidder |
| Detected actor | vendor_bidder |
| Expected intent | bidder_corrigendum_tracking |
| Detected intent | bidder_corrigendum_tracking |
| Retrieved document families | bid_submission_manual, bid_submission_manual, chips_corrigendum_manual, chips_corrigendum_manual, vendor_registration_manual, department_tender_creation_manual, vendor_registration_manual, chips_auction_manual, bid_submission_manual, bid_submission_manual |
| Source documents used | CHiPS_Bid_Submission_Manual_English.pdf |
| Response time | 1.601 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Bidder ko relevant Tender ka Corrigendum/Addendum portal par dekhkar changed dates, conditions aur documents check karne chahiye.

📋 Process
1. Supplier login se relevant live Tender open karein.
2. Tender page par View Corrigendum/Addendum option dekhein.
3. Har amendment aur revised Bid submission date/condition padhein.
4. Portal/email alerts ke saath deadline tak Tender ko dobara check karte rahein.
5. Bid pehle submit ho chuki ho to uska status check karke revised Tender instructions ke mutabik required update ya resubmission karein.

📘 Source: Bid Submission Manual (CHiPS)
```

### E10. Department admin bid evaluation report kaise generate kare?

| Field | Value |
|---|---|
| Expected actor | department_operator |
| Detected actor | department_operator |
| Expected intent | bid_evaluation |
| Detected intent | bid_evaluation |
| Retrieved document families | chhattisgarh_store_purchase_rules, procurement_manual, procurement_manual, current_procurement_rules, current_procurement_rules, procurement_manual, procurement_manual, other, chhattisgarh_store_purchase_rules, chhattisgarh_store_purchase_rules |
| Source documents used | store purchase rule cg.pdf, publicProManual-1755343081262-715558279.pdf |
| Response time | 2.271 seconds |
| Benchmark result | Pass |
| Root cause if not Pass | — |

**Full response**

```text
💡 Answer
Bids ko published Tender criteria ke against evaluate karein: pehle eligibility, technical responsiveness, required documents aur compliance; financial bids ko Tender conditions ke mutabik evaluate karein. Sirf lowest quoted bidder automatically winner nahi hota—proposed awardee eligible, responsive aur technically acceptable bhi hona chahiye.

📋 Process
1. Bid opening record karke eligibility aur required submissions verify karein.
2. Technical specifications, Tender conditions aur compliance check karein.
3. Published criteria ke mutabik technically responsive bids identify karein.
4. Applicable case mein sirf eligible/responsive bidders ki financial bids evaluate karein.
5. Evaluated bids rank karke reasons record karein aur award se pehle competent approval lein.

📘 Source: Chhattisgarh Store Purchase Rules; Manual for Procurement of Goods 2024
```

## Notes

- The source documents listed for each question are the sources returned by the live backend with that response.
- The complete-answer capture is intentionally separate from the frozen UAT scorer so response text can be retained without truncation.

