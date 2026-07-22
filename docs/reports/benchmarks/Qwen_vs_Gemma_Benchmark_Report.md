# Primary-Model A/B Benchmark — `qwen2.5:7b` vs `gemma3-q3km:12b`

**Date:** 2026-06-18 · **Question:** *"Would degrading to a smaller Qwen as the primary make responses faster without losing much quality?"*
**Method:** Same production RAG pipeline for both runs — identical retrieval (BGE-M3), reranker (bge-reranker-v2-m3), lexical routes + clarifier cards, prompt, and `num_ctx=5120`. **Only the Ollama generation model was swapped** (via `.env`, Flask restarted between passes; Qdrant single-lock forces sequential runs). Fallback was set equal to the primary in each pass so we measure *that model's own* output (no `llama3:8b` contamination). Each pass: 1 untimed warmup (loads the model into VRAM) + 25 questions. Live `/api/stream`, hit directly on `:5000`.

**Question set (25):** the canonical 20 Bid/Vendor questions (card-backed/tuned) + 5 open-ended Hindi/English probes (lighter scaffolding, to expose raw model quality). Mixed HI / EN / Hinglish.

---

## 1. Headline

| Metric | **gemma3-q3km:12b** (current) | **qwen2.5:7b** (candidate) |
|---|---|---|
| **Answers fully correct** | **25 / 25** | **11 / 25** |
| Partial (right fact, garbled/incomplete) | 0 | 9 |
| Wrong | 0 | 5 |
| **Empty generations** (nothing produced) | **0** | **2** (Q06, Q14 — both Hindi) |
| Hindi prose quality | **clean & fluent** | **frequently garbled** |
| English prose quality | clean | clean |
| **Avg latency / question** | 100.5 s | **63.9 s** |
| Median latency | 97.4 s | **59.4 s** |
| Avg time-to-first-token | ~55 s | ~33 s |
| Max latency (outlier) | 144.6 s | 214.5 s (Q17 ramble) |
| Source: target at rank-1 | 19 / 25 | 19 / 25 *(identical — retrieval is model-independent)* |
| Source: target in top-k | 22 / 25 | 22 / 25 *(identical)* |

**Verdict: Qwen is ~36% faster but loses major answer quality, almost entirely in Hindi. It is NOT a safe primary for this Hindi-heavy government bot.**

---

## 2. Latency — Qwen is faster, but the bottleneck isn't the model

Qwen2.5:7b (4.7 GB) is meaningfully quicker than gemma3-q3km (6 GB): **median 59.4 s vs 97.4 s (~39% faster)**, and ~2× faster to first token (~33 s vs ~55 s). The smaller model ingests the prompt and generates faster on the Arc iGPU.

**But the dominant cost is the shared CPU retrieval+rerank floor, not generation.** Even Qwen's *best* time-to-first-token was ~21 s — that ~20–30 s of BGE-M3 embedding + cross-encoder reranking happens on CPU and is **identical for both models**. So swapping the LLM only shaves the generation tail; it can't fix the biggest latency component.

> **If latency is the goal, the highest-leverage fix is the reranker (GPU it, or reduce candidate count), not shrinking the LLM.** Qwen also occasionally *rambles* (Q17 = 214 s, QO1 = 104 s) — it doesn't stop cleanly, which partly erodes its speed advantage on exactly the long-form answers users care about.

---

## 3. Quality — Qwen's Hindi is the problem

English answers were comparable: Qwen got Q02, Q05, Q07, Q09, Q11, Q13, Q16, QO2 right, in clean English. **The damage is concentrated in Hindi and Hinglish**, where Qwen copies the headline fact from the clarifier card but mistranslates the supporting prose into broken, sometimes nonsensical Hindi:

| Q | Qwen output (excerpt) | Problem |
|---|---|---|
| Q01 | "इंडियन डिप्लोमेटिक सरकार में अधिसूचित दस्तावेजों के साथ निवासी डिप्लोमाटिक प्रदेश या एमबीएस चलाएँ … ऑनलाइन मूद्राअदान करें" | near-nonsense |
| Q03 | "सही डिजिटल **सिक्वर** … **ड्रपDownList** में चुनें" | wrong word ("सिक्वर"≠सिग्नेचर), mangled "DropDownList" |
| Q10 | "9.00 **अपराहद** से 23.00 रात" | garbled time word |
| Q17 | "रजिस्ट्रेशन की संशोधन परms **अपमानजनक हस्ताक्षर** का सहमति दें" | "insulting signature" — nonsense; also took **214 s** |
| QO4 | forward vs reverse auction — no actual ascending/descending distinction given | wrong + garbled |

**Two outright empty answers** (Q06 vendor-category limits, Q14 regional settings) — both Hindi, both card-backed, both of which gemma answers correctly. Qwen2.5:7b empty-generates on some Hindi + long-English-context prompts (the same failure mode the code comments note for `llama3:8b`).

