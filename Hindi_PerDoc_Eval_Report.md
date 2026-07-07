# Hindi Per-Document Evaluation — CHiPS e-Procurement Chatbot

**Model in production:** `gemma3-q3km:12b` (Q3_K_M) · **Path tested:** live streaming `/api/stream` (same as the browser UI) · **Date:** 2026-06-16
**Test:** 2 Hindi questions for **each of the 30 ingested documents** = **60 questions**, all in Hindi (Devanagari, with code-mixed English domain terms as real users type).

---

## 1. Headline results

| Metric | Result | |
|---|---|---|
| **Correct source retrieved (rank-1)** | **46 / 60** | 77% |
| **Correct source in top-5 (family-aware)** | **51 / 60** | 85% |
| **Answer fully correct** | **47 / 60** | 78% |
| **Answer partially correct** | **8 / 60** | 13% |
| **Answer wrong / not produced** | **5 / 60** | 8% |
| **Usable (correct + partial)** | **55 / 60** | **92%** |
| **Replied in Hindi** | 60 / 60 | 100% |
| **Avg latency** | ~100 s/question | (1 outlier at 488 s) |
| **Stability** | No OOM cascade; 1 empty generation, 1 false refusal | Q3_K_M headroom held |

**One-line verdict:** Source retrieval and answer quality are **strong (≈85–92%)**. The bot reasons like a rule-book — it quotes the exact rule/clause, then explains it in Hindi. Almost every failure is a **retrieval-recall gap or a near-duplicate-document mix-up**, not a hallucination — when the retrieved chunk lacks the fact, the bot honestly says "not in the documents" rather than inventing an answer.

---

## 2. How "correct source" was scored (important)

The corpus has **heavy near-duplicate families**, so demanding the *exact* file would be misleading. A question whose answer legitimately lives in any sibling was counted correct:

| Family | Member documents |
|---|---|
| **GoI procurement manuals** | Manual_for_Procurement_of_works_2019, PPM 00002 (Works 2022), `mannual procurement` (Works 2022 — duplicate of PPM 00002), publicProManual (Goods 2024) |
| **GFR** | FInal_GFR_upto_31_07_2024, GFRupdatedupto31012026, GFR2017_HINDI |
| **CG Store Purchase Rules** | Store_Purhase_Rules_28.01.2021, store purchase rule cg |
| **Vigilance / CVC** | Vigilance Manual (English), Vigilance Manual (Hindi), Compilation of CVC Circulars |
| **IT Act 2000** | it_act_2000_updated english, it_act_2000_updated hindi |
| **Short-tender notices** | short tender notice 2 days, 11.02.2004 transp…, 160616_AMC_AC short tender |

`T1` = correct family at rank-1 · `Tk` = correct family in top-5 but not rank-1 · `MISS` = not retrieved · `REFUSE` = scope-gate refused.

---

## 3. Per-document results (60 questions)

Answer verdict: ✅ correct · 🟡 partial · ❌ wrong / not produced.

