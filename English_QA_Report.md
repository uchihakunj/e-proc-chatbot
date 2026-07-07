# English QA Report — e-Procurement Chatbot

**Test:** 5 English questions per document x 25 documents = 125 questions.
**Method:** each question sent to the live `/api/stream` RAG endpoint; recorded the
retrieved document(s), whether the expected source was in the top-5, the answer language,
and the answer text.

**Overall:** correct-source **83/125 (66%)**  |  English-answer **125/125 (100%)**  |  false-refusals **5**

## Per-document scorecard

| # | Document | Correct-source | English |
|---|---|---|---|
| 1 | Short-term tender transparency | 5/5 | 5/5 |
| 2 | AMC / AC short tender | 3/5 | 5/5 |
| 3 | e-Auction Manual | 1/5 | 5/5 |
| 4 | CVC Circulars & Guidelines | 5/5 | 5/5 |
| 5 | Corrigendum Instructions | 3/5 | 5/5 |
| 6 | EDGE Browser Setup | 5/5 | 5/5 |
| 7 | EMD Challan Payment | 3/5 | 5/5 |
| 8 | CHiPS FAQ | 4/5 | 5/5 |
| 9 | GFR (Final upto 2024) | 4/5 | 5/5 |
| 10 | GFR 2017 (Hindi) | 4/5 | 5/5 |
| 11 | GFR (updated 2026) | 5/5 | 5/5 |
| 12 | Guidelines to Bidders (EPS) | 3/5 | 5/5 |
| 13 | Offline Tenders Manual | 0/5 | 5/5 |
| 14 | Procurement of Works 2019 | 4/5 | 5/5 |
| 15 | EMD Refund Notice | 5/5 | 5/5 |
| 16 | PEF | 1/5 | 5/5 |
| 17 | PPM 00002 | 4/5 | 5/5 |
| 18 | Preferred System Configuration | 4/5 | 5/5 |
| 19 | Precis e-Procurement Project | 1/5 | 5/5 |
| 20 | Vigilance Manual (English) | 4/5 | 5/5 |
| 21 | Vigilance Manual (Hindi) | 5/5 | 5/5 |
| 22 | Public Procurement Manual (mannual) | 5/5 | 5/5 |
| 23 | Procurement of Goods (publicProManual) | 5/5 | 5/5 |
| 24 | Short Tender Notice (2 days) | 0/5 | 5/5 |
| 25 | Store Purchase Rules (CG) | 0/5 | 5/5 |

## Scope-gate false refusals (answered in <1s with no retrieval)

- Q40 [CHiPS FAQ]: "What is a Digital Signature Certificate as per the FAQ?"
- Q77 [PEF]: "What information does the PEF form capture?"
- Q79 [PEF]: "What fields are part of the PEF?"
- Q85 [PPM 00002]: "What approval levels are defined in the PPM?"
- Q97 [Vigilance Manual (English)]: "Within what time should a decision on the inquiry report be taken?"

## Detailed results — all 125 questions

### Short-term tender transparency — 5/5 correct-source

- **Q1 [OK] [EN] [75.14s]** What are the rules for transparency in short term tenders?
  - top source: 11.02.2004 transp in short term tender
  - answer: 💡 Answer: The rules for transparency in short-term tenders can be inferred from various sources. Firstly, the Commission's circular (No.98/ORD/1 dated 18.12.2003) emphasizes the importance of transparency and recommends that notices be put on the web-site of the departments. This suggests that all information related to the tender should be publicly accessible.  Additionally, the manual for procurement of goods (Seco
- **Q2 [OK] [EN] [53.81s]** When can a short term tender be used instead of open tender?
  - top source: 11.02.2004 transp in short term tender
  - answer: 💡 Answer: A short term tender can be used instead of an open tender under the following conditions:  1. There is an urgent need for the work and engaging in competitive tendering process would, therefore, be impractical. 2. The circumstances giving rise to the urgency were neither foreseeable by the procuring entity nor the result of dilatory conduct on its part. 3. The procurement entity engages in procurement invol
- **Q3 [OK] [EN] [46.87s]** What is the notice period for a short term tender?
  - top source: mannual procurement
  - answer: 💡 Answer: The notice period for a short-term tender can be put on the web-site of the department, which does not take any time compared to giving advertisements in newspapers and practically does not cost anything. This will benefit the department by bringing in transparency and reducing opportunities for abuse of power.  📋 Process:  * The practice of short-term tenders is understandable due to the cost and time invo
- **Q4 [OK] [EN] [53.79s]** What conditions must be met for short term tendering?
  - top source: mannual procurement
  - answer: 💡 Answer: The conditions that must be met for short-term tendering are:  1. There is an urgent need for the work and engaging in competitive tendering process would be impractical. 2. The circumstances giving rise to the urgency were neither foreseeable by the procuring entity nor the result of dilatory conduct on its part. 3. The incremental work should not be more than 25% of the original contract value.  These con
- **Q5 [OK] [EN] [43.41s]** How should short term tenders ensure transparency?
  - top source: mannual procurement
  - answer: 💡 Answer Short-term tenders can ensure transparency by putting notice on the department's website, as per the instructions given in the Commission's circular. This method does not take any time and practically does not cost anything.  📋 Process 1. Put notice on the department's website. 2. Follow the instructions given in the Commission's circular (No. 98/ORD/1 dated 18.12.2003).  📘 Source: Compilation of CVC Circula

### AMC / AC short tender — 3/5 correct-source

- **Q6 [OK] [EN] [74.34s]** What is the procedure for an AMC short tender?
  - top source: 160616_AMC_AC short tender
  - answer: 💡 Answer:  The procedure for an AMC short tender involves the following steps:  1. Review of eligibility criteria: The bidder must ensure that they meet the pre-qualification requirements specified in the tender document, including having a minimum 3 years of experience in dealing with air conditioners and having previous AMC work experience with a government department or public sector undertaking. 2. Submission of 
- **Q7 [MISS] [EN] [50.29s]** How is an Annual Maintenance Contract tender processed?
  - top source: publicProManual
  - answer: 💡 Answer: An Annual Maintenance Contract (AMC) tender is processed as follows:  📋 Process:  1. The purchase organisation may enter into a maintenance contract for proper maintenance of goods, especially sophisticated equipment and machinery. 2. The primary intention is the procurement of goods with services being incidental to it. 3. If the primary intention is the procurement of works/services with procurement of go
- **Q8 [MISS] [EN] [49.06s]** What is the tender process for air conditioner maintenance?
  - top source: publicProManual
  - answer: 💡 Answer: The tender process for air conditioner maintenance involves floating a separate tender enquiry for this purpose and evaluating tenders accordingly. The details of services required, payment terms, and other relevant conditions are to be incorporated in the tender enquiry document. The maintenance contract may be entered into with the OEM manufacturer/supplier or a competent and eligible firm.  📋 Process:  1
- **Q9 [OK] [EN] [49.37s]** What are the timelines for an AMC short tender?
  - top source: 160616_AMC_AC short tender
  - answer: 💡 Answer: The timelines for an AMC short tender are as follows:  * The condition of Air Conditioners can be inspected at NIELIT's Office in Electronics Niketan between 10:00 hrs to 16:30 hrs up to 01.07.2016 on any working day. * The sealed cover containing technical & commercial Bids should be addressed to the Deputy Director (Civil), NIELIT, HQ, Electronics Niketan, 6, CGO Complex, Lodhi Road, New Delhi-10003 and r
- **Q10 [OK] [EN] [51.80s]** What documents are needed for an AMC tender?
  - top source: 160616_AMC_AC short tender
  - answer: 💡 Answer: The following documents are required for an AMC tender:  1. Technical Bid 2. Commercial Bid 3. Declaration Form (Annexure-A) 4. Earnest Money Deposit (EMD) in the form of Demand Draft drawn on any nationalized bank in favor of NIELIT payable at New Delhi.  📋 Process: The bidder should submit their offer in two parts: 'Technical Bid' and 'Commercial Bid'. The Technical Bid should be submitted along with the 

