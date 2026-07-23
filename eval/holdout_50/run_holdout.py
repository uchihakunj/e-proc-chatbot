"""Evaluation-only 50-question holdout UAT for the eproc-chatbot chatbot."""
from __future__ import annotations

import csv
import json
import statistics
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WEBUI = ROOT / "05_webui"
sys.path.insert(0, str(WEBUI))
from actor_boundary import detect_response_language
from fine_intent_policy import detect_answer_mode
from nlp_features import classify_actor, classify_intent, correct_typos, detect_commodity
from fine_intent_policy import classify_fine_intent

SOURCE = {
    "planning": ["store purchase rule cg.pdf", "publicProManual-1755343081262-715558279.pdf"],
    "method": ["store purchase rule cg.pdf", "GFRupdatedupto31012026.pdf"],
    "approval": ["store purchase rule cg.pdf", "publicProManual-1755343081262-715558279.pdf"],
    "evaluation": ["publicProManual-1755343081262-715558279.pdf", "GFRupdatedupto31012026.pdf"],
    "specification": ["publicProManual-1755343081262-715558279.pdf", "Compilation of CVC Circulars and Guidelines.pdf"],
    "eligibility": ["Guidelines_To_Bidders_EPS_v1.6.pdf", "publicProManual-1755343081262-715558279.pdf"],
    "portal": ["CHiPS_Bid_Submission_Manual_English.pdf"],
    "corrigendum": ["CHiPS_Corrigendum_Issuance_Manual.pdf", "CHiPS_Bid_Submission_Manual_English.pdf"],
    "payment": ["Online_EMD_Refund_Notice.pdf", "EMD_CHALLAN_PAYMENT_V1.0.pdf"],
}

PROFILE = {
    "planning": (["requirement", "estimate", "approval"], ["requirement", "budget", "method"], ["vendor registration", "submit bid"]),
    "method": (["GeM", "rules", "approval"], ["method", "value", "approval"], ["invented threshold", "unrestricted direct purchase"]),
    "single": (["exceptional", "justification", "approval"], ["single source", "written justification", "approval"], ["convenience alone", "automatic permission"]),
    "split": (["consolidated", "split", "requirement"], ["must not split", "consolidated"], ["split to avoid", "always direct purchase"]),
    "approval": (["budget", "approval", "sanction"], ["approval", "budget", "competent"], ["order before approval", "skip sanction"]),
    "evaluation": (["eligibility", "responsive", "price"], ["evaluation", "reasons", "approval"], ["lowest automatically wins", "ignore tender conditions"]),
    "specification": (["generic", "measurable", "competition"], ["generic", "technical justification", "equivalent"], ["brand automatically allowed", "restrict competition"]),
    "eligibility": (["tender conditions", "documents", "eligibility"], ["tender-specific", "evidence"], ["automatic eligibility", "automatic exemption"]),
    "portal": (["bid", "deadline", "DSC"], ["portal", "bid", "deadline"], ["department approval", "buyer workflow"]),
    "corrigendum": (["corrigendum", "bid", "tender"], ["corrigendum", "check", "submit"], ["department workflow for bidder"]),
    "payment": (["EMD", "status", "receipt"], ["EMD", "status", "support"], ["assume payment successful", "ignore deadline"]),
    "inspection": (["inspection", "acceptance", "payment"], ["inspection", "acceptance"], ["release payment without acceptance"]),
}

