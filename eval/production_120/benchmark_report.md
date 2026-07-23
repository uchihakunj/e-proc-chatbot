# Production Procurement Benchmark — 120 Queries

## Executive summary

- Pass: 28/120 (23.33%)
- Partial: 18/120 (15.00%)
- Fail: 74/120 (61.67%)
- Expected limitation: 0/120 (0.00%)

The benchmark is frozen at 30 department-buyer, 30 vendor/bidder, 25 department-operator, 25 general-information and 10 ambiguous/mixed-role phrasings. Language balance is 45 English, 45 Hinglish and 30 Hindi. Every answer was sent to the production `/api/stream` path with an isolated session ID.

## Layer metrics

| Layer | Result |
|---|---:|
| Actor accuracy | 68.33% |
| Fine-intent accuracy | 54.17% |
| Retrieval top-5 accuracy | 80.00% |
| Final-context accuracy | 75.00% |
| Answer factual accuracy | 54.17% |
| Citation/source-list accuracy | 75.00% |
| Procedural completeness | 76.67% |
| Language consistency | 96.67% |
| Fallback rate | 48.33% |
| Workflow leakage rate | 0.00% |
| Streaming consistency | 99.17% |

Automated factual scoring uses intent-specific concept groups stored in `run_benchmark.py`; it is stricter than simple keyword overlap but is not a substitute for a legal-policy review. Citation scoring verifies that every final source was retrieved and that at least one expected evidence family survived final context selection.

## Latency

| Statistic | Seconds |
|---|---:|
| Median | 8.697 |
| P90 | 21.563 |
| P95 | 21.705 |
| Maximum | 22.114 |

## Actor confusion matrix

| Expected \ Detected | department_buyer | vendor_bidder | department_operator | general_information_user |
|---|---:|---:|---:|---:|
| department_buyer | 25 | 0 | 0 | 8 |
| vendor_bidder | 0 | 16 | 0 | 14 |
| department_operator | 2 | 2 | 10 | 11 |
| general_information_user | 0 | 0 | 1 | 31 |

## Fine-intent confusion pairs

| Expected fine intent | Detected fine intent | Count |
|---|---|---:|
| procurement_planning | procurement_planning | 11 |
| tender_method_definition | tender_method_definition | 6 |
| corrigendum_portal_steps | corrigendum_policy | 5 |
| bid_opening_portal_steps | unknown | 4 |
| bid_submission_portal_steps | unknown | 4 |
| emd_definition | emd_definition | 4 |
| tender_creation_portal_steps | unknown | 4 |
| corrigendum_policy | corrigendum_policy | 3 |
| corrigendum_portal_steps | corrigendum_portal_steps | 3 |
| dsc_mapping | dsc_mapping | 3 |
| procurement_method_selection | procurement_planning | 3 |
| procurement_methods_overview | unknown | 3 |
| specification_preparation | specification_preparation | 3 |
| tender_publication_portal_steps | unknown | 3 |
| auction_participation | unknown | 2 |
| emd_exemption | emd_exemption | 2 |
| emd_payment | emd_payment | 2 |
| emd_refund_unsuccessful_bidder | emd_refund_unsuccessful_bidder | 2 |
| gem_definition | gem_definition | 2 |
| inspection_and_acceptance | inspection_and_acceptance | 2 |
| password_recovery | password_recovery | 2 |
| payment_and_asset_entry | payment_and_asset_entry | 2 |
| procurement_methods_overview | procurement_methods_overview | 2 |
| procurement_planning | unknown | 2 |
| tender_creation_portal_steps | tender_creation_portal_steps | 2 |
| tender_method_definition | unknown | 2 |
| vendor_registration | unknown | 2 |
| approval_and_budget | approval_and_budget | 1 |
| approval_and_budget | inspection_and_acceptance | 1 |
| bid_deletion_after_corrigendum | corrigendum_policy | 1 |
| bid_evaluation | procurement_planning | 1 |
| bidder_corrigendum_tracking | bidder_corrigendum_tracking | 1 |
| corrigendum_portal_steps | emd_definition | 1 |
| dsc_login_problem | dsc_login_problem | 1 |
| dsc_obtainment | dsc_obtainment | 1 |
| emd_definition | unknown | 1 |
| emd_payment | payment_and_asset_entry | 1 |
| emd_payment_failure | emd_payment_failure | 1 |
| emd_refund_l1_bidder | emd_refund_l1_bidder | 1 |
| emd_refund_unsuccessful_bidder | unknown | 1 |
| emd_remittance_to_department | emd_refund_unsuccessful_bidder | 1 |
| emd_remittance_to_department | emd_remittance_to_department | 1 |
| emd_remittance_to_department | procurement_planning | 1 |
| gem_definition | unknown | 1 |
| gem_department_purchase_process | gem_department_purchase_process | 1 |
| gem_direct_purchase_rule | gem_department_purchase_process | 1 |
| gem_eproc_comparison | gem_definition | 1 |
| gem_eproc_comparison | gem_eproc_comparison | 1 |
| gem_eproc_comparison | unknown | 1 |
| gem_l1_purchase | gem_department_purchase_process | 1 |
| gem_reverse_auction | gem_reverse_auction | 1 |
| mixed_role_clarification | tender_creation_policy | 1 |
| mixed_role_clarification | tender_creation_portal_steps | 1 |
| mixed_role_clarification | unknown | 1 |
| procurement_planning | tender_method_definition | 1 |
| purchase_order | bid_evaluation | 1 |
| purchase_order | purchase_order | 1 |
| tender_eligibility | unknown | 1 |
| vendor_registration | vendor_registration | 1 |
| vendor_registration_documents | unknown | 1 |
| vendor_registration_documents | vendor_registration_documents | 1 |
| vendor_registration_fee | vendor_registration_fee | 1 |

