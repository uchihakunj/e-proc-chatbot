"""Compare legacy and adaptive Sarvam prompts on the four profiling queries.

Run from the repository root:
    python scratch/benchmark_adaptive_context.py

The script retrieves once per question, then generates one legacy-prompt answer
and one adaptive-prompt answer from the same evidence.  Results (including the
answers needed for a human quality review) are written to scratch/.
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "05_webui"))
sys.path.insert(0, str(ROOT / "04_embeddings_and_kg" / "scripts"))

import app

rag = app._rag_module
QUERIES = [
    "What is EMD and why is it required?",
    "What is Performance Security and when is it required?",
    "Should I purchase through GeM or through the Chhattisgarh e-Procurement portal? What is the difference?",
    "How can I issue a corrigendum after publishing a tender?",
]


def legacy_context(results):
    """The pre-change 7,000/1,600-character prefix-based construction."""
    parts, source_refs, used = [], [], 0
    for index, result in enumerate(results or [], 1):
        point = result.get("point")
        if not getattr(point, "payload", None):
            continue
        source = app.get_actual_filename(point.payload.get("source", ""))
        body = app.strip_chunk_header(point.payload.get("text", ""))[:1600]
        if parts and used + len(body) > 7000:
            break
        parts.append(f"[Source {index}: {source}]\n{body}")
        used += len(body)
        if source not in source_refs:
            source_refs.append(source)
    return "\n\n".join(parts), source_refs


def generate(messages):
    """Generate a complete answer while recording request-to-first-token timing."""
    started = time.perf_counter()
    first_token_ms, answer = None, []
    response = requests.post(
        "https://api.sarvam.ai/v1/chat/completions",
        headers={"api-subscription-key": os.environ["SARVAM_API_KEY"],
                 "Content-Type": "application/json"},
        json={"model": os.getenv("SARVAM_MODEL", "sarvam-30b"),
              # Match the live Sarvam request. This reasoning model can spend
              # much of a smaller cap on hidden reasoning and emit no answer.
              "messages": messages, "temperature": 0, "max_tokens": 4096,
              "stream": True},
        stream=True,
        timeout=120,
    )
    response.raise_for_status()
    for raw in response.iter_lines(decode_unicode=True):
        if not raw or not raw.startswith("data: ") or raw == "data: [DONE]":
            continue
        try:
            event = json.loads(raw[6:])
            choice = (event.get("choices") or [{}])[0]
            content = ((choice.get("delta") or {}).get("content") or
                       (choice.get("message") or {}).get("content") or
                       choice.get("text", ""))
        except json.JSONDecodeError:
            continue
        if content:
            if first_token_ms is None:
                first_token_ms = (time.perf_counter() - started) * 1000
            answer.append(content)
    return {
        "latency_ms": round((time.perf_counter() - started) * 1000, 1),
        "time_to_first_token_ms": round(first_token_ms or 0, 1),
        "answer": "".join(answer).strip(),
    }


def coverage_score(question, answer):
    """Transparent, lightweight quality guard; final review uses saved answers."""
    text = (answer or "").lower()
    expectations = {
        QUERIES[0]: ("emd", "bid security", "deposit", "security"),
        QUERIES[1]: ("performance", "security", "contract", "successful"),
        QUERIES[2]: ("gem", "e-procurement", "difference", "portal"),
        QUERIES[3]: ("corrigendum", "tender", "publish", "bid"),
    }[question]
    hits = sum(term in text for term in expectations)
    return {"matched_terms": hits, "expected_terms": len(expectations),
            "score": round(hits / len(expectations), 2)}


def main():
    rows = []
    for query in QUERIES:
        print(f"\n--- {query}")
        retrieve_start = time.perf_counter()
        results = app.retrieve_context(app.expand_query_for_retrieval(query),
                                       rerank_query=query)
        retrieval_ms = round((time.perf_counter() - retrieve_start) * 1000, 1)

        old_context, old_sources = legacy_context(results)
        adaptive = app.build_generation_context(query, results)
        old_messages = [
            {"role": "system", "content": app.SYSTEM_PROMPT + "\n\nAvailable source documents: " + ", ".join(old_sources)},
            {"role": "user", "content": f"Context:\n{old_context}\n\nQuestion: {query}\n\nAnswer:"},
        ]
        new_messages = [
            {"role": "system", "content": app.GENERATION_SYSTEM_PROMPT + "\n\nAvailable source documents: " + ", ".join(adaptive["source_refs"])},
            {"role": "user", "content": f"Context:\n{adaptive['context_text']}\n\nQuestion: {query}\n\nAnswer:"},
        ]
        old_prompt = "\n".join(message["content"] for message in old_messages)
        new_prompt = "\n".join(message["content"] for message in new_messages)
        old_run = generate(old_messages)
        new_run = generate(new_messages)
        row = {
            "question": query,
            "retrieval_ms": retrieval_ms,
            "before": {"prompt_tokens_estimate": rag.estimate_tokens(old_prompt),
                       "prompt_characters": len(old_prompt), "chunks": len(old_context.split("[Source ")) - 1,
                       **old_run, "coverage": coverage_score(query, old_run["answer"])},
            "after": {"prompt_tokens_estimate": rag.estimate_tokens(new_prompt),
                      "prompt_characters": len(new_prompt),
                      "chunks": adaptive["selected_chunk_count"],
                      "query_type": adaptive["query_type"],
                      "confidence": adaptive["top_confidence"],
                      **new_run, "coverage": coverage_score(query, new_run["answer"])},
        }
        rows.append(row)
        print(f"before: {row['before']['prompt_tokens_estimate']} tokens, {row['before']['latency_ms']} ms, coverage {row['before']['coverage']['score']}")
        print(f"after:  {row['after']['prompt_tokens_estimate']} tokens, {row['after']['latency_ms']} ms, coverage {row['after']['coverage']['score']}")

    summary = {
        "average_before_prompt_tokens": round(sum(r["before"]["prompt_tokens_estimate"] for r in rows) / len(rows), 1),
        "average_after_prompt_tokens": round(sum(r["after"]["prompt_tokens_estimate"] for r in rows) / len(rows), 1),
        "average_before_generation_ms": round(sum(r["before"]["latency_ms"] for r in rows) / len(rows), 1),
        "average_after_generation_ms": round(sum(r["after"]["latency_ms"] for r in rows) / len(rows), 1),
        "average_before_coverage": round(sum(r["before"]["coverage"]["score"] for r in rows) / len(rows), 2),
        "average_after_coverage": round(sum(r["after"]["coverage"]["score"] for r in rows) / len(rows), 2),
    }
    output = {"summary": summary, "queries": rows}
    destination = ROOT / "scratch" / "adaptive_context_benchmark_results.json"
    destination.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nSummary:", json.dumps(summary, indent=2))
    print(f"Saved detailed answers to {destination}")


if __name__ == "__main__":
    main()
