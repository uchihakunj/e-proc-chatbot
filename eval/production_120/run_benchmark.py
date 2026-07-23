"""Run and score the frozen benchmark through the production SSE endpoint."""

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
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "05_webui"))

from actor_boundary import (  # noqa: E402
    detect_response_language,
    language_is_consistent,
    prohibited_workflow_leaks,
)
from fine_intent_policy import (  # noqa: E402
    classify_fine_intent,
    detect_answer_mode,
    fine_intent_answer_guard,
    has_exact_answer_contract,
    source_family,
)
from nlp_features import classify_actor, classify_intent, detect_commodity  # noqa: E402


PRINT_LOCK = threading.Lock()
FALLBACK_MARKERS = (
    "sufficiently reliable section", "reliable section available nahi",
    "विश्वसनीय अनुभाग", "original question", "मूल प्रश्न",
)
MIN_CONCEPT_COVERAGE = 2 / 3

# Each tuple is an OR-group. A factual answer must cover the configured share.
CONCEPTS = {
    "procurement_methods_overview": [("gem",), ("tender", "निविदा"), ("direct", "सीधी", "प्रत्यक्ष")],
    "procurement_planning": [("need", "requirement", "आवश्यकता"), ("specification", "विनिर्देश"), ("approval", "sanction", "स्वीकृति"), ("gem", "tender", "निविदा"), ("purchase order", "po", "क्रय आदेश")],
    "procurement_method_selection": [("method", "विधि"), ("rule", "नियम"), ("approval", "justification", "स्वीकृति", "औचित्य")],
    "specification_preparation": [("specification", "विनिर्देश"), ("functional", "performance", "कार्यात्मक"), ("brand", "ब्रांड"), ("competition", "प्रतिस्पर्धा")],
    "approval_and_budget": [("budget", "बजट"), ("approval", "sanction", "स्वीकृति"), ("estimate", "अनुमान")],
    "bid_evaluation": [("technical", "तकनीकी"), ("financial", "price", "वित्तीय", "मूल्य"), ("evaluation", "मूल्यांकन")],
    "purchase_order": [("purchase order", "po", "क्रय आदेश"), ("approval", "स्वीकृति"), ("terms", "condition", "शर्त")],
    "inspection_and_acceptance": [("inspection", "निरीक्षण"), ("acceptance", "स्वीकृति"), ("specification", "विनिर्देश")],
    "payment_and_asset_entry": [("payment", "भुगतान"), ("asset", "stock", "संपत्ति", "स्टॉक"), ("invoice", "bill", "चालान", "बिल")],
    "gem_definition": [("gem",), ("marketplace", "बाजार")],
    "gem_eproc_comparison": [("gem",), ("e-procurement", "e procurement", "ई-प्रोक्योरमेंट"), ("tender", "निविदा")],
    "gem_direct_purchase_rule": [("gem",), ("direct", "सीधे", "प्रत्यक्ष"), ("threshold", "condition", "सीमा", "शर्त")],
    "gem_department_purchase_process": [("gem",), ("department", "विभाग"), ("purchase", "procure", "खरीद")],
    "gem_l1_purchase": [("gem",), ("l1", "l-1"), ("seller", "विक्रेता")],
    "gem_reverse_auction": [("gem",), ("reverse auction", "नीलामी")],
    "tender_method_definition": [("tender", "निविदा"), ("bid", "offer", "बोली", "प्रस्ताव"), ("supplier", "vendor", "source", "आपूर्तिकर्ता", "विक्रेता", "स्रोत")],
    "emd_definition": [("emd", "earnest money", "ईएमडी", "बोली सुरक्षा"), ("bid", "बोली")],
    "emd_exemption": [("emd", "ईएमडी"), ("exempt", "exemption", "छूट")],
    "emd_payment": [("emd", "ईएमडी"), ("payment", "pay", "deposit", "जमा", "भुगतान"), ("tender", "निविदा")],
    "emd_payment_failure": [("emd", "ईएमडी"), ("failed", "failure", "विफल"), ("debit", "कट")],
    "emd_refund_unsuccessful_bidder": [("emd", "ईएमडी"), ("refund", "return", "वापस", "वापसी"), ("unsuccessful", "असफल")],
    "emd_refund_l1_bidder": [("emd", "ईएमडी"), ("l1", "l-1", "successful bidder")],
    "emd_remittance_to_department": [("emd", "ईएमडी"), ("refund", "remit", "वापसी"), ("department", "विभाग")],
    "vendor_registration": [("vendor", "supplier", "विक्रेता"), ("registration", "register", "पंजीकरण"), ("portal", "पोर्टल")],
    "vendor_registration_documents": [("document", "दस्तावेज"), ("registration", "पंजीकरण")],
    "vendor_registration_fee": [("registration", "पंजीकरण"), ("fee", "payment", "शुल्क", "भुगतान")],
    "password_recovery": [("password", "पासवर्ड"), ("reset", "recover", "forgot", "भूल")],
    "dsc_obtainment": [("dsc", "digital signature", "डिजिटल हस्ताक्षर"), ("certificate", "प्रमाणपत्र")],
    "dsc_mapping": [("dsc", "digital signature", "डिजिटल हस्ताक्षर"), ("map", "mapping", "register", "जोड़")],
    "dsc_login_problem": [("dsc",), ("login", "लॉगिन"), ("browser", "token", "certificate")],
    "bid_submission_portal_steps": [("bid", "बोली"), ("technical", "तकनीकी"), ("price", "financial", "मूल्य", "वित्तीय"), ("submit", "जमा")],
    "tender_eligibility": [("eligib", "पात्र"), ("tender", "bid", "निविदा", "बोली")],
    "bidder_corrigendum_tracking": [("corrigendum", "शुद्धिपत्र"), ("view", "check", "track", "देख")],
    "bid_deletion_after_corrigendum": [("corrigendum", "शुद्धिपत्र"), ("bid", "बोली"), ("delete", "resubmit", "हट", "दोबारा")],
    "auction_participation": [("auction", "नीलामी"), ("bid", "बोली"), ("participat", "भाग")],
    "tender_creation_portal_steps": [("tender", "निविदा"), ("portal", "पोर्टल"), ("create", "upload", "बना", "अपलोड")],
    "tender_publication_portal_steps": [("tender", "निविदा"), ("publish", "प्रकाशित"), ("portal", "पोर्टल")],
    "corrigendum_portal_steps": [("corrigendum", "शुद्धिपत्र"), ("portal", "पोर्टल"), ("publish", "submit", "जारी", "प्रकाशित")],
    "bid_opening_portal_steps": [("bid", "बोली"), ("open", "खोल"), ("technical", "price", "तकनीकी", "मूल्य")],
    "corrigendum_policy": [("corrigendum", "शुद्धिपत्र"), ("amend", "change", "संशोधन", "परिवर्तन")],
    "mixed_role_clarification": [("department", "buyer", "vendor", "bidder", "विभाग", "विक्रेता", "बोलीदाता")],
}


