# Human-style 20-query RAG benchmark

## Aggregate metrics

- total_queries: **20**
- semantic_backend: **sentence_transformers:BAAI/bge-m3**
- actor_accuracy_percent: **100.0**
- fine_intent_accuracy_percent: **100.0**
- expected_source_recall_top10_percent: **90.0**
- expected_source_recall_final_context_percent: **85.0**
- expected_chunk_evidence_coverage_top10_percent: **95.0**
- literal_response_keyword_coverage_percent: **86.25**
- question_answer_cosine_mean: **0.6408**
- reference_answer_cosine_mean: **0.8106**
- llm_judge_without_reference_score_mean: **4.05**
- llm_judge_without_reference_pass_percent: **100.0**
- llm_judge_with_reference_score_mean: **4.0**
- llm_judge_with_reference_pass_percent: **100.0**
- fallback_count: **0**

## Per-query outcomes

| ID | Persona | Source top-10 | Chunk evidence | Keywords | Q→A cosine | Reference cosine | Time |
|---|---|---:|---:|---:|---:|---:|---:|
| H01 | store officer | 100% | 100% | 80% | 0.677 | 0.7611 | 2.84s |
| H02 | department buyer | 100% | 50% | 100% | 0.5803 | 0.8357 | 2.60s |
| H03 | IT procurement officer | 100% | 100% | 100% | 0.4463 | 0.7388 | 2.81s |
| H04 | accounts officer | 100% | 100% | 100% | 0.6149 | 0.8092 | 2.92s |
| H05 | emergency store officer | 100% | 50% | 25% | 0.4383 | 0.7476 | 2.60s |
| H06 | first-time vendor | 100% | 100% | 80% | 0.6035 | 0.7609 | 2.05s |
| H07 | existing bidder | 100% | 100% | 100% | 0.5698 | 0.7571 | 1.98s |
| H08 | vendor | 100% | 100% | 80% | 0.7534 | 0.7838 | 2.80s |
| H09 | unsuccessful bidder | 100% | 100% | 100% | 0.5859 | 0.885 | 2.80s |
| H10 | bidder | 100% | 100% | 60% | 0.6704 | 0.7234 | 2.43s |
| H11 | bidder | 100% | 100% | 100% | 0.7265 | 0.9215 | 2.59s |
| H12 | startup founder | 100% | 100% | 100% | 0.7221 | 0.9541 | 2.55s |
| H13 | foreign supplier | 100% | 100% | 80% | 0.6944 | 0.8612 | 1.27s |
| H14 | auction bidder | 100% | 100% | 100% | 0.7556 | 0.8161 | 2.44s |
| H15 | department operator | 50% | 100% | 100% | 0.6866 | 0.8007 | 2.16s |
| H16 | department operator | 100% | 100% | 80% | 0.5986 | 0.7345 | 2.33s |
| H17 | bid opener | 0% | 100% | 80% | 0.6104 | 0.867 | 2.37s |
| H18 | department accounts operator | 100% | 100% | 100% | 0.7253 | 0.8374 | 1.79s |
| H19 | new procurement officer | 50% | 100% | 100% | 0.722 | 0.8468 | 2.49s |
| H20 | citizen information seeker | 100% | 100% | 60% | 0.6343 | 0.771 | 2.74s |

## Interpretation

Literal keyword and cosine scores are diagnostic only: paraphrases can be correct with low literal overlap, and a question-answer cosine score does not prove factual grounding. The source/chunk measures and the reference-aware judge should be considered together.
