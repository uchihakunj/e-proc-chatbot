"""Run the 20-query human-style RAG benchmark against the production SSE API.

This benchmark is intentionally separate from ``production_120``.  Its data
contains reviewer-authored reference answers, expected source documents, chunk
evidence terms and answer concepts, allowing retrieval and answer quality to be
reported independently.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import sys
import time
from pathlib import Path

import numpy as np
import requests
from dotenv import load_dotenv


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

# These phrases identify known high-risk regressions. They are deliberately
# narrow: a clean result means the benchmark did not reproduce those mistakes,
# not that arbitrary natural-language output has been proven safe.
PROHIBITED_RESPONSE_PHRASES = (
    "password@123",
    "1 or 2 din",
    "1-2 days",
    "1–2 days",
)


def normalise_source(value: str) -> str:
    return Path(str(value or "").replace("\\", "/")).name.casefold()


def parse_sse(response):
    events = []
    for raw in response.iter_lines(decode_unicode=True):
        if not raw or not raw.startswith("data: "):
            continue
        try:
            events.append(json.loads(raw[6:]))
        except json.JSONDecodeError:
            events.append({"type": "parse_error", "raw": raw[6:]})
    return events


def literal_keyword_coverage(answer: str, keywords: list[str]) -> dict:
    """Case-insensitive literal coverage; reported as a diagnostic, not truth."""
    low = (answer or "").casefold()
    hits = [term for term in keywords if term.casefold() in low]
    return {
        "hit_keywords": hits,
        "missing_keywords": [term for term in keywords if term not in hits],
        "coverage": round(len(hits) / len(keywords), 3) if keywords else 1.0,
    }


def source_coverage(expected: list[str], sources: list[str]) -> dict:
    expected_norm = {normalise_source(source) for source in expected}
    actual_norm = {normalise_source(source) for source in sources}
    hits = sorted(expected_norm.intersection(actual_norm))
    return {
        "matched_expected_sources": hits,
        "missing_expected_sources": sorted(expected_norm - actual_norm),
        "coverage": round(len(hits) / len(expected_norm), 3) if expected_norm else 1.0,
    }


def safety_violations(answer: str) -> list[str]:
    low = (answer or "").casefold()
    return [phrase for phrase in PROHIBITED_RESPONSE_PHRASES if phrase in low]


def chunk_evidence_coverage(expected_groups: list[list[str]], context_results: list[dict]) -> dict:
    """Check whether each reviewer-authored evidence group occurs in a retrieved chunk."""
    context = "\n".join(
        str(result.get("text") or result.get("excerpt") or "")
        for result in context_results
    ).casefold()
    hits = []
    for group in expected_groups:
        matched = next((term for term in group if term.casefold() in context), None)
        hits.append({"alternatives": group, "matched": matched})
    covered = sum(item["matched"] is not None for item in hits)
    return {
        "groups": hits,
        "coverage": round(covered / len(expected_groups), 3) if expected_groups else 1.0,
    }


class SemanticScorer:
    """BGE-M3 cosine scorer with an explicit TF-IDF fallback for offline runs."""

    def __init__(self, model_name: str, device: str, disabled: bool = False):
        self.backend = "disabled" if disabled else None
        self.model = None
        if disabled:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name, device=device)
            self.backend = f"sentence_transformers:{model_name}"
        except Exception as exc:
            self.backend = f"tfidf_fallback:{type(exc).__name__}"

    def similarities(self, question: str, answer: str, reference: str) -> tuple[float | None, float | None]:
        if self.backend == "disabled" or not (answer or "").strip():
            return None, None
        texts = [question or "", answer or "", reference or ""]
        if self.model is not None:
            vectors = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return round(float(np.dot(vectors[0], vectors[1])), 4), round(float(np.dot(vectors[1], vectors[2])), 4)
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        matrix = TfidfVectorizer(ngram_range=(1, 2)).fit_transform(texts)
        return (
            round(float(cosine_similarity(matrix[0], matrix[1])[0, 0]), 4),
            round(float(cosine_similarity(matrix[1], matrix[2])[0, 0]), 4),
        )


def _extract_json_object(text: str) -> dict:
    match = re.search(r"\{.*\}", text or "", flags=re.DOTALL)
    if not match:
        return {"score": None, "pass": None, "reason": "Judge did not return JSON."}
    try:
        value = json.loads(match.group(0))
        score = value.get("overall_score", value.get("score"))
        if isinstance(score, (int, float)) and 1 <= score <= 5:
            dimensions = value.get("dimensions")
            if not isinstance(dimensions, dict):
                dimensions = {
                    key: value[key]
                    for key in ("groundedness", "relevance", "completeness",
                                "workflow_safety", "helpfulness")
                    if isinstance(value.get(key), (int, float))
                }
            dimensions = {
                str(key): float(dimension_score)
                for key, dimension_score in dimensions.items()
                if isinstance(dimension_score, (int, float)) and 1 <= dimension_score <= 5
            }
            # The model's boolean is not stable across otherwise identical score
            # anchors. Derive the benchmark pass from the documented threshold,
            # while retaining the model's raw value and dimensions for audit.
            return {
                "score": float(score),
                "pass": score >= 4,
                "model_pass": value.get("pass"),
                "dimensions": dimensions,
                "reason": str(value.get("reason", ""))[:300],
            }
    except json.JSONDecodeError:
        pass
    return {"score": None, "pass": None, "reason": "Judge returned invalid JSON."}


def build_judge_prompt(question: str, answer: str, reference: str | None) -> str:
    """Build a calibrated evaluation prompt, not a second answer-generation prompt.

    A reference-free judge cannot establish factual grounding from the question
    alone. It therefore scores answer quality and workflow safety only. The
    reference-aware judge assesses factual grounding and completeness separately.
    """
    common = (
        "You are calibrating a government-procurement RAG evaluation. Treat accurate paraphrases, "
        "synonyms, reordered steps, and different formatting as equivalent coverage. Do not require "
        "literal keyword overlap or the same structure as a reviewer reference. Do not penalise a "
        "careful answer for declining to invent an amount, threshold, rule number, or portal click path "
        "that is not supported. Penalise only material factual contradiction, a missing material action, "
        "unsafe cross-role workflow advice, or generic boilerplate that does not answer the question.\n\n"
        "Score anchors: 5 = fully correct/direct/safe; 4 = correct with only a minor omission; "
        "3 = partly useful but a material point is missing; 2 = substantially incomplete or questionable; "
        "1 = irrelevant, contradictory, or unsafe."
    )
    if reference is None:
        return (
            f"{common}\n\n"
            "This is a REFERENCE-FREE quality review. Do not claim to verify factual grounding without "
            "source evidence. Score relevance, helpfulness, and workflow safety only.\n\n"
            f"Question:\n{question}\n\nAssistant answer:\n{answer}\n\n"
            "Return only a valid JSON object with these fields: overall_score (your chosen integer from 1 to 5), "
            "pass (boolean), dimensions (object containing your chosen integer scores from 1 to 5 for relevance, "
            "helpfulness and workflow_safety), and reason (short string). Use your selected scores; do not copy "
            "a placeholder or default every dimension to 1. Set pass to true only when overall_score is 4 or 5."
        )
    return (
        f"{common}\n\n"
        "This is a REFERENCE-AWARE factual review. The reviewer reference defines the material facts, "
        "not wording to copy. Assess factual_grounding, material_completeness, workflow_safety and "
        "helpfulness independently.\n\n"
        f"Question:\n{question}\n\nReviewer reference:\n{reference}\n\nAssistant answer:\n{answer}\n\n"
        "Return only a valid JSON object with these fields: overall_score (your chosen integer from 1 to 5), "
        "pass (boolean), dimensions (object containing your chosen integer scores from 1 to 5 for "
        "factual_grounding, material_completeness, workflow_safety and helpfulness), and reason (short string). "
        "Use your selected scores; do not copy a placeholder or default every dimension to 1. Set pass to true "
        "only when overall_score is 4 or 5."
    )


def sarvam_judge(question: str, answer: str, reference: str | None, api_key: str, timeout: int) -> dict:
    if not api_key:
        return {"score": None, "pass": None, "reason": "SARVAM_API_KEY is not configured."}
    prompt = build_judge_prompt(question, answer, reference)
    try:
        response = requests.post(
            "https://api.sarvam.ai/v1/chat/completions",
            headers={"api-subscription-key": api_key, "Content-Type": "application/json"},
            json={
                "model": "sarvam-30b",
                "messages": [
                    {"role": "system", "content": "You are a calibrated RAG evaluation judge. Return JSON only."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
                "reasoning_effort": None,
                "max_tokens": 260,
                "stream": False,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        body = response.json()
        choice = (body.get("choices") or [{}])[0]
        content = (choice.get("message") or {}).get("content") or choice.get("text") or ""
        return _extract_json_object(content)
    except Exception as exc:
        return {"score": None, "pass": None, "reason": f"Judge error: {type(exc).__name__}: {exc}"[:300]}


def run_one(row: dict, endpoint: str, timeout: int, semantic: SemanticScorer,
            use_llm_judge: bool, api_key: str) -> dict:
    started = time.perf_counter()
    events, error, status_code = [], None, None
    try:
        with requests.post(
            endpoint,
            json={"query": row["query"], "session_id": f"human-20-{row['id']}", "diagnostics": True},
            stream=True,
            timeout=(10, timeout),
        ) as response:
            status_code = response.status_code
            response.raise_for_status()
            events = parse_sse(response)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    elapsed = round(time.perf_counter() - started, 3)

    context_events = [event for event in events if event.get("type") == "context"]
    context_results = context_events[-1].get("results", []) if context_events else []
    retrieved_sources = [result.get("actual_pdf") or result.get("source") or "" for result in context_results]
    done_events = [event for event in events if event.get("type") == "done"]
    done = done_events[-1] if done_events else {}
    answer = done.get("answer") or "".join(event.get("content", "") for event in events if event.get("type") == "token")
    final_sources = done.get("sources") or []
    keyword = literal_keyword_coverage(answer, row["expected_response_keywords"])
    retrieved_source = source_coverage(row["expected_source_documents"], retrieved_sources[:10])
    final_source = source_coverage(row["expected_source_documents"], final_sources)
    primary_expected_source = normalise_source((row["expected_source_documents"] or [""])[0])
    primary_source_matched = primary_expected_source in {
        normalise_source(source) for source in final_sources
    }
    chunk_coverage = chunk_evidence_coverage(row["expected_chunk_terms"], context_results[:10])
    question_answer_cosine, reference_answer_cosine = semantic.similarities(
        row["query"], answer, row["reference_answer"]
    )
    judge_without_reference = sarvam_judge(row["query"], answer, None, api_key, timeout) if use_llm_judge else None
    judge_with_reference = sarvam_judge(row["query"], answer, row["reference_answer"], api_key, timeout) if use_llm_judge else None
    return {
        **row,
        "detected_actor": done.get("detected_actor"),
        "detected_fine_intent": done.get("detected_intent"),
        "actor_correct": done.get("detected_actor") == row["expected_actor"],
        "fine_intent_correct": done.get("detected_intent") == row["expected_fine_intent"],
        "retrieved_sources_top10": retrieved_sources[:10],
        "final_sources": final_sources,
        "retrieved_expected_source": retrieved_source,
        "final_expected_source": final_source,
        "primary_expected_source_matched": primary_source_matched,
        "retrieved_expected_chunk": chunk_coverage,
        "response_keyword_coverage": keyword,
        "question_answer_cosine": question_answer_cosine,
        "reference_answer_cosine": reference_answer_cosine,
        "llm_judge_without_reference": judge_without_reference,
        "llm_judge_with_reference": judge_with_reference,
        "fallback_reason_code": done.get("fallback_reason_code"),
        "validation_issues": done.get("validation_issues") or [],
        "safety_violations": safety_violations(answer),
        "response_time_seconds": elapsed,
        "http_status": status_code,
        "error": error,
        "answer": answer,
    }


def mean(values: list[float | None]) -> float | None:
    usable = [value for value in values if value is not None]
    return round(statistics.mean(usable), 4) if usable else None


def pct(rows: list[dict], key: str) -> float:
    return round(100 * sum(bool(row.get(key)) for row in rows) / len(rows), 2) if rows else 0.0


def aggregate(rows: list[dict], semantic_backend: str) -> dict:
    latencies = [row["response_time_seconds"] for row in rows]
    judge_without = [row["llm_judge_without_reference"] for row in rows if row["llm_judge_without_reference"]]
    judge_with = [row["llm_judge_with_reference"] for row in rows if row["llm_judge_with_reference"]]
    latencies_summary = {
        "average": round(statistics.mean(latencies), 3),
        "median": round(statistics.median(latencies), 3),
        "p95": round(sorted(latencies)[max(0, int(len(latencies) * .95 + .999999) - 1)], 3),
        "maximum": round(max(latencies), 3),
    }
    routing_pass = all(row.get("actor_correct") and row.get("fine_intent_correct") for row in rows)
    no_errors = all(not row.get("error") for row in rows)
    no_safety_violations = all(not row.get("safety_violations") for row in rows)
    primary_source_match_percent = pct(rows, "primary_expected_source_matched")
    quality_gate = {
        "routing_100_percent": routing_pass,
        "no_request_errors": no_errors,
        "no_known_safety_regressions": no_safety_violations,
        "primary_source_match_at_least_70_percent": primary_source_match_percent >= 70.0,
        "p95_latency_at_most_6_seconds": latencies_summary["p95"] <= 6.0,
    }
    return {
        "total_queries": len(rows),
        "semantic_backend": semantic_backend,
        "actor_accuracy_percent": pct(rows, "actor_correct"),
        "fine_intent_accuracy_percent": pct(rows, "fine_intent_correct"),
        "expected_source_recall_top10_percent": round(100 * statistics.mean(row["retrieved_expected_source"]["coverage"] for row in rows), 2),
        "expected_source_recall_final_context_percent": round(100 * statistics.mean(row["final_expected_source"]["coverage"] for row in rows), 2),
        "expected_chunk_evidence_coverage_top10_percent": round(100 * statistics.mean(row["retrieved_expected_chunk"]["coverage"] for row in rows), 2),
        "literal_response_keyword_coverage_percent": round(100 * statistics.mean(row["response_keyword_coverage"]["coverage"] for row in rows), 2),
        "primary_expected_source_match_percent": primary_source_match_percent,
        "known_safety_violation_count": sum(len(row.get("safety_violations") or []) for row in rows),
        "question_answer_cosine_mean": mean([row["question_answer_cosine"] for row in rows]),
        "reference_answer_cosine_mean": mean([row["reference_answer_cosine"] for row in rows]),
        "llm_judge_without_reference_score_mean": mean([row["score"] for row in judge_without]),
        "llm_judge_without_reference_pass_percent": round(100 * sum(bool(row["pass"]) for row in judge_without) / len(judge_without), 2) if judge_without else None,
        "llm_judge_with_reference_score_mean": mean([row["score"] for row in judge_with]),
        "llm_judge_with_reference_pass_percent": round(100 * sum(bool(row["pass"]) for row in judge_with) / len(judge_with), 2) if judge_with else None,
        "fallback_count": sum(bool(row["fallback_reason_code"]) for row in rows),
        "latency_seconds": latencies_summary,
        "release_gate": {
            "checks": quality_gate,
            "passed": all(quality_gate.values()),
        },
    }


def write_outputs(rows: list[dict], semantic_backend: str):
    summary = aggregate(rows, semantic_backend)
    (HERE / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "aggregate_metrics.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = ["id", "persona", "language", "query", "expected_actor", "detected_actor", "expected_fine_intent", "detected_fine_intent", "response_time_seconds", "fallback_reason_code", "answer"]
    with (HERE / "results.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    report = ["# Human-style 20-query RAG benchmark", "", "## Aggregate metrics", ""]
    report.extend(f"- {key}: **{value}**" for key, value in summary.items() if key != "latency_seconds")
    report.extend(["", "## Per-query outcomes", "", "| ID | Persona | Source top-10 | Chunk evidence | Keywords | Q→A cosine | Reference cosine | Time |", "|---|---|---:|---:|---:|---:|---:|---:|"])
    for row in rows:
        report.append(
            f"| {row['id']} | {row['persona']} | {row['retrieved_expected_source']['coverage']:.0%} | "
            f"{row['retrieved_expected_chunk']['coverage']:.0%} | {row['response_keyword_coverage']['coverage']:.0%} | "
            f"{row['question_answer_cosine'] if row['question_answer_cosine'] is not None else 'n/a'} | "
            f"{row['reference_answer_cosine'] if row['reference_answer_cosine'] is not None else 'n/a'} | {row['response_time_seconds']:.2f}s |"
        )
    report.extend(["", "## Interpretation", "", "Literal keyword and cosine scores are diagnostic only: paraphrases can be correct with low literal overlap, and a question-answer cosine score does not prove factual grounding. The source/chunk measures and the reference-aware judge should be considered together."])
    (HERE / "benchmark_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://127.0.0.1:5000/api/stream")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--semantic-model", default="BAAI/bge-m3")
    parser.add_argument("--semantic-device", default="cpu")
    parser.add_argument("--skip-semantic", action="store_true")
    parser.add_argument("--llm-judge", action="store_true", help="Run both Sarvam judge variants; consumes API calls.")
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    dataset = json.loads((HERE / "dataset.json").read_text(encoding="utf-8"))
    if len(dataset) != 20:
        raise ValueError(f"Expected exactly 20 human queries, found {len(dataset)}")
    api_key = os.getenv("SARVAM_API_KEY", "")
    semantic = SemanticScorer(args.semantic_model, args.semantic_device, args.skip_semantic)
    rows = []
    for index, row in enumerate(dataset, 1):
        result = run_one(row, args.endpoint, args.timeout, semantic, args.llm_judge, api_key)
        rows.append(result)
        print(f"[{index:02d}/20] {row['id']} {result['response_time_seconds']:.2f}s", flush=True)
    summary = write_outputs(rows, semantic.backend)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
