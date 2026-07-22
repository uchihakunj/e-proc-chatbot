# CHiPS e-Procurement Chatbot — Hindi & Hinglish QA Report (20 Questions)

**Date:** 2026-07-03
**Endpoint:** `POST /api/stream` (BGE-M3 retrieval + bge-reranker on OpenVINO GPU + Ollama `gemma3:4b`)
**Knowledge base:** Qdrant `db3`
**Harness:** `05_webui/run_hin_eval_20.py` · **Raw data:** `05_webui/hin_eval_20_results.json`
**Set:** 10 Hindi (Devanagari) + 10 Hinglish (Roman), each on its own session (no carry-over).

> Responses below are the **raw model output** captured from the stream. In the browser, a Hinglish answer that drifts into Devanagari is auto-romanised client-side; none of these 20 needed that (the Hinglish drifts here were into *English*, which is left as-is).

---

## 1. Scorecard

| Verdict | Count | Questions |
|---|---|---|
| ✅ **Correct** | **12 / 20** | Q1, Q3, Q4, Q5, Q10, Q12, Q13, Q14, Q16, Q17, Q18, Q19 |
| ⚠️ **Partial / caveat** | **6 / 20** | Q2, Q7, Q8, Q11, Q15, Q20 |
| ❌ **Wrong** | **2 / 20** | Q6, Q9 |

> **Correction (post-review):** Q15 was first marked ❌ for "3–5%". On checking the KB, **3–5% is correct** for Goods/Consultancy per the *amended* GFR Rule 171 (Works/Plants remain 5–10%). Its only real defect was cosmetic (`[Source N]` tags), so it's reclassified ⚠️.
>
> **All three (Q6, Q9, Q15) have since been fixed — see §5.**

**Language compliance**
- Hindi questions → 9/10 answered in Hindi (Q9 wrongly refused).
- Hinglish questions → 8/10 in Roman Hinglish; **Q11 answered in English**, Q16 mostly English.

**Latency:** avg ≈ 31 s, median ≈ 32 s, range 26–46 s (Q9 = 0.6 s instant refusal).

**Cross-cutting wins (from the recent fixes):**
- ✅ The **"I'm not fully certain…" prefix is gone** from all 20 answers.
- ✅ **No "go check the CHiPS manual" deflections.**

---

## 2. Key findings (act on these)

1. **❌ Q6 — DSC conflated with EMD.** The answer opens *"डिजिटल हस्ताक्षर (DSC), जिसे Earnest Money Deposit (EMD) के रूप में भी जाना जाता है"* — DSC is **not** EMD. A serious factual hallucination (the retrieved DSC chunk got merged with EMD text). Contrast Q19, which explains DSC correctly.
2. **❌ Q9 — false "not found" for परचेज कमेटी (Hindi).** It refused with *"उपलब्ध दस्तावेज़ों में नहीं मिला"* in 0.6 s — yet **Q17 (Hinglish "GFR rule 155") answered the exact same thing correctly**. So it's a Hindi-phrasing retrieval/scope-gate miss, not missing data.
3. **⚠️ Q15 — figure is actually correct; only a cosmetic tag leak.** The **amended** GFR Rule 171 (KB text) sets Performance Security at **3–5% for Goods/Consultancy** and **5–10% for Works/Plants** — so Q15's "3–5%" (goods) and Q5's "5–10%" (works) are **both right**, not contradictory. The genuine defect is that Q15 **leaks raw `[Source 1]…[Source 5]` tags** into the prose. *(Original ❌ was my mis-assessment.)*
4. **⚠️ Q8 — demo URL.** Gave `https://eprocdemo.cgstate.gov.in/CHEPS/` (a *demo* address from a corrigendum-instructions doc). The real portal is **`eproc.cgstate.gov.in`** — which the bot itself uses correctly in Q3.
5. **⚠️ Q11 — Hinglish asked, English answered.** Content is right, but language drifted to English (the transliteration net only fixes Devanagari drift, not English drift).
6. **⚠️ Q7 & Q20 — threshold depends on the manual.** Limited Tender "up to ₹50 lakh" (Q7) and Advertised Tender "above ₹50 lakh" (Q20). GFR-2017 for *goods* uses ₹25 lakh; the ₹50 lakh figure appears to come from the works manual. Internally consistent, but flag if you expect the GFR-goods thresholds.
7. **Truncation.** Several answers cut off mid-sentence (Q2, Q6, Q7, Q10, Q18, Q19) and the `📎` grounding note is chopped (Q17, Q20). Worth raising `num_predict` and capping/cleaning the grounding-note extraction.

---

## 3. Full questions & responses

