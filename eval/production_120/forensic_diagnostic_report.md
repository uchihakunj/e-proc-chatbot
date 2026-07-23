# Forensic diagnostic report — frozen 120-query production benchmark

Date of audit: 15 July 2026  
Scope: the historical benchmark represented by `results.json`, `aggregate_metrics.json`, and `scratch/benchmark_server2.out.log`.  
Code changes made by this audit: none.

## Executive conclusion

Retrieval was stronger than answer delivery, but the benchmark does **not** prove that most failures began after retrieval. Using the earliest proven broken layer as the single primary cause, 65 of the 92 non-pass cases (70.65%) first broke in actor or fine-intent classification. Post-retrieval delivery failures are nevertheless substantial: 15 LLM failures, 5 deterministic-responder failures, and 5 false fallback activations.

The fallback rate is the clearest post-retrieval defect. Of 58 fallback answers:

- 33 had an expected evidence family in final context.
- 18 had the expected actor, expected fine intent, and expected evidence in final context, so a safe answer was demonstrably possible.
- 45 reached approximately the configured 20-second Sarvam generation deadline.
- 22 generic fallbacks were scored as factually correct because the scorer matched concepts repeated in the original question or intent name. Therefore the reported 54.17% answer accuracy is optimistic; removing those 22 false positives gives a conservative useful-answer ceiling of 43/120, or 35.83%, before manual review of the remaining answers.

## Evidence limitations

The benchmark runner did not retain all requested forensic fields. This is an evidence limitation, not a finding that those stages did nothing.

| Requested field | Available evidence |
|---|---|
| User query, language, actor/confidence, fine intent/confidence | Recorded exactly in `results.json` |
| Query expansion | Server log records **5 variations**, but not the strings |
| Metadata filters | Not recorded; only resulting document families were retained |
| Top 10 before reranking | Not recorded |
| Top reranked results | Ordered context-card sources were retained; chunk IDs, pages, sections, and scores were discarded by `run_benchmark.py` |
| Final selected context | Final source names/families retained; exact selected chunk text and token count were not retained in results |
| Deterministic responder vs LLM | Reconstructed from presence/absence of Sarvam chunks in the server log |
| Raw LLM draft | Not retained |
| Validation result/issues | Not retained |
| Fallback reason code | Not retained; codes marked `~` below are evidence-based inferences |
| Final answer | Recorded exactly in `results.json` |

`CHIPPY_TRACE_RAG` was not enabled during the run. Although the application contains pre/post-rerank tracing, those events are absent from the benchmark log. Therefore an exact pre-rerank chunk/score audit cannot be reconstructed retrospectively.

## Root-cause assignment rule

Each non-pass query receives exactly one primary cause: the earliest layer with direct evidence of failure. Actor failure precedes fine intent; fine intent precedes retrieval; retrieval precedes context; context precedes response selection/generation/validation. Secondary failures remain visible in the row-level fields but are not double-counted.

## Root-cause distribution

| Cause | Count | % of 92 non-pass | % points of all 120 | Query IDs |
|---|---:|---:|---:|---|
| A. Actor Classification Failure | 38 | 41.30% | 31.67% | 3, 16, 18, 26–29, 31, 34, 40, 41, 43, 47, 53–60, 64, 68, 69, 72–79, 81, 82, 84, 85, 113, 119 |
| B. Fine-Intent Classification Failure | 27 | 29.35% | 22.50% | 8, 9, 12, 14, 15, 19, 30, 50, 51, 62, 65–67, 71, 80, 83, 91, 94, 97, 99, 103–106, 109, 116, 120 |
| J. LLM Generation Failure | 15 | 16.30% | 12.50% | 11, 13, 25, 32, 35, 38, 44–46, 49, 70, 87, 95, 96, 112 |
| G. Deterministic Responder Failure | 5 | 5.43% | 4.17% | 17, 63, 90, 100, 108 |
| I. False Fallback Activation | 5 | 5.43% | 4.17% | 20, 21, 36, 110, 118 |
| E. Reranking Failure | 2 | 2.17% | 1.67% | 101, 117 |
| C/D/F/H/K/L/M as primary cause | 0 | 0% | 0% | Earlier failures explain every remaining non-pass row. Context, citation and streaming defects still occur as secondary defects. |

## Top 10 failure clusters

The clusters below partition the largest root-cause/bucket combinations; they do not double-count queries.

| Rank | Cluster | Count | Queries | Primary cause |
|---:|---|---:|---|---|
| 1 | Department-operator actor confusion | 15 | 64, 68, 69, 72–79, 81, 82, 84, 85 | A |
| 2 | Vendor/bidder actor confusion | 14 | 31, 34, 40, 41, 43, 47, 53–60 | A |
| 3 | General-information fine-intent misses | 9 | 91, 94, 97, 99, 103–106, 109 | B |
| 4 | Department-buyer actor confusion | 7 | 3, 16, 18, 26–29 | A |
| 5 | Department-buyer fine-intent overlap | 7 | 8, 9, 12, 14, 15, 19, 30 | B |
| 6 | Department-operator fine-intent `unknown`/wrong branch | 7 | 62, 65–67, 71, 80, 83 | B |
| 7 | Vendor LLM timeout/incomplete generation | 7 | 32, 35, 38, 44–46, 49 | J |
| 8 | General-information deterministic responder incomplete | 3 | 90, 100, 108 | G |
| 9 | Department-buyer LLM failure after correct context | 3 | 11, 13, 25 | J |
| 10 | General-information LLM timeout after correct context | 3 | 87, 95, 96 | J |