## Results by bucket

| Bucket | N | Actor | Fine intent | Answer | Pass |
|---|---:|---:|---:|---:|---:|
| ambiguous_mixed_role | 10 | 80.00% | 60.00% | 40.00% | 30.00% |
| department_buyer | 30 | 76.67% | 66.67% | 56.67% | 33.33% |
| department_operator | 25 | 40.00% | 24.00% | 48.00% | 4.00% |
| general_information | 25 | 100.00% | 64.00% | 40.00% | 32.00% |
| vendor_bidder | 30 | 53.33% | 56.67% | 73.33% | 20.00% |

## Results by language

| Language | N | Actor | Fine intent | Answer language | Answer |
|---|---:|---:|---:|---:|---:|
| en | 45 | 80.00% | 64.44% | 97.78% | 68.89% |
| hi | 30 | 43.33% | 30.00% | 100.00% | 50.00% |
| hinglish | 45 | 73.33% | 60.00% | 93.33% | 42.22% |

## Prioritized remaining defects

### 1. fallback — 58 queries

- Examples: Q3: We need printers for the government office; what should we do first?; Q9: Can our department purchase a printer directly from GeM?; Q11: What budget and administrative approvals are needed before a department purchase?
- Root cause evidence: the corresponding per-query boolean is false/true in `results.json`; inspect each row's detected actor/intent, retrieved families, final families and answer.
- Likely files: 05_webui/fine_intent_policy.py; 05_webui/actor_boundary.py
- Recommended minimal fix: Determine whether the fallback is caused by missing evidence or a rejected grounded draft before changing fallback text.
- Regression risk: Medium-high: fallback logic is already verified.

### 2. actor classification — 38 queries

- Examples: Q3: We need printers for the government office; what should we do first?; Q16: Bid evaluation ke baad purchase order issue karne ka process batao.; Q18: Supplier ko payment aur asset register entry ka workflow kya hai?
- Root cause evidence: the corresponding per-query boolean is false/true in `results.json`; inspect each row's detected actor/intent, retrieved families, final families and answer.
- Likely files: 05_webui/actor_policy.py; 05_webui/nlp_features.py
- Recommended minimal fix: Add only the failing phrase to the narrow actor signal/rule and add its regression case.
- Regression risk: High: actor changes affect retrieval and generation.

### 3. generation — 35 queries

- Examples: Q9: Can our department purchase a printer directly from GeM?; Q11: What budget and administrative approvals are needed before a department purchase?; Q13: Department ke liye printer ki specifications kaise banayein?
- Root cause evidence: the corresponding per-query boolean is false/true in `results.json`; inspect each row's detected actor/intent, retrieved families, final families and answer.
- Likely files: 05_webui/app.py; 05_webui/fine_intent_policy.py
- Recommended minimal fix: Tighten the intent-specific evidence/answer contract; do not add an unrelated synthetic workflow.
- Regression risk: Medium: stronger guards can increase fallback use.

### 4. citation — 30 queries

- Examples: Q3: We need printers for the government office; what should we do first?; Q40: How can I submit my technical and price bid online?; Q41: Am I eligible to participate in this government tender?
- Root cause evidence: the corresponding per-query boolean is false/true in `results.json`; inspect each row's detected actor/intent, retrieved families, final families and answer.
- Likely files: 05_webui/app.py; 05_webui/static/script.js
- Recommended minimal fix: Keep final source IDs aligned with selected context and rendered source links.
- Regression risk: Low if source normalization is isolated.

### 5. procedural completeness — 28 queries