def percentile(values, p):
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)


def normalized_source(value):
    return Path(str(value or "").replace("\\", "/")).name.casefold()


def concept_score(intent, answer):
    groups = CONCEPTS.get(intent, ())
    if not groups:
        return 1.0
    low = (answer or "").casefold()
    hit = sum(any(term.casefold() in low for term in group) for group in groups)
    return hit / len(groups)


def is_generic_fallback(answer):
    """Return True only for the benchmark's known generic fallback templates."""
    low = (answer or "").casefold()
    return any(marker.casefold() in low for marker in FALLBACK_MARKERS)


def score_answer(row, answer):
    """Score answer usefulness without crediting concept-rich fallback templates."""
    fallback_used = is_generic_fallback(answer)
    cscore = concept_score(row["expected_fine_intent"], answer)
    numbered_steps = len(re.findall(r"(?m)^\s*\d+[.)]\s+", answer or ""))
    factual_ok = (
        bool((answer or "").strip())
        and not fallback_used
        and cscore >= MIN_CONCEPT_COVERAGE
    )
    procedural_ok = (not row["procedural"]) or (
        not fallback_used and (numbered_steps >= 3 or cscore >= 0.8)
    )
    return {
        "fallback_used": fallback_used,
        "concept_coverage": round(cscore, 3),
        "answer_factual_correctness": factual_ok,
        "numbered_step_count": numbered_steps,
        "procedural_completeness": procedural_ok,
    }