Remaining clusters: mixed-role actor failure (113,119); mixed-role fine-intent failure (116,120); vendor bid-submission fine-intent failure (50,51); buyer false fallback (20,21); EMD reranking (101,117); and single-query deterministic/false-fallback clusters.

## Fallback analysis

The exact `fallback_reason` field was not persisted. The following inferred codes use the runtime control flow and timing:

- `~sarvam_timeout`: total latency reached the configured 20-second generation limit.
- `~supporting_section_not_selected`: latency was below the generation deadline and final context lacked the required family.
- `~workflow_guard_rejected`: latency was below the deadline and the required family was present in final context.

| Inferred fallback reason | Count | Query IDs |
|---|---:|---|
| `~sarvam_timeout` | 45 | 3, 11, 19, 25, 27, 32, 34, 35, 38, 41, 44, 45, 49, 50, 53–56, 58–60, 62, 66, 67, 69–71, 73, 74, 79, 80, 83, 85, 87, 95–97, 101, 105, 106, 112, 116, 117, 119, 120 |
| `~workflow_guard_rejected` | 9 | 9, 18, 20, 21, 36, 43, 47, 110, 118 |
| `~supporting_section_not_selected` | 4 | 65, 75, 81, 82 |
| Exact recorded reason | 0 | The runner did not persist it |

Family-level evidence was present in final context for 33 fallback queries: 9, 11, 18–21, 25, 27, 32, 34–36, 38, 43–45, 47, 49, 50, 53–55, 60, 69, 70, 87, 95–97, 110, 112, 118, 119. It was absent for the other 25 fallback queries. On the available evidence, a safe answer was possible for the 33 evidence-present cases; the strongest proof exists for the 18 cases where actor and intent were also correct: 11, 20, 21, 25, 32, 35, 36, 38, 44, 45, 49, 70, 87, 95, 96, 110, 112, 118.

### Per-fallback evidence audit

`Evidence` and `Safe` are family-level determinations from final selected context. `Y` means an expected family survived final selection; it does not prove that the exact supporting sentence was in the unretained selected chunk.

|Q|Inferred reason|Required family/families|Actual final family/families|Actor|Intent|Evidence|Safe|
|---:|---|---|---|---|---|:---:|:---:|
|3|~timeout|state rules, procurement manual|other|general information|unknown|N|N|
|9|~guard|state rules, current rules|state rules, current rules|department buyer|GeM department process|Y|Y|
|11|~timeout|procurement manual, state rules|state rules, procurement manual|department buyer|approval/budget|Y|Y|
|18|~guard|procurement manual, state rules|state rules, procurement manual, other|general information|payment/asset entry|Y|Y|
|19|~timeout|current rules, state rules|state rules, current rules|department buyer|GeM department process|Y|Y|
|20|~guard|state rules, current rules|state rules, current rules, other|department buyer|GeM department process|Y|Y|
|21|~guard|current rules, procurement manual|current rules, procurement manual, auction manual|department buyer|GeM reverse auction|Y|Y|
|25|~timeout|procurement manual, CVC|procurement manual, CVC|department buyer|specifications|Y|Y|
|27|~timeout|procurement manual, state rules|state rules|general information|purchase order|Y|Y|
|32|~timeout|vendor registration manual|vendor registration manual|vendor bidder|registration documents|Y|Y|
|34|~timeout|vendor registration manual|vendor registration, bid submission|general information|password recovery|Y|Y|
|35|~timeout|vendor registration, bid submission|vendor registration|vendor bidder|DSC obtainment|Y|Y|
|36|~guard|vendor registration, bidder guidelines|vendor registration|vendor bidder|DSC mapping|Y|Y|
|38|~timeout|EMD payment manual|EMD payment manual|vendor bidder|EMD payment failure|Y|Y|
|41|~timeout|bid submission, bidder guidelines|procurement manual|general information|unknown|N|N|
|43|~guard|vendor registration manual|vendor registration manual|general information|unknown|Y|Y|
|44|~timeout|vendor registration manual|vendor registration manual|vendor bidder|password recovery|Y|Y|
|45|~timeout|vendor registration, bidder guidelines|vendor registration|vendor bidder|DSC mapping|Y|Y|
|47|~guard|EMD payment manual|EMD payment manual|general information|EMD payment|Y|Y|
|49|~timeout|procurement manual, EMD refund|procurement manual|vendor bidder|L1 EMD refund|Y|Y|
|50|~timeout|bid submission manual|other, bid submission|vendor bidder|unknown|Y|Y|
|53|~timeout|auction, bid submission|auction manual|general information|unknown|Y|Y|
|54|~timeout|vendor registration manual|vendor registration manual|general information|unknown|Y|Y|
|55|~timeout|vendor registration, bidder guidelines|vendor registration|general information|DSC mapping|Y|Y|
|56|~timeout|EMD payment manual|state rules|general information|payment/asset entry|N|N|
|58|~timeout|bid submission manual|other|general information|unknown|N|N|
|59|~timeout|corrigendum, bid submission|procurement manual|general information|corrigendum policy|N|N|
|60|~timeout|auction, bid submission|auction manual|general information|unknown|Y|Y|
|62|~timeout|department tender manual|corrigendum, other|department operator|unknown|N|N|
|65|~source|corrigendum manual|other|department operator|EMD definition|N|N|
|66|~timeout|department tender, procurement manual|other|department operator|unknown|N|N|
|67|~timeout|department tender, procurement manual|other|department operator|unknown|N|N|
|69|~timeout|department tender manual|department tender manual|general information|unknown|Y|Y|
|70|~timeout|department tender manual|department tender, procurement manual|department operator|tender creation|Y|Y|
|71|~timeout|department tender manual|other|department operator|unknown|N|N|
|73|~timeout|corrigendum manual|current rules, procurement manual, state rules, other|department buyer|corrigendum policy|N|N|
|74|~timeout|corrigendum manual|current rules, procurement manual, other|general information|corrigendum policy|N|N|
|75|~source|corrigendum manual|current rules, procurement manual|general information|corrigendum policy|N|N|
|79|~timeout|department tender manual|other|general information|unknown|N|N|
|80|~timeout|department tender manual|state rules, other|department operator|unknown|N|N|
|81|~source|corrigendum manual|current rules|general information|corrigendum policy|N|N|
|82|~source|corrigendum manual|current rules|general information|corrigendum policy|N|N|
|83|~timeout|department tender, procurement manual|other|department operator|unknown|N|N|
|85|~timeout|department tender manual|other|general information|unknown|N|N|
|87|~timeout|current rules, state rules|state rules|general information|GeM definition|Y|Y|
|95|~timeout|state rules, current rules|state rules, current rules, procurement manual|general information|procurement methods|Y|Y|
|96|~timeout|current rules, state rules|state rules|general information|GeM definition|Y|Y|
|97|~timeout|current rules, procurement manual, state rules|state rules, current rules|general information|GeM definition|Y|Y|
|101|~timeout|current rules, procurement manual|other, state rules|general information|EMD definition|N|N|
|105|~timeout|current rules, state rules|other|general information|unknown|N|N|
|106|~timeout|current rules, procurement manual, state rules|other|general information|unknown|N|N|
|110|~guard|current rules, procurement manual|current rules, procurement manual|general information|corrigendum policy|Y|Y|
|112|~timeout|current rules, procurement manual|other, procurement manual, state rules|general information|EMD definition|Y|Y|
|116|~timeout|procurement manual, bid submission|state rules|general information|tender creation policy|N|N|
|117|~timeout|current rules, procurement manual|state rules, other|general information|EMD definition|N|N|
|118|~guard|current rules, procurement manual|current rules, procurement manual, other|general information|corrigendum policy|Y|Y|
|119|~timeout|state rules, procurement manual|procurement manual, other|general information|unknown|Y|Y|
|120|~timeout|procurement manual, bid submission|other|general information|unknown|N|N|