- Examples: Q3: We need printers for the government office; what should we do first?; Q11: What budget and administrative approvals are needed before a department purchase?; Q13: Department ke liye printer ki specifications kaise banayein?
- Root cause evidence: the corresponding per-query boolean is false/true in `results.json`; inspect each row's detected actor/intent, retrieved families, final families and answer.
- Likely files: 05_webui/fine_intent_policy.py; 05_webui/app.py
- Recommended minimal fix: Require the missing in-scope stages only for this procedural intent.
- Regression risk: Low-medium if limited to one intent.

### 6. fine-intent classification — 27 queries

- Examples: Q8: Which purchase method should our department choose during an emergency?; Q9: Can our department purchase a printer directly from GeM?; Q12: How should the department evaluate technical and financial bids?
- Root cause evidence: the corresponding per-query boolean is false/true in `results.json`; inspect each row's detected actor/intent, retrieved families, final families and answer.
- Likely files: 05_webui/fine_intent_policy.py; 05_webui/nlp_features.py
- Recommended minimal fix: Add or refine only the missing fine-intent route and its evidence contract.
- Regression risk: Medium-high: overlapping keywords can reroute adjacent intents.

### 7. context selection — 7 queries

- Examples: Q40: How can I submit my technical and price bid online?; Q66: How should the bid opener open the technical bid online?; Q67: How does the department operator open the price bid?
- Root cause evidence: the corresponding per-query boolean is false/true in `results.json`; inspect each row's detected actor/intent, retrieved families, final families and answer.
- Likely files: 05_webui/app.py
- Recommended minimal fix: Preserve the already-retrieved authoritative family during adaptive context selection.
- Regression risk: Medium: token-budget changes can alter latency and citations.

### 8. language — 4 queries

- Examples: Q51: Submitted bid ko deadline se pehle modify aur resubmit kaise karein?; Q78: Offline tendr portal pe upload kaise karna hai?; Q94: What do the Chhattisgarh Store Purchase Rules govern?
- Root cause evidence: the corresponding per-query boolean is false/true in `results.json`; inspect each row's detected actor/intent, retrieved families, final families and answer.
- Likely files: 05_webui/app.py; 05_webui/actor_boundary.py
- Recommended minimal fix: Preserve the query language directive and reject only the failing output-language pattern.
- Regression risk: Medium.

### 9. retrieval filtering — 2 queries

- Examples: Q101: EMD kya hai aur kyu li jati hai?; Q117: EMD ka process short me batao.
- Root cause evidence: the corresponding per-query boolean is false/true in `results.json`; inspect each row's detected actor/intent, retrieved families, final families and answer.
- Likely files: 05_webui/app.py; 04_embeddings_and_kg/scripts/embeddings_production.py
- Recommended minimal fix: Inspect expansion, metadata policy, hybrid scores and top-5 family filtering for the failing intent.
- Regression risk: Medium: broad retrieval changes can regress passing intents.

### 10. streaming — 1 queries

- Examples: Q91: What does open tender mean?
- Root cause evidence: the corresponding per-query boolean is false/true in `results.json`; inspect each row's detected actor/intent, retrieved families, final families and answer.
- Likely files: 05_webui/app.py; 05_webui/streaming_utils.py; 05_webui/static/script.js
- Recommended minimal fix: Fix only the event lifecycle proven by the failing trace.
- Regression risk: High: streaming is already verified and shared by all answers.

## Slowest 10 queries

| ID | Seconds | Classification | Query |
|---:|---:|---|---|
| 11 | 22.114 | Fail | What budget and administrative approvals are needed before a department purchase? |
| 95 | 22.027 | Fail | CG me govt procurement ke alag tarike kya hain? |
| 25 | 22.026 | Fail | प्रिंटर की तकनीकी विनिर्देश निष्पक्ष रूप से कैसे तैयार करें? |
| 73 | 21.874 | Fail | Tender term corrigendum kaise jari kare department user? |
| 96 | 21.767 | Fail | GeM kya hota hai? |
| 59 | 21.715 | Fail | शुद्धिपत्र आने पर मेरी जमा बोली का क्या होगा? |
| 19 | 21.705 | Fail | GeM par L1 purchase department kaise kare? |
| 49 | 21.655 | Partial | L1 bidder ki EMD ka kya hota hai? |
| 74 | 21.630 | Fail | Attachment corrigendum upload aur publish kaise hoga? |
| 97 | 21.609 | Fail | GeM aur state e-procurement portal me fark batao. |

## Reproduction

```powershell
python eval\production_120\build_dataset.py
python eval\production_120\run_benchmark.py --endpoint http://127.0.0.1:5000/api/stream --workers 1 --timeout 150
python eval\production_120\generate_report.py
```

No application code was changed after the benchmark run began. The report is diagnostic only; no failure-triggered fixes were applied.