| # | Document | Hindi question (trimmed) | Src | Ans |
|--|----------|--------------------------|-----|-----|
| 1 | Bid Submission Manual | ऑनलाइन बिड कैसे जमा करें? | MISS | ✅ |
| 2 | Bid Submission Manual | आइटम रेट (BOQ) में दरें कैसे भरें? | Tk | ✅ |
| 3 | Vendor Registration | पंजीकरण / नवीनीकरण शुल्क कितना है? | T1 | 🟡 |
| 4 | Vendor Registration | पंजीकरण क्रमांक कैसे मिलता है? | T1 | ✅ |
| 5 | Corrigendum Instructions | विभाग शुद्धिपत्र कैसे जारी करते हैं? | T1 | ✅ |
| 6 | Corrigendum Instructions | शुद्धिपत्र की सूचना बिडर्स को कैसे? | MISS | 🟡 |
| 7 | EDGE Browser Setup | इंटरनेट प्रॉपर्टी कैसे खोलें? | T1 | ✅ |
| 8 | EDGE Browser Setup | ट्रस्टेड साइट्स / ActiveX सेटिंग? | T1 | ✅ |
| 9 | EMD Challan Payment | चालान से EMD भुगतान कैसे? | T1 | ✅ |
| 10 | EMD Challan Payment | EMD भुगतान के तरीके? | T1 | ✅ |
| 11 | FAQ (CHiPS) | हेल्पडेस्क टोल-फ्री नंबर व समय? | T1 | ❌ |
| 12 | FAQ (CHiPS) | बिड हेतु कौन-सा DSC क्लास? | T1 | ✅ |
| 13 | FInal_GFR_2024 | GFR नियम 144 मूल सिद्धांत? | MISS | ✅ |
| 14 | FInal_GFR_2024 | GeM खरीद किस नियम के तहत? | Tk | ✅ |
| 15 | GFR_upto_2026 | नियम 170 बिड सिक्योरिटी %? | T1 | ✅ |
| 16 | GFR_upto_2026 | नियम 171 परफॉर्मेंस सिक्योरिटी? | T1 | ✅ |
| 17 | Guidelines to Bidders | कंप्यूटर आवश्यकताएँ (Java)? | T1 | ✅ |
| 18 | Guidelines to Bidders | दस्तावेज़ साइज़ सीमा / बैंडविड्थ? | T1 | 🟡 |
| 19 | Offline Tenders Manual | ऑफलाइन टेंडर कैसे अपलोड करें? | T1 | 🟡 |
| 20 | Offline Tenders Manual | हेडर में NIT रेफ़/कॉल नंबर कहाँ? | Tk | ✅ |
| 21 | Procurement of Works 2019 | बिड वैधता अवधि कितने दिन? | T1 | ✅ |
| 22 | Procurement of Works 2019 | परफॉर्मेंस सिक्योरिटी % (works)? | T1 | ✅ |
| 23 | Online EMD Refund Notice | असफल बिडर को EMD रिफंड कैसे? | T1 | ✅ |
| 24 | Online EMD Refund Notice | रिफंड कौन शुरू करता, कहाँ जमा? | T1 | ✅ |
| 25 | PEF | PEF किसलिए / NICSI अग्रिम? | T1 | ✅ |
| 26 | PEF | PEF में विभाग का कौन-सा विवरण? | T1 | ✅ |
| 27 | PPM 00002 (Works 2022) | LTE किस मूल्य सीमा तक? | T1 | 🟡 |
| 28 | PPM 00002 (Works 2022) | खुली निविदा प्रकाशन कैसे? | Tk | ✅ |
| 29 | Preferred System Config | अनुशंसित OS / ब्राउज़र? | T1 | ❌ |
| 30 | Preferred System Config | जावा (JRE) कौन-सा वर्ज़न? | T1 | ✅ |
| 31 | Store Purchase Rules 2021 | शासकीय क्रय किस माध्यम से? | T1 | ✅ |
| 32 | Store Purchase Rules 2021 | GeM से खरीद किन परिस्थितियों में? | T1 | ✅ |
| 33 | mannual procurement | दो-बोली मूल्यांकन कैसे? | T1 | ✅ |
| 34 | mannual procurement | बिड डॉक्युमेंट के प्रमुख भाग? | T1 | ✅ |
| 35 | publicProManual (Goods 2024) | वस्तुओं की खरीद विधियाँ? | T1 | ❌ |
| 36 | publicProManual (Goods 2024) | MSE को छूट / प्राथमिकता? | T1 | ✅ |
| 37 | short tender notice 2 days | SNIT में पात्रता शर्तें? | MISS | 🟡 |
| 38 | short tender notice 2 days | कैनवासिंग पर बिड निरस्त? | Tk | ✅ |
| 39 | 11.02.2004 transparency | अल्पकालीन निविदा में पारदर्शिता? | T1 | ✅ |
| 40 | 11.02.2004 transparency | निविदा सूचना प्रकाशन प्रावधान? | MISS | 🟡 |
| 41 | 160616 AMC AC tender | AC AMC निविदा की शर्तें? | T1 | ✅ |
| 42 | 160616 AMC AC tender | NIELIT फ़ाइल क्रमांक? | T1 | ✅ |
| 43 | CVC Circulars | पोस्ट-टेंडर नेगोशिएशन निर्देश? | T1 | ✅ |
| 44 | CVC Circulars | मोबिलाइज़ेशन एडवांस दिशानिर्देश? | T1 | ✅ |
| 45 | GFR2017_HINDI | ₹25,000 तक बिना कोटेशन खरीद? | T1 | ✅ |
| 46 | GFR2017_HINDI | पारदर्शिता के मूल सिद्धांत? | MISS | ✅ |
| 47 | Vigilance Manual (Eng) | सतर्कता के मुख्य प्रकार? | T1 | ✅ |
| 48 | Vigilance Manual (Eng) | CTE संगठन की भूमिका? | T1 | ✅ |
| 49 | Vigilance Manual (Hin) | सतर्कता जाँच / अनुशासन प्रक्रिया? | T1 | ✅ |
| 50 | Vigilance Manual (Hin) | लोक सेवक शिकायत पर कार्रवाई? | T1 | ✅ |
| 51 | IT Act (Eng) | धारा 43 कंप्यूटर क्षति दंड? | T1 | 🟡 |
| 52 | IT Act (Eng) | DSC कौन जारी करता (CA)? | MISS | ✅ |
| 53 | IT Act (Hin) | 'संरक्षित प्रणाली' क्या है? | T1 | ✅ |
| 54 | IT Act (Hin) | इलेक्ट्रॉनिक अभिलेख मान्यता धारा? | T1 | ✅ |
| 55 | Auction Manual | ऑक्शन पोर्टल लॉगिन कैसे? | T1 | ✅ |
| 56 | Auction Manual | लाइव ऑक्शन में H1 / रीफ्रेश? | MISS | ❌ |
| 57 | store purchase rule cg | भण्डार क्रय नियम 2002 उद्देश्य? | T1 | ✅ |
| 58 | store purchase rule cg | CSIDC ई-मानक / बीज निगम दरें? | T1 | ✅ |
| 59 | Précis e-Proc Project | नोडल एजेंसी कौन, कब शुरू? | T1 | ✅ |
| 60 | Précis e-Proc Project | परियोजना 2.0 की कुल लागत? | REFUSE | ❌ |

