# LLM Benchmark — gemma4:12b vs qwen2.5:7b

**Date:** 2026-06-14
**Hardware:** Intel Arc 130T iGPU (16 GB shared), torch CPU-only, Ollama (`OLLAMA_IGPU_ENABLE=1`)
**Pipeline:** real Flask `/api/stream` end-to-end — BGE-M3 retrieval + bge-reranker-v2-m3, `temperature 0`, `seed 42`, `num_ctx 5120`, `think:False`, llama3:8b auto-fallback on crash/empty.
**Question:** is qwen2.5:7b worth switching to for faster + better Hindi/English handling?

## Verdict

**Keep gemma4:12b.** qwen2.5:7b is ~20–30% faster but its Hindi/Hinglish quality collapses
(garbled grammar, invented words, wrong chunk selection, and one outright empty failure).
For a Hindi-facing procurement bot, that trade is not worth a modest speed gain — and the
gain is modest because the bottleneck is the large RAG prompt on the iGPU, not model size.

## Summary table

| Query | gemma4:12b | qwen2.5:7b |
|---|---|---|
| 1. धरोहर राशि (Hindi / EMD) | ✅ Accurate, fluent — **135.6s** | ❌ Garbled, wrong chunk — **96.7s** |
| 2. शुद्धिपत्र (Hindi / corrigendum) | ✅ Clear def + 5-step process — **85.3s** | ❌ Broken grammar, invented word — **61.9s** |
| 3. nivida…tithi (Hinglish) | ✅ Correct timelines, clean — **110.4s** | ❌ Empty → fallback → apology — **132.4s** |
| 4. What is EMD (English) | ✅ Complete 4-step — **69.2s** | ⚠️ Correct but thinner — **54.8s** |

- **Speed:** qwen faster on the 3 it completed (~55–97s vs ~69–136s), but not transformative.
- **Hindi:** gemma clearly more fluent and correct; qwen unnatural and sometimes wrong.
- **Hinglish:** qwen failed outright (empty output → llama3 fallback also empty).
- **English:** roughly comparable; gemma slightly more complete.

---

## Full answers

### Query 1 — धरोहर राशि क्या होती है और कब वापस मिलती है? (Hindi / EMD)

**gemma4:12b** — 135.6s · no fallback · top docs: EMD_CHALLAN_PAYMENT_V1.0, Manual_for_Procurement_of_works_2019

> 💡 उत्तर — धरोहर राशि (जिसे Bid Security या Earnest Money भी कहा जाता है) एक ऐसी राशि है जो बोली की अवधि के दौरान किसी Bidder द्वारा अपनी Bid को वापस लेने या उसमें बदलाव करने से रोकने के लिए ली जाती है। असफल Bidders की Bid Security, अंतिम Bid वैधता अवधि समाप्त होने के बाद जल्द से जल्द और अनुबंध दिए जाने के 30वें दिन या उससे पहले उन्हें वापस कर दी जानी चाहिए।
> नियम/प्रावधान — Bid Security (also known as Earnest Money) is to be obtained from the bidders except Micro and Small Enterprises (MSEs)… returned at the earliest after expiry of the final bid validity and latest on or before the 30th day after the award of the contract.
> व्याख्या — धरोहर राशि आमतौर पर अनुमानित मूल्य के दो से पांच प्रतिशत के बीच होती है; DD, FDR, Banker's Cheque या Bank Guarantee के रूप में स्वीकार्य।
> 📘 स्रोत: General Financial Rules (GFR)

**qwen2.5:7b** — 96.7s · no fallback · same top docs

> 💡 उत्तर — धरोहर राशि धारा विनिमय की एक प्रक्रिया है, जिसमें अगर EMD/Bid Security को eChallan विकल्प से भुगतान किया गया है और यह दिए गए बट्टा तिथि 13-04-2018 06:00 Hrs. पर अनुकूल राशि को भीत्र नहीं आया है, तो यह ब्याज से वापस मिलेगी इसके स्रोत खाते में।
> 📘 स्रोत: EMD Refund Guidelines (CHiPS)

*Assessment:* qwen never defines धरोहर राशि; it grabbed a 2018-specific eChallan chunk, used unnatural/invented phrasing ("धारा विनिमय", "बट्टा तिथि", "भीत्र"), and is effectively wrong.

### Query 2 — शुद्धिपत्र क्या है? (Hindi / corrigendum)

**gemma4:12b** — 85.3s · no fallback · top docs: publicProManual…, mannual procurement

