# E-Procurement Chatbot — Tricky Question Test Report

Generated: 2026-06-19 16:04:16
LLM: gemma3-q3km:12b via Ollama (Intel Arc GPU, 100% GPU mode)

---

## Q01 — Scope & Edge Cases [PASS]

**Question:** `mera EMD wapas kab aayega?`

**Expected:** Should explain EMD refund/return process — not refuse as out-of-scope

**Verdict:** `PASS`

**Elapsed:** 100.6s | **Sources retrieved:** 5

**Source files:** mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf, publicProManual-1755343081262-715558279.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf

**Answer preview:**
> 💡 Answer The refund of your Earnest Money Deposit (EMD) is initiated by the Department Admin after approval. Once approved, the e-Procurement system instructs the bank, and the amount is credited to your account within 1–2 days. You can check the refund status on the portal.  📋 Process 1. Department Admin initiates the refund process. 2. Department Approver verifies and approves the refund. 3. The system sends instructions to the bank. 4. The amount is credited to the bidder's account. 5. Refund...

---

## Q02 — Scope & Edge Cases [PASS]

**Question:** `tender expired ho gaya, kya main abhi bhi bid kar sakta hoon?`

**Expected:** Should explain expired tender rule — may cite deadline policy

**Verdict:** `PASS`

**Elapsed:** 58.6s | **Sources retrieved:** 5

**Source files:** mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf, Store_Purhase_Rules_28.01.2021.pdf

**Answer preview:**
> 💡 Answer Agar tender ki validity period expire ho gaya hai, toh abhi bid karne ka option nahi rahega. Once the tender validity ends, it can't be revived. Tumhe fresh tenders ke liye wait karna hoga jo CHiPS portal par publish honge.  📋 Process 1.  CHIPS e-procurement portal regularly check karte raho. 2.  Fresh tenders ki notification enable karo. 3.  Eligibility criteria check karo aur bid submit karne ka time dekho.  📘 Source: mannual procurement.pdf

---

## Q03 — Scope & Edge Cases [PASS]

**Question:** `agar main do companies ka owner hoon toh kya dono se bid kar sakta hoon?`

**Expected:** Conflict-of-interest — may be out-of-scope; clean refusal expected without hallucination

**Verdict:** `PASS`

**Elapsed:** 92.1s | **Sources retrieved:** 5

**Source files:** mannual procurement.pdf, GFR2017_HINDI.pdf, publicProManual-1755343081262-715558279.pdf

**Notes:**
- NOTE: answered where refusal was expected — check if answer is factual

**Answer preview:**
> 💡 Answer Agar aap do companies ke owner hain toh aap dono se bid kar sakte hain, lekin ismein kuch conditions apply hote hain. Aapko ensure karna hoga ki har company ka registration alag-alag hai aur unke documents (PAN, DSC) bhi separate hain. Beneficial ownership guidelines ke according, aapki identity clear hona chahiye aur koi conflict of interest nahi honi chahiye.  📋 Process 1.  Dono companies ko CHIPS portal par register karwaein. 2.  Har company ke liye alag-alag login ID banwaein. 3.  B...

---

## Q04 — Personalization [PASS]

**Question:** `main suresh verma hoon, vendor registration ke liye kya karna hoga?`

**Expected:** Answer should mention 'Suresh'/'Suresh Verma' by name

**Verdict:** `PASS`

**Elapsed:** 102.4s | **Sources retrieved:** 5

**Source files:** Chatbot_Capabilities.pdf, CHiPS_Vendor_Registration_Manual_English.pdf, mannual procurement.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, FInal_GFR_upto_31_07_2024.pdf

**Answer preview:**
> 💡 Answer Suresh Verma ko vendor registration karne ke liye pehle CHiPS portal par register hona hoga. Registration process mein PAN number, CRN certificate, authorized signatory details, bank details aur contact information submit karna hoga. Suresh ko DSC (Digital Signature Certificate) bhi provide karna hoga.  📋 Process 1.  CHiPS e-procurement portal par jaaenge. 2.  "New Supplier Registration" option select karenge. 3.  Suresh Verma apna PAN number enter karega. 4.  CRN certificate ki scanned...

---

## Q05 — Personalization [PASS]

**Question:** `my company name is TechBuild Pvt Ltd, how do I get registered?`

**Expected:** Answer should mention 'TechBuild' in the response

**Verdict:** `PASS`

**Elapsed:** 138.8s | **Sources retrieved:** 5

**Source files:** CHiPS_Vendor_Registration_Manual_English.pdf, CHiPS_Bid_Submission_Manual_English.pdf, Guidelines_To_Bidders_EPS_v1.6.pdf, publicProManual-1755343081262-715558279.pdf