---

## 4. What went well

- **Rule/law corpus is excellent.** GFR (144/149/170/171, ₹25k), CVC (post-tender negotiation only with L-1; mobilisation advance), Vigilance (types; CTE; disciplinary process; complaint handling), IT Act (Sec 70 protected system; Sec 4 e-records), Store Purchase Rules (objective; tender mode; CSIDC e-Manak) — all retrieved the right family and quoted the **exact provision verbatim**, then explained it. This is the strongest part of the system.
- **Distinctive portal docs nailed it:** EDGE setup (`inetcpl.cpl`, trusted sites, ActiveX), EMD Challan (RTGS/CHALLAN → counterfoil → DSC), Online EMD Refund (Dept Admin initiates → approver → bank → registered account → MIS), Auction login (`Password@123`, H1 view, 1-min refresh), DSC class (Class II/III).
- **Thin documents surprised on the upside:** **PEF** (the bilingual NICSI advance form) and the **NIELIT AC-AMC short tender** both retrieved rank-1 and extracted real specifics (GSTIN/contact fields; 3-yr dealership, EMD ₹10,000, file no. `1(55)/2000 NIELIT`).
- **Reasoning format is consistent and auditable:** every answer gives 💡 उत्तर → 📋 प्रक्रिया → नियम/प्रावधान (quoted clause) → व्याख्या → 📘 स्रोत. Good for a government assistant.
- **No hallucination.** When the retrieved chunk lacked the fact, the bot said "not in the documents" instead of fabricating — the right failure mode for a compliance bot.
- **Language:** 100% Hindi, correctly handling code-mixed English terms (EMD, GeM, DSC, BOQ, corrigendum).

---

## 5. The failures, explained (5 wrong + 8 partial)