### e-Auction Manual — 1/5 correct-source

- **Q11 [MISS] [EN] [52.45s]** How does a bidder participate in an e-auction?
  - top source: CHiPS_Bid_Submission_Manual_English
  - answer: 💡 Answer:  To participate in an e-auction, a bidder can follow these steps:  1. Register with the e-Auction Service Provider (eASP) and obtain a login ID and password. 2. Browse through the auction catalogue to find the items they are interested in bidding on. 3. Read the terms and conditions of each item carefully, including any special conditions or reserve prices. 4. Place a bid by entering their maximum price and
- **Q12 [OK] [EN] [69.59s]** What is the process of forward auction on the portal?
  - top source: AuctionManual_FA
  - answer: 💡 Answer: The process of forward auction on the portal involves the following steps:  1. Registration and Creation of Auction Event by the Government Agency: The role of the Government Agency Seller is called Forward Auction Seller/Auctioneer (FA-SA). All buyers registered on GeM shall have the option to auto-enrol as FA-SA on the Forward Auction Platform. 2. Participation by FA-BB: FA-BB can log in to the GeM portal
- **Q13 [MISS] [EN] [49.11s]** How is the start price set in an e-auction?
  - top source: publicProManual
  - answer: 💡 Answer: The start price in an e-auction is set as the L-1 landed price in the financial bid (as per the calculation schema based on the Tender Document evaluation criteria) unless modified by the procuring Entity.  📋 Process:  * The Procuring Entity specifies the decrement value before starting the e-Reverse Auction. * The reduction in bids shall have to be made as per decrement value or in multiple thereof. * An i
- **Q14 [MISS] [EN] [52.41s]** How does automatic bid extension work in an e-auction?
  - top source: publicProManual
  - answer: 💡 Answer: Automatic bid extension in an e-auction works as follows:  * If the auction closes without a winning bidder due to low competition, the system automatically extends the closing time by a specified number of days. * The system declares that the tender closing time has been extended up to (date and time). * This automatic extension is done only once, not repeatedly. * The most favorable bid at the end of the 
- **Q15 [MISS] [EN] [47.24s]** How is the winning bid decided in an e-auction?
  - top source: publicProManual
  - answer: 💡 Answer:  The winning bid in an e-auction is decided through a reverse auction process. The system automatically generates a technical scrutiny report and commercial scrutiny report for techno-commercial bids, and a price comparative statement for price bids. The bid openers download the bids and reports/statements and sign them for further processing.  📋 Process:  The winning bid is determined by the lowest bidder 

### CVC Circulars & Guidelines — 5/5 correct-source

- **Q16 [OK] [EN] [55.46s]** What do the CVC guidelines say about mobilization advance?
  - top source: Compilation of CVC Circulars and Guidelines
  - answer: 💡 Answer:  The CVC guidelines state that provision of mobilization advance should essentially be need-based. Suitable delegation of authority may be done in the Organisation to take decision for grant of the mobilisation advance, whether interest-free or interest-bearing.  📋 Process:  1. The amount of mobilization advance, interest to be charged (if any), its recovery schedule, and other relevant details should be ex
- **Q17 [OK] [EN] [45.37s]** What does CVC recommend about reverse auctions in e-procurement?
  - top source: publicProManual
  - answer: 💡 Answer: The Central Vigilance Commission (CVC) recommends that the entire process of e-procurement/reverse auction be conducted in a transparent and fair manner. The CVC does not provide specific guidelines on the use of reverse auctions, but rather emphasizes the importance of transparency and fairness in the procurement process.  📋 Process: There is no specific process mentioned by the CVC regarding the use of re
- **Q18 [OK] [EN] [48.20s]** What is the role of the Chief Technical Examiner per CVC?
  - top source: Compilation of CVC Circulars and Guidelines
  - answer: 💡 Answer: The role of the Chief Technical Examiner (CTE) as per CVC is to provide assistance and advice to the Commission on technical matters and issues relating to procurement. The CTE Organisation, headed by the Chief Technical Examiners, carries out inspection of civil, electrical, and horticulture works of Central Government Departments, Central Public Sector Enterprises, PSBs, and FIs, etc.  📋 Process:  The CTE
- **Q19 [OK] [EN] [49.12s]** What do CVC circulars say about e-payment and e-receipt?
  - top source: Compilation of CVC Circulars and Guidelines
  - answer: 💡 Answer: The Central Vigilance Commission (CVC) circulars emphasize the importance of leveraging technology for efficient payment and receipt systems. They provide guidelines for implementing electronic payment (e-payment) and electronic receipt (e-receipt) systems in government departments and organizations.  📋 Process:  * The CVC instructs that 50% of payment transactions should be made through ECS/EFT mechanism b
- **Q20 [OK] [EN] [43.65s]** What does CVC say about Bank Guarantees against advances?
  - top source: Compilation of CVC Circulars and Guidelines
  - answer: 💡 Answer: The Central Vigilance Commission (CVC) recommends that while making any advance payment, adequate safeguards in the form of a bank guarantee (or e-Bank Guarantee of at least 110% of advance) should be obtained from the firm. In case the advances are to be paid/recovered in instalments, an equal number of part BGs (with proportionate amount and validity) may be taken instead of lumpsum BG, with each BG relea

### Corrigendum Instructions — 3/5 correct-source

- **Q21 [MISS] [EN] [48.86s]** How is a corrigendum to a tender issued on the portal?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: A corrigendum to a tender is issued on the portal by notifying all known prospective bidders in writing through registered post/speed post/courier/email. The corrigendum shall also be published on the CPPP.  📋 Process:  1. At any time prior to the date of submission of bids, the Procuring Entity may amend bid documents by issuing a corrigendum. 2. The corrigendum is notified in writing by registered post/sp
- **Q22 [OK] [EN] [55.95s]** Who can publish a corrigendum for a tender?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: The Tender owner/Department user or the Procuring Entity may publish a corrigendum for a tender.  📋 Process:  * The Tender owner/Department user logs in via their user credentials. * They search for the tender and click on "Go to RFQ" to access the corrigendum issuance page. * They can issue one or more than one corrigendum, selecting the relevant options (e.g., EMD/BID SECURITY, ITEM CORRIGENDUM). * The sy
- **Q23 [OK] [EN] [58.29s]** How are bidders notified about a corrigendum?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: Bidders are notified about a corrigendum through various means. According to the sources provided, bidders can be notified via:  * Registered post/speed post/courier/email * Publication on the CPPP (Central Public Procurement Portal) * Uploading on the procuring entity's own website  Additionally, the system will mandatorily delete any already submitted bids after issuance of certain types of corrigendums, 
- **Q24 [OK] [EN] [54.47s]** Can the bid due date be changed through a corrigendum?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: Yes, the bid due date can be changed through a corrigendum. According to the sources provided, if an amendment/modification changes the requirement significantly and/or when there is not much time left for the bidders to respond to such amendments, it is better to prepare a revised tender and extend the time and date of submission of tenders suitably (not less than 3 days).  📋 Process: The process involves 
- **Q25 [MISS] [EN] [50.24s]** What is the process for amending tender documents?
  - top source: mannual procurement
  - answer: 💡 Answer The Procuring Entity may amend bid documents by issuing a corrigendum at any time prior to the date of submission of bids. The corrigendum shall be notified in writing by registered post/speed post/courier/email to all known prospective bidders and published on CPPP.  📋 Process  1. At any time prior to the date of submission of bids, the Procuring Entity may amend bid documents by issuing a corrigendum. 2. T

### EDGE Browser Setup — 5/5 correct-source

- **Q26 [OK] [EN] [51.07s]** How do I set up Microsoft Edge for the e-procurement portal?
  - top source: EDGE_Browser_Setup_V1.0
  - answer: 💡 Answer:  To set up Microsoft Edge for the e-procurement portal, follow these steps:  1. Open Microsoft Edge and click on the three horizontal lines () at the top right corner of the browser window. 2. Click on "Settings" from the dropdown menu. 3. Scroll down to the "Default browser" section and select "Microsoft Edge" as your default browser.  📋 Process:  * Step 1: Open Microsoft Edge * Step 2: Click on the three 