## Exact files responsible

| Cause/layer | File and relevant code |
|---|---|
| Actor classification | `05_webui/actor_policy.py` actor signals and `classify_procurement_actor`; `05_webui/nlp_features.py` `classify_actor` |
| Coarse/fine intent | `05_webui/nlp_features.py` `classify_intent`; `05_webui/fine_intent_policy.py` `classify_fine_intent` |
| Expansion/hybrid retrieval/reranking | `04_embeddings_and_kg/scripts/rag_pipeline.py` `multi_query_retrieval`, `rerank_results`, and final reranker scoring |
| Adaptive/final context | `05_webui/app.py` `build_generation_context` |
| Deterministic responder selection | `05_webui/app.py` `_deterministic_intents` block; `05_webui/fine_intent_policy.py` `render_fine_intent_fallback` |
| Source-family validation | `05_webui/fine_intent_policy.py` `intent_sources_are_sufficient` and `source_family` |
| LLM deadline/stream | `05_webui/app.py` `_stream_model` |
| Grounding guard/fallback | `05_webui/fine_intent_policy.py` `fine_intent_answer_guard`; `05_webui/app.py` final guard/fallback block |
| Benchmark data loss and fallback false positives | `eval/production_120/run_benchmark.py`: `parse_sse`, `run_one`, `FALLBACK_MARKERS`, source-family reduction, and `concept_score` |

No primary-cause evidence points to OCR, PDF preprocessing, chunk creation, embeddings generation, or Qdrant storage. Those components should not be modified on the basis of this benchmark.

## Estimated gain if each primary cause were fixed

These are isolated upper bounds, not additive guarantees; downstream failures can become visible after an upstream correction.

| Fix target | Non-pass cases exposed | Maximum pass-rate gain | Direct measured answer-accuracy failures in cluster | Plausible measured answer gain |
|---|---:|---:|---:|---:|
| Actor classification | 38 | +31.67 points | 19 | up to +15.83 points |
| Fine-intent classification | 27 | +22.50 points | 18 | up to +15.00 points |
| LLM timeout/incomplete generation | 15 | +12.50 points | 9* | at least +7.50 points; useful-answer gain can be +12.50 |
| Deterministic responder | 5 | +4.17 points | 5 | +4.17 points |
| False fallback | 5 | +4.17 points | 2* | at least +1.67 points; useful-answer gain can be +4.17 |
| Reranking | 2 | +1.67 points | 2 | +1.67 points |

`*` The measured answer scorer falsely marked generic fallback restatements as correct in several cases.

## Recommended fix order and smallest changes

