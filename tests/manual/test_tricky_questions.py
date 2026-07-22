"""
Tricky question test suite for E-Procurement Chatbot.
Uses /api/stream (Ollama/Gemma3 path) — NOT /api/query (Sarvam, dead key).
Produces a Markdown report saved to CHATBOT_TEST_REPORT.md
"""

import json
import time
import sys
import requests
from datetime import datetime

BASE_URL = "http://localhost:5000/api/stream"
TIMEOUT  = 200   # seconds per question

QUESTIONS = [
    # ── Scope & Edge Cases ──────────────────────────────────────────────────
    {
        "id": "Q01",
        "category": "Scope & Edge Cases",
        "question": "mera EMD wapas kab aayega?",
        "expect_pass": True,
        "expected": "Should explain EMD refund/return process — not refuse as out-of-scope",
        "check_source": "EMD",
        "check_not_refuse": True,
    },
    {
        "id": "Q02",
        "category": "Scope & Edge Cases",
        "question": "tender expired ho gaya, kya main abhi bhi bid kar sakta hoon?",
        "expect_pass": True,
        "expected": "Should explain expired tender rule — may cite deadline policy",
        "check_source": None,
        "check_not_refuse": False,
    },
    {
        "id": "Q03",
        "category": "Scope & Edge Cases",
        "question": "agar main do companies ka owner hoon toh kya dono se bid kar sakta hoon?",
        "expect_pass": False,
        "expected": "Conflict-of-interest — may be out-of-scope; clean refusal expected without hallucination",
        "check_source": None,
        "check_not_refuse": False,
    },
    # ── Personalization ──────────────────────────────────────────────────────
    {
        "id": "Q04",
        "category": "Personalization",
        "question": "main suresh verma hoon, vendor registration ke liye kya karna hoga?",
        "expect_pass": True,
        "expected": "Answer should mention 'Suresh'/'Suresh Verma' by name",
        "check_source": "Vendor_Registration",
        "check_not_refuse": True,
        "check_name": "suresh",
    },
    {
        "id": "Q05",
        "category": "Personalization",
        "question": "my company name is TechBuild Pvt Ltd, how do I get registered?",
        "expect_pass": True,
        "expected": "Answer should mention 'TechBuild' in the response",
        "check_source": "Vendor_Registration",
        "check_not_refuse": True,
        "check_name": "techbuild",
    },
    # ── Typos & Broken Hindi ─────────────────────────────────────────────────
    {
        "id": "Q06",
        "category": "Typos & Broken Hindi",
        "question": "emd chalaan kaise bhren",
        "expect_pass": True,
        "expected": "Should understand typo 'bhren'='bharein' and explain EMD challan payment",
        "check_source": "EMD",
        "check_not_refuse": True,
    },
    {
        "id": "Q07",
        "category": "Typos & Broken Hindi",
        "question": "tendor mein paticipate kerna hai",
        "expect_pass": True,
        "expected": "Should handle 'tendor/paticipate/kerna' typos and explain tender participation",
        "check_source": None,
        "check_not_refuse": False,
    },
    # ── Multi-step / Compound ────────────────────────────────────────────────
    {
        "id": "Q08",
        "category": "Multi-step / Compound",
        "question": "vendor registration ke baad tender mein participate karne ki kya process hai? step by step batao",
        "expect_pass": True,
        "expected": "Should cover registration completion AND tender participation steps",
        "check_source": None,
        "check_not_refuse": True,
    },
    {
        "id": "Q09",
        "category": "Multi-step / Compound",
        "question": "what are the documents needed for EMD and also for vendor registration?",
        "expect_pass": True,
        "expected": "Should list documents for BOTH EMD and vendor registration",
        "check_source": None,
        "check_not_refuse": True,
    },
    # ── Trick / Out-of-scope ─────────────────────────────────────────────────
    {
        "id": "Q10",
        "category": "Trick / Out-of-scope",
        "question": "CG e-procurement portal ka helpline number kya hai?",
        "expect_pass": False,
        "expected": "Should refuse — contact info likely absent in docs. Must NOT hallucinate a number",
        "check_source": None,
        "check_not_refuse": False,
        "check_no_phone": True,
    },
    {
        "id": "Q11",
        "category": "Trick / Out-of-scope",
        "question": "tell me about GST rules for government tenders",
        "expect_pass": False,
        "expected": "Out-of-scope (tax law). Clean refusal — must not invent GST percentages",
        "check_source": None,
        "check_not_refuse": False,
    },
    {
        "id": "Q12",
        "category": "Trick / Out-of-scope",
        "question": "who made this chatbot?",
        "expect_pass": True,
        "expected": "Meta-question about origin. Should answer from Chatbot_Capabilities or give honest answer",
        "check_source": None,
        "check_not_refuse": False,
    },
    # ── Comparison / Analytical ──────────────────────────────────────────────
    {
        "id": "Q13",
        "category": "Comparison / Analytical",
        "question": "offline tender aur online tender mein kya difference hai?",
        "expect_pass": True,
        "expected": "Should compare offline vs online tender using docs",
        "check_source": None,
        "check_not_refuse": True,
    },
    {
        "id": "Q14",
        "category": "Comparison / Analytical",
        "question": "kaunsa payment method sabse fast hai EMD ke liye?",
        "expect_pass": True,
        "expected": "Should list EMD payment methods from docs; may decline to single-pick fastest",
        "check_source": "EMD",
        "check_not_refuse": True,
    },
]

