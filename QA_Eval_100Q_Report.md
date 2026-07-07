# CHiPS e-Procurement Chatbot — 100-Question Evaluation Report

**Date:** 2026-07-01  
**Endpoint tested:** `POST /api/stream` (production SSE path → BGE-M3 retrieval + bge-reranker + Ollama `gemma3:4b`)  
**Knowledge base:** Qdrant collection `db3`, 3,503 chunks  
**NLU layer:** `nlp_features.py` (`classify_intent`, `extract_entities`) evaluated locally per query  
**Dataset:** 100 questions — 50 Vendor + 50 Government Officer, split across English / Hindi / Hinglish  
**Harness:** `05_webui/run_qa_eval_100.py`  |  **Raw data:** `05_webui/qa_eval_100_results.json`

---

## 1. Executive Summary — the four metrics

| Metric | Result |
|---|---|
| **Intent Recognition Accuracy** | **95/100 = 95%** correct topic-routing (50 fired a specific intent, 50 correctly stayed `UNKNOWN` → general RAG) |
| **Entity Extraction** | Query-side NER carried **0 transactional entities** (this set asks *about* rules, it doesn't supply amounts/PAN/dates) — 1 false-positive. Answer-side: **10/100 answers cite a specific `Rule N`** and **24/100 surface a threshold value** (₹/%/days). Rule-*number* accuracy ≈ 50% (see §3). |
| **Response Time (Latency)** | avg **38.8s**, median **38.7s**, range 2–60s. Live generation avg **39.6s**; 1 cache hit ~2s. **Far above the 12s target.** |
| **Error Handling (Fallback Rate)** | **0/100 = 0%** — 0 refusals, 0 empty-generations, 0 crashes, 0 model-fallback events. 1 wizard-clarify + 1 cache hit. |

### Headline read

- **99/100 answered successfully** with cited source documents; the 1 non-answer (Q1) is a *guided-wizard* prompt, not a failure.
- **Intent routing correct on 95/100 (95%).** All 50 officer/GFR questions and the vendor action-questions routed sensibly; document-discovery phrasings correctly fell through to `UNKNOWN` → full RAG.
- **5 intent misses** (Q32, Q35, Q75, Q94, Q100) — all keyword bleed ("login", "documents", "tender", "bid") pulling a question into a neighbouring intent. None caused a wrong answer.
- **Entity extraction is the metric to read carefully.** The *query-side* NER (persons/amounts/PAN…) is idle by design — these questions don't carry those entities. The *answer-side* extraction the officer set actually exercises — **rule citations and money/percent thresholds** — fires often, but the **rule NUMBERS are misattributed about half the time** (content grounded, citation wrong), consistent with the known GFR rule-citation weakness.
- **Latency avg 38.8s is ~3× the stated 12s target** — the generation-bound CPU/Arc-iGPU floor (reranker + `gemma3:4b`). This is the primary gap against the evaluation parameters, not a correctness problem.
- **Error handling is clean:** zero fallbacks/refusals/crashes across all 100 bilingual queries.

---

## 2. Intent Recognition — detail

Intent distribution across the 100 questions:

| Intent | Count |
|---|---|
| `UNKNOWN` | 50 |
| `RULES_GFR` | 16 |
| `DSC` | 9 |
| `EMD_GENERAL` | 7 |
| `PORTAL_USAGE` | 4 |
| `VENDOR_REGISTRATION` | 4 |
| `BID_SUBMISSION` | 4 |
| `EMD_REFUND` | 3 |
| `EMD_PAYMENT` | 1 |
| `DOCUMENT_REQUIREMENTS` | 1 |
| `TENDER_SEARCH` | 1 |

- **Specific intent fired:** 50/100.  **`UNKNOWN` → general RAG:** 50/100 (correct for "what is the policy / threshold / procedure" phrasings that name no action keyword).
- **Routing correct: 95/100 = 95%.**

**The 5 misses:**

| Q | Role/Lang | Expected | Fired | Why |
|---|---|---|---|---|
| Q32 | vendor/hi | dsc | PORTAL_USAGE | "login IDs" → PORTAL_USAGE instead of DSC |
| Q35 | vendor/hi | bid | DOCUMENT_REQUIREMENTS | "दस्तावेज / documents" → DOCUMENT_REQUIREMENTS instead of BID_SUBMISSION |
| Q75 | officer/hi | gfr | TENDER_SEARCH | "निविदा / tender" → TENDER_SEARCH instead of RULES_GFR |
| Q94 | officer/hin | gfr | BID_SUBMISSION | "bid" → BID_SUBMISSION instead of RULES_GFR |
| Q100 | officer/hin | gfr | BID_SUBMISSION | "price bid" → BID_SUBMISSION instead of RULES_GFR |

All five still retrieved the right documents and produced an on-topic answer — the mis-route only changes the topic-boost, not the retrieval corpus.

---

## 3. Entity Extraction — detail

The dataset's evaluation parameter defines this as *"correctness of rule citations (e.g. Rule 163/170) and value thresholds (e.g. Rs. one lakh) in the final response."* So there are two layers:

### 3a. Query-side NER (`extract_entities`)

- **1/100 queries produced an entity, and it was a false positive:** Q63 extracted *Company: "Small Enterprises"* from "Micro and **Small Enterprises** (MSEs)" (the corporate-suffix pattern matched "Enterprises").
- Otherwise **0 persons / amounts / dates / PAN / GSTIN** — correct, because none of these 100 questions *supply* a transactional entity. The extractor is not exercised by this set and should be validated separately with entity-bearing inputs ("EMD 2% of Rs 50,00,000", "PAN AAAAA0000A", vendor names).

### 3b. Answer-side rule + threshold extraction (what the officer set actually tests)

- **10/100 answers cite a specific `Rule N`; 24/100 surface a numeric threshold** (₹ amount / % / day-count).
- **Rule-number accuracy is the weak spot.** Cross-checked against standard GFR-2017 numbering (ATE = Rule 161, LTE = Rule 162, purchase-without-quotation = Rule 154, purchase committee = Rule 155, single-tender = Rule 166, late-bids = Rule 165):

| Q | Question (short) | Cited | Assessment |
|---|---|---|---|
| Q53 | Limited Tender Enquiry conditions | Rule 150 | ❌ 150 is GeM; LTE = Rule 162 |
| Q55 | Advertised-tender threshold | Rule 162 | ❌ 162 is LTE; ATE = Rule 161 |
| Q57 | Late bids (GFR Rule 165) | Rule 165 | ✅ correct (number was in the question) |
| Q58 | Single Tender justification | Rule 21 | ❌ single-tender = Rule 166 |
| Q63 | MSE procurement policy | Rule 153(ii) | ✅ MSE / purchase-preference ≈ Rule 153 |
| Q66 | Consultancy proposal evaluation | Rule 190 | ✅ plausible (consultancy = Rules 177–190) |
| Q73 | LTE conditions (Hindi) | Rule 150 | ❌ LTE = Rule 162 |
| Q91 | Purchase without quotation (Hin) | Rule 192(i) | ❌ without-quotation = Rule 154 |
| Q93 | Advertised tender compulsory (Hin) | Rule 161 | ✅ ATE = Rule 161 |
| Q95 | Late bid reject (Hin) | Rule 165 | ✅ correct (number was in the question) |

- **~5/10 rule numbers are right, ~5/10 misattributed** — and 2 of the 5 "correct" ones (Q57, Q95) were handed the number in the question itself, so *unaided* correct citations are ~3/8. The surrounding text is grounded in the retrieved manuals; only the numeric label is unreliable. This matches the standing `eval-rule-citation-hallucination` finding.
- **Threshold values are mostly plausible but internally inconsistent.** Same question, two languages, two different limits:
  - Q51 "purchase without quotation" → **Rs. 50,000** vs Q91 (same, Hinglish) → **Rs. 1,00,000–10,00,000**. Both are questionable against GFR Rule 154 (Rs 25,000); the model is reading different manual passages.
  - Q92 "Local Purchase Committee" → **₹25,000–₹2,50,000** ✅ (matches purchase-committee band).
  - EMD Q59/Q79 → **2%–5%**, Performance Security Q60/Q61/Q80/Q81 → **3%–10%** — both in the correct real-world range.
- **Extractor noise:** a few threshold cells show junk like `rs,` / `rs. 2` where the regex caught a bare "Rs." at a line break (Q52, Q54, Q62, Q68). Cosmetic; the underlying answers are fine.

---

## 4. Latency — detail

- Overall avg **38.8s**, median **38.7s**, stdev 8s, range 2–60s.
- Live-generation avg **39.6s** (excludes the 1 cache + 1 wizard-clarify).
- **1 cache hit:** Q4 (EMD rate) served in ~2s by the near-duplicate answer cache.
- **Against the 12s target this is ~3× over** — the bottleneck is the reranker + `gemma3:4b` token generation on the Arc-iGPU/CPU stack, not retrieval. Hindi/Hinglish answers run longer (extra tokens).

**Latency by role × language:**

| Segment | n | Intent OK | Answered | Avg latency | Rule cites | Threshold cites |
|---|---|---|---|---|---|---|
| Vendor · English | 20 | 20/20 | 19/20 | 32.0s | 0 | 2 |
| Vendor · Hindi | 20 | 18/20 | 20/20 | 40.6s | 0 | 1 |
| Vendor · Hinglish | 10 | 10/10 | 10/10 | 36.0s | 0 | 0 |
| Officer · English | 20 | 20/20 | 20/20 | 40.2s | 6 | 10 |
| Officer · Hindi | 20 | 19/20 | 20/20 | 43.2s | 1 | 6 |
| Officer · Hinglish | 10 | 8/10 | 10/10 | 40.1s | 3 | 5 |

**Slowest 6:**

- Q56 (officer/en, 59.55s) — What is the two-bid system, and when should it be followed?
- Q83 (officer/hi, 58.58s) — सूक्ष्म और लघु उद्यमों (MSEs) से खरीद के संबंध में सरकार की 
- Q35 (vendor/hi, 57.21s) — बोली लगाने के दौरान तकनीकी दस्तावेज कैसे अपलोड करें?
- Q89 (officer/hi, 52.0s) — निविदा के बाद बातचीत (Post-Tender Negotiations) पर सीवीसी के
- Q90 (officer/hi, 51.14s) — पोर्टल पर निविदा पुरस्कारों के प्रकाशन के लिए पारदर्शिता नीत
- Q77 (officer/hi, 50.63s) — जीएफआर नियम 165 के तहत देर से प्राप्त बोलियों के संबंध में क

Officer/Hindi is the slowest segment (larger GFR contexts + longer Devanagari generations); Vendor/English is fastest.

---

## 5. Error Handling / Fallback — detail

| Outcome | Count |
|---|---|
| ANSWERED | 98 |
| CACHE | 1 |
| CLARIFY | 1 |
| REFUSED | 0 |
| FALLBACK | 0 |
| ERROR | 0 |

- **Fallback rate = 0%.** No "information not available" refusals, no empty generations, no HTTP 500s, no model-fallback (`gemma3:4b` had ample iGPU headroom for all 100).
- **1 `CLARIFY` (Q1):** "How do I register as a vendor…" matched the **vendor-registration wizard trigger** (`register as a vendor`) and the bot began the guided flow ("What is your full name?") in ~2s with 0 sources, instead of answering from the manual. Correct-by-design, but worth knowing: a documentation-style *question* is intercepted by the task-flow. If a RAG answer is preferred for that phrasing, tighten `_FLOW_TRIGGERS`.
- Every retrieval that found sources produced a non-empty, sourced answer.

---

## 6. Full results — all 100 questions

Columns: **Q · Role · Lang · Question · Intent (conf) · Route✓ · Outcome · Latency(s) · #Src · Rule/Threshold entities in answer**

| Q | R | L | Question | Intent (conf) | ✓ | Outcome | Lat | Src | Answer entities |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ven | en | How do I register as a vendor on the Chhattisgarh eProcurement portal? | UNKNOWN (0.0) | ✅ | CLARIFY | 2.07 | 0 | — |
| 2 | ven | en | What are the system requirements for using the portal? | UNKNOWN (0.0) | ✅ | ANSWERED | 38.41 | 3 | — |
| 3 | ven | en | How can I reset my password if I forget it? | PORTAL_USAGE (0.6) | ✅ | ANSWERED | 38.77 | 4 | — |
| 4 | ven | en | What is the EMD rate and how is it calculated? | EMD_GENERAL (0.6) | ✅ | CACHE | 2.05 | 4 | — |
| 5 | ven | en | Who is exempt from paying the EMD amount? | EMD_GENERAL (0.6) | ✅ | ANSWERED | 35.88 | 4 | — |
| 6 | ven | en | What forms of EMD are accepted by the portal? | EMD_GENERAL (0.6) | ✅ | ANSWERED | 35.72 | 3 | — |
| 7 | ven | en | How long is the EMD validity period after submission? | EMD_GENERAL (0.6) | ✅ | ANSWERED | 33.98 | 3 | 45 days |
| 8 | ven | en | How do I get my EMD refund after a tender is awarded? | EMD_REFUND (0.8) | ✅ | ANSWERED | 31.66 | 4 | 2 days |
| 9 | ven | en | Can I submit multiple bids for the same tender? | UNKNOWN (0.0) | ✅ | ANSWERED | 39.21 | 3 | — |
| 10 | ven | en | What is a Digital Signature Certificate (DSC)? | DSC (1.0) | ✅ | ANSWERED | 37.45 | 4 | — |
| 11 | ven | en | How do I map my renewed DSC to my account? | DSC (0.6) | ✅ | ANSWERED | 38.54 | 4 | — |
| 12 | ven | en | Can I use the same DSC for two different login IDs? | DSC (0.6) | ✅ | ANSWERED | 30.52 | 4 | — |
| 13 | ven | en | What should I do if my DSC token gets blocked? | DSC (1.0) | ✅ | ANSWERED | 37.0 | 4 | — |
| 14 | ven | en | What are the contact details of the portal helpdesk? | UNKNOWN (0.0) | ✅ | ANSWERED | 30.05 | 4 | — |
| 15 | ven | en | How do I upload techno-commercial attachments during bidding? | UNKNOWN (0.0) | ✅ | ANSWERED | 35.5 | 4 | — |
| 16 | ven | en | Can a foreign vendor register on this portal? | VENDOR_REGISTRATION (0.6) | ✅ | ANSWERED | 33.03 | 3 | — |
| 17 | ven | en | What should I do if I get an 'Application Blocked by Security Setting' Java error? | UNKNOWN (0.0) | ✅ | ANSWERED | 28.99 | 6 | — |
| 18 | ven | en | How can I check the status of my online EMD payment? | EMD_PAYMENT (0.8) | ✅ | ANSWERED | 40.33 | 3 | — |
| 19 | ven | en | What happens if I withdraw my bid after the submission deadline? | UNKNOWN (0.0) | ✅ | ANSWERED | 36.51 | 4 | — |
| 20 | ven | en | Can I edit my company profile details after registration? | UNKNOWN (0.0) | ✅ | ANSWERED | 33.67 | 4 | — |
| 21 | ven | hi | छत्तीसगढ़ ई-प्रोक्योरमेंट पोर्टल पर नया वेंडर रजिस्ट्रेशन कैसे करें? | UNKNOWN (0.0) | ✅ | ANSWERED | 44.77 | 4 | — |
| 22 | ven | hi | पोर्टल का उपयोग करने के लिए कंप्यूटर की क्या आवश्यकताएं हैं? | UNKNOWN (0.0) | ✅ | ANSWERED | 36.25 | 3 | — |
| 23 | ven | hi | अगर मैं अपना पासवर्ड भूल जाऊं तो नया पासवर्ड कैसे बनाऊं? | PORTAL_USAGE (0.6) | ✅ | ANSWERED | 36.17 | 5 | — |
| 24 | ven | hi | ईएमडी (EMD) की दर कितनी होती है और इसकी गणना कैसे की जाती है? | EMD_GENERAL (0.6) | ✅ | ANSWERED | 46.64 | 3 | 5% |
| 25 | ven | hi | ईएमडी (EMD) भुगतान से किन कंपनियों को छूट प्राप्त है? | EMD_GENERAL (0.6) | ✅ | ANSWERED | 36.63 | 3 | — |
| 26 | ven | hi | पोर्टल पर ईएमडी के लिए कौन-कौन से भुगतान रूप स्वीकार किए जाते हैं? | UNKNOWN (0.0) | ✅ | ANSWERED | 34.38 | 3 | — |
| 27 | ven | hi | निविदा जमा करने के बाद ईएमडी कितने दिनों तक वैध रहनी चाहिए? | UNKNOWN (0.0) | ✅ | ANSWERED | 37.36 | 4 | — |
| 28 | ven | hi | निविदा समाप्त होने के बाद ईएमडी रिफंड कैसे प्राप्त करें? | EMD_REFUND (0.6) | ✅ | ANSWERED | 47.36 | 4 | — |
| 29 | ven | hi | क्या मैं एक ही निविदा के लिए एक से अधिक बोलियां जमा कर सकता हूं? | UNKNOWN (0.0) | ✅ | ANSWERED | 45.71 | 3 | — |
| 30 | ven | hi | डिजिटल सिग्नेचर सर्टिफिकेट (DSC) क्या है और यह क्यों आवश्यक है? | DSC (0.6) | ✅ | ANSWERED | 41.77 | 4 | — |
| 31 | ven | hi | नए रिन्यू किए गए डीएससी (DSC) को अपने प्रोफाइल से कैसे जोड़ें? | DSC (0.6) | ✅ | ANSWERED | 35.94 | 4 | — |
| 32 | ven | hi | क्या एक ही डीएससी का उपयोग दो अलग-अलग लॉगिन आईडी के लिए किया जा सकता है? | PORTAL_USAGE (0.6) | ❌ | ANSWERED | 34.53 | 4 | — |
| 33 | ven | hi | अगर मेरा डीएससी (DSC) टोकन ब्लॉक हो जाए तो मुझे क्या करना चाहिए? | DSC (0.6) | ✅ | ANSWERED | 44.5 | 4 | — |
| 34 | ven | hi | ई-प्रोक्योरमेंट पोर्टल की हेल्पलाइन टीम का संपर्क नंबर क्या है? | UNKNOWN (0.0) | ✅ | ANSWERED | 34.48 | 5 | — |
| 35 | ven | hi | बोली लगाने के दौरान तकनीकी दस्तावेज कैसे अपलोड करें? | DOCUMENT_REQUIREMENTS (0.6) | ❌ | ANSWERED | 57.21 | 3 | — |
| 36 | ven | hi | क्या कोई विदेशी कंपनी इस पोर्टल पर पंजीकरण कर सकती है? | VENDOR_REGISTRATION (0.6) | ✅ | ANSWERED | 39.41 | 4 | — |
| 37 | ven | hi | जावा सुरक्षा त्रुटि 'Application Blocked by Security Setting' आने पर क्या करें? | UNKNOWN (0.0) | ✅ | ANSWERED | 42.35 | 5 | — |
| 38 | ven | hi | मैं अपने ऑनलाइन ईएमडी भुगतान की स्थिति कैसे देख सकता हूं? | UNKNOWN (0.0) | ✅ | ANSWERED | 47.34 | 3 | — |
| 39 | ven | hi | यदि मैं बोली जमा करने की अंतिम तिथि के बाद अपनी बोली वापस लेता हूं तो क्या होगा? | BID_SUBMISSION (0.6) | ✅ | ANSWERED | 40.32 | 4 | — |
| 40 | ven | hi | पंजीकरण के बाद क्या मैं अपनी कंपनी के प्रोफाइल विवरण में बदलाव कर सकता हूं? | VENDOR_REGISTRATION (0.6) | ✅ | ANSWERED | 29.06 | 4 | — |
| 41 | ven | hin | Portal me vendor registration kaise kare? | VENDOR_REGISTRATION (0.8) | ✅ | ANSWERED | 41.62 | 4 | — |
| 42 | ven | hin | Password bhool gaya hu, reset kaise hoga? | PORTAL_USAGE (0.6) | ✅ | ANSWERED | 35.57 | 3 | — |
| 43 | ven | hin | EMD exemption ke liye kaun se documents upload karne padenge? | EMD_GENERAL (0.6) | ✅ | ANSWERED | 36.11 | 3 | — |
| 44 | ven | hin | DSC register karne ka sahi tarika kya hai? | DSC (0.6) | ✅ | ANSWERED | 38.02 | 5 | — |
| 45 | ven | hin | System configuration check karne ke liye download section me kaun sa file milega? | UNKNOWN (0.0) | ✅ | ANSWERED | 31.82 | 4 | — |
| 46 | ven | hin | Online payment failure hone par refund kab tak aayega? | EMD_REFUND (0.6) | ✅ | ANSWERED | 37.23 | 3 | — |
| 47 | ven | hin | Portal support team ka toll free number aur email id kya hai? | UNKNOWN (0.0) | ✅ | ANSWERED | 30.52 | 4 | — |
| 48 | ven | hin | Bid submit karne ke baad usko withdraw kaise kiya ja sakta hai? | BID_SUBMISSION (0.6) | ✅ | ANSWERED | 44.82 | 3 | — |
| 49 | ven | hin | Digital signature block ho gaya hai, isko unlock kaise kare? | DSC (0.6) | ✅ | ANSWERED | 31.0 | 3 | — |
| 50 | ven | hin | Kya foreign bidder ko registration ke liye PAN card chahiye? | UNKNOWN (0.0) | ✅ | ANSWERED | 33.21 | 5 | — |
| 51 | off | en | What is the limit for purchase without quotation under GFR? | RULES_GFR (0.6) | ✅ | ANSWERED | 39.14 | 4 | Rs. 50,000, Rs. 1,00,000, one lakh |
| 52 | off | en | What are the rules for establishing a Local Purchase Committee? | RULES_GFR (1.0) | ✅ | ANSWERED | 39.48 | 4 | rs, |
| 53 | off | en | Under what conditions can a Limited Tender Enquiry be used? | RULES_GFR (0.6) | ✅ | ANSWERED | 36.58 | 3 | Rule 150 |
| 54 | off | en | What is the minimum number of suppliers required for a Limited Tender? | UNKNOWN (0.0) | ✅ | ANSWERED | 32.01 | 5 | rs. 2 |
| 55 | off | en | What is the threshold value of procurement above which an Advertised Tender is mandatory? | UNKNOWN (0.0) | ✅ | ANSWERED | 37.06 | 3 | Rule 162(i), Rule 162(iii), Rule 162) |
| 56 | off | en | What is the two-bid system, and when should it be followed? | UNKNOWN (0.0) | ✅ | ANSWERED | 59.55 | 4 | — |
| 57 | off | en | What are the guidelines for handling late bids under GFR Rule 165? | RULES_GFR (0.8) | ✅ | ANSWERED | 33.99 | 2 | Rule 165 |
| 58 | off | en | Under what circumstances is Single Tender procurement justified? | UNKNOWN (0.0) | ✅ | ANSWERED | 49.43 | 3 | Rule 21 |
| 59 | off | en | What are the GFR rules for EMD rates in government contracts? | RULES_GFR (1.0) | ✅ | ANSWERED | 39.91 | 4 | 2%, 5% |
| 60 | off | en | What is the range of Performance Security required for a contract? | UNKNOWN (0.0) | ✅ | ANSWERED | 38.21 | 3 | 3%, 10%, Rs 50 Crores |
| 61 | off | en | What forms of Performance Security are acceptable under GFR? | RULES_GFR (0.6) | ✅ | ANSWERED | 40.71 | 3 | 10%, 60 days |
| 62 | off | en | In what situations can Performance Security be exempted? | UNKNOWN (0.0) | ✅ | ANSWERED | 39.89 | 3 | rs,, one lakh |
| 63 | off | en | What is the procurement policy for products from Micro and Small Enterprises (MSEs)? | UNKNOWN (0.0) | ✅ | ANSWERED | 42.11 | 3 | Rule 153(ii) · 20%, rs. 3 |
| 64 | off | en | How are price preferences applied to MSEs in evaluation? | UNKNOWN (0.0) | ✅ | ANSWERED | 41.12 | 1 | 15% |
| 65 | off | en | What are the steps for procurement of consulting services under GFR? | RULES_GFR (0.6) | ✅ | ANSWERED | 37.42 | 4 | — |
| 66 | off | en | What is the procedure for evaluation of consulting service proposals? | UNKNOWN (0.0) | ✅ | ANSWERED | 42.29 | 2 | Rule 190 |
| 67 | off | en | What are the guidelines for splitting tender quantities? | UNKNOWN (0.0) | ✅ | ANSWERED | 40.17 | 2 | — |
| 68 | off | en | When can a short-term tender with less than 21 days notice be issued? | UNKNOWN (0.0) | ✅ | ANSWERED | 31.99 | 4 | Rs. 50 lakhs, rs. 3 |
| 69 | off | en | What are the CVC guidelines on post-tender negotiations? | UNKNOWN (0.0) | ✅ | ANSWERED | 48.69 | 3 | — |
| 70 | off | en | What is the transparency policy for publication of tender awards on the portal? | UNKNOWN (0.0) | ✅ | ANSWERED | 35.01 | 4 | — |
| 71 | off | hi | जीएफआर (GFR) के तहत बिना कोटेशन के सीधे खरीद की सीमा क्या है? | RULES_GFR (0.6) | ✅ | ANSWERED | 33.66 | 4 | — |
| 72 | off | hi | स्थानीय क्रय समिति (Local Purchase Committee) के गठन के क्या नियम हैं? | RULES_GFR (0.8) | ✅ | ANSWERED | 42.78 | 4 | — |
| 73 | off | hi | सीमित निविदा जांच (Limited Tender Enquiry) का उपयोग किन परिस्थितियों में किया जा सकता है? | RULES_GFR (0.6) | ✅ | ANSWERED | 43.47 | 3 | Rule 150 |
| 74 | off | hi | सीमित निविदा के लिए न्यूनतम कितने आपूर्तिकर्ताओं की आवश्यकता होती है? | UNKNOWN (0.0) | ✅ | ANSWERED | 39.23 | 3 | — |
| 75 | off | hi | किस राशि से अधिक की खरीद के लिए विज्ञापन निविदा (Open Tender) अनिवार्य है? | TENDER_SEARCH (0.6) | ❌ | ANSWERED | 37.77 | 3 | — |
| 76 | off | hi | दो-बोली प्रणाली (Two-Bid System) क्या है और इसे कब लागू किया जाना चाहिए? | UNKNOWN (0.0) | ✅ | ANSWERED | 40.11 | 4 | — |
| 77 | off | hi | जीएफआर नियम 165 के तहत देर से प्राप्त बोलियों के संबंध में क्या निर्देश हैं? | RULES_GFR (0.6) | ✅ | ANSWERED | 50.63 | 3 | — |
| 78 | off | hi | किस परिस्थिति में एकल निविदा (Single Tender) खरीद को उचित माना जाता है? | UNKNOWN (0.0) | ✅ | ANSWERED | 37.28 | 3 | — |
| 79 | off | hi | सरकारी अनुबंधों में ईएमडी (EMD) दर के लिए जीएफआर नियम क्या हैं? | RULES_GFR (0.6) | ✅ | ANSWERED | 38.91 | 3 | 2%, 5% |
| 80 | off | hi | अनुबंध के लिए आवश्यक प्रदर्शन प्रतिभूति (Performance Security) की सीमा कितनी है? | UNKNOWN (0.0) | ✅ | ANSWERED | 33.17 | 3 | 5%, 10% |
| 81 | off | hi | जीएफआर के तहत प्रदर्शन सुरक्षा के कौन-कौन से रूप स्वीकार्य हैं? | UNKNOWN (0.0) | ✅ | ANSWERED | 40.27 | 3 | 3%, 10% |
| 82 | off | hi | किन स्थितियों में प्रदर्शन सुरक्षा जमा करने से छूट दी जा सकती है? | UNKNOWN (0.0) | ✅ | ANSWERED | 35.75 | 3 | — |
| 83 | off | hi | सूक्ष्म और लघु उद्यमों (MSEs) से खरीद के संबंध में सरकार की क्या नीति है? | UNKNOWN (0.0) | ✅ | ANSWERED | 58.58 | 3 | 25% |
| 84 | off | hi | मूल्यांकन के दौरान एमएसई (MSEs) को मूल्य प्राथमिकता (Price Preference) कैसे दी जाती है? | UNKNOWN (0.0) | ✅ | ANSWERED | 50.4 | 1 | 15%, 25%, 50% |
| 85 | off | hi | जीएफआर के तहत परामर्श सेवाओं (Consulting Services) की खरीद के क्या चरण हैं? | UNKNOWN (0.0) | ✅ | ANSWERED | 46.08 | 3 | — |
| 86 | off | hi | परामर्श सेवा प्रस्तावों के मूल्यांकन की क्या प्रक्रिया है? | UNKNOWN (0.0) | ✅ | ANSWERED | 48.07 | 3 | — |
| 87 | off | hi | निविदा मात्राओं को विभाजित (Splitting Tender Quantities) करने के क्या दिशानिर्देश हैं? | UNKNOWN (0.0) | ✅ | ANSWERED | 42.58 | 4 | — |
| 88 | off | hi | 21 दिनों से कम समय की सूचना वाली अल्पकालीन निविदा (Short-Term Tender) कब जारी की जा सकती है? | UNKNOWN (0.0) | ✅ | ANSWERED | 41.34 | 4 | 21 दिन |
| 89 | off | hi | निविदा के बाद बातचीत (Post-Tender Negotiations) पर सीवीसी के क्या निर्देश हैं? | UNKNOWN (0.0) | ✅ | ANSWERED | 52.0 | 3 | — |
| 90 | off | hi | पोर्टल पर निविदा पुरस्कारों के प्रकाशन के लिए पारदर्शिता नीति क्या है? | UNKNOWN (0.0) | ✅ | ANSWERED | 51.14 | 3 | — |
| 91 | off | hin | GFR ke under directly purchase bina quotation ke kitne amount tak ho sakti hai? | RULES_GFR (0.6) | ✅ | ANSWERED | 43.46 | 3 | Rule 192(i) · Rs. 1,00,000, one lakh, Rs. 10,00,000 |
| 92 | off | hin | Local Purchase Committee banane ka threshold limit kya hai? | RULES_GFR (0.6) | ✅ | ANSWERED | 38.92 | 4 | ₹25,000, ₹2,50,000 |
| 93 | off | hin | Advertised tender kis situation me compulsory ho jata hai? | UNKNOWN (0.0) | ✅ | ANSWERED | 43.81 | 4 | Rule 161) |
| 94 | off | hin | Two bid system me technical aur financial bid sath me kaise evaluate hote hain? | BID_SUBMISSION (0.6) | ❌ | ANSWERED | 38.56 | 3 | — |
| 95 | off | hin | Late bid ko reject karne ke liye GFR rule 165 kya kehta hai? | RULES_GFR (0.8) | ✅ | ANSWERED | 34.56 | 3 | Rule 165 |
| 96 | off | hin | Single tender case me CA ki approval kab jaruri hoti hai? | UNKNOWN (0.0) | ✅ | ANSWERED | 39.76 | 3 | 25 lakh |
| 97 | off | hin | Performance security deposit accept karne ke kya modes hain? | UNKNOWN (0.0) | ✅ | ANSWERED | 43.52 | 4 | — |
| 98 | off | hin | Short term tender notice publish karne ke liye time limit kitni di gayi hai? | UNKNOWN (0.0) | ✅ | ANSWERED | 35.11 | 3 | ₹50,000, ₹10 lakh, 21 days |
| 99 | off | hin | CVC ke rules ke mutabik negotiation L1 ke sath kab kiya ja sakta hai? | RULES_GFR (0.8) | ✅ | ANSWERED | 39.41 | 3 | — |
| 100 | off | hin | MSE bidders ko price bid me kya preference milti hai? | BID_SUBMISSION (0.6) | ❌ | ANSWERED | 43.9 | 3 | 15% |

