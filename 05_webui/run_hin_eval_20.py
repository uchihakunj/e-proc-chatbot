# -*- coding: utf-8 -*-
"""Drive 10 Hindi (Devanagari) + 10 Hinglish (Roman) questions through the live
/api/stream endpoint and capture the full responses + metrics into JSON."""
import json, time, urllib.request, os

URL = "http://127.0.0.1:5000/api/stream"

# (lang, question)  — lang: 'hi' Devanagari, 'hin' Hinglish
QUESTIONS = [
    # ── Hindi (Devanagari) ──
    ("hi", "निविदा क्या होती है?"),
    ("hi", "EMD क्या है और यह कितनी होती है?"),
    ("hi", "वेंडर पंजीकरण कैसे करें?"),
    ("hi", "GeM क्या है?"),
    ("hi", "परफॉर्मेंस सिक्योरिटी कितने प्रतिशत होती है?"),
    ("hi", "डिजिटल हस्ताक्षर (DSC) क्या है और क्यों जरूरी है?"),
    ("hi", "लिमिटेड टेंडर इंक्वायरी कब इस्तेमाल की जाती है?"),
    ("hi", "e-Procurement पोर्टल का वेब पता क्या है?"),
    ("hi", "परचेज कमेटी कब बनाई जाती है और उसमें कितने सदस्य होते हैं?"),
    ("hi", "कोरिजेंडम (Corrigendum) क्या होता है?"),
    # ── Hinglish (Roman) ──
    ("hin", "Tender kya hota hai?"),
    ("hin", "EMD refund kaise hota hai?"),
    ("hin", "Vendor registration ke liye kaunse documents chahiye?"),
    ("hin", "Bid submit kaise karte hain?"),
    ("hin", "Performance security kitni honi chahiye?"),
    ("hin", "Bid security yaani EMD kitne percent hoti hai?"),
    ("hin", "GFR rule 155 kya kehta hai?"),
    ("hin", "Two-bid system kya hota hai?"),
    ("hin", "DSC kaise register karte hain portal par?"),
    ("hin", "Advertised tender enquiry kab use hoti hai?"),
]

def ask(query):
    body = json.dumps({"query": query, "session_id": f"hineval-{time.time()}"}).encode("utf-8")
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
for i, (lg, q) in enumerate(QUESTIONS, 1):
    print(f"[{i}/20] ({lg}) {q}")
    try:
        ans, lang, src, dt = ask(q)
    except Exception as e:
        ans, lang, src, dt = f"__ERROR__: {e}", None, [], 0
    print(f"       {dt}s  lang={lang}  src={len(src)}")
    results.append({"idx": i, "lang": lg, "question": q, "answer": ans,
                    "detected_lang": lang, "sources": src, "latency_s": dt})
    json.dump(results, open(os.path.join(os.path.dirname(__file__), "hin_eval_20_results.json"),
                            "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("DONE — wrote hin_eval_20_results.json")
