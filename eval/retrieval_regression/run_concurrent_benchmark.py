"""Concurrent force-retrieval benchmark over the regression dataset."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from run_retrieval_regression import run_case


HERE = Path(__file__).resolve().parent


def percentile(values, fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def build_workload(cases: list[dict], total_requests: int) -> list[dict]:
    if not cases or total_requests <= 0:
        return []
    workload = []
    idx = 0
    while len(workload) < total_requests:
        base = dict(cases[idx % len(cases)])
        base["id"] = f"{base['id']}-R{len(workload) + 1}"
        workload.append(base)
        idx += 1
    return workload


def execute_case(case: dict, endpoint: str, timeout: int) -> dict:
    started = time.perf_counter()
    try:
        result = run_case(case, endpoint, timeout)
        result["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        result["error"] = None
        return result
    except Exception as exc:
        return {
            "id": case["id"],
            "query": case["query"],
            "sources": [],
            "missing_required_sources": [],
            "forbidden_sources": [],
            "forbidden_answer_terms": [],
            "passed": False,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "error": str(exc),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://127.0.0.1:5000/api/stream")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--requests", type=int, default=0,
                        help="Total requests to issue. Default is max(workers, dataset size).")
    args = parser.parse_args()

    cases = json.loads((HERE / "dataset.json").read_text(encoding="utf-8"))
    total_requests = args.requests or max(args.workers, len(cases))
    workload = build_workload(cases, total_requests)

    rows = []
    wall_started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(execute_case, case, args.endpoint, args.timeout)
            for case in workload
        ]
        for future in as_completed(futures):
            rows.append(future.result())
    wall_elapsed = round(time.perf_counter() - wall_started, 3)

    timings = [row["elapsed_seconds"] for row in rows]
    errors = [row for row in rows if row.get("error")]
    failures = [row for row in rows if not row["passed"]]
    summary = {
        "workers": args.workers,
        "total_requests": len(rows),
        "wall_seconds": wall_elapsed,
        "p50_seconds": round(percentile(timings, 0.50), 3),
        "p95_seconds": round(percentile(timings, 0.95), 3),
        "mean_seconds": round(statistics.mean(timings), 3) if timings else 0.0,
        "passed": not failures,
        "failure_count": len(failures),
        "error_count": len(errors),
    }
    print(json.dumps({"summary": summary, "cases": rows}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
