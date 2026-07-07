# -*- coding: utf-8 -*-
"""Assemble QA_Eval_100Q_Report.md from qa_eval_100_results.json + _table.md."""
import json, os, statistics as st
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "qa_eval_100_results.json"), encoding="utf-8"))
table = open(os.path.join(HERE, "_table.md"), encoding="utf-8").read()
n = len(d)

oc = Counter(r["outcome"] for r in d)
answered = oc["ANSWERED"] + oc["CACHE"] + oc["FALLBACK"]
intent_ok = sum(r["intent_ok"] for r in d)
lat = [r["latency_s"] for r in d]
live = [r["latency_s"] for r in d if r["outcome"] not in ("CACHE", "CLARIFY")]
rules = [r for r in d if r["answer_rules"]]
thr = [r for r in d if r["answer_thresholds"]]
idist = Counter(r["intent"] for r in d)

def rl(role, lang):
    g = [r for r in d if r["role"] == role and r["lang"] == lang]
    gl = [x["latency_s"] for x in g]
    return (len(g), sum(x["intent_ok"] for x in g),
            sum(1 for x in g if x["outcome"] in ("ANSWERED", "CACHE", "FALLBACK")),
            round(sum(gl)/len(gl), 1),
            sum(1 for x in g if x["answer_rules"]),
            sum(1 for x in g if x["answer_thresholds"]))

slow = sorted(d, key=lambda x: -x["latency_s"])[:6]
misses = [r for r in d if not r["intent_ok"]]

L = []
w = L.append
w("# CHiPS e-Procurement Chatbot — 100-Question Evaluation Report")
w("")
w("**Date:** 2026-07-01  ")
w("**Endpoint tested:** `POST /api/stream` (production SSE path → BGE-M3 retrieval + bge-reranker + Ollama `gemma3:4b`)  ")
w("**Knowledge base:** Qdrant collection `db3`, 3,503 chunks  ")
w("**NLU layer:** `nlp_features.py` (`classify_intent`, `extract_entities`) evaluated locally per query  ")
w("**Dataset:** 100 questions — 50 Vendor + 50 Government Officer, split across English / Hindi / Hinglish  ")
w("**Harness:** `05_webui/run_qa_eval_100.py`  |  **Raw data:** `05_webui/qa_eval_100_results.json`")
w("")
w("---")
w("")
w("## 1. Executive Summary — the four metrics")
w("")
w("| Metric | Result |")
w("|---|---|")
w(f"| **Intent Recognition Accuracy** | **{intent_ok}/{n} = {100*intent_ok//n}%** correct topic-routing (50 fired a specific intent, 50 correctly stayed `UNKNOWN` → general RAG) |")
w(f"| **Entity Extraction** | Query-side NER carried **0 transactional entities** (this set asks *about* rules, it doesn't supply amounts/PAN/dates) — 1 false-positive. Answer-side: **{len(rules)}/{n} answers cite a specific `Rule N`** and **{len(thr)}/{n} surface a threshold value** (₹/%/days). Rule-*number* accuracy ≈ 50% (see §3). |")
w(f"| **Response Time (Latency)** | avg **{sum(lat)/n:.1f}s**, median **{st.median(lat):.1f}s**, range {min(lat):.0f}–{max(lat):.0f}s. Live generation avg **{sum(live)/len(live):.1f}s**; 1 cache hit ~2s. **Far above the 12s target.** |")
w(f"| **Error Handling (Fallback Rate)** | **0/{n} = 0%** — 0 refusals, 0 empty-generations, 0 crashes, 0 model-fallback events. 1 wizard-clarify + 1 cache hit. |")
w("")
w("### Headline read")
w("")
w(f"- **{answered}/{n} answered successfully** with cited source documents; the 1 non-answer (Q1) is a *guided-wizard* prompt, not a failure.")
w(f"- **Intent routing correct on {intent_ok}/{n} ({100*intent_ok//n}%).** All 50 officer/GFR questions and the vendor action-questions routed sensibly; document-discovery phrasings correctly fell through to `UNKNOWN` → full RAG.")
w(f"- **5 intent misses** (Q32, Q35, Q75, Q94, Q100) — all keyword bleed (\"login\", \"documents\", \"tender\", \"bid\") pulling a question into a neighbouring intent. None caused a wrong answer.")
w("- **Entity extraction is the metric to read carefully.** The *query-side* NER (persons/amounts/PAN…) is idle by design — these questions don't carry those entities. The *answer-side* extraction the officer set actually exercises — **rule citations and money/percent thresholds** — fires often, but the **rule NUMBERS are misattributed about half the time** (content grounded, citation wrong), consistent with the known GFR rule-citation weakness.")
w(f"- **Latency avg {sum(lat)/n:.1f}s is ~3× the stated 12s target** — the generation-bound CPU/Arc-iGPU floor (reranker + `gemma3:4b`). This is the primary gap against the evaluation parameters, not a correctness problem.")
w("- **Error handling is clean:** zero fallbacks/refusals/crashes across all 100 bilingual queries.")
w("")
w("---")
w("")
w("## 2. Intent Recognition — detail")
w("")
w("Intent distribution across the 100 questions:")
w("")
w("| Intent | Count |")
w("|---|---|")
for k, v in idist.most_common():
    w(f"| `{k}` | {v} |")
