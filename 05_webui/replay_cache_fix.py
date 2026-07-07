# -*- coding: utf-8 -*-
"""Live end-to-end check of the answer-cache collision fix.

Seeds the cache with the SAME prior answers that caused the report's wrong-answer
collisions (DSC manual / DSC objective / tutorial-not-found), then fires the GeM /
procurement questions that previously hit those stale entries. After the fix each
must ANSWER fresh with its OWN document, not serve a CACHE hit from another doc.
"""
import json
import sys
import time
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = "http://localhost:5000/api/stream"

SEEDS = [
    (15, "What are the main guidelines mentioned in the DSC manual?"),
    (16, "What is the core objective of the DSC manual?"),
    (19, "Under GFR and government rules, what is the procedure for the tutorial?"),
]
# (idx, question, previously-wrongly-served-from, must-now-cite-substring)
REPLAYS = [
    (23, "What are the main guidelines mentioned in the GeM manual?", "DSC manual", "GeM"),
    (24, "Under GFR and government rules, what is the procedure for the GeM manual?", "tutorial-not-found", "GeM"),
    (25, "What is the core objective of the GeM manual?", "DSC objective", "GeM"),
    (31, "What are the main guidelines mentioned in the procurement manual?", "DSC manual", "rocurement"),
]


def ask(idx, q):
    answer, statuses, sources = [], [], []
    with requests.post(URL, json={"query": q, "session_id": f"replay_{idx}"},
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
                answer.append(e.get("content", ""))
            elif t == "status":
                statuses.append(e.get("message", ""))
            elif t == "context":
                sources = [c.get("actual_pdf") or c.get("source") for c in e.get("results", [])]
    cached = any("cached" in s.lower() for s in statuses)
    return "".join(answer).strip(), cached, sources


print("=== SEEDING prior answers (reproduces the pre-fix cache state) ===", flush=True)
for idx, q in SEEDS:
    t0 = time.time()
    a, cached, src = ask(idx, q)
    print(f"  seed Q{idx} ({time.time()-t0:.0f}s) cached={cached} :: {a[:70]!r}", flush=True)

print("\n=== REPLAY: previously-colliding questions ===", flush=True)
all_ok = True
for idx, q, was_served, must_cite in REPLAYS:
    t0 = time.time()
    a, cached, src = ask(idx, q)
    # PASS if it did NOT silently serve a cache hit AND the answer/sources are
    # about the right document (contains the expected doc keyword).
    served_wrong = cached  # any cache hit here would be the bug resurfacing
    on_topic = (must_cite.lower() in a.lower()) or any(must_cite.lower() in (s or "").lower() for s in src)
    ok = (not served_wrong) and on_topic
    all_ok &= ok
    print(f"\nQ{idx}  ({time.time()-t0:.0f}s)  cached={cached}  -> {'PASS' if ok else 'FAIL'}", flush=True)
    print(f"   was wrongly served: {was_served}", flush=True)
    print(f"   sources: {[s for s in src if s][:4]}", flush=True)
    print(f"   answer head: {a[:160]!r}", flush=True)

print("\n=====================================", flush=True)
print("OVERALL:", "ALL PASS ✅" if all_ok else "SOME FAIL ❌", flush=True)
