# Source-vs-Chatbot Answer Gap Audit

## Bottom line

The chatbot's routing and source selection are often correct, but several answers are **not question-first**. It frequently substitutes a generic workflow for a direct rule, condition, timeframe, or portal action that is present in the PDFs. Therefore, the earlier 100% structural UAT result should not be interpreted as 100% document-faithful answer quality.

## Highest-impact gaps

| Priority | Question | What the chatbot said | What the PDF supports / a better answer | Gap |
|---:|---|---|---|---|
| 1 | `Bid deadline ke baad bid edit kar sakte hain kya?` | Returns the entire bid-submission workflow and never answers the deadline question. | **No.** The GFR source states that bidders should not be permitted to alter or modify bids after the deadline for receipt of bids. Give that answer first; then say to check a corrigendum only if the procuring entity formally changes the tender. | Direct-answer failure; relevant rule exists in corpus. |
| 2 | `Can one government department purchase goods from another government department?` | Gives a general overview of procurement routes. | **Yes, it is not prohibited under the Chhattisgarh Store Purchase Rules; the purchase is at original rates.** State the exception/conditions for the particular listed entities, if relevant. | Direct-answer omission; source was retrieved but not synthesized. |
| 3 | `Can we split a purchase into smaller orders?` | Gives the full department-purchase lifecycle. | **Do not split a requirement to avoid the applicable procurement route or higher approval.** The public procurement manual explicitly identifies artificial splitting as a risk and says requirements must not be split to bring procurement under a method. | Policy-risk question answered as generic workflow. |
| 4 | `Vendor registration approve hone mein kitna time lagta hai?` | Gives steps for domestic supplier registration. | The vendor-registration manual says what happens **after approval** (the vendor is intimated to pay); it does not establish a fixed approval SLA. The correct answer is: *the supplied manual does not specify a fixed time; check the portal/CHiPS support for the current status.* | Wrong intent; invents relevance instead of declaring missing evidence. |
| 5 | `Foreign company tender mein participate kaise kare?` | Says only to check the tender and does not give the available foreign-vendor procedure. | The CHiPS vendor and bid manuals contain a dedicated **procedure to obtain DSC for foreign vendors** and a **foreign-vendor documentation** section. Answer with those documented portal prerequisites, then clearly state that tender-specific eligibility controls participation. | Relevant section is present but omitted; overly defensive fallback. |
| 6 | `Can a startup participate in tenders?` | Correctly says new vendors can take part in Open Tender after registration, but stops there. | The Chhattisgarh rules and procurement manual contain startup-specific treatment: recognised startups may receive procurement preference/relaxation subject to stated conditions, quality/technical compliance and tender provisions. The answer should distinguish **participation**, **portal registration**, and any **tender-specific startup benefit**. | Incomplete state-policy answer; weak source family selection. |
| 7 | `Tender ki last date extend karni hai. Kya process hai?` | Gives the broad corrigendum workflow and bid-deletion warnings. | The answer should start: *issue a Date Corrigendum through the authorised department workflow, enter the revised bid dates, obtain approval, publish it, and verify the new deadline is visible.* Bid deletion should be mentioned only when the selected corrigendum type triggers it, not as a general date-extension step. | Correct document family, but insufficiently scoped synthesis. |
| 8 | `Department admin bid evaluation report kaise generate kare?` | Explains how to evaluate bids, not how an operator generates a portal report. | The returned sources support bid evaluation criteria, not a verified report-generation screen. The safe answer should say that the available corpus supports evaluation steps but does not verify a specific “generate report” portal action; it should not present evaluation as the UI procedure. | Operator-action question collapsed into policy explanation. |
| 9 | `Department ko AC units ka AMC karana hai. Procedure kya hai?` | Uses a goods-procurement lifecycle, including delivery and stock/asset-entry language. | AMC is a service/contract-management request. The answer should first define service scope, SLA/response time, assets covered, uptime/penalties, estimate and approval, then choose GeM/tender as permitted. If the corpus lacks an AMC-specific manual, the assistant should say so instead of presenting goods-delivery steps as AMC rules. | Commodity/service mismatch and possible missing-corpus coverage. |
| 10 | `When is Single Tender allowed?` | Says it is exceptional and needs justification, but does not give the usable grounds. | The supporting procurement rules describe recognised grounds such as a sole known manufacturer/source, emergency procurement from a particular source, or other permitted exceptional circumstances. The answer should list only the grounds supported by the applicable Chhattisgarh rule set and clearly require justification and approval. | Too generic for a policy-condition question. |

## What the chatbot does well

- Department-buyer workflows correctly avoid vendor registration and bid-submission steps.
- Specification guidance is strong: generic, measurable and competition-friendly specifications; avoid brand-only requirements without recorded technical justification.
- EMD L1 handling and post-purchase inspection/acceptance answers are substantially closer to their source documents.
- The corrected procurement-method responses now start with estimated value, GeM availability, rules, delegated powers and approval rather than automatically recommending Limited Tender.

## Root causes

1. **Generic-template override.** A broad deterministic template can replace a specific source-backed answer.
2. **Intent is too broad.** Examples: timeline, post-deadline edit, portal-report generation and AMC are mapped to registration, bid submission, evaluation, or generic purchase planning.
3. **Source section not used.** The PDF can be present and cited while the final answer ignores the exact page/section that resolves the question.
4. **No evidence-aware refusal.** When the PDF does not contain a fixed time or a portal screen procedure, the bot gives adjacent instructions instead of saying the evidence is unavailable.
5. **Structural scoring is insufficient.** Actor, intent, citation and retrieval-family checks can pass even when the response does not answer the user’s actual question.

## Recommended acceptance checks

For every policy/decision question, assert that the first sentence directly answers the yes/no/when/cannot question. For every portal-action question, assert that the answer describes the requested screen/action, or explicitly says that the supplied documents do not verify it. Add document-section checks for the ten questions above.

## Evidence used

- `store purchase rule cg.pdf`: Rule 8 supports inter-departmental purchase at original rates and contains state-specific startup and emergency provisions.
- `FInal_GFR_upto_31_07_2024.pdf`: says bidders should not alter/modify bids after the receipt deadline; gives supplementary single-tender grounds.
- `publicProManual-1755343081262-715558279.pdf`: flags artificial splitting of requirements and provides startup/contract guidance.
- `CHiPS_Vendor_Registration_Manual_English.pdf` and `CHiPS_Bid_Submission_Manual_English.pdf`: contain foreign-vendor DSC/documentation sections and Open Tender/new-vendor registration language.
- `CHiPS_Corrigendum_Issuance_Manual.pdf`: supports the authorised corrigendum workflow and its separate corrigendum types.