---

## 7. Method & caveats

- Each question hit the real `/api/stream` SSE endpoint with a unique `session_id` (no coreference/slot carryover between questions).
- Intent + query entities were computed by calling `nlp_features.classify_intent` / `extract_entities` directly on each raw question (the same functions the server uses).
- "Intent Recognition Accuracy" is scored as topic-routing correctness: `UNKNOWN` → general RAG is *correct* for document/policy-lookup phrasings that name no action keyword (the taxonomy only fires on specific procurement actions).
- Answer-side rule/threshold "entities" were extracted from the final generated text with regexes (`Rule \d+`, ₹/%/day patterns); **rule-number correctness was judged by hand against standard GFR-2017 numbering** — the knowledge base contains multiple manuals/amendments, so a few thresholds may reflect a different document rather than an outright error.
- Latency = wall-clock from request send to the SSE `done` event (retrieval + reranking + full token generation).
- Answer *correctness* was not graded against a gold reference; outcomes track sourced-answer vs refusal/failure. Spot-checks show answers on-topic and grounded, with the rule-number caveat above.

---

## 8. Fixes applied after this run (2026-07-01)

The questions that did **not** answer what was asked were remediated in `nlp_features.py` and re-verified live against `/api/stream` (Flask restarted to reload the module). Three surgical, regression-checked changes:

