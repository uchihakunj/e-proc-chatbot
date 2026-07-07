# CHiPS e-Procurement Chatbot — 100-Question Q&A Report (with full responses)

**Date:** 2026-07-01  
**Endpoint:** `POST /api/stream` (BGE-M3 retrieval + bge-reranker + Ollama `gemma3:4b`)  
**Knowledge base:** Qdrant `db3`, 3,503 chunks  
**Dataset:** 100 questions — 50 Vendor + 50 Government Officer × English / Hindi / Hinglish  
**Harness:** `05_webui/run_qa_eval_100.py`  |  **Raw data:** `05_webui/qa_eval_100_results.json`  
**Responses shown are the server-sanitised `done.answer`** (ungrounded rule numbers stripped — same text the browser shows).

> This run was taken **after** the fixes in §8 of `QA_Eval_100Q_Report.md`: the vendor-registration
> wizard no longer intercepts documentation questions (Q1 now answers), the DSC/`open tender` intent
> mis-routes are corrected, and the server now emits the sanitised answer to all consumers.

---

## 1. The four metrics

| Metric | Result |
|---|---|
| **Intent Recognition** | **97/100 = 97%** correct topic-routing |
| **Entity Extraction (answer-side)** | **10/100** answers cite a `Rule N`; **0** ungrounded rule-number(s) auto-stripped across **0** answer(s) before display |
| **Response Time** | avg **37.2s**, median **37.8s**, range 2–59s (live-gen avg 39.0s) |
| **Fallback Rate** | **0/100** — 95 ANSWERED, 5 cache, 0 clarify, 0 refused, 0 error |

### Rule-number sanitization (option 1, now server-authoritative)

No ungrounded rule numbers were stripped in this run — every cited number was present in the retrieved context.

**Caveat (unchanged):** the validator only removes numbers *absent* from the context. Numbers that *are* in the retrieved chunks but attached to the wrong concept (e.g. citing a GeM rule number for a Limited-Tender question) are considered grounded and kept — that is a semantic mis-application the citation check cannot catch, and hard-coding "correct" numbers is unsafe because this KB blends multiple manuals whose numbering can differ from vanilla GFR-2017.

---

## 2. Full questions & responses (all 100)

## — Vendor · English —

### Q1. How do I register as a vendor on the Chhattisgarh eProcurement portal?

- **Role/Lang:** Vendor · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 46.68s  |  **Sources:** 3  
- **Cited:** CHiPS_Vendor_Registration_Manual_English.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, Guidelines_To_Bidders_EPS_v1.6.pdf  

> **Response:**
> 💡 Answer
> To register as a vendor on the Chhattisgarh e-Procurement portal, you must follow these steps as outlined in the Vendor Registration Manual (CHiPS):
>
> 1. Visit the website https://eproc.cgstate.gov.in and click on ‘New User’ under Register.
> 2. Enter your PAN card details accurately. This is essential for registration.
> 3. Select “New User” and “Enter” to continue, acknowledging any system setup guide download prompts.
> 4. Enter a Preferred Login Code to check availability – this confirms that the vendor slot is open.
> 5. Fill in all required details, including Authorized Signatory, Contact Information, Bank Details, CRN (Central Registry Number), and Vendor Business & Partner information.
> 6. Complete the validation process by pressing “Save & Next” to proceed with registration.
>
> 📋 Process
> 1. Navigate to https://eproc.cgstate.gov.in.
> 2. Click on ‘New User’ under the ‘Register’ section.
> 3. Input your PAN card details.
> 4. Select "New User" and click “Enter”.
> 5. Enter a Preferred Login Code.
> 6. Complete all required fields in the registration form.
> 7. Press “Save & Next” to validate your information.
>
> 📘 Source: Vendor Registration Manual (CHiPS)

### Q2. What are the system requirements for using the portal?

- **Role/Lang:** Vendor · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 38.5s  |  **Sources:** 3  
- **Cited:** Guidelines_To_Bidders_EPS_v1.6.pdf, publicProManual-1755343081262-715558279.pdf, AuctionManual_FA.pdf  

> **Response:**
> 💡 Answer
> To operate on the e-Procurement portal, your computer system requires Java version 8.77, and one of the following browsers: Internet Explorer 9 or 11, Mozilla Firefox, or Google Chrome with the IE Tab V2 (Enhanced IE Tab) extension. Internet connectivity should be at least 1 MBPS. The auto setup utility is available on the e-Procurement portal home page to automatically configure your client system – link: https://eproc.cgstate.gov.in --> Auto Setup.
>
> 📋 Process
> 1. Install Java version 8.77 on your computer.
> 2. Download and install one of the supported browsers (Internet Explorer, Firefox, or Chrome with IE Tab).
> 3. Obtain and install the IE Tab V2 extension for Google Chrome if using that browser.
> 4. Access the e-Procurement portal home page: https://eproc.cgstate.gov.in.
> 5. Utilize the auto setup utility to configure your client system.
>
> 📘 Source: Guidelines_To_Bidders_EPS_v1.6.pdf

### Q3. How can I reset my password if I forget it?

- **Role/Lang:** Vendor · English  
- **Intent:** `PORTAL_USAGE` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 37.4s  |  **Sources:** 4  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Bid_Submission_Manual_English.pdf, AuctionManual_FA.pdf, CHiPS_Vendor_Registration_Manual_English.pdf  

> **Response:**
> 💡 Answer
> If you have forgotten your password, you can use the “FORGOT PASSWORD?” option available on the homepage to generate a new temporary password. The new password will be generated and emailed to your registered email address. You will then need to log in with this temporary password, which you should change immediately upon logging in.
>
> 📋 Process
> 1. Navigate to the CPPP Portal homepage.
> 2. Click on the “FORGOT PASSWORD?” option.
> 3. Enter your User ID and registered Email address or Mobile or PAN.
> 4. Complete the Captcha verification.
> 5. Validate using DSC or OTP.
> 6. A new password will be created and sent to your registered email address.
>
> 📘 Source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Bid_Submission_Manual_English.pdf

### Q4. What is the EMD rate and how is it calculated?

- **Role/Lang:** Vendor · English  
- **Intent:** `EMD_GENERAL` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 50.7s  |  **Sources:** 4  
- **Cited:** publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf, Guidelines_To_Bidders_EPS_v1.6.pdf  

> **Response:**
> 💡 Answer
> **1. What is the EMD rate**
> The Bid Security (also known as Earnest Money Deposit or EMD) should ordinarily be between two (2) to five (5) per cent of the estimated value of the goods to be procured.
>
> **2. how is the EMD rate calculated**
> The amount of bid security should ordinarily range between two (2) to five (5) per cent of the estimated value of the goods to be procured. The exact bid security amount should be indicated in the tender document.

### Q5. Who is exempt from paying the EMD amount?

- **Role/Lang:** Vendor · English  
- **Intent:** `EMD_GENERAL` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 34.19s  |  **Sources:** 4  
- **Cited:** publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf, Chatbot_Capabilities.pdf, mannual procurement.pdf  

> **Response:**
> 💡 Answer
> Certain categories of bidders are exempt from paying the Earnest Money Deposit (EMD), as specified in DPIIT guidelines. These include Micro and Small Enterprises (MSEs) and other entities falling under specific exemptions notified by the Department of Expenditure. Specifically, these exemptions apply when the bidder is registered with relevant authorities and provides a certified copy of its valid registration details.
>
> 📋 Process
> 1. Check if your enterprise qualifies for EMD exemption based on DPIIT guidelines and notifications from the Department of Expenditure.
> 2. If eligible, prepare and submit a certified copy of your valid registration details to the Tender Owner (Department Admin).
> 3. Verify that the exemption is correctly applied by the Tender Owner.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf

### Q6. What forms of EMD are accepted by the portal?

- **Role/Lang:** Vendor · English  
- **Intent:** `EMD_GENERAL` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 34.48s  |  **Sources:** 3  
- **Cited:** Guidelines_To_Bidders_EPS_v1.6.pdf, Manual_for_Procurement_of_works_2019.pdf, publicProManual-1755343081262-715558279.pdf  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> The CHiPS portal accepts Earnest Money Deposit (EMD) through several methods. Bidders can submit EMD as a physically sealed envelope, or they can pay online via payment gateways like Internet banking, Debit Card, Credit Card, NEFT, RTGS, eChallan, or wallet – subject to tender terms and conditions. Additionally, the portal accepts scanned copies of the EMD instrument or online payment receipts along with relevant reference details.
>
> 📋 Process
> 1. Bidders can submit EMD physically in a sealed envelope.
> 2. Alternatively, they can make an online payment through approved gateways.
> 3. Upon online payment, bidders must upload a scanned copy of the payment receipt/instrument and provide relevant reference details to the portal.
>
> 📘 Source: Guidelines_To_Bidders_EPS_v1.6.pdf

### Q7. How long is the EMD validity period after submission?

- **Role/Lang:** Vendor · English  
- **Intent:** `EMD_GENERAL` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 33.8s  |  **Sources:** 3  
- **Cited:** EMD_CHALLAN_PAYMENT_V1.0.pdf, Manual_for_Procurement_of_works_2019.pdf, publicProManual-1755343081262-715558279.pdf  
- **Answer entities:** Thresholds: 45 days  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> The Bid Security (also known as EMD) remains valid for a period of 45 days beyond the final bid validity period.
>
> 📋 Process
> 1. The Bid Security is normally valid for 45 days beyond the final bid validity period.
> 2. In certain cases, Procuring Entities may consider asking Bidders to submit a Bid securing declaration (BSD) instead of the Bid Security.
>
> 📘 Source: [Source 1: EMD_CHALLAN_PAYMENT_V1.0.pdf], [Source 2: Manual_for_Procurement_of_works_2019.pdf], [Source 3: publicProManual-1755343081262-715558279.pdf]

### Q8. How do I get my EMD refund after a tender is awarded?

- **Role/Lang:** Vendor · English  
- **Intent:** `EMD_REFUND` (conf 0.8) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 31.53s  |  **Sources:** 4  
- **Cited:** mannual procurement.pdf, Guidelines_To_Bidders_EPS_v1.6.pdf, publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf  
- **Answer entities:** Thresholds: 2 days  

> **Response:**
> 💡 Answer
> After a tender is awarded, unsuccessful bidders will receive their Earnest Money Deposit (EMD) refund through an e-payment system. The process involves the Department Admin initiating the refund after approval, with the e-Procurement system instructing the bank to credit the amount within 1–2 days. Bidders must have provided correct account details during registration for this purpose.
>
> 📋 Process
> 1. Department Admin initiates the EMD refund.
> 2. The e-Procurement system instructs the bank for payment.
> 3. The amount is credited to the bidder’s account within 1–2 days.
>
> 📘 Source: mannual procurement.pdf

### Q9. Can I submit multiple bids for the same tender?

- **Role/Lang:** Vendor · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 41.28s  |  **Sources:** 3  
- **Cited:** mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf, publicProManual-1755343081262-715558279.pdf  

> **Response:**
> 💡 Answer
> Multiple bid submissions are permitted for the same tender, subject to certain conditions outlined within the procurement manual. Specifically, when multiple bids are received, the Tender Committee (TC) will assess the level of competition based on factors like value, specifications, and the tendering system used. A sufficient number of independent bids is desirable – less than three without suspicion of a cartel may indicate a lack of competition. However, even with only one bid submitted, it can be considered valid if the advertisement was satisfactory, qualification criteria weren’t overly restrictive, and prices are reasonable.
>
> 📋 Process
> 1. Assess the Number of Bids: The Tender Committee (TC) evaluates the number of bids received to determine the level of competition.
> 2. Evaluate Qualification Criteria: Ensure that the bid meets all specified eligibility requirements.
> 3. Analyze Price Reasonableness: Verify that the quoted prices are reasonable considering market conditions and specifications.
> 4. Document TC Assessment: The TC must record its assessment regarding competition in the tender report.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf

### Q10. What is a Digital Signature Certificate (DSC)?