> 💡 उत्तर — एक Corrigendum एक ऐसा संशोधन है जिसे Procuring Entity द्वारा Bid जमा करने की तारीख से पहले किसी भी समय जारी किया जा सकता है… (clarification के जवाब में भी)।
> 📋 प्रक्रिया — 1) Bid जमा करने की तिथि से पहले Corrigendum जारी कर सकती है; 2) सभी ज्ञात Bidders को लिखित सूचना; 3) CPPP पोर्टल पर प्रकाशन; 4) शेष Tender दस्तावेजों/वेबसाइट पर संलग्न; 5) बड़े बदलाव पर तिथि बढ़ाना बेहतर।
> नियम/प्रावधान — "At any time prior to the date of submission of bids, the Procuring Entity may… amend bid documents by issuing a corrigendum."
> 📘 स्रोत: Manual for Procurement of Goods 2024, Public Procurement Manual

**qwen2.5:7b** — 61.9s · no fallback · same top docs

> 💡 उत्तर — शुद्धिपत्र (Corrigendum) है शिकायत का समीक्षण और परिवर्तन के लिए जानकारी देने का एक बाध्यपद्रों है।
> 📋 प्रक्रिया — 1) शिकायत अथवा परिवर्तन की मांग करने वाला विनिमय… 2) प्राप्तवर्ती विनिमय की जानकारी… 3) सभी अवसरप्राप्त विक्रेताओं को भेजी जाएगी।
> 📘 स्रोत: publicProManual…, mannual procurement

*Assessment:* broken grammar, "बाध्यपद्रों" is not a word, conflates corrigendum with शिकायत (complaint). Semantically wrong.

### Query 3 — nivida jama krne ki tithi kya hai? (Hinglish)

**gemma4:12b** — 110.4s · no fallback · top docs: Store_Purhase_Rules_28.01.2021

> 💡 Answer — Nivida submit karne ki samay-seema nivida ke prakar par depend karti hai. Limited tender 15 din, open tender (₹50k–₹10L) 21 din, open tender (>₹10L) 30 din, Global tender 45 din.
> 📋 Process — 1) Limited 15 din; 2) Open ₹50k–₹10L 21 din; 3) Open >₹10L 30 din; 4) Global 45 din.
> Rule — "सीमित निविदा 15 दिन, खुली निविदा (50,000–10 लाख) 21 दिन, (10 लाख से अधिक) 30 दिन, ग्लोबल 45 दिन… गणना निविदा विज्ञप्ति प्रकाशन की तिथि से।"
> 📘 Source: Store Purchase Rules 2021

**qwen2.5:7b** — 132.4s · **fallback to llama3:8b fired** · same top docs

> Sorry, answer generate nahi ho paya. Please question thoda badal kar dobara poochhein.

*Assessment:* qwen produced empty output; the auto-fallback to llama3:8b also produced nothing, so the user got the graceful apology. Complete miss on the Hinglish case.

### Query 4 — What is EMD and when is it refunded? (English)

**gemma4:12b** — 69.2s · no fallback · top docs: EMD_CHALLAN_PAYMENT_V1.0, mannual procurement

> 💡 Answer — EMD = Earnest Money Deposit, refunded to unsuccessful bidders after evaluation of the Technical Bid and confirmation of the Price Bid.
> 📋 Process — 1) admin initiates refund after PQ/Technical + Price Bid; 2) Approver verifies/approves; 3) system instructs bank to credit registered account; 4) status via MIS on portal.
> 📘 Source: EMD Refund Guidelines (CHiPS)

**qwen2.5:7b** — 54.8s · no fallback · same top docs

> 💡 Answer — EMD = Earnest Money Deposit, refunded to unsuccessful bidders if not credited by the Bid Due Date.
> 📋 Process — 1) eChallan not credited within Bid Due Date → refunded to source account; 2) admin initiates refund after evaluation; 3) system instructs bank to credit registered account.
> 📘 Source: EMD Refund Guidelines (CHiPS)

*Assessment:* both correct; gemma's process is more complete and general, qwen slightly conflates the eChallan-not-credited edge case as the main rule. Roughly comparable.

---

## Recommendation

1. **Stay on gemma4:12b** (`OLLAMA_MODEL` in root `.env`) — best Hindi/Hinglish, which is the point of this bot.
2. If pure speed ever outranks Hindi quality, **llama3:8b** (already the fallback) is a better fast option than qwen here.
3. **Don't** pull qwen3:8b for this — it's a reasoning model (slower) and unlikely to beat gemma on Hindi.
4. qwen2.5:7b remains installed (4.7 GB); `ollama rm qwen2.5:7b` to reclaim space.
