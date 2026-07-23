import json

with open("scratch/batch_test_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

for r in results:
    q = r.get("question", "")
    success = r.get("success", False)
    if not success:
        print(f"Q: {q}")
        print(f"FAILED (Timeout or error: {r.get('error', '')})\n")
        continue

    ans = r.get("answer", "")
    srcs = r.get("sources", [])
    src_str = ", ".join(set(srcs))
    
    print(f"Q: {q}")
    print(f"Sources: {src_str}")
    print(f"Ans: {ans}")
    print("-" * 50)