**Answer preview:**
> 💡 Answer TechBuild Pvt Ltd needs to register as a vendor on the Chhattisgarh e-Procurement portal. The process involves visiting the website https://eproc.cgstate.gov.in and clicking on ‘New User’ under Register. You will then need to enter your PAN card details, select “New User,” and press OK while the system setup guide downloads. After that, you can enter a preferred login code, along with other business details like authorized signatory information, contact details, bank information, CRN, a...

---

## Q06 — Typos & Broken Hindi [PASS]

**Question:** `emd chalaan kaise bhren`

**Expected:** Should understand typo 'bhren'='bharein' and explain EMD challan payment

**Verdict:** `PASS`

**Elapsed:** 101.1s | **Sources retrieved:** 5

**Source files:** Guidelines_To_Bidders_EPS_v1.6.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf, Manual_for_Procurement_of_works_2019.pdf, publicProManual-1755343081262-715558279.pdf

**Answer preview:**
> 💡 Answer EMD challan bharna ke liye, bidder ko pehle CPPP portal par register hona hoga. Phir, tender document mein specified EMD amount ka online payment karna hai. Payment options RTGS/NEFT ya e-challan ho sakte hain.  e-challan option select karne par, system ek challan generate karega jise bidder ko fill karna aur submit karna hoga.  📋 Process 1. CPPP portal par register karo. 2. Relevant tender document khojo aur open karo. 3. EMD amount calculate karo (tender document mein specified). 4. "...

---

## Q07 — Typos & Broken Hindi [PASS]

**Question:** `tendor mein paticipate kerna hai`

**Expected:** Should handle 'tendor/paticipate/kerna' typos and explain tender participation

**Verdict:** `PASS`

**Elapsed:** 19.7s | **Sources retrieved:** 0

**Answer preview:**
> Is question ka answer uplabdh documents mein nahi mila.

---

## Q08 — Multi-step / Compound [PASS]

**Question:** `vendor registration ke baad tender mein participate karne ki kya process hai? step by step batao`

**Expected:** Should cover registration completion AND tender participation steps

**Verdict:** `PASS`

**Elapsed:** 93.8s | **Sources retrieved:** 1

**Source files:** Chatbot_Capabilities.pdf

**Answer preview:**
> 💡 Answer Vendor registration ke baad tender mein participate karne ki process thodi steps mein complete hoti hai. Pehle, aapko CPPP portal par active tenders dekhne honge. Fir, jo tender relevant ho usko select karo aur "View Tender Document" option click karo. Technical bid aur Price Bid dono properly fill-up karke upload karna hai. DSC (Digital Signature Certificate) se bid submit karna mandatory hai.  📋 Process 1. **Tender Search:** CPPP portal par login karke active tenders search karo. 2. *...

---

## Q09 — Multi-step / Compound [PASS]

**Question:** `what are the documents needed for EMD and also for vendor registration?`

**Expected:** Should list documents for BOTH EMD and vendor registration

**Verdict:** `PASS`

**Elapsed:** 130.2s | **Sources retrieved:** 5

**Source files:** 160616_AMC_AC short tender.pdf, publicProManual-1755343081262-715558279.pdf, Guidelines_To_Bidders_EPS_v1.6.pdf

**Answer preview:**
> 💡 Answer For the EMD, the required documents include a copy of the EMD instrument (as per the tender conditions), along with copies of PAN card, VAT, Service Tax, and Firm's Registration. Additionally, copies of Balance sheets and Profit & Loss Account related to annual turnover are needed. For vendor registration, Ramesh needs to provide his PAN details and CRN certificate if he falls under Vendor Class A–D. He also needs to create a Preferred Login code and fill in all business coordinates.  📋...

---

## Q10 — Trick / Out-of-scope [FAIL]

**Question:** `CG e-procurement portal ka helpline number kya hai?`

**Expected:** Should refuse — contact info likely absent in docs. Must NOT hallucinate a number

**Verdict:** `FAIL`

**Elapsed:** 80.1s | **Sources retrieved:** 7

**Source files:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Vendor_Registration_Manual_English.pdf, AuctionManual_FA.pdf, CHiPS_Bid_Submission_Manual_English.pdf, Guidelines_To_Bidders_EPS_v1.6.pdf

**Notes:**
- FAIL: hallucinated phone number(s): ['1800 419 9140']

**Answer preview:**
> 💡 Answer CG e-procurement portal ka helpline number 1800 419 9140 hai. Isko subah ke 9 baje se raat ke 11 baje tak call kar sakte ho (IST time mein). Email helpdesk.eproc@cgswan.gov.in par bhi contact kar sakte ho.  📋 Process No process is required, it's just a helpline number and email address.  📘 Source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf

---

## Q11 — Trick / Out-of-scope [PASS]

**Question:** `tell me about GST rules for government tenders`

**Expected:** Out-of-scope (tax law). Clean refusal — must not invent GST percentages

**Verdict:** `PASS`

**Elapsed:** 97.2s | **Sources retrieved:** 5

**Source files:** mannual procurement.pdf, publicProManual-1755343081262-715558279.pdf

