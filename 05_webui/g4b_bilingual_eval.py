# -*- coding: utf-8 -*-
"""Test 10 questions in English + Hindi on the running chatbot (gemma3:4b + Arc).
Captures latency, outcome, language fidelity, table presence, sources, answer.
Writes g4b_bilingual_results.json incrementally."""
import sys, json, time, requests
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = "http://localhost:5000/api/stream"
REFUSAL = ["was not found in the available documents", "nahi mila", "नहीं मिला",
           "could not be generated"]

# 10 questions, each in English and Hindi
QUESTIONS = [
    ("Q1", "What is the step-by-step process for challan payment?",
           "चालान भुगतान की चरण-दर-चरण प्रक्रिया क्या है?"),
    ("Q2", "What is the step-by-step process for CHiPS vendor registration?",
           "CHiPS पर विक्रेता पंजीकरण की प्रक्रिया क्या है?"),
    ("Q3", "What are the main guidelines mentioned in the DSC manual?",
           "DSC मैनुअल में उल्लिखित मुख्य दिशानिर्देश क्या हैं?"),
    ("Q4", "What is EMD and when is it exempted?",
           "EMD क्या है और इसे कब छूट दी जाती है?"),
    ("Q5", "What are the main guidelines mentioned in the GeM manual?",
           "GeM मैनुअल में उल्लिखित मुख्य दिशानिर्देश क्या हैं?"),
    ("Q6", "What is the step-by-step process for EDGE browser setup?",
           "EDGE ब्राउज़र सेटअप की चरण-दर-चरण प्रक्रिया क्या है?"),
    ("Q7", "Under GFR and government rules, what is the procedure for MSME procurement?",
           "GFR और सरकारी नियमों के तहत MSME खरीद की प्रक्रिया क्या है?"),
    ("Q8", "What is the core objective of the e-Procurement project?",
           "e-Procurement परियोजना का मुख्य उद्देश्य क्या है?"),
    ("Q9", "What system settings or configurations are needed for CHiPS online?",
           "CHiPS ऑनलाइन के लिए कौन-सी सिस्टम सेटिंग्स आवश्यक हैं?"),
    ("Q10", "What is the step-by-step process for the auction manual?",
            "नीलामी मैनुअल की चरण-दर-चरण प्रक्रिया क्या है?"),
]


def devanagari_ratio(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    deva = sum(1 for c in letters if "ऀ" <= c <= "ॿ")
    return round(deva / len(letters), 2)


def run(qid, lang, q):
    t0 = time.time(); ttc = ttft = None; toks = []; sources = []; cached = False
    try:
        with requests.post(URL, json={"query": q, "session_id": f"{qid}_{lang}"},
                           stream=True, timeout=400) as r:
            for line in r.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                try: e = json.loads(line[6:])
                except json.JSONDecodeError: continue
                ty = e.get("type")
                if ty == "context" and ttc is None:
                    ttc = time.time() - t0
                    sources = [c.get("actual_pdf") or c.get("source") for c in e.get("results", [])]
                elif ty == "status" and "cached" in e.get("message", "").lower():
                    cached = True
                elif ty == "token":
                    if ttft is None: ttft = time.time() - t0
                    toks.append(e.get("content", ""))
        ans = "".join(toks).strip()
        total = round(time.time() - t0, 1)
        outcome = "REFUSED" if any(m in ans for m in REFUSAL) else ("CACHE" if cached else "ANSWERED")
        return {
            "id": qid, "lang": lang, "question": q, "outcome": outcome,
            "total_s": total, "ttc_s": round(ttc, 1) if ttc else None,
            "ttft_s": round(ttft, 1) if ttft else None,
            "chars": len(ans), "n_sources": len(sources),
            "sources": [s for s in sources if s][:4],
            "devanagari_ratio": devanagari_ratio(ans) if lang == "HI" else None,
            "has_table": ("|---" in ans or "|--" in ans or "| " in ans),
            "answer": ans,
        }
    except Exception as ex:
        return {"id": qid, "lang": lang, "question": q, "outcome": "ERROR",
                "total_s": round(time.time()-t0, 1), "error": str(ex), "answer": ""}


results = []
n = len(QUESTIONS) * 2
i = 0
for qid, en, hi in QUESTIONS:
    for lang, q in (("EN", en), ("HI", hi)):
        i += 1
        print(f"[{i}/{n}] {qid} {lang}: {q[:50]}...", flush=True)
        res = run(qid, lang, q)
        extra = f" deva={res.get('devanagari_ratio')}" if lang == "HI" else ""
        print(f"    -> {res['outcome']} total={res['total_s']}s ttc={res.get('ttc_s')}s "
              f"chars={res.get('chars')} src={res.get('n_sources')}{extra}", flush=True)
        results.append(res)
        with open("g4b_bilingual_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

# summary
import statistics as st
def med(xs): return round(st.median(xs), 1) if xs else 0
en_t = [r["total_s"] for r in results if r["lang"] == "EN" and r["outcome"] == "ANSWERED"]
hi_t = [r["total_s"] for r in results if r["lang"] == "HI" and r["outcome"] == "ANSWERED"]
print("\n===== SUMMARY =====")
print(f"EN answered: {len(en_t)}/10  median {med(en_t)}s  mean {round(st.mean(en_t),1) if en_t else 0}s")
print(f"HI answered: {len(hi_t)}/10  median {med(hi_t)}s  mean {round(st.mean(hi_t),1) if hi_t else 0}s")
hi_deva = [r["devanagari_ratio"] for r in results if r["lang"] == "HI" and r.get("devanagari_ratio") is not None]
print(f"HI devanagari ratio: min {min(hi_deva) if hi_deva else 0}  mean {round(st.mean(hi_deva),2) if hi_deva else 0}")
print(f"Refused/Error: {sum(1 for r in results if r['outcome'] in ('REFUSED','ERROR'))}/{n}")
print("done")