REFUSAL_PHRASES = [
    "sorry", "i cannot", "i can't", "out of scope", "is scope se bahar",
    "mujhe maafi", "yeh meri", "nahi aata", "nahi pata", "scope mein nahi",
    "i'm unable", "unable to", "do not cover", "don't cover", "not cover",
    "not able to", "i don't have", "i do not have",
    "is question ka answer uplabdh", "yeh sawaal",
    "sambandhit jaankari nahi", "mere paas yeh",
]


def ask_stream(question: str) -> dict:
    """POST to /api/stream, consume SSE, return aggregated result."""
    t0 = time.time()
    full_answer = []
    sources = []
    result_count = 0
    error = None

    try:
        with requests.post(
            BASE_URL,
            json={"query": question},
            stream=True,
            timeout=TIMEOUT,
        ) as resp:
            resp.raise_for_status()
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                if not line.startswith("data: "):
                    continue
                payload_str = line[6:]
                try:
                    payload = json.loads(payload_str)
                except json.JSONDecodeError:
                    continue

                ptype = payload.get("type", "")
                if ptype == "token":
                    full_answer.append(payload.get("content", ""))
                elif ptype == "context":
                    results = payload.get("results", [])
                    result_count = len(results)
                    sources = [r.get("source", "") for r in results]
                elif ptype == "done":
                    # done also carries elapsed; sources may be in 'sources' key
                    done_sources = payload.get("sources", [])
                    if done_sources:
                        sources = done_sources
                    break
                elif ptype == "error":
                    error = payload.get("message", "unknown error")
                    break

    except requests.exceptions.Timeout:
        error = "TIMEOUT"
    except Exception as e:
        error = str(e)

    answer = "".join(full_answer)
    elapsed = time.time() - t0
    return {
        "elapsed": elapsed,
        "answer": answer,
        "sources": sources,
        "result_count": result_count,
        "error": error,
    }


def evaluate(q: dict, r: dict) -> tuple:
    """Return (verdict_str, notes_list)."""
    notes = []

    if r["error"]:
        return f"ERROR ({r['error'][:60]})", notes

    answer_lower = r["answer"].lower()
    is_refusal = any(p in answer_lower for p in REFUSAL_PHRASES)

    # Check if refused when we expected content
    if q.get("check_not_refuse") and is_refusal:
        notes.append("FAIL: refused but a doc-based answer was expected")
        return "FAIL", notes

    # Check source file match
    if q.get("check_source"):
        src_match = any(q["check_source"].lower() in s.lower() for s in r["sources"])
        if not src_match and not is_refusal:
            notes.append(f"WARN: expected source containing '{q['check_source']}' not found in {r['sources'][:3]}")

    # Check name personalization
    if q.get("check_name"):
        if q["check_name"] not in answer_lower:
            notes.append(f"WARN: name '{q['check_name']}' not found in answer — personalization may be missing")

    # Check no hallucinated phone number (Q10)
    if q.get("check_no_phone"):
        import re
        phones = re.findall(r'\b\d[\d\s\-]{6,}\d\b', r["answer"])
        if phones:
            notes.append(f"FAIL: hallucinated phone number(s): {phones}")
            return "FAIL", notes

    # If we expected a refusal but got content, that's a bonus pass (better than expected)
    if not q.get("expect_pass") and not is_refusal and not q.get("check_not_refuse"):
        notes.append("NOTE: answered where refusal was expected — check if answer is factual")

    if notes and any(n.startswith("FAIL") for n in notes):
        return "FAIL", notes
    if notes and any(n.startswith("WARN") for n in notes):
        return "PARTIAL", notes
    return "PASS", notes


