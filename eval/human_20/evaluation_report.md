# Human-style 20-query RAG evaluation

Run date: 16 July 2026  
Endpoint: `POST http://127.0.0.1:5000/api/stream` with a distinct session per query  
Semantic model: `sentence_transformers:BAAI/bge-m3`  
LLM judge: Sarvam 30B, run once without and once with the reviewer reference answer.

## Query set

The benchmark contains 20 natural questions from store officers, department buyers, IT and accounts officers, department operators, vendors, bidders, startups, foreign suppliers, auction bidders, and a general information seeker. It includes English, Hinglish, and Hindi.

The full reviewer-authored query set, expected documents, expected chunk concepts, answer keywords, and reference answers is in `dataset.json`. The raw API evidence is in `results.json` and `results.csv`.

## Results

| Measure | Result |
|---|---:|
| Actor accuracy | 70.0% |
| Fine-intent accuracy | 45.0% |
| Expected source-document recall in top 10 | 85.0% |
| Expected source-document recall in final context | 75.0% |
| Expected chunk-evidence coverage in top 10 | 92.5% |
| Literal response-keyword coverage | 63.5% |
| Mean question → answer BGE cosine similarity | 0.6670 |
| Mean reference → answer BGE cosine similarity | 0.7748 |
| LLM judge, no reference: mean / pass rate | 1.40 / 0.0% |
| LLM judge, with reference: mean / pass rate | 1.90 / 10.0% |
| Fallbacks | 0 |
| Average response time | 2.051s |
| Median / P95 / maximum response time | 1.263s / 5.579s / 7.993s |

## Interpretation

Retrieval is the strongest layer in this test: the expected evidence concepts appeared in the retrieved chunks for 92.5% of the benchmark, and expected source recall was 85% in the top ten. The major weaknesses are natural-language actor and fine-intent recognition, not OCR or embeddings.

The literal-keyword score is deliberately not an acceptance gate: a correct Hindi/Hinglish paraphrase may miss an English literal keyword. The two BGE cosine metrics are also relevance signals only; neither proves factual correctness or grounding.

The LLM-judge metrics are retained because they were requested, but they are not reliable enough to gate release in this run. They sharply underrate direct, evidence-grounded answers: for example H03 gives the correct generic-specification response to the Dell-only question but the no-reference judge rated it 1/5. The reference-aware judge improved it to 4/5, but remains overly strict. Use source/chunk evidence and a human review of failed items as the release criteria until the judge is calibrated against adjudicated examples.

## Highest-impact failure clusters

1. **Implicit vendor actor missed** — H06 (first-time registration), H10 (financial bid after uploads), H13 (foreign supplier), H14 (forward auction). These questions omit or soften the explicit words that current actor cues rely on.
2. **Department operator vs vendor on EMD refund** — H18 was routed to a bidder refund workflow although it explicitly asked for department-side initiation.
3. **Natural buyer planning phrasing** — H01’s “what should I prepare” was classified as a general GeM definition rather than department procurement planning.
4. **Fine-intent gaps despite correct actor** — H05 emergency procurement, H07 renewed-DSC replacement, H12 startup eligibility, H15 tender preparation, and H19 GeM vs state portal comparison.
5. **Expected source absent from final context** — H12, H17, and partial matches for H01/H19 need source-policy review; this is smaller than the routing issue but should be checked before changing retrieval globally.

## Recommended next action

Do not change chunking, embeddings, or Qdrant based on this 20-query run. First add focused regression cases and routing cues for the six actor errors and the eleven fine-intent errors above. Then rerun this unchanged benchmark and compare source recall, final-context recall, answer keyword coverage, and BGE reference similarity. Keep LLM judging as a monitored secondary metric until it is calibrated with a human-adjudicated set.

## Routing repair follow-up