def serialize_context_result(result, rank):
    """Keep the retrieval evidence emitted by the production SSE endpoint."""
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


def classify_local(query):
    actor, actor_conf = classify_actor(query)
    coarse, coarse_conf = classify_intent(query)
    commodity = detect_commodity(query)
    fine, fine_conf = classify_fine_intent(query, actor, coarse, commodity)
    return actor, actor_conf, coarse, coarse_conf, commodity, fine, fine_conf


def run_one(row, endpoint, timeout):
    started = time.perf_counter()
    actor, actor_conf, coarse, coarse_conf, commodity, fine, fine_conf = classify_local(row["query"])
    error = None
    status_code = None
    events = []
    try:
        with requests.post(
            endpoint,
            json={
                "query": row["query"],
                "session_id": f"prod-bench-120-{row['id']}",
                "diagnostics": True,
            },
            stream=True,
            timeout=(10, timeout),
        ) as response:
            status_code = response.status_code
            response.raise_for_status()
            events = parse_sse(response)
    except Exception as exc:  # evidence is recorded instead of aborting the full run
        error = f"{type(exc).__name__}: {exc}"
    response_time = time.perf_counter() - started

    context_events = [e for e in events if e.get("type") == "context"]
    context_results = context_events[-1].get("results", []) if context_events else []
    context_trace = [serialize_context_result(result, rank) for rank, result in enumerate(context_results, 1)]
    top_sources = [r.get("actual_pdf") or r.get("source") or "" for r in context_results]
    top_families = [source_family(s) for s in top_sources]
    done_events = [e for e in events if e.get("type") == "done"]
    done = done_events[-1] if done_events else {}
    final_sources = done.get("sources") or []
    final_families = [source_family(s) for s in final_sources]
    token_text = "".join(e.get("content", "") for e in events if e.get("type") == "token")
    answer = done.get("answer") or token_text
    answer_scores = score_answer(row, answer)
    answer_language = detect_response_language(answer) if answer else "unknown"
    expected_families = set(row["expected_document_families"])
    top5_ok = bool(expected_families.intersection(top_families[:5]))
    final_context_ok = bool(expected_families.intersection(final_families))
    actor_ok = actor == row["expected_actor"]
    intent_ok = fine == row["expected_fine_intent"]
    language_ok = bool(answer) and language_is_consistent(row["language"], answer)
    cscore = answer_scores["concept_coverage"]
    factual_ok = answer_scores["answer_factual_correctness"]
    numbered_steps = answer_scores["numbered_step_count"]
    procedural_ok = answer_scores["procedural_completeness"]
    leaks = list(prohibited_workflow_leaks(row["expected_actor"], answer or ""))
    guard_ok, guard_issues = fine_intent_answer_guard(fine, answer or "", row["query"])
    unsupported = [issue for issue in guard_issues if not issue.startswith("missing:")]
    fallback_used = answer_scores["fallback_used"]
    answer_mode = detect_answer_mode(row["query"], fine)
    # This is deliberately an additional metric: existing frozen actor/intent
    # and factual scoring stay unchanged, while narrow questions can no longer
    # receive full credit for an adjacent generic workflow.
    exact_question_ok = guard_ok if has_exact_answer_contract(row["query"], fine) else factual_ok
    retrieved_norm = {normalized_source(s) for s in top_sources}
    citation_ok = bool(final_sources) and all(normalized_source(s) in retrieved_norm for s in final_sources) and final_context_ok
    stream_ok = (
        len(done_events) == 1
        and not any(e.get("type") in ("error", "parse_error") for e in events)
        and bool(answer.strip())
        and (not token_text or token_text.strip() == answer.strip())
    )

    if row["expected_fine_intent"] == "mixed_role_clarification" and any(
        term in (answer or "").casefold() for term in ("which role", "clarify", "department or vendor", "भूमिका")
    ):
        classification = "Expected clarification"
    elif all((actor_ok, intent_ok, language_ok, top5_ok, final_context_ok, factual_ok,
              procedural_ok, citation_ok, not unsupported, not leaks, not fallback_used,
              stream_ok, error is None)):
        classification = "Pass"
    elif actor_ok and factual_ok and error is None and stream_ok:
        classification = "Partial"
    else:
        classification = "Fail"

    return {
        **row,
        "detected_actor": actor,
        "actor_confidence": actor_conf,
        "coarse_intent": coarse,
        "coarse_intent_confidence": coarse_conf,
        "commodity": commodity,
        "detected_fine_intent": fine,
        "fine_intent_confidence": fine_conf,
        "answer_language": answer_language,
        "retrieved_sources": top_sources,
        "retrieved_document_families": top_families,
        "context_results": context_trace,
        "reranked_top10": context_trace[:10],
        "final_sources": final_sources,
        "final_document_families": final_families,
        "correct_evidence_top5": top5_ok,
        "correct_evidence_final_context": final_context_ok,
        "actor_correct": actor_ok,
        "fine_intent_correct": intent_ok,
        "language_correct": language_ok,
        "answer_factual_correctness": factual_ok,
        "answer_mode": answer_mode,
        "exact_question_answering": exact_question_ok,
        "concept_coverage": round(cscore, 3),
        "procedural_completeness": procedural_ok,
        "numbered_step_count": numbered_steps,
        "citation_correctness": citation_ok,
        "unsupported_claims": unsupported,
        "workflow_leakage": leaks,
        "fallback_used": fallback_used,
        "stream_consistent": stream_ok,
        "completion_event_count": len(done_events),
        "sse_event_types": [event.get("type", "unknown") for event in events],
        "diagnostic_events": [event for event in events if event.get("type") == "diagnostic"],
        "fallback_reason_code": done.get("fallback_reason_code") or done.get("fallback_reason"),
        "validation_issues": done.get("validation_issues") or [],
        "response_time_seconds": round(response_time, 3),
        "http_status": status_code,
        "error": error,
        "classification": classification,
        "answer": answer,
    }