- **Q27 [OK] [EN] [49.32s]** What settings are needed in Edge to use the portal?
  - top source: EDGE_Browser_Setup_V1.0
  - answer: 💡 Answer:  To use the portal with Microsoft Edge browser, you need to configure the following settings:  1. Open Internet Properties by following these steps: 	* Go to Start menu > click Windows+Run > enter the command `inetcpl.cpl` and click OK 2. Add the application URL to the Trusted Site List (Security > Trusted Sites) 3. Set the IE security levels as follows: 	* Internet: Medium-high (default) 	* Trusted sites: 
- **Q28 [OK] [EN] [46.68s]** How do I enable IE mode in Edge for the portal?
  - top source: EDGE_Browser_Setup_V1.0
  - answer: 💡 Answer:  To enable IE mode in Edge for the portal, follow these steps:  📋 Process:  1. Open the EDGE Browser. 2. Click on the three horizontal lines () at the top right corner of the browser to open the settings menu. 3. Click on "Settings" from the dropdown menu. 4. Scroll down to the "Advanced" section and click on it. 5. Under the "IE mode" section, toggle the switch to enable IE mode.  📘 Source:  * EDGE_Browser
- **Q29 [OK] [EN] [45.65s]** What browser configuration is required for digital signing?
  - top source: EDGE_Browser_Setup_V1.0
  - answer: 💡 Answer:  The preferred browser configuration for digital signing is:  * Internet Explorer 9 * Mozilla Firefox Version 44 with IE Tab Add-on * Google Chrome Version 48 with IE Tab Extension  📋 Process:  1. Ensure that the browser is set to use the correct compatibility mode. 2. Enable the "Include Local Directory Path" option when uploading files to a server (available in Internet Explorer). 3. Set the browser's sec