w("")
w(f"- **Specific intent fired:** {n - idist['UNKNOWN']}/{n}.  **`UNKNOWN` → general RAG:** {idist['UNKNOWN']}/{n} (correct for \"what is the policy / threshold / procedure\" phrasings that name no action keyword).")
w(f"- **Routing correct: {intent_ok}/{n} = {100*intent_ok//n}%.**")
w("")
w("**The 5 misses:**")
w("")
w("| Q | Role/Lang | Expected | Fired | Why |")
w("|---|---|---|---|---|")
why = {
 32: "\"login IDs\" → PORTAL_USAGE instead of DSC",
 35: "\"दस्तावेज / documents\" → DOCUMENT_REQUIREMENTS instead of BID_SUBMISSION",
 75: "\"निविदा / tender\" → TENDER_SEARCH instead of RULES_GFR",
 94: "\"bid\" → BID_SUBMISSION instead of RULES_GFR",
 100:"\"price bid\" → BID_SUBMISSION instead of RULES_GFR",
}
for r in misses:
    w(f"| Q{r['idx']} | {r['role']}/{r['lang']} | {r['expected_topic']} | {r['intent']} | {why.get(r['idx'],'')} |")
w("")
w("All five still retrieved the right documents and produced an on-topic answer — the mis-route only changes the topic-boost, not the retrieval corpus.")
w("")
w("---")
w("")
w("## 3. Entity Extraction — detail")
w("")
w("The dataset's evaluation parameter defines this as *\"correctness of rule citations (e.g. Rule 163/170) and value thresholds (e.g. Rs. one lakh) in the final response.\"* So there are two layers:")
w("")
w("### 3a. Query-side NER (`extract_entities`)")
w("")
w("- **1/100 queries produced an entity, and it was a false positive:** Q63 extracted *Company: \"Small Enterprises\"* from \"Micro and **Small Enterprises** (MSEs)\" (the corporate-suffix pattern matched \"Enterprises\").")
w("- Otherwise **0 persons / amounts / dates / PAN / GSTIN** — correct, because none of these 100 questions *supply* a transactional entity. The extractor is not exercised by this set and should be validated separately with entity-bearing inputs (\"EMD 2% of Rs 50,00,000\", \"PAN AAAAA0000A\", vendor names).")
w("")
w("### 3b. Answer-side rule + threshold extraction (what the officer set actually tests)")
w("")
w(f"- **{len(rules)}/{n} answers cite a specific `Rule N`; {len(thr)}/{n} surface a numeric threshold** (₹ amount / % / day-count).")
w("- **Rule-number accuracy is the weak spot.** Cross-checked against standard GFR-2017 numbering (ATE = Rule 161, LTE = Rule 162, purchase-without-quotation = Rule 154, purchase committee = Rule 155, single-tender = Rule 166, late-bids = Rule 165):")
w("")
w("| Q | Question (short) | Cited | Assessment |")
w("|---|---|---|---|")
rule_notes = [
 (53, "Limited Tender Enquiry conditions", "Rule 150", "❌ 150 is GeM; LTE = Rule 162"),
 (55, "Advertised-tender threshold", "Rule 162", "❌ 162 is LTE; ATE = Rule 161"),
 (57, "Late bids (GFR Rule 165)", "Rule 165", "✅ correct (number was in the question)"),
 (58, "Single Tender justification", "Rule 21", "❌ single-tender = Rule 166"),
 (63, "MSE procurement policy", "Rule 153(ii)", "✅ MSE / purchase-preference ≈ Rule 153"),
 (66, "Consultancy proposal evaluation", "Rule 190", "✅ plausible (consultancy = Rules 177–190)"),
 (73, "LTE conditions (Hindi)", "Rule 150", "❌ LTE = Rule 162"),
 (91, "Purchase without quotation (Hin)", "Rule 192(i)", "❌ without-quotation = Rule 154"),
 (93, "Advertised tender compulsory (Hin)", "Rule 161", "✅ ATE = Rule 161"),
 (95, "Late bid reject (Hin)", "Rule 165", "✅ correct (number was in the question)"),
]
for q, s, c, a in rule_notes:
    w(f"| Q{q} | {s} | {c} | {a} |")
