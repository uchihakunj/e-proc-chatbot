import json, time, urllib.request, os

URL = "http://127.0.0.1:5000/api/stream"

QUESTIONS = [
    "Tender kya hota hai?",
    "EMD refund kaise hota hai?",
    "Vendor registration ke liye kaunse documents chahiye?",
    "Bid submit kaise karte hain?",
    "Performance security kitni honi chahiye?",
    "Bid security yaani EMD kitne percent hoti hai?",
    "GFR rule 155 kya kehta hai?",
    "Two-bid system kya hota hai?",
    "DSC kaise register karte hain portal par?",
    "Advertised tender enquiry kab use hoti hai?"
]

def ask(query):
    body = json.dumps({"query": query, "session_id": f"hinglish-{time.time()}"}).encode("utf-8")
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    toks, lang, sources = [], None, []
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=200) as r:
        for raw in r:
            ln = raw.decode("utf-8", "replace").strip()
            if not ln.startswith("data:"):
                continue
            try:
                ev = json.loads(ln[5:].strip())
            except Exception:
                continue
            t = ev.get("type")
            if t == "lang":
                lang = ev.get("lang")
            elif t == "token":
                toks.append(ev.get("content", ""))
            elif t == "context":
                sources = [x.get("actual_pdf") or x.get("source") for x in (ev.get("results") or [])]
            elif t == "done":
                if ev.get("sources"):
                    sources = ev["sources"]
    return "".join(toks).strip(), lang, sources, round(time.time() - t0, 1)

results = []
for i, q in enumerate(QUESTIONS, 1):
    print(f"[{i}/10] {q}")
    try:
        ans, lang, src, dt = ask(q)
    except Exception as e:
        ans, lang, src, dt = f"__ERROR__: {e}", None, [], 0
    print(f"       {dt}s  lang={lang}  src={len(src)}")
    results.append({"idx": i, "question": q, "answer": ans, "detected_lang": lang, "sources": src, "latency_s": dt})
    with open(os.path.join(os.path.dirname(__file__), "hinglish_only_eval.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

print("DONE")