# id, question, actor, fine intent, expected answer mode, source family, profile
RAW = [
 ("H50-01","Our office needs 30 laptops. How should we decide whether to use GeM or a tender?","department_buyer","procurement_planning","direct_answer","planning","planning"),
 ("H50-02","Department ko ₹4 lakh ka furniture kharidna hai. Kaunsa procurement method use karna chahiye?","department_buyer","procurement_method_selection","direct_answer","method","method"),
 ("H50-03","Can we buy an item directly if only one quotation is available on GeM?","department_buyer","gem_direct_purchase_rule","direct_answer","method","method"),
 ("H50-04","Agar item GeM par available nahi hai, department ko next kya karna chahiye?","department_buyer","procurement_method_selection","direct_answer","method","method"),
 ("H50-05","Can a department invite quotations from three local suppliers instead of issuing an open tender?","department_buyer","tender_method_definition","direct_answer","method","method"),
 ("H50-06","Hamare office ko urgently printers chahiye, lekin emergency nahi hai. Fastest lawful option kya hai?","department_buyer","procurement_method_selection","direct_answer","method","method"),
 ("H50-07","What factors should be checked before choosing Limited Tender?","general_information_user","tender_method_definition","direct_answer","method","method"),
 ("H50-08","When should an Open Tender be preferred over Limited Tender?","general_information_user","tender_method_definition","comparison","method","method"),
 ("H50-09","Can Single Tender be used because the earlier supplier already knows our system?","department_buyer","tender_method_definition","policy_conditions","method","single"),
 ("H50-10","Ek proprietary software sirf ek company provide karti hai. Kya Single Tender allowed hoga?","department_buyer","tender_method_definition","policy_conditions","method","single"),
 ("H50-11","Can the department purchase spare parts only from the original equipment manufacturer?","department_buyer","tender_method_definition","direct_answer","method","single"),
 ("H50-12","Government department ko dusre government undertaking se goods purchase karne hain. Kya tender zaroori hai?","general_information_user","procurement_methods_overview","yes_no_policy","method","method"),
 ("H50-13","Can we split a ₹10 lakh requirement into five smaller purchase orders?","department_buyer","procurement_planning","restriction_or_prohibition","planning","split"),
 ("H50-14","Same item alag-alag months mein chahiye. Kya har month direct purchase kar sakte hain?","department_buyer","procurement_planning","direct_answer","planning","split"),
 ("H50-15","How should the department estimate the total procurement value before selecting the method?","department_buyer","procurement_planning","direct_answer","planning","planning"),
 ("H50-16","Purchase start karne se pehle administrative approval aur financial sanction mein kya difference hai?","department_buyer","approval_and_budget","comparison","approval","approval"),
 ("H50-17","Who should confirm budget availability before a tender is published?","department_buyer","approval_and_budget","direct_answer","approval","approval"),
 ("H50-18","Can a tender be initiated before the budget is formally available?","department_buyer","approval_and_budget","direct_answer","approval","approval"),
 ("H50-19","Department ke paas budget hai, lekin financial sanction pending hai. Kya GeM order place kar sakte hain?","department_buyer","approval_and_budget","direct_answer","approval","approval"),
 ("H50-20","What records should be kept to prove that the selected procurement method was justified?","department_buyer","approval_and_budget","direct_answer","approval","approval"),
 ("H50-21","Can the competent authority approve a purchase after the order has already been placed?","department_buyer","approval_and_budget","direct_answer","approval","approval"),
 ("H50-22","What is delegated financial power, and how does it affect procurement method selection?","department_buyer","approval_and_budget","direct_answer","approval","approval"),
 ("H50-23","Agar purchase value officer ki delegated power se zyada hai, to next approval kis stage par lena chahiye?","department_buyer","approval_and_budget","direct_answer","approval","approval"),
 ("H50-24","Can the department use last year's approved rate without conducting a fresh procurement?","department_buyer","procurement_method_selection","direct_answer","method","method"),
 ("H50-25","How should price reasonableness be established when only one valid bid is received?","department_buyer","bid_evaluation","direct_answer","evaluation","evaluation"),
 ("H50-26","Kya lowest quotation milne ka matlab price reasonable hai?","general_information_user","bid_evaluation","direct_answer","evaluation","evaluation"),
 ("H50-27","What should the department do if all received bids are much higher than the estimated cost?","department_buyer","bid_evaluation","direct_answer","evaluation","evaluation"),
 ("H50-28","Can negotiations be conducted with the L1 bidder after opening financial bids?","department_buyer","bid_evaluation","direct_answer","evaluation","evaluation"),
 ("H50-29","Tender cancel karne ke liye kya reasons record karne chahiye?","department_operator","tender_creation_policy","direct_answer","evaluation","evaluation"),
 ("H50-30","Can the department reject all bids without giving any reason?","department_buyer","bid_evaluation","direct_answer","evaluation","evaluation"),
 ("H50-31","Can we mention a preferred brand and write ‘or equivalent’ in the technical specifications?","department_buyer","specification_preparation","direct_answer","specification","specification"),
 ("H50-32","Laptop specification banate waqt processor brand mention karna allowed hai kya?","department_buyer","specification_preparation","direct_answer","specification","specification"),
 ("H50-33","How can specifications be written so that they do not favour one vendor?","department_buyer","specification_preparation","direct_answer","specification","specification"),
 ("H50-34","Can experience and turnover requirements be higher than the estimated tender value?","general_information_user","tender_eligibility","direct_answer","eligibility","eligibility"),
 ("H50-35","Tender mein three-year experience mandatory rakhna kab justified hota hai?","department_buyer","tender_eligibility","direct_answer","eligibility","eligibility"),
 ("H50-36","Can a startup be exempted from prior experience and turnover requirements?","vendor_bidder","tender_eligibility","specific_portal_step","eligibility","eligibility"),
 ("H50-37","Does MSME registration automatically make a bidder eligible for every tender?","vendor_bidder","tender_eligibility","specific_portal_step","eligibility","eligibility"),
 ("H50-38","Can EMD exemption be claimed without uploading the required registration certificate?","vendor_bidder","emd_exemption","direct_answer","eligibility","eligibility"),
 ("H50-39","What should happen if a bidder meets the technical specification but misses one mandatory document?","department_operator","bid_evaluation","direct_answer","evaluation","evaluation"),
 ("H50-40","A bidder uploaded an expired certificate. Should the bid be rejected or can clarification be requested?","department_operator","bid_evaluation","direct_answer","evaluation","evaluation"),
 ("H50-41","Technical evaluation ke baad financial bids kin bidders ki open honi chahiye?","department_operator","bid_opening_portal_steps","direct_answer","portal","portal"),
 ("H50-42","Can a technically non-responsive bidder be selected because its price is the lowest?","general_information_user","bid_evaluation","direct_answer","evaluation","evaluation"),
 ("H50-43","L1 bidder ki rate estimate se 25% zyada hai. Department ko kya karna chahiye?","department_buyer","bid_evaluation","direct_answer","evaluation","evaluation"),
 ("H50-44","How should the evaluation committee record reasons for rejecting a bidder?","department_operator","bid_evaluation","direct_answer","evaluation","evaluation"),
 ("H50-45","Can tender conditions be changed after bids have already been opened?","department_operator","corrigendum_policy","direct_answer","corrigendum","corrigendum"),
 ("H50-46","Purchase Order issue hone ke baad vendor delivery delay kare to department kya action le sakta hai?","department_buyer","purchase_order","direct_answer","evaluation","evaluation"),
 ("H50-47","Goods receive ho gaye, but specification match nahi kar rahi. Payment release karna chahiye kya?","department_buyer","inspection_and_acceptance","direct_answer","evaluation","inspection"),
 ("H50-48","What documents should be completed before processing payment to the supplier?","department_buyer","payment_and_asset_entry","direct_answer","evaluation","inspection"),
 ("H50-49","Bid submit karne ke baad corrigendum se specifications change ho gayi. Kya mujhe bid dobara submit karni hogi?","vendor_bidder","bidder_corrigendum_tracking","direct_answer","corrigendum","corrigendum"),
 ("H50-50","EMD payment successful hai but portal par status pending dikh raha hai, aur deadline close hai. Main kya karun?","vendor_bidder","emd_payment_failure","direct_answer","payment","payment"),
]

