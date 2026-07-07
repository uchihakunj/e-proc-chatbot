"""
100-question Q&A evaluation harness for the CHiPS e-Proc chatbot.

Extends run_qa_eval.py to the 100-question Vendor + Government-Officer dataset
(English / Hindi / Hinglish). For each question it records:

  - Role (vendor / officer), Language (en / hi / hin)
  - Intent Recognition  : classify_intent() label + confidence (local NLU)
                          plus expected topic -> routing correctness
  - Entity Extraction   : local NER on the query AND a scan of the FINAL answer
                          for rule citations ("Rule 170") and value thresholds
                          ("Rs. one lakh", "Rs 25,00,000", "2%") -- this is the
                          metric the officer set actually exercises.
  - Response Time       : full end-to-end latency of /api/stream
  - Error Handling      : outcome class -> fallback rate

Writes qa_eval_100_results.json next to this file.
"""
import json
import os
import re
import sys
import time
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from nlp_features import classify_intent, extract_entities, entities_summary

STREAM_URL = "http://localhost:5000/api/stream"

REFUSAL_MARKERS = [
    "was not found in the available documents",
    "nahi mila",
    "नहीं मिला",
    "could not be generated",
    "not available in the",
]

# Map the intent taxonomy label to a coarse topic area, so we can score
# "intent recognition" as topic-routing correctness (emd / dsc / gfr / ...).
INTENT_TO_TOPIC = {
    "EMD_REFUND": "emd", "EMD_PAYMENT": "emd", "EMD_GENERAL": "emd",
    "VENDOR_REGISTRATION": "vendor", "DSC": "dsc", "BID_SUBMISSION": "bid",
    "TENDER_SEARCH": "tender", "AUCTION": "auction",
    "DOCUMENT_REQUIREMENTS": "documents", "PORTAL_USAGE": "portal",
    "RULES_GFR": "gfr", "UNKNOWN": "general",
}

