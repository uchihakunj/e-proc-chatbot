# End-to-End LLM Answer Report — 150-Question Trilingual Test Bank

_Live chatbot (/api/stream, production gemma4 + fallback). Each answer graded on:_

_**Answered** (not a false refusal/empty) · **Language** (EN/HIN→Latin, HI→Devanagari) · **Source** (expected doc in cited top-5)._


## Summary (150/150 completed)

- **Answered (no false refusal): 113/150 (75%)**
- **Correct response language: 102/150 (68%)**
- **Correct source cited (top-5): 108/150 (72%)**
- **All three correct (answered + language + source): 71/150 (47%)**
- Run time: 148 min (this session)

### By language

| Lang | Answered | Language-correct | Source-correct | All-3 |
|---|---|---|---|---|
| EN | 44/60 | 42/60 | 43/60 | 30/60 |
| HI | 45/60 | 44/60 | 44/60 | 31/60 |
| HIN | 24/30 | 16/30 | 21/30 | 10/30 |

### By model (gemma4 = first batch, llama3:8b = resumed tail)

| Model | Q | Answered | Language | Source | All-3 |
|---|---|---|---|---|---|
| gemma4:12b | 91 | 85/91 | 81/91 | 58/91 | 51/91 |
| llama3:8b | 59 | 28/59 | 21/59 | 50/59 | 20/59 |

## Per-document (all-3-correct /5)

| # | Document | All-3 /5 |
|---|---|---|
| 1 | EMD_CHALLAN_PAYMENT_V1.0 | 4/5 |
| 2 | Online_EMD_Refund_Notice | 2/5  ⚠️ |
| 3 | mannual procurement | 1/5  ⚠️ |
| 4 | Manual_for_Procurement_of_works_2019 | 5/5 |
| 5 | publicProManual-1755343081262-715558279 | 1/5  ⚠️ |
| 6 | PPM 00002 | 3/5 |
| 7 | FInal_GFR_upto_31_07_2024 | 3/5 |
| 8 | GFRupdatedupto31012026 | 4/5 |
| 9 | GFR2017_HINDI | 2/5  ⚠️ |
| 10 | Store_Purhase_Rules_28.01.2021 | 2/5  ⚠️ |
| 11 | store purchase rule cg | 2/5  ⚠️ |
| 12 | AuctionManual_FA | 3/5 |
| 13 | CHiPS_Bid_Submission_Manual_English | 2/5  ⚠️ |
| 14 | CHiPS_Vendor_Registration_Manual_English | 5/5 |
| 15 | Guidelines_To_Bidders_EPS_v1.6 | 3/5 |
| 16 | Corrigendum_Instructions_to_department_users_and_bidders | 5/5 |
| 17 | Manual_Offline_Tenders_v.1.0 | 3/5 |
| 18 | short tender notice 2 days | 0/5  ❌ |
| 19 | 11.02.2004 transp in short term tender | 1/5  ⚠️ |
| 20 | 160616_AMC_AC short tender | 4/5 |
| 21 | EDGE_Browser_Setup_V1.0 | 4/5 |
| 22 | Preferred_System_Configuration_V_2 | 2/5  ⚠️ |
| 23 | it_act_2000_updated english | 4/5 |
| 24 | it_act_2000_updated hindi | 4/5 |
| 25 | Compilation of CVC Circulars and Guidelines | 2/5  ⚠️ |
| 26 | Vigilance Manual (Updated 2021) English | 0/5  ❌ |
| 27 | Vigilance Manual 2021 (Hindi) | 0/5  ❌ |
| 28 | FAQ of Chhattisgarh Infotech Promotion Society(CHIPS) | 0/5  ❌ |
| 29 | Précis  e-Procurement Project | 0/5  ❌ |
| 30 | PEF | 0/5  ❌ |

## False refusals / empty answers (had context but didn't answer)

