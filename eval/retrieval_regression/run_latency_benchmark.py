"""Measure live force-retrieval latency across the regression dataset."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from run_retrieval_regression import run_case


HERE = Path(__file__).resolve().parent


def percentile(values, fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://127.0.0.1:5000/api/stream")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--limit", type=int, default=0, help="0 runs all cases")
    args = parser.parse_args()
    cases = json.loads((HERE / "dataset.json").read_text(encoding="utf-8"))
    if args.limit:
        cases = cases[:args.limit]
    rows = []
    for case in cases:
        started = time.perf_counter()
        result = run_case(case, args.endpoint, args.timeout)
        result["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        rows.append(result)
    timings = [row["elapsed_seconds"] for row in rows]
    print(json.dumps({
        "cases": rows,
        "summary": {
            "count": len(timings), "p50_seconds": round(percentile(timings, .50), 3),
            "p95_seconds": round(percentile(timings, .95), 3),
            "mean_seconds": round(statistics.mean(timings), 3) if timings else 0,
            "passed": all(row["passed"] for row in rows),
        },
    }, ensure_ascii=False, indent=2))
    return 0 if all(row["passed"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