# (role, lang, expected_topic, question)
# expected_topic uses the same coarse vocabulary as INTENT_TO_TOPIC. Where a
# question legitimately spans two areas the primary one is listed and scoring
# also accepts the secondary via TOPIC_ALIASES below.
QUESTIONS = [
    # ── VENDOR · English (20) ────────────────────────────────────────────────
    ("vendor", "en", "vendor", "How do I register as a vendor on the Chhattisgarh eProcurement portal?"),
    ("vendor", "en", "portal", "What are the system requirements for using the portal?"),
    ("vendor", "en", "portal", "How can I reset my password if I forget it?"),
    ("vendor", "en", "emd",    "What is the EMD rate and how is it calculated?"),
    ("vendor", "en", "emd",    "Who is exempt from paying the EMD amount?"),
    ("vendor", "en", "emd",    "What forms of EMD are accepted by the portal?"),
    ("vendor", "en", "emd",    "How long is the EMD validity period after submission?"),
    ("vendor", "en", "emd",    "How do I get my EMD refund after a tender is awarded?"),
    ("vendor", "en", "bid",    "Can I submit multiple bids for the same tender?"),
    ("vendor", "en", "dsc",    "What is a Digital Signature Certificate (DSC)?"),
    ("vendor", "en", "dsc",    "How do I map my renewed DSC to my account?"),
    ("vendor", "en", "dsc",    "Can I use the same DSC for two different login IDs?"),
    ("vendor", "en", "dsc",    "What should I do if my DSC token gets blocked?"),
    ("vendor", "en", "portal", "What are the contact details of the portal helpdesk?"),
    ("vendor", "en", "bid",    "How do I upload techno-commercial attachments during bidding?"),
    ("vendor", "en", "vendor", "Can a foreign vendor register on this portal?"),
    ("vendor", "en", "portal", "What should I do if I get an 'Application Blocked by Security Setting' Java error?"),
    ("vendor", "en", "emd",    "How can I check the status of my online EMD payment?"),
    ("vendor", "en", "bid",    "What happens if I withdraw my bid after the submission deadline?"),
    ("vendor", "en", "vendor", "Can I edit my company profile details after registration?"),
    # ── VENDOR · Hindi (20) ──────────────────────────────────────────────────
    ("vendor", "hi", "vendor", "छत्तीसगढ़ ई-प्रोक्योरमेंट पोर्टल पर नया वेंडर रजिस्ट्रेशन कैसे करें?"),
    ("vendor", "hi", "portal", "पोर्टल का उपयोग करने के लिए कंप्यूटर की क्या आवश्यकताएं हैं?"),
    ("vendor", "hi", "portal", "अगर मैं अपना पासवर्ड भूल जाऊं तो नया पासवर्ड कैसे बनाऊं?"),
    ("vendor", "hi", "emd",    "ईएमडी (EMD) की दर कितनी होती है और इसकी गणना कैसे की जाती है?"),
    ("vendor", "hi", "emd",    "ईएमडी (EMD) भुगतान से किन कंपनियों को छूट प्राप्त है?"),
    ("vendor", "hi", "emd",    "पोर्टल पर ईएमडी के लिए कौन-कौन से भुगतान रूप स्वीकार किए जाते हैं?"),
    ("vendor", "hi", "emd",    "निविदा जमा करने के बाद ईएमडी कितने दिनों तक वैध रहनी चाहिए?"),
    ("vendor", "hi", "emd",    "निविदा समाप्त होने के बाद ईएमडी रिफंड कैसे प्राप्त करें?"),
    ("vendor", "hi", "bid",    "क्या मैं एक ही निविदा के लिए एक से अधिक बोलियां जमा कर सकता हूं?"),
    ("vendor", "hi", "dsc",    "डिजिटल सिग्नेचर सर्टिफिकेट (DSC) क्या है और यह क्यों आवश्यक है?"),
    ("vendor", "hi", "dsc",    "नए रिन्यू किए गए डीएससी (DSC) को अपने प्रोफाइल से कैसे जोड़ें?"),
    ("vendor", "hi", "dsc",    "क्या एक ही डीएससी का उपयोग दो अलग-अलग लॉगिन आईडी के लिए किया जा सकता है?"),
    ("vendor", "hi", "dsc",    "अगर मेरा डीएससी (DSC) टोकन ब्लॉक हो जाए तो मुझे क्या करना चाहिए?"),
    ("vendor", "hi", "portal", "ई-प्रोक्योरमेंट पोर्टल की हेल्पलाइन टीम का संपर्क नंबर क्या है?"),
    ("vendor", "hi", "bid",    "बोली लगाने के दौरान तकनीकी दस्तावेज कैसे अपलोड करें?"),
    ("vendor", "hi", "vendor", "क्या कोई विदेशी कंपनी इस पोर्टल पर पंजीकरण कर सकती है?"),
    ("vendor", "hi", "portal", "जावा सुरक्षा त्रुटि 'Application Blocked by Security Setting' आने पर क्या करें?"),
    ("vendor", "hi", "emd",    "मैं अपने ऑनलाइन ईएमडी भुगतान की स्थिति कैसे देख सकता हूं?"),
    ("vendor", "hi", "bid",    "यदि मैं बोली जमा करने की अंतिम तिथि के बाद अपनी बोली वापस लेता हूं तो क्या होगा?"),
    ("vendor", "hi", "vendor", "पंजीकरण के बाद क्या मैं अपनी कंपनी के प्रोफाइल विवरण में बदलाव कर सकता हूं?"),
    # ── VENDOR · Hinglish (10) ───────────────────────────────────────────────
    ("vendor", "hin", "vendor", "Portal me vendor registration kaise kare?"),
    ("vendor", "hin", "portal", "Password bhool gaya hu, reset kaise hoga?"),
    ("vendor", "hin", "emd",    "EMD exemption ke liye kaun se documents upload karne padenge?"),
    ("vendor", "hin", "dsc",    "DSC register karne ka sahi tarika kya hai?"),
    ("vendor", "hin", "portal", "System configuration check karne ke liye download section me kaun sa file milega?"),
    ("vendor", "hin", "emd",    "Online payment failure hone par refund kab tak aayega?"),
    ("vendor", "hin", "portal", "Portal support team ka toll free number aur email id kya hai?"),
    ("vendor", "hin", "bid",    "Bid submit karne ke baad usko withdraw kaise kiya ja sakta hai?"),
    ("vendor", "hin", "dsc",    "Digital signature block ho gaya hai, isko unlock kaise kare?"),
    ("vendor", "hin", "vendor", "Kya foreign bidder ko registration ke liye PAN card chahiye?"),
    # ── OFFICER · English (20) ───────────────────────────────────────────────
    ("officer", "en", "gfr", "What is the limit for purchase without quotation under GFR?"),
    ("officer", "en", "gfr", "What are the rules for establishing a Local Purchase Committee?"),
    ("officer", "en", "gfr", "Under what conditions can a Limited Tender Enquiry be used?"),
    ("officer", "en", "gfr", "What is the minimum number of suppliers required for a Limited Tender?"),
    ("officer", "en", "gfr", "What is the threshold value of procurement above which an Advertised Tender is mandatory?"),
    ("officer", "en", "gfr", "What is the two-bid system, and when should it be followed?"),
    ("officer", "en", "gfr", "What are the guidelines for handling late bids under GFR Rule 165?"),
    ("officer", "en", "gfr", "Under what circumstances is Single Tender procurement justified?"),
    ("officer", "en", "gfr", "What are the GFR rules for EMD rates in government contracts?"),
    ("officer", "en", "gfr", "What is the range of Performance Security required for a contract?"),
    ("officer", "en", "gfr", "What forms of Performance Security are acceptable under GFR?"),
    ("officer", "en", "gfr", "In what situations can Performance Security be exempted?"),
    ("officer", "en", "gfr", "What is the procurement policy for products from Micro and Small Enterprises (MSEs)?"),
    ("officer", "en", "gfr", "How are price preferences applied to MSEs in evaluation?"),
    ("officer", "en", "gfr", "What are the steps for procurement of consulting services under GFR?"),
    ("officer", "en", "gfr", "What is the procedure for evaluation of consulting service proposals?"),
    ("officer", "en", "gfr", "What are the guidelines for splitting tender quantities?"),
    ("officer", "en", "gfr", "When can a short-term tender with less than 21 days notice be issued?"),
    ("officer", "en", "gfr", "What are the CVC guidelines on post-tender negotiations?"),
    ("officer", "en", "gfr", "What is the transparency policy for publication of tender awards on the portal?"),
    # ── OFFICER · Hindi (20) ─────────────────────────────────────────────────
    ("officer", "hi", "gfr", "जीएफआर (GFR) के तहत बिना कोटेशन के सीधे खरीद की सीमा क्या है?"),
    ("officer", "hi", "gfr", "स्थानीय क्रय समिति (Local Purchase Committee) के गठन के क्या नियम हैं?"),
    ("officer", "hi", "gfr", "सीमित निविदा जांच (Limited Tender Enquiry) का उपयोग किन परिस्थितियों में किया जा सकता है?"),
    ("officer", "hi", "gfr", "सीमित निविदा के लिए न्यूनतम कितने आपूर्तिकर्ताओं की आवश्यकता होती है?"),
    ("officer", "hi", "gfr", "किस राशि से अधिक की खरीद के लिए विज्ञापन निविदा (Open Tender) अनिवार्य है?"),
    ("officer", "hi", "gfr", "दो-बोली प्रणाली (Two-Bid System) क्या है और इसे कब लागू किया जाना चाहिए?"),
    ("officer", "hi", "gfr", "जीएफआर नियम 165 के तहत देर से प्राप्त बोलियों के संबंध में क्या निर्देश हैं?"),
    ("officer", "hi", "gfr", "किस परिस्थिति में एकल निविदा (Single Tender) खरीद को उचित माना जाता है?"),
    ("officer", "hi", "gfr", "सरकारी अनुबंधों में ईएमडी (EMD) दर के लिए जीएफआर नियम क्या हैं?"),
    ("officer", "hi", "gfr", "अनुबंध के लिए आवश्यक प्रदर्शन प्रतिभूति (Performance Security) की सीमा कितनी है?"),
    ("officer", "hi", "gfr", "जीएफआर के तहत प्रदर्शन सुरक्षा के कौन-कौन से रूप स्वीकार्य हैं?"),
    ("officer", "hi", "gfr", "किन स्थितियों में प्रदर्शन सुरक्षा जमा करने से छूट दी जा सकती है?"),
    ("officer", "hi", "gfr", "सूक्ष्म और लघु उद्यमों (MSEs) से खरीद के संबंध में सरकार की क्या नीति है?"),
    ("officer", "hi", "gfr", "मूल्यांकन के दौरान एमएसई (MSEs) को मूल्य प्राथमिकता (Price Preference) कैसे दी जाती है?"),
    ("officer", "hi", "gfr", "जीएफआर के तहत परामर्श सेवाओं (Consulting Services) की खरीद के क्या चरण हैं?"),
    ("officer", "hi", "gfr", "परामर्श सेवा प्रस्तावों के मूल्यांकन की क्या प्रक्रिया है?"),
    ("officer", "hi", "gfr", "निविदा मात्राओं को विभाजित (Splitting Tender Quantities) करने के क्या दिशानिर्देश हैं?"),
    ("officer", "hi", "gfr", "21 दिनों से कम समय की सूचना वाली अल्पकालीन निविदा (Short-Term Tender) कब जारी की जा सकती है?"),
    ("officer", "hi", "gfr", "निविदा के बाद बातचीत (Post-Tender Negotiations) पर सीवीसी के क्या निर्देश हैं?"),
    ("officer", "hi", "gfr", "पोर्टल पर निविदा पुरस्कारों के प्रकाशन के लिए पारदर्शिता नीति क्या है?"),
    # ── OFFICER · Hinglish (10) ──────────────────────────────────────────────
    ("officer", "hin", "gfr", "GFR ke under directly purchase bina quotation ke kitne amount tak ho sakti hai?"),
    ("officer", "hin", "gfr", "Local Purchase Committee banane ka threshold limit kya hai?"),
    ("officer", "hin", "gfr", "Advertised tender kis situation me compulsory ho jata hai?"),
    ("officer", "hin", "gfr", "Two bid system me technical aur financial bid sath me kaise evaluate hote hain?"),
    ("officer", "hin", "gfr", "Late bid ko reject karne ke liye GFR rule 165 kya kehta hai?"),
    ("officer", "hin", "gfr", "Single tender case me CA ki approval kab jaruri hoti hai?"),
    ("officer", "hin", "gfr", "Performance security deposit accept karne ke kya modes hain?"),
    ("officer", "hin", "gfr", "Short term tender notice publish karne ke liye time limit kitni di gayi hai?"),
    ("officer", "hin", "gfr", "CVC ke rules ke mutabik negotiation L1 ke sath kab kiya ja sakta hai?"),
    ("officer", "hin", "gfr", "MSE bidders ko price bid me kya preference milti hai?"),
]

