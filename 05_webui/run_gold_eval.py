# -*- coding: utf-8 -*-
"""Gold-answer evaluation for the CHiPS e-Proc chatbot.

Unlike run_qa_eval.py (which only measures answered-vs-refused), this scores each
answer against VERIFIED expected facts, so it catches *content* regressions and
the rule-number-hallucination class specifically.

Each gold item (gold_eval.json) may declare:
  must_include      list of regexes; ALL must match the answer (case-insensitive)
  must_not_include  list of regexes; NONE may match (e.g. wrong rule numbers)
  expect_source     list of friendly doc names; at least one must be cited
  expect_refusal    true => the answer must be the one-line refusal

Run with the live server up (Flask :5000). Writes gold_eval_results.json.
"""
import sys, json, re, time, requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = "http://localhost:5000/api/stream"
REFUSAL = ["was not found in the available documents", "nahi mila", "नहीं मिला",
           "could not be generated"]


def ask(q, qid):
    """Stream one question; return (answer_text, [source friendly names])."""
    toks, sources, ctx_text = [], [], []
    with requests.post(URL, json={"query": q, "session_id": f"gold_{qid}"},
                       stream=True, timeout=400) as r:
        for line in r.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            try:
                e = json.loads(line[6:])
            except json.JSONDecodeError:
                continue
            t = e.get("type")
            if t == "token":
                toks.append(e.get("content", ""))
            elif t == "context":
                sources = [c.get("actual_pdf") or c.get("source")
                           for c in e.get("results", [])]
                ctx_text.append(" ".join((c.get("text") or "") for c in e.get("results", [])))
            elif t == "done" and e.get("sources"):
                sources = [s if isinstance(s, str) else (s.get("actual_pdf") or s.get("source"))
                           for s in e["sources"]]
    # Grade the DELIVERED answer: the UI (and cache) strip ungrounded rule numbers,
    # so measure that sanitised view, not the raw model stream.
    answer = _sanitize_rule_numbers("".join(toks).strip(), " ".join(ctx_text))
    return answer, [s for s in sources if s]


def _sanitize_rule_numbers(text, context_text):
    """Python twin of app.py's guard / the client stripUngroundedRuleNumbers."""
    if not text or not context_text:
        return text
    def _grounded(num):
        return bool(re.search(rf'(?:Rule|Section|Order|Clause|Regulation|Para)\s*0*{num}\b',
                              context_text, re.I)
                    or re.search(rf'\b0*{num}\s*\(', context_text))
    def _paren(m):
        inner = m.group(1)
        nums = re.findall(r'(?:Rule|Section|Clause|Order)\s+(\d+)', inner, re.I)
        return '' if (nums and all(not _grounded(n) for n in nums)) else m.group(0)
    text = re.sub(r'\(((?:[^()]|\([^()]*\))*?\b(?:Rule|Section|Clause|Order)\s+\d+(?:[^()]|\([^()]*\))*)\)',
                  _paren, text, flags=re.I)
    def _inline(m):
        if _grounded(m.group(2)):
            return m.group(0)
        return 'the relevant GFR rule' if m.group(1).lower() == 'rule' else 'the relevant section'
    text = re.sub(r'\b(Rule|Section)\s+(\d+)(?:[A-Za-z]+|\([ivxlcdmIVXLCDM\d]+\))?',
                  _inline, text, flags=re.I)
    return re.sub(r'\s+([,.;:)])', r'\1', re.sub(r'[ \t]{2,}', ' ', re.sub(r'\(\s*\)', '', text)))


def grade(item, answer, sources):
    """Return (passed: bool, failures: list[str])."""
    fails = []
    is_refusal = any(m in answer for m in REFUSAL)

    if item.get("expect_refusal"):
        if not is_refusal:
            fails.append("expected a refusal but got an answer")
        return (not fails), fails

    if is_refusal:
        fails.append("unexpected refusal")
        return False, fails

    for pat in item.get("must_include", []):
        if not re.search(pat, answer, re.IGNORECASE):
            fails.append(f"missing: /{pat}/")
    for pat in item.get("must_not_include", []):
        if re.search(pat, answer, re.IGNORECASE):
            fails.append(f"forbidden present: /{pat}/")

    exp = item.get("expect_source")
    if exp:
        joined = " | ".join(sources)
        # Map raw filenames to friendly names is non-trivial here; match on the
        # raw filename stems the friendly names derive from, OR accept if the
        # answer body itself names the expected source.
        if not any(_src_hit(e, sources, answer) for e in exp):
            fails.append(f"none of expected sources cited: {exp} (got {sources})")

    return (not fails), fails


# Friendly-name -> filename-stem hints so we can match the served raw filenames.
_SRC_STEMS = {
    "Manual for Procurement of Goods 2024": "publicProManual",
    "Public Procurement Manual": "mannual procurement",
    "Manual for Procurement of Works 2019": "Manual_for_Procurement_of_works",
    "Vendor Registration Manual (CHiPS)": "Vendor_Registration",
    "EMD Challan Payment Guide (CHiPS)": "CHALLAN",
    "Preferred System Configuration": "Preferred_System_Configuration",
    "e-Auction Manual": "AuctionManual",
}


def _src_hit(expected, sources, answer):
    stem = _SRC_STEMS.get(expected, expected)
    joined = " | ".join(sources)
    return (stem.lower() in joined.lower()
            or expected.lower() in joined.lower()
            or expected.lower() in answer.lower())


def main():
    gold = json.load(open("gold_eval.json", encoding="utf-8"))
    results, passed = [], 0
    for item in gold:
        t0 = time.time()
        try:
            answer, sources = ask(item["q"], item["id"])
            err = None
        except Exception as ex:
            answer, sources, err = "", [], str(ex)
        ok, fails = (False, [f"error: {err}"]) if err else grade(item, answer, sources)
        passed += ok
        dt = round(time.time() - t0, 1)
        print(f"[{item['id']}] {'PASS' if ok else 'FAIL'} ({dt}s) {item['q'][:55]}")
        for f in fails:
            print(f"        - {f}")
        results.append({"id": item["id"], "q": item["q"], "pass": ok,
                        "failures": fails, "latency_s": dt,
                        "sources": sources, "answer": answer})
        with open("gold_eval_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    n = len(gold)
    print(f"\n===== GOLD SCORE: {passed}/{n} = {100*passed/n:.0f}% =====")


if __name__ == "__main__":
    main()
