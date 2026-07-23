"""Live API smoke test for actor/fine-intent routing regression cases."""

import json
import time
import uuid

import requests


CASES = [
    ("H50-03", "Can we buy an item directly if only one quotation is available on GeM?", "department_buyer"),
    ("H50-09", "Can Single Tender be used because the earlier supplier already knows our system?", "department_buyer"),
    ("H50-10", "Ek proprietary software sirf ek company provide karti hai. Kya Single Tender allowed hoga?", "department_buyer"),
    ("H50-12", "Government department ko dusre government undertaking se goods purchase karne hain. Kya tender zaroori hai?", "general_information_user"),
    ("H50-13", "Can we split a 10 lakh requirement into five smaller purchase orders?", "department_buyer"),
    ("H50-16", "Purchase start karne se pehle administrative approval aur financial sanction mein kya difference hai?", "department_buyer"),
    ("H50-17", "Who should confirm budget availability before a tender is published?", "department_buyer"),
    ("H50-18", "Can a tender be initiated before the budget is formally available?", "department_buyer"),
    ("H50-26", "Kya lowest quotation milne ka matlab price reasonable hai?", "general_information_user"),
    ("H50-41", "Technical evaluation ke baad financial bids kin bidders ki open honi chahiye?", "department_operator"),
]


def main():
    rows = []
    for case_id, question, expected_actor in CASES:
        started = time.perf_counter()
        events = []
        with requests.post(
            "http://127.0.0.1:5000/api/stream",
            json={"query": question, "diagnostics": True, "session_id": f"actor-live-{uuid.uuid4().hex}"},
            stream=True,
            timeout=35,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    try:
                        events.append(json.loads(line[6:]))
                    except json.JSONDecodeError:
                        pass
        done = next((event for event in reversed(events) if event.get("type") == "done"), {})
        rows.append({
            "id": case_id,
            "expected_actor": expected_actor,
            "detected_actor": done.get("detected_actor"),
            "detected_intent": done.get("detected_intent"),
            "latency_seconds": round(time.perf_counter() - started, 2),
            "diagnostics": done.get("diagnostics"),
        })
    print(json.dumps(rows, indent=2))
    print("passed", sum(row["expected_actor"] == row["detected_actor"] for row in rows), "of", len(rows))


if __name__ == "__main__":
    main()
