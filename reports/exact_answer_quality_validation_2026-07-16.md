# Exact Answer Quality Validation — 16 July 2026

## Scope

This validation covers the narrow-answer repair for:

- D9: submitting the financial/price/BOQ portion after the technical bid;
- E10: preparing or generating a department evaluation report;
- the earlier Phase 2 software-licence and AMC buyer workflows; and
- the answer-quality metric added to the production benchmark runner.

No retrieval, embedding, Qdrant, chunking, reranking, actor-routing, or model configuration was changed.

## Code-level regression result

`python -m unittest test_fine_intent_routing test_actor_boundary_audit test_purchase_workflow`

Result: **49 passed**.

The suite includes actor boundaries, narrow-answer contracts, D9/ E10 source-supported content, and software/AMC workflow checks.

## Live API validation

The normal Waitress backend was restarted and queried through `/api/stream` with `diagnostics: true`. Each result below is a grounded deterministic answer; `fallback_reason_code` was null.

| Query | Actor | Fine intent | Principal source | Time | Result |
|---|---|---|---|---:|---|
| Open vs Limited Tender | general_information_user | tender_method_definition | Store Purchase Rules / Procurement Manual | 1.57s | Pass |
| When is Single Tender allowed? | general_information_user | tender_method_definition | Store Purchase Rules / Procurement Manual | 1.33s | Pass |
| Department-to-department purchase | general_information_user | procurement_methods_overview | Store Purchase Rules | 1.82s | Pass |
| Direct GeM laptop purchase | department_buyer | gem_direct_purchase_rule | Store Purchase Rules / GFR | 1.50s | Pass |
| Laptop specifications | department_buyer | specification_preparation | Procurement Manual / CVC guidance | 1.55s | Pass |
| Startup tender participation | general_information_user | tender_eligibility | Bid Submission Manual | 1.43s | Pass |
| Foreign company participation | vendor_bidder | vendor_registration | Vendor Registration Manual | 1.03s | Pass |
| Edit after bid deadline | vendor_bidder | bid_submission_portal_steps | Bid Submission Manual | 1.48s | Pass |
| D9: financial bid after technical bid | vendor_bidder | bid_submission_portal_steps | Bid Submission Manual | 1.54s | Pass |
| E10: evaluation report generation | department_operator | bid_evaluation | Store Purchase Rules / Procurement Manual | 1.51s | Pass |
| Software licence purchase | department_buyer | procurement_planning | Store Purchase Rules / Procurement Manual | 1.68s | Pass |
| AC AMC procurement | department_buyer | procurement_planning | Store Purchase Rules / Procurement Manual | 1.73s | Pass |

**Focused live result: 12 / 12 pass; no workflow leakage; mean latency 1.51s; maximum 1.82s.**

## D9 answer check

The live response answers the requested stage only: use the same tender's Financial Bid/Price Bid/BOQ part, enter or upload required rates, validate totals, sign/encrypt using a valid DSC, submit before the deadline, and verify acknowledgement/status. It explicitly avoids restarting vendor registration.

## E10 answer check

The live response gives report content rather than invented portal clicks: bid-opening record, eligibility/compliance review, technical responsiveness, responsive/non-responsive bids and rejection reasons, financial comparison, L1/rate-reasonableness assessment, applicable preferences/exemptions, recommendation, and approval record. It states that the available corpus does not verify a universal menu/button sequence.

## Browser-format check

Backend output has clean heading and source fields. The requested rendered-browser check could not be completed because the local desktop browser-control runtime fails during initialisation with a `Cannot redefine property: process` environment error. This is recorded as **environment-blocked**, not as a visual pass. No frontend code was changed.

## Benchmark scoring change

`eval/production_120/run_benchmark.py` now records `answer_mode` and `exact_question_answering`, and includes `exact_question_answering_accuracy_percent` in the aggregate. This measures whether narrow questions are answered narrowly, rather than treating a broadly factual answer as automatically correct.

