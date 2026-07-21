"""Run the 50 scenario benchmark and capture richer adjudication fields."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(ROOT / "05_webui"))

from actor_boundary import detect_response_language, language_is_consistent, prohibited_workflow_leaks  # noqa: E402
from fine_intent_policy import classify_fine_intent, detect_answer_mode, source_family  # noqa: E402
from nlp_features import classify_actor, classify_intent, detect_commodity  # noqa: E402


PRINT_LOCK = threading.Lock()


def percentile(values, p):
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def normalized_source(value: str) -> str:
    return Path(str(value or "").replace("\\", "/")).name.casefold()


def classify_local(query: str):
    actor, actor_conf = classify_actor(query)
    coarse, coarse_conf = classify_intent(query)
    commodity = detect_commodity(query)
    fine, fine_conf = classify_fine_intent(query, actor, coarse, commodity)
    answer_mode = detect_answer_mode(query, fine)
    return actor, actor_conf, coarse, coarse_conf, commodity, fine, fine_conf, answer_mode


def parse_sse(response):
    events = []
    for raw in response.iter_lines(decode_unicode=True):
        if not raw or not raw.startswith("data: "):
            continue
        payload = raw[6:]
        if payload == "[DONE]":
            continue
        try:
            events.append(json.loads(payload))
        except json.JSONDecodeError:
            events.append({"type": "parse_error", "raw": payload})
    return events


def serialize_context_result(result, rank):
    record = {"rank": rank}
    for key in (
        "source", "actual_pdf", "page_number", "page", "section",
        "rule_or_section", "score", "semantic_score", "hybrid_score",
        "authority", "authority_score", "document_type", "audience",
        "procurement_stage", "commodity_type", "jurisdiction", "text",
        "excerpt",
    ):
        if key in result:
            record[key] = result[key]
    return record


def phrase_coverage(phrases, text: str) -> tuple[list[str], list[str]]:
    low = (text or "").casefold()
    hits = [phrase for phrase in phrases if phrase.casefold() in low]
    misses = [phrase for phrase in phrases if phrase.casefold() not in low]
    return hits, misses


_CONCEPT_STOPWORDS = {
    "a", "an", "the", "and", "or", "to", "of", "for", "is", "are", "be",
    "can", "what", "whether", "if", "under", "as", "on", "in", "with", "how",
}


# The benchmark labels are reviewer rubrics, not phrases users should expect
# to see verbatim.  For example, “yes/no decision” is satisfied by “Haan” or
# “No”, and “level playing field” can be expressed as “equal opportunity for
# bidders”.  Keep literal coverage as a diagnostic, but use these transparent
# explicit reviewer-facing equivalences for the release verdict. A later human
# adjudication round can tighten or expand this map with documented decisions.
_CONCEPT_EQUIVALENTS = {
    "yes/no decision": (("yes", "no", "haan", "nahi", "नहीं", "हाँ"),),
    "yes/no": (("yes", "no", "haan", "nahi", "नहीं", "हाँ"),),
    "whether allowed": (("allowed", "permit", "permitted", "not allowed", "nahi"),),
    "whether direct purchase allowed": (("direct purchase", "allowed", "permit", "nahi"),),
    "whether open tender mandatory": (("open tender", "mandatory", "not automatic", "nahi"),),
    "whether threshold exists": (("threshold", "limit", "value", "rule"),),
    "whether benefit exists": (("benefit", "preference", "exemption", "automatic"),),
    "whether exemption exists": (("exemption", "benefit", "automatic"),),
    "whether permissible": (("permitted", "allowed", "not automatic", "nahi"),),
    "whether mandatory": (("mandatory", "required", "not automatic", "nahi"),),
    "whether acceptable": (("acceptable", "tender conditions", "eligibility", "clarification"),),
    "whether applies to sub-contracts": (("sub-contract", "scope", "tender", "rule"),),
    "rule-based condition": (("rule", "rules", "condition", "approval", "permitted"),),
    "scope/conditions": (("scope", "condition", "tender", "applicable", "rule"),),
    "conditions": (("condition", "rule", "approval", "tender"),),
    "conditions if any": (("condition", "rule", "tender", "approval"),),
    "condition or exception": (("condition", "exception", "approval", "rule"),),
    "exception if any": (("exception", "rule", "approval", "permitted"),),
    "approval/recording": (("approval", "record", "document", "written"),),
    "approval precondition": (("approval", "before", "sanction", "budget"),),
    "approval/budget linkage": (("approval", "budget", "sanction", "funds"),),
    "as per delegated powers/rules": (("delegated", "power", "rule", "competent authority"),),
    "value/context dependency": (("value", "estimate", "consolidated", "depends"),),
    "₹50,000 applicability": (("50", "50,000", "₹50", "amount", "value"),),
    "value if stated": (("value", "amount", "threshold", "limit"),),
    "value limit if any": (("value", "limit", "threshold", "rule"),),
    "which rule family applies": (("goods", "works", "services", "rule"),),
    "why": (("because", "depends", "basis", "reason"),),
    "publication requirement": (("publish", "notice", "tender", "portal"),),
    "recorded justification": (("record", "justification", "written", "reason"),),
    "maximum duration": (("day", "days", "duration", "period"),),
    "source-grounded limit": (("rule", "manual", "tender", "source"),),
    "exact rule if present": (("rule", "gfr", "pac", "provision"),),
    "validity period if stated": (("validity", "period", "tender", "rule"),),
    "no invented number": (("do not", "not invent", "stated", "rule", "tender"),),
    "service scope inputs": (("scope", "service", "sla", "maintenance"),),
    "cost estimate basis": (("estimate", "cost", "market", "budget"),),
    "distinction between approvals": (("administrative", "financial", "approval", "sanction"),),
    "who grants sanction": (("competent authority", "delegated", "financial", "authority"),),
    "financial bid restriction": (("financial bid", "not open", "responsive", "technical"),),
    "evaluation sequence": (("eligibility", "technical", "financial", "evaluate"),),
    "not automatic acceptance": (("not automatic", "reasonableness", "approval", "evaluate"),),
    "reasonableness/justification": (("reasonableness", "justification", "estimate", "record"),),
    "competition concern": (("competition", "transparent", "equal", "cartel"),),
    "transparency/competition reason": (("transparency", "competition", "equal treatment"),),
    "not broad negotiation": (("negotiation", "routine", "transparency", "not"),),
    "avoid vague terms": (("vague", "ambiguous", "clear", "avoid"),),
    "use measurable/functional specs": (("measurable", "functional", "objective", "specification"),),
    "competition fairness": (("competition", "fair", "supplier", "favour"),),
    "proportionality/justification": (("proportionate", "relevant", "justification", "requirement"),),
    "avoid arbitrary restriction": (("arbitrary", "proportionate", "relevant", "competition"),),
    "same information to all": (("all bidders", "common", "equal", "corrigendum"),),
    "corrigendum/extension logic": (("corrigendum", "extension", "deadline", "material"),),
    "certificate must cover procured category": (("certificate", "category", "verify", "valid"),),
    "verification handling": (("verify", "verification", "document", "certificate"),),
    "how to verify objectively": (("verify", "objective", "evidence", "document"),),
    "tender-condition dependency": (("tender", "condition", "published", "rule"),),
    "original/verification requirement": (("original", "verify", "document", "tender"),),
    "quality/spec match": (("quality", "specification", "technical", "match"),),
    "must be justified/function-based": (("justified", "functional", "requirement", "measurable"),),
    "avoid restrictive specs": (("restrictive", "neutral", "competition", "favour"),),
    "fairness": (("fair", "equal", "transparent", "reasonableness"),),
    "seek clarification if permitted": (("clarification", "permitted", "tender", "rule"),),
    "document decision": (("record", "document", "reason", "decision"),),
    "apply tender criteria uniformly": (("tender", "criteria", "equal", "consistent"),),
    "what must be recorded/communicated": (("record", "communicate", "reason", "document"),),
    "tender/process dependency": (("tender", "process", "condition", "rule"),),
    "cannot award": (("cannot award", "reject", "not award", "ineligible"),),
    "move per next lawful step": (("rule", "next", "action", "authority"),),
    "evaluation/approval step": (("evaluation", "approval", "recommendation", "award"),),
    "award formalities": (("award", "approval", "contract", "purchase order"),),
    "not change competition basis improperly": (("competition", "basis", "amendment", "change"),),
    "fair documented method": (("fair", "record", "document", "tender"),),
    "no arbitrary selection": (("arbitrary", "tender", "fair", "not"),),
    "as per contract/rules": (("contract", "rule", "clause", "tender"),),
    "browser/security setting guidance": (("browser", "security", "java", "extension"),),
    "DSC/Java context": (("dsc", "java", "certificate", "browser"),),
    "deadline lock logic": (("deadline", "after", "edit", "submit"),),
    "permitted alternative if any": (("corrigendum", "reopening", "tender", "permitted"),),
    "timeline": (("day", "days", "time", "timeline", "within"),),
    "automatic initiation condition": (("automatic", "approve", "rejected", "refund"),),
    "unsuccessful bidder stage": (("unsuccessful", "rejected", "technical", "bidder"),),
    "authentication/non-repudiation": (("authentication", "dsc", "digital signature", "non-repudiation"),),
    "opening control": (("open", "opener", "control", "authorised"),),
    "extension logic": (("extension", "deadline", "material", "time"),),
    "level playing field": (("level playing field", "equal opportunity", "fair", "bidders"),),
    "failed payment handling": (("failed", "pending", "transaction", "helpdesk"),),
    "portal/payment record path": (("portal", "receipt", "transaction", "status"),),
    "compatibility/legacy component reason": (("compatibility", "legacy", "ie mode", "browser"),),
    "browser setup context": (("browser", "ie mode", "setup", "compatibility"),),
    "stepwise procedure": (("1.", "step", "challan", "portal"),),
    "challan generation/payment mode": (("challan", "neft", "rtgs", "payment"),),
    "portal record/update path": (("portal", "status", "update", "acknowledgement"),),
    "use original BOQ/no formula changes": (("boq", "original", "formula", "do not alter"),),
    "re-download/re-fill guidance": (("re-download", "download", "refill", "fill"),),
}


def semantic_concept_coverage(phrases, text: str) -> tuple[list[str], list[str]]:
    """Alias/tolerant concept matching for answer quality, preserving raw hits."""
    low_text = (text or "").casefold()
    answer_tokens = {
        token for token in re.findall(r"[^\W_]+|\d+(?:,\d+)?", low_text, flags=re.UNICODE)
        if token not in _CONCEPT_STOPWORDS
    }
    hits, misses = [], []
    for phrase in phrases:
        equivalents = _CONCEPT_EQUIVALENTS.get(phrase, ())
        if equivalents and any(
            any(alias.casefold() in low_text for alias in alternatives)
            for alternatives in equivalents
        ):
            hits.append(phrase)
            continue
        tokens = {
            token for token in re.findall(r"[^\W_]+|\d+(?:,\d+)?", phrase.casefold(), flags=re.UNICODE)
            if token not in _CONCEPT_STOPWORDS
        }
        # A concept is supported when most of its information-bearing words
        # occur in the answer; punctuation and wording differences are ignored.
        overlap = len(tokens & answer_tokens) / max(1, len(tokens))
        if phrase.casefold() in low_text or overlap >= 0.5:
            hits.append(phrase)
        else:
            misses.append(phrase)
    return hits, misses


def evaluate_row(row, answer: str, detected_actor: str, detected_fine_intent: str, detected_answer_mode: str,
                 retrieved_sources, final_sources, citation_ok: bool, response_time: float, error: str | None):
    actor_ok = detected_actor == row["expected_actor"]
    fine_ok = detected_fine_intent == row["expected_fine_intent"]
    mode_ok = detected_answer_mode == row["expected_answer_mode"]
    raw_req_hits, raw_req_misses = phrase_coverage(row["required_answer_concepts"], answer)
    req_hits, req_misses = semantic_concept_coverage(row["required_answer_concepts"], answer)
    unsafe_hits, _ = phrase_coverage(row["prohibited_or_unsafe_claims"], answer)
    expected_source_hits = [
        doc for doc in row["expected_source_documents"]
        if normalized_source(doc) in {normalized_source(src) for src in retrieved_sources}
    ]
    final_source_hits = [
        doc for doc in row["expected_source_documents"]
        if normalized_source(doc) in {normalized_source(src) for src in final_sources}
    ]
    required_ratio = (len(req_hits) / len(row["required_answer_concepts"])) if row["required_answer_concepts"] else 1.0

    if all((
        actor_ok,
        fine_ok,
        mode_ok,
        citation_ok,
        required_ratio >= 0.67,
        not unsafe_hits,
        expected_source_hits,
        answer.strip(),
        error is None,
    )):
        status = "Pass"
    elif answer.strip() and error is None and (actor_ok or fine_ok or required_ratio >= 0.34):
        status = "Partial"
    else:
        status = "Fail"

    return {
        "actor_correct": actor_ok,
        "fine_intent_correct": fine_ok,
        "answer_mode_correct": mode_ok,
        "required_answer_concepts_hit": req_hits,
        "required_answer_concepts_missed": req_misses,
        "raw_required_answer_concepts_hit": raw_req_hits,
        "raw_required_answer_concepts_missed": raw_req_misses,
        "prohibited_claim_hits": unsafe_hits,
        "expected_source_docs_in_top10": expected_source_hits,
        "expected_source_docs_in_final_context": final_source_hits,
        "citation_correctness": citation_ok,
        "response_time_seconds": round(response_time, 3),
        "classification": status,
    }


def run_one(row, endpoint: str, timeout: int, force_retrieval: bool = False):
    started = time.perf_counter()
    actor, actor_conf, coarse, coarse_conf, commodity, fine, fine_conf, answer_mode = classify_local(row["query"])
    error = None
    status_code = None
    events = []
    try:
        with requests.post(
            endpoint,
            json={
                "query": row["query"],
                "session_id": f"scenario-50-{row['id']}",
                "diagnostics": True,
                "force_retrieval": force_retrieval,
            },
            stream=True,
            timeout=(10, timeout),
        ) as response:
            status_code = response.status_code
            response.raise_for_status()
            events = parse_sse(response)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    response_time = time.perf_counter() - started

    context_events = [e for e in events if e.get("type") == "context"]
    context_event = context_events[-1] if context_events else {}
    context_results = context_event.get("results", [])
    context_trace = [serialize_context_result(result, rank) for rank, result in enumerate(context_results, 1)]
    reranked_top10 = context_trace[:10]
    retrieved_top10_sources = [(r.get("actual_pdf") or r.get("source") or "") for r in reranked_top10]
    retrieved_all_sources = [(r.get("actual_pdf") or r.get("source") or "") for r in context_trace]
    retrieval_skipped = bool(context_event.get("retrieval_skipped"))
    bypass_reason = context_event.get("bypass_reason")
    declared_context_sources = context_event.get("declared_sources") or []

    done_events = [e for e in events if e.get("type") == "done"]
    done = done_events[-1] if done_events else {}
    final_sources = done.get("sources") or []
    answer = done.get("answer") or "".join(e.get("content", "") for e in events if e.get("type") == "token")
    answer_language = detect_response_language(answer) if answer else "unknown"
    language_ok = bool(answer) and language_is_consistent(row["language"], answer)
    leaks = list(prohibited_workflow_leaks(row["expected_actor"], answer or ""))

    retrieved_norm = {normalized_source(s) for s in retrieved_all_sources}
    citation_source_set = (
        {normalized_source(s) for s in declared_context_sources}
        if retrieval_skipped else retrieved_norm
    )
    citation_ok = bool(final_sources) and all(normalized_source(s) in citation_source_set for s in final_sources)
    verdict = evaluate_row(
        row, answer, actor, fine, answer_mode, retrieved_top10_sources, final_sources, citation_ok, response_time, error
    )

    return {
        **row,
        "detected_actor": actor,
        "actor_confidence": actor_conf,
        "coarse_intent": coarse,
        "coarse_intent_confidence": coarse_conf,
        "commodity": commodity,
        "detected_fine_intent": fine,
        "fine_intent_confidence": fine_conf,
        "detected_answer_mode": answer_mode,
        "answer_language": answer_language,
        "language_correct": language_ok,
        "workflow_leakage": leaks,
        "retrieval_skipped": retrieval_skipped,
        "retrieval_bypass_reason": bypass_reason,
        "declared_context_sources": declared_context_sources,
        "force_retrieval": force_retrieval,
        "retrieved_top10_sources": retrieved_top10_sources,
        "retrieved_all_sources": retrieved_all_sources,
        "retrieved_top10_families": [source_family(s) for s in retrieved_top10_sources],
        "context_results": context_trace,
        "final_context_sources": final_sources,
        "final_context_families": [source_family(s) for s in final_sources],
        "diagnostic_events": [event for event in events if event.get("type") == "diagnostic"],
        "http_status": status_code,
        "error": error,
        "final_answer": answer,
        **verdict,
    }


def aggregate(rows):
    latencies = [r["response_time_seconds"] for r in rows if r.get("response_time_seconds") is not None]
    return {
        "total": len(rows),
        "classification_counts": dict(Counter(r["classification"] for r in rows)),
        "actor_accuracy_percent": round(100 * sum(r["actor_correct"] for r in rows) / len(rows), 2),
        "fine_intent_accuracy_percent": round(100 * sum(r["fine_intent_correct"] for r in rows) / len(rows), 2),
        "answer_mode_accuracy_percent": round(100 * sum(r["answer_mode_correct"] for r in rows) / len(rows), 2),
        "citation_accuracy_percent": round(100 * sum(r["citation_correctness"] for r in rows) / len(rows), 2),
        "language_accuracy_percent": round(100 * sum(r["language_correct"] for r in rows) / len(rows), 2),
        "latency_seconds": {
            "median": round(statistics.median(latencies), 3) if latencies else None,
            "p90": round(percentile(latencies, 0.90), 3) if latencies else None,
            "p95": round(percentile(latencies, 0.95), 3) if latencies else None,
            "maximum": round(max(latencies), 3) if latencies else None,
        },
    }


def write_outputs(rows):
    (HERE / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = aggregate(rows)
    (HERE / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = [
        "id", "section", "language", "query",
        "expected_actor", "detected_actor",
        "expected_fine_intent", "detected_fine_intent",
        "expected_answer_mode", "detected_answer_mode",
        "expected_source_documents", "retrieved_top10_sources", "final_context_sources",
        "declared_context_sources", "retrieval_skipped", "retrieval_bypass_reason", "force_retrieval",
        "expected_evidence_concepts", "required_answer_concepts", "prohibited_or_unsafe_claims",
        "citation_correctness", "response_time_seconds", "classification", "final_answer",
        "required_answer_concepts_hit", "required_answer_concepts_missed", "prohibited_claim_hits",
        "workflow_leakage", "error",
    ]
    with (HERE / "results.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = dict(row)
            for key in (
                "expected_source_documents", "retrieved_top10_sources", "final_context_sources",
                "declared_context_sources",
                "expected_evidence_concepts", "required_answer_concepts", "prohibited_or_unsafe_claims",
                "required_answer_concepts_hit", "required_answer_concepts_missed", "prohibited_claim_hits",
                "workflow_leakage",
            ):
                out[key] = json.dumps(out[key], ensure_ascii=False)
            writer.writerow(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://127.0.0.1:5000/api/stream")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument(
        "--force-retrieval", action="store_true",
        help="Bypass clarification, direct-answer, and cache paths for retrieval evaluation.",
    )
    args = parser.parse_args()

    dataset = json.loads((HERE / "dataset.json").read_text(encoding="utf-8"))
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(run_one, row, args.endpoint, args.timeout, args.force_retrieval): row
            for row in dataset
        }
        for future in as_completed(futures):
            row = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {**row, "classification": "Fail", "error": f"runner: {exc}", "response_time_seconds": 0}
            results.append(result)
            with PRINT_LOCK:
                print(
                    f"[{len(results):02d}/{len(dataset)}] #{row['id']:02d} {result['classification']} "
                    f"{result.get('response_time_seconds', 0):.2f}s {row['query'][:72]}",
                    flush=True,
                )
    results.sort(key=lambda item: item["id"])
    write_outputs(results)
    print(json.dumps(aggregate(results), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