### — Hindi (Devanagari) —

### Q1. निविदा क्या होती है? — ✅ Correct
*Latency 45.5 s · Sources: Store Purchase Rules, Chatbot_Capabilities, Public Proc Manual, Works Manual*

> 💡 उत्तर
> निविदा का अर्थ है किसी कार्य या वस्तु की खरीद के लिए एक औपचारिक प्रस्ताव। यह एक ऐसी प्रक्रिया है जिसमें संभावित आपूर्तिकर्ता (suppliers) एक निर्धारित प्रारूप में अपनी कीमतें और शर्तें प्रस्तुत करते हैं, जिनका मूल्यांकन करके सबसे उपयुक्त आपूर्तिकर्ता को चुना जाता है।
>
> 📋 प्रक्रिया
> 1. निविदा विज्ञप्ति (NIT) जारी की जाती है जिसमें कार्य या वस्तु का विवरण होता है।
> 2. आपूर्तिकर्ताओं को निविदा प्रपत्र भरने और जमा करने के लिए कहा जाता है।
> 3. निविदाएँ निर्धारित समय सीमा के भीतर प्राप्त की जाती हैं।
> 4. निविदाओं का मूल्यांकन किया जाता है और सबसे कम कीमत या सर्वोत्तम शर्तों वाला आपूर्तिकर्ता चुना जाता है।
>
> 📘 स्रोत: निविदाएँ और प्रक्रिया (Tenders & Procurement Process) - Chatbot_Capabilities.pdf

**Assessment:** Accurate definition and NIT→evaluation flow. (Weak source attribution — cites the capabilities doc — but the content is correct.)

---

### Q2. EMD क्या है और यह कितनी होती है? — ⚠️ Partial
*Latency 28.8 s*

> 💡 उत्तर
> EMD का मतलब है Earnest Money या Bid Security। यह एक प्रकार की जमानत होती है जो बोली लगाने वाले द्वारा जमा की जाती है ताकि यह सुनिश्चित किया जा सके कि वे अपनी बोली वापस नहीं लेंगे या बोली अवधि के दौरान उसमें कोई बदलाव नहीं करेंगे।
>
> 📋 प्रक्रिया
> 1. EMD

**Assessment:** The "what is EMD" half is correct, but the answer is **truncated** and never answers **"कितनी होती है"** (should be 2–5% of estimated value — which Q16 gets right). Two-part question, second part dropped + cut off.

---

### Q3. वेंडर पंजीकरण कैसे करें? — ✅ Correct
*Latency 34.6 s · Sources: Vendor Registration Manual, Guidelines to Bidders, FAQ*

> 💡 उत्तर
> नया विक्रेता/आपूर्तिकर्ता रजिस्टर करने की प्रक्रिया इस प्रकार है:
> 1. सबसे पहले, आधिकारिक वेबसाइट https://eproc.cgstate.gov.in पर जाएं।
> 2. "New User" के लिंक पर क्लिक करें।
> 3. PAN कार्ड की जानकारी सही ढंग से दर्ज करें।
> 4. "New User" और "Enter" पर क्लिक करके आगे बढ़ें।
> 5. सिस्टम द्वारा पूछे गए सभी विवरण (अधिकृत हस्ताक्षरकर्ता, संपर्क जानकारी, बैंक विवरण, CRN, विक्रेता व्यवसाय और भागीदार) भरें।
> 6. सभी जानकारी भरने के बाद, सिस्टम सत्यापन का अनुरोध करेगा। "Save &Next" पर क्लिक करें।
> 📋 प्रक्रिया … (repeats steps, truncated at 5)

**Assessment:** Correct portal (`eproc.cgstate.gov.in`) and registration steps. Minor: Process block repeats the Answer and is truncated.

---

### Q4. GeM क्या है? — ✅ Correct
*Latency 39.7 s · Sources: Public Proc Manual, GFR*

> 💡 उत्तर
> GeM (Government e-Marketplace) भारत सरकार द्वारा स्थापित एक ऑनलाइन ई-कॉमर्स प्लेटफॉर्म है … खरीद प्रक्रिया को ऑनलाइन और इलेक्ट्रॉनिक बनाता है।
>
> उपलब्ध खरीद सीमाएँ:
> (i) ₹50,000/- तक — किसी भी योग्य विक्रेता से।
> (ii) ₹50,000/- से ₹10,00,000/- तक — कम से कम तीन निर्माताओं में सबसे कम कीमत वाले से।
> (iii) ₹10,00,000/- से अधिक — ऑनलाइन नीलामी / रिवर्स ऑक्शन से सबसे कम कीमत वाले से।
>
> 📘 स्रोत: FInal_GFR_upto_31_07_2024.pdf