1. **Repair benchmark observability/scoring before using it for another code decision.** Persist expansion strings, filter policy, pre/post-rerank chunk records and scores, selected chunks, raw draft, validation issues, and exact fallback reason. Exclude generic fallback templates from factual scoring before concept matching. Smallest scope: `eval/production_120/run_benchmark.py`; enable existing trace output rather than changing retrieval.
2. **Actor boundary, narrow phrase additions only.** Address the 38 frozen phrases in `actor_policy.py`, keeping confidence behavior stable. Do not touch retrieval.
3. **Fine-intent routes/precedence only.** Address the 27 frozen intent misses in `fine_intent_policy.py`; especially operator publication/opening/corrigendum, vendor bid submission, GeM comparison/L1/direct purchase, and Hindi definitions.
4. **Evidence-backed deterministic coverage for repeated timeout routes.** Add only routes whose required family is present and whose answer contract is unambiguous. This targets the 15 LLM failures and avoids global model/prompt changes.
5. **Fallback/guard correction.** For the 5 quick false fallbacks, inspect the raw rejected draft first; then change only the offending required/forbidden term or source-family alias.
6. **Reranking for EMD definition.** Q101 and Q117 retrieved the procurement manual at rank 7; promote the already-retrieved authoritative family for the exact EMD-definition route. Do not rebuild embeddings.

## Per-query forensic trace

Legend:

- Every request generated 5 query variations, but the expansion strings and metadata filters were not recorded.
- `R10` is the ordered context-card source list retained by the runner, capped here at ten. It is post-rerank; the true pre-rerank top 10 is unavailable. `R5` is therefore the first five entries of `R10`.
- `Final` is the selected source list. Exact selected chunk/page/section/token information was discarded.
- `DET` means no Sarvam chunks appeared; `LLM` means generation was attempted.
- `FB` is the generic fallback answer; `BAD` failed factual/procedural scoring; `OK` passed factual scoring but may still be non-pass for actor, intent, fallback, citation, or streaming.
- Full final answer text and full ordered sources are in `results.json` under the same query ID.
- Source abbreviations: SPR=Chhattisgarh Store Purchase Rules; GFR=current GFR; FGFR=Final GFR; PG24=Goods Manual 2024; PPM=Public Procurement Manual; PWM=Works Manual; VRM=Vendor Registration Manual; BSM=Bid Submission Manual; EMDP=EMD payment; EMDR=EMD refund; COR=Corrigendum manual; OFF=Offline Tender manual; AUC=Auction manual; CVC=CVC guidance; GFRH=Hindi GFR; SPR21=2021 Store Rules; CAP=Capabilities; VIG=Vigilance Manual.

The compact rows use: `Q | query | language | actor(conf) | fine intent(conf) | R10 (R5 is first five) | Final | responder | fallback | answer | root`.

### Department buyer and buyer-like cases

|Q|Query|Lang|Detected actor|Detected fine intent|R10|Final|Responder|Fallback|Answer|Root|
|---:|---|---|---|---|---|---|---|---|---|---|
|3|We need printers for the government office; what should we do first?|en|general_information_user .55|unknown .00|GFRH/FGFR/FGFR/GFR/GFRH/SPR21/SPR/PG24|GFRH/FGFR|LLM|~timeout|FB|A|
|8|Which purchase method should our department choose during an emergency?|en|department_buyer .98|procurement_planning .86|SPR/GFR/PG24/SPR/PPM/SPR/PG24/PG24/GFR/FGFR|SPR/PG24|DET|-|OK|B|
|9|Can our department purchase a printer directly from GeM?|en|department_buyer .98|gem_department_purchase_process .75|SPR/GFR/PG24/SPR/SPR/FGFR/PG24/PWM/PPM/FGFR|SPR/GFR|LLM|~guard|FB|B|
|11|What budget and administrative approvals are needed before a department purchase?|en|department_buyer .98|approval_and_budget .92|SPR/GFR/PG24/Précis/SPR/SPR/PG24/PG24/PWM/FGFR|SPR/PG24|LLM|~timeout|FB|J|
|12|How should the department evaluate technical and financial bids?|en|department_buyer .85|procurement_planning .86|PWM/FGFR/PPM/PPM/PWM/SPR/PG24/PG24/PWM/PWM|SPR/PG24/PWM|DET|-|OK|B|
|13|Department ke liye printer ki specifications kaise banayein?|hinglish|department_buyer .85|specification_preparation .96|PG24/PG24/SPR/SPR/CVC/CVC/FGFR/FGFR/PG24/PG24|PG24/CVC|LLM|-|BAD|J|
|14|Hamare office ko open tender se furniture lena hai, planning kya hogi?|hinglish|department_buyer .85|tender_method_definition .92|SPR/GFR/PG24/FGFR/SPR/SPR/PG24/PG24/FGFR/FGFR|SPR/PG24/GFR|DET|-|BAD|B|
|15|Limited tender kab choose kare department buyer?|hinglish|department_buyer .98|procurement_planning .86|SPR/GFR/PG24/FGFR/SPR/SPR/PG24/PG24/FGFR/FGFR|SPR/PG24|DET|-|OK|B|
|16|Bid evaluation ke baad purchase order issue karne ka process batao.|hinglish|general_information_user .55|bid_evaluation .96|SPR/SPR/PG24/PPM/FGFR/FGFR/SPR21/PPM/SPR/SPR|SPR/PG24|LLM|-|BAD|A|
|17|PO ke baad maal ka inspection aur acceptance kaise karein?|hinglish|department_buyer .86|inspection_and_acceptance .94|PG24/PG24/CVC/CVC/VIG/VIG/VIG/PG24/PG24/PG24|PG24|DET|-|BAD|G|
|18|Supplier ko payment aur asset register entry ka workflow kya hai?|hinglish|general_information_user .55|payment_and_asset_entry .92|SPR/SPR/PG24/PG24/GFRH/GFRH/FGFR/GFR|SPR/PG24/GFRH|LLM|~guard|FB|A|
|19|GeM par L1 purchase department kaise kare?|hinglish|department_buyer .98|gem_department_purchase_process .97|SPR/GFR/PG24/SPR/SPR/PG24/PG24/FGFR/FGFR/SPR21|SPR/GFR|LLM|~timeout|FB|B|
|20|Department ko GeM bidding se computer kharidne hain, kya process hai?|hinglish|department_buyer .98|gem_department_purchase_process .97|SPR/GFR/PG24/CVC/FGFR/SPR/SPR/PG24/PPM/FGFR|SPR/GFR/FGFR|LLM|~guard|FB|I|
|21|GeM reverse auction department kab use kare?|hinglish|department_buyer .85|gem_reverse_auction .96|AUC/SPR/GFR/GFR/PG24/PG24/SPR/SPR21/SPR21|GFR/PG24/AUC|LLM|~guard|FB|I|
|25|प्रिंटर की तकनीकी विनिर्देश निष्पक्ष रूप से कैसे तैयार करें?|hi|department_buyer .86|specification_preparation .96|PG24/PG24/SPR/SPR/CVC/CVC/GFRH/FGFR/PG24/PG24|PG24/CVC|LLM|~timeout|FB|J|
|26|विभागीय खरीद से पहले बजट और प्रशासनिक स्वीकृति कैसे लें?|hi|general_information_user .55|inspection_and_acceptance .93|Précis/PG24/PG24/VIG/VIG/VIG/PG24/PG24/PG24/PG24|PG24|DET|-|BAD|A|
|27|बोली मूल्यांकन के बाद क्रय आदेश जारी करने की प्रक्रिया क्या है?|hi|general_information_user .55|purchase_order .90|SPR/SPR/PG24/FGFR/SPR21/FGFR/PPM/PPM|SPR|LLM|~timeout|FB|A|
|28|आपूर्ति मिलने पर निरीक्षण और स्वीकृति कैसे की जाए?|hi|general_information_user .55|inspection_and_acceptance .93|PG24/PG24/VIG/VIG/VIG/VIG/CVC/CVC/PG24/PG24|PG24|DET|-|OK|A|
|29|भुगतान के बाद स्टॉक और संपत्ति रजिस्टर में प्रविष्टि कैसे करें?|hi|general_information_user .55|payment_and_asset_entry .92|SPR/SPR/PG24/PG24/GFRH/FGFR/GFRH/FGFR|SPR|LLM|-|BAD|A|
|30|आपातकाल में विभाग को तुरंत सामान खरीदना हो तो कौन सी विधि चुनें?|hi|department_buyer .98|procurement_planning .86|SPR/GFR/PG24/SPR/SPR/PG24/PG24/GFR/PPM/FGFR|SPR/PG24|DET|-|OK|B|

