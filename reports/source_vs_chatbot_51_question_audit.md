# Source vs Chatbot: 51-Question Audit

## Scope and method

This is a read-only comparison of:

- the document-grounded reference answers in `uat_50_manual_responses_from_documents.md`, prepared from the local input PDFs and structured text;
- the historical live chatbot capture in `uat_51_full_response_report.md`; and
- the Phase 1 repairs now live for ten narrow policy/portal questions.

`Aligned` means the chatbot materially answers the question and stays within the document-supported workflow. It does **not** mean the wording is copied from the PDF. `Partial` means the general subject is right but a decisive condition, limitation, or answer-first statement is missing. `Repaired` means the historical response had a gap but the current deterministic answer contract corrects it. `Source limit` means the input corpus does not establish the exact requested portal action, so the correct chatbot behavior is to say that rather than invent buttons.

## Per-question comparison

| ID | Document-grounded answer should focus on | Historical chatbot behavior | Current assessment |
|---|---|---|---|
| A1 | Consolidated need, specifications, estimate, budget and approval before method selection. | Gives the department-buyer lifecycle beginning with need/specification/budget. | Aligned; longer than the question needs. |
| A2 | GeM only if availability, conditions, value/rules and approval permit it. | Says yes conditionally and warns that direct purchase is not automatic. | Aligned. |
| A3 | Choose method from value, GeM availability, rules and delegated powers. | Previously defaulted to Limited Tender wording. | Repaired earlier: decision-first method answer. |
| A4 | Compare public Open Tender with restricted Limited Tender. | Explained Limited Tender only. | Repaired: table now contrasts both methods. |
| A5 | Single Tender is exceptional; give supported grounds, justification and approval. | Said exceptional but did not give usable grounds. | Repaired: policy-conditions answer gives supported examples without inventing thresholds. |
| A6 | Direct purchase vs tender depends on consolidated value, GeM and rules; no splitting. | Initially recommended Limited Tender because multiline input broke phrase matching. | Repaired earlier: whitespace-normalised decision answer. |
| A7 | Yes; inter-department purchase is not prohibited and the rule says original rates. | Returned a broad procurement-method overview. | Repaired: answers yes and states original-rates condition. |
| A8 | Emergency is exceptional; record urgency, justification and competent approval. | Gives exceptional-route controls and rejects an automatic bypass. | Aligned. |
| A9 | Need/indent, budget, administrative/financial sanction, technical and method approval. | Gives the same approvals checklist. | Aligned. |
| A10 | Delivery, inspection/testing, formal acceptance, invoice/payment and stock/asset recording. | Gives inspection and acceptance workflow. | Aligned. |
| A11 | Distinguish procurement channels from tender methods; list state routes. | Gives GeM, tender subtypes, import, direct/inter-departmental and emergency routes. | Aligned. |
| B1 | Buyer workflow for printer: need, specs, budget, approval, channel, method, award and acceptance. | Gives the buyer lifecycle and avoids vendor workflow. | Aligned. |
| B2 | Software-specific scope: users, term, support, security, renewal and lock-in controls. | Uses a generic goods lifecycle. | Partial: missing software/service profile. |
| B3 | Functional, measurable, competition-friendly laptop specifications. | Gives generic/measurable/competition-friendly specification guidance. | Aligned. |
| B4 | Brand-only Dell specification normally inappropriate; exception requires technical justification. | Gives generic specifications and brand restriction safeguards. | Aligned. |
| B5 | AMC service scope, SLA, response time, assets, spares, penalties, term and service monitoring. | Uses goods-delivery/asset-register workflow. | Partial: AMC is a service-profile gap. |
| B6 | Do not artificially split known requirements to bypass approvals/method. | Returned full buyer lifecycle. | Repaired: direct anti-splitting rule. |
| B7 | Urgency is not automatically emergency; use lawful GeM/tender option with approvals. | Clearly distinguishes urgency from emergency and rejects automatic Single Tender. | Aligned. |
| B8 | Eligibility, responsiveness, technical compliance, financial evaluation, ranking and approval. | Gives that sequence. | Aligned. |
| B9 | Lowest price is insufficient without eligibility, responsiveness and technical acceptability. | Says L1 is not automatically selected. | Aligned. |
| B10 | Verify delivery against PO, inspect/test, accept or record defects. | Gives inspection/acceptance process. | Aligned. |
| C1 | Domestic new-supplier registration: PAN, business/contact/bank details, documents, submission. | Gives New Supplier Registration process. | Aligned. |
| C2 | PAN, applicable CRN, identity/contact/bank/business details and DSC. | Gives the core document/details checklist. | Aligned. |
| C3 | Use password recovery and validated recovery route; escalate blocked accounts. | Gives portal password-recovery steps. | Aligned, subject to exact UI availability. |
| C4 | Domestic vendor obtains signing/encryption DSC from licensed CA, then token/drivers and mapping. | Started with foreign-vendor embassy procedure. | Repaired: domestic workflow is now the default. |
| C5 | Map renewed valid DSC to account and verify before submission. | Gives DSC mapping steps. | Aligned. |
| C6 | Participation plus tender-specific startup treatment/relaxations where conditions are met. | States participation but misses state startup preference/relaxation detail. | Partial: state-policy coverage is incomplete. |
| C7 | Foreign vendor must meet tender eligibility and documented DSC/document requirements. | Was overly defensive and did not present the available foreign-vendor procedure. | Partial: foreign-vendor source section needs a dedicated contract. |
| C8 | Technical documents/compliance versus financial rates; price stage follows tender conditions. | Gives a direct technical-versus-financial comparison. | Aligned. |
| C9 | Check NIT eligibility, documents, experience, turnover/capacity, EMD, dates and corrigenda. | Previously included unrelated material. | Repaired: focused eligibility checklist. |
| C10 | No fixed SLA is documented; monitor portal/email and contact CHiPS if delayed. | Returned registration steps instead of answering time. | Repaired: clearly says the manual has no fixed approval time. |
| D1 | Tender-specific EMD amount/deadline and successful payment status. | Preserves user amount/date and gives payment route. | Aligned. |
| D2 | Check transaction status; failed credit by deadline can leave bid unpaid/rejected; preserve proof. | Gives payment-failure handling. | Aligned. |
| D3 | Department initiates refund after relevant stage; approver verifies; registered account receives credit. | Gives the department-side process. | Aligned. |
| D4 | L1 EMD is not the ordinary unsuccessful-bidder flow; PBG/contract conditions matter. | Gives conditional L1 treatment. | Aligned. |
| D5 | Exemption only if tender/rules and proof permit it. | Gives conditional MSE exemption. | Aligned. |
| D6 | Vendor registration/DSC, tender/NIT, eligibility, payment if applicable, technical and price parts, final acknowledgement. | Gives the vendor bid-submission workflow. | Aligned. |
| D7 | Modification/withdrawal only before deadline and subject to tender/portal conditions. | Gives before-deadline modification workflow. | Aligned. |
| D8 | No edit/alter/modify after bid deadline. | Returned the full pre-deadline submission workflow. | Repaired: starts with `No` and prohibits alteration after deadline. |
| D9 | Follow tender bid-part instructions; price bid stage depends on tender design and deadline. | Returned generic bid-submission workflow. | Repaired: does not invent a separate financial-bid action. |
| D10 | Auction login, RFx/auction steps, bid increments and monitoring. | Gives auction participation workflow. | Aligned. |
| E1 | Authorised operator creates/offline uploads tender header, dates, bid parts and attachments. | Gives supported manual/offline tender workflow. | Aligned with a caution: not every portal menu is universally documented. |
| E2 | Verify complete NIT, dates, documents/approval, then publish through authorised workflow. | Gives that process. | Aligned. |
| E3 | Authorised operator uploads Manual/Offline Tender header/details/attachments. | Gives offline tender upload steps. | Aligned. |
| E4 | Open technical bids after scheduled opening with authorised account; preserve record. | Historical answer named generic screens as though universal. | Partial: avoid unsupported universal UI labels. |
| E5 | Price opening only under tender/two-bid conditions, with authorised record. | Gives broad opening/evaluation description. | Partial: portal specifics need stronger evidence. |
| E6 | Authorised department user prepares and publishes the appropriate corrigendum. | Gives corrigendum procedure. | Aligned. |
| E7 | Issue/publish a Date Corrigendum with revised dates and approval; do not overstate bid deletion. | Gives broad corrigendum workflow with bid-deletion warnings. | Partial: date-extension subtype needs tighter synthesis. |
| E8 | Department admin/approver initiates and approves eligible unsuccessful-bidder refund. | Gives department-side EMD refund route. | Aligned. |
| E9 | Bidder checks corrigendum, revised dates/conditions and applicable bid status. | Gives bidder tracking workflow. | Aligned. |
| E10 | Generate/export report through authorised workflow only if documented; otherwise state corpus limit. | Explained bid evaluation rather than report generation. | Repaired: explicitly states the corpus does not verify a universal report-generation menu/button sequence. |

