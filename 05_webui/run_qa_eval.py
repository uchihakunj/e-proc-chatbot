"""
Q&A evaluation harness for the CHiPS e-Proc chatbot.

For each question it measures:
  - Intent Recognition  : classify_intent() label + confidence (local NLU)
  - Entity Extraction   : extract_entities() (local NLU)
  - Response Time       : full end-to-end latency of /api/stream
  - Error Handling      : outcome class (ANSWERED / REFUSED / CLARIFY /
                          CACHE / FALLBACK / ERROR) -> fallback rate

Writes qa_eval_results.json next to this file.
"""
import json
import re
import sys
import time
import requests

sys.path.insert(0, ".")
from nlp_features import classify_intent, extract_entities, entities_summary

STREAM_URL = "http://localhost:5000/api/stream"

REFUSAL_MARKERS = [
    "was not found in the available documents",
    "nahi mila",
    "नहीं मिला",
    "could not be generated",
]

QUESTIONS = [
    "What are the main guidelines mentioned in short term tender?",
    "What are the main guidelines mentioned in short tender?",
    "What is the core objective of Notification EMDExemption?",
    "What are the main guidelines mentioned in CVC Guidelines on Tenders and Contracts?",
    "What does the document regulate regarding Compilation Tenders Contracts?",
    "Under GFR and government rules, what is the procedure for Compilation Tenders Contracts?",
    "What are the main guidelines mentioned in Instructions to department users and bidders?",
    "What does the document regulate regarding Instructions for department users and bidders?",
    "Under GFR and government rules, what is the procedure for Instructions for department users and bidders?",
    "Where can I find the specific sections about Instructions for department users and bidders?",
    "What are the main guidelines mentioned in CVC guidelines?",
    "What is the core objective of CVC guidelines?",
    "What are the main guidelines regarding CVC guidelines?",
    "Is it mandatory to follow the rules of CVC guidelines?",
    "What are the main guidelines mentioned in the DSC manual?",
    "What is the core objective of the DSC manual?",
    "What procedure is prescribed under the DSC manual?",
    "What are the main guidelines mentioned in the DSC tutorial?",
    "Under GFR and government rules, what is the procedure for the tutorial?",
    "Where can I find the specific sections about the tutorial?",
    "What are the main guidelines mentioned in the final GFR?",
    "What does the final GFR regulate regarding 2024?",
    "What are the main guidelines mentioned in the GeM manual?",
    "Under GFR and government rules, what is the procedure for the GeM manual?",
    "What is the core objective of the GeM manual?",
    "What are the main guidelines mentioned in the GeM handbook?",
    "What does the GeM handbook regulate regarding the handbook?",
    "What are the main guidelines mentioned in the general financial rules?",
    "Under GFR and government rules, what is the procedure for general financial rules?",
    "What is the core objective of the IT Act Rules?",
    "What are the main guidelines mentioned in the procurement manual?",
    "What does the procurement manual regulate regarding procurement?",
    "What are the main guidelines mentioned in the procurement of works manual?",
    "What does the procurement of works manual regulate regarding procurement of works?",
    "What are the main guidelines mentioned in the MSME procurement policy?",
    "Under GFR and government rules, what is the procedure for MSME procurement?",
    "What are the main guidelines mentioned in PPM?",
    "Under GFR and government rules, what is the procedure for PPM?",
    "What is the core objective of the e-Procurement project?",
    "What are the main guidelines mentioned in the public procurement manual?",
    "What does the public procurement manual regulate regarding the public procurement manual?",
    "What is the step-by-step process for the auction manual?",
    "What are the troubleshooting steps mentioned in the auction manual?",
    "What is the step-by-step process for CHiPS bid submission?",
    "What is the step-by-step process for CHiPS vendor registration?",
    "What is the step-by-step process for EDGE browser setup?",
    "What system settings or configurations are needed for EDGE browser setup?",
    "What is the step-by-step process for challan payment?",
    "What is the step-by-step process for FAQs?",
    "What system settings or configurations are needed for CHiPS online?",
]