**Notes:**
- NOTE: answered where refusal was expected — check if answer is factual

**Answer preview:**
> 💡 Answer GST compliance is mandatory for bidders participating in Chhattisgarh Infotech Promotion Society (CHIPS) tenders. Bidders must be registered under GST and furnish their GSTIN number and registration certificate. The bid and contract must explicitly show the GST tax rates and amount separately from the price, adhering to the GST Act. If a bidder claims exemption due to turnover below the threshold, they need a valid certificate from a Chartered Accountant (CA) or Cost Accountant.  📋 Proc...

---

## Q12 — Trick / Out-of-scope [PASS]

**Question:** `who made this chatbot?`

**Expected:** Meta-question about origin. Should answer from Chatbot_Capabilities or give honest answer

**Verdict:** `PASS`

**Elapsed:** 80.1s | **Sources retrieved:** 1

**Source files:** Chatbot_Capabilities.pdf

**Answer preview:**
> 💡 Answer This AI assistant was created for the Chhattisgarh Infotech Promotion Society (CHIPS) e-Procurement Portal.  📋 Process There is no process to determine who specifically developed this chatbot; it's a CHiPS resource.  📘 Source: Chatbot_Capabilities.pdf

---

## Q13 — Comparison / Analytical [PASS]

**Question:** `offline tender aur online tender mein kya difference hai?`

**Expected:** Should compare offline vs online tender using docs

**Verdict:** `PASS`

**Elapsed:** 75.2s | **Sources retrieved:** 5

**Source files:** publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf

**Answer preview:**
> 💡 Answer Offline tender mein bids physical format mein submit kiye jaate hain, yaani paper ke zariye. Ismein bid documents ko sealed envelope mein dal kar designated place par submit karna hota hai. Online tender mein, sab kuch e-Procurement portal ke zariye hota hai – bids digitally submit hoti hain aur process completely online hoti hai.  📋 Process 1. **Offline Tender:** Bidder ko tender document purchase karna hoga, phir technical bid aur price bid separate sealed envelopes mein dal kar deadl...

---

## Q14 — Comparison / Analytical [PASS]

**Question:** `kaunsa payment method sabse fast hai EMD ke liye?`

**Expected:** Should list EMD payment methods from docs; may decline to single-pick fastest

**Verdict:** `PASS`

**Elapsed:** 64.3s | **Sources retrieved:** 5

**Source files:** EMD_CHALLAN_PAYMENT_V1.0.pdf, publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf

**Answer preview:**
> 💡 Answer Online payment through Payment gateways available on GeM hai sabse fast option EMD ke liye. Unsuccessful bidders ka EMD auction generate hone ke baad 2 din mein auto-refund ho jaata hai GeM ke zariye hi.  📋 Process 1. FA-BB ko GeM par available payment gateway se EMD pay karna chahiye. 2. Auction complete hone ke baad, successful bidder ka EMD account mein transfer ho jayega. 3. Unsuccessful bidders ka EMD 2 din mein auto-refund ho jaayega.  📘 Source: publicProManual-1755343081262-71555...

---

## Summary

| ID | Category | Question | Verdict | Time |
|---|---|---|---|---|
| Q01 | Scope & Edge Cases | mera EMD wapas kab aayega? | `PASS` | 101s |
| Q02 | Scope & Edge Cases | tender expired ho gaya, kya main abhi bhi bid ka... | `PASS` | 59s |
| Q03 | Scope & Edge Cases | agar main do companies ka owner hoon toh kya don... | `PASS` | 92s |
| Q04 | Personalization | main suresh verma hoon, vendor registration ke l... | `PASS` | 102s |
| Q05 | Personalization | my company name is TechBuild Pvt Ltd, how do I g... | `PASS` | 139s |
| Q06 | Typos & Broken Hindi | emd chalaan kaise bhren | `PASS` | 101s |
| Q07 | Typos & Broken Hindi | tendor mein paticipate kerna hai | `PASS` | 20s |
| Q08 | Multi-step / Compound | vendor registration ke baad tender mein particip... | `PASS` | 94s |
| Q09 | Multi-step / Compound | what are the documents needed for EMD and also f... | `PASS` | 130s |
| Q10 | Trick / Out-of-scope | CG e-procurement portal ka helpline number kya h... | `FAIL` | 80s |
| Q11 | Trick / Out-of-scope | tell me about GST rules for government tenders | `PASS` | 97s |
| Q12 | Trick / Out-of-scope | who made this chatbot? | `PASS` | 80s |
| Q13 | Comparison / Analytical | offline tender aur online tender mein kya differ... | `PASS` | 75s |
| Q14 | Comparison / Analytical | kaunsa payment method sabse fast hai EMD ke liye... | `PASS` | 64s |

**Results: 13 PASS / 0 PARTIAL / 1 FAIL / 0 ERROR out of 14**

**Pass rate (strict): 13/14 (92%)**