### Vendor/bidder cases

|Q|Query|Lang|Detected actor|Detected fine intent|R10|Final|Responder|Fallback|Answer|Root|
|---:|---|---|---|---|---|---|---|---|---|---|
|31|How do I register as a new vendor on the portal?|en|general_information_user .55|unknown .00|VRM/VRM/PWM/PG24/PPM/PWM/BSM/FGFR|VRM|LLM|-|OK|A|
|32|Which documents are required for new supplier registration?|en|vendor_bidder .90|vendor_registration_documents .98|VRM/VRM/OFF/COR/COR/EMDP/EMDP/EMDR/VRM|VRM|LLM|~timeout|FB|J|
|34|I forgot my vendor login password. How can I reset it?|en|general_information_user .55|password_recovery .98|BSM/FAQ/VRM/VRM/BSM/BSM/AUC/OFF/COR/FAQ|VRM/BSM|LLM|~timeout|FB|A|
|35|As a bidder, how do I obtain a DSC?|en|vendor_bidder .98|dsc_obtainment .94|VRM/VRM/BSM/COR/BSM/OFF/COR/EMDP|VRM|LLM|~timeout|FB|J|
|36|How do I map my renewed DSC on the e-procurement portal?|en|vendor_bidder .90|dsc_mapping .98|VRM/VRM/VRM/AUC/COR/EMDP/BSM/COR/BSM|VRM|LLM|~guard|FB|I|
|38|My EMD payment failed but the amount was debited. What next?|en|vendor_bidder .90|emd_payment_failure .98|EMDP/EMDP/COR/COR/FAQ/BSM/OFF/VRM/EMDP/EMDP|EMDP|LLM|~timeout|FB|J|
|40|How can I submit my technical and price bid online?|en|general_information_user .55|unknown .00|PPM/BSM/PWM/PWM/PPM/PG24/FGFR/FGFR|PPM|LLM|-|OK|A|
|41|Am I eligible to participate in this government tender?|en|general_information_user .55|unknown .00|PG24/PPM/FGFR/PPM/FGFR/SPR21/SPR/SPR|PG24|LLM|~timeout|FB|A|
|43|Vendor registrtion ke liye kya dokuments lagenge?|hinglish|general_information_user .55|unknown .00|VRM/VRM/OFF/COR/COR/EMDP/EMDP/EMDR/VRM|VRM|LLM|~guard|FB|A|
|44|Mera vendor password bhool gaya, reset kaise hoga?|hinglish|vendor_bidder .90|password_recovery .98|VRM/VRM/BSM/BSM/AUC/OFF/COR/COR/VRM|VRM|LLM|~timeout|FB|J|
|45|Bidder DSC token ko portal se map kaise kare?|hinglish|vendor_bidder .90|dsc_mapping .96|VRM/VRM/VRM/BSM/BSM/OFF/COR/COR/EMDP/VRM|VRM|LLM|~timeout|FB|J|
|46|Renewed DSC se login nahi ho raha, kya karun?|hinglish|vendor_bidder .90|dsc_login_problem .98|BSM/VRM/VRM/BSM/BSM/OFF/COR/COR/FAQ/VRM|VRM|LLM|-|BAD|J|
|47|EMD 2 lakh jama karni hai 30 July 2026 tak, steps batao.|hinglish|general_information_user .55|emd_payment .96|EMDP/EMDP/BSM/OFF/COR/COR/EMDP/EMDP/EMDP|EMDP|LLM|~guard|FB|A|
|49|L1 bidder ki EMD ka kya hota hai?|hinglish|vendor_bidder .90|emd_refund_l1_bidder .98|PG24/PG24/EMDR/PWM/FGFR/GFRH/GFRH/FGFR/PG24/PG24|PG24|LLM|~timeout|FB|J|
|50|Tender me bid submit kaise karu?|hinglish|vendor_bidder .90|unknown .00|FGFR/BSM/BSM/VRM/OFF/VRM/PWM/PWM|FGFR/BSM|LLM|~timeout|FB|B|
|51|Submitted bid ko deadline se pehle modify aur resubmit kaise karein?|hinglish|vendor_bidder .90|unknown .00|BSM/BSM/FGFR/GFRH/FGFR/PWM/BSM/BSM/OFF/PPM|BSM|LLM|-|BAD|B|
|53|Reverse auction mein vendor kaise participate kare?|hinglish|general_information_user .55|unknown .00|AUC/SPR/PG24/GFRH/FGFR/FGFR/GFRH/PG24/PPM|AUC|LLM|~timeout|FB|A|
|54|मैं नया विक्रेता हूँ। पोर्टल पर पंजीकरण कैसे करूँ?|hi|general_information_user .55|unknown .00|VRM/VRM/PG24/FGFR/GFRH/FAQ/BSM/OFF|VRM|LLM|~timeout|FB|A|
|55|बोलीदाता अपना डिजिटल हस्ताक्षर प्रमाणपत्र कैसे जोड़े?|hi|general_information_user .55|dsc_mapping .96|VRM/VRM/EMDP/OFF/BSM/BSM/COR/COR/VRM|VRM|LLM|~timeout|FB|A|
|56|मुझे ईएमडी जमा करनी है। ऑनलाइन भुगतान प्रक्रिया बताइए।|hi|general_information_user .55|payment_and_asset_entry .92|SPR/SPR/PPM/PG24/PG24/PWM/FGFR/SPR21|SPR|LLM|~timeout|FB|A|
|57|असफल बोलीदाता की ईएमडी वापसी कैसे होती है?|hi|general_information_user .55|unknown .00|PWM/EMDR/GFRH/SPR/PG24/EMDR/EMDP/GFRH|PWM/EMDR|LLM|-|OK|A|
|58|तकनीकी और मूल्य बोली ऑनलाइन कैसे जमा करें?|hi|general_information_user .55|unknown .00|PPM/VIG/PWM/PWM/GFRH/FGFR/GFRH/FGFR|PPM|LLM|~timeout|FB|A|
|59|शुद्धिपत्र आने पर मेरी जमा बोली का क्या होगा?|hi|general_information_user .55|corrigendum_policy .94|PG24/PG24/GFRH/GFRH/FGFR/FGFR/SPR21/PWM|PG24|LLM|~timeout|FB|A|
|60|ई-नीलामी में बोलीदाता कैसे भाग ले?|hi|general_information_user .55|unknown .00|AUC/VIG/VIG/SPR/BSM/GFRH/GFRH/PWM/PG24|AUC|LLM|~timeout|FB|A|