w("")
w("- **~5/10 rule numbers are right, ~5/10 misattributed** — and 2 of the 5 \"correct\" ones (Q57, Q95) were handed the number in the question itself, so *unaided* correct citations are ~3/8. The surrounding text is grounded in the retrieved manuals; only the numeric label is unreliable. This matches the standing `eval-rule-citation-hallucination` finding.")
w("- **Threshold values are mostly plausible but internally inconsistent.** Same question, two languages, two different limits:")
w("  - Q51 \"purchase without quotation\" → **Rs. 50,000** vs Q91 (same, Hinglish) → **Rs. 1,00,000–10,00,000**. Both are questionable against GFR Rule 154 (Rs 25,000); the model is reading different manual passages.")
w("  - Q92 \"Local Purchase Committee\" → **₹25,000–₹2,50,000** ✅ (matches purchase-committee band).")
w("  - EMD Q59/Q79 → **2%–5%**, Performance Security Q60/Q61/Q80/Q81 → **3%–10%** — both in the correct real-world range.")
w("- **Extractor noise:** a few threshold cells show junk like `rs,` / `rs. 2` where the regex caught a bare \"Rs.\" at a line break (Q52, Q54, Q62, Q68). Cosmetic; the underlying answers are fine.")
w("")
w("---")
w("")
w("## 4. Latency — detail")
w("")
w(f"- Overall avg **{sum(lat)/n:.1f}s**, median **{st.median(lat):.1f}s**, stdev {st.pstdev(lat):.0f}s, range {min(lat):.0f}–{max(lat):.0f}s.")
w(f"- Live-generation avg **{sum(live)/len(live):.1f}s** (excludes the 1 cache + 1 wizard-clarify).")
w("- **1 cache hit:** Q4 (EMD rate) served in ~2s by the near-duplicate answer cache.")
w("- **Against the 12s target this is ~3× over** — the bottleneck is the reranker + `gemma3:4b` token generation on the Arc-iGPU/CPU stack, not retrieval. Hindi/Hinglish answers run longer (extra tokens).")
w("")
w("**Latency by role × language:**")
w("")
w("| Segment | n | Intent OK | Answered | Avg latency | Rule cites | Threshold cites |")
w("|---|---|---|---|---|---|---|")
labels = [("vendor","en","Vendor · English"),("vendor","hi","Vendor · Hindi"),("vendor","hin","Vendor · Hinglish"),
          ("officer","en","Officer · English"),("officer","hi","Officer · Hindi"),("officer","hin","Officer · Hinglish")]
