# -*- coding: utf-8 -*-
"""Measure time-to-context (retrieval + rerank) only, aborting the stream once
the context event arrives — so we isolate the rerank cost without paying for LLM
generation. Run once per reranker backend to A/B the rerank speedup end-to-end."""
import sys, json, time, statistics, requests
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LABEL = sys.argv[1] if len(sys.argv) > 1 else "run"
QS = [
    "What is the step-by-step process for CHiPS vendor registration?",
    "What are the main guidelines mentioned in the GeM manual?",
    "What is the procedure for challan payment?",
    "What are the main guidelines mentioned in the DSC manual?",
    "Under GFR and government rules, what is the procedure for MSME procurement?",
    "What is the step-by-step process for the auction manual?",
]

def ttc(q):
    t0 = time.time()
    with requests.post("http://localhost:5000/api/stream",
                       json={"query": q, "session_id": f"ttc_{abs(hash(q))}"},
                       stream=True, timeout=120) as r:
        for line in r.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                try: e = json.loads(line[6:])
                except: continue
                if e.get("type") == "context":
                    return time.time() - t0   # abort: close the stream here
    return time.time() - t0

# warm one query (model/cache warmup) before timing
ttc(QS[0])
times = []
for q in QS:
    dt = ttc(q)
    times.append(dt)
    print(f"  {dt:5.2f}s  {q[:50]}")
print(f"\n[{LABEL}] time-to-context  median={statistics.median(times):.2f}s  "
      f"mean={statistics.mean(times):.2f}s  min={min(times):.2f}s  max={max(times):.2f}s")