### Department-operator cases

|Q|Query|Lang|Detected actor|Detected fine intent|R10|Final|Responder|Fallback|Answer|Root|
|---:|---|---|---|---|---|---|---|---|---|---|
|62|How does the tender owner publish a completed tender?|en|department_operator .95|unknown .00|COR/PPM/PWM/FGFR/PPM/SPR21/PWM/OFF|COR/PPM/PWM|LLM|~timeout|FB|B|
|63|How does a department issue a corrigendum on the portal?|en|department_operator .95|corrigendum_portal_steps .97|PG24/COR/COR/PG24/VRM/OFF/AUC/EMDP/EMDR/COR|COR|DET|-|BAD|G|
|64|Give the portal steps for issuing a Date Corrigendum.|en|general_information_user .55|corrigendum_portal_steps .97|COR/COR/PG24/VRM/VRM/OFF/AUC/EMDP/COR/COR|COR|DET|-|BAD|A|
|65|How does a tender owner issue an EMD/Bid Security Corrigendum?|en|department_operator .95|emd_definition .90|PWM/PWM/FGFR/PPM/PPM/PG24/VIG/VIG|PWM/FGFR|LLM|~source|FB|B|
|66|How should the bid opener open the technical bid online?|en|department_operator .95|unknown .00|PG24/PPM/PWM/PWM/PPM/PG24/BSM/BSM/OFF|PPM/PWM|LLM|~timeout|FB|B|
|67|How does the department operator open the price bid?|en|department_operator .95|unknown .00|PG24/PWM/PPM/PWM/PPM/OFF/FGFR/BSM/BSM|PWM/PPM|LLM|~timeout|FB|B|
|68|How do department users process bidders' EMD refunds?|en|vendor_bidder .90|emd_refund_unsuccessful_bidder .82|EMDR/EMDR/COR/PG24/PG24/BSM/OFF/BSM/EMDR|EMDR|DET|-|OK|A|
|69|How can an operator upload and publish an offline tender?|en|general_information_user .55|unknown .00|OFF/PPM/OFF/PG24/PWM/SPR/SPR21/SPR21/SPR|OFF|LLM|~timeout|FB|A|
|70|Tender owner portal par naya tender create kaise kare?|hinglish|department_operator .95|tender_creation_portal_steps .97|PG24/OFF/PG24/COR/COR/EMDP/EMDP/VIG/VIG/OFF|OFF/PG24|LLM|~timeout|FB|J|
|71|Department operator tender publish kaise kare?|hinglish|department_operator .95|unknown .00|PG24/GFRH/FGFR/FGFR/SPR/SPR21/BSM/OFF/BSM|GFRH/FGFR|LLM|~timeout|FB|B|
|72|Date corrigendum portal par issue karne ke steps?|hinglish|general_information_user .55|corrigendum_portal_steps .97|COR/COR/PG24/VRM/VRM/OFF/EMDP/EMDR/COR/COR|COR|DET|-|BAD|A|
|73|Tender term corrigendum kaise jari kare department user?|hinglish|department_buyer .85|corrigendum_policy .94|GFR/PG24/PG24/SPR/FGFR/SPR/SPR21/FGFR|GFR/PG24/SPR/FGFR|LLM|~timeout|FB|A|
|74|Attachment corrigendum upload aur publish kaise hoga?|hinglish|general_information_user .55|corrigendum_policy .94|GFR/PG24/FGFR/GFRH/FGFR/GFRH/PPM/PWM|GFR/PG24/FGFR/GFRH|LLM|~timeout|FB|A|
|75|Required attachment corrigendum me bid deletion option kya kare?|hinglish|general_information_user .55|corrigendum_policy .94|GFR/PG24/PG24/FGFR/FGFR/GFRH/GFRH/PPM|GFR/PG24|LLM|~source|FB|A|
|76|Technical bid open karne ka operator workflow batao.|hinglish|general_information_user .55|unknown .00|CAP/FGFR/GFRH/PWM/PPM/PWM/PPM/PG24|CAP/FGFR|LLM|-|OK|A|
|77|Department approver EMD refund process kaise complete kare?|hinglish|vendor_bidder .90|emd_remittance_to_department .98|EMDR/EMDR/BSM/BSM/OFF/VRM/VRM/AUC/EMDR|EMDR|LLM|-|OK|A|
|78|Offline tendr portal pe upload kaise karna hai?|hinglish|general_information_user .55|unknown .00|OFF/GFRH/FGFR/FGFR/SPR/SPR/OFF/BSM/BSM|OFF|LLM|-|OK|A|
|79|विभागीय ऑपरेटर पोर्टल पर निविदा कैसे बनाए?|hi|general_information_user .55|unknown .00|GFRH/SPR/PWM/SPR/SPR21/FGFR/GFRH/SPR21|GFRH|LLM|~timeout|FB|A|
|80|निविदा स्वामी निविदा प्रकाशित कैसे करे?|hi|department_operator .95|unknown .00|PG24/SPR/GFRH/SPR21/PWM/FGFR/SPR/BSM/BSM|SPR/GFRH/SPR21|LLM|~timeout|FB|B|
|81|विभागीय उपयोगकर्ता ईएमडी शुद्धिपत्र कैसे जारी करे?|hi|general_information_user .55|corrigendum_policy .94|GFR/GFR/PG24/PG24/GFRH/FGFR/GFRH/SPR21|GFR|LLM|~source|FB|A|
|82|आइटम शुद्धिपत्र जारी करने की पोर्टल प्रक्रिया बताइए।|hi|general_information_user .55|corrigendum_policy .94|GFR/GFR/PG24/GFRH/FGFR/GFRH/FGFR/SPR21|GFR|LLM|~source|FB|A|
|83|तकनीकी बोली खोलने की ऑनलाइन प्रक्रिया क्या है?|hi|department_operator .95|unknown .00|PG24/PPM/PWM/PWM/PG24/VIG/PPM/COR/COR|PPM|LLM|~timeout|FB|B|
|84|विभाग असफल बोलीदाताओं की ईएमडी वापसी कैसे संसाधित करे?|hi|department_buyer .85|procurement_planning .86|PWM/SPR/SPR/PG24/PG24/FGFR/PWM/FGFR/PWM|SPR/PG24/PWM|DET|-|BAD|A|
|85|ऑफलाइन निविदा को पोर्टल पर अपलोड और प्रकाशित कैसे करें?|hi|general_information_user .55|unknown .00|GFRH/PPM/PWM/GFRH/COR/PG24/FGFR/SPR|GFRH/PPM|LLM|~timeout|FB|A|

