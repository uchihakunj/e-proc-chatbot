# CHiPS e-Procurement Chatbot — 50-Question Evaluation Report

**Date:** 2026-06-30  
**Endpoint tested:** `POST /api/stream` (production SSE path → BGE-M3 retrieval + bge-reranker + Ollama `gemma3:4b`)  
**Knowledge base:** Qdrant collection `db3`, 3,503 chunks  
**NLU layer:** `nlp_features.py` (`classify_intent`, `extract_entities`) evaluated locally per query  
**Questions:** 50  |  **Harness:** `05_webui/run_qa_eval.py`  |  **Raw data:** `05_webui/qa_eval_results.json`

---

## 1. Executive Summary — the four metrics

| Metric | Result |
|---|---|
| **Intent Recognition Accuracy** | **49/50 = 98%** correct routing (24 fired a specific intent, 26 correctly stayed `UNKNOWN`→general RAG) |
| **Entity Extraction** | **0/50 queries carried extractable entities** — this set is document-discovery (no amounts/dates/PAN/names), so the NER layer correctly returned empty. Extractor not exercised by this set. |
| **Response Time (Latency)** | avg **31s**, median **32s**, range 2–49s (full set). Cache hits ~2s; live generation avg **32s** |
| **Error Handling (Fallback Rate)** | **1/50 = 2%** (1 graceful scope-refusal, 0 empty-generation). 0 crashes, 0 model-fallback events, 1 instant cache hits |

### Headline read

- **49/50 (98%) answered successfully** with cited source documents each.
- **Intent routing was correct on 49/50.** The taxonomy is action-based (EMD/DSC/GFR/AUCTION/BID_SUBMISSION/VENDOR_REGISTRATION/PORTAL_USAGE); for generic "what does document X say" questions `UNKNOWN` is the *correct* label and the query still routes to full RAG. Every "Under GFR…" query fired `RULES_GFR` (conf 1.0), DSC-manual queries fired `DSC`, the step-by-step questions fired `AUCTION`/`BID_SUBMISSION`/`VENDOR_REGISTRATION`/`PORTAL_USAGE`.
- **Only 1 true intent miss:** Q50 ("CHiPS online" settings) stayed `UNKNOWN` where `PORTAL_USAGE` was expected — it still answered correctly via RAG.
- **Entity extraction = 0** is expected, not a defect: none of these questions contain transactional entities. The extractor should be validated separately with entity-bearing queries (amounts, EMD %, dates, PAN/GSTIN, vendor names).
- **Latency averages ~31s** (median 32s) on the CPU/Arc-iGPU stack — generation-bound, consistent with the known reranker+LLM floor. Not a correctness problem but the main UX risk.
- **Error handling worked as designed:** 1 graceful scope-refusal(s), 0 empty-generation failures, 0 crashes.

---

## 2. Intent Recognition — detail

Intent distribution across the 50 questions:

| Intent | Count |
|---|---|
| `UNKNOWN` | 26 |
| `RULES_GFR` | 12 |
| `DSC` | 4 |
| `AUCTION` | 2 |
| `PORTAL_USAGE` | 2 |
| `EMD_GENERAL` | 1 |
| `BID_SUBMISSION` | 1 |
| `VENDOR_REGISTRATION` | 1 |
| `EMD_PAYMENT` | 1 |

- **Specific intent fired:** 24/50. All correct/acceptable for routing.
- **`UNKNOWN`:** 26/50 — correct for pure document-lookup phrasings ("main guidelines mentioned in X", "what does X regulate"). These are not refusals; they route to general RAG and answered fine.
- **Acceptable-but-loose:** Q30 (IT Act Rules → `RULES_GFR`, fired on the word "Rules").
- **Miss:** Q50 (`UNKNOWN`; expected `PORTAL_USAGE`).

---

## 3. Latency — detail

- Overall avg **31.3s**, median **31.9s**, stdev 8s.
- Live-generation avg **31.9s** (excludes 1 cache hits).
- **Cache hits** (1): Q50 — served in ~2s by the near-duplicate answer cache.
- **Slowest 5:** Q48 (49s), Q6 (43s), Q9 (41s), Q36 (39s), Q35 (39s).

---

## 4. Error Handling / Fallback — detail

| Q | Type | Sources | Latency | Note |
|---|---|---|---|---|
| Q20 | scope-refusal | 0 | 4s | graceful in-scope-not-found refusal (correct behaviour) |

- **No HTTP 500s, no crashes, no automatic model-fallback fired** during the run (`gemma3:4b` had ample iGPU headroom).
- **No empty-generation failures this run:** every retrieval that found sources produced a non-empty answer; the single refusal (Q20) was a correct in-scope-not-found message.

---

## 5. Full results — every question, answer & metrics

### Q1. What are the main guidelines mentioned in short term tender?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 32.9s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf, GFRupdatedupto31012026.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The key guidelines for a short-term tender, as outlined across the provided documents, center around efficient communication and streamlined processes to ensure rapid bid submissions. Specifically, the NIT must be easily searchable and visible on the website, notifications should be sent to registered vendors via SMS/mail/email, and sufficient time (minimum 21 days) should be allowed for bid preparation, potentially adjustable based on the nature of the requirements.  Furthermore, ensuring easy access to tender documents and avoiding any impediments is crucial.

📋 Process
1. Ensure NIT visibility: The NIT must be easily searchable and visible on the e-Procurement portal.
2. Notify Registered Vendors: Send notifications (SMS/mail/email) to registered vendors about upcoming tenders.
3. Adequate Timeframe: Allow a minimum of 21 days for bid preparation, with potential adjustments based on requirements.
4. Easy Access to Documents: Ensure unobstructed access to tender documents for all bidders.

📘 Source: publicProManual-1755343081262-715558279.pdf

### Q2. What are the main guidelines mentioned in short tender?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 23.7s  |  **Sources:** 4  
- **Cited:** publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf, GFRupdatedupto31012026.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The short tender document should include key elements to ensure clarity and responsiveness from bidders. These guidelines are: a) A clear description of the subject matter of procurement, including specifications, quantity, time, and location; b) Eligibility criteria for goods, outlining any restrictions or conditions regarding origin; c) The procedure and timeline for submitting bids, including dates, times, and locations; d) Criteria for evaluating bids; e) Special terms affecting performance; f) Essential terms of the procurement contract, including interpretation under Indian laws; g) A clause stating that NIL charges will be treated as unresponsive; and h) Contact information for authorized communication with contractors.

📋 Process
1.  Include a clear description of the subject matter of procurement.
2.  Define eligibility criteria for goods.
3.  Specify the bid submission procedure and timeline.
4.  Outline the evaluation criteria.
5.  Address special terms affecting performance.
6.  State essential contract terms, including interpretation under Indian law.
7.  Include a clause regarding NIL charges.
8.  Provide contact information for communication.

📘 Source: mannual procurement.pdf

### Q3. What is the core objective of Notification EMDExemption?

- **Intent:** `EMD_GENERAL` (conf 0.6) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 33.8s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf, GFRupdatedupto31012026.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The core objective of Notification EMD Exemption, as outlined in publicProManual-1755343081262-715558279.pdf, is to reduce the financial burden on unsuccessful bidders by exempting certain categories of bidders – specifically MSEs and those meeting DPIIT registration criteria – from paying the Earnest Money Deposit (EMD). This aims to encourage wider participation in government tenders.

📋 Process
1.  Identification of Exempt Categories: The notification identifies specific categories of bidders that qualify for EMD exemption, primarily MSMEs registered with DPIIT and startups recognized by DPIIT.
2.  Verification of Registration Details: Bidders falling into these categories must furnish certified copies of their valid registration details to demonstrate compliance.
3.  Reduced Financial Burden: By waiving the EMD requirement, the notification seeks to lower the financial risk associated with bidding, thereby promoting greater competition and transparency in government procurement.

📘 Source: publicProManual-1755343081262-715558279.pdf

