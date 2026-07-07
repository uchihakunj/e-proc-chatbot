# LLM Benchmark — gemma4:12b vs llama3:8b

**Date:** 2026-06-14
**Hardware:** Intel Arc 130T iGPU (16 GB shared), torch CPU-only, Ollama (`OLLAMA_IGPU_ENABLE=1`)
**Pipeline:** real Flask `/api/stream` end-to-end — BGE-M3 retrieval + bge-reranker-v2-m3, `temperature 0`, `seed 42`, `num_ctx 5120`, `think:False`.
**Note:** llama3:8b was run **twice** because its output is non-deterministic on this pipeline (intermittent empty answers). Both runs are reported.
**Question:** is llama3:8b a viable primary (it is already the auto-fallback)?

## Verdict

**Keep gemma4:12b as primary.** llama3:8b is faster (~35–69s vs ~69–136s) but on this bilingual
RAG pipeline it is **unreliable and weaker**: it intermittently returns an empty answer (the
graceful apology), its Hindi is noticeably weaker, it **consistently fails the Hinglish query**,
and it got the corrigendum question **wrong both times**. llama3:8b remains a reasonable *fallback*
(better than nothing when gemma OOM-crashes), but it is not a quality substitute.

## Summary table

| Query | gemma4:12b | llama3:8b (run 1 / run 2) |
|---|---|---|
| 1. धरोहर राशि (Hindi / EMD) | ✅ Accurate, fluent — **135.6s** | ⚠️ empty / weak-mediocre — **69.2s / 64.2s** |
| 2. शुद्धिपत्र (Hindi / corrigendum) | ✅ Clear def + 5-step — **85.3s** | ❌ **wrong both runs** — **61.1s / 35.8s** |
| 3. nivida…tithi (Hinglish) | ✅ Correct timelines — **110.4s** | ❌ **empty both runs** — **47.3s / 51.3s** |
| 4. What is EMD (English) | ✅ Complete 4-step — **69.2s** | ⚠️ empty / good — **62.1s / 61.4s** |

- **Speed:** llama3 is ~30–50% faster — the real win, expected from a 8B vs 12B on the iGPU.
- **Reliability:** llama3 returned a blank/apology on 3 of 8 attempts; gemma never did.
- **Hindi:** gemma fluent and correct; llama3 weak/garbled when it answers.
- **Hinglish:** llama3 failed both times; gemma nailed it.
- **English:** gemma complete and stable; llama3 good *when* it answers, but flaky.
- **Corrigendum:** llama3 wrong both times (claimed शुद्धिपत्र = "Hindi translation of tender document").

---

## Full answers

### Query 1 — धरोहर राशि क्या होती है और कब वापस मिलती है? (Hindi / EMD)

**gemma4:12b** — 135.6s

> 💡 उत्तर — धरोहर राशि (Bid Security / Earnest Money) बोली की अवधि में Bidder को Bid वापस लेने/बदलने से रोकने के लिए ली जाती है। असफल Bidders की Bid Security अंतिम Bid वैधता समाप्ति के बाद जल्द से जल्द और अनुबंध दिए जाने के 30वें दिन या उससे पहले वापस की जानी चाहिए।
> व्याख्या — आमतौर पर अनुमानित मूल्य के 2–5%; DD/FDR/Banker's Cheque/Bank Guarantee के रूप में स्वीकार्य।
> 📘 स्रोत: General Financial Rules (GFR)

**llama3:8b** — run 1: **empty** → "क्षमा करें, उत्तर तैयार नहीं हो सका…" (apology) · run 2: 64.2s

> 💡 उत्तर — धरोहर राशि (Earnest Money Deposit/ Bid Security) होती है, जिसका मूल्य निर्धारित किया गया है और यह बिड की स्थिति के आधार पर वापस मिलती है। यदि बिडर की बिड नाकाम हो जाती है, तो धरोहर राशि उसे वापस मिल जाती है।
> 📋 प्रक्रिया — 1) बिडर की बिड नाकाम होने पर; 2) वापस मिलने का निर्धारित समय (Bid Due Date) है; 3) यदि राशि खाते में नहीं आती तो बिडर ने राशि नहीं दी।
> 📘 स्रोत: EMD_CHALLAN…, Manual_for_Procurement_of_works_2019, GFR

*Assessment:* gemma gives the precise rule (2–5%, 30-day refund). llama3 is vague, omits the timeline/percentage, and step 3 is confused. And it failed entirely on run 1.