def run_one(q, idx):
    intent, conf = classify_intent(q)
    ents = extract_entities(q)
    ent_sum = entities_summary(ents)

    answer_parts = []
    statuses = []
    sources = []
    elapsed_srv = None
    err = None
    outcome = "ANSWERED"

    t0 = time.time()
    try:
        # unique session per question -> no coreference/slot carryover
        payload = {"query": q, "session_id": f"eval_{idx}"}
        with requests.post(STREAM_URL, json=payload, stream=True, timeout=400) as r:
            for line in r.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                try:
                    evt = json.loads(line[6:])
                except json.JSONDecodeError:
                    continue
                t = evt.get("type")
                if t == "token":
                    answer_parts.append(evt.get("content", ""))
                elif t == "status":
                    statuses.append(evt.get("message", ""))
                elif t == "context":
                    sources = [c.get("actual_pdf") or c.get("source")
                               for c in evt.get("results", [])]
                elif t == "done":
                    elapsed_srv = evt.get("elapsed")
                    if evt.get("sources"):
                        sources = [s if isinstance(s, str) else
                                   (s.get("actual_pdf") or s.get("source"))
                                   for s in evt["sources"]]
                elif t == "error":
                    err = evt.get("message")
                    outcome = "ERROR"
    except Exception as e:
        err = str(e)
        outcome = "ERROR"
    latency = round(time.time() - t0, 2)

    answer = "".join(answer_parts).strip()

    # Classify outcome (error already set above)
    joined_status = " | ".join(statuses)
    if outcome != "ERROR":
        if any(m in answer for m in REFUSAL_MARKERS):
            outcome = "REFUSED"
        elif "Switching to a lighter model" in joined_status:
            outcome = "FALLBACK"
        elif "Instant answer (cached)" in joined_status:
            outcome = "CACHE"
        elif not sources and answer:
            # clarification / greeting style (no retrieval sources)
            outcome = "CLARIFY"
        elif not answer:
            outcome = "ERROR"
            err = err or "empty answer"

    return {
        "idx": idx,
        "question": q,
        "intent": intent,
        "intent_conf": conf,
        "entities": {k: v for k, v in ents.items() if v and k != "amounts_value"},
        "entities_summary": ent_sum,
        "outcome": outcome,
        "latency_s": latency,
        "server_elapsed": elapsed_srv,
        "n_sources": len(sources),
        "sources": sources[:5],
        "error": err,
        "answer": answer,
    }


def main():
    results = []
    for i, q in enumerate(QUESTIONS, 1):
        print(f"[{i}/{len(QUESTIONS)}] {q[:60]}...", flush=True)
        res = run_one(q, i)
        print(f"    -> intent={res['intent']}({res['intent_conf']}) "
              f"outcome={res['outcome']} latency={res['latency_s']}s "
              f"sources={res['n_sources']}", flush=True)
        results.append(res)
        with open("qa_eval_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    # Summary
    n = len(results)
    answered = sum(1 for r in results if r["outcome"] in ("ANSWERED", "CACHE", "FALLBACK"))
    refused = sum(1 for r in results if r["outcome"] == "REFUSED")
    clarify = sum(1 for r in results if r["outcome"] == "CLARIFY")
    fallback = sum(1 for r in results if r["outcome"] == "FALLBACK")
    errors = sum(1 for r in results if r["outcome"] == "ERROR")
    known_intent = sum(1 for r in results if r["intent"] != "UNKNOWN")
    with_ent = sum(1 for r in results if r["entities"])
    lat = [r["latency_s"] for r in results]
    lat_sorted = sorted(lat)
    print("\n===== SUMMARY =====")
    print(f"Total questions      : {n}")
    print(f"Answered (RAG)       : {answered}")
    print(f"Refused (fallback)   : {refused}")
    print(f"Clarify              : {clarify}")
    print(f"Model fallback fired : {fallback}")
    print(f"Errors               : {errors}")
    print(f"Known intent (!=UNK) : {known_intent}")
    print(f"With entities        : {with_ent}")
    print(f"Latency avg          : {sum(lat)/n:.1f}s")
    print(f"Latency min/median/max: {lat_sorted[0]}/{lat_sorted[n//2]}/{lat_sorted[-1]}s")
    print(f"Fallback rate        : {100*(refused+errors)/n:.1f}%")


if __name__ == "__main__":
    main()