# Some questions legitimately map to more than one topic; accept either when
# scoring intent-routing correctness. Also: for many document-lookup phrasings
# the *correct* label is general RAG (UNKNOWN), same as the prior 50Q report.
TOPIC_ALIASES = {
    "emd": {"emd", "general"},
    "gfr": {"gfr", "emd", "general"},   # officer GFR set: emd-rate & general ok
    "vendor": {"vendor", "documents", "general", "portal"},
    "dsc": {"dsc", "general"},
    "portal": {"portal", "general", "documents"},
    "bid": {"bid", "general"},
}

# Rule-citation + threshold scanners for the answer-side "entity extraction".
_RULE_RE = re.compile(r"\bRule\s+\d+[A-Za-z()]*", re.I)
_THRESH_RE = re.compile(
    r"(?:₹|rs\.?|inr|rupees?)\s*[\d,]+(?:\.\d+)?\s*"
    r"(?:lakh?s?|lac?s?|crore?s?|cr|k|thousand)?"
    r"|\b[\d,]+\s*(?:lakh?s?|lac?s?|crore?s?|cr)\b"
    r"|\bone\s+lakh\b|\btwo\s+lakh\b|\bfive\s+lakh\b|\bten\s+lakh\b"
    r"|\b\d+(?:\.\d+)?\s*%|\b\d+\s+days?\b|\b21\s*दिन", re.I)