def confusion(rows, expected_key, detected_key):
    labels = sorted({r[expected_key] for r in rows} | {r[detected_key] for r in rows})
    matrix = {expected: {detected: 0 for detected in labels} for expected in labels}
    for row in rows:
        matrix[row[expected_key]][row[detected_key]] += 1
    return {"labels": labels, "matrix": matrix}


def pct(rows, key):
    return round(100 * sum(bool(r[key]) for r in rows) / len(rows), 2)


def aggregate(rows):
    latencies = [r["response_time_seconds"] for r in rows]
    return {
        "total": len(rows),
        "classification_counts": dict(Counter(r["classification"] for r in rows)),
        "actor_accuracy_percent": pct(rows, "actor_correct"),
        "fine_intent_accuracy_percent": pct(rows, "fine_intent_correct"),
        "retrieval_top5_accuracy_percent": pct(rows, "correct_evidence_top5"),
        "final_context_accuracy_percent": pct(rows, "correct_evidence_final_context"),
        "answer_accuracy_percent": pct(rows, "answer_factual_correctness"),
        "exact_question_answering_accuracy_percent": pct(rows, "exact_question_answering"),
        "citation_accuracy_percent": pct(rows, "citation_correctness"),
        "procedural_completeness_percent": pct(rows, "procedural_completeness"),
        "language_accuracy_percent": pct(rows, "language_correct"),
        "fallback_rate_percent": pct(rows, "fallback_used"),
        "workflow_leakage_rate_percent": pct(rows, "workflow_leakage"),
        "stream_consistency_percent": pct(rows, "stream_consistent"),
        "latency_seconds": {
            "median": round(statistics.median(latencies), 3),
            "p90": round(percentile(latencies, 0.90), 3),
            "p95": round(percentile(latencies, 0.95), 3),
            "maximum": round(max(latencies), 3),
        },
        "by_bucket": {
            bucket: {
                "count": len(group),
                "actor_accuracy_percent": pct(group, "actor_correct"),
                "fine_intent_accuracy_percent": pct(group, "fine_intent_correct"),
                "answer_accuracy_percent": pct(group, "answer_factual_correctness"),
                "pass_percent": round(100 * sum(r["classification"] == "Pass" for r in group) / len(group), 2),
            }
            for bucket, group in sorted(
                ((b, [r for r in rows if r["bucket"] == b]) for b in {r["bucket"] for r in rows})
            )
        },
        "by_language": {
            language: {
                "count": len(group),
                "actor_accuracy_percent": pct(group, "actor_correct"),
                "fine_intent_accuracy_percent": pct(group, "fine_intent_correct"),
                "language_accuracy_percent": pct(group, "language_correct"),
                "answer_accuracy_percent": pct(group, "answer_factual_correctness"),
            }
            for language, group in sorted(
                ((lang, [r for r in rows if r["language"] == lang]) for lang in {r["language"] for r in rows})
            )
        },
    }