CASES = [dict(id=i, question=q, expected_actor=a, expected_fine_intent=t, expected_answer_mode=m,
              expected_source_documents=SOURCE[s], expected_evidence_concepts=PROFILE[p][0],
              required_answer_concepts=PROFILE[p][1], prohibited_unsafe_claims=PROFILE[p][2])
         for i, q, a, t, m, s, p in RAW]

def parse_sse(response):
    for raw in response.iter_lines(decode_unicode=True):
        if raw and raw.startswith("data: "):
            try: yield json.loads(raw[6:])
            except json.JSONDecodeError: pass

def source_match(expected, observed):
    normal = lambda x: (x or "").lower().replace("_", " ").replace("-", " ")
    found = [e for e in expected if any(normal(e).replace(".pdf", "") in normal(o) or normal(o).replace(".pdf", "") in normal(e) for o in observed)]
    return found

def coverage(answer, concepts):
    low = (answer or "").lower()
    hits = [c for c in concepts if c.lower() in low]
    return round(len(hits) / len(concepts), 3) if concepts else 1.0, hits

def classify(question):
    corrected = correct_typos(question)
    normal = corrected[0] if isinstance(corrected, tuple) else corrected
    actor, confidence = classify_actor(normal)
    coarse, _ = classify_intent(normal)
    intent, intent_conf = classify_fine_intent(normal, actor, coarse, detect_commodity(normal))
    return actor, confidence, intent, intent_conf, detect_response_language(question), detect_answer_mode(question, intent)

