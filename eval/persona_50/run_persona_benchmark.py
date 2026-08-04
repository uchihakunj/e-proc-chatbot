"""Run the supplied 50 role-based e-Procurement questions against SSE chat.

Writes full answers and a transparent functional-quality report. A "Pass" means
the service returned a non-empty, non-error answer with at least one source;
legal/policy correctness remains visible for human review in the full response.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import statistics
import threading
import time
from pathlib import Path

import requests


HERE = Path(__file__).resolve().parent
PRINT_LOCK = threading.Lock()
ERROR_MARKERS = (
    "sorry, no answer was received", "answer generate nahi ho paya",
    "rag backend is unreachable", "could not be generated",
)


def cases(role: str, questions: list[str], prefix: str) -> list[dict]:
    return [
        {"id": f"{prefix}-{number:02d}", "role": role, "query": question}
        for number, question in enumerate(questions, 1)
    ]


CASES = (
    cases("General User", [
        "Hamare office ko naye laptops chahiye. Humein process kahan se start karna chahiye?",
        "Government office mein saman kharidne ka normal process kya hota hai?",
        "GeM aur e-Procurement portal mein difference kya hai?",
        "Mujhe samajh nahi aa raha ki GeM use karun ya tender nikalu.",
        "Kya har government purchase tender se hi hoti hai?",
        "Agar office ke liye furniture lena ho to kya procedure hota hai?",
        "Single Tender ka matlab simple language mein batao.",
        "Limited Tender kab use karte hain?",
        "Department ko office stationery kharidni ho to kya karna padega?",
        "Chhattisgarh mein government procurement kaise hoti hai?",
    ], "GENERAL")
    + cases("Department Buyer", [
        "Hamare department ko 40 desktops kharidne hain. Sabse pehle kya karein?",
        "Office ke liye printers lene hain. Tender karna padega ya GeM chalega?",
        "Agar GeM par laptop available hai to kya wahi se lena compulsory hai?",
        "Hamare office ko projector kharidna hai. Kaunsi procurement method sahi rahegi?",
        "Purchase start karne se pehle kis-kis se approval lena hota hai?",
        "Technical specification banate waqt kya dhyan rakhna chahiye?",
        "Kya hum specification mein HP ya Dell ka naam likh sakte hain?",
        "Budget approve ho gaya hai. Ab next step kya hai?",
        "Agar sirf ek vendor qualify kare to kya purchase ho sakti hai?",
        "Lowest price dene wale ko hi order dena padta hai kya?",
        "Purchase Order issue hone ke baad department ko kya karna hota hai?",
        "Vendor ne galat material deliver kar diya. Ab kya process rahega?",
        "Agar delivery late ho jaye to department kya action le sakta hai?",
        "Payment release karne se pehle kya verify karna hota hai?",
        "Office ke liye AC ka AMC karwana hai. Process kya rahega?",
    ], "BUYER")
    + cases("Vendor / Bidder", [
        "Main pehli baar government tender mein participate kar raha hoon. Kahan se shuru karun?",
        "Vendor registration ka process kya hai?",
        "Registration ke liye kaun-kaun se documents chahiye?",
        "DSC map kaise karte hain?",
        "Bid submit karne ke baad usme changes kar sakte hain kya?",
        "Deadline nikal gayi hai. Kya ab bhi bid edit ho sakti hai?",
        "EMD ka payment kaise karna hota hai?",
        "Paisa account se kat gaya lekin EMD update nahi hua. Ab kya karun?",
        "Agar meri bid reject ho gayi to EMD kab wapas milegi?",
        "Corrigendum aaya hai ya nahi, kaise pata chalega?",
        "Reverse auction mein participate kaise karte hain?",
        "Financial bid kab open hoti hai?",
        "Startup company hoon. Kya government tender mein participate kar sakta hoon?",
        "Foreign company bhi Chhattisgarh tender mein participate kar sakti hai kya?",
        "Bid submit karne ke baad acknowledgement kahan milega?",
    ], "VENDOR")
    + cases("Department Operator", [
        "Naya tender create karna hai. Process batao.",
        "Tender publish kaise karte hain portal par?",
        "Tender ki last date badhani ho to kya karna padega?",
        "Corrigendum issue karne ka process kya hai?",
        "Technical bids open kaise karte hain?",
        "Financial bids kab open karni chahiye?",
        "Bid evaluation report generate kaise karte hain?",
        "EMD refund initiate kaise karte hain department side se?",
        "Offline tender upload karna ho to kya process hai?",
        "Tender publish hone ke baad koi mistake mil jaye to kya karna chahiye?",
    ], "OPERATOR")
)


def run_one(case: dict, endpoint: str, timeout: int) -> dict:
    started = time.perf_counter()
    answer, sources, followups, error = [], [], [], ""
    try:
        with requests.post(
            endpoint,
            json={"query": case["query"], "session_id": f"persona-{case['id']}-{time.time_ns()}"},
            stream=True,
            timeout=timeout,
        ) as response:
            response.raise_for_status()
            for raw in response.iter_lines(decode_unicode=True):
                if not raw or not raw.startswith("data: "):
                    continue
                event = json.loads(raw[6:])
                if event.get("type") == "token":
                    answer.append(event.get("content", ""))
                elif event.get("type") == "followups":
                    followups = event.get("items", [])
                elif event.get("type") == "done":
                    sources = event.get("sources", [])
    except Exception as exc:
        error = str(exc)

    text = "".join(answer).strip()
    lower = text.casefold()
    checks = {
        "answer_present": bool(text),
        "source_present": bool(sources),
        "provider_or_transport_error": bool(error) or any(marker in lower for marker in ERROR_MARKERS),
        "followups_present": bool(followups),
    }
    status = "Pass" if checks["answer_present"] and checks["source_present"] and not checks["provider_or_transport_error"] else "Review"
    return {
        **case,
        "status": status,
        "response_time_seconds": round(time.perf_counter() - started, 3),
        "answer": text,
        "sources": sources,
        "followups": followups,
        "checks": checks,
        "error": error,
    }


def report(rows: list[dict], summary: dict) -> str:
    lines = [
        "# Role-based e-Procurement functional test report", "",
        "## Meaning of the status", "",
        "A **Pass** means the live service returned a non-empty answer, at least one source, and no known provider/transport error. It is a functional-grounding screen; policy/legal correctness should be reviewed against the full response and cited documents.",
        "", "## Summary", "",
    ]
    lines += [f"- **{name.replace('_', ' ')}:** {value}" for name, value in summary.items() if name != "by_role"]
    lines += ["", "### By role", "", "| Role | Questions | Pass | Review |", "| --- | ---: | ---: | ---: |"]
    for role, values in summary["by_role"].items():
        lines.append(f"| {role} | {values['total']} | {values['pass']} | {values['review']} |")

    for row in rows:
        lines += [
            "", f"## {row['id']} — {row['role']} — {row['status']}", "",
            f"**Question:** {row['query']}", "",
            f"**Response time:** {row['response_time_seconds']} seconds  ",
            f"**Sources:** {', '.join(row['sources']) or 'None'}  ",
            f"**Follow-ups:** {' | '.join(row['followups']) or 'None'}  ",
            f"**Checks:** answer={row['checks']['answer_present']}, source={row['checks']['source_present']}, provider/transport error={row['checks']['provider_or_transport_error']}",
            "", "### Chatbot response", "", row['answer'] or "_No response returned._",
        ]
        if row["error"]:
            lines += ["", f"**Error:** `{row['error']}`"]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://127.0.0.1:8080/api/stream")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(run_one, case, args.endpoint, args.timeout): case for case in CASES}
        for future in concurrent.futures.as_completed(pending):
            row = future.result()
            rows.append(row)
            with PRINT_LOCK:
                print(f"[{len(rows):02d}/{len(CASES)}] {row['id']} {row['status']} {row['response_time_seconds']:.2f}s", flush=True)
    rows.sort(key=lambda row: row["id"])
    by_role = {}
    for role in sorted({row["role"] for row in rows}):
        selected = [row for row in rows if row["role"] == role]
        by_role[role] = {"total": len(selected), "pass": sum(row["status"] == "Pass" for row in selected), "review": sum(row["status"] != "Pass" for row in selected)}
    latencies = [row["response_time_seconds"] for row in rows]
    summary = {
        "total_questions": len(rows),
        "pass": sum(row["status"] == "Pass" for row in rows),
        "review": sum(row["status"] != "Pass" for row in rows),
        "source_coverage_percent": round(100 * sum(bool(row["sources"]) for row in rows) / len(rows), 1),
        "followup_coverage_percent": round(100 * sum(bool(row["followups"]) for row in rows) / len(rows), 1),
        "median_latency_seconds": round(statistics.median(latencies), 3),
        "p95_latency_seconds": round(sorted(latencies)[max(0, int(len(latencies) * .95) - 1)], 3),
        "by_role": by_role,
    }
    HERE.mkdir(parents=True, exist_ok=True)
    (HERE / "dataset.json").write_text(json.dumps(CASES, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "full_response_report.md").write_text(report(rows, summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