**Two card facts lost entirely:**
- **Q04 (Hinglish, JRE install):** Qwen gave a generic `java.com/download` link instead of the portal path + **JRE 8.77** — i.e. it ignored the injected card. Gemma answered exactly.
- **Q08 (Hindi, payment modes):** Qwen returned "RTGS/CHALLAN + Internet Banking" (the *EMD-Challan* concept) instead of the card's **Debit/Credit/Net-banking**. Gemma got both.

By contrast, **gemma produced clean, fluent Hindi on every question**, including the hard-won fixes (Q12 regret = "केवल रेट कॉन्ट्रैक्ट… 'सभी बोलियां अस्वीकार करें' का कार्य नहीं है", Q18 "लाल रंग में", Q06 exact A/B/C/D limits). Its only blemishes were cosmetic typos (Q07 "NDUSIND/INSDL", QO1 "CPPP" slip) — never misleading.

---

## 4. Per-question comparison

| Q | Lang | gemma | qwen | Note |
|--|--|--|--|--|
| 01 | HI | ✅ | 🟡 | qwen: fact right, process steps garbled |
| 02 | EN | ✅ all 6 CAs | 🟡 | qwen gave only 4 of 6 CAs |
| 03 | HI | ✅ | 🟡 | qwen: "सिक्वर", "ड्रपDownList" |
| 04 | HIN | ✅ JRE 8.77 + portal path | ❌ | qwen: generic java.com, no 8.77 |
| 05 | EN | ✅ | ✅ | both: Open/Limited/Restricted/Short |
| 06 | HI | ✅ A>10cr…D≤1cr | ❌ **empty** | qwen produced no answer |
| 07 | EN | ✅ | ✅ | both got ATOM + BILLDESK |
| 08 | HI | ✅ Debit/Credit/Net | ❌ | qwen: RTGS/Challan only |
| 09 | EN | ✅ | ✅ | both: DSC/OTP recovery |
| 10 | HI | ✅ | ✅ | qwen number right, "अपराहद" garbled |
| 11 | EN | ✅ 24/48/72h | ✅ | both correct |
| 12 | HI | ✅ rate-contract only | ✅ | qwen headline right, process garbled |
| 13 | EN | ✅ | ✅ | both: Part1 prequal+techno / Part2 price |
| 14 | HI | ✅ Control Panel→English(US) | ❌ **empty** | qwen produced no answer |
| 15 | HI | ✅ full flow | 🟡 | qwen ok but thinner |
| 16 | EN | ✅ ₹500/₹100 | ✅ | both correct |
| 17 | HIN | ✅ (82 s) | 🟡 (214 s) | qwen: garbled + very slow |
| 18 | HI | ✅ Reg Number "red" | ✅ | qwen got number, missed "red" |
| 19 | EN | ✅ | 🟡 | qwen missed several field names |
| 20 | HI | ✅ PWD pre-fill | 🟡 | qwen vague/garbled |
| O1 | HI | ✅ bid flow | 🟡 | qwen: garbled "DSC वाइज़र", "लॉनच" |
| O2 | EN | ✅ EMD | ✅ | both correct |
| O3 | HIN | ✅ fee vs EMD | 🟡 | qwen conflated tender-fee % with EMD |
| O4 | HI | ✅ forward vs reverse | ❌ | qwen: no real distinction, garbled |
| O5 | EN | ✅ | 🟡 | qwen generic, missed the field list |

✅ correct · 🟡 partial (fact present but garbled/incomplete) · ❌ wrong/empty

---

## 5. Conclusion & recommendation

1. **Do NOT make `qwen2.5:7b` the primary.** For a Hindi/Hinglish-first portal it degrades the product: garbled Hindi prose, 2 empty answers, 2 lost card facts, and an answer-quality drop from 25/25 → 11/25. The ~36% speed gain does not justify this for factual government Q&A.

2. **Keep `gemma3-q3km:12b` as primary.** It held 25/25 with fluent Hindi and only cosmetic typos — the scaffolding (retrieval + clarifier cards) plus gemma's strong multilingual decoding is what makes the bot reliable.

3. **Fallback swap is still worth it (separate, low-risk).** As a *fallback* (replacing today's `llama3:8b`), `qwen2.5:7b` is still the better of the two weak models — it at least stays in Devanagari and gets headline facts, where `llama3:8b` scored ~36% language adherence. But the fallback only fires on a primary OOM/empty (rare with Q3_K_M's headroom), so the everyday path is unaffected. *(Not applied — `.env` left on the original `llama3:8b` default; can set `OLLAMA_FALLBACK_MODEL=qwen2.5:7b` on request.)*

4. **For latency, target the reranker, not the LLM.** ~20–30 s/query is CPU-bound BGE retrieval+rerank, identical regardless of model. GPU-ing or trimming the reranker would help more than a smaller LLM — and wouldn't cost any answer quality.

*Raw data: `bench_qwen.jsonl`, `bench_gemma.jsonl` (Temp); harness `bench_ab.py`. Production stack restored to `gemma3-q3km:12b`.*
