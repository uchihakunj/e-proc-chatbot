"""Assert source-level retrieval quality against the production SSE endpoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests


HERE = Path(__file__).resolve().parent


def normalise_source(value: str) -> str:
    return Path(str(value or "").replace("\\", "/")).name.casefold().removesuffix(".pdf")


def parse_sse(response) -> list[dict]:
    events = []
    for raw in response.iter_lines(decode_unicode=True):
        if raw and raw.startswith("data: "):
            try:
                events.append(json.loads(raw[6:]))
            except json.JSONDecodeError:
                pass
    return events


def evaluate_sources(case: dict, sources: list[str], answer: str = "") -> dict:
    """Return deterministic source and workflow-contract failures."""
    actual = [normalise_source(source) for source in sources if source]
    missing = [source for source in case["required_sources"]
               if normalise_source(source) not in actual]
    forbidden = [source for source in actual
                 if any(term.casefold() in source for term in case["forbidden_source_terms"])]
    answer_low = (answer or "").casefold()
    forbidden_answer_terms = [term for term in case.get("forbidden_answer_terms", [])
                              if term.casefold() in answer_low]
    return {
        "id": case["id"], "query": case["query"], "sources": actual,
        "missing_required_sources": missing, "forbidden_sources": forbidden,
        "forbidden_answer_terms": forbidden_answer_terms,
        "passed": not missing and not forbidden and not forbidden_answer_terms,
    }


def run_case(case: dict, endpoint: str, timeout: int) -> dict:
    with requests.post(
        endpoint,
        json={"query": case["query"], "session_id": f"retrieval-regression-{case['id']}",
              "diagnostics": True, "force_retrieval": True},
        stream=True, timeout=(10, timeout),
    ) as response:
        response.raise_for_status()
        events = parse_sse(response)
    context_events = [event for event in events if event.get("type") == "context"]
    context = context_events[-1].get("results", []) if context_events else []
    sources = [row.get("actual_pdf") or row.get("source") or "" for row in context]
    done_events = [event for event in events if event.get("type") == "done"]
    done = done_events[-1] if done_events else {}
    answer = done.get("answer") or "".join(
        event.get("content", "") for event in events if event.get("type") == "token"
    )
    return evaluate_sources(case, sources, answer)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://127.0.0.1:5000/api/stream")
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args()
    cases = json.loads((HERE / "dataset.json").read_text(encoding="utf-8"))
    results = [run_case(case, args.endpoint, args.timeout) for case in cases]
    print(json.dumps(results, indent=2, ensure_ascii=False))
    failed = [result["id"] for result in results if not result["passed"]]
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    print(f"PASS: {len(results)} retrieval regression cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
