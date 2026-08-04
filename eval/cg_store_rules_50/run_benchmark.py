"""Independent, rule-linked 50-question benchmark for CG Store Purchase Rules.

This runner uses the production SSE endpoint and writes the question set, raw
answers, scoring evidence, and a readable full-response report to this folder.
It is deliberately independent of the existing frozen benchmark.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import statistics
import threading
import time
from collections import Counter
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
PRINT_LOCK = threading.Lock()
SOURCE_TOKEN = "store purchase rule"
FALLBACK_MARKERS = (
    "sufficiently reliable section", "reliable section available nahi",
    "original question", "relevant official section check",
)


def case(identifier, bucket, language, question, rule, reference, all_of, groups, prohibited=()):
    return {
        "id": identifier, "bucket": bucket, "language": language,
        "query": question, "expected_rule": rule, "reference_answer": reference,
        "required_all": list(all_of), "required_any_groups": [list(g) for g in groups],
        "prohibited_claims": list(prohibited),
        "expected_source_document": "store purchase rule cg.pdf",
    }


# Authored as fresh user-style questions. Every expected result is traceable to
# the July 2024 consolidation of the CG Store Purchase Rules, not to an LLM.
CASES = [
    case("CGSPR-01", "scope", "en", "Which public bodies are covered by the CG Store Purchase Rules?", "Rule 2 and 2.1", "They cover government departments and also the State Electricity Board, public undertakings, boards, district/janpad panchayats and urban bodies.", ["government"], [("public undertaking", "public sector"), ("panchayat", "urban body", "electricity")]),
    case("CGSPR-02", "gem-route", "en", "If an item and its specifications are available on GeM, what purchase route should a Chhattisgarh department normally use?", "Rule 3.1.1", "Purchase through GeM using its prescribed procedure; the buyer remains responsible for checking technical specifications, seller credibility, L1 price, economy and quality.", ["gem"], [("procedure", "process"), ("specification", "technical"), ("quality", "economy", "l1")]),
    case("CGSPR-03", "gem-route", "hinglish", "GeM par laptop listed hai. Buyer ko order se pehle kya-kya verify karna hota hai?", "Rule 3.1.1", "The buyer must examine technical specifications, seller credibility and L1 price, and ensure economy and quality; availability alone is not enough.", ["gem"], [("technical", "specification"), ("seller", "vendor", "credibility"), ("quality", "economy", "l1")]),
    case("CGSPR-04", "gem-route", "en", "Can a department choose tendering even when the relevant goods are available on GeM? What approval is needed first?", "Rule 3.1.1", "It may use the tender route, but before doing so it must obtain written concurrence of the Finance Department through the concerned administrative department.", ["tender"], [("written", "in writing"), ("finance department", "finance"), ("concurrence", "consent", "approval")]),
    case("CGSPR-05", "special-sources", "en", "A Schedule 1 item is not available on GeM but its rate is listed on CSIDC's e-Standard portal. May the office buy through that portal?", "Rule 3.1.2", "Yes. Schedule 1 items unavailable on GeM may be purchased through the CSIDC e-Standard portal when their rate and specifications are available there.", ["csidc"], [("schedule 1", "appendix 1", "annexure 1"), ("e-standard", "portal")]),
    case("CGSPR-06", "special-sources", "hinglish", "GeM, CSIDC e-Standard aur Schedule 2 rate source mein item nahi mil raha. Department ko kaunsi process follow karni chahiye?", "Rules 3.1.3 and 3.4", "Where the item is not available through the specified sources, the department should procure it through the tender procedure in Rule 4.", ["tender"], [("rule 4", "tender procedure", "tender process")]),
    case("CGSPR-07", "tender-basics", "en", "What is the normal procurement method under Rule 4 of the CG Store Purchase Rules?", "Rule 4", "Government procurement is normally through the tender system, subject to the stated exceptions and routes.", ["tender"], [("normally", "general", "generally")]),
    case("CGSPR-08", "startup", "en", "A valid Chhattisgarh-recognised startup is bidding. Can the tender require prior experience and prior turnover?", "Rule 4.2", "A qualifying valid startup receives exemption from prior-experience and prior-turnover conditions under this rule.", ["startup"], [("prior experience", "experience exemption", "experience"), ("turnover", "turn-over")]),
    case("CGSPR-09", "specifications", "hinglish", "Tender issue karne se pehle technical specification kis tarah decide honi chahiye?", "Rule 4.1", "Before inviting a tender, standards/specifications for the goods should be determined by experts with technical knowledge.", ["specification"], [("expert", "technical knowledge", "technical expert")]),
    case("CGSPR-10", "single-tender", "en", "Can a proprietary item with an annual requirement of Rs. 45,000 be procured through a single tender?", "Rule 4.3.1(a)", "Yes, a proprietary single item may be procured by single tender from one firm when competition is not needed and the annual requirement does not exceed Rs. 50,000.", ["single tender"], [("proprietary", "proprietary character"), ("50,000", "fifty thousand")]),
    case("CGSPR-11", "single-tender", "en", "For a proprietary item above Rs. 50,000, is merely calling it proprietary enough to use one supplier?", "Rule 4.3.1(b)", "No. The buyer must establish that only one manufacturer makes the required item, and the prescribed proprietary and approval process applies.", ["proprietary"], [("one manufacturer", "only one manufacturer", "single manufacturer"), ("approval", "procedure", "certificate")], ["automatically allowed"]),
    case("CGSPR-12", "single-tender", "hinglish", "Emergency mein ek supplier se purchase karne ke liye department ko kya record aur approval chahiye?", "Rule 4.3.1(b)(2)", "In an emergency, the decision to purchase from one supplier must record the reasons and obtain approval of the competent authority.", ["emergency"], [("reasons", "justification", "record"), ("competent authority", "competent approval", "approval")]),
    case("CGSPR-13", "single-tender", "en", "Can compatible spare parts for existing equipment be bought from one selected firm?", "Rule 4.3.1(b)(3)", "It may be possible for standardisation or compatibility of spare parts, but it needs advice of a competent technical expert and approval of the competent authority.", ["spare"], [("technical expert", "technical"), ("competent authority", "approval")]),
    case("CGSPR-14", "single-tender", "en", "Before purchasing a proprietary article through tender from a sole manufacturer or authorised seller, which certificate is required?", "Rule 4.3.1(b)(3), Appendix 4", "A Proprietary Article Certificate in the prescribed Appendix 4 form is required before the purchase process.", ["proprietary article certificate"], [("appendix 4", "annexure 4", "prescribed form")]),
    case("CGSPR-15", "single-tender", "hinglish", "PAC milne ke baad objection/claim notice kahan aur kitne minimum din ke liye publish karna chahiye?", "Rule 4.3.1(b)(3)", "Publish a brief claim/objection notice in newspapers and detailed notice on the government/department website, allowing at least 30 days.", ["30"], [("newspaper", "news paper"), ("website", "web site")]),
    case("CGSPR-16", "single-tender", "en", "After objections to a proprietary-article purchase are resolved, what should happen before award?", "Rule 4.3.1(b)(3)", "Obtain the proposed supplier's rates and justification; the purchase committee recommends acceptance, rejection or negotiation, followed by competent approval before further action/rate contract.", ["purchase committee"], [("rate", "price"), ("justification", "reasons"), ("competent approval", "approval")]),
    case("CGSPR-17", "limited-tender", "en", "What estimated annual purchase-value band is normally meant for Limited Tender under these rules?", "Rule 4.3.2", "Limited Tender is normally used for estimated annual purchases from Rs. 50,001 to Rs. 3,00,000.", ["50,001"], [("3,00,000", "300,000", "three lakh")]),
    case("CGSPR-18", "limited-tender", "hinglish", "Limited Tender mein minimum kitne manufacturers, authorised representatives ya registered manufacturers ko invite karna chahiye?", "Rule 4.3.2", "At least three manufacturers, authorised representatives, or registered manufacturers should be approached for Limited Tender.", ["three"], [("manufacturer", "authorised", "registered")]),
    case("CGSPR-19", "open-tender", "en", "From what estimated value does the Open Tender procedure start under Rule 4.3.3?", "Rule 4.3.3", "Open Tender applies from an estimated value of Rs. 3,00,001 upward.", ["3,00,001"], [("open tender", "open")]),
    case("CGSPR-20", "open-tender", "en", "For an Open Tender valued above Rs. 3 lakh and up to Rs. 5 lakh, what newspaper publicity is prescribed?", "Rule 4.3.3(a)(1)", "Publish it in one widely circulated local-level newspaper.", ["one"], [("local", "local-level"), ("newspaper", "news paper")]),
    case("CGSPR-21", "open-tender", "hinglish", "Rs. 5 lakh se zyada aur Rs. 10 lakh tak ke Open Tender ko kitne state-level newspapers mein advertise karna hai?", "Rule 4.3.3(a)(2)", "It must be advertised in two widely circulated state-level newspapers.", ["two"], [("state", "state-level"), ("newspaper", "news paper")]),
    case("CGSPR-22", "open-tender", "en", "What publicity is required for an Open Tender above Rs. 10 lakh and up to Rs. 20 lakh?", "Rule 4.3.3(a)(3)", "Use two widely circulated state-level newspapers and one national-level newspaper.", ["two"], [("state", "state-level"), ("one national", "national-level")]),
    case("CGSPR-23", "open-tender", "en", "What publicity is required for an Open Tender above Rs. 20 lakh?", "Rule 4.3.3(a)(4)", "Use two widely circulated state-level newspapers and two national-level newspapers.", ["two"], [("state", "state-level"), ("national", "national-level")]),
    case("CGSPR-24", "gem-methods", "hinglish", "GeM par available goods ko purchase karne ke liye Rule 4.3.3 kaun-kaun se GeM methods mention karta hai?", "Rule 4.3.3(c)", "The rule mentions Direct Purchase, L1, e-bidding and Reverse Auction on GeM, as required.", ["gem"], [("direct purchase", "direct"), ("l1", "l-1"), ("e-bidding", "e bidding"), ("reverse auction", "reverse")]),
    case("CGSPR-25", "receipts-payment", "en", "After GeM goods are received, by when must the buyer issue the Provisional Receipt Certificate (PRC)?", "Rule 4.3.3(c)", "The buyer must issue the PRC within 48 hours of receiving the goods.", ["48"], [("prc", "provisional receipt")]),
    case("CGSPR-26", "receipts-payment", "en", "After verifying GeM goods, what certificate follows the PRC and what is its deadline?", "Rule 4.3.3(c)", "After verification, issue the Consignee Receipt and Acceptance Certificate (CRAC/CARC) within 10 days from PRC issuance.", ["10 days"], [("crac", "carc", "acceptance certificate"), ("prc", "provisional receipt")]),
    case("CGSPR-27", "receipts-payment", "hinglish", "GeM mein CRAC/CARC issue hone ke baad payment kab tak karna chahiye?", "Rule 4.3.3(c)", "Payment should be made within 10 days from issuance of the acceptance certificate, subject to effective GeM directions.", ["10 days"], [("payment", "pay"), ("crac", "carc", "acceptance")]),
    case("CGSPR-28", "open-tender", "en", "For a first Open Tender, how many eligible tenderers must normally be ensured for adequate competition?", "Rule 4.3.3(d)", "The first invitation should ensure participation of at least three eligible tenderers, through manufacturers or authorised supplier representatives.", ["three"], [("eligible", "qualified"), ("open tender", "first tender")]),
    case("CGSPR-29", "open-tender", "hinglish", "Agar tender notice publish karne ke baad sufficient bids nahi aayi, department ko kya karna chahiye?", "Rule 4.12", "Call the tender again and make efforts to ensure that the notice reaches all potential tenderers.", ["tender"], [("again", "re-tender", "retender", "fresh"), ("potential", "all bidders", "widely")]),
    case("CGSPR-30", "tender-notice", "en", "What essential information should a short tender notice include?", "Rules 4.4 and 4.4.1", "It should briefly state the main goods/purpose and essential conditions such as the last date and time for accepting tenders; detailed terms may be made available with the tender form.", ["last date"], [("goods", "item", "purpose"), ("time", "deadline"), ("detailed", "tender form")]),
    case("CGSPR-31", "tender-notice", "en", "Must a competent officer state reasons before cancelling an invited tender under Rule 4.4.3?", "Rule 4.4.3", "No. The competent officer may cancel an invited tender at any time without stating reasons.", ["without"], [("reason", "reasons"), ("competent officer", "competent authority")]),
    case("CGSPR-32", "tender-timelines", "hinglish", "Limited Tender ke first, second aur third invitation ke minimum timelines kya hain?", "Rule 4.5", "Limited Tender timelines are 15 days for first invitation, 10 days for second, and 5 days for third.", ["15"], [("10",), ("5",)]),
    case("CGSPR-33", "tender-timelines", "en", "State the first/second/third invitation timelines for an Open Tender above Rs. 3,00,001 and up to Rs. 10 lakh.", "Rule 4.5", "The timelines are 21, 14 and 7 days respectively.", ["21"], [("14",), ("7",)]),
    case("CGSPR-34", "tender-timelines", "en", "State the first/second/third invitation timelines for an Open Tender above Rs. 10 lakh.", "Rule 4.5", "The timelines are 30, 20 and 10 days respectively.", ["30"], [("20",), ("10",)]),
    case("CGSPR-35", "tender-timelines", "hinglish", "Global Tender ke first, second aur third invitation ke liye kitne din hain?", "Rule 4.5", "Global Tender timelines are 45, 30 and 20 days respectively.", ["45"], [("30",), ("20",)]),
    case("CGSPR-36", "bid-opening", "en", "For an offline tender, when should tenders be opened in relation to the submission deadline?", "Rule 4.6.3", "Open them one hour after the stipulated closing time on the same day; online tenders follow the published schedule.", ["one hour"], [("same day", "same date"), ("online", "schedule")]),
    case("CGSPR-37", "emd", "en", "In a two-envelope tender, which envelope is opened first and when is the tender-form envelope opened?", "Rule 4.6.4", "Open the EMD/exemption-certificate envelope first. Open the tender-form envelope only if sufficient EMD or a valid exemption certificate is present; otherwise reject the bid.", ["emd"], [("first",), ("exemption", "certificate"), ("reject", "rejected")]),
    case("CGSPR-38", "bid-opening", "hinglish", "Deadline ke baad receive hui offline tender ko department ko open karna chahiye ya return?", "Rule 4.6.5", "A tender received after the prescribed final date and time must not be opened; it should be returned, noting the return date and time on the sealed envelope.", ["not be opened"], [("return", "returned"), ("date", "time")]),
    case("CGSPR-39", "emd", "en", "What EMD percentage must normally accompany each tender under Rule 4.7?", "Rule 4.7(a)", "EMD of 1% of the estimated purchase value is normally required with each tender.", ["1%"], [("estimated", "estimate"), ("emd", "earnest money")]),
    case("CGSPR-40", "emd", "en", "What happens to EMD after tender finalisation for the successful bidder and the other bidders?", "Rule 4.7(a)", "Retain the successful bidder's EMD and refund the remaining bidders' EMD within 15 days.", ["successful"], [("retain", "retained", "keep"), ("15 days", "fifteen days"), ("refund", "return")]),
    case("CGSPR-41", "emd", "hinglish", "Registered small/cottage unit ya valid startup ko EMD exemption kab milegi?", "Rules 4.7(b)-(c)", "A qualifying registered small/cottage unit or valid recognised startup can receive EMD exemption only after submitting the required proof/certificate with the tender.", ["emd"], [("startup", "small", "cottage"), ("certificate", "proof", "document"), ("with the tender", "submit")]),
    case("CGSPR-42", "security-deposit", "en", "Before issuing a purchase order to the eligible successful bidder, what minimum security deposit is required?", "Rule 4.7.1", "Obtain security deposit of at least 3% of the actual purchase value before issuing the purchase order.", ["3%"], [("actual purchase value", "actual value"), ("before", "prior")]),
    case("CGSPR-43", "security-deposit", "en", "Can the prescribed security deposit or EMD be accepted in cash?", "Rule 4.8(a)", "No. The prescribed security deposit/EMD must not be accepted in cash.", ["cash"], [("no", "not")]),
    case("CGSPR-44", "tender-conditions", "hinglish", "Tender conditions aur GST/tax details ke baare mein Rule 4.9 kya kehta hai?", "Rule 4.9", "Conditions must be clear and unambiguous; the bidder must be GST-registered for the tendered goods, and quoted rates must separately state taxes.", ["clear"], [("gst", "registration"), ("tax", "taxes"), ("separately", "separate")]),
    case("CGSPR-45", "quality", "en", "If a sample cannot be obtained before purchase, how can the buyer protect quality under Rule 4.10?", "Rule 4.10", "The supplier may demonstrate the item; if that is also not possible, the contract should reserve the buyer's right to inspect at the manufacturing site.", ["inspection"], [("demonstration", "demonstrate", "demo"), ("manufacturing site", "manufacturing", "factory")]),
    case("CGSPR-46", "purchase-committee", "en", "When is a purchase committee compulsory, and who must be included?", "Rule 4.12", "Every office purchasing Rs. 50,000 or more per year must form a purchase committee including the departmental accounts officer/accounts in-charge and officers with technical knowledge of the goods.", ["50,000"], [("accounts", "account"), ("technical", "expert")]),
    case("CGSPR-47", "purchase-committee", "hinglish", "Agar L1/lowest tender accept nahi ki ja rahi, to committee ko kya karna hoga?", "Rule 4.12", "When the lowest tender is not accepted, the reasons for not accepting it must be recorded in writing.", ["lowest"], [("reasons", "reason"), ("writing", "written", "record")]),
    case("CGSPR-48", "purchase-order", "en", "May a purchase order be issued before a contract is executed with the supplier?", "Rule 4.13", "No. Execute the contract before issuing the purchase order; it should bind supply within the fixed time and to the sample/specification.", ["before"], [("contract", "agreement"), ("purchase order", "po")]),
    case("CGSPR-49", "repeat-order", "en", "Can a repeat supply order be issued seven months after the original order, and what is the maximum repeat quantity?", "Rule 4.14", "No repeat order may be issued after six months from the original order. A repeat order cannot exceed 25% of the original order quantity.", ["six months"], [("25%", "25 percent"), ("repeat order", "repeat")]),
    case("CGSPR-50", "inspection-payment", "hinglish", "Delivered goods ki quality inspection aur supplier payment ke liye Rule 11 kya timelines deta hai?", "Rule 11", "Arrange quality inspection at the delivery site within a maximum of 10 days; departments must pay the bill according to rules within 20 days of receiving goods and the bill.", ["10 days"], [("inspection", "quality"), ("20 days", "twenty days"), ("payment", "pay")]),
]


def parse_sse(response):
    events = []
    for raw in response.iter_lines(decode_unicode=True):
        if raw and raw.startswith("data: "):
            try:
                events.append(json.loads(raw[6:]))
            except json.JSONDecodeError:
                events.append({"type": "parse_error", "raw": raw})
    return events


def normalized(text):
    return re.sub(r"\s+", " ", (text or "").casefold()).strip()


def has_term(answer, term):
    term = normalized(term)
    return term in normalized(answer)


def source_is_store_rule(source):
    return SOURCE_TOKEN in normalized(source)


def score(case_row, answer, retrieved, final_sources, error, done):
    all_hits = [term for term in case_row["required_all"] if has_term(answer, term)]
    all_missing = [term for term in case_row["required_all"] if term not in all_hits]
    group_hits, group_missing = [], []
    for group in case_row["required_any_groups"]:
        matched = next((term for term in group if has_term(answer, term)), None)
        (group_hits if matched else group_missing).append(matched or " / ".join(group))
    low = normalized(answer)
    prohibited = [claim for claim in case_row["prohibited_claims"] if normalized(claim) in low]
    fallback = any(marker in low for marker in FALLBACK_MARKERS)
    source_retrieved = any(source_is_store_rule(s) for s in retrieved)
    source_final = any(source_is_store_rule(s) for s in final_sources)
    response_ok = bool(answer.strip()) and not error and not fallback
    rule_coverage = (len(all_hits) + len(group_hits)) / max(1, len(case_row["required_all"]) + len(case_row["required_any_groups"]))
    correct = response_ok and not prohibited and not all_missing and not group_missing
    classification = "Pass" if (correct and source_final) else ("Partial" if response_ok and rule_coverage >= 0.5 and not prohibited else "Fail")
    return {
        "classification": classification, "rule_correctness": correct,
        "rule_coverage": round(rule_coverage, 3), "required_all_hit": all_hits,
        "required_all_missing": all_missing, "required_groups_hit": group_hits,
        "required_groups_missing": group_missing, "prohibited_claims_found": prohibited,
        "fallback_used": fallback, "store_rule_retrieved": source_retrieved,
        "store_rule_in_final_sources": source_final,
    }


def run_one(case_row, endpoint, timeout):
    started = time.perf_counter(); events = []; error = None; status = None
    try:
        with requests.post(endpoint, json={"query": case_row["query"], "diagnostics": True, "session_id": case_row["id"]}, stream=True, timeout=(15, timeout)) as response:
            status = response.status_code
            response.raise_for_status()
            events = parse_sse(response)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    elapsed = round(time.perf_counter() - started, 3)
    contexts = [event for event in events if event.get("type") == "context"]
    results = contexts[-1].get("results", []) if contexts else []
    retrieved = [item.get("actual_pdf") or item.get("source") or "" for item in results]
    done_events = [event for event in events if event.get("type") == "done"]
    done = done_events[-1] if done_events else {}
    answer = done.get("answer") or "".join(event.get("content", "") for event in events if event.get("type") == "token")
    final_sources = done.get("sources") or []
    scored = score(case_row, answer, retrieved, final_sources, error, done)
    return {
        **case_row, **scored, "answer": answer, "retrieved_sources": retrieved,
        "final_sources": final_sources, "response_time_seconds": elapsed,
        "http_status": status, "error": error,
        "detected_actor": done.get("detected_actor"), "detected_intent": done.get("detected_intent"),
        "generation_diagnostics": done.get("diagnostics") or {},
        "sse_event_types": [event.get("type", "unknown") for event in events],
    }


def percentage(rows, predicate):
    return round(100 * sum(bool(predicate(row)) for row in rows) / len(rows), 2) if rows else 0.0


def percentile(values, fraction):
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * fraction
    lower, upper = int(position), min(int(position) + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def report(rows, summary):
    lines = ["# CG Store Purchase Rules — independent 50-question benchmark", "", "## Outcome", ""]
    lines += [f"- **{key.replace('_', ' ')}:** {value}" for key, value in summary.items() if key != "by_bucket"]
    lines += ["", "## Scoring method", "", "A response passes only when it answers every rule-linked rubric item, contains no configured unsafe claim, and cites the CG Store Purchase Rules in final sources. This is a reproducible automated correctness screen; it is not a legal opinion.", "", "## Full responses", ""]
    for row in rows:
        lines += [
            f"### {row['id']} — {row['classification']}",
            f"- **Question:** {row['query']}", f"- **Rule:** {row['expected_rule']}",
            f"- **Reference answer:** {row['reference_answer']}",
            f"- **Required evidence hit:** {', '.join(row['required_all_hit'] + row['required_groups_hit']) or 'None'}",
            f"- **Missing evidence:** {', '.join(row['required_all_missing'] + row['required_groups_missing']) or 'None'}",
            f"- **Store Rules retrieved / cited:** {row['store_rule_retrieved']} / {row['store_rule_in_final_sources']}",
            f"- **Sources:** {', '.join(row['final_sources']) or 'None'}",
            f"- **Latency:** {row['response_time_seconds']}s", "", "**Chatbot response**", "", row['answer'] or "_No response returned._", "",
        ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://127.0.0.1:8080/api/stream")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    HERE.mkdir(parents=True, exist_ok=True)
    (HERE / "dataset.json").write_text(json.dumps(CASES, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_one, row, args.endpoint, args.timeout): row for row in CASES}
        for future in concurrent.futures.as_completed(futures):
            result = future.result(); rows.append(result)
            with PRINT_LOCK:
                print(f"[{len(rows):02d}/{len(CASES)}] {result['id']} {result['classification']} {result['response_time_seconds']:.2f}s", flush=True)
    rows.sort(key=lambda row: row["id"])
    latencies = [row["response_time_seconds"] for row in rows]
    summary = {
        "total_questions": len(rows), "pass": sum(row["classification"] == "Pass" for row in rows),
        "partial": sum(row["classification"] == "Partial" for row in rows), "fail": sum(row["classification"] == "Fail" for row in rows),
        "rule_correctness_percent": percentage(rows, lambda row: row["rule_correctness"]),
        "store_rule_retrieval_percent": percentage(rows, lambda row: row["store_rule_retrieved"]),
        "store_rule_final_citation_percent": percentage(rows, lambda row: row["store_rule_in_final_sources"]),
        "fallback_rate_percent": percentage(rows, lambda row: row["fallback_used"]),
        "average_rule_coverage_percent": round(100 * statistics.mean(row["rule_coverage"] for row in rows), 2),
        "median_latency_seconds": round(statistics.median(latencies), 3), "p95_latency_seconds": round(percentile(latencies, .95), 3),
        "by_bucket": dict(Counter(row["bucket"] for row in rows)),
    }
    (HERE / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "full_response_report.md").write_text(report(rows, summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