**❌ Hard failures (5):**
1. **Q11 — FAQ helpline number "not available".** Source was right (FAQ, rank-1) but the retrieved chunk didn't contain `1800-419-9140`. The number *is* in the corpus (Vendor Reg manual). → **retrieval-recall gap**, not hallucination.
2. **Q29 — Preferred System Config produced an empty answer** ("उत्तर तैयार नहीं हो सका"). Retrieval was fine; the model returned nothing. A **one-off generation hiccup** (1/60) — worth watching as a Q3_K_M stability data point.
3. **Q35 — Goods procurement methods "not specified".** Retrieved a Works-2019 chunk that didn't enumerate the methods; the answer exists in the manuals but wasn't in the retrieved window. → recall gap.
4. **Q56 — Live-auction H1/refresh answered *wrong*.** Retrieval pulled the *reverse-auction* chunk of the Goods manual ("only L-1 displayed") and the bot said bidders **cannot** see H1 — the opposite of the CG Auction Manual (which says bidders **can** view H1 + ranking, 1-min refresh). Ironically Q55 on the *same* doc was perfect. → **reranker picked the wrong sibling.**
5. **Q60 — Project 2.0 cost falsely refused.** The answer (₹36.90 crore) is plainly in the Précis doc, but retrieval scored low and the scope-gate refused. → **over-aggressive scope-gate / recall gap.**

**🟡 Partial (8):** Q3 (renewal fee — bot said ₹250, but the Vendor Reg manual says ₹100 → **needs verification**), Q6 & Q37 & Q40 (answered from a sibling/manual instead of the target doc — content reasonable but not doc-specific), Q18 (didn't give the actual size/bandwidth numbers), Q19 (offline-tender upload steps too shallow — that doc is screenshot-heavy), Q27 (LTE thresholds muddled CG-store vs GFR), Q51 (gave Section 66's punishment for a Section 43 question — 43 is civil *compensation*).

---

## 6. Cross-cutting findings

- **The duplicate-manual family is the #1 source of "wrong source".** The 4 GoI manuals (Works-2019, Works-2022 ×2, Goods-2024) + 3 GFRs share almost identical text, so the reranker freely swaps among them (Q1, Q2, Q13, Q46, Q27, Q35). Family-aware scoring (85% top-5) reflects reality better than rank-1 (77%). **Consider de-duplicating** `mannual procurement` vs `PPM 00002` (identical Works-2022 manual) to cut noise.
- **Bilingual pairs behave well.** Hindi questions on the IT-Act and Vigilance EN/HI pairs correctly land on the family; the Hindi member is usually preferred (expected, and fine).
- **OCR'd Hindi scans degrade the *citation* block, not the answer.** Store Rules / GFR-Hindi / Vigilance-Hindi answers are factually right, but the quoted "नियम/प्रावधान" text shows OCR garble (`:पए`, `#पए`, `–षटया`). The 💡 उत्तर itself reads clean.
- **Latency:** ~100 s/question average on the iGPU is the real end-to-end cost (retrieval + CPU cross-encoder rerank + generation). One question hit **488 s** (Q6) — a likely transient model reload. Q3_K_M's VRAM headroom prevented any OOM cascade across all 60.

---

## 7. Recommendations (priority order)

1. **Helpdesk fast-path on the server.** The client UI has an instant FAQ dictionary, but `/api/stream` doesn't — so helpline/contact questions depend on chunk luck (Q11). Add a small server-side lexical answer (or a dedicated FAQ chunk boost) for contact/helpline/fee queries.
2. **De-duplicate the GoI manuals** (drop one of `mannual procurement` / `PPM 00002`) to reduce sibling-swap noise.
3. **Soften the scope-gate** for in-domain factual lookups like Q60 (it refused an answer that was in the corpus). Tie refusal to retrieval score *and* a domain check, not retrieval alone.
4. **Auction vs reverse-auction disambiguation** (Q56): boost `AuctionManual_FA` when the query mentions नीलामी/ऑक्शन/H1 so the portal manual outranks the GFR reverse-auction chunk.
5. **Verify the renewal fee** (₹100 vs ₹250) and, if ₹100 is correct, prefer the Vendor Registration manual over the Guidelines change-log for fee questions.
6. **Re-OCR the Hindi scans** (Store Rules, GFR-Hindi, Vigilance-Hindi) so the cited clause text is clean, not garbled.

---

*Method: 60 Hindi questions POSTed to the live `/api/stream` endpoint; the reranked `context` event gave the actual retrieved sources, the token stream gave the answer. Source correctness scored automatically (family-aware); answer correctness and reasoning judged by reading every answer against the source documents. Raw data: `hi_doc_eval.jsonl`.*