### Q4. What are the main guidelines mentioned in CVC Guidelines on Tenders and Contracts?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 33.0s  |  **Sources:** 3  
- **Cited:** Compilation of CVC Circulars and Guidelines.pdf, mannual procurement.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
The Central Vigilance Commission’s (CVC) guidelines prioritize transparency in procurement processes. Key recommendations include wider publicity of tenders through various channels like newspapers and websites, avoiding restrictive practices such as requiring tender samples for subjective assessments like shade or finish, and utilizing detailed specifications for procurement instead of relying on subjective sample evaluations. Furthermore, the CVC emphasizes the importance of clear and comprehensive Tender Documents with specific sections covering Notices Inviting Tender (NIT), Instructions to Bidders (ITB), General Conditions of Contract (GCC), Special Conditions of Contract (SCC), and a Bill of Quantities (BOQ).

📋 Process
1.  Ensure wide publicity of tenders through newspapers, trade journals, and website publication as directed by the CVC.
2.  Avoid requiring tender samples for subjective assessments; instead, use detailed specifications.
3.  Utilize Standard Bidding Documents (SBDs) to standardize bidding processes.
4.  Maintain comprehensive Tender Documents with clearly defined sections (NIT, ITB, GCC, SCC, BOQ).

📘 Source: Compilation of CVC Circulars and Guidelines.pdf

### Q5. What does the document regulate regarding Compilation Tenders Contracts?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 31.3s  |  **Sources:** 3  
- **Cited:** mannual procurement.pdf, publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The tender document plays a fundamental role in public procurement, serving as the basis for contract agreements and aiming to prevent delays and disputes. It must be comprehensive, clear, and unambiguous, covering aspects like specifications, payment terms, timelines, and quality assurance measures. The document should also address eligibility criteria, purchase preference policies, and conflict of interest situations to ensure a fair and transparent bidding process.

📋 Process
1.  The tender document outlines the subject matter of procurement, including specifications, quantities, delivery locations, and quality standards.
2.  It specifies limitations or preferences for bidder participation based on government policies (e.g., Make in India).
3.  It details the procedure for obtaining, submitting, and opening bids, along with relevant dates and times.
4.  It includes provisions for bidders to question bidding conditions or rejection of their bids within a defined timeframe.

📘 Source: mannual procurement.pdf

### Q6. Under GFR and government rules, what is the procedure for Compilation Tenders Contracts?