def scan_answer_entities(answer: str):
    rules = sorted(set(m.group(0).strip() for m in _RULE_RE.finditer(answer)),
                   key=lambda s: (int(re.search(r"\d+", s).group()), s))
    thresholds = []
    for m in _THRESH_RE.finditer(answer):
        v = m.group(0).strip()
        if v.lower() not in (t.lower() for t in thresholds):
            thresholds.append(v)
    return rules, thresholds[:12]


def run_one(item, idx):
    role, lang, expected_topic, q = item
    intent, conf = classify_intent(q)
    ents = extract_entities(q)
    ent_sum = entities_summary(ents)

    answer_parts, statuses, sources = [], [], []
    elapsed_srv, err = None, None
    answer_clean = None      # server-sanitised full answer from the done event
    outcome = "ANSWERED"

    t0 = time.time()
    try:
        payload = {"query": q, "session_id": f"eval100_{idx}"}
        with requests.post(STREAM_URL, json=payload, stream=True, timeout=600) as r:
            for line in r.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                try:
                    evt = json.loads(line[6:])
                except json.JSONDecodeError:
                    continue
                t = evt.get("type")
                if t == "token":
                    answer_parts.append(evt.get("content", ""))
                elif t == "status":
                    statuses.append(evt.get("message", ""))
                elif t == "context":
                    sources = [c.get("actual_pdf") or c.get("source")
                               for c in evt.get("results", [])]
                elif t == "done":
                    elapsed_srv = evt.get("elapsed")
                    answer_clean = evt.get("answer")
                    if evt.get("sources"):
                        sources = [s if isinstance(s, str) else
                                   (s.get("actual_pdf") or s.get("source"))
                                   for s in evt["sources"]]
                elif t == "error":
                    err = evt.get("message")
                    outcome = "ERROR"
    except Exception as e:
        err = str(e)
        outcome = "ERROR"
    latency = round(time.time() - t0, 2)

    answer_raw = "".join(answer_parts).strip()          # raw live token stream
    # Prefer the server-sanitised answer (ungrounded rule numbers stripped);
    # fall back to the raw stream if the done event carried none.
    answer = (answer_clean if answer_clean else answer_raw).strip()
    joined_status = " | ".join(statuses)
    if outcome != "ERROR":
        if any(m in answer for m in REFUSAL_MARKERS):
            outcome = "REFUSED"
        elif "Switching to a lighter model" in joined_status:
            outcome = "FALLBACK"
        elif "Instant answer (cached)" in joined_status:
            outcome = "CACHE"
        elif not sources and answer:
            outcome = "CLARIFY"
        elif not answer:
            outcome = "ERROR"
            err = err or "empty answer"

    got_topic = INTENT_TO_TOPIC.get(intent, "general")
    accept = TOPIC_ALIASES.get(expected_topic, {expected_topic})
    intent_ok = got_topic in accept or got_topic == expected_topic

    ans_rules, ans_thresholds = scan_answer_entities(answer)      # sanitised
    raw_rules, _ = scan_answer_entities(answer_raw)               # before clean
    stripped_rules = [r for r in raw_rules if r not in ans_rules]

    return {
        "idx": idx, "role": role, "lang": lang, "question": q,
        "expected_topic": expected_topic,
        "intent": intent, "intent_conf": conf, "intent_topic": got_topic,
        "intent_ok": intent_ok,
        "entities": {k: v for k, v in ents.items() if v and k != "amounts_value"},
        "entities_summary": ent_sum,
        "answer_rules": ans_rules,
        "answer_thresholds": ans_thresholds,
        "raw_rules": raw_rules,
        "stripped_rules": stripped_rules,
        "outcome": outcome,
        "latency_s": latency, "server_elapsed": elapsed_srv,
        "n_sources": len(sources), "sources": sources[:5],
        "error": err, "answer": answer, "answer_raw": answer_raw,
    }


