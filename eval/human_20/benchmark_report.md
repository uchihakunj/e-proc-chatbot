# Human-style 20-query RAG benchmark

## Aggregate metrics

- total_queries: **20**
- semantic_backend: **disabled**
- actor_accuracy_percent: **100.0**
- fine_intent_accuracy_percent: **100.0**
- expected_source_recall_top10_percent: **77.5**
- expected_source_recall_final_context_percent: **72.5**
- expected_chunk_evidence_coverage_top10_percent: **90.0**
- literal_response_keyword_coverage_percent: **87.25**
- primary_expected_source_match_percent: **70.0**
- known_safety_violation_count: **0**
- question_answer_cosine_mean: **None**
- reference_answer_cosine_mean: **None**
- llm_judge_without_reference_score_mean: **None**
- llm_judge_without_reference_pass_percent: **None**
- llm_judge_with_reference_score_mean: **None**
- llm_judge_with_reference_pass_percent: **None**
- fallback_count: **0**
- release_gate: **{'checks': {'routing_100_percent': True, 'no_request_errors': True, 'no_known_safety_regressions': True, 'primary_source_match_at_least_70_percent': True, 'p95_latency_at_most_6_seconds': True}, 'passed': True}**

## Per-query outcomes

| ID | Persona | Source top-10 | Chunk evidence | Keywords | Q→A cosine | Reference cosine | Time |
|---|---|---:|---:|---:|---:|---:|---:|
| H01 | store officer | 50% | 100% | 100% | n/a | n/a | 1.91s |
| H02 | department buyer | 100% | 50% | 100% | n/a | n/a | 1.72s |
| H03 | IT procurement officer | 100% | 50% | 80% | n/a | n/a | 1.58s |
| H04 | accounts officer | 50% | 100% | 100% | n/a | n/a | 1.81s |
| H05 | emergency store officer | 0% | 50% | 25% | n/a | n/a | 1.64s |
| H06 | first-time vendor | 100% | 100% | 100% | n/a | n/a | 1.62s |
| H07 | existing bidder | 100% | 100% | 100% | n/a | n/a | 1.62s |
| H08 | vendor | 100% | 100% | 80% | n/a | n/a | 1.77s |
| H09 | unsuccessful bidder | 100% | 100% | 100% | n/a | n/a | 2.16s |
| H10 | bidder | 100% | 100% | 100% | n/a | n/a | 1.70s |
| H11 | bidder | 100% | 100% | 100% | n/a | n/a | 1.86s |
| H12 | startup founder | 0% | 100% | 40% | n/a | n/a | 1.83s |
| H13 | foreign supplier | 100% | 100% | 100% | n/a | n/a | 1.62s |
| H14 | auction bidder | 100% | 100% | 100% | n/a | n/a | 1.69s |
| H15 | department operator | 50% | 50% | 100% | n/a | n/a | 1.66s |
| H16 | department operator | 100% | 100% | 80% | n/a | n/a | 1.71s |
| H17 | bid opener | 100% | 100% | 100% | n/a | n/a | 1.69s |
| H18 | department accounts operator | 100% | 100% | 100% | n/a | n/a | 1.66s |
| H19 | new procurement officer | 0% | 100% | 80% | n/a | n/a | 1.66s |
| H20 | citizen information seeker | 100% | 100% | 60% | n/a | n/a | 1.98s |

## Interpretation

Literal keyword and cosine scores are diagnostic only: paraphrases can be correct with low literal overlap, and a question-answer cosine score does not prove factual grounding. The source/chunk measures and the reference-aware judge should be considered together.