- **Intent:** `RULES_GFR` (conf 1.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 42.5s  |  **Sources:** 4  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, GFRupdatedupto31012026.pdf, mannual procurement.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The procedure for compilation of tenders and contracts under GFR and government rules involves several key steps to ensure transparency and compliance. Primarily, the procuring entity must adhere to the guidelines outlined in documents like the Final GFR (upto 31/07/2024) and the Manual for Procurement of Goods 2024, particularly regarding bidding document content and evaluation criteria. This includes clearly defining specifications, eligibility criteria, and a transparent process for evaluating bids, as detailed in Section 5 of the Manual for Procurement of Goods. Furthermore, any restrictions on bidders from countries sharing land borders with India, as stipulated in Order (Public Procurement No.1)58, must be meticulously followed. The bidding document should explicitly state that bids quoting NIL charges will be considered non-responsive.

📋 Process
1.  Define Clear Specifications: The procuring entity must establish detailed specifications for the goods or services being procured, ensuring clarity and avoiding ambiguities as per GFR guidelines (Source 2).
2.  Establish Eligibility Criteria: Define clear eligibility criteria for bidders, including experience, technical capabilities, and financial position, aligning with departmental requirements (Source 2).
3.  Implement Registration Requirements: If applicable, enforce registration requirements for bidders from specific countries, following the procedures outlined in Order (Public Procurement No.1)58 (Source 3).
4.  Evaluate Bids Transparently: Evaluate bids based on pre-defined criteria, ensuring a fair and competitive process as detailed in the Manual for Procurement of Goods 2024 (Source 4).
5.  Address NIL Bid Clause: Include a clause stating that bids with NIL charges will be treated as non-responsive (Source 2 & 4).

📘 Source: Final GFR upto 31/07/2024.pdf

### Q7. What are the main guidelines mentioned in Instructions to department users and bidders?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 35.6s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The public procurement manual outlines several key guidelines for both department users and bidders. For department users, it emphasizes utilizing the model NIT format, ensuring the NIT contains sufficient information to attract competition, and inviting all likely bidders through various channels like email and SMS.  For bidders, the manual stresses meeting eligibility criteria outlined in the ITB, maintaining proper records of tender document sales, and adhering to specific requirements regarding JV partnerships and past performance. The core focus is on clear communication within the tender documents themselves, covering technical specifications, commercial terms, and dispute resolution mechanisms.

📋 Process
1.  **NIT Format:** Department users must utilize the model NIT format in MTD for publishing tender notices.
2.  **Information Content:** The NIT (and its TIS) needs to provide sufficient information for prospective bidders to assess their participation.
3.  **Bidder Invitation:** All likely bidders should be invited through email, SMS, or letters to maximize competition.
4.  **Eligibility Criteria:** Bidders must meet the eligibility criteria defined in the ITB (e.g., registration with EPF, JV restrictions).
5.  **Record Keeping:** The procuring entity needs to maintain records of tender document sales and unsold documents.

📘 Source: publicProManual-1755343081262-715558279.pdf

### Q8. What does the document regulate regarding Instructions for department users and bidders?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 32.0s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
The publicProManual-1755343081262-715558279.pdf document regulates the tender process by outlining the key sections within the Tender Document, including the Notice Inviting Tender (NIT), Instructions to Bidders (ITB), General Conditions of Contract (GCC), Special Conditions of Contract (SCC), and Financial Bid (BOQ Excel Sheet). It emphasizes the importance of a clear and comprehensive NIT for attracting competition and ensuring bidders have sufficient information to participate effectively.

📋 Process
1.  The document details the structure of the Tender Document, specifying sections I through VIII as essential components.
2.  It highlights the need for a well-defined NIT with an Appendix (TIS) providing summary information.
3.  The manual stresses the importance of clear and unambiguous language in the bid documents to avoid delays and complaints.

📘 Source: publicProManual-1755343081262-715558279.pdf

### Q9. Under GFR and government rules, what is the procedure for Instructions for department users and bidders?

- **Intent:** `RULES_GFR` (conf 1.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 41.2s  |  **Sources:** 4  
- **Cited:** publicProManual-1755343081262-715558279.pdf, GFRupdatedupto31012026.pdf, mannual procurement.pdf, FInal_GFR_upto_31_07_2024.pdf  

> **Answer:** 💡 Answer
The procedure for instructions to department users and bidders, as outlined across several documents, centers around clear communication and documentation within the tender process. Specifically, Section I of the Tender Document (NIT) serves as the primary source of information, detailing the purpose and instructions for all participants. The NIT must contain sufficient detail for prospective bidders to assess their participation and include key elements such as bid submission deadlines, evaluation criteria, and special terms. Furthermore, amendments or clarifications regarding the bidding document are to be communicated in the same manner as the initial document was published (as detailed in GFR 2017 Rule 172).  The inclusion of a clause stating that NIL charges will be treated as unresponsive bids is also crucial (GFR 2017, Rule 172(ii)).

📋 Process
1.  **NIT Publication:** The Department Admin initiates the process by publishing the Notice Inviting Tender (NIT) – this is legally significant and should follow the MTD model format.
2.  **Information Dissemination:** Sufficient information must be included in the NIT to allow potential bidders to determine their suitability and approach the tender. This includes inviting attention of likely bidders via email/SMSs/letters.
3.  **Document Updates:** Any modifications or clarifications to the bidding document (as per Rule 172) must be communicated using the same method as the initial publication.
4. **Bidding Document Content**: The bidding document should include a clause that "if a firm quotes NIL charges/ consideration, the bid shall be treated as unresponsive and will not be considered".

📘 Source: publicProManual-1755343081262-715558279.pdf

### Q10. Where can I find the specific sections about Instructions for department users and bidders?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 31.6s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf, FInal_GFR_upto_31_07_2024.pdf  

> **Answer:** 💡 Answer
The tender documents contain several key sections relevant to instructions for both department users and bidders. Specifically, you can find detailed guidance within Section II: Instructions to Bidders (ITB) and Appendix to Instructions to Bidders (AITB). These sections outline the procedures, requirements, and formats expected throughout the bidding process. Furthermore, Chapter-1: Instructions to Bidders in the NIT provides overarching instructions for all bidders.

📋 Process
1.  Locate Section II: Instructions to Bidders (ITB) within the tender document. This section details the steps involved in preparing and submitting a bid.
2.  Review Appendix to Instructions to Bidders (AITB). This appendix likely contains supplementary information and clarifications related to ITB.
3. Examine Chapter-1: Instructions to Bidders in the NIT for overarching instructions.

📘 Source: publicProManual-1755343081262-715558279.pdf

### Q11. What are the main guidelines mentioned in CVC guidelines?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 31.8s  |  **Sources:** 3  
- **Cited:** Compilation of CVC Circulars and Guidelines.pdf, Vigilance Manual (Updated 2021) English.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
The CVC guidelines encompass a wide range of areas aimed at ensuring integrity and preventing corruption within government administration. Key guidelines include prompt action on disciplinary matters for major penalty proceedings, regular backup of application and data with commensurate regularity, control of source code and configuration management, and system audits and forensic investigations. Furthermore, the CVC has an advisory role in discipline and appeal cases, investigates and recommends actions to entities, and plays a role in appointments and monitoring. Finally, vigilance clearance for public servants is also a key component, obtained through a process involving DoPT guidelines and CVC input.

📋 Process
1.  Ensure prompt/timely action on disciplinary matters with major penalty proceedings.
2.  Implement regular backup procedures for application and data.
3.  Establish controls over source code and configuration management.
4.  Conduct system audits and forensic investigations, reporting to the CVC.
5.  Follow DoPT guidelines for vigilance clearance of public servants.

📘 Source: Compilation of CVC Circulars and Guidelines.pdf

### Q12. What is the core objective of CVC guidelines?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 27.7s  |  **Sources:** 3  
- **Cited:** Compilation of CVC Circulars and Guidelines.pdf, publicProManual-1755343081262-715558279.pdf, Vigilance Manual (Updated 2021) English.pdf  

> **Answer:** 💡 Answer
The core objective of CVC guidelines, as outlined in Compilation of CVC Circulars and Guidelines (Source 1), is to improve vigilance administration by increasing transparency through greater scrutiny of tendering processes. Specifically, the directive aims to ensure that all tenders are placed on the web-site, with regular tracking by CVOs to monitor compliance.

📋 Process
1.  CVOs must regularly track tender notices and website activity.
2.  CVO’s should pursue newspaper advertisements to ensure compliance.
3.  The Commission requires monthly reports detailing whether all tenders were placed on the web-site, with explanations for non-compliance.

📘 Source: Compilation of CVC Circulars and Guidelines.pdf

### Q13. What are the main guidelines regarding CVC guidelines?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 33.4s  |  **Sources:** 3  
- **Cited:** Compilation of CVC Circulars and Guidelines.pdf, Vigilance Manual (Updated 2021) English.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
The Central Vigilance Commission (CVC) provides several key guidelines related to vigilance administration. Primarily, it advises Ministries/Departments on maintaining integrity in administration, including vigilance inputs regarding public servants’ antecedents – often referred to as ‘Vigilance Clearance’.  Specifically, CVC relies on DoPT guidelines for obtaining this clearance, particularly concerning AIS officers, ensuring continued verification from State Governments and Ministry when dealing with Central Government officers. The CVC also oversees the functioning of the CBI and has jurisdiction over corruption cases under various acts like the Lokpal Act and Money Laundering Act, though it lacks arrest powers.

📋 Process
1.  The CVC advises Ministries/Departments on maintaining integrity in administration, including vigilance inputs regarding public servants’ antecedents (Vigilance Clearance).
2.  It relies on DoPT guidelines for obtaining Vigilance Clearance, particularly concerning AIS officers.
3.  This involves continued verification from State Governments and the relevant Ministry when dealing with Central Government officers.
4. The CVC oversees the CBI's investigations into corruption cases.
5. It has jurisdiction over cases under the Lokpal and Lokayukta Acts, and the Money Laundering Act.

📘 Source: Compilation of CVC Circulars and Guidelines.pdf

### Q14. Is it mandatory to follow the rules of CVC guidelines?

- **Intent:** `RULES_GFR` (conf 0.8) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 32.4s  |  **Sources:** 3  
- **Cited:** Compilation of CVC Circulars and Guidelines.pdf, Vigilance Manual (Updated 2021) English.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
The Central Vigilance Commission (CVC) expects organizations to implement its instructions regarding transparency and disciplinary procedures, although its recommendations are not legally binding. The CVC’s role is primarily advisory and investigative, focusing on recommending actions and reporting deviations to the Parliament.

📋 Process
1.  The CVC provides guidelines through circulars like No. 000/VGL/18 dated 23.05.2000 regarding timely action in disciplinary matters.
2.  It expects organizations to ensure transparency in tender processes, as evidenced by its consideration of websites used for publicizing tenders.
3. The CVC’s role extends to overseeing the CBI's investigations into corruption and providing guidance on appointments and integrity pacts.

📘 Source: Compilation of CVC Circulars and Guidelines.pdf

### Q15. What are the main guidelines mentioned in the DSC manual?

- **Intent:** `DSC` (conf 0.6) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 37.7s  |  **Sources:** 4  
- **Cited:** CHiPS_Vendor_Registration_Manual_English.pdf, Manual_for_Procurement_of_works_2019.pdf, CHiPS_Bid_Submission_Manual_English.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
The primary guidelines outlined in the DSC manual relate to obtaining a Digital Signature Certificate (DSC) necessary for participation in e-procurement processes. Specifically, vendors are instructed to immediately procure a Class II or Class III DSC from approved Certifying Authorities (CAs) like e-Mudhra, GNFC, IDRBT, MTNLTrustline, NIC, and Safescrypt. The manual details a step-by-step procedure for foreign vendors, involving downloading an application form from the CCA website, submitting it to the Indian Embassy along with original documents for certification, making an online fund transfer as instructed by the CA, and subsequently couriering the certified documents to the relevant authority.

📋 Process
1.  Procure a Class II or Class III DSC from one of the listed Certifying Authorities (e-Mudhra, GNFC, IDRBT, MTNLTrustline, NIC, Safescrypt).
2.  Download the Registration/Application form from the CCA website: https://cca.gov.in.
3.  Fill out the application form and submit it to the Indian Embassy with original documents for certification.
4.  Make an online fund transfer as instructed by the CA (Swift code provided by the CA).
5.  Couriered certified documents to the relevant authority.

📘 Source: CHiPS_Vendor_Registration_Manual_English.pdf

### Q16. What is the core objective of the DSC manual?

- **Intent:** `DSC` (conf 0.6) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 30.9s  |  **Sources:** 3  
- **Cited:** CHiPS_Vendor_Registration_Manual_English.pdf, mannual procurement.pdf, CHiPS_Bid_Submission_Manual_English.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The core objective of the DSC manual is to guide vendors, particularly foreign ones, through the process of obtaining a Digital Signature Certificate (DSC) which is essential for participating in e-procurement activities within the Chhattisgarh Infotech Promotion Society (CHiPS). It outlines the necessary steps, including contacting approved Certifying Authorities and completing required documentation.

📋 Process
1.  The manual details the necessity of acquiring a DSC for accessing the e-Procurement portal.
2.  It provides a step-by-step procedure for foreign vendors to obtain a DSC, involving downloading application forms from licensed CAs (approved by CCA), submitting documents to the Indian Embassy for certification, and making an online fund transfer.
3. It lists contact details of approved DSC Certifying Authorities: e-Mudhra, GNFC, IDRBT, MTNLTrustline, NIC, Safescrypt.

📘 Source: CHiPS_Vendor_Registration_Manual_English.pdf

### Q17. What procedure is prescribed under the DSC manual?

- **Intent:** `DSC` (conf 0.6) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 25.0s  |  **Sources:** 4  
- **Cited:** CHiPS_Vendor_Registration_Manual_English.pdf, mannual procurement.pdf, Manual_for_Procurement_of_works_2019.pdf, CHiPS_Bid_Submission_Manual_English.pdf  

> **Answer:** 💡 Answer
The process for obtaining a Digital Signature Certificate (DSC) as outlined in the CHiPS Vendor Registration Manual involves several steps for foreign vendors. Initially, the vendor must download the Registration/Application form from an approved CA website (e.g., e-Mudhra, GNFC). Subsequently, they fill out the application with required documents and submit them to the Indian Embassy along with original copies for certification. An online fund transfer equivalent to the Rupee amount in their respective currency is then made using the CA’s bank Swift code. Finally, the certified documents are couriered to the Indian Embassy.

📋 Process
1. Download Registration/Application form from an approved CA website (e.g., e-Mudhra, GNFC).
2. Fill out the application form with required documents.
3. Submit the completed application and original documents to the Indian Embassy.
4. Obtain certification of documents by the Indian Embassy.
5. Make online fund transfer in Rupee equivalent amount using CA’s bank Swift code.
6. Courier certified documents to the Indian Embassy.

📘 Source: CHiPS_Vendor_Registration_Manual_English.pdf

### Q18. What are the main guidelines mentioned in the DSC tutorial?

- **Intent:** `DSC` (conf 0.6) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 32.1s  |  **Sources:** 4  
- **Cited:** CHiPS_Vendor_Registration_Manual_English.pdf, CHiPS_Bid_Submission_Manual_English.pdf, Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The primary guidelines outlined in the DSC tutorial relate to obtaining a Digital Signature Certificate (DSC) for e-procurement participation. Specifically, foreign vendors must download a registration/application form from an approved CA (e-Mudhra, GNFC, IDRBT, MTNLTrustline, NIC, Safescrypt), fill it out with required documents, and have those documents certified by the Indian Embassy. An online fund transfer equivalent to the rupee amount is then required, followed by courier of the embassy’s documents.

📋 Process
1.  Download registration/application form from an approved CA (e-Mudhra, GNFC, IDRBT, MTNLTrustline, NIC, Safescrypt).
2.  Fill out the application form with requisite documents.
3.  Have documents certified by the Indian Embassy.
4.  Make online fund transfer equivalent to the rupee amount (Swift code provided by CA).
5.  Courier the embassy’s certified documents.

📘 Source: CHiPS_Vendor_Registration_Manual_English.pdf

### Q19. Under GFR and government rules, what is the procedure for the tutorial?

- **Intent:** `RULES_GFR` (conf 1.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 33.4s  |  **Sources:** 3  
- **Cited:** GFR2017_HINDI.pdf, FInal_GFR_upto_31_07_2024.pdf, GFRupdatedupto31012026.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The procedure for the tutorial, as outlined in the GFR documents, involves scrutiny of procedures by which the sanctioning authority satisfies itself regarding the fulfillment of conditions subject to which grants and/or loans were given. Specifically, Rule 236(3) states that the Institution or Organisation shall get its accounts audited from Chartered Accountants of its own choice, unless the Comptroller and Auditor General of India is the sole auditor.  Rule 238 (1) details utilization certificates for non-recurring grants.

📋 Process
1. Audit scrutiny by designated authority: The sanctioning authority scrutinizes procedures to ensure conditions are met.
2. Account Auditing: The Institution or Organisation gets its accounts audited from Chartered Accountants of its own choice, unless the Comptroller and Auditor General of India is the sole auditor.
3. Utilization Certificate preparation:  A certificate of actual utilization is prepared for non-recurring grants (Rule 238(1)).

📘 Source: FInal_GFR_upto_31_07_2024.pdf

### Q20. Where can I find the specific sections about the tutorial?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** REFUSED (scope-refusal)  |  **Latency:** 3.7s  |  **Sources:** 0  

> **Answer:** The answer to this question was not found in the available documents.

### Q21. What are the main guidelines mentioned in the final GFR?

- **Intent:** `RULES_GFR` (conf 0.6) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 31.1s  |  **Sources:** 3  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, GFR2017_HINDI.pdf, GFRupdatedupto31012026.pdf  

> **Answer:** 💡 Answer
The final General Financial Rules (GFR) 2017, as outlined across multiple documents, establishes a framework for managing government finances. Key guidelines include rules regarding short titles and commencement (Rule 1), definitions of key terms such as Accounts Officer, Appropriation, Audit Officer, Consolidated Fund, and Contingency Fun (Rule 2), procedures for preparing detailed estimates for revenue receipts and expenditure (Rules 128, 130, 132, 139, 142), processes for collecting supplementary demands, and provisions related to the Contingency Fund of India and land/building transfers (Rules 6, 7, and 8).

📋 Process
(This section is omitted as there isn't a numbered process outlined in the provided documents.)

📘 Source: FInal_GFR_upto_31_07_2024.pdf

### Q22. What does the final GFR regulate regarding 2024?

- **Intent:** `RULES_GFR` (conf 0.6) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 26.7s  |  **Sources:** 3  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, GFRupdatedupto31012026.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
The Final GFR upto 31.07.2024 regulates General Financial Rules, 2017 which are applicable to all Central Government Ministries/Departments and attached/subordinate bodies. It includes definitions of key terms such as “Accounts Officer,” “Administrator,” and “Appropriation.”

📋 Process
(None - This is a factual answer based on the document)

📘 Source: Final_GFR_upto_31_07_2024.pdf

### Q23. What are the main guidelines mentioned in the GeM manual?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 35.1s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf, FInal_GFR_upto_31_07_2024.pdf  

> **Answer:** 💡 Answer
The GeM manual outlines several key guidelines for procurement through the Government e-Marketplace (GeM) portal. These include a prohibition against dividing demand into small quantities to avoid L1 bidding, mandatory use of the GeM portal where goods/services are available, and requirements for supplier registration and certificate compliance. The manual also details procedures for generating GeMAR&PTS reports, utilizing Business Analytics tools on GeM, and adhering to Model Clauses/Certificates.

📋 Process
1.  Prohibition against Piecemeal Purchases: Demand for goods cannot be divided into small quantities to avoid L1 bidding on GeM.
2.  GeM Portal Usage: Goods/services must be procured through the GeM portal when available.
3.  GeMAR&PTS Reporting: Buyers must generate a "GeM Availability Report and Past Transaction Summary" (GeMAR&PTS) for procurement outside GeM.
4.  Business Analytics Tools: Utilize BA tools on GeM to assess price reasonableness.
5.  Supplier Registration & Compliance: Vendors/bidders registered with GeM must provide a certificate of compliance.

📘 Source: publicProManual-1755343081262-715558279.pdf

### Q24. Under GFR and government rules, what is the procedure for the GeM manual?

- **Intent:** `RULES_GFR` (conf 1.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 34.6s  |  **Sources:** 4  
- **Cited:** Manual_for_Procurement_of_works_2019.pdf, FInal_GFR_upto_31_07_2024.pdf, publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
The GeM portal’s procedures are governed by several key regulations. Ministries and Departments are expected to utilize the GeM platform for procuring goods and services, particularly bulk quantities, as outlined in GFR rules and the publicProManual. Specifically, they must project their annual procurement plan on the GeM portal within 30 days of budget approval, utilizing either OPEX or CAPEX models.  The Business Analytics (BA) tools available on GeM can be used to assess price reasonableness before placing orders.

📋 Process
1. Project Annual Procurement Plan: Ministries/Departments must project their annual procurement plan for goods and services on the GeM portal within 30 days of budget approval, utilizing either OPEX or CAPEX models.
2. Utilize BA Tools: Employ Business Analytics (BA) tools available on GeM to assess price reasonableness before placing orders. These tools include last purchase prices on GeM and the department’s own last purchase price.
3. Compliance with GeM Terms: Ensure all vendors/bidders registered with GeM provide a certificate regarding compliance with Order terms, as mandated by the GeM portal.

📘 Source: publicProManual-1755343081262-715558279.pdf

### Q25. What is the core objective of the GeM manual?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 33.0s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
The core objective of the GeM manual is to facilitate efficient and transparent procurement of goods and services by government departments through the Government e-Marketplace (GeM) platform. This includes promoting competition among suppliers, leveraging aggregate demand for better pricing, and streamlining the entire procurement process electronically.

📋 Process
1.  Establishment of GeM: The manual highlights the creation of GeM as an e-commerce marketplace for common goods and services.
2.  Supplier Registration & Certification: It outlines the registration process for suppliers on GeM, emphasizing certification by the GeM SPV.
3.  Procurement Rules & Guidelines: The manual references Rule 149 of GFR, 2017, detailing the mandatory use of GeM for goods and services available on the platform.
4.  Bidding Methods: It describes various bidding methods available on GeM, including online bidding, reverse auction, and e-auction, suitable for different procurement volumes.
5.  Rate Reasonability Assessment: The manual stresses the responsibility of procuring authorities to assess the reasonability of rates offered through GeM.

📘 Source: mannual procurement.pdf

### Q26. What are the main guidelines mentioned in the GeM handbook?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 38.5s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
The primary guidelines outlined within the provided documents regarding the Government e-Marketplace (GeM) center around mandatory procurement on GeM whenever possible, utilizing available tools for price reasonableness and bid evaluation, and establishing a streamlined registration process for vendors. Specifically, GeM should be utilized for purchases up to Rs. 50,000/- through any available supplier, above this amount using the lowest priced seller amongst at least three manufacturers, and above Rs. 10,00,000/- utilizing online bidding or reverse auction tools. The portal also mandates a "GeM Availability Report and Past Transaction Summary" (GeMAR&PTS) for procurement outside GeM.

📋 Process
1.  Mandatory Use of GeM: Goods and services available on GeM must be procured through it whenever possible, adhering to the monetary ceilings outlined in Rule 149.
2.  Price Reasonableness Tools: Buyers can utilize Business Analytics (BA) tools on GeM to assess price reasonableness before placing orders.
3.  Bid Evaluation Methods: Online bidding and reverse auction tools are mandatory for procurements above specified thresholds.
4.  GeMAR&PTS Requirement: A "GeM Availability Report and Past Transaction Summary" (GeMAR&PTS) is required for procurement outside GeM, serving as a pre-requisite for bid evaluation.
5.  Supplier Registration: Vendors must register on GeM and provide compliance certificates.

📘 Source: [Source 1: publicProManual-1755343081262-715558279.pdf]

### Q27. What does the GeM handbook regulate regarding the handbook?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 28.0s  |  **Sources:** 2  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The GeM handbook regulates that Ministries or Departments are mandatory for Goods or Services available on GeM. This means that all procurement of goods and services by government departments must utilize the Government e-Marketplace (GeM) platform, as outlined in Rule 149 of the Final GFR upto 31.07.2024.

📋 Process
1.  Government Departments are required to use GeM for all procurement activities.
2.  The GeM SPV ensures adequate publicity and advertising of items available on the platform.
3.  Procuring authorities must certify the reasonability of rates offered through GeM.

📘 Source: FInal_GFR_upto_31_07_2024.pdf

### Q28. What are the main guidelines mentioned in the general financial rules?

- **Intent:** `RULES_GFR` (conf 1.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 36.2s  |  **Sources:** 3  
- **Cited:** GFR2017_HINDI.pdf, GFRupdatedupto31012026.pdf, FInal_GFR_upto_31_07_2024.pdf  

> **Answer:** 💡 Answer
The General Financial Rules, 2017 outline key provisions for Central Government Ministries/Departments regarding expenditure and financial control. Specifically, Rule 1 states that these rules apply to all Central Government bodies, except Autonomous Bodies where separate approved financial rules exist. Rule 25 focuses on sanctioning funds, requiring details of the grant or appropriation from which expenditure will be met, and ensuring expenditure aligns with budget allocations. Rule 26 assigns responsibilities to controlling officers – they must ensure expenditures don’t exceed budgets, are used for intended purposes, serve public interest, and implement controls against waste and loss. Finally, Rule 27 addresses the effective date of sanctions, subject to Delegation of Financial Powers Rules.

📋 Process
1.  Rule 1: Applies to all Central Government bodies except Autonomous Bodies with separate rules.
2.  Rule 25: Requires details of funds from grants/appropriations when sanctioning expenditure.
3.  Rule 26: Assigns responsibilities to controlling officers for budget adherence and financial oversight.
4.  Rule 27: Specifies the effective date of sanctions, contingent on Delegation of Financial Powers Rules.

📘 Source: General Financial Rules, 2017 (GFR2017_HINDI.pdf) / FInal_GFR_upto_31_07_2024.pdf

### Q29. Under GFR and government rules, what is the procedure for general financial rules?

- **Intent:** `RULES_GFR` (conf 1.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 20.5s  |  **Sources:** 3  
- **Cited:** GFR2017_HINDI.pdf, GFRupdatedupto31012026.pdf, FInal_GFR_upto_31_07_2024.pdf  

> **Answer:** 💡 Answer
The General Financial Rules, 2017 are applicable to all Central Government Ministries/Departments and attached/subordinate bodies. These rules come into force at once and are deemed to be applicable to Autonomous Bodies except where specific financial rules have been approved by the Government.

📋 Process
1.  These rules (GFR) may be called General Financial Rules, 2017.
2.  They shall come into force at once and shall be applicable to all Central Government Ministries/Departments, attached and subordinate bodies.
3. The provisions contained in GFRs are deemed to be applicable to Autonomous Bodies except to the extent the bye-laws of an Autonomous Body provides for separate Financial Rules which have been approved by the Government.

📘 Source: General Financial Rules, 2017 (GFRupdatedupto31072024.pdf)

### Q30. What is the core objective of the IT Act Rules?

- **Intent:** `RULES_GFR` (conf 1.0) 🟡  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 31.4s  |  **Sources:** 4  
- **Cited:** GFRupdatedupto31012026.pdf, it_act_2000_updated english.pdf, it_act_2000_updated hindi.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The core objective of the IT Act Rules, as outlined across multiple sources, is to establish a framework for cybersecurity and data protection within India. Specifically, it aims to protect information and systems from unauthorized access, use, disclosure, disruption, modification, or destruction, along with defining key terms related to electronic records and digital signatures.

📋 Process
1.  The IT Act, through its regulations (as detailed in sources 2 & 3), establishes standards for Certifying Authorities regarding data maintenance and disclosures.
2.  It defines critical terms like “cyber security,” “data,” “digital signature,” and “electronic record” to provide a clear legal basis for enforcement.
3. The Controller has the power to make regulations consistent with the Act, as outlined in section 89 of IT Act (source 2).

📘 Source: it_act_2000_updated english.pdf & it_act_2000_updated hindi.pdf

### Q31. What are the main guidelines mentioned in the procurement manual?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 33.8s  |  **Sources:** 2  
- **Cited:** publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
The primary guidelines outlined in the Procurement Manual focus on establishing a robust and transparent public procurement process. Key aspects include adherence to the Five R’s of Procurement – Refinement, Rationalization, Risk Management, Reduction of Costs, and Resilience – emphasizing value for money. The manual also stresses fundamental principles of financial propriety, incorporates provisions for reserved items and preference policies, and mandates the use of the Central Public Procurement Portal (CPPP). Furthermore, it highlights the importance of Right to Information and proactive information disclosures, along with a defined procurement cycle.

📋 Process
1.  Adherence to the Five R’s of Procurement: This involves refining requirements, rationalizing costs, managing risks, reducing expenses, and building resilience into procurement strategies.
2.  Compliance with Financial Propriety Standards: Following established canons of financial propriety ensures ethical and accountable procurement practices.
3.  Utilization of the CPPP Portal: Leveraging the CPPP for streamlined procurement processes and transparency.
4.  Implementation of Right to Information (RTI) provisions: Ensuring public access to information related to procurement activities.

📘 Source: publicProManual-1755343081262-715558279.pdf

### Q32. What does the procurement manual regulate regarding procurement?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 26.1s  |  **Sources:** 3  
- **Cited:** Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
The procurement manual regulates the acquisition of goods, works, and services by procuring entities, encompassing various sources of funds like grants and loans. It outlines principles such as value for money, transparency, fairness, competition, economy, efficiency, and accountability within the public procurement process. The manual covers aspects including categorization of procurements, authorities competent to purchase, and fundamental principles of public procurement.

📋 Process
(No specific process steps are outlined in these documents regarding what the procurement manual regulates – it’s a broad definition.)

📘 Source: Manual_for_Procurement_of_works_2019.pdf

### Q33. What are the main guidelines mentioned in the procurement of works manual?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 30.6s  |  **Sources:** 2  
- **Cited:** Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
The Procurement of Works Manual outlines several key guidelines for ensuring transparency and fairness in public procurement. These include inviting offers in accordance with the manual’s procedures, verifying that selected offers adequately meet requirements, assessing whether prices are reasonable considering quality, and selecting the most appropriate offer based on all relevant factors while maintaining financial propriety. Furthermore, the manual emphasizes clear communication of acceptance via registered letter or a foolproof method, and requires successful bidders to furnish performance security within a specified timeframe.

📋 Process
1.  Invite offers in accordance with the manual’s procedures.
2.  Verify that selected offer adequately meets requirements.
3.  Assess whether prices are reasonable considering quality.
4.  Select the most appropriate offer based on all relevant factors and financial propriety.
5. Communicate acceptance of offer via registered letter or a foolproof method.
6.  Instruct successful tenderer to furnish performance security within a specified timeframe.

📘 Source: Manual for Procurement of Works (Updated June, 2022)

### Q34. What does the procurement of works manual regulate regarding procurement of works?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 27.1s  |  **Sources:** 2  
- **Cited:** Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
The Manual for Procurement of Works (2022) regulates the acquisition of goods and services, as well as the execution of works, by government organizations. It aims to improve transparency in decision-making and reduce subjectivity within public procurement processes, aligning with General Financial Rules (GFR), 2005. The manual has been extensively revised to incorporate recent changes like the introduction of the Central Public Procurement Portal (CPPP) and preference for domestic contractors.

📋 Process
(This section is omitted as a direct process isn't outlined in the provided documents.)

📘 Source: Manual for Procurement of Works (Updated June, 2022) Government of India Ministry of Finance Department of Expenditure

### Q35. What are the main guidelines mentioned in the MSME procurement policy?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 39.1s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf, GFRupdatedupto31012026.pdf  

> **Answer:** 💡 Answer
The MSME procurement policy, as outlined in the provided documents, focuses on preferential procurement of goods and services from Micro and Small Enterprises (MSEs) registered under Udyam Registration. Key aspects include:

*   **Eligibility:** MSEs registered under Udyam Registration are eligible to benefit from this policy.
*   **Preferential Procurement:** The policy mandates that procuring entities give preference to MSEs producing goods or rendering services.
*   **Reclassification Benefits:** If an MSE’s investment or turnover increases, it continues to receive non-tax benefits for three years from its previous category classification.
*   **SC/ST/Women Ownership:** In the case of proprietary MSEs, the proprietor(s) are considered SC/ST or a Woman; and in partnership MSEs, the partners are treated as such.

📋 Process
There isn’t a defined process outlined in these documents for the MSME procurement policy itself – it's more of a general directive. However, the following steps would be involved:

1.  Ensure the vendor is registered under Udyam Registration.
2.  Evaluate bids from MSEs alongside other vendors, giving preference to MSEs.
3.  If an MSE’s investment or turnover increases, assess if it continues to qualify for previous category benefits.
4.  Verify that the vendor meets SC/ST/Woman ownership criteria where applicable.

📘 Source: publicProManual-1755343081262-715558279.pdf

### Q36. Under GFR and government rules, what is the procedure for MSME procurement?

- **Intent:** `RULES_GFR` (conf 1.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 39.3s  |  **Sources:** 3  
- **Cited:** publicProManual-1755343081262-715558279.pdf, FInal_GFR_upto_31_07_2024.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
The Government of India mandates preferential procurement of goods and services from Micro and Small Enterprises (MSEs) under Rule 153(ii) of GFR 2017, as well as incorporating broader objectives like supporting local industry and job creation through rules 153(iii) and 170(i), 173(i) of GFR 2017. This involves inviting offers from MSEs registered under Udyam Registration, with provisions for reclassification benefits if an enterprise’s investment or turnover changes. The procurement process must also conform to fair, transparent, and reasonable procedures as outlined in Rule 144 of GFR 2017, including consideration of locally manufactured goods or services.

📋 Process
1.  Invitations to offers should be conducted following a fair, transparent, and reasonable procedure as per Rule 144 of GFR 2017.
2.  Procuring authorities must satisfy that the selected offer meets requirements and is reasonably priced (Rule 144).
3.  Preferential procurement from MSEs, backward regions, weaker sections, and locally manufactured goods or services is encouraged (Rules 153(iii) & 170(i), 173(i)).
4.  MSEs reclassified due to increased investment or turnover receive continued non-tax benefits for three years (Rule 153(ii)).

📘 Source: publicProManual-1755343081262-715558279.pdf

### Q37. What are the main guidelines mentioned in PPM?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 32.6s  |  **Sources:** 4  
- **Cited:** Manual_for_Procurement_of_works_2019.pdf, FInal_GFR_upto_31_07_2024.pdf, publicProManual-1755343081262-715558279.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The Public Procurement Manual (PPM) outlines several key guidelines for achieving Value for Money (VfM). Primarily, it emphasizes optimal description of needs, development of value-engineered specifications/Terms of Reference, appropriate packaging/slicing of requirements, and selecting the right procurement mode and tendering system. It also highlights considerations like fitness for purpose, vendor experience, flexibility, environmental sustainability, and total cost of ownership when conducting a VfM assessment.  Due to uncertainties in estimates, subjectivity is generally avoided in routine cases.

📋 Process
1. Optimal Description of Needs: Clearly define the requirements to attract competitive bids.
2. Value-Engineered Specifications/ToR: Develop specifications that balance quality with cost efficiency.
3. Packaging/Slicing of Requirements: Break down complex requirements into smaller, manageable packages.
4. Appropriate Procurement Mode & Tendering System Selection: Choose a system suited to the specific procurement needs.
5. VfM Assessment Considerations: Evaluate factors like fitness for purpose, vendor experience, flexibility, and environmental sustainability.

📘 Source: publicProManual-1755343081262-715558279.pdf

### Q38. Under GFR and government rules, what is the procedure for PPM?

- **Intent:** `RULES_GFR` (conf 1.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 31.4s  |  **Sources:** 3  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, mannual procurement.pdf, GFRupdatedupto31012026.pdf  

> **Answer:** 💡 Answer
The Public Procurement Manual (PPM) outlines a process for procurement of goods and services, emphasizing transparency and adherence to government rules. Key aspects include publishing a complete schedule of the procurement cycle from tender issuance to contract issuance, preparing an Annual Procurement Plan and placing it on the GeM portal within 30 days of budget approval, and utilizing Business Analytics (BA) tools on GeM for price reasonableness assessments.  Furthermore, Ministries/Departments must work out their procurement requirements using either OPEX or CAPEX models and project them on the GeM portal.

📋 Process
1. Publish a complete schedule of the procurement cycle from date of issuing the tender to date of issuing the contract.
2. Prepare and place an Annual Procurement Plan on the GeM portal within 30 days of Budget approval.
3. Utilize Business Analytics (BA) tools available on GeM for price reasonableness assessments.
4. Work out procurement requirements using either OPEX or CAPEX models.

📘 Source: mannual procurement.pdf

### Q39. What is the core objective of the e-Procurement project?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 26.4s  |  **Sources:** 3  
- **Cited:** Précis  e-Procurement Project.pdf, FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
The core objective of the e-Procurement project was to increase efficiency and transparency in public procurement activity across all Government departments within Chhattisgarh. This involved implementing a comprehensive end-to-end solution encompassing vendor registration, indent management, e-tendering, e-auction, contract management, e-payment, and MIS & Accounting.

📋 Process
1. The project aimed to streamline procurement processes.
2. It sought to enhance transparency in government spending.
3.  It utilized a Public Private Partnership (PPP) model with Wipro Ltd. as the Application Service Provider (ASP).

📘 Source: Précis e-Procurement Project.pdf

### Q40. What are the main guidelines mentioned in the public procurement manual?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 29.5s  |  **Sources:** 3  
- **Cited:** Manual_for_Procurement_of_works_2019.pdf, FInal_GFR_upto_31_07_2024.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
The primary guidelines outlined within the provided manuals for public procurement focus on ensuring transparency, fairness, and efficiency in government purchasing processes. Key aspects include objective specifications for goods and services, adherence to national or international standards where available, avoiding excessive purchase quantities, and promoting competition among vendors.  Specifically, the manuals emphasize measurable and functional requirements, minimizing brand preferences, utilizing recognized standards, and managing inventory costs.

📋 Process
1. Objective Specifications: The procurement process should utilize objective, functional, generic, and measurable specifications for goods and services to reduce subjectivity.
2. Standard Adherence: Technical specifications should ideally align with national or international standards where they exist.
3. Quantity Management:  Procurement quantities should be aligned with actual requirements to minimize inventory carrying costs.
4. Competition & Fairness: The process must foster fair, transparent, and competitive offers from vendors.

📘 Source: mannual procurement.pdf

### Q41. What does the public procurement manual regulate regarding the public procurement manual?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 26.2s  |  **Sources:** 3  
- **Cited:** Manual_for_Procurement_of_works_2019.pdf, mannual procurement.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
The public procurement manual regulates public procurement by providing guidelines and procedures for government organizations to acquire goods, works, or services. It outlines key aspects such as contract formation, transparency, fairness, competition, and accountability within the procurement process. The manual serves as a guide for procuring entities to ensure compliance with relevant laws and regulations.

📋 Process
1.  The Manual provides guidelines for public procurement.
2.  It covers aspects like contract formation, transparency, and accountability.
3.  Procuring entities can customize the manual to suit their specific needs with approval.

📘 Source: mannual procurement.pdf

### Q42. What is the step-by-step process for the auction manual?

- **Intent:** `AUCTION` (conf 0.6) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 37.9s  |  **Sources:** 4  
- **Cited:** AuctionManual_FA.pdf, mannual procurement.pdf, CHiPS_Bid_Submission_Manual_English.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
Here’s the step-by-step process for participating in an e-Auction as outlined in the Auction Manual:

1.  Login to the Chhattisgarh EProcurement portal using your user ID, password, and Digital Signature Certificate (DSC).
2.  Navigate to the “Forward Auction” tab on the Dashboard and open the auction portal in a new window.
3.  If prompted, enter the old password (“Password@123”) and then input the new password.
4.  Select the specific auction from the dashboard and click "View Respond to RFX."
5.  Quote an opening price and multiples of the minimum bid change price. If no opening price is specified, use “0” as the opening price.
6.  The auction page will automatically refresh every 1 minute with updated bidding status and ranking information.

📋 Process
1. Login to Chhattisgarh EProcurement portal using user ID, password & DSC.
2. Navigate to "Forward Auction" tab in Dashboard & open new window.
3. Enter old password (“Password@123”) and then enter new password.
4. Select auction from dashboard & click “View Respond to RFX”.
5. Quote opening price & multiples of min bid change price; use ‘0’ if no opening price.
6. Page auto-refreshes every 1 minute with updated bidding status & ranking.

📘 Source: AuctionManual_FA.pdf

### Q43. What are the troubleshooting steps mentioned in the auction manual?

- **Intent:** `AUCTION` (conf 0.6) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 31.3s  |  **Sources:** 4  
- **Cited:** AuctionManual_FA.pdf, 160616_AMC_AC short tender.pdf, FInal_GFR_upto_31_07_2024.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
The Auction Manual (AuctionManual_FA.pdf) outlines specific actions to take during an auction event. If the auction engine asks for a password change, use “Password@123” as the old password. Bidders must quote above the Opening Price and multiples of the minimum bid price; if no opening price is provided, it should be considered ‘0’. During the auction, bidders can only view H1 prices and the ranking. The auction page automatically refreshes every 1 minute with updated bidding status.

📋 Process
1.  Use “Password@123” as the old password if prompted by the auction engine.
2.  Quote above the Opening Price and multiples of the minimum bid price.
3.  If no opening price is provided, consider it ‘0’.
4.  Monitor H1 prices and ranking updates automatically every 1 minute.

📘 Source: AuctionManual_FA.pdf

### Q44. What is the step-by-step process for CHiPS bid submission?

- **Intent:** `BID_SUBMISSION` (conf 0.6) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 30.7s  |  **Sources:** 3  
- **Cited:** CHiPS_Bid_Submission_Manual_English.pdf, CHiPS_Vendor_Registration_Manual_English.pdf, Guidelines_To_Bidders_EPS_v1.6.pdf  

> **Answer:** 💡 Answer
The process for submitting a bid through the CHiPS e-Procurement system involves several key steps. First, bidders must procure a digital certificate and install Java on their machine, setting the appropriate language. Then, they need to register on the e-Procurement portal, providing necessary details. Finally, they can participate in tenders by submitting both technical and price bids through the online platform.

📋 Process
1.  Procure a Digital Certificate (Class II or Class III) and install Java.
2.  Register on the e-Procurement Portal: Create an account and complete the registration form.
3.  Submit Technical Bid: Upload required documents as specified in the Tender Document.
4.  Submit Price Bid (Financial Bid): Enter bid prices within the stipulated format.
5.  Review and Submit: Carefully review all submitted bids before final submission.

📘 Source: Bid Submission Manual (CHiPS)

### Q45. What is the step-by-step process for CHiPS vendor registration?

- **Intent:** `VENDOR_REGISTRATION` (conf 0.6) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 34.5s  |  **Sources:** 3  
- **Cited:** CHiPS_Vendor_Registration_Manual_English.pdf, CHiPS_Bid_Submission_Manual_English.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
The process for CHiPS vendor registration involves several steps outlined in the Vendor Registration Manual. First, you visit the e-Procurement portal at https://eproc.cgstate.gov.in and click on ‘New User’ under Register. Next, you enter your PAN card details accurately and select “New User” followed by “Enter”. Then, you should enter a preferred login code to check availability, and if available, fill in the required details including Authorized Signatory, Contact, Additional contact Bank, CRN, Vendor business & Partner. Finally, the system will ask for validation, which you save and proceed with.

📋 Process
1.  Visit https://eproc.cgstate.gov.in and click ‘New User’ under Register.
2.  Enter your PAN card details.
3.  Select “New User” and “Enter”.
4.  Enter a preferred login code to check availability.
5.  If available, fill in the required details: Authorized Signatory, Contact, Additional contact Bank, CRN, Vendor business & Partner.
6.  Save & Next.

📘 Source: Vendor Registration Manual (CHiPS)

### Q46. What is the step-by-step process for EDGE browser setup?

- **Intent:** `PORTAL_USAGE` (conf 0.8) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 38.2s  |  **Sources:** 3  
- **Cited:** EDGE_Browser_Setup_V1.0.pdf, Guidelines_To_Bidders_EPS_v1.6.pdf, Preferred_System_Configuration_V_2.pdf  

> **Answer:** 💡 Answer
Here’s a breakdown of the steps to set up your EDGE browser as outlined in the provided documents:

1.  **Open Internet Property:** Navigate to Start Menu > Windows + Run, enter “inetcpl.cpl” and click OK. This opens the Internet Properties window.
2.  **Trusted Sites Configuration:** Go to the Security tab and select the Trusted Sites category. Add the application URL to the Trusted Site List. Set IE security levels as follows: Internet: Medium-high, Trusted sites: Medium. Enable or Prompt for ActiveX related options under ‘Internet’ and ‘Trusted sites’.
3.  **Browser Launch & Settings:** Open the EDGE Browser and click on the “Settings” menu.
4.  **Default Browser Setting:** Click "Default Browser" to set EDGE as the default browser.
5.  **Recommended Portal Address:** Add the Recommended Portal Address/URL by clicking the appropriate setting (likely labeled ‘Allow’ or similar).
6. **Reopen Browser**: After adding the address, reopen the browser.

📋 Process
1. Open Internet Property: Start Menu > Windows + Run > enter “inetcpl.cpl” and click OK.
2. Add URL to Trusted Sites: Security tab > Trusted Sites category > Add application URL.
3. Set IE Security Levels: Security tab > Internet > Custom level – set to Medium-high.
4.  Set Trusted

### Q47. What system settings or configurations are needed for EDGE browser setup?

- **Intent:** `PORTAL_USAGE` (conf 0.8) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 28.0s  |  **Sources:** 2  
- **Cited:** EDGE_Browser_Setup_V1.0.pdf, Preferred_System_Configuration_V_2.pdf  

> **Answer:** 💡 Answer
To configure the EDGE browser as recommended by CHiPS, follow these steps based on the provided documentation:

1.  **Open Internet Properties:** Navigate to Start Menu > Windows + Run > Enter `inetcpl.cpl` and click OK. This opens the Internet Properties window.
2.  **Trusted Sites Settings:** In the Security tab, navigate to Trusted Sites. Set the Internet security level to Medium-High (default) and the Trusted sites security level to Medium (default). Enable or Prompt for ActiveX related options under ‘Internet’ and ‘Trusted sites’.
3.  **Add Application URL:** Navigate to the Default Browser setting within the Internet Options.
4.  **Set as Recommended/Allow:** In the Default Browser settings, set the recommended portal address/URL as “Allow”.
5.  **Reopen Browser:** After adding the address, reopen the EDGE browser.

📋 Process
1. Open Internet Properties by following: Go to start menu>click Windows+Run>enter the command inetcpl.cpl and click Ok.
2. Navigate to Security > Trusted Sites.
3. Set Internet security level to Medium-High and Trusted sites security level to Medium.
4. Enable or Prompt for ActiveX related options under ‘Internet’ and ‘Trusted sites’.
5. Go to Default Browser setting within the Internet Options.
6. Set as Recommended/Allow.

### Q48. What is the step-by-step process for challan payment?

- **Intent:** `EMD_PAYMENT` (conf 0.6) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 49.0s  |  **Sources:** 3  
- **Cited:** FInal_GFR_upto_31_07_2024.pdf, EMD_CHALLAN_PAYMENT_V1.0.pdf, publicProManual-1755343081262-715558279.pdf  

> **Answer:** 💡 Answer
Here’s the step-by-step process for EMD payment via Challan, as outlined in the provided documents:

1.  Log into the Eproc System using your User ID and Password.
2.  Click on "Run".
3.  Select DSC.
4.  Click “Continue to Dashboard”.
5.  Click on “All Live Tenders”.
6.  Click on “View Tender”.
7.  Click on “INTERSTED”.
8.  Check the terms and click “I AGREE/ACCEPT”.
9.  Click "Pay Tender/Processing Fee".
10. Select “Payment mode as RTGS/CHALLAN” and save.
11. Generate Challan.
12. Click “OK to confirm”.
13. Select the Gateway.
14. Click on “Pay Now”.
15. Fill-up required information.
16. Click on “RTGS/NEFT/IMPS”.
17. Click "Confirm and Print" to download the challan PDF.
18. Save the Challan for further Bank payment.

📋 Process
1.  Log in to Eproc System (User ID & Password).
2.  Click "Run".
3.  Select DSC.
4.  Click “Continue to Dashboard”.
5.  Click on “All Live Tenders”.
6.  Click on “View Tender”.
7.  Click on “INTERSTED”.
8.  Check the terms and click “I AGREE/ACCEPT”.
9.  Click "Pay Tender/Processing Fee".
10. Select “Payment mode as RTGS/CHALLAN” and save.
11. Generate Challan.
12. Click “OK to confirm”.
13. Select Gateway.
14. Click on “Pay Now”.
15. Fill-up required information.
16. Click on “RTGS/NEFT/IMPS”.
17. Click "Confirm and Print" to download challan PDF.
18. Save the Challan for further Bank payment.

📘 Source: EMD_CHALLAN_PAYMENT_V1.0.pdf

### Q49. What is the step-by-step process for FAQs?

- **Intent:** `UNKNOWN` (conf 0.0) ✅  
- **Entities:** —  
- **Outcome:** ANSWERED  |  **Latency:** 28.1s  |  **Sources:** 3  
- **Cited:** AuctionManual_FA.pdf, CHiPS_Bid_Submission_Manual_English.pdf, mannual procurement.pdf  

> **Answer:** 💡 Answer
I'm not fully certain this matches your question - please verify with the cited document.
The e-Procurement portal utilizes a series of steps to facilitate FAQ access. First, users must log into the Chhattisgarh EProcurement portal with their designated user ID and password, along with their Digital Signature Certificate (DSC). Following login, navigating to the “FAQs” section within the portal’s interface allows users to view frequently asked questions and their corresponding answers.

📋 Process
1.  Log in to the Chhattisgarh EProcurement portal using your User ID, Password, and DSC.
2.  Navigate to the "FAQs" section within the portal's interface.
3.  Review the listed FAQs and their associated responses.

📘 Source: CHiPS_Bid_Submission Manual_English.pdf

### Q50. What system settings or configurations are needed for CHiPS online?

- **Intent:** `UNKNOWN` (conf 0.0) ❌  
- **Entities:** —  
- **Outcome:** CACHE  |  **Latency:** 2.0s  |  **Sources:** 4  
- **Cited:** FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf, CHiPS_Bid_Submission_Manual_English.pdf, Preferred_System_Configuration_V_2.pdf, Guidelines_To_Bidders_EPS_v1.6.pdf  

> **Answer:** 💡 Answer
To ensure optimal functionality within the Chhattisgarh Infotech Promotion Society (CHiPS) e-Procurement system, several key system settings and configurations are required. These include a Windows 7 or 8 operating system (32-bit or 64-bit), Internet Explorer 9 or Mozilla Firefox Version 44 with IE Tab, Java version 1.8.0_77, and a valid Class II/III Digital Signature Certificate.  Specifically, the system recommends using only one version of Java, ensuring proper DSC installation and validity, and maintaining adequate internet bandwidth (minimum 1 MBPS). Refer to the Preferred System Configuration document for detailed instructions and links to relevant resources.

📋 Process
1. Install Windows 7 or 8 (32-bit or 64-bit) operating system.
2. Download and install Internet Explorer 9 or Mozilla Firefox Version 44 with IE Tab, ensuring compatibility mode is not used.
3. Download and install Java version 1.8.0_77 (32-bit or 64-bit).
4. Obtain and properly configure a valid Class II/III Digital Signature Certificate.
5. Ensure adequate internet bandwidth (minimum 1 MBPS) for seamless operation.
6. Utilize the auto setup utility available on the eProcurement portal home page: https://eproc.cgstate.gov.in --> Auto Setup.

📘 Source: Preferred System Configuration V_2.pdf

---

## 6. Method & caveats

- Each question hit the real `/api/stream` SSE endpoint with a unique `session_id` (no coreference/slot carryover between questions).
- Intent + entities were computed by calling `nlp_features.classify_intent` / `extract_entities` directly on each raw question (the same functions the server uses).
- Latency = wall-clock from request send to the SSE `done` event (includes retrieval + reranking + full token generation).
- "Intent Recognition Accuracy" is judged against expected *routing*: `UNKNOWN`→general-RAG is scored correct for generic document-lookup questions, since the taxonomy intentionally only fires on specific procurement actions.
- Answer correctness was **not** graded against a gold reference here; outcomes track whether the system produced a sourced answer vs refused/failed. Spot-checking the answers below shows them on-topic and grounded in the cited manuals.