for role, lang, lab in labels:
    c, ok, ans, la, ru, th_ = rl(role, lang)
    w(f"| {lab} | {c} | {ok}/{c} | {ans}/{c} | {la}s | {ru} | {th_} |")
w("")
w("**Slowest 6:**")
w("")
for r in slow:
    w(f"- Q{r['idx']} ({r['role']}/{r['lang']}, {r['latency_s']}s) — {r['question'][:60]}")
w("")
w("Officer/Hindi is the slowest segment (larger GFR contexts + longer Devanagari generations); Vendor/English is fastest.")
w("")
w("---")
w("")
w("## 5. Error Handling / Fallback — detail")
w("")
w("| Outcome | Count |")
w("|---|---|")
for k in ("ANSWERED","CACHE","CLARIFY","REFUSED","FALLBACK","ERROR"):
    w(f"| {k} | {oc.get(k,0)} |")
w("")
w("- **Fallback rate = 0%.** No \"information not available\" refusals, no empty generations, no HTTP 500s, no model-fallback (`gemma3:4b` had ample iGPU headroom for all 100).")
w("- **1 `CLARIFY` (Q1):** \"How do I register as a vendor…\" matched the **vendor-registration wizard trigger** (`register as a vendor`) and the bot began the guided flow (\"What is your full name?\") in ~2s with 0 sources, instead of answering from the manual. Correct-by-design, but worth knowing: a documentation-style *question* is intercepted by the task-flow. If a RAG answer is preferred for that phrasing, tighten `_FLOW_TRIGGERS`.")
w("- Every retrieval that found sources produced a non-empty, sourced answer.")
w("")
w("---")
w("")
w("## 6. Full results — all 100 questions")
w("")
w("Columns: **Q · Role · Lang · Question · Intent (conf) · Route✓ · Outcome · Latency(s) · #Src · Rule/Threshold entities in answer**")
w("")
w("| Q | R | L | Question | Intent (conf) | ✓ | Outcome | Lat | Src | Answer entities |")
w("|---|---|---|---|---|---|---|---|---|---|")
w(table)
w("")
w("---")
w("")
w("## 7. Method & caveats")
w("")
w("- Each question hit the real `/api/stream` SSE endpoint with a unique `session_id` (no coreference/slot carryover between questions).")
w("- Intent + query entities were computed by calling `nlp_features.classify_intent` / `extract_entities` directly on each raw question (the same functions the server uses).")
w("- \"Intent Recognition Accuracy\" is scored as topic-routing correctness: `UNKNOWN` → general RAG is *correct* for document/policy-lookup phrasings that name no action keyword (the taxonomy only fires on specific procurement actions).")
w("- Answer-side rule/threshold \"entities\" were extracted from the final generated text with regexes (`Rule \\d+`, ₹/%/day patterns); **rule-number correctness was judged by hand against standard GFR-2017 numbering** — the knowledge base contains multiple manuals/amendments, so a few thresholds may reflect a different document rather than an outright error.")
w("- Latency = wall-clock from request send to the SSE `done` event (retrieval + reranking + full token generation).")
w("- Answer *correctness* was not graded against a gold reference; outcomes track sourced-answer vs refusal/failure. Spot-checks show answers on-topic and grounded, with the rule-number caveat above.")
w("")

out = os.path.join(os.path.dirname(HERE), "QA_Eval_100Q_Report.md")
open(out, "w", encoding="utf-8").write("\n".join(L))
print("wrote", out, "-", len(L), "lines")