def build_report(results: list) -> str:
    lines = []
    lines.append("# E-Procurement Chatbot — Tricky Question Test Report")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("LLM: gemma3-q3km:12b via Ollama (Intel Arc GPU, 100% GPU mode)\n")
    lines.append("---\n")

    for entry in results:
        q = entry["q"]
        r = entry["result"]
        v = entry["verdict"]
        notes = entry["notes"]

        badge = {"PASS": "[PASS]", "FAIL": "[FAIL]", "PARTIAL": "[PARTIAL]", "ERROR": "[ERROR]"}.get(v[:5].strip("("), "[?]")

        lines.append(f"## {q['id']} — {q['category']} {badge}")
        lines.append(f"\n**Question:** `{q['question']}`")
        lines.append(f"\n**Expected:** {q['expected']}")
        lines.append(f"\n**Verdict:** `{v}`")
        lines.append(f"\n**Elapsed:** {r['elapsed']:.1f}s | **Sources retrieved:** {r['result_count']}")

        if r["sources"]:
            unique_src = []
            seen = set()
            for s in r["sources"]:
                fname = s.split("/")[-1].split("\\")[-1]
                if fname not in seen:
                    unique_src.append(fname)
                    seen.add(fname)
            lines.append(f"\n**Source files:** {', '.join(unique_src[:5])}")

        if notes:
            lines.append("\n**Notes:**")
            for n in notes:
                lines.append(f"- {n}")

        answer_preview = r["answer"][:500].replace("\n", " ").strip() if r["answer"] else "(no answer)"
        if r["error"]:
            answer_preview = f"ERROR: {r['error']}"
        lines.append(f"\n**Answer preview:**\n> {answer_preview}{'...' if len(r['answer']) > 500 else ''}")

        lines.append("\n---\n")

    # Summary table
    lines.append("## Summary\n")
    lines.append("| ID | Category | Question | Verdict | Time |")
    lines.append("|---|---|---|---|---|")
    pass_n = fail_n = partial_n = error_n = 0
    for entry in results:
        q = entry["q"]
        r = entry["result"]
        v = entry["verdict"]
        short_q = q["question"][:48] + ("..." if len(q["question"]) > 48 else "")
        lines.append(f"| {q['id']} | {q['category']} | {short_q} | `{v}` | {r['elapsed']:.0f}s |")
        if v.startswith("PASS"): pass_n += 1
        elif v.startswith("FAIL"): fail_n += 1
        elif v.startswith("PARTIAL"): partial_n += 1
        else: error_n += 1

    total = len(results)
    lines.append(f"\n**Results: {pass_n} PASS / {partial_n} PARTIAL / {fail_n} FAIL / {error_n} ERROR out of {total}**\n")
    lines.append(f"**Pass rate (strict): {pass_n}/{total} ({100*pass_n//total}%)**")

    return "\n".join(lines)


def main():
    print(f"Running {len(QUESTIONS)} questions against {BASE_URL}")
    print("Using Ollama/Gemma3 streaming path. Each question may take 25-90s.\n")
    all_results = []

    for q in QUESTIONS:
        sys.stdout.write(f"[{q['id']}] {q['question'][:55]}...")
        sys.stdout.flush()
        result = ask_stream(q["question"])
        verdict, notes = evaluate(q, result)
        sys.stdout.write(f" {verdict} ({result['elapsed']:.0f}s)\n")
        sys.stdout.flush()
        all_results.append({"q": q, "result": result, "verdict": verdict, "notes": notes})

    report = build_report(all_results)
    report_path = "CHATBOT_TEST_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReport saved to {report_path}")
    print("\n" + "="*60)
    # Print summary table only to console
    pass_n = sum(1 for e in all_results if e["verdict"].startswith("PASS"))
    fail_n = sum(1 for e in all_results if e["verdict"].startswith("FAIL"))
    part_n = sum(1 for e in all_results if e["verdict"].startswith("PARTIAL"))
    err_n  = sum(1 for e in all_results if e["verdict"].startswith("ERROR"))
    total  = len(all_results)
    print(f"PASS: {pass_n}  PARTIAL: {part_n}  FAIL: {fail_n}  ERROR: {err_n}  (Total: {total})")
    print(f"Pass rate: {pass_n}/{total} ({100*pass_n//total}%)")


if __name__ == "__main__":
    main()