## Why an apparently relevant RAG answer can still be unlike the source answer

1. **Retrieval selects documents, not the exact answer sentence.** A document title or broad chunk can be relevant while the decisive rule is in a neighbouring section. Example: `D8` needed the short post-deadline prohibition, but the system used the broader bid-submission workflow.
2. **Fine intent can be correct but answer mode can be wrong.** `A7` was correctly recognised as procurement information, yet the answer needed a yes/no rule response, not an overview. `C10` needed a timeline/absence-of-SLA response, not registration instructions.
3. **Generic deterministic responders can dominate source wording.** They make answers stable, but before this repair they were often broad lifecycle templates. This was the main cause of `B6`, `D8`, and `D9`.
4. **Some corpus areas are not commodity-specific.** The goods manual does not provide a fully verified AMC/service or software-license workflow. A generic goods answer may sound plausible but omit SLA, renewals, support, security and service-performance controls.
5. **Portal manuals may not prove a universal UI path.** A safe answer must not invent screen names or buttons where the supplied manual only supports policy/workflow. `E10` is the clear example.
6. **The prior UAT scorer measured structure, not exact semantic fit.** Actor, intent, retrieved family and citation can all be correct while the first sentence fails to answer `yes/no`, `when`, `can I`, or `how long`.

## Evidence-backed conclusion