| # Doc | Lang | Question | Top source |
|---|---|---|---|
| 2.1 Online_EMD_Refund_Notice | EN | In how many days is the EMD credited back afte | mannual procurement |
| 11.1 store purchase rule cg | EN | What is the approval hierarchy for store purch | store purchase rule cg |
| 12.1 AuctionManual_FA | EN | What is the bid decrement/increment in an e-au | publicProManual-1755343081262-715558279 |
| 17.3 Manual_Offline_Tenders_v.1.0 | HI | ऑफलाइन निविदा की बोलियाँ सिस्टम में कैसे दर्ज  | GFR2017_HINDI |
| 18.0 short tender notice 2 days | EN | When can a short (2-day) tender notice be used | GFRupdatedupto31012026 |
| 18.1 short tender notice 2 days | EN | What justification is required for a shortened | - |
| 19.1 11.02.2004 transp in short t | EN | What approvals are needed before floating a sh | mannual procurement |
| 19.2 11.02.2004 transp in short t | HI | अल्पकालीन निविदाओं में पारदर्शिता के लिए क्या  | 11.02.2004 transp in short term tender |
| 19.3 11.02.2004 transp in short t | HI | अल्पकालीन निविदा जारी करने से पहले कौन-सी स्वी | GFR2017_HINDI |
| 25.2 Compilation of CVC Circulars | HI | सार्वजनिक खरीद में पारदर्शिता पर CVC के दिशानि | Compilation of CVC Circulars and Guidelines |
| 25.3 Compilation of CVC Circulars | HI | भ्रष्टाचार रोकने हेतु ई-खरीद पर CVC की सलाह क् | Compilation of CVC Circulars and Guidelines |
| 25.4 Compilation of CVC Circulars | HIN | CVC guidelines procurement me transparency ke  | Compilation of CVC Circulars and Guidelines |
| 26.0 Vigilance Manual (Updated 20 | EN | What is the role of the Chief Vigilance Office | Vigilance Manual (Updated 2021) English |
| 26.1 Vigilance Manual (Updated 20 | EN | What types of cases fall under preventive vigi | Vigilance Manual (Updated 2021) English |
| 26.2 Vigilance Manual (Updated 20 | HI | खरीद में मुख्य सतर्कता अधिकारी (CVO) की भूमिका | Vigilance Manual 2021 (Hindi) |
| 26.3 Vigilance Manual (Updated 20 | HI | निवारक सतर्कता (Preventive Vigilance) के अंतर् | Vigilance Manual 2021 (Hindi) |
| 26.4 Vigilance Manual (Updated 20 | HIN | procurement me CVO ka role kya hota hai? | mannual procurement |
| 27.0 Vigilance Manual 2021 (Hindi | EN | What is the disciplinary process for vigilance | Vigilance Manual (Updated 2021) English |
| 27.1 Vigilance Manual 2021 (Hindi | EN | What is the difference between preventive and  | Vigilance Manual (Updated 2021) English |
| 27.2 Vigilance Manual 2021 (Hindi | HI | सतर्कता मामलों में अनुशासनात्मक प्रक्रिया क्या | Vigilance Manual 2021 (Hindi) |
| 27.3 Vigilance Manual 2021 (Hindi | HI | निवारक और दंडात्मक सतर्कता में क्या अंतर है? | Vigilance Manual 2021 (Hindi) |
| 27.4 Vigilance Manual 2021 (Hindi | HIN | vigilance case me disciplinary process kya hot | Vigilance Manual (Updated 2021) English |
| 28.0 FAQ of Chhattisgarh Infotech | EN | What services does CHiPS provide for e-Procure | FAQ of Chhattisgarh Infotech Promotion Society(CHIPS) |
| 28.1 FAQ of Chhattisgarh Infotech | EN | Whom do I contact for e-Procurement help desk  | FAQ of Chhattisgarh Infotech Promotion Society(CHIPS) |
| 28.2 FAQ of Chhattisgarh Infotech | HI | CHiPS e-Procurement के लिए कौन-सी सेवाएँ प्रदा | FAQ of Chhattisgarh Infotech Promotion Society(CHIPS) |
| 28.3 FAQ of Chhattisgarh Infotech | HI | e-Procurement हेल्प डेस्क सहायता के लिए किससे  | FAQ of Chhattisgarh Infotech Promotion Society(CHIPS) |
| 28.4 FAQ of Chhattisgarh Infotech | HIN | e-procurement me problem aaye to help desk kah | FAQ of Chhattisgarh Infotech Promotion Society(CHIPS) |
| 29.0 Précis  e-Procurement Projec | EN | What is the objective of the CHiPS e-Procureme | CHiPS_Bid_Submission_Manual_English |
| 29.1 Précis  e-Procurement Projec | EN | What are the main modules of the e-Procurement | Guidelines_To_Bidders_EPS_v1.6 |
| 29.2 Précis  e-Procurement Projec | HI | CHiPS e-Procurement परियोजना का उद्देश्य क्या  | CHiPS_Bid_Submission_Manual_English |
| 29.3 Précis  e-Procurement Projec | HI | e-Procurement प्रणाली के मुख्य मॉड्यूल कौन-से  | FAQ of Chhattisgarh Infotech Promotion Society(CHIPS) |
| 29.4 Précis  e-Procurement Projec | HIN | e-procurement project ka maksad kya hai? | Précis  e-Procurement Project |
| 30.0 PEF | EN | What is the purpose of the PEF and who fills i | PEF |
| 30.1 PEF | EN | What information must be provided in the PEF? | PEF |
| 30.2 PEF | HI | PEF का उद्देश्य क्या है और इसे कौन भरता है? | PEF |
| 30.3 PEF | HI | PEF में कौन-सी जानकारी देनी आवश्यक है? | PEF |
| 30.4 PEF | HIN | PEF form kis kaam ke liye hota hai? | PEF |

## Wrong-language answers

| # | Lang asked | Devanagari ratio | Question |
|---|---|---|---|
| 10.0 | EN | 0.37 | What are the tender submission timelines for limit |
| 10.4 | HIN | 0.31 | nivida jama karne ki tithi kitne din ki hoti hai? |
| 11.0 | EN | 0.26 | What are the Chhattisgarh store purchase rules for |
| 11.4 | HIN | 0.16 | CG store purchase rule me kharidi ka process kya h |
| 19.4 | HIN | 0.83 | short term tender me transparency ke liye kya rule |
| 20.4 | HIN | 0.62 | AC AMC tender me EMD aur eligibility kya hai? |
| 21.4 | HIN | 0.64 | portal chalane ke liye Edge browser kaise set kare |
| 22.3 | HI | 0.28 | बोलीदाता के कंप्यूटर पर कौन-से Java/DSC घटक आवश्यक |
| 22.4 | HIN | 0.54 | portal ke liye computer me kya configuration chahi |
| 23.4 | HIN | 0.91 | IT Act 2000 me digital signature kya hota hai? |
| 24.4 | HIN | 0.94 | IT Act ke hisaab se electronic record valid kaise  |