### General-information and mixed-role cases

|Q|Query|Lang|Detected actor|Detected fine intent|R10|Final|Responder|Fallback|Answer|Root|
|---:|---|---|---|---|---|---|---|---|---|---|
|87|What is GeM?|en|general_information_user .55|gem_definition .90|FGFR/PWM/PPM/SPR/PPM/PG24/SPR/GFR|SPR|LLM|~timeout|FB|J|
|90|What is a single tender and when is it exceptional?|en|general_information_user .55|tender_method_definition .92|FGFR/PWM/VIG/VIG/SPR/SPR/PG24/PG24/PWM|SPR/PG24/FGFR/PWM|DET|-|BAD|G|
|91|What does open tender mean?|en|general_information_user .55|unknown .00|FGFR/VIG/PWM/PWM/PPM/PG24/PPM/SPR21/SPR|FGFR|LLM|-|BAD|B|
|94|What do the Chhattisgarh Store Purchase Rules govern?|en|general_information_user .55|unknown .00|SPR21/SPR/SPR/SPR21/FGFR/FGFR/GFR/GFRH|SPR21/SPR|LLM|-|BAD|B|
|95|CG me govt procurement ke alag tarike kya hain?|hinglish|general_information_user .55|procurement_methods_overview .97|SPR/SPR/GFR/GFR/PG24/PG24/SPR21/SPR21|SPR/GFR/PG24|LLM|~timeout|FB|J|
|96|GeM kya hota hai?|hinglish|general_information_user .55|gem_definition .75|SPR/SPR/GFR/GFR/FGFR/GFRH/FGFR/GFRH|SPR|LLM|~timeout|FB|J|
|97|GeM aur state e-procurement portal me fark batao.|hinglish|general_information_user .55|gem_definition .75|SPR/SPR/GFR/GFR/PPM/FGFR/PG24/GFRH|SPR/GFR|LLM|~timeout|FB|B|
|99|Single tender kab allowed hota hai?|hinglish|general_information_user .55|unknown .00|FGFR/GFRH/SPR/SPR21/GFRH/SPR21/FGFR/SPR/FGFR|FGFR|LLM|-|BAD|B|
|100|Open tender sab vendors ke liye hota hai kya?|hinglish|general_information_user .55|tender_method_definition .92|FGFR/SPR/SPR/PG24/PG24/SPR21/FGFR/FGFR/SPR21|SPR|DET|-|BAD|G|
|101|EMD kya hai aur kyu li jati hai?|hinglish|general_information_user .55|emd_definition .90|FGFR/FGFR/SPR/GFRH/GFRH/PWM/PG24/PPM|FGFR/SPR/GFRH|LLM|~timeout|FB|E|
|103|Store Purchase Rules CG kis purchase par apply hote hain?|hinglish|general_information_user .55|unknown .00|SPR/SPR/SPR21/SPR21/GFRH/FGFR/FGFR/PG24|SPR/SPR21|LLM|-|BAD|B|
|104|छत्तीसगढ़ में सरकारी खरीद की अलग-अलग विधियाँ क्या हैं?|hi|general_information_user .55|unknown .00|SPR/SPR/SPR|SPR|DET|-|OK|B|
|105|जेम क्या है?|hi|general_information_user .55|unknown .00|PWM/FGFR/PPM/GFRH/PPM/SPR/SPR/GFRH|PWM/FGFR|LLM|~timeout|FB|B|
|106|जेम और छत्तीसगढ़ ई-प्रोक्योरमेंट पोर्टल में क्या अंतर है?|hi|general_information_user .55|unknown .00|PPM/PWM/FGFR/SPR/PPM/SPR/PG24/GFRH|PPM/PWM|LLM|~timeout|FB|B|
|108|एकल निविदा क्या है और इसका उपयोग कब होता है?|hi|general_information_user .55|tender_method_definition .92|FGFR/GFRH/VIG/SPR/SPR/PG24/PG24/PWM/PWM|SPR|DET|-|BAD|G|
|109|ईएमडी या बोली सुरक्षा का अर्थ क्या है?|hi|general_information_user .55|unknown .00|PWM/PG24/FGFR/EMDP/EMDP/COR/GFRH/SPR|PWM/PG24|LLM|-|OK|B|
|110|शुद्धिपत्र का कानूनी उद्देश्य क्या है?|hi|general_information_user .55|corrigendum_policy .94|GFR/PG24/PG24/GFRH/GFRH/FGFR/SPR21/FGFR|GFR/PG24|LLM|~guard|FB|I|
|112|What is the EMD process?|en|general_information_user .55|emd_definition .90|PWM/PG24/SPR/PPM/PPM/PWM/FGFR/FGFR|PWM/PG24/SPR|LLM|~timeout|FB|J|
|113|Should I create a tender or submit a bid?|en|department_operator .95|tender_creation_portal_steps .97|PG24/PG24/OFF/COR/COR/EMDP/VIG/VIG/CVC/PG24|OFF/PG24|LLM|-|OK|A|
|116|Tender banana hai ya bid bharni hai, kya karu?|hinglish|general_information_user .55|tender_creation_policy .92|SPR/SPR/PG24/PG24/SPR21/SPR21/FGFR/FGFR|SPR|LLM|~timeout|FB|B|
|117|EMD ka process short me batao.|hinglish|general_information_user .55|emd_definition .90|SPR/FGFR/FGFR/GFRH/GFRH/PWM/PG24/PPM|SPR/FGFR|LLM|~timeout|FB|E|
|118|Corrigendum kaise hota hai?|hinglish|general_information_user .55|corrigendum_policy .94|GFR/PG24/GFRH/GFRH/FGFR/FGFR/PPM/PPM|GFR/PG24/GFRH|LLM|~guard|FB|I|
|119|मुझे प्रिंटर खरीदने की प्रक्रिया बताइए।|hi|general_information_user .55|unknown .00|PG24/GFRH/SPR/SPR/SPR21/FGFR/SPR21/FGFR|PG24/GFRH|LLM|~timeout|FB|A|
|120|निविदा बनानी है या बोली जमा करनी है?|hi|general_information_user .55|unknown .00|GFRH/GFRH/SPR21/SPR/SPR21/PWM/PWM/PPM|GFRH|LLM|~timeout|FB|B|

## Final forensic finding

The strongest historical defect is not vector retrieval. It is the combination of actor/fine-intent misses and a generation path that frequently reaches the Sarvam deadline or replaces an evidence-backed draft with a generic fallback. Retrieval changes are not justified until a rerun with complete traces proves a remaining retrieval-specific failure.
