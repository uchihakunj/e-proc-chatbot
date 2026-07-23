"""Generate the evidence and failure-only reports from frozen benchmark results."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent


CAUSES = (
    ("actor classification", lambda r: not r["actor_correct"], "05_webui/actor_policy.py; 05_webui/nlp_features.py", "Add only the failing phrase to the narrow actor signal/rule and add its regression case.", "High: actor changes affect retrieval and generation."),
    ("fine-intent classification", lambda r: r["actor_correct"] and not r["fine_intent_correct"], "05_webui/fine_intent_policy.py; 05_webui/nlp_features.py", "Add or refine only the missing fine-intent route and its evidence contract.", "Medium-high: overlapping keywords can reroute adjacent intents."),
    ("retrieval filtering", lambda r: r["fine_intent_correct"] and not r["correct_evidence_top5"], "05_webui/app.py; 04_embeddings_and_kg/scripts/embeddings_production.py", "Inspect expansion, metadata policy, hybrid scores and top-5 family filtering for the failing intent.", "Medium: broad retrieval changes can regress passing intents."),
    ("context selection", lambda r: r["correct_evidence_top5"] and not r["correct_evidence_final_context"], "05_webui/app.py", "Preserve the already-retrieved authoritative family during adaptive context selection.", "Medium: token-budget changes can alter latency and citations."),
    ("generation", lambda r: r["correct_evidence_final_context"] and not r["answer_factual_correctness"], "05_webui/app.py; 05_webui/fine_intent_policy.py", "Tighten the intent-specific evidence/answer contract; do not add an unrelated synthetic workflow.", "Medium: stronger guards can increase fallback use."),
    ("procedural completeness", lambda r: not r["procedural_completeness"], "05_webui/fine_intent_policy.py; 05_webui/app.py", "Require the missing in-scope stages only for this procedural intent.", "Low-medium if limited to one intent."),
    ("citation", lambda r: not r["citation_correctness"], "05_webui/app.py; 05_webui/static/script.js", "Keep final source IDs aligned with selected context and rendered source links.", "Low if source normalization is isolated."),
    ("fallback", lambda r: r["fallback_used"], "05_webui/fine_intent_policy.py; 05_webui/actor_boundary.py", "Determine whether the fallback is caused by missing evidence or a rejected grounded draft before changing fallback text.", "Medium-high: fallback logic is already verified."),
    ("streaming", lambda r: not r["stream_consistent"], "05_webui/app.py; 05_webui/streaming_utils.py; 05_webui/static/script.js", "Fix only the event lifecycle proven by the failing trace.", "High: streaming is already verified and shared by all answers."),
    ("language", lambda r: not r["language_correct"], "05_webui/app.py; 05_webui/actor_boundary.py", "Preserve the query language directive and reject only the failing output-language pattern.", "Medium."),
)


def percent(value, total):
    return f"{100 * value / total:.2f}%"


def actor_matrix_markdown(matrix):
    preferred = ["department_buyer", "vendor_bidder", "department_operator", "general_information_user"]
    labels = [label for label in preferred if label in matrix["labels"]]
    lines = ["| Expected \\ Detected | " + " | ".join(labels) + " |", "|---|" + "---:|" * len(labels)]
    for expected in labels:
        lines.append("| " + expected + " | " + " | ".join(str(matrix["matrix"][expected][detected]) for detected in labels) + " |")
    return "\n".join(lines)


def intent_confusions(rows):
    pairs = Counter((r["expected_fine_intent"], r["detected_fine_intent"]) for r in rows)
    lines = ["| Expected fine intent | Detected fine intent | Count |", "|---|---|---:|"]
    for (expected, detected), count in sorted(pairs.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {expected} | {detected} | {count} |")
    return "\n".join(lines)


def failure_clusters(rows):
    clusters = []
    for name, predicate, files, fix, risk in CAUSES:
        affected = [r for r in rows if predicate(r)]
        if affected:
            clusters.append((name, affected, files, fix, risk))
    clusters.sort(key=lambda item: len(item[1]), reverse=True)
    return clusters


def main():
    rows = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
    metrics = json.loads((HERE / "aggregate_metrics.json").read_text(encoding="utf-8"))
    clusters = failure_clusters(rows)
    counts = metrics["classification_counts"]
    total = metrics["total"]
    lines = [
        "# Production Procurement Benchmark — 120 Queries",
        "",
        "## Executive summary",
        "",
        f"- Pass: {counts.get('Pass', 0)}/{total} ({percent(counts.get('Pass', 0), total)})",
        f"- Partial: {counts.get('Partial', 0)}/{total} ({percent(counts.get('Partial', 0), total)})",
        f"- Fail: {counts.get('Fail', 0)}/{total} ({percent(counts.get('Fail', 0), total)})",
        f"- Expected clarification: {counts.get('Expected clarification', 0)}/{total} ({percent(counts.get('Expected clarification', 0), total)})",
        "",
        "The benchmark is frozen at 30 department-buyer, 30 vendor/bidder, 25 department-operator, 25 general-information and 10 ambiguous/mixed-role phrasings. Language balance is 45 English, 45 Hinglish and 30 Hindi. Every answer was sent to the production `/api/stream` path with an isolated session ID.",
        "",
        "## Layer metrics",
        "",
        "| Layer | Result |",
        "|---|---:|",
        f"| Actor accuracy | {metrics['actor_accuracy_percent']:.2f}% |",
        f"| Fine-intent accuracy | {metrics['fine_intent_accuracy_percent']:.2f}% |",
        f"| Retrieval top-5 accuracy | {metrics['retrieval_top5_accuracy_percent']:.2f}% |",
        f"| Final-context accuracy | {metrics['final_context_accuracy_percent']:.2f}% |",
        f"| Answer factual accuracy | {metrics['answer_accuracy_percent']:.2f}% |",
        f"| Citation/source-list accuracy | {metrics['citation_accuracy_percent']:.2f}% |",
        f"| Procedural completeness | {metrics['procedural_completeness_percent']:.2f}% |",
        f"| Language consistency | {metrics['language_accuracy_percent']:.2f}% |",
        f"| Fallback rate | {metrics['fallback_rate_percent']:.2f}% |",
        f"| Workflow leakage rate | {metrics['workflow_leakage_rate_percent']:.2f}% |",
        f"| Streaming consistency | {metrics['stream_consistency_percent']:.2f}% |",
        "",
        "Automated factual scoring uses intent-specific concept groups stored in `run_benchmark.py`; it is stricter than simple keyword overlap but is not a substitute for a legal-policy review. Citation scoring verifies that every final source was retrieved and that at least one expected evidence family survived final context selection.",
        "",
        "## Latency",
        "",
        "| Statistic | Seconds |",
        "|---|---:|",
        f"| Median | {metrics['latency_seconds']['median']:.3f} |",
        f"| P90 | {metrics['latency_seconds']['p90']:.3f} |",
        f"| P95 | {metrics['latency_seconds']['p95']:.3f} |",
        f"| Maximum | {metrics['latency_seconds']['maximum']:.3f} |",
        "",
        "## Actor confusion matrix",
        "",
        actor_matrix_markdown(metrics["actor_confusion_matrix"]),
        "",
        "## Fine-intent confusion pairs",
        "",
        intent_confusions(rows),
        "",
        "## Results by bucket",
        "",
        "| Bucket | N | Actor | Fine intent | Answer | Pass |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for bucket, values in metrics["by_bucket"].items():
        lines.append(f"| {bucket} | {values['count']} | {values['actor_accuracy_percent']:.2f}% | {values['fine_intent_accuracy_percent']:.2f}% | {values['answer_accuracy_percent']:.2f}% | {values['pass_percent']:.2f}% |")
    lines.extend(["", "## Results by language", "", "| Language | N | Actor | Fine intent | Answer language | Answer |", "|---|---:|---:|---:|---:|---:|"])
    for language, values in metrics["by_language"].items():
        lines.append(f"| {language} | {values['count']} | {values['actor_accuracy_percent']:.2f}% | {values['fine_intent_accuracy_percent']:.2f}% | {values['language_accuracy_percent']:.2f}% | {values['answer_accuracy_percent']:.2f}% |")
    lines.extend(["", "## Prioritized remaining defects", ""])
    if not clusters:
        lines.append("No benchmark failures were detected by the frozen assertions.")
    for rank, (name, affected, files, fix, risk) in enumerate(clusters, 1):
        examples = "; ".join(f"Q{r['id']}: {r['query']}" for r in affected[:3])
        lines.extend([
            f"### {rank}. {name} — {len(affected)} queries",
            "",
            f"- Examples: {examples}",
            f"- Root cause evidence: the corresponding per-query boolean is false/true in `results.json`; inspect each row's detected actor/intent, retrieved families, final families and answer.",
            f"- Likely files: {files}",
            f"- Recommended minimal fix: {fix}",
            f"- Regression risk: {risk}",
            "",
        ])
    slow = sorted(rows, key=lambda r: r["response_time_seconds"], reverse=True)[:10]
    lines.extend(["## Slowest 10 queries", "", "| ID | Seconds | Classification | Query |", "|---:|---:|---|---|"])
    for row in slow:
        lines.append(f"| {row['id']} | {row['response_time_seconds']:.3f} | {row['classification']} | {row['query'].replace('|', '/')} |")
    lines.extend([
        "",
        "## Reproduction",
        "",
        "```powershell",
        "python eval\\production_120\\build_dataset.py",
        "python eval\\production_120\\run_benchmark.py --endpoint http://127.0.0.1:5000/api/stream --workers 1 --timeout 150",
        "python eval\\production_120\\generate_report.py",
        "```",
        "",
        "No application code was changed after the benchmark run began. The report is diagnostic only; no failure-triggered fixes were applied.",
    ])
    (HERE / "benchmark_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    failure_rows = [r for r in rows if r["classification"] != "Pass"]
    failure_lines = ["# Failure-only report", "", f"Non-pass cases: {len(failure_rows)}/{len(rows)}", ""]
    for name, affected, files, fix, risk in clusters:
        failure_lines.extend([f"## {name} ({len(affected)})", ""])
        for row in affected:
            failure_lines.append(
                f"- Q{row['id']} [{row['classification']}]: {row['query']} — "
                f"actor {row['expected_actor']}→{row['detected_actor']}; intent "
                f"{row['expected_fine_intent']}→{row['detected_fine_intent']}; "
                f"top5={row['correct_evidence_top5']}; final={row['correct_evidence_final_context']}"
            )
        failure_lines.extend(["", f"Likely files: {files}", "", f"Minimal fix: {fix}", "", f"Risk: {risk}", ""])
    (HERE / "failure_report.md").write_text("\n".join(failure_lines) + "\n", encoding="utf-8")
    print(f"Wrote benchmark_report.md and failure_report.md for {len(rows)} rows")


if __name__ == "__main__":
    main()