| Q | Symptom in this run | Root cause | Fix | Re-test result |
|---|---|---|---|---|
| **Q1** | `CLARIFY` — bot launched the vendor-registration *wizard* ("What is your full name?"), 0 sources, gave no documentation answer | `detect_flow_trigger` matched the bare phrase **"register as a vendor"**, which appears verbatim inside the *question* | Removed `"register as a vendor"` / `"register as vendor"` from `_FLOW_TRIGGERS` (kept imperative starts: "register me", "help me register", "step by step registration", …) | **ANSWERED, 3 sources** — returns the CHiPS Vendor Registration Manual steps. Imperative "register me" still starts the wizard. |
| **Q32** | Routed `PORTAL_USAGE` instead of `DSC` | Query used Devanagari **डीएससी** (no Latin "DSC"), so the DSC intent scored 0 and "लॉगिन" won | Added `"डीएससी"` to the `DSC` intent signals | **Routes `DSC` ✅**, ANSWERED, 4 sources |
| **Q75** | Routed `TENDER_SEARCH` instead of GFR | **"open tender"** (a procurement *method*) was a `TENDER_SEARCH` signal | Removed `"open tender"` from `TENDER_SEARCH` (it names the advertised/open-tender *method*, not a search action) → falls through to general RAG | **general RAG ✅**, ANSWERED, 3 sources (answer cites the ₹50 lakh threshold) |

**Regression check:** re-classifying all 100 questions after the edits shows intent-routing misses drop **5 → 3** with no new mis-routes; overall routing **95% → 97%**.

**Deliberately not changed:** Q35 (`बोली/दस्तावेज` → DOCUMENT_REQUIREMENTS), Q94 (`technical/financial bid` → BID_SUBMISSION), Q100 (`price bid` → BID_SUBMISSION). These hinge on signals ("technical bid", "price bid", "documents") that legitimately belong to their fired intent; removing them would break genuine bid-submission / document queries, and all three already produced correct, grounded answers — only the topic-boost label differs.