- **Role/Lang:** Vendor · English  
- **Intent:** `DSC` (conf 1.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 39.94s  |  **Sources:** 4  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Bid_Submission_Manual_English.pdf, CHiPS_Vendor_Registration_Manual_English.pdf, mannual procurement.pdf  

> **Response:**
> 💡 Answer
> A Digital Signature Certificate (DSC) is a Class II or Class III certificate used for e-commerce transactions on the CG e-Procurement portal. It’s required to log into the secured site and participate in the tendering process. Vendors need to procure these certificates from authorized Certifying Authorities (CAs).
>
> 📋 Process
> 1. Vendors must obtain a DSC, which is Class II or Class III – Signing & Encryption.
> 2. DSCs can be obtained from authorized CAs like e-Mudhra, GNFC, IDRBT, MTNLTrustline, NIC, or Safescrypt.
> 3. Foreign vendors need to download the Registration/Application form from a licensed CA approved by CCA (https://cca.gov.in).
> 4. They must fill out the application form with required documents and submit them to the Indian Embassy for certification.
> 5. The CA will provide the Swift code for online fund transfer.
>
> 📘 Source: CHiPS_Bid_Submission_Manual_English.pdf

### Q11. How do I map my renewed DSC to my account?

- **Role/Lang:** Vendor · English  
- **Intent:** `DSC` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 40.08s  |  **Sources:** 4  
- **Cited:** CHiPS_Vendor_Registration_Manual_English.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Bid_Submission_Manual_English.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf  

> **Response:**
> 💡 Answer
> To map your renewed Digital Signature Certificate (DSC) to your account on the CHiPS portal, follow these steps:
>
> 1. Log in to the CPPP Portal with your existing vendor credentials.
> 2. Navigate to the "Vendor Profile" or “My Account” section of the portal.
> 3. Locate the option labeled "Register DSC" (or similar wording – refer to FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf for details on the exact location).
> 4. Follow the prompts to upload the renewed DSC file and complete the mapping process. The system will verify the certificate’s validity as per the information provided in Source 1 and Source 6.
>
> 📋 Process
> 1. Log into the CPPP Portal.
> 2. Go to "Vendor Profile" or “My Account”.
> 3. Click on “Register DSC”.
> 4. Upload the renewed DSC file.
> 5. Verify certificate details.
>
> 📘 Source: CHiPS_Vendor_Registration_Manual_English.pdf

### Q12. Can I use the same DSC for two different login IDs?

- **Role/Lang:** Vendor · English  
- **Intent:** `DSC` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 32.62s  |  **Sources:** 4  
- **Cited:** CHiPS_Bid_Submission_Manual_English.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Vendor_Registration_Manual_English.pdf, Preferred_System_Configuration_V_2.pdf  

> **Response:**
> 💡 Answer
> No, the same Digital Signature Certificate (DSC) cannot be used to enroll more than one login ID in the e-Procurement portal. This restriction is implemented for security reasons to prevent unauthorized access and maintain data integrity.
>
> 📋 Process
> 1. You must procure a separate DSC for each login ID you intend to use on the e-Procurement portal.
> 2. Ensure that the DSC is valid and meets the specified requirements (Class II or Class III - Signing & Encryption).
>
> 📘 Source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf

### Q13. What should I do if my DSC token gets blocked?

- **Role/Lang:** Vendor · English  
- **Intent:** `DSC` (conf 1.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 40.25s  |  **Sources:** 4  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Bid_Submission_Manual_English.pdf, CHiPS_Vendor_Registration_Manual_English.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf  

> **Response:**
> 💡 Answer
> If your Digital Signature Certificate (DSC) token gets blocked, you need to contact the DSC service provider immediately. The block occurs when an incorrect token password is supplied or if more than the allowed number of attempts are made to access it. The vendor needs to reach out to the specific DSC Certifying Authority you used to unlock the token.
>
> 📋 Process
> 1. Contact the DSC Service Provider: Immediately contact the issuing Certificate Authority (CA) – e-Mudhra, GNFC, IDRBT, MTNLTrustline, NIC, or Safescrypt – that issued your DSC. You can find their website addresses in Source 3.
> 2. Provide Details: Be prepared to provide details such as your DSC serial number and any relevant transaction information.
> 3. Follow Instructions: The CA will guide you through the process of unlocking your DSC, which typically involves resetting the password or obtaining a new token.
>
> 📘 Source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf

### Q14. What are the contact details of the portal helpdesk?

- **Role/Lang:** Vendor · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 34.15s  |  **Sources:** 4  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Vendor_Registration_Manual_English.pdf, AuctionManual_FA.pdf, Manual_Offline_Tenders_v.1.0.pdf  

> **Response:**
> 💡 Answer
> The CHiPS Helpdesk team can be contacted via email at helpdesk.eproc@cgswan.gov.in or by calling their toll-free helpline at 1800 419 9140 (IST, 9:00 AM to 11:00 PM).
>
> 📋 Process
> There is no process described in the provided documents for contacting the helpdesk; it simply lists the contact details.
>
> 📘 Source: FAQ of Chhattisgarh Infotech Promotion Society(CHiPS).pdf

### Q15. How do I upload techno-commercial attachments during bidding?

- **Role/Lang:** Vendor · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 39.52s  |  **Sources:** 4  
- **Cited:** publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf, Manual_Offline_Tenders_v.1.0.pdf  

> **Response:**
> 💡 Answer
> To upload techno-commercial attachments during bidding, bidders must first submit their bids through the e-Procurement portal. Specifically, they need to upload scanned copies of all required documents in cover-I, as outlined in the NIT (Tender Notice). This includes eligibility documents, technical quality assessments, performance aspects, commercial terms and conditions, and relevant financial details – excluding the price itself. The system then generates techno-commercial and price comparative statements when submitted in Excel format.
>
> 📋 Process
> 1. Log into the e-Procurement portal.
> 2. Navigate to the cover-I section of the bid submission.
> 3. Upload scanned copies of all required documents as specified in the NIT.
> 4. Ensure the documents are submitted in a compatible format (e.g., Excel) for system comparison.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf

### Q16. Can a foreign vendor register on this portal?

- **Role/Lang:** Vendor · English  
- **Intent:** `VENDOR_REGISTRATION` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 35.01s  |  **Sources:** 3  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf  

> **Response:**
> 💡 Answer
> Yes, a foreign vendor can register on this portal, but prior registration is required. Please refer to the Vendor Registration manuals (available in both Hindi and English) under the “Manuals” section of the Homepage. Specifically, if your Digital Signature Certificate (DSC) is issued by a Foreign Service provider, it may not be compatible with the portal; you will need an Indian CA-issued DSC.
>
> 📋 Process
> 1. Purchase a Digital Signature Certificate (DSC) from an authorized Indian DSC provider (CA).
> 2. If using a foreign service provider for DSC, ensure document authentication by the Indian Embassy in your country before obtaining the certificate.
> 3. Complete vendor registration on the portal following instructions provided within the tender document.
>
> 📘 Source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf

### Q17. What should I do if I get an 'Application Blocked by Security Setting' Java error?

- **Role/Lang:** Vendor · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 30.28s  |  **Sources:** 6  
- **Cited:** CHiPS_Bid_Submission_Manual_English.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, Preferred_System_Configuration_V_2.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf, EDGE_Browser_Setup_V1.0.pdf  

> **Response:**
> 💡

### Q18. How can I check the status of my online EMD payment?

- **Role/Lang:** Vendor · English  
- **Intent:** `EMD_PAYMENT` (conf 0.8) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 42.38s  |  **Sources:** 3  
- **Cited:** Guidelines_To_Bidders_EPS_v1.6.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf, publicProManual-1755343081262-715558279.pdf  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> Bidders who have paid their Earnest Money Deposit (EMD) online through modes like Internet banking can track its status via the e-Procurement portal. Specifically, you will need to access the portal and locate the tender details for which the EMD was submitted. The system should provide an update on the refund process, including confirmation that it has been received and is being evaluated by the department authority as per the guidelines.
>
> 📋 Process
> 1. Log in to the CPPP Portal using your DSC.
> 2. Navigate to the tender details for which you paid the EMD online.
> 3. Locate the section pertaining to payment status or refund tracking (refer to Guidelines_To_Bidders_EPS_v1.6.pdf for specific instructions).
> 4. The system should display the current status of your EMD refund request, including any relevant transaction details.
>
> 📘 Source: Guidelines_To_Bidders_EPS_v1.6.pdf

### Q19. What happens if I withdraw my bid after the submission deadline?

- **Role/Lang:** Vendor · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 38.42s  |  **Sources:** 4  
- **Cited:** CHiPS_Bid_Submission_Manual_English.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf, publicProManual-1755343081262-715558279.pdf  

> **Response:**
> 💡 Answer
> If a bidder withdraws their bid after the submission deadline, the bid security (EMD) will be forfeited. This is outlined in several sections of the documents, including Manual for Procurement of Works 2019 and the general principles regarding Bid Security outlined across multiple sources. The system administrator may extend the bid submission date by 24/48/72 hours due to unforeseen events, but this does not override the forfeiture of the EMD upon withdrawal after the deadline.
>
> 📋 Process
> 1. Bidder withdraws their bid after the specified deadline.
> 2. The System Administrator initiates the process of forfeiting the Bid Security (EMD).
> 3. The forfeited amount is handled according to the EMD Challan Payment Guide (CHiPS).
>
> 📘 Source: Manual for Procurement of Works 2019, CHiPS_Bid_Submission_Manual_English.pdf

### Q20. Can I edit my company profile details after registration?

- **Role/Lang:** Vendor · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 34.8s  |  **Sources:** 4  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, publicProManual-1755343081262-715558279.pdf, CHiPS_Vendor_Registration_Manual_English.pdf, mannual procurement.pdf  

> **Response:**
> 💡 Answer
> Yes, it is possible to edit your profile details within the vendor login through the Chhattisgarh Infotech Promotion Society (CHIPS) e-Procurement portal. The manual outlines a step-by-step process for new supplier registration, including entering PAN card details and other relevant information.
>
> 📋 Process
> 1. Visit the e-Procurement portal at https://eproc.cgstate.gov.in and click on ‘New User’ under Register.
> 2. Enter your PAN card details accurately.
> 3. Fill in all required details, including Preferred Login Code, Authorized Signatory, Contact information, Bank Details, CRN, Vendor business & Partner information.
> 4. Validate the entered information by pressing “Save &Next”.
>
> 📘 Source: CHiPS_Vendor_Registration_Manual_English.pdf

## — Vendor · Hindi —

### Q21. छत्तीसगढ़ ई-प्रोक्योरमेंट पोर्टल पर नया वेंडर रजिस्ट्रेशन कैसे करें?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 46.08s  |  **Sources:** 4  
- **Cited:** Guidelines_To_Bidders_EPS_v1.6.pdf, AuctionManual_FA.pdf, CHiPS_Vendor_Registration_Manual_English.pdf, Manual_Offline_Tenders_v.1.0.pdf  

> **Response:**
> 💡 उत्तर
> छत्तीसगढ़ ई-प्रोक्योरमेंट पोर्टल पर नया वेंडर रजिस्ट्रेशन निम्नलिखित चरणों में किया जा सकता है:
>
> 1. पोर्टल पर जाएँ: https://eproc.cgstate.gov.in और ‘New User’ के अंतर्गत ‘Register’ पर क्लिक करें।
> 2. उपयोगकर्ता आईडी और पासवर्ड चुनें।
> 3. डिजिटल हस्ताक्षर प्रमाणपत्र (DSC) अपलोड करें।
> 4. क्षेत्रीय और भाषा प्रारूप सेटिंग्स को समायोजित करें:
>  * कंट्रोल पैनल पर जाएँ।
>  * ‘Region and Language Options’ आइकन पर क्लिक करें।
>  * अंग्रेजी (United States) का चयन करें।
>  * ‘OK’ पर क्लिक करें।
> 5. आवश्यक जानकारी भरें और फॉर्म सबमिट करें।
>
> 📋 प्रक्रिया
> 1. पोर्टल पर जाएँ: https://eproc.cgstate.gov.in और ‘New User’ के अंतर्गत ‘Register’ पर क्लिक करें।
> 2. उपयोगकर्ता आईडी और पासवर्ड चुनें।
> 3. डिजिटल हस्ताक्षर प्रमाणपत्र (DSC) अपलोड करें।
> 4. क्षेत्रीय और भाषा प्रारूप सेटिंग्स को समायोजित करें:
>  * कंट्रोल पैनल पर जाएँ।
>  * ‘Region and Language Options’ आइकन पर क्लिक करें।
>  * अंग्रेजी (United States) का चयन करें।
>  * ‘OK’ पर क्लिक करें।
> 5. आवश्यक जानकारी भरें और फॉर्म सबमिट करें।
>
> 📘 स्रोत: CHiPS_Vendor_Registration_Manual_English.pdf

### Q22. पोर्टल का उपयोग करने के लिए कंप्यूटर की क्या आवश्यकताएं हैं?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 37.45s  |  **Sources:** 3  
- **Cited:** Guidelines_To_Bidders_EPS_v1.6.pdf, GFR2017_HINDI.pdf, it_act_2000_updated hindi.pdf  

> **Response:**
> 💡 उत्तर
> पोर्टल का उपयोग करने के लिए कंप्यूटर सिस्टम/डेस्कटॉप/लैपटॉप की निम्नलिखित आवश्यकताएं हैं: Java ver.8.77, Internet explorer 9 / 11, नवीनतम Mozilla Firefox, Google Chrome के साथ IE Tab V2 (Enhanced IE Tab)। इसके अतिरिक्त, इंटरनेट कनेक्टिविटी न्यूनतम एक MBPS होनी चाहिए। उपयोगकर्ता को ऑटो कॉन्फ़िगर करने के लिए eProcurement पोर्टल होम पेज पर एक ऑटो सेटअप यूटिलिटी उपलब्ध है, जिसका लिंक https://eproc.cgstate.gov.in --> Auto Setup है।
>
> 📋 प्रक्रिया
> 1. eProcurement पोर्टल होम पेज पर "Auto Setup" लिंक पर क्लिक करें।
> 2. ऑटो सेटअप यूटिलिटी डाउनलोड और इंस्टॉल करें।
> 3. इंटरनेट कनेक्टिविटी की जाँच करें और सुनिश्चित करें कि यह न्यूनतम 1 MBPS है।
>
> 📘 स्रोत: Guidelines_To_Bidders_EPS_v1.6.pdf

### Q23. अगर मैं अपना पासवर्ड भूल जाऊं तो नया पासवर्ड कैसे बनाऊं?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `PORTAL_USAGE` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 37.31s  |  **Sources:** 5  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, AuctionManual_FA.pdf, CHiPS_Bid_Submission_Manual_English.pdf, Vigilance Manual 2021 (Hindi).pdf, Corrigendum_Instructions_to_department_users_and_bidders.pdf  

> **Response:**
> 💡 उत्तर
> यदि आप अपना पासवर्ड भूल जाते हैं तो नया पासवर्ड उत्पन्न करने के लिए “FORGOT PASSWORD?” विकल्प का उपयोग करें जो होमपेज पर उपलब्ध है। नए पासवर्ड को उत्पन्न किया जाएगा और विक्रेता के पंजीकृत ईमेल पते पर ईमेल द्वारा भेजा जाएगा। फिर वह अस्थायी पासवर्ड के साथ लॉग इन कर सकता है जिसे लॉग इन करते समय बदलने की आवश्यकता होगी।
>
> 📋 प्रक्रिया
> 1. होमपेज पर “FORGOT PASSWORD?” विकल्प ढूंढें।
> 2. सिस्टम द्वारा जेनरेट किए गए नए टेम्पोररी पासवर्ड को प्राप्त करें और अपने पंजीकृत ईमेल पते पर प्राप्त करें।
> 3. टेम्पोररी पासवर्ड का उपयोग करके लॉग इन करें।
> 4. लॉग इन करते समय, अपना पासवर्ड बदलें।
>
> 📘 स्रोत: FAQ of Chhattisgarh Infotech Promotion Society(CHiPS)

### Q24. ईएमडी (EMD) की दर कितनी होती है और इसकी गणना कैसे की जाती है?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `EMD_GENERAL` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 46.13s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf, Guidelines_To_Bidders_EPS_v1.6.pdf  
- **Answer entities:** Thresholds: 5%  

> **Response:**
> 💡 उत्तर
> ईएमडी (EMD) की दर आम तौर पर बोली के अनुमानित मूल्य का 5% होती है, लेकिन यह निविदा दस्तावेज़ में स्पष्ट रूप से दर्शाया जाता है। यह दर अधिकतम 500,000 रुपये तक सीमित हो सकती है।
>
> 📋 प्रक्रिया
> 1. निविदा दस्तावेज़ में उल्लिखित अनुमानित मूल्य की गणना करें।
> 2. अनुमानित मूल्य को 5% से गुणा करें।
> 3. यदि परिणाम 500,000 रुपये से अधिक है, तो अधिकतम 500,000 रुपये तक की दर का उपयोग करें।
> 4. ईएमडी की गणना के लिए निविदा दस्तावेज़ में दिए गए सूत्र का पालन करें।
>
> नियम/प्रावधान:
> publicProManual-1755343081262-715558279.pdf के अनुसार, "The amount of bid security should ordinarily be 5% (five per cent) of the assessed or reserved price of the goods." (ईएमडी की राशि आम तौर पर मूल्यांकन या आरक्षित मूल्य का 5% होनी चाहिए।)
>
> व्याख्या
> ईएमडी एक सुरक्षा जमा है जो यह सुनिश्चित करता है कि बोलीदाता निविदा में गंभीर इरादा रखते हैं। यदि कोई बोलीदाता सफल होता है, तो ईएमडी को आमतौर पर अनुबंध मूल्य में समायोजित किया जाता है। यदि कोई बोलीदाता असफल होता है, तो ईएमडी वापस कर दी जाती है।
>
> 📘 स्रोत: publicProManual-1755343081262-715558279.pdf

### Q25. ईएमडी (EMD) भुगतान से किन कंपनियों को छूट प्राप्त है?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `EMD_GENERAL` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 37.06s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf  

> **Response:**
> 💡 उत्तर
> निम्नलिखित कंपनियों को ईएमडी (EMD) भुगतान से छूट प्राप्त है:
> * DPIIT द्वारा अधिसूचित छोटे और मध्यम उद्यमों (MSMEs)।
> * अन्य विशिष्ट श्रेणियां जो DPIIT द्वारा निर्धारित की गई हैं, जैसा कि सार्वजनिक प्रोManual-1755343081262-715558279.pdf में पैरा 1.11.2-4-a में उल्लिखित है।
>
> 📋 प्रक्रिया
> 1. Bid Submission Manual (CHiPS) के अनुसार, यदि आप MSME हैं, तो आपको EMD जमा करने की आवश्यकता नहीं है।
> 2. अन्य छूटों के लिए, DPIIT द्वारा निर्धारित मानदंडों को पूरा करें और संबंधित दस्तावेज़ उपलब्ध कराएं।
>
> 📘 स्रोत: publicProManual-1755343081262-715558279.pdf

### Q26. पोर्टल पर ईएमडी के लिए कौन-कौन से भुगतान रूप स्वीकार किए जाते हैं?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 35.53s  |  **Sources:** 3  
- **Cited:** EMD_CHALLAN_PAYMENT_V1.0.pdf, publicProManual-1755343081262-715558279.pdf, Chatbot_Capabilities.pdf  

> **Response:**
> 💡 उत्तर
> पोर्टल पर ईएमडी/बिड सिक्योरिटी के लिए निम्नलिखित भुगतान रूप स्वीकार किए जाते हैं: ऑनलाइन (Internet Banking, RTGS/CHALLAN), चेक, बैंक ड्राफ्ट।
>
> 📋 प्रक्रिया
> 1. पोर्टल पर "FEES TO BE PAID" सेक्शन में जाएं।
> 2. "EMD/BID SECURITY" वाले एंट्री के आगे "Select Payment mode as RTGS/CHALLAN & save" बटन पर क्लिक करें।
> 3. सिस्टम द्वारा निर्देशित भुगतान मोड का चयन करें और भुगतान पूर्ण करें।
>
> 📘 स्रोत: EMD_CHALLAN_PAYMENT_V1.0.pdf, Chatbot_Capabilities.pdf

### Q27. निविदा जमा करने के बाद ईएमडी कितने दिनों तक वैध रहनी चाहिए?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 36.95s  |  **Sources:** 4  
- **Cited:** Manual_for_Procurement_of_works_2019.pdf, Store_Purhase_Rules_28.01.2021.pdf, publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf  

> **Response:**
> 💡 उत्तर
> निविदा जमा करने के बाद ईएमडी (Earnest Money Deposit), जिसे Bid Security भी कहा जाता है, की वैधता अवधि निविदा के प्रकार पर निर्भर करती है। सामान्य तौर पर, OTE (Open Tender Enquiries) के लिए यह 90 दिन और GTE (Government Tender Enquiries) के लिए 120 दिन होती है। यदि परिस्थितियाँ असामान्य हैं, तो विभाग ईएमडी की वैधता अवधि बढ़ाने का अनुरोध कर सकता है।
>
> 📋 प्रक्रिया
> 1. निविदा दस्तावेज़ों में निविदा की वैधता अवधि स्पष्ट रूप से बताई जाती है।
> 2. यदि आवश्यक हो, तो विभाग ईएमडी की वैधता अवधि बढ़ाने के लिए बोलीदाता से लिखित में अनुरोध कर सकता है।
> 3. ईएमडी की वैधता अवधि को निविदा की अंतिम तिथि तक वैध रखा जाना चाहिए।
>
> 📘 स्रोत: publicProManual-1755343081262-715558279.pdf

### Q28. निविदा समाप्त होने के बाद ईएमडी रिफंड कैसे प्राप्त करें?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `EMD_REFUND` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 43.41s  |  **Sources:** 4  
- **Cited:** Online_EMD_Refund_Notice.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf, store purchase rule cg.pdf  

> **Response:**
> 💡 उत्तर
> निविदा समाप्त होने के बाद EMD रिफंड प्राप्त करने की प्रक्रिया इस प्रकार है:
>
> 1. विभाग प्रशासक/टेंडर मालिक EMD रिफंड प्रक्रिया शुरू करते हैं।
> 2. अनुमोदन के लिए विभाग अनुमो्षक द्वारा सत्यापन किया जाता है।
> 3. एक बार विभाग द्वारा अनुमोदन हो जाने के बाद, e-Procurement प्रणाली बैंक को संबंधित खाते में EMD की वापसी के लिए निर्देश भेजती है, जो कि पंजीकृत विवरण संख्या के अनुसार bidder profile/registration details पर दर्ज है।
> 4. EMD रिफंड MIS पहले से ही e-procurement पोर्टल पर उपलब्ध है, जिसका उपयोग विभाग और बिडर अपने लॉगिन के माध्यम से EMD रिफंड स्थिति की जांच करने के लिए कर सकते हैं।
> 5. EMD की स्थिति जानने के लिए CHiPS कार्यालय जाने की आवश्यकता नहीं है, क्योंकि यह पहले से ही पोर्टल पर ऑनलाइन उपलब्ध है।
> 6. वापसी और विभाग अधिकारियों द्वारा अनुमोदन के 1 या 2 दिनों के भीतर, EMD राशि संबंधित बिडर के खाते में जमा हो जाती है।
>
> 📋 प्रक्रिया
> 1. विभाग प्रशासक रिफंड शुरू करते हैं।
> 2. विभाग अनुमो्षक सत्यापन और अनुमोदन करता है।
> 3. e-Procurement प्रणाली बैंक को निर्देश भेजती है।
> 4. बैंक EMD की वापसी करता है।
> 5. बिडर के खाते में EMD राशि जमा हो जाती है।
>
> 📘 स्रोत: EMD Refund Guidelines (CHiPS)

### Q29. क्या मैं एक ही निविदा के लिए एक से अधिक बोलियां जमा कर सकता हूं?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 46.58s  |  **Sources:** 3  
- **Cited:** GFR2017_HINDI.pdf, Manual_for_Procurement_of_works_2019.pdf, Store_Purhase_Rules_28.01.2021.pdf  

> **Response:**
> 💡 उत्तर
> हाँ, यदि निविदा का अनुमानित मूल्य 1= रू. 1,00,001 से 200 लाख तक है तो एक ही निविदा के लिए एक से अधिक बोलियां जमा की जा सकती हैं। 
>
> 📋 प्रक्रिया
> 1. खुली निविदा पद्धति में लोक विज्ञापन द्वारा नियमानुसार बोलियां बुलाने चाहिए।
> 2. निविदा बुलाने हेतु निम्नलिखित लोक विज्ञापन किए जाने चाहिए:
>  - रू. 1,00,001 से 200 लाख तक: स्थानीय स्तर के बहुप्रचारित एक समाचार पत्र में।
>  - रू. 200 लाख से अधिक तथा रू. 10.00 लाख तक: प्रदेश स्तरीय बहुप्रचारित दो समाचार पत्रों में।
>  - रू. 10,000 लाख से अधिक तथा रू. 20.00 लाख तक: प्रदेश स्तरीय बहुप्रचारित दो समाचार पत्रों में तथा राष्ट्रीय स्तर के एक समाचार पत्र में।
>  - रू. 20.00 लाख से अधिक: प्रदेश स्तरीय बहुप्रचारित दो समाचार पत्रों में तथा राष्ट्रीय स्तर के दो समाचार पत्रों में।
> 3. निविदा बुलाने की प्रक्रिया इन्टरनेट पर भी की जा सकती है, परन्तु केन्द्रीय क्षेत्रीय / केन्द्र प्रवर्तित योजनाओं के अंतर्गत क्रय के मामलों में भारत सरकार द्वारा निर्देशित क्रय की निर्धारित / उल्लेखित प्रक्रिया का पालन किया जाना चाहिए। 
>
> 📘 स्रोत: Store_Purhase_Rules_28.01.2021.pdf

### Q30. डिजिटल सिग्नेचर सर्टिफिकेट (DSC) क्या है और यह क्यों आवश्यक है?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `DSC` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 40.7s  |  **Sources:** 4  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Bid_Submission_Manual_English.pdf, CHiPS_Vendor_Registration_Manual_English.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf  

> **Response:**
> 💡 उत्तर
> डिजिटल सिग्नेचर सर्टिफिकेट (DSC) एक उच्च-सुरक्षा प्रमाणपत्र है जो Class II या Class III का होता है, जिसका उपयोग e-procurement पोर्टल पर लॉग इन करने और निविदा प्रक्रिया में भाग लेने के लिए किया जाता है। यह सुनिश्चित करता है कि लेनदेन सुरक्षित हैं और किसी भी छेड़छाड़ को रोका जा सके। DSC की आवश्यकता इसलिए है क्योंकि यह एक डिजिटल पहचान प्रदान करता है और e-Procurement साइट तक पहुँचने के लिए आवश्यक है।
>
> 📋 प्रक्रिया
> 1. DSC प्राप्त करें: आपको e-Mudhra, GNFC, IDRBT, MTNLTrustline, NIC या Safescrypt जैसे किसी भी प्रमाणित CA (Certifying Authority) से Class II या III का Signing & Encryption DSC प्राप्त करना होगा।
> 2. पंजीकरण: CPPP पोर्टल पर पंजीकरण करने के लिए DSC की आवश्यकता होती है।
> 3. दस्तावेज़ सत्यापन: भारतीय दूतावास के माध्यम से अपने दस्तावेजों को सत्यापित करें।
> 4. फंड ट्रांसफर: अपने देश की मुद्रा में Rupee के बराबर ऑनलाइन फंड ट्रांसफर करें (CA के बैंक का SWIFT कोड प्राप्त करें)।
>
> 📘 स्रोत:
> CHiPS_Vendor_Registration_Manual_English.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf

### Q31. नए रिन्यू किए गए डीएससी (DSC) को अपने प्रोफाइल से कैसे जोड़ें?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `DSC` (conf 0.8) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 36.13s  |  **Sources:** 4  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Bid_Submission_Manual_English.pdf, CHiPS_Vendor_Registration_Manual_English.pdf, Manual_Offline_Tenders_v.1.0.pdf  

> **Response:**
> 💡 उत्तर
> नए रिन्यू किए गए डीएससी (Digital Signature Certificate) को अपने प्रोफाइल से जोड़ने की प्रक्रिया इस प्रकार है:
>
> पोर्टल पर लॉग इन करने के बाद, "Register DSC" विकल्प चुनें। इससे आप अपने नए डीएससी को अपने प्रोफाइल में जोड़ सकते हैं।
>
> 📋 प्रक्रिया
> 1. पोर्टल पर लॉग इन करें।
> 2. "Register DSC" विकल्प ढूंढें और उस पर क्लिक करें।
> 3. डीएससी को अपने प्रोफाइल से लिंक करें।
>
> 📘 स्रोत:
> [Source 1: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf], [Source 2: CHiPS_Bid_

### Q32. क्या एक ही डीएससी का उपयोग दो अलग-अलग लॉगिन आईडी के लिए किया जा सकता है?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `DSC` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 33.28s  |  **Sources:** 4  
- **Cited:** CHiPS_Bid_Submission_Manual_English.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, Vigilance Manual 2021 (Hindi).pdf, Compilation of CVC Circulars and Guidelines.pdf  

> **Response:**
> 💡 उत्तर
> एक ही डीएससी (डिजिटल सिग्नेचर सर्टिफिकेट) का उपयोग दो अलग-अलग लॉगिन आईडी के लिए नहीं किया जा सकता है। यह सुरक्षा कारणों से किया जाता है। प्रत्येक लॉगिन आईडी के लिए एक अलग डीएससी की आवश्यकता होती है।
>
> 📋 प्रक्रिया
> 1. CHiPS पोर्टल पर लॉग इन करें।
> 2. अपने डीएससी को प्रमाणित करने के लिए e-Mudhra, GNFC, IDRBT, MTNLTrustline, NIC या Safescrypt जैसे अधिकृत CA से एक क्लास II या क्लास III डीएससी प्राप्त करें।
> 3. सुनिश्चित करें कि आपके पास वैध डीएससी है।
>
> 📘 स्रोत: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf

### Q33. अगर मेरा डीएससी (DSC) टोकन ब्लॉक हो जाए तो मुझे क्या करना चाहिए?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `DSC` (conf 0.8) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 41.62s  |  **Sources:** 4  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Vendor_Registration_Manual_English.pdf, CHiPS_Bid_Submission_Manual_English.pdf, Vigilance Manual 2021 (Hindi).pdf  

> **Response:**
> 💡 उत्तर
> यदि आपका डीएससी (DSC) टोकन ब्लॉक हो जाए तो आपको निम्नलिखित कदम उठाने होंगे:
>
> 1. डीएससी सर्विस प्रोवाइडर से संपर्क करें: गलत टोकन पासवर्ड इस्तेमाल किए जाने पर या अधिकृत समय सीमा से अधिक बार प्रयास करने पर डीएससी ब्लॉक हो सकता है। इस स्थिति में, आपको तुरंत डीएससी सर्विस प्रोवाइडर से संपर्क करके इसे अनलॉक करवाना होगा।
> 2. अनलॉकिंग प्रक्रिया का पालन करें: डीएससी सर्विस प्रोवाइडर के निर्देशों का पालन करें और आवश्यक जानकारी प्रदान करें ताकि वे आपके डीएससी को अनलॉक कर सकें।
>
> 📋 प्रक्रिया
> 1. डीएससी ब्लॉक होना: गलत टोकन पासवर्ड या अधिकृत प्रयासों से अधिक बार प्रयास करने पर डीएससी ब्लॉक हो जाता है।
> 2. डीएससी सर्विस प्रोवाइडर से संपर्क: डीएससी ब्लॉक होने की स्थिति में, संबंधित डीएससी सर्विस प्रोवाइडर से संपर्क करें।
> 3. अनलॉकिंग अनुरोध: डीएससी सर्विस प्रोवाइडर को अनलॉकिंग के लिए अनुरोध भेजें।
> 4. निर्देशों का पालन: डीएससी सर्विस प्रोवाइडर द्वारा दिए गए निर्देशों का सावधानीपूर्वक पालन करें।
> 5. डीएससी अनलॉक: डीएससी सर्विस प्रोवाइडर आपके डीएससी को अनलॉक कर देगा।
>
> 📘 स्रोत: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf

### Q34. ई-प्रोक्योरमेंट पोर्टल की हेल्पलाइन टीम का संपर्क नंबर क्या है?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 33.93s  |  **Sources:** 5  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Vendor_Registration_Manual_English.pdf, Chatbot_Capabilities.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf, Vigilance Manual 2021 (Hindi).pdf  

> **Response:**
> 💡 उत्तर
> ई-प्रोक्योरमेंट पोर्टल की हेल्पलाइन टीम का संपर्क नंबर है 1800 419 9140। यह हेल्पलाइन सुबह 9.00 बजे से रात 11.00 बजे (IST) के बीच उपलब्ध है।
>
> 📋 प्रक्रिया
> 1. CPPP Portal पर हेल्पडेस्क विकल्प खोजें।
> 2. 1800 419 9140 नंबर पर कॉल करें।
> 3. या, helpdesk.eproc@cgswan.gov.in पर ईमेल करें।
>
> 📘 स्रोत: CHiPS_Vendor_Registration_Manual_English.pdf

### Q35. बोली लगाने के दौरान तकनीकी दस्तावेज कैसे अपलोड करें?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `DOCUMENT_REQUIREMENTS` (conf 0.6) ❌  |  **Outcome:** ANSWERED  |  **Latency:** 55.65s  |  **Sources:** 3  
- **Cited:** Manual_Offline_Tenders_v.1.0.pdf, mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf  

> **Response:**
> 💡 उत्तर
> तकनीकी दस्तावेज अपलोड करने की प्रक्रिया इस प्रकार है:
>
> 1. “Offline Tender” पर क्लिक करें।
> 2. सभी तकनीकी दस्तावेजों को स्क्रीन पर दिखाए गए अनुसार भरें।
> 3. “SAVE” पर क्लिक करें।
> 4. “Attachment” पर क्लिक करें।
> 5. उपयुक्त तकनीकी दस्तावेज का चयन करने के लिए “BROWSE” पर क्लिक करें, फिर “SIGN FILE” पर क्लिक करें।
> 6. अपना DSC (Digital Signature Certificate) चुनें और “OK” पर क्लिक करें।
> 7. साइन किए गए दस्तावेज़ को अपलोड करने के लिए “Attach/Detach” पर क्लिक करें।
> 8. अपलोड किए गए दस्तावेज़ का लिंक स्क्रीन पर उपलब्ध है।
> 9. “ADD ROW” पर क्लिक करें और बोलीदाताओं द्वारा आवश्यक सहायक दस्तावेजों को दर्ज करें, फिर “SAVE” पर क्लिक करें।
> 10. “Payment” पर क्लिक करें।
> 11. भुगतान विवरण दर्ज करें और “SAVE” पर क्लिक करें।
> 12. “Evaluation” पर क्लिक करें।
> 13. PAN नंबर दर्ज करके बोलीदाताओं को जोड़ने के लिए “ADD ROW” पर क्लिक करें और खोजें (“SEARCH”) पर क्लिक करें।
> 14. बोलीदाता का नाम सत्यापित करें और L1, L2...Ln के रूप में रैंक की पुष्टि करने के लिए “OK” पर क्लिक करें।
>
> 📋 प्रक्रिया
> 1. “Offline Tender” पर क्लिक करें।
> 2. सभी तकनीकी दस्तावेजों को भरें।
> 3. “SAVE” पर क्लिक करें।
> 4. “Attachment” पर क्लिक करें।
> 5. दस्तावेज़ का चयन करें और “SIGN FILE” पर क्लिक करें।
> 6. DSC चुनें और “OK” पर क्लिक करें।
> 7. दस्तावेज अपलोड करें।
> 8. “ADD ROW” पर क्लिक करें और सहायक दस्तावेज दर्ज करें।
> 9. “SAVE” पर क्लिक करें।
> 10. भुगतान करें।
> 11. मूल्यांकन करें।
> 12. बोलीदाताओं को PAN नंबर से जोड़ें और खोजें।
> 13. बोलीदाता का नाम सत्यापित करें और रैंक की पुष्टि करें।
>
> 📘 स्रोत: mannual procurement.pdf

### Q36. क्या कोई विदेशी कंपनी इस पोर्टल पर पंजीकरण कर सकती है?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `VENDOR_REGISTRATION` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 38.41s  |  **Sources:** 4  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, publicProManual-1755343081262-715558279.pdf, it_act_2000_updated hindi.pdf, GFR2017_HINDI.pdf  

> **Response:**
> 💡 उत्तर
> I'm not fully certain this matches your question - please verify with the cited document.
> विदेशी कंपनी इस पोर्टल पर पंजीकरण कर सकती है, लेकिन पूर्व में पोर्टल पर पंजीकरण आवश्यक है। कृपया "Manuals" अनुभाग में Vendor Registration मैनुअल (हिंदी और अंग्रेजी दोनों में) देखें।
>
> 📋 प्रक्रिया
> 1. पोर्टल पर "New Supplier Registration" विकल्प चुनें।
> 2. विदेशी कंपनी के लिए, GFR 2017 के प्रावधानों का पालन करना होगा।
> 3. पंजीकरण आवेदन में कंपनी की योग्यता, विशेषज्ञता, जनशक्ति, वित्तीय संसाधन और अन्य प्रासंगिक सुविधाओं का मूल्यांकन किया जाएगा।
> 4. कंपनी के बैंकर्स से वित्तीय स्थिति पर सलाह ली जाएगी।
> 5. नियंत्रक (Controller) शर्तों और निबंधनों के अधीन विदेशी प्रमाणकर्ता प्राधिकारी को इस अधिनियम के प्रयोजन के लिए प्रमाणकर्ता प्राधिकारी के रूप में मान्यता दे सकेगा।
>
> 📘 स्रोत: publicProManual-1755343081262-715558279.pdf

### Q37. जावा सुरक्षा त्रुटि 'Application Blocked by Security Setting' आने पर क्या करें?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 42.08s  |  **Sources:** 5  
- **Cited:** CHiPS_Bid_Submission_Manual_English.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, Preferred_System_Configuration_V_2.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf, EDGE_Browser_Setup_V1.0.pdf  

> **Response:**
> 💡 उत्तर
> जावा सुरक्षा त्रुटि ‘Application Blocked by Security Setting’ आने पर निम्नलिखित उपाय करें:
>
> 1. Control Panel → Java Control Panel → Security में जाकर Java security level को Medium या High पर सेट करें।
> 2. Control Panel → Java Control Panel → Security में, eproc.cgstate.gov.in URL को Exception Site List में जोड़ें।
> 3. IE में, eproc.cgstate.gov.in URL को Compatibility View Settings में जोड़ें।
> 4. IE → Tools → Internet Options → Security में, eproc.cgstate.gov.in URL को Trusted Site List में जोड़ें।
> 5. Internet और Trusted sites के लिए ActiveX संबंधित विकल्पों के लिए Enable या Prompt सेट करें।
>
> 📋 प्रक्रिया
> 1. Start menu > Windows+Run > enter the command inetcpl.cpl and click Ok से Internet Properties खोलें।
> 2. Security > Trusted Sites पर क्लिक करें।
> 3. Internet विकल्प: Medium-high (default) और Trusted sites: Medium (default) सेट करें।
> 4. ‘Enable or Prompt for the required ActiveX related options’ विकल्प को

### Q38. मैं अपने ऑनलाइन ईएमडी भुगतान की स्थिति कैसे देख सकता हूं?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 47.15s  |  **Sources:** 3  
- **Cited:** EMD_CHALLAN_PAYMENT_V1.0.pdf, CHiPS_Bid_Submission_Manual_English.pdf, publicProManual-1755343081262-715558279.pdf  

> **Response:**
> 💡 उत्तर
> अपने ऑनलाइन EMD भुगतान की स्थिति देखने के लिए, निम्नलिखित चरणों का पालन करें:
>
> 1. e-Procurement पोर्टल पर लॉग इन करें, अपने यूजर आईडी और पासवर्ड का उपयोग करके।
> 2. "All Live Tenders" सेक्शन में जाएं।
> 3. उस टेंडर का चयन करें जिसके लिए आपने EMD भुगतान किया है।
> 4. "View Tender" बटन पर क्लिक करें।
> 5. फिर "INTERSTED" विकल्प चुनें।
> 6. I AGREE/ACCEPT पर क्लिक करें।
> 7. "Pay Tender/Processing Fee" बटन पर क्लिक करें।
> 8. "Payment mode as Internet Banking" का चयन करें और सेव करें।
> 9. "PAY NOW" बटन पर क्लिक करें।
> 10. भुगतान सफलतापूर्वक होने के बाद, सिस्टम आपको भुगतान विवरण और स्थिति दिखाएगा। आप "Verify Payment Status" विकल्प का उपयोग करके अपनी भुगतान स्थिति की जांच कर सकते हैं।
>
> 📋 प्रक्रिया
> 1. e-Procurement पोर्टल पर लॉग इन करें।
> 2. "All Live Tenders" सेक्शन में जाएं।
> 3. टेंडर चुनें।
> 4. "View Tender" पर क्लिक करें।
> 5. "INTERSTED" विकल्प चुनें।
> 6. I AGREE/ACCEPT पर क्लिक करें।
> 7. "Pay Tender/Processing Fee" पर क्लिक करें।
> 8. Internet Banking का चयन करें और सेव करें।
> 9. "PAY NOW" पर क्लिक करें।
> 10. भुगतान की स्थिति जांचें।
>
> 📘 स्रोत: EMD_CHALLAN_PAY

### Q39. यदि मैं बोली जमा करने की अंतिम तिथि के बाद अपनी बोली वापस लेता हूं तो क्या होगा?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `BID_SUBMISSION` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 39.58s  |  **Sources:** 4  
- **Cited:** GFR2017_HINDI.pdf, FInal_GFR_upto_31_07_2024.pdf, CHiPS_Bid_Submission_Manual_English.pdf, publicProManual-1755343081262-715558279.pdf  

> **Response:**
> 💡 उत्तर
> यदि आप बोली जमा करने की अंतिम तिथि के बाद अपनी बोली वापस लेते हैं, तो निम्नलिखित परिणाम हो सकते हैं:
>
> 1. बोलीदाता को निलंबन अवधि का सामना करना पड़ सकता है, जो कि निविदा दस्तावेज में निर्धारित की गई अवधि के लिए हो सकती है।
> 2. उन्हें भविष्य की निविदाओं में भाग लेने से रोका जा सकता है।
> 3. अंतिम बोली वापस लेने पर, निविदा दस्तावेज़ में उल्लिखित प्रावधानों के अनुसार, संबंधित विभाग या एजेंसी द्वारा आगे की कार्रवाई की जा सकती है।
>
> 📋 प्रक्रिया
> 1. बोलीदाता द्वारा अंतिम तिथि के बाद बोली वापस ली जाती है।
> 2. विभाग निविदा दस्तावेज में उल्लिखित नियमों और शर्तों के अनुसार कार्रवाई करता है।
> 3. यदि कोई प्रावधान है कि बोली वापस लेने पर निलंबन अवधि लागू होती है, तो उस अवधि के लिए बोलीदाता को निलंबित कर दिया जाता है।
> 4. अंतिम बोली वापस लेने की सूचना संबंधित पक्षों को दी जाती है।
>
> 📘 स्रोत: FInal_GFR_upto_31_07_2024.pdf

### Q40. पंजीकरण के बाद क्या मैं अपनी कंपनी के प्रोफाइल विवरण में बदलाव कर सकता हूं?

- **Role/Lang:** Vendor · Hindi  
- **Intent:** `VENDOR_REGISTRATION` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 29.41s  |  **Sources:** 4  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, publicProManual-1755343081262-715558279.pdf, GFR2017_HINDI.pdf, mannual procurement.pdf  

> **Response:**
> 💡 उत्तर
> अपनी कंपनी प्रोफाइल में बदलाव करने की सुविधा आपके लिए उपलब्ध है। आप अपने विक्रेता लॉगिन में संबंधित विवरणों को संपादित कर सकते हैं।
>
> 📋 प्रक्रिया
> 1. विक्रेता लॉगिन में प्रवेश करें।
> 2. अपनी कंपनी प्रोफाइल में आवश्यक परिवर्तन करें।
> 3. परिवर्तनों को सहेजें।
>
> 📘 स्रोत: FAQ of Chhattisgarh Infotech Promotion Society(CHiPS).pdf

## — Vendor · Hinglish —

### Q41. Portal me vendor registration kaise kare?

- **Role/Lang:** Vendor · Hinglish  
- **Intent:** `VENDOR_REGISTRATION` (conf 0.8) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 39.5s  |  **Sources:** 4  
- **Cited:** CHiPS_Vendor_Registration_Manual_English.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, mannual procurement.pdf, publicProManual-1755343081262-715558279.pdf  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> Vendor registration karne ke liye, aap Chhattisgarh e-Procurement portal par ja sakte hain. First, aapko Supplier Registration Manual (CHiPS_Vendor_Registration_Manual_English.pdf) mein deewani darjein padhen. Portal par "New Supplier Registration" option select karein aur required details bhar dein. System validation ke liye “Save & Next” button dabayein aur DSC (Digital Signature Certificate) select karein. Aapko CRN (Chhattisgarh Registration Number) bhi generate karna hoga.
>
> 📋 Process
> 1. CHiPS portal par "New Supplier Registration" option ko select karein.
> 2. PAN details bhar dein.
> 3. CRN certificate ki scanned copy upload karein.
> 4. Preferred Login Code generate karein (VENDORI2345, VENDOR12345).
> 5. “Save & Next” button dabayein aur KSINCH@CMAIL COMI INDIA GUJARAT AHMEDABAD DARUN last time provide karein.
>
> 📘 Source: Supplier Registration Manual (CHiPS_Vendor_Registration_Manual_English.pdf)

### Q42. Password bhool gaya hu, reset kaise hoga?

- **Role/Lang:** Vendor · Hinglish  
- **Intent:** `PORTAL_USAGE` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 34.73s  |  **Sources:** 3  
- **Cited:** CHiPS_Bid_Submission_Manual_English.pdf, AuctionManual_FA.pdf, CHiPS_Vendor_Registration_Manual_English.pdf  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> If you have forgotten your password, you can reset it using the Digital Signature Certificate (DSC) or OTP method as outlined in the CPPP Portal. First, click on "Password Recovery Using DSC or OTP". Then, enter your User ID and registered email address, mobile number, or PAN. After that, validate using your DSC or OTP. A new password creation option will appear.
>
> 📋 Process
> 1. Click “Password Recovery Using DSC or OTP”.
> 2. Enter User ID & registered Email address or Mobile or Pan.
> 3. Enter Captcha.
> 4. Validate using DSC or OTP.
> 5.

### Q43. EMD exemption ke liye kaun se documents upload karne padenge?

- **Role/Lang:** Vendor · Hinglish  
- **Intent:** `EMD_GENERAL` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 35.23s  |  **Sources:** 3  
- **Cited:** Guidelines_To_Bidders_EPS_v1.6.pdf, publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> Unsuccessful bidders who fall under exempt categories can furnish a certified copy of their valid registration details. Specifically, those falling under DPIIT recognized MSMEs are exempt from paying EMD and need to provide this certificate. Bidders must also provide correct account details during registration for EMD/Bid Security refund purposes, though CHiPS/System Integrator will not verify these details.
>
> 📋 Process
> 1. Check if the bidder falls under a DPIIT recognized MSME category.
> 2. If so, prepare and upload a certified copy of the valid registration details.
> 3. Provide correct account details during portal registration for potential EMD/Bid Security refund.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf

### Q44. DSC register karne ka sahi tarika kya hai?

- **Role/Lang:** Vendor · Hinglish  
- **Intent:** `DSC` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 37.83s  |  **Sources:** 5  
- **Cited:** CHiPS_Vendor_Registration_Manual_English.pdf, CHiPS_Bid_Submission_Manual_English.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf, mannual procurement.pdf  

> **Response:**
> 💡 Answer
> DSC ko register karne ka sahi tarika yeh hai: (1) pehle class II ya class III DSC procure karein jo signing aur encryption dono certificates ke saath registered ho, (2) registration details fill karein aur Save & Next click karein, (3) ‘Selecting DSC’ step par appropriate Digital Signature Certificate select karein, (4) successful selection ke baad Terms & Conditions ko accept karne ke liye Confirmation click karein.
>
> 📋 Process
> 1. Class II ya class III DSC procure karein jo signing aur encryption dono certificates ke saath registered ho.
> 2. Registration details fill karein aur Save & Next click karein.
> 3. ‘Selecting DSC’ step par appropriate Digital Signature Certificate select karein.
> 4. Successful selection ke baad Terms & Conditions ko accept karne ke liye Confirmation click karein.
>
> 📘 Source: CHiPS_Vendor_Registration_Manual_English.pdf

### Q45. System configuration check karne ke liye download section me kaun sa file milega?

- **Role/Lang:** Vendor · Hinglish  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 31.58s  |  **Sources:** 4  
- **Cited:** Preferred_System_Configuration_V_2.pdf, EDGE_Browser_Setup_V1.0.pdf, CHiPS_Bid_Submission_Manual_English.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> System configuration check karne ke liye download section me "Preferred System Configuration V_2.pdf" file milega. Is file mein Operating System, Browser aur Java ke liye preferred requirements given hain.
>
> 📋 Process
> 1. CHiPS website par jayein.
> 2. “Downloads” section me navigate karein.
> 3. “Preferred System Configuration V_2.pdf” file download karein.
> 4. File ko open karein aur system configuration guidelines follow karein.
>
> 📘 Source: Preferred System Configuration V_2.pdf

### Q46. Online payment failure hone par refund kab tak aayega?

- **Role/Lang:** Vendor · Hinglish  
- **Intent:** `EMD_REFUND` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 36.99s  |  **Sources:** 3  
- **Cited:** Online_EMD_Refund_Notice.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf, publicProManual-1755343081262-715558279.pdf  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> If an online EMD payment fails to credit to the bidder’s account within the Bid Due Date, the refund process is initiated by the Department Admin. The e-Procurement system then automatically instructs the bank to refund the EMD back to the bidder's account as per the registered details. The MIS is available on the portal for checking the EMD refund status.
>
> 📋 Process
> 1. The tender owner/department admin initiates the EMD remittance/refund process for unsuccessful bidders after PQ/Technical Bid and Price Bid evaluation.
> 2. Once approved by the Department Approver, the e-Procurement system automatically sends instructions to the bank for EMD refund to the bidder’s account.
> 3. The EMD refund status is available on the e-procurement portal for both departments and bidders.
>
> 📘 Source: Online_EMD_Refund_Notice.pdf

### Q47. Portal support team ka toll free number aur email id kya hai?

- **Role/Lang:** Vendor · Hinglish  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 30.68s  |  **Sources:** 4  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Vendor_Registration_Manual_English.pdf, AuctionManual_FA.pdf, Manual_Offline_Tenders_v.1.0.pdf  

> **Response:**
> 💡 Answer
> Portal support team ka toll free number 1800 419 9140 hai, jo 9.00 AM se 11.00 PM (IST) tak available hai. Email id helpdesk.

### Q48. Bid submit karne ke baad usko withdraw kaise kiya ja sakta hai?

- **Role/Lang:** Vendor · Hinglish  
- **Intent:** `BID_SUBMISSION` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 44.19s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, GFR2017_HINDI.pdf, Manual_for_Procurement_of_works_2019.pdf  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> Bid submit karne baad usko withdraw karne ke liye, bidder ko iski ek few options hai. Agar bidder ne offer ko ek specific period ke liye open rakhne ka assurance diya hai, lekin koi consideration (e.g., EMD) nahi deposit kiya hai, to woh kisi bhi time tak withdrawal kar sakta hai jab accepting authority apna acceptance declare na kare – yani, acceptance letter dispatch hone ke baad bhi. Agar bidder ne offer ko open rakhne ke liye koi consideration deposit kiya hai (e.g., EMD), to agar uss period mein woh withdraw karta hai, to accepting authority EMD ko forfeit kar sakta hai aur bid securing declaration ya kisi aur relevant clause ka use kar sakta hai. Aapko yeh bhi yaad rakhna chahiye ki offer validity expire hone ke baad automatically lapse ho jaata hai.
>
> 📋 Process
> 1. Bidder ne offer ko open rakhne ka assurance diya ho.
> 2. Bidder withdrawal karne ka decision leta hai.
> 3. Withdrawal request accepting authority ko time pe pahunchana hai – acceptance letter dispatch hone se pehle.
> 4. Accepting authority withdrawal accept karegi aur EMD forfeit kar sakta hai, ya bid securing declaration use kar sakta hai.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf

### Q49. Digital signature block ho gaya hai, isko unlock kaise kare?

- **Role/Lang:** Vendor · Hinglish  
- **Intent:** `DSC` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 29.95s  |  **Sources:** 3  
- **Cited:** it_act_2000_updated english.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> Agar Digital Signature Certificate block ho gaya hai, to usko unlock karne ke liye vendor ko DSC service provider se contact karna hoga. DSC service provider certificate ko unlock karwaega.
>
> 📋 Process
> 1. Vendor ko DSC service provider se contact karna hoga.
> 2. DSC service provider certificate ko unlock karwaega.
> 3. Unlock karne ke baad, Digital Signature Certificate phir se kaam karne lagega.
>
> 📘 Source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS)

### Q50. Kya foreign bidder ko registration ke liye PAN card chahiye?

- **Role/Lang:** Vendor · Hinglish  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 33.33s  |  **Sources:** 5  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Vendor_Registration_Manual_English.pdf, CHiPS_Bid_Submission_Manual_English.pdf, 160616_AMC_AC short tender.pdf, publicProManual-1755343081262-715558279.pdf  

> **Response:**
> 💡 Answer
> Foreign bidders need to provide a PAN card during vendor registration. This is mandatory as stated in the CHIPS FAQ document.
>
> 📋 Process
> 1. The vendor needs to enter their PAN card details while registering on the e-Procurement portal.
> 2. Correctness of the PAN card details is essential for the registration process.
> 3. The vendor must select “New User” and then “Enter”.
>
> 📘 Source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf

## — Officer · English —

### Q51. What is the limit for purchase without quotation under GFR?

- **Role/Lang:** Officer · English  
- **Intent:** `RULES_GFR` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 38.75s  |  **Sources:** 4  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, publicProManual-1755343081262-715558279.pdf, GFRupdatedupto31012026.pdf, GFR2017_HINDI.pdf  
- **Answer entities:** Thresholds: Rs. 50,000, Rs. 1,00,000  

> **Response:**
> 💡 Answer
> The General Financial Rules (GFR) allow for purchases up to the value of Rs. 50,000 (Rupees fifty thousand) only on each occasion without inviting quotations or bids, provided a certificate is recorded by the competent authority in a specific format. However, this limit is enhanced to Rs. 1,00,000/- (Rupees one lakh) for Scientific Ministries/ Departments/ Organizations as outlined in the document.
>
> 📋 Process
> 1. Determine that the goods are not available on Government e-Marketplace (GeM).
> 2. The competent authority records a certificate confirming this.
> 3. Purchase of goods costing up to Rs. 50,000/- or Rs. 1,00,000/- is made without inviting quotations or bids.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf

### Q52. What are the rules for establishing a Local Purchase Committee?

- **Role/Lang:** Officer · English  
- **Intent:** `RULES_GFR` (conf 1.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 38.9s  |  **Sources:** 4  
- **Cited:** GFR2017_HINDI.pdf, GFRupdatedupto31012026.pdf, mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf  

> **Response:**
> 💡 Answer
> A Local Purchase Committee is established according to specific guidelines outlined in GFR2017_HINDI.pdf and mannual procurement.pdf. The committee consists of three members, including the Head of the Department and two other individuals with appropriate levels of expertise. These members must jointly record a certificate confirming satisfaction regarding the goods’ specifications, market price, and supplier reliability, ensuring no prohibition by the Department of Expenditure or concerned Ministry/Department.
>
> 📋 Process
> 1. The Local Purchase Committee is formed with three members as decided by the Head of the Department.
> 2. The committee surveys the market to assess rates, quality, and specifications.
> 3. Committee members jointly record a certificate confirming satisfaction regarding the goods’ specifications, market price, and supplier reliability. This certificate must state that the goods are of requisite specification and quality, priced at the prevailing market rate, and the supplier is reliable and competent. 
> 4. The committee ensures no prohibition by the Department of Expenditure or Ministry/Department concerned.
>
> 📘 Source: GFR2017_HINDI.pdf

### Q53. Under what conditions can a Limited Tender Enquiry be used?

- **Role/Lang:** Officer · English  
- **Intent:** `RULES_GFR` (conf 0.6) ✅  |  **Outcome:** CACHE  |  **Latency:** 2.05s  |  **Sources:** 3  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, GFRupdatedupto31012026.pdf, Manual_for_Procurement_of_works_2019.pdf  
- **Answer entities:** Rules: Rule 150  

> **Response:**
> 💡 Answer
> A Limited Tender Enquiry (LTE) can be utilized when the estimated value of goods to be procured is up to [Rupees Fifty Lakhs]. Specifically, it’s adopted when a pre-selected list of suppliers are approached for bidding, and unsolicited bids are generally not accepted. Efforts should be made to obtain more responsive bids on a competitive basis by identifying a higher number of approved suppliers.
>
> 📋 Process
> 1. The estimated value of goods to be procured is up to [Rupees Fifty Lakhs].
> 2. Copies of the bidding document are sent directly to registered suppliers as per Rule 150.
> 3. More than three supplier firms should be involved.
> 4. Limited tender enquiries should be published on GeM and the CPPP Portal.
>
> 📘 Source: FInal_GFR_upto_31_07_2024.pdf

### Q54. What is the minimum number of suppliers required for a Limited Tender?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 31.79s  |  **Sources:** 5  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Vendor_Registration_Manual_English.pdf, FInal_GFR_upto_31_07_2024.pdf, mannual procurement.pdf, GFRupdatedupto31012026.pdf  

> **Response:**
> 💡 Answer
> For a Limited Tender Enquiry (LTE), the Department needs to send the bid document to more than three approved suppliers/contractors.
>
> 📋 Process
> 1. The Department must identify and contact over three registered suppliers.
> 2. If fewer than three suppliers are available, the Department can still send the LTE to those available with approval from the Competent Authority (CA), documenting the reasons for doing so.
> 3. The Bidder Enlistment section should then be tasked with developing more sources.
>
> 📘 Source: mannual procurement.pdf

### Q55. What is the threshold value of procurement above which an Advertised Tender is mandatory?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** CACHE  |  **Latency:** 2.05s  |  **Sources:** 3  
- **Cited:** Manual_for_Procurement_of_works_2019.pdf, FInal_GFR_upto_31_07_2024.pdf, store purchase rule cg.pdf  
- **Answer entities:** Rules: Rule 162(i), Rule 162(iii), Rule 162)  

> **Response:**
> 💡 Answer
> The threshold value for procurement where an advertised tender becomes mandatory is [Rupees Fifty Lakhs]. This limit is specified in Rule 162(i) of the General Financial Rules. It’s important to note that even when exceeding this amount, a limited tender enquiry may be permissible under specific circumstances as outlined in Rule 162(iii), particularly if urgency justifies it.
>
> 📋 Process
> 1. The threshold value is [Rupees Fifty Lakhs].
> 2. If the estimated value of goods to be procured exceeds this limit, an advertised tender becomes mandatory.
> 3. However, a limited tender enquiry may be considered under Rule 162(iii) if there’s urgent demand and justification for bypassing the standard advertisement process.
>
> 📘 Source: FInal_GFR_upto_31_07_2024.pdf (Rule 162)

### Q56. What is the two-bid system, and when should it be followed?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 59.29s  |  **Sources:** 4  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf  

> **Response:**
> 💡 Answer
> **1. What is the two-bid system,**
> The two-bid system involves submitting technical and financial bids separately in sealed covers. The technical bid is opened first and evaluated by a committee, then only technically acceptable offers have their financial bids opened for ranking and awarding the contract.
>
> **2. when should the two-bid system, be followed**
> The two-envelope system should be followed where technically complex requirements exist, the capability of the source of supply is not critical, and the value of procurement is not high.
>
> 1. When technically complex requirements are present.
> 2. When the source of supply’s capability isn't crucial.
> 3. When the procurement value isn’t high.

### Q57. What are the guidelines for handling late bids under GFR Rule 165?

- **Role/Lang:** Officer · English  
- **Intent:** `RULES_GFR` (conf 0.8) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 33.23s  |  **Sources:** 2  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, GFRupdatedupto31012026.pdf  
- **Answer entities:** Rules: Rule 165  

> **Response:**
> 💡 Answer
> According to GFR Rule 165, late bids (i.e., bids received after the specified date and time for receipt of bids) should not be considered in advertised or limited tender enquiries. However, a bidder can withdraw from the procurement proceedings with adequate justification without forfeiting their bid security or facing penalties by declaring their intention to withdraw.
>
> 📋 Process
> 1. GFR Rule 165 states that late bids are not accepted.
> 2. A bidder may withdraw from the procurement process if they have sufficient justification.
>
> 📘 Source: FInal_GFR_upto_31_07_2024.pdf

### Q58. Under what circumstances is Single Tender procurement justified?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** CACHE  |  **Latency:** 2.07s  |  **Sources:** 3  
- **Cited:** mannual procurement.pdf, FInal_GFR_upto_31_07_2024.pdf, Manual_for_Procurement_of_works_2019.pdf  
- **Answer entities:** Rules: Rule 21  

> **Response:**
> 💡 Answer
> Single Tender procurement is justified under several specific circumstances as outlined across multiple documents. Primarily, it’s permissible when a procuring entity receives only one responsive bid, treating this as a ‘Single Tender,’ provided the quoted price is reasonable and certain conditions are met. Specifically, Rule 21 of DFPR (explained in mannual procurement.pdf) allows for placement with the single bidder if open competition isn't achieved. Furthermore, it’s justified when only one firm manufactures required goods or during emergencies necessitating purchase from a specific source, always requiring documented justification and competent authority approval (as detailed in FInal_GFR_upto_31_07_2024.pdf). Finally, it can be used for standardization of machinery parts if recommended by a technical expert and approved by the appropriate authority, as described in Manual_for_Procurement_of_works_2019.pdf.
>
> 📋 Process
> 1. Single Offer Situation: The procuring entity recognizes that only one bid has been received.
> 2. Price Assessment: The quoted price is evaluated to ensure it’s reasonable.
> 3. Condition Verification: All necessary requirements and formalities (standard conditions, industry-friendly specifications, wide publicity, sufficient time for bidding) were fulfilled during the initial tender process – as detailed in mannual procurement.pdf.
> 4. Emergency/Standardization Justification: If applicable, a valid reason is documented and approved (e.g., emergency or standardization need).
> 5. Approval: The competent authority grants approval for single-source procurement.
>
> 📘 Source: mannual procurement.pdf, FInal_GFR_upto_31_07_2024.pdf, Manual_for_Procurement_of_works_2019.pdf

### Q59. What are the GFR rules for EMD rates in government contracts?

- **Role/Lang:** Officer · English  
- **Intent:** `RULES_GFR` (conf 1.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 39.62s  |  **Sources:** 4  
- **Cited:** publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf, GFRupdatedupto31012026.pdf  
- **Answer entities:** Thresholds: 2%, 5%  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> According to the provided documents, the Bid Security (also known as Earnest Money Deposit or EMD) should generally range between two (2) and five (5) per cent of the estimated value of the goods to be procured. The Procuring Entity determines the exact amount, rounding it off to the nearest thousands of Rupees. These guidelines are outlined across multiple procurement manuals including Public Procurement Manual, Manual for Procurement of Works 2019, and mannual procurement.pdf.
>
> 📋 Process
> 1. The EMD rate is typically set between 2% and 5% of the estimated value of goods.
> 2. The Procuring Entity determines the specific amount, rounded to the nearest thousand Rupees.
> 3. The Bid Security must be obtained in acceptable forms like demand drafts, bank guarantees (including e-bank guarantees), or online payments.
>
> 📘 Source: mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf, publicProManual-1755343081262-715558279.pdf

### Q60. What is the range of Performance Security required for a contract?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 37.7s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf, GFRupdatedupto31012026.pdf  
- **Answer entities:** Thresholds: 3%, 10%, Rs 50 Crores, Rs 75 Lakhs, Rs 50 Cr  

> **Response:**
> 💡 Answer
> The requirement for Performance Security varies depending on the contract value and type. Generally, it’s between five to ten percent of the contract value for works contracts, with a typical range of 3% to 10%. For tenders above Rs 50 Crores, the ceiling can be up to Rs 75 Lakhs, while for tenders exceeding Rs 50 Cr but below Rs 300 Cr, it’s capped at Rs 3 Crore. For contracts valued at Rs one lakh or less, Performance Security is not required.
>
> 📋 Process
> 1. Determine the contract value.
> 2. Calculate the Performance Security amount based on the applicable percentage (5-10% for works).
> 3. Confirm the upper ceiling limit if the contract exceeds specified thresholds.
> 4. Ensure compliance with the specific requirements outlined in the tender documents.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf

### Q61. What forms of Performance Security are acceptable under GFR?

- **Role/Lang:** Officer · English  
- **Intent:** `RULES_GFR` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 40.11s  |  **Sources:** 3  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf  
- **Answer entities:** Thresholds: 10%, 60 days  

> **Response:**
> 💡 Answer
> Performance security can be furnished in several acceptable forms as outlined within the General Financial Rules (GFR) and related manuals. These include an Insurance Surety Bond, Account Payee Demand Draft, Fixed Deposit Receipt from a Commercial Bank, a Bank Guarantee (including e-Bank Guarantee) issued by a Commercial Bank, or an online payment safeguarding the purchaser’s interest. The amount required for performance security typically ranges from five to ten percent of the contract value, although this can be reduced to three percent until 31.03.2023 for procurement of works.
>
> 📋 Process
> 1. Determine the required Performance Security amount (typically 5-10% of the contract value).
> 2. Select an acceptable form of security as detailed in GFR and related manuals.
> 3. Prepare and submit the chosen instrument (e.g., Demand Draft, Bank Guarantee) to the Department Admin.
> 4. Ensure the validity period of the Performance Security is at least 60 days beyond the completion date of contractual obligations, including warranty periods.
>
> 📘 Source: FInal_GFR_upto_31_07_2024.pdf

### Q62. In what situations can Performance Security be exempted?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 37.26s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf  

> **Response:**
> 💡 Answer
> Performance Security can be exempted under specific circumstances as outlined in Public Procurement Manual - 1755343081262-715558279.pdf. Specifically, entities like Ministries, Departments, and Autonomous Bodies are exempt from submitting Performance Security when tendered against PACs. Additionally, for contracts spanning multiple years, procuring entities may proportionately reduce the security based on the remaining contract period. Finally, a contract value up to Rs. one lakh does not require Performance Security.
>
> 📋 Process
> 1. Entities like Ministries/Departments/Autonomous Bodies are exempt from submitting Performance Security when tendered against PACs.
> 2. Procuring entities can reduce performance security proportionally for multi-year contracts based on the remaining period.
> 3. Contracts valued up to Rs. one lakh do not require Performance Security.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf

### Q63. What is the procurement policy for products from Micro and Small Enterprises (MSEs)?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 41.1s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf, GFRupdatedupto31012026.pdf  
- **Answer entities:** Rules: Rule 153(ii) | Thresholds: 20%  

> **Response:**
> 💡 Answer
> The Government of India’s procurement policy for Micro and Small Enterprises (MSEs), as outlined in Rule 153(ii) of the General Financial Rules (GFR) 2017, aims to support inclusive national economic growth. This policy mandates preferential procurement of goods produced and services rendered by MSEs registered under Udyam Registration. Specifically, at least 20% of textile items required by Central Government departments must be procured from handloom origin items exclusively through KVIC and/or Handloom Clusters. Additionally, in the case of proprietary MSEs, the proprietor(s) are considered the SC/ST or Woman entrepreneur, while for partnership MSEs, the partners are treated as such.
>
> 📋 Process
> 1. MSEs registered under Udyam Registration are eligible to avail benefits under this policy.
> 2. At least 20% of textile items required by Central Government departments must be procured from handloom origin items exclusively through KVIC and/ or Handloom Clusters.
> 3. In the case of proprietary MSE, the proprietor(s) is considered the SC/ST or Woman entrepreneur.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf

### Q64. How are price preferences applied to MSEs in evaluation?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 39.98s  |  **Sources:** 1  
- **Cited:** publicProManual-1755343081262-715558279.pdf  
- **Answer entities:** Thresholds: 15%  

> **Response:**
> 💡 Answer
> When evaluating bids, a preference is given to Micro and Small Enterprises (MSEs) if they fall within a 15% margin of the lowest L1 price. Specifically, if the L1 bidder isn't an MSE, eligible MSE bidders whose prices are within that 15% range are invited to match the L1 price, and offered a further opportunity to compete for the entire quantity. This ensures that government procurement actively supports MSEs where possible.
>
> 📋 Process
> 1. If the L1 bidder is not an MSE, the system identifies eligible MSE bidders whose prices fall within the 15% preference margin of the L1 price.
> 2. These eligible MSE bidders are invited to match the L1 price.
> 3. If a matching bid is received from an MSE, that MSE receives the contract for the full quantity (or the portion not already awarded).
> 4. If no MSE bids match the L1 price, the contract proceeds to the original L1 bidder.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf

### Q65. What are the steps for procurement of consulting services under GFR?

- **Role/Lang:** Officer · English  
- **Intent:** `RULES_GFR` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 36.97s  |  **Sources:** 4  
- **Cited:** GFRupdatedupto31012026.pdf, FInal_GFR_upto_31_07_2024.pdf, publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf  

> **Response:**
> 💡 Answer
> Procurement of consulting services generally follows a process outlined within the Public Procurement Manual and GFR guidelines. The key steps involve identifying the need, engaging with the Financial Advisor, developing a detailed justification, and documenting the rationale for choosing a specific contractor.
>
> 📋 Process
> 1. **Identify Need & Consult:** Determine the requirement for consulting services and consult with the Financial Advisor to assess the best approach.
> 2. **Detailed Justification:** Develop a comprehensive proposal outlining the circumstances leading to the need for choice procurement, including special interests or purposes. This justification must be integral to the proposal.
> 3. **Competent Authority Approval:** The Competent Authority in the Ministry or Department must approve the procurement by choice.
> 4. **Documentation:** Maintain thorough records of all decisions and approvals related to the procurement process.
>
> 📘 Source: [Source 1: GFRupdatedupto31012026.pdf]

### Q66. What is the procedure for evaluation of consulting service proposals?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 42.06s  |  **Sources:** 2  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, GFRupdatedupto31012026.pdf  
- **Answer entities:** Rules: Rule 190  

> **Response:**
> 💡 Answer
> The evaluation of consultancy service proposals follows a structured process as outlined in Rule 190 and 191 of the General Financial Rules. Initially, only bidders who have been declared technically qualified by the Consultancy Evaluation Committee (CEC) are considered for financial bid analysis. The CEC evaluates technical proposals based on criteria announced in the Request for Proposal (RFP), and responsive bids achieving a minimum qualifying score proceed to the next stage. Subsequently, the financial proposals of these technically qualified bidders are scored using predefined relative weights assigned to both quality and cost, depending on the specific circumstances of the assignment. A final combined score is then calculated, determining the successful bidder for placement of the consultancy contract.
>
> 📋 Process
> 1. Technical Qualification: The CEC evaluates technical proposals based on RFP criteria, declaring bidders technically qualified.
> 2. Quality Scoring: Responsive bids achieving a minimum qualifying score are assessed and scored according to the pre-defined criteria in the RFP.
> 3. Financial Proposal Scoring: Financial proposals of technically qualified bidders are evaluated using predefined relative weights for quality and cost.
> 4. Combined Score Calculation: A final combined score is calculated based on the weighted scores from steps 2 and 3, selecting the L1 bidder.
>
> 📘 Source: FInal_GFR_upto_31_07_2024.pdf

### Q67. What are the guidelines for splitting tender quantities?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 38.76s  |  **Sources:** 2  
- **Cited:** mannual procurement.pdf, publicProManual-1755343081262-715558279.pdf  

> **Response:**
> 💡 Answer
> When a tender quantity is split, several guidelines apply to ensure fairness and transparency. The primary approach involves distributing the remaining quantities among other bidders based on objective data like eligibility criteria, delivery requirements, and unit loads. Specifically, if no prior declaration exists in the bid documents regarding quantity splitting, the Procuring Entity can distribute the remaining quantities fairly using objective data. Parallel contracts with defined ratios (70:30 or 50:30:20) may also be utilized, though these are approximate and subject to adjustment based on bidder capacity and past performance. It’s crucial that the tender documents clearly define the criteria for splitting the contract quantity.
>
> 📋 Process
> 1. If a quantity split is deemed necessary, the Procuring Entity distributes remaining quantities among other bidders using objective data (eligibility, delivery, unit loads).
> 2. Parallel contracts can be established with defined ratios (70:30 or 50:30:20), subject to adjustment based on bidder capacity and performance.
> 3. The tender documents must clearly outline the criteria for quantity splitting.
>
> 📘 Source: mannual procurement.pdf

### Q68. When can a short-term tender with less than 21 days notice be issued?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 31.77s  |  **Sources:** 4  
- **Cited:** Store_Purhase_Rules_28.01.2021.pdf, GFRupdatedupto31012026.pdf, mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf  
- **Answer entities:** Thresholds: Rs. 50 lakhs  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> A short-term tender (limited tender enquiry) can be issued when the estimated value of the goods to be procured is up to [Rs. 50 lakhs (Rupees Fifty Lakhs)].
>
> 📋 Process
> 1. The Department Admin initiates the limited tender enquiry.
> 2. Copies of the bidding document are sent directly by speed post/registered post/courier/e-mail to firms on the list of registered suppliers.
> 3. More than three supplier firms should be identified to obtain more responsive bids.
>
> 📘 Source: GFRupdatedupto31012026.pdf

### Q69. What are the CVC guidelines on post-tender negotiations?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 47.29s  |  **Sources:** 3  
- **Cited:** Compilation of CVC Circulars and Guidelines.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf  

> **Response:**
> 💡 Answer
> The Central Vigilance Commission (CVC) has issued several directives regarding post-tender negotiations, primarily aiming to prevent undue influence and maintain transparency. Specifically, CVC instruction No.8(1)(h)/98(1) dated 18/11/98 bans post-tender negotiations except with the lowest bidder (L1). However, clarifications have been provided to address concerns regarding World Bank projects and other international funding agencies, stating that the Commission’s instructions do not apply specifically to these projects, meaning departments must adhere to the criteria set by those agencies. Furthermore, CVC guidelines discourage using public sector enterprises as a shield for improper purchases and recommend distributing quantities among bidders fairly when L1 cannot fulfill the entire order. Negotiations should be conducted solely by the CA or TC, with extended validity periods for original offers if negotiations extend beyond the initial period.
>
> 📋 Process
> 1. CVC Instruction No. 8(1)(h)/98(1) prohibits post-tender negotiations except with L1.
> 2. For World Bank projects and similar international funding agencies, adherence to the criteria of the respective agency is required; CVC instructions do not apply directly.
> 3. Departments should avoid using public sector enterprises as a means to obtain costlier inputs or engage in improper purchases.
> 4. Quantities should be distributed among bidders fairly when L1 cannot fulfill the entire order.
> 5. Negotiations must be conducted solely by the CA or TC.
> 6. The validity of the original offer must be extended if negotiations extend beyond its initial period.
> 7. Revised bids should be obtained in writing from the selected tenderers at the end of the negotiations.
>
> 📘 Source: Compilation of CVC Circulars and Guidelines (Source 1)

### Q70. What is the transparency policy for publication of tender awards on the portal?

- **Role/Lang:** Officer · English  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 33.75s  |  **Sources:** 4  
- **Cited:** Manual_for_Procurement_of_works_2019.pdf, publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf, FInal_GFR_upto_31_07_2024.pdf  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> The transparency policy regarding publication of tender awards involves several key steps. Following technical evaluation, the list of successful bidders will be published on the portal, as required by the Tender document. Confidential information contained within the tender file will not be shared with anyone not officially involved in the decision-making process until the contract award is notified to the successful firm. This ensures a publicly accessible record of the procurement outcome.
>
> 📋 Process
> 1. Technical evaluation completed.
> 2. List of successful bidders identified.
> 3. Publication of bidder list on the e-Procurement Portal.
> 4. Confidential information remains restricted until official notification.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf

## — Officer · Hindi —

### Q71. जीएफआर (GFR) के तहत बिना कोटेशन के सीधे खरीद की सीमा क्या है?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `RULES_GFR` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 32.55s  |  **Sources:** 4  
- **Cited:** publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf, GFR2017_HINDI.pdf, GFRupdatedupto31012026.pdf  

> **Response:**
> 💡 उत्तर
> GFR के तहत बिना कोटेशन के सीधे खरीद की सीमा 25,000/- (पच्चीस हजार रुपये) तक है। यह सीमा प्रत्येक अवसर पर केवल माल की खरीद के लिए लागू होती है।
>
> 📋 प्रक्रिया
> 1. सक्षम प्राधिकारी द्वारा रिकॉर्ड किए जाने वाले प्रमाण पत्र के आधार पर दर उद्धरण या बोलियां आमंत्रित किए बगैर, इस सीमा तक के मूल्य के माल की खरीद की जा सकती है।
> 2. यह प्रावधान नियम 154 में उल्लिखित है।
>
> 📘 स्रोत: GFR2017_HINDI.pdf

### Q72. स्थानीय क्रय समिति (Local Purchase Committee) के गठन के क्या नियम हैं?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `RULES_GFR` (conf 0.8) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 41.73s  |  **Sources:** 4  
- **Cited:** GFR2017_HINDI.pdf, store purchase rule cg.pdf, GFRupdatedupto31012026.pdf, Store_Purhase_Rules_28.01.2021.pdf  

> **Response:**
> 💡 उत्तर
> स्थानीय क्रय समिति (Local Purchase Committee) के गठन के नियम निम्नलिखित हैं:
>
> * समिति में तीन सदस्य हों जो उपयुक्त स्तर के हों, जैसा कि विभाग प्रमुख द्वारा तय किया गया है।
> * समिति में विभाग में पदस्थ लेखा अधिकारी/लेखा प्रभारी को अनिवार्य रूप से शामिल किया जाए।
> * समिति में ऐसे अधिकारियों को अवश्य शामिल किया जाए जिनके पास क्रय की जाने वाली वस्तु का तकनीकी ज्ञान हो।
> * समिति मूल्य और वस्तु की गुणवत्ता का परीक्षण करेगी और अपनी अनुशंसा देगी।
>
> 📋 प्रक्रिया
> 1. प्रत्येक कार्यालय में जहां प्रतिवर्ष रु. 50,000/- या इससे अधिक का क्रय किया जाता है, एक क्रय समिति बनाई जाएगी।
> 2. क्रय समिति में विभाग में पदस्थ लेखा अधिकारी/लेखा प्रभारी को सदस्य के रूप में अनिवार्यतः सम्मिलित हो।
> 3. समिति में कितने सदस्य हों, यह निर्णय सक्षम अधिकारी अपने विवेक से ले सकते हैं, लेकिन तकनीकी ज्ञान रखने वाले अधिकारियों को अवश्य शामिल करना चाहिए।
> 4. क्रय समिति मूल्य और वस्तु की गुणवत्ता का परीक्षण करेगी और अपनी अनुशंसा देगी।
>
> 📘 स्रोत: GFR2017_HINDI.pdf

### Q73. सीमित निविदा जांच (Limited Tender Enquiry) का उपयोग किन परिस्थितियों में किया जा सकता है?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `RULES_GFR` (conf 0.6) ✅  |  **Outcome:** CACHE  |  **Latency:** 2.07s  |  **Sources:** 3  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, GFRupdatedupto31012026.pdf, Vigilance Manual 2021 (Hindi).pdf  
- **Answer entities:** Rules: Rule 150  

> **Response:**
> 💡 उत्तर
> सीमित निविदा जांच (Limited Tender Enquiry) का उपयोग निम्नलिखित परिस्थितियों में किया जा सकता है:
>
> 1. अनुमानित मूल्य [रूpeesFifty Lakhs]³⁰ तक की वस्तुओं की खरीद के मामले में।
> 2. आपातकालीन स्थितियों में।
> 3. मौजूदा उपकरण सेटों के सुसंगत बनाने हेतु मशीनरी या अतिरिक्त पुर्जों की खरीद के मामले में।
> 4. आवषयक मदों की खरीद किसी चयनित फर्म से ही की जानी चाहिए तथा कई चरणों की निविदा प्रक्रिया के बाद भी कोई अनुक्रिया न मिलने पर एकल निविदा से यथासंभव बचा जाना चाहिए।
>
> 📋 प्रक्रिया
> 1. अनुमानित मूल्य [Rupees Fifty Lakhs]³⁰ तक की वस्तुओं की खरीद के लिए यह विधि अपनाई जा सकती है।
> 2. बidding document के copies को स्पीड पोस्ट/registered post/courier/ e-mail द्वारा उन फर्मों को भेजे जाने चाहिए जो Rule 150 के तहत पंजीकृत हैं।
> 3. सीमित निविदा जांच में फर्मों की संख्या तीन से अधिक होनी चाहिए।
> 4. अधिकतम प्रतिस्पर्धी बोली प्राप्त करने के लिए अधिक अनुमोदित आपूर्तिकर्ताओं की पहचान करने का प्रयास किया जाना चाहिए।
> 5. संगठन को GeM और GeM- Central

### Q74. सीमित निविदा के लिए न्यूनतम कितने आपूर्तिकर्ताओं की आवश्यकता होती है?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 38.49s  |  **Sources:** 3  
- **Cited:** GFR2017_HINDI.pdf, store purchase rule cg.pdf, mannual procurement.pdf  

> **Response:**
> 💡 उत्तर
> सीमित निविदा पूछ-ताछ जारी किए जाने के लिए न्यूनतम तीन अनुमोदित संविदाकारों की आवश्यकता होती है। यदि कम से कम तीन अनुमोदित आपूर्तिकर्ताओं/ठेकेदारों उपलब्ध नहीं होते हैं, तो सक्षम प्राधिकारी (CA) की मंजूरी के साथ उपलब्ध आपूर्तिकर्ताओं/ठेकेदारों को भेजा जा सकता है, और इस बारे में कारणों का भी रिकॉर्ड रखा जाना चाहिए। इस मामले में, बोलीदाता को अधिक स्रोतों के विकास के लिए चिह्नित किया जाएगा।
>
> 📋 प्रक्रिया
> 1. सीमित निविदा पूछ-ताछ जारी करे।
> 2. तीन से अधिक अनुमोदित संविदाकारों की आवश्यकता होती है।
> 3. यदि कम से कम तीन अनुमोदित आपूर्तिकर्ताओं/ठेकेदारों उपलब्ध नहीं होते हैं, तो CA की मंजूरी के साथ उपलब्ध आपूर्तिकर्ताओं/ठेकेदारों को भेजा जा सकता है।
> 4. बोलीदाता को अधिक स्रोतों के विकास के लिए चिह्नित किया जाएगा।
>
> 📘 स्रोत: mannual procurement.pdf

### Q75. किस राशि से अधिक की खरीद के लिए विज्ञापन निविदा (Open Tender) अनिवार्य है?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 37.32s  |  **Sources:** 3  
- **Cited:** Store_Purhase_Rules_28.01.2021.pdf, store purchase rule cg.pdf, Manual_for_Procurement_of_works_2019.pdf  

> **Response:**
> 💡 उत्तर
> 50 लाख रुपये से अधिक की खरीद के लिए विज्ञापन और निविदा (Open Tender) अनिवार्य है।
>
> 📋 प्रक्रिया
> 1. 300 लाख रुपये से अधिक की खरीद के लिए स्थानीय स्तर के एक समाचार पत्र में विज्ञापन दिया जाना चाहिए।
> 2. 200 लाख रुपये से अधिक तथा 10 लाख रुपये तक की खरीद के लिए प्रदेश स्तरीय दो समाचार पत्रों में विज्ञापन दिया जाना चाहिए।
> 3. 10 लाख रुपये से अधिक तथा 20 लाख रुपये तक की खरीद के लिए प्रदेश स्तरीय दो समाचार पत्रों में और राष्ट्रीय स्तर के एक समाचार पत्र में विज्ञापन दिया जाना चाहिए।
> 4. 20 लाख रुपये से अधिक की खरीद के लिए प्रदेश स्तरीय दो समाचार पत्रों में और राष्ट्रीय स्तर के दो समाचार पत्रों में विज्ञापन दिया जाना चाहिए।
>
> 📘 स्रोत: Store_Purhase_Rules_28.01.2021.pdf

### Q76. दो-बोली प्रणाली (Two-Bid System) क्या है और इसे कब लागू किया जाना चाहिए?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 39.51s  |  **Sources:** 4  
- **Cited:** publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf, GFR2017_HINDI.pdf, Manual_for_Procurement_of_works_2019.pdf  

> **Response:**
> 💡 उत्तर
> दो-बोली प्रणाली (Two-Bid System) एक ऐसी प्रक्रिया है जिसमें बोलीदाताओं से दो अलग-अलग भागों में बोलियां जमा करने की अपेक्षा की जाती है। पहला भाग तकनीकी और वाणिज्यिक पहलुओं का होता है, जिसमें तकनीकी योग्यता, प्रदर्शन क्षमता और वित्तीय शर्तें शामिल होती हैं। दूसरा भाग केवल वित्तीय प्रस्ताव होता है।
>
> 📋 प्रक्रिया
> 1. बोलीदाताओं से दो अलग-अलग envelopes में बोलियां जमा करने के लिए कहा जाता है।
> 2. पहले envelope (techno-commercial bid) में तकनीकी विनिर्देशों, गुणवत्ता मानकों और वाणिज्यिक शर्तों का मूल्यांकन किया जाता है।
> 3. दूसरे envelope (financial bid) में वित्तीय प्रस्ताव प्रस्तुत किया जाता है।
> 4. दोनों envelopes को एक सीलबंद envelope में जमा किया जाता है।
> 5. तकनीकी बोलियों को निर्धारित तिथि और समय पर खोला जाता है और तकनीकी समिति (TC) द्वारा मूल्यांकन किया जाता है।
>
> 📘 स्रोत: FInal_GFR_upto_31_07_2024.pdf, Manual_for_Procurement_of_works_2019.pdf

### Q77. जीएफआर नियम 165 के तहत देर से प्राप्त बोलियों के संबंध में क्या निर्देश हैं?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `RULES_GFR` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 49.65s  |  **Sources:** 3  
- **Cited:** GFR2017_HINDI.pdf, GFRupdatedupto31012026.pdf, FInal_GFR_upto_31_07_2024.pdf  

> **Response:**
> 💡 उत्तर
> जीएफआर नियम 165 के तहत देर से प्राप्त बोलियों के संबंध में निम्नलिखित निर्देश हैं:
>
> (प) इस पद्धति को तब अपनाया जा सकता है जब प्रापण किए जाने वाले माल का अनुमानित मूल्य पच्चीस लाख #पए तक हो। बोली दस्तावेजों की प्रतियां उन फमो± को सीधो ही स्पीड पोस्ट/पंजी—त डाक/ कुरियर/ई-मेल से भेजी जाएं जिन्हें उपयुर्ä नियम 150 के तहत किए गए उल्लेख के अनु:प प्र’नगत माल के लिए पंजी—त आपूÆतकतार्ओं की सूची में शामिल किया गया हो। सीमित निविदा पूछ-ताछ में आपूÆतकतार् फमो± की संखया तीन से अधिक होनी चाहिए। प्रतिस्पधार्त्मक आधार पर अधिक प्रतिक्रिया’ाील बोलियां प्राप्त करने के लिए अधिक संखया में अनुमोदित आपूÆतकतार्ओं की पहचान करने के प्रयास किए जाएं। इसके अतिरिä] नियम 159 के अनुसार] संगठन को अपनी सीमित निविदा पूछ-ताछ केन्द्वीय लोक प्रापण पोर्टल पर प्रकाि’ात करनी होगी। केन्द्वीय लोक प्रापण पोर्टल के अलावा संगठनों को निविदा पूछ-ताछ विभाग या मंत्रालय की वेबसाइट पर प्रकाि’ात करनी होगी। (पप) अयाचित बोलियों को स्वीकार न किया जाए। तथापि] मंत्रालयों/विभागों को ऐसी प्रणाली विकसित करनी होगी कि इच्छुक फमे± निविदा मंगाए जाने के अगले दौर में पंजीकरण करा सकें और बोली लगा सकें। (पपप) जहां प्रापण का अनुमानित मूल्य पच्चीस लाख #पए से अधिक हो वहां भी निम्नलिखित परिस्थितियों में सीमित निविदा पूछ-ताछ के माधयम से खरीद की जा सकती हैः- (क) मंत्रालय या विभाग का सक्षम प्राधिकारी प्रमाणित करता

### Q78. किस परिस्थिति में एकल निविदा (Single Tender) खरीद को उचित माना जाता है?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 36.17s  |  **Sources:** 3  
- **Cited:** mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf, store purchase rule cg.pdf  

> **Response:**
> 💡 उत्तर
> एकल निविदा (Single Tender) खरीद को उचित मानने की परिस्थिति निम्नलिखित है:
>
> 1. खरीद प्रक्रिया में आवश्यक आवश्यकताओं और औपचारिकताओं का पूर्ण होना - जैसे मानक शर्तें, उद्योग-अनुकूल विनिर्देशन, व्यापक प्रचार, पर्याप्त बोली लगाने का समय आदि। यदि ये आवश्यकताएं पूरी नहीं हुई हैं, तो एक नई निविदा जारी की जानी चाहिए।
> 2. बोली की कीमत उचित होनी चाहिए, बाजार मूल्यों के सापेक्ष।
> 3. यदि कीमत उचित नहीं है, तो बातचीत (L1) या पुन: निविदा पर विचार किया जा सकता है।
>
> 📋 प्रक्रिया
> 1. आवश्यक आवश्यकताओं और औपचारिकताओं का पूर्ण होना।
> 2. बोली की कीमत उचित होनी चाहिए।
> 3. यदि कीमत उचित नहीं है, तो बातचीत (L1) या पुन: निविदा पर विचार किया जा सकता है।
>
> 📘 स्रोत: mannual procurement.pdf

### Q79. सरकारी अनुबंधों में ईएमडी (EMD) दर के लिए जीएफआर नियम क्या हैं?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `RULES_GFR` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 37.27s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf, GFR2017_HINDI.pdf  
- **Answer entities:** Thresholds: 2%, 5%  

> **Response:**
> 💡 उत्तर
> I'm not fully certain this matches your question - please verify with the cited document.
> सरकारी अनुबंधों में EMD (Earnest Money Deposit) दर के लिए जीएफआर (GFR) नियम निम्नलिखित हैं:
>
> आमतौर पर, EMD की राशि खरीदी जा रही वस्तुओं के मूल्य का दो (2) से पाँच (5) प्रतिशत के बीच होनी चाहिए। यह राशि खरीद इकाई द्वारा निर्धारित की जाती है और निकटतम हजारों रुपये में पूर्णांकित की जाती है। 
>
> 📋 प्रक्रिया
> 1. जीएफआर नियम के अनुसार, EMD की राशि आमतौर पर खरीदी जा रही वस्तुओं के मूल्य का 2% से 5% के बीच होती है।
> 2. खरीद इकाई द्वारा निर्धारित की गई यह राशि निकटतम हजारों रुपये में पूर्णांकित की जाती है।
> 3. EMD को अकाउंट पे योजना डिमांड ड्राफ्ट, फिक्स्ड डिपॉजिट रिसीट, बैंक चेक या बैंक गारंटी (जिसमें ई-बैंक गारंटी भी शामिल है) के रूप में दिया जा सकता है।
>
> 📘 स्रोत: GFR2017_HINDI.pdf

### Q80. अनुबंध के लिए आवश्यक प्रदर्शन प्रतिभूति (Performance Security) की सीमा कितनी है?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 33.59s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf  
- **Answer entities:** Thresholds: 5%, 10%  

> **Response:**
> 💡 उत्तर
> अनुबंध के लिए आवश्यक प्रदर्शन प्रतिभूति (Performance Security) की सीमा पांच से दस प्रतिशत (5%–10%) अनुबंध मूल्य तक है। 
>
> 📋 प्रक्रिया
> 1. यह प्रदर्शन प्रतिभूति निर्माण कार्यों के लिए पाँच प्रतिशत और वस्तुओं के लिए दस प्रतिशत होगी।
> 2. प्रदर्शन प्रतिभूति का भुगतान बीमा Surety Bond, Account Payee Demand Draft, किसी वाणिज्यिक बैंक द्वारा जारी किया गया Bank Guarantee या ऑनलाइन भुगतान के रूप में किया जा सकता है।
> 3. यदि JV है, तो प्रदर्शन प्रतिभूति के लिए BG सभी भागीदारों द्वारा उनकी परियोजना में भागीदारी के अनुपात में प्रदान की जाएगी।
>
> 📘 स्रोत: Manual_for_Procurement_of_works_2019.pdf

### Q81. जीएफआर के तहत प्रदर्शन सुरक्षा के कौन-कौन से रूप स्वीकार्य हैं?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 39.71s  |  **Sources:** 3  
- **Cited:** GFRupdatedupto31012026.pdf, FInal_GFR_upto_31_07_2024.pdf, publicProManual-1755343081262-715558279.pdf  
- **Answer entities:** Thresholds: 3%, 10%  

> **Response:**
> 💡 उत्तर
> जीएफआर के तहत प्रदर्शन सुरक्षा के निम्नलिखित रूप स्वीकार्य हैं: [Insurance Surety Bond], खाते से भुगतान का ड्राफ्ट, एक वाणिज्यिक बैंक से जमा राशि की गारंटी (जिसमें ई-बैंक गारंटी भी शामिल है) किसी वाणिज्यिक बैंक से, या एक स्वीकार्य रूप में ऑनलाइन भुगतान जो खरीदार के हित को सभी पहलुओं में सुरक्षित रखता है।
>
> 📋 प्रक्रिया
> 1. प्रदर्शन सुरक्षा [Insurance Surety Bond], खाते से भुगतान का ड्राफ्ट, एक वाणिज्यिक बैंक से जमा राशि की गारंटी (जिसमें ई-बैंक गारंटी भी शामिल है) किसी वाणिज्यिक बैंक से, या एक स्वीकार्य रूप में ऑनलाइन भुगतान जो खरीदार के हित को सभी पहलुओं में सुरक्षित रखता है। के रूप में दी जा सकती है।
> 2. प्रदर्शन सुरक्षा की राशि अनुबंध मूल्य का 3% से 10% होगी (कार्य अनुबंधों के लिए)।
> 3. खरीद इकाई प्रदर्शन सुरक्षा की ऊपरी सीमा निर्धारित कर सकती है, सक्षम प्राधिकारी और वित्त सहमति के साथ, प्रतिस्पर्धा की आवश्यकता और प्रदर्शन जोखिम के अपने दृष्टिकोण के आधार पर।
>
> 📘 स्रोत: FInal_GFR_upto_31_07_2024.pdf

### Q82. किन स्थितियों में प्रदर्शन सुरक्षा जमा करने से छूट दी जा सकती है?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 35.56s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf, FInal_GFR_upto_31_07_2024.pdf  

> **Response:**
> 💡 उत्तर
> प्रदर्शन सुरक्षा जमा करने से छूट निम्नलिखित स्थितियों में दी जा सकती है:
>
> * 103Govt. मंत्रालयों, विभागों, संलग्न और अधीनस्थ कार्यालयों, स्वायत्त निकायों को।
> * OEM (Original Equipment Manufacturer) जिनके मामले में PAC (Procurement Approval Committee) के तहत निविदाएं जारी की गई हैं।
>
> 📋 प्रक्रिया
> 1. विभाग प्रमुख द्वारा विशिष्ट अनुरोध या अन्यथा छूट का अनुरोध किया जा सकता है।
> 2. OEM के मामले में, PAC के तहत जारी निविदाओं के लिए OEM को छूट दी जाएगी।
>
> 📘 स्रोत: publicProManual-1755343081262-715558279.pdf

### Q83. सूक्ष्म और लघु उद्यमों (MSEs) से खरीद के संबंध में सरकार की क्या नीति है?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 55.09s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, store purchase rule cg.pdf, FInal_GFR_upto_31_07_2024.pdf  
- **Answer entities:** Thresholds: 25%  

> **Response:**
> 💡 उत्तर
> सूक्ष्म और लघु उद्यमों (MSEs) से खरीद के संबंध में सरकार की नीति निम्नलिखित है:
>
> 1. **नीति का उद्देश्य:** सरकार का उद्देश्य राष्ट्रीय आर्थिक विकास को बढ़ावा देना है, जिसमें सूक्ष्म, लघु और मध्यम उद्यमों तथा कमजोर वर्गों को सहायता प्रदान करना शामिल है। 2012 [संशोधित 2018 और 2021] की सूक्ष्म और लघु उद्यम विकास (MSMED) अधिनियम, 2006 के तहत सरकार द्वारा जारी की गई खरीद नीति का पालन करना अनिवार्य है।
>
> 2. **पात्रता:**
>  * उद्यम पंजीकरण के तहत पंजीकृत MSEs इस नीति के लाभों के लिए पात्र हैं।
>  * यह नीति MSEs से वस्तुओं और सेवाओं की प्राथमिकता खरीद प्रदान करती है।
>  * व्यापारी/वितरक/अकेले एजेंट/कार्य अनुबंध विक्रेता इस नीति के दायरे से बाहर हैं।
>
> 3. **निवेश में परिवर्तन:** यदि किसी MSE के निवेश (प्लांट और मशीनरी, उपकरण या दोनों) में वृद्धि होती है जिसके परिणामस्वरूप वर्गीकरण में बदलाव होता है, तो उसे तीन वर्षों की अवधि के लिए अपने पूर्व वर्गीकरण (सूक्ष्म, लघु या मध्यम) में प्राप्त सभी गैर-कर लाभों का लाभ मिलता रहेगा।
>
> 4. **विक्रेता विकास:** MSME मंत्रालय या विभाग या सार्वजनिक क्षेत्र की उपक्रमों को GeM पोर्टल के माध्यम से MSEs के लिए खरीद करने के लिए उपयुक्त विक्रेता विकसित करने के लिए आवश्यक कदम उठाएंगे। SC/ST/महिलाओं द्वारा स्वामित्व वाले MSEs के लिए MSME मंत्रालय विशेष विक्रेता विकास कार्यक्रम/खरीद-विक्रेता मिलन आयोजित करेगा।
>
> 5. **25% लक्ष्य:** केंद्रीय मंत्रालयों/विभागों/CPSEs को 358 वस्तुओं की सूची पर लगातार समीक्षा करनी होगी, जो exclusivly MSEs से खरीद के लिए आरक्षित हैं, और SC/ST/महिलाओं के MSEs के लिए विशेष विक्रेता विकास कार्यक्रमों/खरीद-विक्रेता मिलन आयोजित करने चाहिए।
>
> 📋 प्रक्रिया
> 1. नीति का पालन करना अनिवार्य है।
> 2. MSEs को GeM पोर्टल पर पंजीकृत होना चाहिए।
> 3. निवेश में वृद्धि होने पर, नीति के अनुसार लाभों का दावा किया जा सकता है।
> 4. MSME मंत्रालय द्वारा

### Q84. मूल्यांकन के दौरान एमएसई (MSEs) को मूल्य प्राथमिकता (Price Preference) कैसे दी जाती है?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 45.11s  |  **Sources:** 1  
- **Cited:** publicProManual-1755343081262-715558279.pdf  
- **Answer entities:** Thresholds: 15%, 25%, 50%  

> **Response:**
> 💡 उत्तर
> मूल्यांकन के दौरान एमएसई (MSEs) को मूल्य प्राथमिकता देने की प्रक्रिया इस प्रकार है:
>
> सबसे पहले, L1 बिडर एमएसई नहीं होने पर, एमएसई बिडरों को उनकी दरें L1+15% मार्जिन के भीतर होने पर वरीयता दी जाती है। यदि निविदाकर्ता (Procuring Entity) L1 बिडर के साथ बातचीत करता है, तो मूल्य प्राथमिकता मार्जिन (L1+15%) को मूल L1 मूल्य पर, रियायती मूल्य पर नहीं, गणना की जानी चाहिए। ऐसे योग्य एमएसई (MSEs) को L1 मूल्य से मेल खाने के लिए आमंत्रित किया जाना चाहिए।
>
> यदि कोई एमएसई (MSE) L1 मूल्य से मेल खाने के लिए सहमत नहीं होता है, तो 25% या 50% (वस्तुओं के प्रकार पर निर्भर करता है) की मात्रा को उन एमएसई (MSEs) को आवंटित किया जाता है जिनकी दरें L1+15% मार्जिन के भीतर हैं। यदि कोई भी एमएसई (MSE) इस मूल्य से मेल खाने के लिए सहमत नहीं होता है, तो खरीद वरीयता (Purchase Preference) प्रदान नहीं की जाती है और शेष मात्रा L1 बिडर को दी जाती है।
>
> उदाहरण के लिए, 100 कंप्यूटरों की खरीद में, यदि L1 बिडर एमएसई नहीं है, तो MSME बिडरों को उनकी दरों के आधार पर 15% मार्जिन के भीतर होने पर वरीयता दी जाएगी।
>
> 📋 प्रक्रिया

### Q85. जीएफआर के तहत परामर्श सेवाओं (Consulting Services) की खरीद के क्या चरण हैं?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 43.82s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf, GFRupdatedupto31012026.pdf  

> **Response:**
> 💡 उत्तर
> I'm not fully certain this matches your question - please verify with the cited document.
> जीएफआर (GFR) के तहत परामर्श सेवाओं (Consulting Services) की खरीद के चरण निम्नलिखित हैं:
>
> 1. **प्रारंभिक निर्णय:** विभाग सचिव (Secretary) द्वारा विशेष प्रक्रिया (Special Procedure) का निर्धारण किया जा सकता है, जिसमें वित्तीय सलाहकार (Financial Adviser)/ एकीकृत वित्त विभाग (IFD) की भूमिका को परिभाषित किया जाता है। इसमें सीमाएं, खरीद के प्रकार (जैसे परामर्श, माल और कार्य अनुबंध), और अन्य पैरामीटर शामिल हो सकते हैं।
> 2. **अनुमोदन:** वित्तीय सलाहकार/ एकीकृत वित्त विभाग (Financial Adviser/ IFD) द्वारा सभी खरीद मामलों पर सहमति प्राप्त की जाती है, सिवाय उन मामलों में जहां सचिव द्वारा विशेष प्रक्रिया स्वीकृत की गई है।
> 3. **भुगतान:** स्वीकृत अनुबंधों के तहत भुगतान के लिए वित्तीय सलाहकार/ एकीकृत वित्त विभाग (Financial Adviser/ IFD) की परामर्श की आवश्यकता नहीं होती है, सिवाय उन मामलों में जहां भुगतान स्वीकृत अनुबंध की शर्तों में छूट या बदलाव के रूप में किए जाते हैं।
>
> 📋 प्रक्रिया
> 1. विभाग सचिव (Secretary) द्वारा विशेष प्रक्रिया का निर्धारण।
> 2. वित्तीय सलाहकार (Financial Adviser)/ एकीकृत वित्त विभाग (IFD) से सहमति प्राप्त करना।
> 3. भुगतान के लिए वित्तीय सलाहकार (Financial Adviser)/ एकीकृत वित्त विभाग (IFD) की परामर्श की आवश्यकता नहीं (केवल छूट/ बदलाव मामलों में)।
>
> 📘 स्रोत: FInal_GFR_upto_31_07_2024.pdf

### Q86. परामर्श सेवा प्रस्तावों के मूल्यांकन की क्या प्रक्रिया है?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 46.31s  |  **Sources:** 3  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, GFRupdatedupto31012026.pdf, GFR2017_HINDI.pdf  

> **Response:**
> 💡 उत्तर
> परामर्श सेवा प्रस्तावों के मूल्यांकन की प्रक्रिया निम्नलिखित है:
>
> 1. मंत्रालय या विभाग द्वारा गठित पराम्णाीर् कार्य मूल्यांकन समिति (CEC) तकनीकी प्रस्तावों का मूल्यांकन करती है।
> 2. CEC तकनीकी रूप से योग्य बोलीदाताओं के वित्तीय बोलियों को खोलता है, जो नियम 189 के अनुसार तकनीकी रूप से योग्य घोषित किए गए हैं।
> 3. वित्तीय बोलियों का मूल्यांकन गुणवत्ता और लागत आधारित चयन (QCBS) विधि के अनुसार किया जाता है। इस प्रक्रिया में, तकनीकी प्रस्तावों की गुणवत्ता के लिए न्यूनतम निर्धारित स्कोर प्राप्त करने वाले प्रस्तावों पर विचार किया जाता है।
> 4. गुणवत्ता और वित्तीय प्रस्तावों को एक साथ मिलाकर अंतिम स्कोर निर्धारित किया जाता है, जिसमें गुणवत्ता और लागत दोनों का अनुपात पूर्व-निर्धारित होता है (जैसे 70:30, 60:40, 50:50)।
> 5. सबसे अधिक संयुक्त स्कोर प्राप्त करने वाले बोलीदाता को पराम्णाीर् कार्य संविदा प्रदान करने के लिए चुना जाता है।
>
> 📋 प्रक्रिया
> 1. CEC तकनीकी प्रस्तावों का मूल्यांकन करता है।
> 2. CEC तकनीकी रूप से योग्य बोलीदाताओं की वित्तीय बोलियों को खोलता है।
> 3. QCBS विधि के अनुसार वित्तीय बोलियों का मूल्यांकन किया जाता है।
> 4. गुणवत्ता और लागत के आधार पर संयुक्त स्कोर निर्धारित किया जाता है।
> 5. उच्चतम संयुक्त स्कोर वाले बोलीदाता को चुना जाता है।
>
> 📘 स्रोत: FInal_GFR_upto_31_07_2024.pdf

### Q87. निविदा मात्राओं को विभाजित (Splitting Tender Quantities) करने के क्या दिशानिर्देश हैं?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 39.37s  |  **Sources:** 4  
- **Cited:** GFR2017_HINDI.pdf, publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf, store purchase rule cg.pdf  

> **Response:**
> 💡 उत्तर
> निविदा मात्राओं को विभाजित करने से संबंधित दिशानिर्देश निम्नलिखित हैं:
>
> मंत्रालय या विभाग कुल मांग के अनुमानित मूल्य के संदर्भ में उच्चतर प्राधिकारी की मंजूरी प्राप्त करने की अनिवार्यता से बचने के उद्देश्य से छोटे-छोटे हिस्सों में खरीद करने के लिए माल की किसी मांग को थोड़ी-थोड़ी मात्राओं में विभाजित नहीं करना चाहिए। (नियम 157)
>
> इसके अतिरिक्त, यदि समानांतर अनुबंधों का अनुमान है, तो मात्राओं को विभाजित करने के मानदंडों को निविदा दस्तावेजों में पहले से ही स्पष्ट रूप से निर्दिष्ट किया जाना चाहिए।
>
> 📋 प्रक्रिया
> 1. कुल मांग के अनुमानित मूल्य के संदर्भ में उच्चतर प्राधिकारी की मंजूरी प्राप्त करने की अनिवार्यता से बचने के उद्देश्य से छोटे-छोटे हिस्सों में खरीद करने के लिए माल की किसी मांग को थोड़ी-थोड़ी मात्राओं में विभाजित न किया जाए।
> 2. यदि समानांतर अनुबंधों का अनुमान है, तो मात्राओं को विभाजित करने के मानदंडों को निविदा दस्तावेजों में पहले से ही स्पष्ट रूप से निर्दिष्ट किया जाना चाहिए।
>
> 📘 स्रोत: FInal_GFR_upto_31_07_2024.pdf

### Q88. 21 दिनों से कम समय की सूचना वाली अल्पकालीन निविदा (Short-Term Tender) कब जारी की जा सकती है?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 39.08s  |  **Sources:** 4  
- **Cited:** Store_Purhase_Rules_28.01.2021.pdf, store purchase rule cg.pdf, GFR2017_HINDI.pdf, GFRupdatedupto31012026.pdf  
- **Answer entities:** Thresholds: 21 दिन  

> **Response:**
> 💡 उत्तर
> अल्पकालीन निविदा (Short-Term Tender) 21 दिनों से कम समय की सूचना वाली खुली निविदा (Open Tender) के मामले में, जब निविदा का अनुमानित मूल्य रू. 50,000 से रू. 10 लाख तक हो, तो इसे 21 दिन की समय-सीमा के साथ जारी किया जा सकता है।
>
> 📋 प्रक्रिया
> 1. निविदा विज्ञप्ति में 21 दिनों की समय-सीमा निर्धारित की जाएगी।
> 2. समय-सीमा की गणना निविदा विज्ञप्ति प्रकाशन की तिथि से की जाएगी।
> 3. निविदा प्राप्ति की पद्धति रजिस्टर्ड पोस्ट (ए.डी.), स्पीड पोस्ट, पी.एंड.टी. विभाग से अधिकृत कोरियर के द्वारा अथवा निर्धारित टेण्डर बाक्स में डाली जाएगी।
> 4. ऑनलाईन निविदा में निर्धारित समय सारणी (शेडयूल) के अनुसार निविदा प्रस्तुत की जावेगी।
>
> 📘 स्रोत: Store_Purhase_Rules_28.01.2021.pdf

### Q89. निविदा के बाद बातचीत (Post-Tender Negotiations) पर सीवीसी के क्या निर्देश हैं?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 49.45s  |  **Sources:** 3  
- **Cited:** Compilation of CVC Circulars and Guidelines.pdf, Vigilance Manual 2021 (Hindi).pdf, mannual procurement.pdf  

> **Response:**
> 💡 उत्तर
> सीवीसी के निर्देशों के अनुसार, निविदा के बाद बातचीत को केवल तकनीकी मूल्यांकनकर्ता (CA) या मुख्य तकनीकी परीक्षक (TC) द्वारा ही किया जाना चाहिए। यह समझा जाना चाहिए कि यदि मूल प्रस्ताव की वैधता अवधि बातचीत के अंत होने से पहले समाप्त हो जाती है, तो मूल प्रस्ताव स्वीकार करने के लिए उपलब्ध नहीं होगा। इसलिए, आवश्यकतानुसार मूल प्रस्ताव की वैधता अवधि को बातचीत से पहले बढ़ाया जाना चाहिए। बोलीदाता को बातचीत के लिए बुलाया जाने पर Annexure 4 के अनुसार संबोधित किया जाना चाहिए ताकि मूल रूप से उद्धृत दरें स्वीकृति के लिए खुली रहें। बातचीत शुरू करने से पहले Annexure 4 के अनुसार हस्ताक्षरित घोषणा प्राप्त की जानी चाहिए, और बातचीत के अंत में Annexure 5 के प्रारूप में चयनित बोलीदाताओं से लिखित में संशोधित प्रस्ताव प्राप्त किए जाने चाहिए। यदि कोई बोलीदाता बातचीत में भाग लेने के बजाय संशोधित प्रस्ताव भेजने का विकल्प चुनता है, तो उस प्रस्ताव पर विचार किया जाएगा। यदि कोई बोलीदाता संशोधित प्रस्ताव जमा नहीं करता है, तो मूल प्रस्ताव पर विचार किया जाएगा।
>
> 📋 प्रक्रिया
> 1. तकनीकी मूल्यांकनकर्ता (CA) या मुख्य तकनीकी परीक्षक (TC) द्वारा बातचीत की जा सकती है।
> 2. मूल प्रस्ताव की वैधता अवधि को बढ़ाया जाना चाहिए यदि यह बातचीत के अंत तक समाप्त होने वाली है।
> 3. Annexure 4 के अनुसार बोलीदाताओं को संबोधित किया जाना चाहिए।
> 4. Annexure 5 के प्रारूप में चयनित बोलीदाताओं से लिखित में संशोधित प्रस्ताव प्राप्त किए जाने चाहिए।
> 5. यदि कोई बोलीदाता संशोधित प्रस्ताव भेजने का विकल्प चुनता है, तो उस प्रस्ताव पर विचार किया जाएगा।
>
> 📘 स्रोत:
> Compilation of CVC Circulars and Guidelines (तारीख 24-02-2014-पीपीसी)

### Q90. पोर्टल पर निविदा पुरस्कारों के प्रकाशन के लिए पारदर्शिता नीति क्या है?

- **Role/Lang:** Officer · Hindi  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 46.58s  |  **Sources:** 3  
- **Cited:** GFR2017_HINDI.pdf, Manual_for_Procurement_of_works_2019.pdf, Store_Purhase_Rules_28.01.2021.pdf  

> **Response:**
> 💡 उत्तर
> I'm not fully certain this matches your question - please verify with the cited document.
> पोर्टल पर निविदा पुरस्कारों के प्रकाशन के लिए पारदर्शिता नीति इस प्रकार है:
>
> 1. **वेबसाइट पर पूर्ण दस्तावेज:** बोली लगाने संबंधी सभी दस्तावेज़, जैसे कि निविदा सूचना (NIT), को संभावित बोलीदाताओं द्वारा वेबसाइट से डाउनलोड किया जा सके, ऐसा सुनिश्चित किया जाना चाहिए।
> 2. **वेबसाइट पर प्रकाि’ात:** संगठन को अपनी वेबसाइट और केन्द्वीय लोक प्रापण पोर्टल पर बोली लगाने संबंधी पूर्ण दस्तावेज प्रकाि’ात करने होंगे ताकि संभावित बोलीदाता वेबसाइट से डाउनलोड करके दस्तावेज़ का उपयोग कर सकें।
> 3. **समय सारणी (शेड्यूल):** निविदाएं आमंत्रित करने के विज्ञापनों में पूरा वेब पता, जहां से बोली लगाने संबंधी दस्तावेज डाउनलोड किए जा सकें, दिया जाए।
> 4. **समाचार पत्रों में विज्ञापन:** NITs को सामान्यतः समाचार पत्रों में प्रकाशित किया जाता है, जिसकी संख्या अनुमानित मूल्य पर निर्भर करती है (जैसे स्थानीय स्तर के एक समाचार पत्र में 1-2 लाख तक, प्रदेश स्तरीय दो समाचार पत्रों में 2-10 लाख तक, और इसी तरह)।
>
> 📋 प्रक्रिया
> 1. NIT का ई-प्रकाशन।
> 2. बोलीदाताओं द्वारा NIT दस्तावेजों को डाउनलोड करना।
> 3. निविदा सूचना में उल्लिखित समय सारणी (शेड्यूल) के अनुसार निविदा प्रस्तुत करना।
> 4. बोली खोलने का समय निविदा प्राप्ति की अंतिम तिथि के निर्धारित समय तक एक घण्टे पष्चात् निर्धारित किया जाना है।
>
> 📘 स्रोत: Manual_for_Procurement_of_works_2019.pdf

## — Officer · Hinglish —

### Q91. GFR ke under directly purchase bina quotation ke kitne amount tak ho sakti hai?

- **Role/Lang:** Officer · Hinglish  
- **Intent:** `RULES_GFR` (conf 0.6) ✅  |  **Outcome:** CACHE  |  **Latency:** 2.03s  |  **Sources:** 3  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, GFR2017_HINDI.pdf, mannual procurement.pdf  
- **Answer entities:** Rules: Rule 192(i) | Thresholds: Rs. 1,00,000, Rs. 10,00,000, 10%, 30%  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> GFR ke under bina quotation ke directly purchase Rs. 1,00,000/- (Rupees one lakh) se lekar Rs. 10,00,000/- (Rupees ten lakh) tak ho sakti hai, jab Scientific Ministries/ Departments/ Organization of Government of India mein Department of Science and Technology, Department of Bio-technology, aur other specified departments hain.
>
> 📋 Process
> 1. Jab estimated value aur proposed contract ke values mein 10% se kam ka difference ho, to quotation bina karne ki zaroorat nahi hai.
> 2. Agar difference 10% se zyada ho, to procurement process ko scratch karna hoga aur QOP (Quality and Price) ya QCBS (Quality Criteria Based on Cost Scoring) basis par phir se shuru karna hoga.
> 3. QCBS ke liye rules Rule 192(i), (ii) aur (iii) mein diye gaye hain, jismein non-financial parameters ka maximum weight 30% tak ho sakta hai.
>
> 📘 Source: FInal_GFR_upto_31_07_2024.pdf

### Q92. Local Purchase Committee banane ka threshold limit kya hai?

- **Role/Lang:** Officer · Hinglish  
- **Intent:** `RULES_GFR` (conf 0.6) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 36.72s  |  **Sources:** 4  
- **Cited:** GFR2017_HINDI.pdf, GFRupdatedupto31012026.pdf, publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf  
- **Answer entities:** Thresholds: ₹25,000, ₹2,50,000  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> Local Purchase Committee banane ka threshold limit ₹25,000/- to ₹2,50,000/- ke antar mein hai. Is committee mein department head ke decision ke hisab se 3 member honge jo appropriate level par constituted honge.
>
> 📋 Process
> 1. ₹25,000/- to ₹2,50,000/- ke antar mein goods ki kharid karne ke liye Local Purchase Committee banane ka threshold limit hai.
> 2. Committee mein department head ke decision se 3 member honge jo appropriate level par constituted honge.
> 3. Committee market survey kar ke rate, quality aur specifications ko ascertain karega.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf

### Q93. Advertised tender kis situation me compulsory ho jata hai?

- **Role/Lang:** Officer · Hinglish  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 39.47s  |  **Sources:** 4  
- **Cited:** publicProManual-1755343081262-715558279.pdf, 160616_AMC_AC short tender.pdf, mannual procurement.pdf, Corrigendum_Instructions_to_department_users_and_bidders.pdf  
- **Answer entities:** Rules: Rule 161)  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> Advertised tender (OTE - Open Tender Enquiry) kis situation me compulsory ho jata hai? Advertised tender, jo ek publicized mode mein hota hai, jismein maximum competition ke liye wide publicity hoti hai. Iska use generally rules under GFR 2017 (Rule 161) ke mutaveed hota hai, jisse OTE, GTE aur rate contracts ke zariye bid submissions ko encourage kiya jata hai. Ismein, department admin by wide publicity, maximum bidders ko participate karne ki opportunity deta hai.
>
> 📋 Process
> 1. Department Admin rules under GFR 2017 (Rule 161) ke mutaveed OTE ke liye tender publish karta hai.
> 2. Tender document publically available hoti hai.
> 3. Bidders wide publicity ke zariye participate karte hain.
> 4. Lowest bid (L1) ke basis selection hota hai.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf

### Q94. Two bid system me technical aur financial bid sath me kaise evaluate hote hain?

- **Role/Lang:** Officer · Hinglish  
- **Intent:** `BID_SUBMISSION` (conf 0.6) ❌  |  **Outcome:** ANSWERED  |  **Latency:** 37.34s  |  **Sources:** 3  
- **Cited:** GFRupdatedupto31012026.pdf, Manual_for_Procurement_of_works_2019.pdf, FInal_GFR_upto_31_07_2024.pdf  

> **Response:**
> 💡 Answer
> Do-stage bidding system mein technical aur financial bid sath me evaluate hote hain isse kuch issi tarah hota hai: Pahla stage technical bids ko evaluating committee ne check karta hai, jismein bidder ki eligibility, technical capabilities aur commercial terms validate hote hain. Iske baad, sirf woh bidders jo technical criteria mein pass hojate hain unke financial bids open karke L1 bidder (lowest evaluated, substantially responsive, technically-suitable bid) ko select kiya jata hai.
>
> 📋 Process
> 1. Technical bids evaluate karne wali committee ne check karte hain.
> 2. Technical criteria par pass hoone wale bidders ke financial bids open karke evaluate karte hain.
> 3. L1 bidder ko select kiya jata hai.
> 4. Untechnical non-compliant bidders ke financial bids return kar diye jaate hain.
>
> 📘 Source: FInal_GFR_upto_31_07_2024.pdf

### Q95. Late bid ko reject karne ke liye GFR rule 165 kya kehta hai?

- **Role/Lang:** Officer · Hinglish  
- **Intent:** `RULES_GFR` (conf 0.8) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 32.78s  |  **Sources:** 3  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, GFRupdatedupto31012026.pdf, GFR2017_HINDI.pdf  
- **Answer entities:** Rules: Rule 165  

> **Response:**
> 💡 Answer
> Late bids (i.e. bids received after the specified date and time for receipt of bids) should not be considered. This is as per Rule 165 of the General Financial Rules (GFR).
>
> 📋 Process
> 1. Rule 165 states that late bids are not to be considered.
> 2. This applies specifically to advertised or limited tender enquiries.
> 3. The bidder can withdraw from procurement with adequate justification without forfeiting bid security.
>
> 📘 Source: General Financial Rules (GFR) [Source 1]

### Q96. Single tender case me CA ki approval kab jaruri hoti hai?

- **Role/Lang:** Officer · Hinglish  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 36.82s  |  **Sources:** 3  
- **Cited:** GFR2017_HINDI.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf  
- **Answer entities:** Thresholds: 25 lakh  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> Single tender case mein, agar kisi bhi procurement ke hasil mein sirf ek hi bid milta hai, to procurement committee (PC) ki approval 25 lakh #pAE se zyada estimated value par jaruri hoti hai. Is approval ka faisla PC ko yeh dekhkar karegi ki enquiry floating karne aur bidding ke liye sufficient time dene mein sabhi nevaly formalities aur requirements poori ki gayi thi ya nahi. Agar nahi, to PC fresh enquiry release karega.
>
> 📋 Process
> 1. Single Offer milte hue, PC check karta hai ki enquiry floating karne mein sabhi nevaly formalities poori ki gayein hain ya nahin.
> 2. Agar formality poore nahi, to PC fresh enquiry release karta hai.
> 3. Agar estimated value 25 lakh #pAE se zyada hai, to PC ki approval lagni chahiye.
>
> 📘 Source: Manual_for_Procurement_of_works_2019.pdf

### Q97. Performance security deposit accept karne ke kya modes hain?

- **Role/Lang:** Officer · Hinglish  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 39.84s  |  **Sources:** 4  
- **Cited:** Manual_for_Procurement_of_works_2019.pdf, GFRupdatedupto31012026.pdf, FInal_GFR_upto_31_07_2024.pdf, publicProManual-1755343081262-715558279.pdf  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> Performance Security deposit karne ke liye ek vikalpachi pratikriya hai jo Sources mein dikha gaya hai. Performance Security ko Insurance Surety Bond, Account Payee Demand Draft, Fixed Deposit Receipt se Commercial bank se Bank Guarantee (including e-Bank Guarantee) aur online payment ke roop mein furnish kiya ja sakta hai. Performance Security ki validity 60 dinon ka hoti hai completion date ke baad, jo contractual obligations ko complete karne ke liye zaroori hai.
>
> 📋 Process
> 1. Performance Security ko Insurance Surety Bond, Account Payee Demand Draft, Fixed Deposit Receipt se Commercial bank se Bank Guarantee (including e-Bank Guarantee) aur online payment ke roop mein furnish kiya ja sakta hai.
> 2. Performance Security ki validity 60 dinon ka hoti hai completion date ke baad, jo contractual obligations ko complete karne ke liye zaroori hai.
>
> 📘 Source: [Source 1: Manual_for_Procurement_of_works_2019.pdf], [Source 2: GFRupdatedupto31012026.pdf], [Source 3: FInal_GFR_upto_31_07_2024.pdf]

### Q98. Short term tender notice publish karne ke liye time limit kitni di gayi hai?

- **Role/Lang:** Officer · Hinglish  
- **Intent:** `UNKNOWN` (conf 0.0) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 34.35s  |  **Sources:** 3  
- **Cited:** Store_Purhase_Rules_28.01.2021.pdf, GFRupdatedupto31012026.pdf, mannual procurement.pdf  
- **Answer entities:** Thresholds: ₹50,000, ₹10 lakh, 21 days, 30 days  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> Open tender notice ke liye time limit tender value par depend karti hai. Agar tender value ₹50,000 se ₹10 lakh tak hai, to time limit 21 din ka hai. Agar tender value ₹10 lakh se zyada hai, to time limit 30 din ka hai.
>
> 📋 Process
> 1. Tender value ₹50,000 - ₹10 lakh: Time limit – 21 days
> 2. Tender value ₹10 lakh ke zyada: Time limit – 30 days
> 3. Time limit above values ki calculation tender notice publication date se hoti hai.
>
> 📘 Source: mannual procurement.pdf

### Q99. CVC ke rules ke mutabik negotiation L1 ke sath kab kiya ja sakta hai?

- **Role/Lang:** Officer · Hinglish  
- **Intent:** `RULES_GFR` (conf 0.8) ✅  |  **Outcome:** ANSWERED  |  **Latency:** 37.57s  |  **Sources:** 3  
- **Cited:** Compilation of CVC Circulars and Guidelines.pdf, mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf  

> **Response:**
> 💡 Answer
> I'm not fully certain this matches your question - please verify with the cited document.
> CVC ke rules ke mutabik negotiation L1 ke sath exceptional circumstances mein hi kiya ja sakta hai. Agar procurement nomination basis par hota hai, single or limited sources se, cartel formation ka suspicion hota hai, ya agar urgent requirements hoti hain jo essential operations, maintenance aur safety ko jeopardise kar sakti hain, tohi L1 bidder ke sath negotiation considered kiya ja sakta hai. However, balance bulk requirement ko re-tender process ke zariye procure karna zaroori hai.
>
> 📋 Process
> 1. Nomination basis par procurement ho raha ho.
> 2. Single or limited sources se procurement ho raha ho.
> 3. Cartel formation ka suspicion ho.
> 4. Urgent requirements jo essential operations, maintenance aur safety ko jeopardise kar sakti hain.
> 5. L1 bidder ke sath negotiation karna.
> 6. Balance bulk requirement ko re-tender process ke zariye procure karna.
>
> 📘 Source: Compilation of CVC Circulars and Guidelines.pdf

### Q100. MSE bidders ko price bid me kya preference milti hai?

- **Role/Lang:** Officer · Hinglish  
- **Intent:** `BID_SUBMISSION` (conf 0.6) ❌  |  **Outcome:** ANSWERED  |  **Latency:** 41.18s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf, mannual procurement.pdf  
- **Answer entities:** Thresholds: 15%  

> **Response:**
> 💡 Answer
> MSE bidders ko price bid me preference milti hai agar unki price L1+15% ke margin mein hoti hai. Iska matlab yeh hai ki agar L1 bidder ek Micro aur Small Enterprise (MSE) nahi hai, to MSE bidders eligible hain jo price preference margin mein L1+15% ke andar apni price qutathein hain. Agar procuring entity L1 bidder se negotiate karta hai, to preference margin ko L1 price par calculate karna chahiye, nahin negotiated price par. Yeh eligible MSEs ko policy ke anusar L1 price ko match karne ki koshish karne doonga.
>
> 📋 Process
> 1. L1 bidder ek MSE nahi hai.
> 2. MSE bidders jo L1+15% margin mein apni price qutathein hain, unhe preference milti hai.
> 3. Procuring entity L1 bidder se negotiate karta hai aur preference margin ko L1 price par calculate karta hai.
> 4. Eligible MSEs L1 price ko match karne ki koshish karte hain.
>
> 📘 Source: publicProManual-1755343081262-715558279.pdf