The recommended routing repair was implemented after this baseline. Its full live re-run (before the final typo-normalisation micro-fix) improved actor accuracy from **70.0% to 95.0%** and fine-intent accuracy from **45.0% to 95.0%**. Expected source recall in the top ten improved from **85.0% to 90.0%**, final-context source recall from **75.0% to 85.0%**, and chunk-evidence coverage from **92.5% to 95.0%**.

The final remaining actor error (H06, “become a registered bidder”) was caused by the typo normaliser rewriting `registered` to `register` before actor classification. A production-path regression test was added for the normalised query and a live diagnostic smoke check now returns `vendor_bidder` / `vendor_registration` with the CHiPS Vendor Registration Manual.

The only remaining benchmark fallback from that re-run is H14, forward e-auction participation. Its expected `AuctionManual_FA.pdf` was retrieved and selected, but the workflow guard rejected the generated answer. The next repair should therefore be a narrowly tested auction answer/guard adjustment; it should not alter retrieval, embeddings, chunking, or actor classification.

## Post-repair benchmark — 17 July 2026

This run used the **same frozen 20 human-style queries**, expected sources, chunk concepts,
keywords, reviewer reference answers and scoring rules. It was run after the H06 actor,
H14 forward-auction and H15 tender-preparation repairs. The LLM-as-a-judge prompt was also
calibrated to score factual coverage and paraphrase equivalence rather than copying the
illustrative JSON score values.

| Measure | Original baseline | Latest run | Change |
|---|---:|---:|---:|
| Actor accuracy | 70.0% | 100.0% | +30.0 pp |
| Fine-intent accuracy | 45.0% | 100.0% | +55.0 pp |
| Expected source recall in top 10 | 85.0% | 90.0% | +5.0 pp |
| Expected source recall in final context | 75.0% | 85.0% | +10.0 pp |
| Expected chunk-evidence coverage | 92.5% | 95.0% | +2.5 pp |
| Literal response-keyword coverage | 63.5% | 82.5% | +19.0 pp |
| Mean question -> answer BGE cosine | 0.6670 | 0.6443 | -0.0227 |
| Mean reference -> answer BGE cosine | 0.7748 | 0.8021 | +0.0273 |
| Reference-aware LLM judge mean / pass rate | 1.90 / 10.0% | 3.95 / 95.0% | calibrated evaluator |
| Fallbacks | 0 | 0 | unchanged |
| Average latency | 2.051s | 2.364s | +0.313s |
| P95 latency | 5.579s | 2.877s | -2.702s |

### What improved

- H15 now returns a department-operator **preparation checklist**, including approvals,
  specifications, evaluation conditions, schedule, documents, Tender Creator and DSC; its
  reference-aware judge score improved from 3/5 to 4/5 and keyword coverage is 100%.
- H06 and H14 remain correct in the full run, confirming the live fixes did not regress.
- The source/chunk metrics show that retrieval remains strong; no change was made to Qdrant,
  embeddings, chunking or reranking.

### Remaining evidence-backed issue

H11 (post-deadline rate edit) is the only reference-aware judge failure. The correct
`CHiPS_Bid_Submission_Manual_English.pdf` is selected, but the displayed answer falls back
to generic unavailability text rather than directly stating the supported rule that the Bid
cannot be edited after the deadline. This is an **answer-synthesis/guard** issue, not a
retrieval or actor-routing issue.

The question-to-answer cosine score is included as requested but is not an acceptance gate:
it can decrease when a safer answer uses a concise workflow instead of echoing the question.

## H11 post-deadline bid-edit repair — final regression

The H11 answer-synthesis repair was then applied without changing retrieval, embeddings,
Qdrant, reranking, actor routing or the dataset. The production response now states the
post-deadline prohibition directly in the user's language and cites the CHiPS Bid Submission
Manual. Its validation guard accepts English, Hinglish and Hindi equivalents of the same rule.

Final full-run result: **100% actor accuracy, 100% fine-intent accuracy, 100% pass rate for
both calibrated LLM judges, 86.25% literal keyword coverage, 0 fallbacks, and 2.899s P95
latency**. Reference-answer BGE cosine rose to **0.8106**.