### Query 2 — शुद्धिपत्र क्या है? (Hindi / corrigendum)

**gemma4:12b** — 85.3s

> 💡 उत्तर — एक Corrigendum एक संशोधन है जिसे Procuring Entity, Bid जमा करने की तारीख से पहले किसी भी समय (स्वयं या clarification के जवाब में) जारी कर सकती है।
> 📋 प्रक्रिया — 1) तिथि से पहले जारी; 2) सभी ज्ञात Bidders को लिखित सूचना; 3) CPPP पोर्टल पर प्रकाशन; 4) शेष दस्तावेजों/वेबसाइट पर संलग्न; 5) बड़े बदलाव पर तिथि बढ़ाना।
> 📘 स्रोत: Manual for Procurement of Goods 2024, Public Procurement Manual

**llama3:8b** — run 1: 61.1s · run 2: 35.8s — **same wrong answer both runs**

> 💡 उत्तर — शुद्धिपत्र tender document का हिंदी में अनुवाद है, जो सार्वजनिक procurement प्रक्रिया का आधारभूत दस्तावेज है। यह contract के हिस्से बन जाता है…
> 📋 प्रक्रिया — नहीं
> 📘 स्रोत: publicProManual…, mannual procurement, PPM 00002

*Assessment:* llama3 is flatly **wrong** — corrigendum is an amendment notice, not "the Hindi translation of a tender document" — and emits "प्रक्रिया: नहीं". gemma is correct and complete.

### Query 3 — nivida jama krne ki tithi kya hai? (Hinglish)

**gemma4:12b** — 110.4s

> 💡 Answer — Limited tender 15 din, open tender (₹50k–₹10L) 21 din, open tender (>₹10L) 30 din, Global tender 45 din. (गणना निविदा विज्ञप्ति प्रकाशन की तिथि से।)
> 📘 Source: Store Purchase Rules 2021

**llama3:8b** — run 1 & run 2: **empty both times**

> Sorry, answer generate nahi ho paya. Please question thoda badal kar dobara poochhein.

*Assessment:* llama3 cannot handle the romanized-Hindi (Hinglish) query through this pipeline — empty on both runs. gemma answers with the exact timelines.

### Query 4 — What is EMD and when is it refunded? (English)

**gemma4:12b** — 69.2s

> 💡 Answer — EMD = Earnest Money Deposit, refunded to unsuccessful bidders after evaluation of the Technical Bid and confirmation of the Price Bid.
> 📋 Process — 1) admin initiates refund after PQ/Technical + Price Bid; 2) Approver verifies/approves; 3) system instructs bank to credit registered account; 4) status via MIS on portal.
> 📘 Source: EMD Refund Guidelines (CHiPS)

**llama3:8b** — run 1: **empty** → apology · run 2: 61.4s

> 💡 Answer — EMD is a security deposit paid by bidders to participate in a tender; refunded when the bid is unsuccessful or requirements are not met.
> 📋 Process — 1) Department Admin initiates refund for unsuccessful bidders; 2) Approver verifies/approves; 3) system instructs bank to credit registered account.
> 📘 Source: Online_EMD_Refund_Notice.pdf

*Assessment:* when llama3 answers (run 2), the English is good and close to gemma. But it returned empty on run 1 — the reliability problem again.

---

## Why llama3 empties out

llama3:8b itself is fine in isolation (a plain `What is EMD?` call returns a full answer in ~20s).
The blanks appear **only through the full RAG pipeline** — the large structured procurement system
prompt (~1.8k tokens) + retrieved context + the strict refuse-if-not-in-context directive. On the
harder/cross-lingual queries llama3 sometimes streams zero content tokens, and the empty-answer
guard then emits the apology. gemma4:12b handles the same prompt reliably. This also means the
gemma→llama3 **fallback is a safety net, not a quality equal** — if a query is hard enough to make
gemma fail, llama3 may also blank on it (as seen on the Hinglish case).

## Recommendation

1. **Primary: gemma4:12b** — reliable, fluent Hindi/Hinglish, accurate. The latency (~37–135s) is the
   cost of quality on this iGPU.
2. **Fallback: keep llama3:8b** — it is faster and recovers many cases when gemma OOM-crashes, but
   treat it as best-effort, not a quality substitute.
3. For real latency gains, the lever is the **iGPU / prompt size**, not swapping to a smaller model —
   smaller models here trade away the Hindi quality that is the point of this bot.