**Assessment:** Correct definition **and** the GeM purchase-limit slabs match GFR (Rule 149).

---

### Q5. परफॉर्मेंस सिक्योरिटी कितने प्रतिशत होती है? — ✅ Correct
*Latency 34.4 s · Sources: Works Manual, Public Proc Manual*

> 💡 उत्तर
> परफॉर्मेंस सिक्योरिटी का प्रतिशत अनुबंध मूल्य का **पांच से दस प्रतिशत** होता है। कार्यों के अनुबंधों के लिए यह आमतौर पर पाँच प्रतिशत का होता है।
> … (form: DD / FDR / bank guarantee / online; JV proportionate; GTE per URDG 758)

**Assessment:** **5–10%** is the correct GFR figure (Rule 171). Note this **contradicts Q15**, which wrongly says 3–5% for the same concept.

---

### Q6. डिजिटल हस्ताक्षर (DSC) क्या है और क्यों जरूरी है? — ❌ Wrong
*Latency 25.9 s*

> 💡 उत्तर
> डिजिटल हस्ताक्षर (DSC), **जिसे Earnest Money Deposit (EMD) के रूप में भी जाना जाता है**, एक उच्च आश्वासन प्रमाण पत्र है … Class – II/Class – III … (truncated)

**Assessment:** **Factually wrong** — DSC is a digital signature certificate, **not** EMD. The retriever merged a DSC chunk with EMD text and the model conflated them. (Q19 explains DSC correctly, so it's a retrieval/generation slip here.)

---

### Q7. लिमिटेड टेंडर इंक्वायरी कब इस्तेमाल की जाती है? — ⚠️ Partial
*Latency 26.0 s · Sources: GFR, Works Manual*

> 💡 उत्तर
> लिमिटेड टेंडर इंक्वायरी (LTE) तब इस्तेमाल की जाती है जब अनुमानित मूल्य **[Rupees Fifty Lakhs]³⁰** तक होता है। यह एक सीमित प्रतिस्पर्धा खरीद विधि है, जिसमें पूर्व-चयनित बोलीदाताओं को … (truncated)

**Assessment:** Concept correct (limited competition, pre-selected bidders). **Threshold:** GFR-2017 for *goods* uses **₹25 lakh** for LTE; the "₹50 lakh" here is a works-manual figure. Flag if you expect GFR-goods thresholds. Truncated.

---

### Q8. e-Procurement पोर्टल का वेब पता क्या है? — ⚠️ Wrong URL
*Latency 25.8 s · Sources: Corrigendum Instructions, FAQ*

> 💡 उत्तर
> e-Procurement पोर्टल का वेब पता है: **https://eprocdemo.cgstate.gov.in/CHEPS/**.

**Assessment:** This is a **demo** URL (`eprocdemo…`) from a corrigendum-instructions doc. The real portal is **`https://eproc.cgstate.gov.in`** (which the bot uses correctly in Q3). Misleading.

---

### Q9. परचेज कमेटी कब बनाई जाती है और उसमें कितने सदस्य होते हैं? — ❌ Wrong (false refusal)
*Latency 0.6 s*

> इस प्रश्न का उत्तर उपलब्ध दस्तावेजों में नहीं मिला।

**Assessment:** **False "not found."** The answer is in the KB — **Q17 answers exactly this** (Rule 155: ₹50k–5 lakh, Local Purchase Committee, 3 members). The Hindi phrasing "परचेज कमेटी" missed retrieval / tripped the scope gate. Should reuse the same lexical concept mapping that made Q17 work.

---

### Q10. कोरिजेंडम (Corrigendum) क्या होता है? — ✅ Correct
*Latency 31.3 s · Sources: Works Manual, Corrigendum Instructions, Bid Submission Manual*

> 💡 उत्तर
> कोरिजेंडम (Corrigendum) एक संशोधन नोटिस है जो निविदा प्रक्रिया के दौरान जारी किया जाता है … सभी संभावित निविदाकर्ताओं को अधिसूचित किया जाता है और CPPP पर प्रकाशित किया जाता है।
> 📋 प्रक्रिया … (truncated at step 4)

**Assessment:** Correct definition (amendment notice, notification + CPPP publication). Tail truncated.

---

### — Hinglish (Roman) —

### Q11. Tender kya hota hai? — ⚠️ Content correct, wrong language (English)
*Latency 34.0 s · detected: hinglish*

> 💡 Answer
> A tender is a formal invitation to bid on a procurement opportunity, typically issued by a government entity like CHiPS. It outlines the requirements … The process involves creating the tender, viewing live tenders, and submitting an interested bid.
> 📋 Process … NITs are issued by Ministries/Departments with fixed days …

**Assessment:** Correct content, but answered in **English** despite a Hinglish question. (English drift isn't caught by the Devanagari→Roman net.)

---

### Q12. EMD refund kaise hota hai? — ✅ Correct
*Latency 32.1 s*

> 💡 Answer
> EMD/Bid Security refund ki process yeh hai: Agar bidder unsuccessful ho toh Department Admin EMD refund process initiate karta hai. Online payment karne wale bidders ke account mein amount online refund ho jaati hai, subject to tender terms & conditions … Bidders ko registration mein relevant account details provide karni hoti hain … CHiPS/System Integrator account details verify nahi karte …
> 📋 Process: 1. Department Admin refund initiate karta hai. 2. Department authority approve karta hai.

**Assessment:** Correct process, clean Hinglish.

---

### Q13. Vendor registration ke liye kaunse documents chahiye? — ✅ Correct
*Latency 30.3 s*

> 💡 Answer
> Vendor registration ke liye … PAN card, CRN certificate, authorized signatory details, bank details aur contact information. Vendor categories A, B, C, D bhi hain … Registration fee ₹500 hai aur renewal fee ₹100 hai.
> 📋 Process: New Supplier Registration → PAN → CRN upload → Preferred Login Code → fill details → Save & Next.

**Assessment:** Correct documents, categories, and fees (₹500 / ₹100). Clean Hinglish.

---

### Q14. Bid submit kaise karte hain? — ✅ Correct
*Latency 36.1 s*

> 💡 Answer
> Bid submit karne ke liye, bidder ko … deadline pe tender form complete bhar kar submit karna hota hai. Technical bid … online submission e-Procurement portal par available hoga. Financial bid (BOQ Excel Sheet) system mein upload karna hota hai … system automatically all-inclusive price calculate karta hai.
> 📋 Process: forms provide → BOQ Excel download → fill → upload → price auto-calc → submit quoted price …

**Assessment:** Correct bid-submission flow (BOQ Excel, auto price calc). Clean Hinglish.

---

### Q15. Performance security kitni honi chahiye? — ⚠️ Figure correct; cosmetic tag leak
*Latency 35.3 s*

> 💡 Answer
> Performance Security ki amount contract ke value ka **3% to 5%** tak honi chahiye. **[Source 1], [Source 2] aur [Source 3]** ne yeh nirnay diya … [Source 4] aur [Source 5] ne bhi yeh kaha ki BG 5% to 10% tak ho sakti hai. …
> 📎 As written in the rulebook — Rule 171: **three to five per cent (3-5%)**³⁷.

**Assessment:** The **figure is correct** — the amended GFR Rule 171 (KB text, `structured.md` L3562) says Performance Security is **3–5% for Goods/Consultancy/Non‑Consultancy**, and **5–10% for Works/Plants** (which is what Q5 quotes). So Q15 and Q5 are both right for their category — *not* contradictory. The only real defect is the leaked `[Source N]` tags, now stripped client-side. *(My original ❌ applied the older GFR‑2017 figure — corrected.)*

---

### Q16. Bid security yaani EMD kitne percent hoti hai? — ✅ Correct
*Latency 34.3 s*

> 💡 Answer
> Bid Security (yaani EMD) ordinarily **2 to 5 percent** of the estimated value of the goods to be procured hoti hai. … EMD can be obtained as Insurance Surety Bonds, Account Payee DD, FDR, Banker's Cheque or Bank Guarantee … or online payment.

**Assessment:** **2–5%** is correct (GFR Rule 170). (Sentences lean English, but the figure and forms are right.)

---

### Q17. GFR rule 155 kya kehta hai? — ✅ Correct
*Latency 32.2 s*

> 💡 Answer
> GFR rule 155 purchase of goods by Purchase Committee ke sambandh mein hai. … **Rs. 50,000 se upto Rs. 5,00,000** ke value ki goods ko **Local Purchase Committee (LPC)** ke recommendations par kharidna chahiye. **LPC mein 3 members hote hain.** Agar GeM par item nahi milti toh bhi LPC recommendation par kharid sakte hain.
> 📎 As written in the rulebook — Rule 155: [Rs.50,000 … and upto Rs.5,00,000/- …

**Assessment:** **Correct** (₹50k–5 lakh, LPC, 3 members). This is exactly what **Q9 wrongly refused** in Hindi.

---

### Q18. Two-bid system kya hota hai? — ✅ Correct
*Latency 28.2 s*

> 💡 Answer
> Do-bid system … bidders do parts mein bid submit karte hain — ek technical bid aur ek financial bid. Technical bid mein product ki technical details aur commercial terms … financial bid mein item-wise price … use hota hai jab technical requirements complex … (truncated)

**Assessment:** Correct (technical + financial bid, used for complex requirements). Tail truncated.

---

### Q19. DSC kaise register karte hain portal par? — ✅ Correct
*Latency 28.7 s*

> 💡 Answer
> Portal par DSC register karne ki process: (1) Class II ya Class III DSC procure karein (Signing + Encryption, licensed CA se); (2) registration details bharein, Save & Next; (3) 'Selecting DSC' step par appropriate certificate select karein — register karna zaroori hai; (4) DSC selection ke baad Terms & Conditions accept karein.

**Assessment:** Correct DSC-registration steps (Class II/III, signing+encryption, select+register, accept T&C). Note this is the **correct** DSC handling that **Q6 got wrong**.

---

### Q20. Advertised tender enquiry kab use hoti hai? — ⚠️ Partial
*Latency 27.8 s*

> 💡 Answer
> Advertised tender enquiry (OTE) ka istemal us goods ke procurement ke liye hota hai jahan estimated value **Rs. 50 lakh se zyada** hota hai. Yeh GeM aur GeM-CPPP par advertisement dene ki salah hoti hai.
> 📎 As written in the rulebook — Rule 161: [Rs. 50 lakhs … (truncated)

**Assessment:** Concept correct (open/advertised, high value, GeM/CPPP). **Threshold** GFR-goods is **₹25 lakh and above**; "₹50 lakh" is a works-manual figure — consistent with Q7's ₹50 lakh boundary but flag vs GFR-goods. Source line and grounding note truncated.

---

## 4. Recommendations

- **Q9 retrieval miss:** extend the concept→rule lexical mapping so Hindi "परचेज कमेटी / क्रय समिति" resolves to Rule 155 the way the Hinglish phrasing already does.
- **Q15 / Q5 Performance-Security inconsistency + `[Source N]` leak:** the grounding note is emitting "Rule 171: 3–5%" (wrong) — audit the Rule 171 extraction so it returns 5–10%; and strip literal `[Source N]` tags from the model prose.
- **Q6 DSC↔EMD conflation:** add DSC as its own concept anchor so an EMD chunk can't bleed into a DSC answer.
- **Q8 demo URL:** prefer the canonical `eproc.cgstate.gov.in` over the `eprocdemo…` string when both are retrievable (or curate the portal-URL fact).
- **Q11 English drift:** the Roman-Hinglish net only fixes Devanagari; English drift needs prompt reinforcement (or a stronger model) if you want it eliminated.
- **Truncation:** raise `OLLAMA_NUM_PREDICT`/`num_predict` and cap the `📎` grounding-note cleanly so it doesn't end mid-word.

---

## 5. Fixes applied (2026-07-03) — re-tested ✅

| # | Root cause | Fix | Re-test result |
|---|---|---|---|
| **Q6** | gemma3:4b hallucinated *"DSC is also known as EMD"* — pure generation slip | Added a **"DISTINCT concepts"** rule to the system prompt (DSC ≠ EMD ≠ Performance Security ≠ fees) | ✅ Now: *"DSC एक डिजिटल प्रमाणपत्र है जो पहचान प्रमाणित करता है…"* — **no EMD conflation** |
| **Q9** | Concept→rule map had `क्रय समिति` / `purchase committee` but **not `परचेज कमेटी`** (English transliterated to Devanagari); BGE‑M3 embedded it poorly → scored below the 0.05 scope gate → 0.6 s refusal | Added `परचेज कमेटी` + variants to the **Rule‑155 concept phrases**, and `कमेटी/समिति/परचेज/क्रय/खरीद` to `DOMAIN_TERMS` | ✅ Now **answers correctly**: ₹50k–5 lakh, LPC, **3 members** (+ accounts officer) |
| **Q15** | Model echoes context `[Source N]` labels into prose (figure was already correct) | Prompt **CITATIONS rule** (don't write `[Source N]`) + **client‑side `stripSourceTags()`** safety net | ✅ Tags removed from the **displayed** answer (4B still emits them in raw output; the client strip cleans them) |

**Files:** `05_webui/app.py` (system prompt TERMINOLOGY + CITATIONS rules; `CONCEPT_RULE_MAP`; `DOMAIN_TERMS`), `05_webui/nodejs/public/app.js` (`stripSourceTags`). Flask restarted; hard-reload the browser for the client-side `[Source N]` strip.