def write_outputs(rows):
    (HERE / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = aggregate(rows)
    summary["actor_confusion_matrix"] = confusion(rows, "expected_actor", "detected_actor")
    summary["fine_intent_confusion_matrix"] = confusion(rows, "expected_fine_intent", "detected_fine_intent")
    (HERE / "aggregate_metrics.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = [
        "id", "bucket", "language", "query", "expected_actor", "detected_actor",
        "actor_confidence", "expected_fine_intent", "detected_fine_intent",
        "fine_intent_confidence", "answer_language", "expected_document_families",
        "retrieved_document_families", "final_document_families", "correct_evidence_top5",
        "correct_evidence_final_context", "answer_factual_correctness", "procedural_completeness",
        "citation_correctness", "unsupported_claims", "workflow_leakage", "fallback_used",
        "fallback_reason_code", "validation_issues", "context_results", "diagnostic_events",
        "stream_consistent", "response_time_seconds", "classification", "error", "answer",
    ]
    with (HERE / "results.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = dict(row)
            for key in (
                "expected_document_families", "retrieved_document_families",
                "final_document_families", "unsupported_claims", "workflow_leakage",
                "validation_issues", "context_results", "diagnostic_events",
            ):
                out[key] = json.dumps(out[key], ensure_ascii=False)
            writer.writerow(out)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://127.0.0.1:5000/api/stream")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=150)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    dataset = json.loads((HERE / "dataset.json").read_text(encoding="utf-8"))
    total = len(dataset)
    results = []
    if args.resume and (HERE / "progress.json").exists():
        results = json.loads((HERE / "progress.json").read_text(encoding="utf-8"))
        completed_ids = {row["id"] for row in results}
        dataset = [row for row in dataset if row["id"] not in completed_ids]
        print(f"Resuming with {len(results)}/{total} completed; {len(dataset)} remaining.", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_one, row, args.endpoint, args.timeout): row for row in dataset}
        for future in as_completed(futures):
            row = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {**row, "classification": "Fail", "error": f"runner: {exc}", "response_time_seconds": 0}
            results.append(result)
            with PRINT_LOCK:
                print(f"[{len(results):03d}/{total}] Q{row['id']:03d} {result['classification']} {result['response_time_seconds']}s", flush=True)
            # Crash-safe progress evidence. This is not used for final aggregation.
            (HERE / "progress.json").write_text(
                json.dumps(sorted(results, key=lambda r: r["id"]), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
    results.sort(key=lambda r: r["id"])
    summary = write_outputs(results)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
