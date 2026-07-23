# Phase 2 Before/After: Source-Answer Comparison

## Scope

Same seven questions previously rated `Partial` in the source-vs-chatbot audit were re-tested on the live backend after the Phase 2 source-specific response changes. The baseline is the historical live capture in `uat_51_full_response_report.md`. The reference standard is `uat_50_manual_responses_from_documents.md`.

## Result

| Measure | Before | After |
|---|---:|---:|
| Source-answer match | 0 / 7 | 5 / 7 |
| Safe source-bound answer (including evidence-limited portal cases) | 0 / 7 | 7 / 7 |
| Unsupported universal portal UI claims | 1 / 7 | 0 / 7 |
| Generic goods workflow used for software/AMC | 2 / 7 | 0 / 7 |
| Average live latency | 2.61 s* | 1.46 s |

`*` Baseline values are the captured per-question times where available. The main comparison is answer fidelity, not performance, because the earlier capture ran under a different backend state.

## Detailed comparison

### B2 — Software licence procurement

**Source reference:** Define licence type, users, subscription period, support, security, renewal and lock-in controls; then follow approval, GeM/tender, evaluation and licence-record steps.

**Before:** A generic goods lifecycle: need, specification, budget, tender/GeM, PO, delivery, inspection and asset register. It omitted licence term, renewal, support and data-security scope.

**After:** Defines licence model, users, term/subscription, support, renewal, data-security and compatibility first; requires neutral specifications, total cost, approval, permitted route, licence-term evaluation and licence record.

**Assessment:** Match.

### B5 — AC AMC procurement

**Source reference:** Define covered AC assets/sites, service frequency, response time, spares, exclusions, SLA/penalties, period and payment terms; procure and monitor service performance.

**Before:** A goods-delivery workflow, including delivery inspection and stock/asset entry for the AMC itself.

**After:** Starts with service scope, AC assets/sites, response time, spares coverage, exclusions, SLA/penalty terms and payment milestones; then uses contract-value approval, permitted route, service-capability evaluation, service-call records and invoice certification.

**Assessment:** Match.

### C6 — Startup tender participation

**Source reference:** Participation depends on tender conditions. Government-recognised startups may receive applicable experience/turnover relaxation or preference, but compliance is not automatically waived.

**Before:** Said a startup can participate if it meets the tender conditions, but did not explain state-policy benefits or their limits.

**After:** States conditional participation, applicable relaxation/procurement preference, and that technical compliance, EMD, all eligibility conditions and submission requirements are not automatically waived.

**Assessment:** Match.

### C7 — Foreign company participation

**Source reference:** Check tender eligibility first. For foreign-vendor DSC, use the licensed CA application, Indian Embassy certification, payment/document dispatch and DSC/e-token process; tender-specific conditions still control.

**Before:** Only advised checking tender eligibility and portal instructions; omitted the foreign-vendor procedure available in the CHiPS manual.

**After:** Gives the licensed CA, Indian Embassy certification, required documents, payment/document dispatch and DSC/e-token steps, then preserves tender-specific eligibility/currency/registration controls.

**Assessment:** Match.

### E4 — Technical bid opening

**Source reference:** An authorised opening action after scheduled time, with opening record, documents/conditions check and preserved system-generated record. The local material does not prove one universal menu/button sequence.

**Before:** Asserted universal-looking labels such as `Tender module` and `Technical Bid/PQ Bid` as mandatory UI steps.

**After:** Uses authorised account, scheduled time, opening record, document/condition checks and system-generated record; explicitly avoids unsupported universal menu labels.

**Assessment:** Safe source-bound answer. It is deliberately not a fabricated click-by-click guide.

### E5 — Price bid opening

**Source reference:** Price opening occurs only as tender conditions permit; where the process is two-bid, technical responsiveness precedes price evaluation. Preserve the official system record/report.

**Before:** Contained a broadly correct statement, but mixed it with unverified universal workflow wording.

**After:** States authorised post-scheduled-opening workflow, preserves system record, and limits price opening/evaluation to the tender's two-bid conditions without inventing navigation.

**Assessment:** Safe source-bound answer.

### E7 — Extend tender last date

**Source reference:** Use a Date Corrigendum, enter revised bid date/time, obtain approval, publish and verify visibility. Bid deletion depends on corrigendum type and is not a general deadline-extension step.

**Before:** Gave the entire corrigendum flow and emphasised mandatory bid deletion, even though that applies only to certain corrigendum types.

**After:** Gives the Date Corrigendum workflow directly and says bid deletion depends on the type.

**Assessment:** Match.

## Why this is a real improvement

The revised responses now start with the decisive source-backed condition instead of adapting a generic procurement template. They preserve a safe limitation where the corpus does not prove exact portal screens. This is closer to the code-agent reference approach: select the relevant source rule/workflow first, then answer the actual question rather than a neighbouring workflow.

## Validation evidence

- Live backend tested after restart.
- Seven responses returned in **1.05–2.22 seconds**; average **1.46 seconds**.
- Regression suite: `48` tests passed.