The chatbot was not failing primarily because it could not retrieve relevant PDFs. It was failing because it sometimes transformed a specific source-backed question into a broader adjacent workflow. The Phase 1 answer contracts correct ten proven cases. The remaining high-value response gaps are:

1. software-procurement profile (`B2`);
2. AMC/service-procurement profile (`B5`);
3. foreign-vendor DSC/document contract (`C7`);
4. startup state-policy treatment (`C6`);
5. evidence-limited operator portal flows (`E4`, `E5`, `E7`).

## Primary source set

- Chhattisgarh Store Purchase Rules (`store purchase rule cg.pdf`)
- Manual for Procurement of Goods 2024 (`publicProManual-1755343081262-715558279.pdf`)
- GFR (`FInal_GFR_upto_31_07_2024.pdf` and `GFRupdatedupto31012026.pdf`)
- CHiPS Vendor Registration Manual
- CHiPS Bid Submission Manual
- EMD Challan Payment Manual and Online EMD Refund Notice
- CHiPS Corrigendum Issuance Manual
- Manual Offline Tenders and Auction Manual

## Phase 2 live comparison (current backend)

The seven previously partial questions were re-run through the live backend after the source-specific profiles were added.

| ID | Result against document-grounded reference | Live outcome |
|---|---|---|
| B2 | Match | Starts with licence model, users, term, support/SLA, security, renewal, compatibility and lock-in controls; then gives approval/channel/method/contract steps. |
| B5 | Match | Starts with AMC service scope, covered assets, response time, spares, exclusions, SLA/penalties and milestones; then gives procurement and monitoring steps. |
| C6 | Match | States conditional startup participation and tender/rule-specific relaxation or preference without treating exemptions as automatic. |
| C7 | Match | Gives the foreign-vendor DSC path documented in the CHiPS manual: licensed CA application, Indian Embassy certification, payment/document dispatch and DSC/e-token, subject to tender conditions. |
| E4 | Safe source-bound response | Gives authorised post-scheduled-opening workflow and preserves system record; does not invent universal menu labels. |
| E5 | Safe source-bound response | States the two-bid/price-opening condition and authorised record; does not invent universal portal buttons. |
| E7 | Match | Gives Date Corrigendum, revised date/time, approval, publication and visibility verification; does not incorrectly make bid deletion a general consequence. |

Live latency for these seven responses ranged from **1.05 s to 2.22 s**. The relevant regression suite passed **48/48** tests before deployment.
