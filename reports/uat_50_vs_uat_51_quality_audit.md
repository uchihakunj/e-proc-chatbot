# UAT Answer Quality Audit: Manual 50 vs Chatbot 51

## Scope

`uat_50_manual_responses_from_documents.md` contains 50 document-grounded reference answers. `uat_51_full_response_report.md` contains 51 chatbot answers: the same 50 topics plus A11, *different ways of government procurement*.

The 51-report's `51 Pass / 0 Partial / 0 Fail` result was a routing/retrieval compliance result. It was not a reliable answer-quality score: it accepted an answer when actor, fine intent and source-family checks passed, even if the answer did not directly resolve the user's question.

## Material comparison findings

| Area | Chatbot response in the 51 report | Reference-answer expectation | Assessment |
|---|---|---|---|
| B6: splitting a purchase | Returned the generic end-to-end buyer workflow. | State the direct prohibition on splitting a known requirement to avoid sanctions/thresholds. | Direct-answer failure. |
| C4: obtaining a DSC | Started with foreign-vendor/Indian-embassy details. | Give the normal domestic DSC route first; foreign conditions are conditional. | Wrong default audience. |
| C9: eligibility criteria | Added unrelated short-tender and system-admin statements. | Give the NIT eligibility/document/corrigendum checklist. | Topic drift. |
| C10: registration approval time | Returned registration steps but did not say whether a fixed time exists. | Say that the manual does not specify a fixed approval time. | Key constraint omitted. |
| D8/D9: bid deadline and price bid | Broad bid-submission workflow could be accepted without directly answering the deadline/price-bid condition. | Explicitly distinguish before/after deadline and require final successful submission. | Insufficient semantic guard. |
| E4/E5: opening bids | Used generic portal labels such as `Tender module` and `Technical/PQ Bid` without a manual establishing a universal screen sequence. | Use only supported operator workflow; avoid invented UI labels. | Unsupported portal detail. |
| E10: evaluation report | Answered evaluation generally, not report-generation capability. | Say what is supported by evidence and avoid claiming a portal action not documented. | Capability overclaim risk. |

## Root cause

1. The quality gate checked required words, forbidden workflow terms, language and source title. It did not test whether the response addressed the question's decisive condition (for example, *split*, *how long*, or *after deadline*).
2. Several fine intents used open-ended model generation even when the question was a stable, high-risk portal or policy question.
3. Actor matching missed the phrase `Tender eligibility criteria kaise check karun?`, so the answer could take a general-information route.
4. Answer-cache hits can bypass retrieval/generation; cache entries must be treated as invalid after a responder-policy change or be evaluated again before reuse.

## Fixes applied

- Added a direct, grounded anti-splitting answer for department-buyer questions.
- Added the distinct `vendor_registration_approval_time` intent. It states that the supplied manual has no fixed approval timeline instead of returning generic registration steps.
- Added deterministic, source-bound responses for DSC obtainment, tender eligibility, technical-vs-financial-bid comparison, and bid opening.
- Corrected actor and coarse-intent signals for `Tender eligibility criteria ...`, routing it to `vendor_bidder → tender_eligibility`.
- Added regression tests for all five high-risk cases and the direct purchase-splitting answer.

## Verification

- `python -m unittest test_purchase_workflow test_fine_intent_routing`: **37 passed**.
- Python syntax compilation passed for the changed modules.
- Live API check confirmed: `Tender eligibility criteria kaise check karun?` routes to `vendor_bidder → tender_eligibility`, uses the deterministic responder, and returns the NIT eligibility checklist.
- The local app is running at `http://127.0.0.1:3000/` with an initialized RAG pipeline.

## Remaining validation recommendation

Re-run the 51-question UAT with semantic acceptance criteria: each case should define the mandatory answer assertion(s), not just expected actor, intent and source. Record `Pass`, `Partial` or `Fail` from those assertions; do not carry forward the earlier 100% factual-accuracy figure.