def main():
    results = []
    out_path = os.path.join(HERE, "qa_eval_100_results.json")
    for i, item in enumerate(QUESTIONS, 1):
        print(f"[{i}/{len(QUESTIONS)}] ({item[0]}/{item[1]}) {item[3][:55]}...", flush=True)
        res = run_one(item, i)
        print(f"    -> intent={res['intent']}({res['intent_conf']}) "
              f"ok={res['intent_ok']} outcome={res['outcome']} "
              f"lat={res['latency_s']}s src={res['n_sources']} "
              f"rules={res['answer_rules']}", flush=True)
        results.append(res)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    n = len(results)
    answered = sum(1 for r in results if r["outcome"] in ("ANSWERED", "CACHE", "FALLBACK"))
    refused = sum(1 for r in results if r["outcome"] == "REFUSED")
    clarify = sum(1 for r in results if r["outcome"] == "CLARIFY")
    fallback = sum(1 for r in results if r["outcome"] == "FALLBACK")
    cache = sum(1 for r in results if r["outcome"] == "CACHE")
    errors = sum(1 for r in results if r["outcome"] == "ERROR")
    intent_ok = sum(1 for r in results if r["intent_ok"])
    with_rules = sum(1 for r in results if r["answer_rules"])
    with_thresh = sum(1 for r in results if r["answer_thresholds"])
    lat = sorted(r["latency_s"] for r in results)
    print("\n===== SUMMARY =====")
    print(f"Total                : {n}")
    print(f"Answered             : {answered}  (cache={cache} fallback={fallback})")
    print(f"Refused              : {refused}")
    print(f"Clarify              : {clarify}")
    print(f"Errors               : {errors}")
    print(f"Intent routing OK    : {intent_ok}/{n} = {100*intent_ok/n:.0f}%")
    print(f"Answers w/ rule cite : {with_rules}")
    print(f"Answers w/ threshold : {with_thresh}")
    print(f"Latency avg          : {sum(lat)/n:.1f}s")
    print(f"Latency min/med/max  : {lat[0]}/{lat[n//2]}/{lat[-1]}s")
    print(f"Fallback rate        : {100*(refused+errors)/n:.1f}%")


if __name__ == "__main__":
    main()