- **Q30 [OK] [EN] [48.83s]** How to add the portal to trusted sites in Edge?
  - top source: EDGE_Browser_Setup_V1.0
  - answer: 💡 Answer:  To add the portal to trusted sites in Edge, follow these steps:  📋 Process:  1. Open Internet Properties by following the steps: 	* Go to Start menu > click Windows+Run > enter the command `inetcpl.cpl` and click OK. 2. In the Internet Properties window, navigate to the "Security" tab. 3. Click on the "Trusted sites" zone and select the "Sites" button. 4. Add the portal URL (`https://eprocdemo.cgstate.gov.

### EMD Challan Payment — 3/5 correct-source

- **Q31 [OK] [EN] [53.27s]** How is the EMD paid online through challan?
  - top source: EMD_CHALLAN_PAYMENT_V1.0
  - answer: 💡 Answer: The EMD (Earnest Money Deposit) can be paid online through challan by following these steps:  1. Log in to the e-Procurement portal and select the relevant tender. 2. Click on the "Document(s) > Payment > Add" option. 3. Select the payment type as "EMD/BID SECURITY". 4. Choose the payment mode as "ONLINE" (RTGS/CHALLAN). 5. Enter the required details, including the amount and currency type (INR). 6. Review 
- **Q32 [MISS] [EN] [41.56s]** What payment options are available for EMD?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: The payment options available for Earnest Money Deposit (EMD) include:  * Insurance Surety Bonds * Account payee demand draft * Banker's cheque * Bank guarantee (including e-bank guarantee) * Payment online in an acceptable form  📘 Source: Sources 1, 2, and 3: Chhattisgarh Infotech Proméning the Government Procurement Assistant
- **Q33 [MISS] [EN] [53.72s]** How long does EMD payment verification take?
  - top source: publicProManual
  - answer: 💡 Answer:  The time taken for EMD payment verification is not explicitly mentioned in the provided sources. However, it can be inferred that the process of verifying bank guarantees submitted by bidders/contractors against EMD/performance security/advance payments and for various other purposes involves obtaining confirmation from the issuing branch of the bank in writing through registered post/speed post/courier. T
- **Q34 [OK] [EN] [47.01s]** How do I generate an EMD challan on the portal?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: To generate an EMD challan on the portal, follow these steps:  1. Log in to your account on the e-procurement portal. 2. Click on "Document(s) > Payment > Add" to access the payment interface. 3. Select the relevant tender number (in this case, 9021 - [ ONLINE EMD CHALLAN PAYMENT ]). 4. Fill in the required details, including the amount and currency type. 5. Choose the payment mode as RTGS/CHALLAN or Intern
- **Q35 [OK] [EN] [46.73s]** Can EMD be paid via NEFT or RTGS?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: Yes, EMD can be paid via NEFT or RTGS. According to [Source 3: EMD_CHALLAN_PAYMENT_V1.0.pdf], if EMD/Bid Security is paid using eChallan payment option and it does not get credited to the Beneficiary/Recipient Account within Bid Due Date, then the amount will be refunded back to the source account & in such a scenario it will be deemed accepted that the bidder has not paid the EMD / Bid Security & according

### CHiPS FAQ — 4/5 correct-source

- **Q36 [OK] [EN] [47.72s]** What is required to register on the CHiPS portal?
  - top source: CHiPS_Vendor_Registration_Manual_English
  - answer: 💡 Answer: To register on the CHiPS portal, a vendor needs to procure a digital certificate (Class II or Class III), install Java in their machine, and set the language for proper functioning of the module. Additionally, they need to provide their PAN details if registered with PWD.  📋 Process:  1. Register on the CHiPS portal by clicking on the "new user" link. 2. Provide PAN details if registered with PWD. 3. Procur
- **Q37 [OK] [EN] [56.78s]** What are the frequently asked questions about e-procurement?
  - top source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS)
  - answer: 💡 Answer: The frequently asked questions about e-procurement include:  * What is E-Procurement? * How do I register in the portal? * How do I login in to the portal? * Is it possible to edit my profile details after registration? * What types of business entities can get registered in the eProcurement portal? * What types of vendors can get registered in the eProcurement portal?  These questions are addressed in vari
- **Q38 [OK] [EN] [53.17s]** How do I recover my password on the portal?
  - top source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS)
  - answer: 💡 Answer: To recover your password on the portal, you can follow these steps:  1. Click on "Password Recovery using EMAIL" or "Password Recovery Using DSC or OTP". 2. Enter your User ID and registered Email address or Mobile number. 3. Validate using your Digital Certificate (DSC) or One-Time Password (OTP). 4. Follow the prompts to create a new password.  Alternatively, you can also use the "Change Password" option 
- **Q39 [OK] [EN] [37.17s]** Whom do I contact for portal support?
  - top source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS)
  - answer: 💡 Answer To get portal support, you can contact the Helpdesk Team at helpdesk.eproc@cgswan.gov.in or call 1800 419 9140 (Toll free) from 9.00 AM to 11.00 PM (IST).  📋 Process: None  📘 Source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS)
- **Q40 [REFUSED] [EN] [0.01s]** What is a Digital Signature Certificate as per the FAQ?
  - top source: (none)
  - answer: The answer to this question was not found in the available documents.

### GFR (Final upto 2024) — 4/5 correct-source

- **Q41 [MISS] [EN] [56.64s]** What does GFR say about purchase preference for MSEs?
  - top source: publicProManual
  - answer: 💡 Answer: According to the Government Procurement Policy for Micro and Small Enterprises (MSEs), the Public Procurement (Preference to Make in India) Order 2017, as per Rule 153 (iii) of GFR, 2017, purchase preference is given to 'Class-I local supplier' in procurements undertaken by procuring entities.  📋 Process: The process for giving purchase preference to MSEs involves the following steps:  1. The lowest bid wil
- **Q42 [OK] [EN] [53.47s]** What are the modes of procurement under GFR?
  - top source: publicProManual
  - answer: 💡 Answer: The modes of procurement under GFR are:  * Advertised Modes: These modes aim for the widest possible competition through wide publicity. Examples include Open Tender Enquiry (OTE), Global Tender Enquiry (GTE), Rate Contracts, and Electronic Reverse Auction (eRA) - Dynamic Price Discovery. * Pre-Qualification Modes: These modes are restricted to shortlisted pre-qualified bidders. Shortlisting is done transpa
- **Q43 [OK] [EN] [48.68s]** What does GFR say about earnest money deposit?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: According to the Government Financial Rules (GFR), Earnest Money Deposit (EMD) is referred to as "Bid Security" and is required to safeguard against a bidder's withdrawing or altering its bid during the bid validity period. The amount of bid security should generally be between two to five per cent of the estimated value of the goods to be procured.  📋 Process: The process for obtaining bid security include
- **Q44 [OK] [EN] [52.55s]** What is the role of a tender committee under GFR?
  - top source: publicProManual
  - answer: 💡 Answer: The role of a Tender Committee under GFR is to evaluate tenders and select the best bidder for a procurement. The committee consists of three or more members with requisite experience and competence, including a Financial Adviser or his representative and a representative of the user department. The committee's primary responsibility is to ensure that the evaluation process is fair, transparent, and in acco
- **Q45 [OK] [EN] [42.04s]** What does GFR say about performance security?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: According to the Final_GFR_upto_31_07_2024.pdf source, Performance Security may be furnished in the form of [Insurance Surety Bond]38 Account Payee Demand Draft, Fixed Deposit Receipt from a Commercial bank, Bank Guarantee [including e-Bank Guarantee]39 from a Commercial bank or online payment in an acceptable form safeguarding the purchaser's interest in all respects.  📘 Source: FInal_GFR_upto_31_07_2024.p

### GFR 2017 (Hindi) — 4/5 correct-source

- **Q46 [OK] [EN] [46.57s]** According to GFR, within how many days must a TA claim be submitted?
  - top source: FInal_GFR_upto_31_07_2024
  - answer: 💡 Answer: A claim for overtime allowance shall fall due for payment on first day of the month following the month to which the overtime allowance relates. The claim shall stand forfeited if not submitted within 60 days of the due date.  📋 Process:  * The claim falls due for payment on the first day of the month following the month to which the overtime allowance relates. * The claim must be submitted within 60 days o
- **Q47 [OK] [EN] [47.66s]** What is the purpose of the General Financial Rules 2017?
  - top source: FInal_GFR_upto_31_07_2024
  - answer: 💡 Answer: The purpose of the General Financial Rules 2017 is to provide a framework for budget formulation and implementation, as well as guidelines for preparation of budget estimates. The rules aim to ensure transparency, accountability, and effective management of public finances.  📋 Process: The rules outline the procedures for preparing, formulating, and submitting the budget to Parliament, including the present
- **Q48 [OK] [EN] [60.61s]** What do the GFR say about advance payments to suppliers?
  - top source: FInal_GFR_upto_31_07_2024
  - answer: 💡 Answer: According to the Government Procurement Rules (GFR), advance payments to suppliers should be made only when necessary and with adequate safeguards. The GFR specify that advance payments should not exceed 30% of the contract value for private firms, 40% for state or central government agencies or public sector undertakings, or the amount payable for six months under a maintenance contract.  📋 Process: The pr
- **Q49 [OK] [EN] [48.47s]** What does GFR provide regarding bid security?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: The Government Procurement Rules (GFR) provides that to safeguard against a bidder's withdrawing or altering its bid during the bid validity period, Bid Security (also known as Earnest Money) is to be obtained from the bidders except Micro and Small Enterprises (MSEs) as defined in MSE Procurement Policy issued by Department of Micro, Small and Medium Enterprises (MSME) or are registered with the Central Pu
- **Q50 [MISS] [EN] [59.17s]** What does GFR 2017 say about the purchase preference policy?
  - top source: PPM 00002
  - answer: 💡 Answer: According to GFR 2017, the purchase preference policy is applicable on the procurement of Goods, Works and Services. The policy gives preference to 'Class-I local suppliers' in procurements undertaken by procuring entities. The margin of purchase preference for 'Class-I local suppliers' has been fixed at 20 (twenty) percent.  📋 Process: The process for giving purchase preference to 'Class-I local suppliers'

### GFR (updated 2026) — 5/5 correct-source

- **Q51 [OK] [EN] [54.08s]** What is the latest GFR provision on bid security declaration?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: The latest GFR provision on bid security declaration is not explicitly mentioned. However, according to Rule 170 of the Final_GFR_upto_31_07_2024.pdf, Bid securing declarations can be used as an alternative to bid securities in certain cases.  📋 Process: To safeguard against a bidder's withdrawing or altering its bid during the bid validity period, the following steps can be taken:  1. Obtain bid security f
- **Q52 [OK] [EN] [45.84s]** What does the updated GFR say about e-procurement thresholds?
  - top source: publicProManual
  - answer: 💡 Answer: The updated GFR says that it is mandatory for ministries/departments to receive all bids through e-procurement portals that are GCQE78 compliant for all procurements with an estimated value of Rs. 50 lakhs (Rupees Fifty Lakh) and above.  📋 Process:  * The threshold for using e-procurement is Rs. 50 lakhs (Rupees Fifty Lakh) and above. * Ministries/departments must use GCQE78 compliant e-procurement portals 
- **Q53 [OK] [EN] [56.15s]** What are the GFR rules for limited tender enquiry?
  - top source: FInal_GFR_upto_31_07_2024
  - answer: 💡 Answer: The Government Procurement Rules (GFR) for Limited Tender Enquiry are as follows:  * The demand should be urgent and any additional expenditure involved by not procuring through advertised tender enquiry is justified in view of urgency. * The Ministry or Department should put on record the nature of the urgency and reasons why the procurement could not be anticipated. * There should be sufficient reasons, t
- **Q54 [OK] [EN] [54.01s]** What does GFR say about single tender enquiry?
  - top source: mannual procurement
  - answer: 💡 Answer: According to the Government Procurement Rules (GFR), a Single Tender Enquiry (STE) or Selection by Nomination is allowed under certain conditions. These conditions are:  * Urgent need for the work and engaging in competitive tendering process would be impractical. * Works that represent a natural continuation of previous work carried out by the firm, provided the incremental work does not exceed 25% of the 
- **Q55 [OK] [EN] [60.20s]** What is the GFR rule on rate contracts?
  - top source: FInal_GFR_upto_31_07_2024
  - answer: 💡 Answer:  The Government Procurement Rules (GFR) do not provide specific rules on rate contracts. However, it is mentioned in Rule 225 that "standard forms of contracts should be adopted wherever possible, with such modifications as are considered necessary in respect of individual contracts." This implies that the GFR encourages the use of standard contract formats and procedures to ensure transparency, fairness, a

### Guidelines to Bidders (EPS) — 3/5 correct-source

- **Q56 [OK] [EN] [67.90s]** What are the key guidelines for bidders on the EPS portal?
  - top source: Guidelines_To_Bidders_EPS_v1.6
  - answer: 💡 Answer:  To participate in tenders floated using the Integrated e-Procurement System (EPS) portal, bidders must follow these key guidelines:  1. **Vendor/Bidder Registration**: Register on the centralized portal https://eproc.cgstate.gov.in and get approved for a specific class (e.g., A, B, C, D, UGE, UDE). 2. **Digital Signature Certificates**: Submit bids online signed digitally with a valid Class II/Class III Di
- **Q57 [MISS] [EN] [67.52s]** How should a bidder prepare and upload bid documents?
  - top source: publicProManual
  - answer: 💡 Answer: To prepare and upload bid documents, a bidder should follow these steps:  1. Review the tender document carefully to understand the requirements. 2. Amend the bid documents by issuing a corrigendum if necessary. 3. Prepare the technical bid (Part 1) with all pages serially numbered, including the bid security, power of attorney, qualification information, and other required documents. 4. Prepare the financi
- **Q58 [OK] [EN] [64.29s]** What are the do's and don'ts for online bidding?
  - top source: mannual procurement
  - answer: 💡 Answer: The do's and don'ts for online bidding can be summarized as follows:  DO:  * Register yourself online on the e-procurement portal with a valid DSC. * Obtain a valid Class-II/Class-III Digital Certificate to encrypt bid data during the bid preparation/responding stage. * Make online payment(s) of the Registration fee/Transaction or Service fees/EMD using the online payments gateway services integrated into t
- **Q59 [MISS] [EN] [46.69s]** What file size limits apply when uploading bids?
  - top source: publicProManual
  - answer: 💡 Answer: There is no specific file size limit mentioned in the provided documents for uploading bids. However, it is generally recommended to keep files within reasonable sizes to ensure smooth upload and processing.  📋 Process:  The process of uploading bids typically involves submitting digital copies of bids through an electronic procurement platform or portal. The exact procedures may vary depending on the speci
- **Q60 [OK] [EN] [59.26s]** How does a bidder digitally sign a bid?
  - top source: PPM 00002
  - answer: 💡 Answer:  A bidder digitally signs a bid by uploading scanned copies of various documents required for eligibility and all other documents as specified in NIT, techno-commercial bid in cover-I, and price bid in cover-II. The bidder will have to give an undertaking online that if the information/ declaration/ scanned documents furnished in respect of eligibility criteria are found to be wrong or misleading at any sta

### Offline Tenders Manual — 0/5 correct-source

- **Q61 [MISS] [EN] [51.77s]** How is an offline tender submitted?
  - top source: publicProManual
  - answer: 💡 Answer: Offline tenders can be submitted through various means such as courier services, post, or hand delivery. In case of bulky/oversized bids that cannot be dropped into tender boxes, officials authorized to receive such bids shall maintain proper records and provide a signed receipt with the date and time to the bearer of the bid.  📋 Process: The process for submitting an offline tender involves several steps: 
- **Q62 [MISS] [EN] [48.53s]** When is the offline tender mode used?
  - top source: publicProManual
  - answer: 💡 Answer: The offline tender mode is used under circumstances where exemptions for e-Procurement are provided as per extant instructions. This is done to avoid rush in internet traffic and ensure proper records about the number of tender documents sold, the list of parties to whom sold, details of the amount received through sale, and the number of unsold tender documents.  📋 Process: The procuring entity shall maint
- **Q63 [MISS] [EN] [34.46s]** What is the process for offline tender evaluation?
  - top source: mannual procurement
  - answer: 💡 Answer The process for offline tender evaluation involves evaluating techno-commercial and price bids offline, based on system-generated reports and comparative statements.  📋 Process 1. Evaluation of techno-commercial and price bids is done offline. 2. The evaluation is based on system-generated reports and comparative statements.  📘 Source Sources: [Source 2: Manual_for_Procurement_of_works_2019.pdf], [Source 3: 
- **Q64 [MISS] [EN] [51.44s]** How are offline tender documents handled?
  - top source: mannual procurement
  - answer: 💡 Answer: Offline tender documents are handled by maintaining proper records about the number of tender documents sold, the list of parties to whom sold, details of the amount received through sale, and the number of unsold tender documents. These records are to be cancelled after the opening of the tenders.  📋 Process:  1. The procuring entity shall maintain proper records about the number of tender documents sold. 
- **Q65 [MISS] [EN] [62.46s]** What are the steps in the offline tender manual?
  - top source: mannual procurement
  - answer: 💡 Answer The steps in the offline tender manual include:  * Receipt and custody of bids to maintain transparency and credibility; * Submission of technical and financial proposals at the same time in separate sealed envelopes; * Tender boxes for receiving bids, with two locks and keys held by authorized officials; * Proper records and signed receipts for bulky or oversized bids; * Evaluation of techno-commercial and 

### Procurement of Works 2019 — 4/5 correct-source

- **Q66 [OK] [EN] [49.84s]** What is bid security as per the Manual for Procurement of Works?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: Bid Security, also known as Earnest Money Deposit (EMD), is a security deposit obtained from bidders to safeguard against their withdrawing or altering their bids during the bid validity period. It is typically required for advertised and limited tender enquiries.  📋 Process: The amount of bid security should generally range between two to five percent of the estimated value of the goods to be procured, as 
- **Q67 [OK] [EN] [52.98s]** What is the performance security requirement for works contracts?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: The performance security requirement for works contracts is to be obtained from the successful bidder awarded the contract. The amount of performance security should be five percent of the value of the contract.  📋 Process:  * Performance security may be furnished in the form of an account payee demand draft, fixed deposit receipt from a commercial bank, bank guarantee issued/confirmed from any of the comme
- **Q68 [MISS] [EN] [65.50s]** How is the lowest bidder determined for works?
  - top source: PPM 00002
  - answer: 💡 Answer: The lowest bidder is determined as follows:  Among all qualified bids, the lowest bid will be termed as L1. If L1 is a 'Class-I local supplier', the contract for full quantity will be awarded to L1.  If L1 bid is not a 'Class-I local supplier', 50 (fifty) percent of the order quantity shall be awarded to L1. Thereafter, the lowest bidder among the 'Class-I local suppliers' will be invited to match the L1 pr
- **Q69 [OK] [EN] [55.52s]** What is the retention money in a works contract?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: The retention money in a works contract is usually five percent of each running bill (periodic/interim payment) to be withheld as Security Deposit/retention money until final acceptance. The earnest money instead of being released may form part of the security deposit.  📋 Process:  * The contractor may, at his option, replace the retention amount with an unconditional Bank Guarantee (BG) from a bank accepta
- **Q70 [OK] [EN] [47.33s]** What is the defect liability period in works procurement?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: The Defects Liability Period in Works Procurement:  According to the sources provided, the Defects Liability Period is specified as two years. This period may be mentioned in the Agreement to provide additional comfort to the Procuring Entity.  📋 Process: No specific process is mentioned for determining the Defects Liability Period. However, it is stated that the selected Procuring Entity's Engineer (Consul

### EMD Refund Notice — 5/5 correct-source

- **Q71 [OK] [EN] [45.91s]** How is the EMD refunded to unsuccessful bidders?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: The EMD refund process for unsuccessful bidders is as follows:  1. The tender owner/department admin initiates the EMD remittance/refund process after opening/evaluation of PQ/Technical Bid and Price Bid. 2. The approved refund process is sent to the appropriate Department Approver. 3. Once the Department Approver approves the refund process, the e-Procurement system automatically sends an instruction to th
- **Q72 [OK] [EN] [48.70s]** Who initiates the EMD refund?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: The tender owner/department admin initiates the EMD refund process for unsuccessful bidders after opening/evaluation of PQ/Technical Bid and confirmation of Price Bid. Additionally, the department approver approves the refund process after verification, which automatically sends instructions to the bank for refund of EMD to respective bidder's account.  📋 Process: 1. The tender owner/department admin initia
- **Q73 [OK] [EN] [38.03s]** How long does an EMD refund take after approval?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: Within 1 or 2 days after the refund and approval process by department officials, the EMD amount gets credited to the respective bidder's account.  📋 Process:  Source: Online_EMD_Refund_Notice.pdf
- **Q74 [OK] [EN] [46.88s]** Where can a bidder check EMD refund status?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: A bidder can check EMD refund status on the Integrated e-Procurement portal.  📋 Process:  1. The tender owner/department admin initiates the EMD refund process for unsuccessful bidders after opening/evaluation of PQ/Technical Bid and Price Bid. 2. The department approver verifies the refund process, and the e-Procurement system sends an instruction to the bank for refund of EMD to the respective bank accoun
- **Q75 [OK] [EN] [56.71s]** What is the online EMD refund process?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: The online EMD refund process for unsuccessful bidders involves the following steps:  1. The tender owner/department admin initiates the EMD remittance/refund process after opening/evaluation of PQ/Technical Bid and Price Bid, and sends it to the appropriate Department Approver. 2. Once the Departments approver approves the refund process after verification, the e-Procurement system automatically sends an i

### PEF — 1/5 correct-source

- **Q76 [OK] [EN] [43.38s]** What is the PEF document about?
  - top source: PEF
  - answer: 💡 Answer:  The PEF document appears to be a Memorandum of Understanding (MoU) between a procuring entity and a project management consultant for the construction of specific works at designated locations.  📋 Process:  The MoU outlines the process for assigning work, preparing preliminary and detailed project reports, and seeking approval from competent authorities. It also mentions the preparation of bid documents, p
- **Q77 [REFUSED] [EN] [0.00s]** What information does the PEF form capture?
  - top source: (none)
  - answer: The answer to this question was not found in the available documents.
- **Q78 [MISS] [EN] [48.09s]** How is the PEF used in procurement?
  - top source: publicProManual
  - answer: 💡 Answer:  The Public Financial Management System (PFMS) is not directly mentioned as being used in procurement. However, it can be inferred that the PFMS might be involved in the financial management and tracking of procurement transactions.  📋 Process:  The PEF (Public Expenditure Framework) is a framework for managing public expenditure, which includes procurement. The PEF is used to ensure transparency, accountab
- **Q79 [REFUSED] [EN] [0.00s]** What fields are part of the PEF?
  - top source: (none)
  - answer: The answer to this question was not found in the available documents.
- **Q80 [MISS] [EN] [51.12s]** When is the PEF prepared in the tender process?
  - top source: publicProManual
  - answer: 💡 Answer: The Public Procurement Guidelines do not explicitly mention when the Pre-qualification Evaluation Form (PEF) is prepared in the tender process. However, it can be inferred that the PEF is likely to be prepared during the planning stage of procurement, as mentioned in Rule 144(x) of GFR 2017.  📋 Process: The planning stage involves publishing the Annual Procurement Plans on the Government e-Marketplace (GeM)

### PPM 00002 — 4/5 correct-source

- **Q81 [OK] [EN] [48.48s]** What does PPM cover regarding procurement procedures?
  - top source: PPM 00002
  - answer: 💡 Answer: The Public Procurement Manual (PPM) covers various aspects of procurement procedures, including:  * Eligibility criteria for bidders * Qualification criteria for contractors * Documentary evidence requirements * Procedure for preparation and submission of tenders * Criteria for determining the responsiveness of bids * Evaluation factors for assessing bids * Terms of procurement contracts * Settlement of dis
- **Q82 [OK] [EN] [63.40s]** What are the key provisions of this procurement policy manual?
  - top source: mannual procurement
  - answer: 💡 Answer:  The key provisions of this procurement policy manual include:  * The fundamental principles of public procurement, including transparency, fairness, competition, economy, efficiency, and accountability. * The five R's of procurement: relevance, reliability, responsiveness, robustness, and reputation. * The importance of need assessment, formulation of specifications, and procurement planning. * The role of
- **Q83 [OK] [EN] [67.33s]** What procurement methods are described in the PPM?
  - top source: PPM 00002
  - answer: 💡 Answer:  The Public Procurement Manual (PPM) describes several procurement methods, including:  1. Push Button Procurement (PBP): a method for small-value procurements with a total value of up to ₹5 lakh, inclusive of all taxes. 2. GeM portal: an electronic platform for procurement that allows buyers to place orders directly. 3. Direct Procurement Without Quotation: a method for procuring goods or services without 
- **Q84 [OK] [EN] [53.73s]** What does the PPM say about tender evaluation?
  - top source: PPM 00002
  - answer: 💡 Answer The Public Procurement Manual (PPM) outlines the process of tender evaluation, which includes reviewing and evaluating tenders based on specific criteria such as quality, price, technical merit, aesthetic and functional characteristics, environmental characteristics, running costs, cost-effectiveness, after-sales service, and technical assistance. The PPM also emphasizes the importance of ensuring that no te
- **Q85 [REFUSED] [EN] [0.00s]** What approval levels are defined in the PPM?
  - top source: (none)
  - answer: The answer to this question was not found in the available documents.

### Preferred System Configuration — 4/5 correct-source

- **Q86 [OK] [EN] [57.31s]** What is the preferred system configuration for the portal?
  - top source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS)
  - answer: 💡 Answer: The preferred system configuration for the portal includes:  * Operating System: Windows 7 or 8 (32-bit or 64-bit) * Browser: IE 9, Mozilla Firefox Version 44 (with IE Tab Add-on), Google Chrome Version 48 (with IE Tab Extension) * Java: Preferred version is 1.8.0_77 (32-bit or 64-bit) with only one version installed * Digital Certificate: CLASS II/III-SHA 2-2048 BIT SIGNING AND ENCRYPTION COMPONENT SEPARAT
- **Q87 [OK] [EN] [45.80s]** Which Java version is required for the e-procurement portal?
  - top source: Guidelines_To_Bidders_EPS_v1.6
  - answer: 💡 Answer: The required Java version for the e-procurement portal is ver.8.77.  📋 Process:  * The computer system or desktop/laptop of the bidder/user is required to have Java ver.8.77, Internet explorer 9/11, latest Mozilla Firefox, and Google Chrome with IE Tab V2 (Enhanced IE Tab). * A detailed step-by-step document on this setup is available on the eProcurement portal home page. * The auto setup utility is also av
- **Q88 [OK] [EN] [39.63s]** What operating system is recommended for the portal?
  - top source: Preferred_System_Configuration_V_2
  - answer: 💡 Answer:  The recommended operating system for the portal is Windows 7 OR Windows 8 (32 bit OR 64 bit), as mentioned in the "Recommended/Preferred System Settings for e-Procurement Portal (for both Buyers & Suppliers)" document.  📋 Process:  N/A  📘 Source:  Source: [Source 1: Recommended/Preferred System Settings for e-Procurement Portal (for both Buyers & Suppliers)]
- **Q89 [MISS] [EN] [47.09s]** What are the minimum hardware requirements for the portal?
  - top source: Guidelines_To_Bidders_EPS_v1.6
  - answer: 💡 Answer: The minimum hardware requirements for the portal are not explicitly mentioned in the provided sources. However, based on general guidelines and industry standards, it is recommended that the system should have:  * A processor with a clock speed of at least 2 GHz * At least 4 GB of RAM (8 GB or more recommended) * A storage capacity of at least 500 GB (1 TB or more recommended) * A compatible operating syste
- **Q90 [OK] [EN] [42.51s]** Which browser version is recommended in the system configuration?
  - top source: Preferred_System_Configuration_V_2
  - answer: 💡 Answer:  According to the system configuration, the recommended browser version is Microsoft Edge.  📋 Process:  The process involves setting up the default browser on a computer. The steps include selecting the "Default browser" option in the settings menu, choosing Microsoft Edge as the preferred browser, and adding the recommended portal address/URL.  📘 Source:  Sources: [Source 1: EDGE_Browser_Setup_V1.0.pdf], [

### Precis e-Procurement Project — 1/5 correct-source

- **Q91 [MISS] [EN] [48.87s]** What is the e-Procurement project about?
  - top source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS)
  - answer: 💡 Answer The e-Procurement project is about the use of information and communication technology (specially the internet) by the Procuring Entity in conducting procurement processes with vendors/contractors for the acquisition of goods, works, and services aimed at open, non-discriminatory, and efficient procurement through transparent procedures.  📋 Process The e-procurement process involves all steps involved in ten
- **Q92 [OK] [EN] [55.32s]** What are the objectives of the e-Procurement project?
  - top source: mannual procurement
  - answer: 💡 Answer:  The objectives of the e-Procurement project are to increase the efficiency and transparency in public procurement activity, as stated in the Précis  e-Procurement Project document. The project aims to implement a comprehensive and end-to-end e-Procurement solution across all Government departments/ agencies/ boards across the State.  📋 Process:  The process of implementing the e-Procurement project involve
- **Q93 [MISS] [EN] [56.32s]** What benefits does the e-Procurement project provide?
  - top source: FAQ of Chhattisgarh Infotech Promotion Society(CHIPS)
  - answer: 💡 Answer:  The e-Procurement project provides several benefits, including:  * Open and non-discriminatory procurement through transparent procedures * Efficient procurement processes * Reduced costs and improved value for money * Improved transparency and accountability in the procurement process * Enhanced security features to protect confidential procurement data * Improved management information system and decisio
- **Q94 [MISS] [EN] [51.61s]** What is the scope of the e-Procurement project?
  - top source: mannual procurement
  - answer: 💡 Answer:  The scope of the e-Procurement project includes the use of information and communication technology (specially the internet) by the Procuring Entity to conduct procurement processes with vendors/contractors for the acquisition of goods, supplies, works, and services. This involves receiving all bids through e-procurement portals in respect of all procurements, as per GFR 2017.  📋 Process:  The process of e
- **Q95 [MISS] [EN] [39.09s]** Who are the stakeholders in the e-Procurement project?
  - top source: mannual procurement
  - answer: 💡 Answer:  The stakeholders in the e-Procurement project include:  * Ministries/ Departments * Service Providers * Vendors/ Contractors * Departmental Users  📋 Process:  Not applicable, as this is an answer to a question.  📘 Source: Sources 1-5 (Government Procurement Assistant for the Chhattisgarh Infotech Promers)

### Vigilance Manual (English) — 4/5 correct-source

- **Q96 [OK] [EN] [48.93s]** What does the Vigilance Manual say about disciplinary proceedings and suspension?
  - top source: Vigilance Manual (Updated 2021) English
  - answer: 💡 Answer: The Vigilance Manual mentions various aspects related to disciplinary proceedings and suspension. It provides guidelines on initiation of disciplinary proceedings for minor and major penalties, appointment of inquiring authorities, procedures for empanelment of retired officers as inquiry officers, and responsibilities of presenting officers.  📋 Process:  * The manual outlines the steps involved in initiati
- **Q97 [REFUSED] [EN] [0.00s]** Within what time should a decision on the inquiry report be taken?
  - top source: (none)
  - answer: The answer to this question was not found in the available documents.
- **Q98 [OK] [EN] [50.59s]** What is the role of the disciplinary authority in the Vigilance Manual?
  - top source: Vigilance Manual (Updated 2021) English
  - answer: 💡 Answer: The role of the disciplinary authority in the Vigilance Manual is to determine whether a pattern has emerged on the basis of which an inference that an officer was actuated by extraneous considerations can be drawn. The disciplinary authority also needs to determine whether there has emerged from the record one or more circumstances that indicate that the decision which forms the basis of the charge of misc
- **Q99 [OK] [EN] [40.55s]** What are the grounds for suspension under the Vigilance Manual?
  - top source: Vigilance Manual (Updated 2021) English
  - answer: 💡 Answer:  The grounds for suspension under the Vigilance Manual are not explicitly mentioned. However, it can be inferred that suspension is recommended by the Central Bureau of Investigation (CBI) as per Chapter VII, Page 195.  📋 Process:  Not applicable, as the question only asks about the grounds for suspension.  📘 Source:  Vigilance Manual (Updated 2021), Chapter VII, Page 195.
- **Q100 [OK] [EN] [47.81s]** What does the Vigilance Manual say about handling complaints?
  - top source: Vigilance Manual (Updated 2021) English
  - answer: 💡 Answer:  The Vigilance Manual does not provide specific information on handling complaints. However, it mentions that the Commission has brought out Vigilance Manuals comprising of compilation of various rules, instructions and guidelines on vigilance administration from time to time. The manual also provides information on the procedure for obtaining and granting vigilance clearance.  📋 Process:  The Vigilance Man

### Vigilance Manual (Hindi) — 5/5 correct-source

- **Q101 [OK] [EN] [48.71s]** As per the vigilance rules, who is the disciplinary authority?
  - top source: Vigilance Manual (Updated 2021) English
  - answer: 💡 Answer:  The disciplinary authority is the Chief Vigilance Officer (CVO) or the concerned cadre authorities.  📘 Source:  [Source 4: Vigilance Manual (Updated 2021) English.pdf]  Headings: ['1.1.4 VIGILANCE UNIT OF THE ORGANISATIONS']  The CVO heads the Vigilance Division of the organisation concerned and acts as an advisor to the chief executive in all matters pertaining to vigilance. He also provides a link betwee
- **Q102 [OK] [EN] [47.75s]** What is the maximum time to complete an inquiry under the vigilance manual?
  - top source: Vigilance Manual (Updated 2021) English
  - answer: 💡 Answer: The maximum time to complete an inquiry under the vigilance manual is six months.  📋 Process:  * The model time limit for investigation of complaints and different stages of Departmental inquiry, as mentioned below, shall be adhered to. * The completion of the staff accountability exercise for frauds and the action taken may be placed before the Special Committee of the Board for monitoring and follow-up of
- **Q103 [OK] [EN] [59.00s]** What does the vigilance manual say about suspension during investigation?
  - top source: Vigilance Manual (Updated 2021) English
  - answer: 💡 Answer:  According to the Vigilance Manual, suspension can be considered as a measure of accountability during an investigation. The manual states that if a Government servant is under suspension or close to retirement, it may not be necessary to conduct a detailed inquiry against them. However, the main vigilance authority will ensure that all necessary steps are taken to prevent any attempt to influence the inves
- **Q104 [OK] [EN] [55.40s]** What is the procedure for departmental inquiry as per vigilance rules?
  - top source: Vigilance Manual (Updated 2021) English
  - answer: **Answer**  The procedure for departmental inquiry as per vigilance rules is outlined below:  1. **Preliminary Enquiry**: The Vigilance Commissioner or any other officer authorized by the Commission conducts a preliminary enquiry to determine whether there are sufficient grounds to proceed with the departmental inquiry. 2. **Formulation of Charges**: If the preliminary enquiry reveals prima facie evidence of miscondu
- **Q105 [OK] [EN] [44.31s]** What penalties are prescribed under the vigilance manual?
  - top source: Vigilance Manual (Updated 2021) English
  - answer: 💡 Answer: The Vigilance Manual does not explicitly prescribe penalties. However, it mentions that serious cases may invite administrative disabilities normally associated with the registration of a vigilance case against an official.  📋 Process: The Vigilance Manual does not provide a specific process for prescribing penalties. It only provides guidelines for processing proposals for appointment to Board level posts 

### Public Procurement Manual (mannual) — 5/5 correct-source

- **Q106 [OK] [EN] [49.31s]** When is a limited tender enquiry used in public procurement?
  - top source: FInal_GFR_upto_31_07_2024
  - answer: 💡 Answer: A Limited Tender Enquiry (LTE) may be used in public procurement when the estimated value of the goods to be procured is up to [Rs. 50 lakhs (Rupees Fifty Lakhs)]27,28. This method is adopted to obtain bids from a limited number of approved suppliers, with efforts made to identify a higher number of approved suppliers to obtain more responsive bids on competitive basis.  📋 Process: The process of LTE involv
- **Q107 [OK] [EN] [42.51s]** What are the methods of procurement in the public procurement manual?
  - top source: mannual procurement
  - answer: 💡 Answer: The methods of procurement mentioned in the public procurement manual are:  1. Modes of Procurement and Tendering Systems 	* Proprietary Article Certificate (PAC) 	* Single Tender Enquiry (STE) without PAC 	* Shopping Modes 2. Nomination Modes 3. Shopping Modes  📋 Process: The manual provides a comprehensive overview of the various modes of procurement, including proprietary article certificates, single ten
- **Q108 [OK] [EN] [53.46s]** What is the two-bid system in public procurement?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: The Two-Bid System in Public Procurement refers to a tendering process where bidders submit two separate bids: a techno-commercial bid and a financial bid. The techno-commercial bid contains the eligibility, technical quality, and performance aspects of the bidder's proposal, while the financial bid includes the price quotation along with other financial details.  📋 Process: The Two-Bid System involves the 
- **Q109 [OK] [EN] [48.53s]** How is e-procurement conducted as per the manual?
  - top source: publicProManual
  - answer: 💡 Answer: E-procurement is conducted through a third-party e-Procurement portal by the buyer in conducting procurement processes with vendors/contractors for the acquisition of goods (supplies), works, and services aimed at open, non-discriminatory, and efficient procurement through transparent procedures.  📋 Process:  1. Electronic procurement (e-procurement) is the use of information and communication technology (s
- **Q110 [OK] [EN] [66.04s]** What does the manual say about registration of suppliers?
  - top source: CHiPS_Vendor_Registration_Manual_English
  - answer: 💡 Answer:  The manual provides guidelines for the registration of suppliers. According to the manual, the registration of suppliers should be done following a fair, transparent, and reasonable procedure and after giving due publicity. The list of registered suppliers should be updated on a regular basis (annually). New supplier(s) may be considered for registration at any time, provided they fulfill all the required 

### Procurement of Goods (publicProManual) — 5/5 correct-source

- **Q111 [OK] [EN] [40.74s]** How much bid security is required in procurement of goods?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer:  The amount of bid security should generally be between two to five percent of the estimated value of the goods to be procured.  📘 Source:  Sources 1-4 (Chhattisgarh Infotech Prom Pre, publicProManual-1755343081262-715558279, FInal_GFR_upto_31_07_2024, and PPM 00002)
- **Q112 [OK] [EN] [58.91s]** What is the process for procurement of goods?
  - top source: Manual_for_Procurement_of_works_2019
  - answer: 💡 Answer: The process for procurement of goods involves the following steps:  1. Decision to procure something: A formal decision is made to procure goods, services, or works, along with an estimate of the expenditure. 2. Consultation with Financial Adviser: The procuring entity consults with a Financial Adviser (unless re-delegated within permissible limits) to ensure that the procurement process meets the requireme
- **Q113 [OK] [EN] [49.91s]** What is a Global Tender Enquiry for goods?
  - top source: publicProManual
  - answer: 💡 Answer: A Global Tender Enquiry (GTE) for goods is an advertised mode of procurement that aims to invite tenders from a wide range of suppliers or vendors globally. This process involves publishing the tender notice on various platforms, including GeM and GeM-CPPP, to attract competitive bids from both domestic and international suppliers.  📋 Process: Before sending the proposals for approval of Global Tenders, the
- **Q114 [OK] [EN] [53.40s]** What are the eligibility conditions for suppliers of goods?
  - top source: publicProManual
  - answer: 💡 Answer The eligibility conditions for suppliers of goods include credentials, manufacturing capability, quality control systems, past performance, after-sales service, and financial background. The supplier's production capability, financial strength, and other factors should not result in unreasonable exclusion of local suppliers who would otherwise be eligible.  📋 Process Before registration, the procuring entity
- **Q115 [OK] [EN] [47.59s]** How are goods inspected before acceptance?
  - top source: publicProManual
  - answer: 💡 Answer: Goods inspection before acceptance typically involves a post-delivery inspection upon receipt of goods. This process is usually carried out for goods that are available off-the-shelf and are BIS-marked. The final goods that may be directly consumed or used are inspected to ensure they meet the required quality standards.  📋 Process:  1. Post-delivery inspection is conducted upon receipt of goods before acce

### Short Tender Notice (2 days) — 0/5 correct-source

- **Q116 [MISS] [EN] [38.92s]** What are the rules for a 2-day short tender notice?
  - top source: mannual procurement
  - answer: 💡 Answer:  There is no specific rule mentioned in the provided sources for a 2-day short tender notice. The rules mentioned are related to Limited Tender Enquiry and Two bid system (simultaneous receipt of separate technical and financial bids), but not specifically for a 2-day short tender notice.  📋 Process: N/A  📘 Source: None
- **Q117 [MISS] [EN] [48.04s]** When can a 2-day tender notice be issued?
  - top source: mannual procurement
  - answer: 💡 Answer: According to Rule 162 of GFRupdatedupto31012026.pdf, a 2-day tender notice can be issued when the estimated value of the goods to be procured is up to [Rs. 50 lakhs (Rupees Fifty Lakhs)]. This rule applies to Limited Tender Enquiry, where copies of the bidding document should be sent directly by speed post/registered post/courier/e-mail to firms which are borne on the list of registered suppliers for the go
- **Q118 [MISS] [EN] [55.09s]** What approvals are needed for a short tender notice?
  - top source: publicProManual
  - answer: 💡 Answer: For a short tender notice, approval from the competent authority is required. The competent authority may be the Ministry/Department or the indentor, depending on the situation. The authority should certify that there is an existing or prospective urgency for operational or technical requirements and that any additional expenditure involved by not procuring through an advertised tender enquiry is justified 
- **Q119 [MISS] [EN] [52.59s]** What is the minimum notice period for short tenders?
  - top source: GFRupdatedupto31012026
  - answer: 💡 Answer: The minimum notice period for short tenders is not explicitly mentioned in the provided sources. However, it can be inferred that the notice period may vary depending on the organization and the type of tender.  📘 Source:  * [Source 2: 11.02.2004 transp in short term tender.pdf] In this source, it is mentioned that putting a notice on the department's website does not take any time compared to giving advert
- **Q120 [MISS] [EN] [50.06s]** What conditions justify a short tender notice?
  - top source: mannual procurement
  - answer: 💡 Answer: The conditions that justify a short tender notice are as follows:  1. There is an urgent need for the work and engaging in competitive tendering process would be impractical. 2. The works represent a natural continuation of previous work carried out by the firm, considering the limited size of the additional work in relation to the original procurement and the reasonableness of the price.  These conditions 

### Store Purchase Rules (CG) — 0/5 correct-source

- **Q121 [MISS] [EN] [47.24s]** What is the purpose of the Store Purchase Rules?
  - top source: publicProManual
  - answer: 💡 Answer:  The purpose of the Store Purchase Rules is to bring efficiency, economy, and transparency in matters relating to public procurement and for fair and equitable treatment of suppliers and promotion of competition in public procurement.  📋 Process:  The rules provide a framework for the procurement of goods required for use in the public service. The procedure to be followed in making public procurement must 
- **Q122 [MISS] [EN] [51.60s]** What are the methods of purchase under the Store Purchase Rules?
  - top source: FInal_GFR_upto_31_07_2024
  - answer: 💡 Answer: The methods of purchase under the Store Purchase Rules include:  1. Advertised Tender Enquiry 2. Limited Tender Enquiry 3. Two-Stage Bidding 4. Single Tender Enquiry 5. Electronic Reverse Auctions  These methods are mentioned in Rule 159 of the General Financial Rules.  📋 Process: The process involves following a standard method of obtaining bids, which includes:  1. Advertised Tender Enquiry: This involves
- **Q123 [MISS] [EN] [36.88s]** What is the monetary limit for direct purchase under store rules?
  - top source: publicProManual
  - answer: 💡 Answer:  The monetary limit for direct purchase under store rules is Rs. 50,000/-.  📋 Process:  Not applicable, as this answer provides a specific monetary limit.  📘 Source:  Source: GFRupdatedupto31012026.pdf (Rule 149)
- **Q124 [MISS] [EN] [45.55s]** What does the store purchase rule say about rate contracts?
  - top source: publicProManual
  - answer: 💡 Answer: The store purchase rule says that a Rate Contract should typically be for one year for stable technology products. However, in exceptional cases, a shorter or longer period of not more than two years may be considered.  📋 Process:  * The Procuring Entity may prescribe the amount of Bid Security in the Tender Document. * No quantity is mentioned in the Schedule of Requirement; only the anticipated drawable q
- **Q125 [MISS] [EN] [55.49s]** What is the procedure for store purchase in Chhattisgarh?
  - top source: CHiPS_Vendor_Registration_Manual_English
  - answer: 💡 Answer:  The procedure for store purchase in Chhattisgarh is not explicitly mentioned in the provided sources. The sources primarily focus on e-procurement, vendor registration, and digital signature certificates. However, it can be inferred that the process might involve registering as a vendor/bidder, obtaining a digital certificate, and submitting quotations or bids for tenders.  📋 Process:  The process of store