def run_one(case, endpoint, timeout):
    started = time.perf_counter(); events=[]; error=None; status=None
    try:
        with requests.post(endpoint, json={"query":case["question"],"diagnostics":True,"session_id":case["id"]}, stream=True, timeout=(10,timeout)) as response:
            status=response.status_code; response.raise_for_status(); events=list(parse_sse(response))
    except Exception as exc: error=f"{type(exc).__name__}: {exc}"
    elapsed=round(time.perf_counter()-started,3)
    context=[e for e in events if e.get("type")=="context"]
    top=(context[-1].get("results",[]) if context else [])
    top_sources=[r.get("actual_pdf") or r.get("source") or "" for r in top][:10]
    done=next((e for e in reversed(events) if e.get("type")=="done"),{})
    answer=done.get("answer") or "".join(e.get("content","") for e in events if e.get("type")=="token")
    actor, actor_conf, intent, intent_conf, language, answer_mode=classify(case["question"])
    req_cov, hits=coverage(answer,case["required_answer_concepts"])
    low=answer.lower(); unsafe=[p for p in case["prohibited_unsafe_claims"] if p.lower() in low]
    top_match=source_match(case["expected_source_documents"],top_sources)
    final_sources=done.get("sources") or []
    generation_diagnostics=done.get("diagnostics") or {}
    fallback_used=bool(generation_diagnostics.get("deterministic_fallback"))
    final_match=source_match(case["expected_source_documents"],final_sources)
    citation="Pass" if final_match else ("Partial" if top_match else "Fail")
    actor_ok=done.get("detected_actor",actor)==case["expected_actor"]
    intent_ok=done.get("detected_intent",intent)==case["expected_fine_intent"]
    fail=bool(error or done.get("fallback_reason_code") or unsafe or not actor_ok)
    passed=not fail and intent_ok and req_cov>=.67 and citation=="Pass"
    result="Fail" if fail else ("Pass" if passed else "Partial")
    return {**case,"detected_actor":done.get("detected_actor",actor),"actor_confidence":done.get("actor_confidence",actor_conf),
            "detected_intent":done.get("detected_intent",intent),"intent_confidence":done.get("intent_confidence",intent_conf),
            "detected_language":language,"detected_answer_mode":answer_mode,"retrieved_top_10_sources":top_sources,
            "final_context_sources":final_sources,"final_answer":answer,"citation_correctness":citation,
            "generation_diagnostics":generation_diagnostics,"fallback_used":fallback_used,
            "required_concept_coverage":req_cov,"required_concepts_hit":hits,"unsafe_claims_found":unsafe,
            "response_time_seconds":elapsed,"http_status":status,"error":error,"result":result}

def main():
    endpoint="http://127.0.0.1:5000/api/stream"; timeout=75
    rows=[]
    for n, case in enumerate(CASES,1):
        row=run_one(case,endpoint,timeout); rows.append(row); print(f"[{n:02d}/50] {case['id']} {row['result']} {row['response_time_seconds']:.2f}s",flush=True)
    HERE.mkdir(parents=True,exist_ok=True)
    (HERE/"dataset.json").write_text(json.dumps(CASES,ensure_ascii=False,indent=2),encoding="utf-8")
    (HERE/"results.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    fields=list(rows[0]);
    with (HERE/"results.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)
    summary={"total":len(rows),"pass":sum(r['result']=='Pass' for r in rows),"partial":sum(r['result']=='Partial' for r in rows),"fail":sum(r['result']=='Fail' for r in rows),
             "actor_accuracy_percent":round(100*sum(r['detected_actor']==r['expected_actor'] for r in rows)/len(rows),2),
             "fine_intent_accuracy_percent":round(100*sum(r['detected_intent']==r['expected_fine_intent'] for r in rows)/len(rows),2),
             "top10_source_recall_percent":round(100*sum(bool(source_match(r['expected_source_documents'],r['retrieved_top_10_sources'])) for r in rows)/len(rows),2),
             "final_context_source_recall_percent":round(100*sum(bool(source_match(r['expected_source_documents'],r['final_context_sources'])) for r in rows)/len(rows),2),
             "avg_required_concept_coverage_percent":round(100*statistics.mean(r['required_concept_coverage'] for r in rows),2),
             "citation_pass_percent":round(100*sum(r['citation_correctness']=='Pass' for r in rows)/len(rows),2),
             "fallbacks":sum(r.get('fallback_used', False) for r in rows),"avg_latency_seconds":round(statistics.mean(r['response_time_seconds'] for r in rows),3),
             "p95_latency_seconds":round(sorted(r['response_time_seconds'] for r in rows)[47],3)}
    (HERE/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=["# 50-question holdout UAT", "", "## Summary", ""]+[f"- {k}: **{v}**" for k,v in summary.items()]+["", "## Per-query report", ""]
    for r in rows:
        lines += [f"### {r['id']} — {r['result']}", f"- Question: {r['question']}", f"- Expected / detected actor: {r['expected_actor']} / {r['detected_actor']}", f"- Expected / detected intent: {r['expected_fine_intent']} / {r['detected_intent']}", f"- Expected / detected answer mode: {r['expected_answer_mode']} / {r['detected_answer_mode']}", f"- Expected sources: {', '.join(r['expected_source_documents'])}", f"- Evidence concepts: {', '.join(r['expected_evidence_concepts'])}", f"- Required concepts: {', '.join(r['required_answer_concepts'])}", f"- Prohibited claims: {', '.join(r['prohibited_unsafe_claims'])}", f"- Retrieved top-10: {', '.join(r['retrieved_top_10_sources'])}", f"- Final-context sources: {', '.join(r['final_context_sources'])}", f"- Citation correctness: {r['citation_correctness']}", f"- Response time: {r['response_time_seconds']}s", f"- Final answer: {r['final_answer']}", ""]
    (HERE/"report.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
