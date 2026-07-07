# -*- coding: utf-8 -*-
"""Build QA_Eval_100Q_FullResponses.md — every question WITH its full (server-
sanitised) response, plus the four metrics and a rule-number before/after."""
import json, os, re, statistics as st
from collections import Counter

def _clean(s):
    """Collapse whitespace/newlines so noisy captures (bare 'Rs.' at a line
    break) don't break the markdown bullet."""
    return re.sub(r"\s+", " ", str(s)).strip()

def _good_threshold(t):
    """Drop junk captures like 'rs,' or 'rs. 2' (bare Rs. + line-break digit)
    that carry no real magnitude — keep only amounts/percents/day-counts."""
    c = _clean(t).lower()
    if re.fullmatch(r"rs[.,]*\s*\d{0,2}[.,]*", c):
        return False
    return bool(re.search(r"\d", c)) and bool(
        re.search(r"%|lakh|lac|crore|\bcr\b|thousand|\bk\b|day|दिन|₹|,\d{3}|\d{4,}", c)
        or re.search(r"\b(one|two|three|five|ten)\s+lakh", c))

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "qa_eval_100_results.json"), encoding="utf-8"))
n = len(d)

oc = Counter(r["outcome"] for r in d)
answered = oc["ANSWERED"] + oc["CACHE"] + oc["FALLBACK"]
intent_ok = sum(r["intent_ok"] for r in d)
lat = [r["latency_s"] for r in d]
live = [r["latency_s"] for r in d if r["outcome"] not in ("CACHE", "CLARIFY")]
rules_ans = [r for r in d if r["answer_rules"]]
stripped = [r for r in d if r.get("stripped_rules")]
n_stripped = sum(len(r.get("stripped_rules", [])) for r in d)

ROLE = {"vendor": "Vendor", "officer": "Officer"}
LANG = {"en": "English", "hi": "Hindi", "hin": "Hinglish"}

def q_block(r):
    L = []
    L.append(f"### Q{r['idx']}. {r['question']}")
    L.append("")
    ent = []
    if r["answer_rules"]:
        ent.append("Rules: " + ", ".join(_clean(x) for x in r["answer_rules"]))
    good_th = [_clean(x) for x in r["answer_thresholds"] if _good_threshold(x)]
    if good_th:
        ent.append("Thresholds: " + ", ".join(good_th[:5]))
    strip_note = ""
    if r.get("stripped_rules"):
        strip_note = f"  |  🧹 stripped ungrounded: {', '.join(_clean(x) for x in r['stripped_rules'])}"
    L.append(f"- **Role/Lang:** {ROLE[r['role']]} · {LANG[r['lang']]}  ")
    tick = "✅" if r["intent_ok"] else "❌"
    L.append(f"- **Intent:** `{r['intent']}` (conf {r['intent_conf']}) {tick}  |  "
             f"**Outcome:** {r['outcome']}  |  **Latency:** {r['latency_s']}s  |  "
             f"**Sources:** {r['n_sources']}  ")
    if r["sources"]:
        L.append(f"- **Cited:** {', '.join(str(s) for s in r['sources'] if s)}  ")
    if ent or strip_note:
        L.append(f"- **Answer entities:** {' | '.join(ent) if ent else '—'}{strip_note}  ")
    L.append("")
    L.append("> **Response:**")
    ans = (r["answer"] or "").strip() or "*(no answer)*"
    for line in ans.split("\n"):
        L.append(f"> {line}" if line.strip() else ">")
    L.append("")
    return "\n".join(L)

out = []
w = out.append
w("# CHiPS e-Procurement Chatbot — 100-Question Q&A Report (with full responses)")
w("")
w("**Date:** 2026-07-01  ")
w("**Endpoint:** `POST /api/stream` (BGE-M3 retrieval + bge-reranker + Ollama `gemma3:4b`)  ")
w("**Knowledge base:** Qdrant `db3`, 3,503 chunks  ")
w("**Dataset:** 100 questions — 50 Vendor + 50 Government Officer × English / Hindi / Hinglish  ")
w("**Harness:** `05_webui/run_qa_eval_100.py`  |  **Raw data:** `05_webui/qa_eval_100_results.json`  ")
w("**Responses shown are the server-sanitised `done.answer`** (ungrounded rule numbers stripped — same text the browser shows).")
w("")
w("> This run was taken **after** the fixes in §8 of `QA_Eval_100Q_Report.md`: the vendor-registration")
w("> wizard no longer intercepts documentation questions (Q1 now answers), the DSC/`open tender` intent")
w("> mis-routes are corrected, and the server now emits the sanitised answer to all consumers.")
w("")
w("---")
w("")
w("## 1. The four metrics")
w("")
w("| Metric | Result |")
w("|---|---|")
w(f"| **Intent Recognition** | **{intent_ok}/{n} = {round(100*intent_ok/n)}%** correct topic-routing |")
w(f"| **Entity Extraction (answer-side)** | **{len(rules_ans)}/{n}** answers cite a `Rule N`; **{n_stripped}** ungrounded rule-number(s) auto-stripped across **{len(stripped)}** answer(s) before display |")
w(f"| **Response Time** | avg **{sum(lat)/n:.1f}s**, median **{st.median(lat):.1f}s**, range {min(lat):.0f}–{max(lat):.0f}s (live-gen avg {sum(live)/len(live):.1f}s) |")
w(f"| **Fallback Rate** | **{oc.get('REFUSED',0)+oc.get('ERROR',0)}/{n}** — {oc.get('ANSWERED',0)} ANSWERED, {oc.get('CACHE',0)} cache, {oc.get('CLARIFY',0)} clarify, {oc.get('REFUSED',0)} refused, {oc.get('ERROR',0)} error |")
w("")
w("### Rule-number sanitization (option 1, now server-authoritative)")
w("")
if stripped:
    w("Ungrounded rule numbers the model invented (absent from the retrieved context) were stripped to "
      "\"the relevant GFR rule\" before the answer was returned:")
    w("")
    w("| Q | Stripped (ungrounded) | Kept (grounded) |")
    w("|---|---|---|")
    for r in stripped:
        w(f"| Q{r['idx']} | {', '.join(r['stripped_rules'])} | {', '.join(r['answer_rules']) or '—'} |")
    w("")
else:
    w("No ungrounded rule numbers were stripped in this run — every cited number was present in the "
      "retrieved context.")
    w("")
w("**Caveat (unchanged):** the validator only removes numbers *absent* from the context. Numbers that "
  "*are* in the retrieved chunks but attached to the wrong concept (e.g. citing a GeM rule number for a "
  "Limited-Tender question) are considered grounded and kept — that is a semantic mis-application the "
  "citation check cannot catch, and hard-coding \"correct\" numbers is unsafe because this KB blends "
  "multiple manuals whose numbering can differ from vanilla GFR-2017.")
w("")
w("---")
w("")
w("## 2. Full questions & responses (all 100)")
w("")
cur = None
for r in d:
    seg = (r["role"], r["lang"])
    if seg != cur:
        cur = seg
        w(f"## — {ROLE[r['role']]} · {LANG[r['lang']]} —")
        w("")
    w(q_block(r))

report = os.path.join(os.path.dirname(HERE), "QA_Eval_100Q_FullResponses.md")
open(report, "w", encoding="utf-8").write("\n".join(out))
print("wrote", report, "-", len(out), "blocks,", n, "questions")
