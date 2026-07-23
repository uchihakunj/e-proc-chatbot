# Context packing and citation-selection repair

## Scope

Implemented a post-retrieval context packer. It does **not** modify embeddings,
Qdrant, chunking, hybrid retrieval, or reranking.

## Problem addressed

The former prompt builder accepted chunks strictly in reranker order. Duplicate
or older-policy chunks could consume the bounded prompt before the route's
authoritative source was included. It also built the displayed citations before
Sarvam's later context truncation, so a cited source could be omitted from the
model prompt.

## Repair

- Prefer the fine-intent route's named authoritative document sources among
  chunks that were already retrieved.
- Select one chunk per document before admitting a second chunk from any source.
- Suppress the narrow disposal-only false-grounding case for normal purchase
  questions. A query about surplus, disposal or auction remains unaffected.
- Pack Sarvam context to its real configured input budget before generation.
- Generate the final citation list from exactly the chunks sent to the model.

## Validation

| Check | Result |
|---|---|
| Route-authoritative source is prioritised | Pass |
| Duplicate-source crowd-out is prevented | Pass |
| Disposal rule is excluded for a new-furniture purchase question | Pass |
| Citation list equals documents included in prompt text | Pass |
| Production backend restart and health check | Pass |
| Existing actor/fine-intent regression subset | Pass |

An unrelated existing procurement-overview formatting test still expects an old
emoji heading and fails against the current table-format deterministic answer.
It was not changed by this repair.

## Frozen 50-question UAT re-run

The unchanged Set-3 holdout was rerun against the restarted production backend.
The comparison baseline is the immediately preceding 50-question run made
before this context-packing repair.

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Actor accuracy | 100.0% | 100.0% | 0.0 pp |
| Fine-intent accuracy | 88.0% | 88.0% | 0.0 pp |
| Top-10 source recall | 72.0% | 70.0% | -2.0 pp |
| Final-context source recall | 42.0% | 72.0% | **+30.0 pp** |
| Citation accuracy | 42.0% | 72.0% | **+30.0 pp** |
| Pass / Partial / Fail | 4 / 44 / 2 | 11 / 37 / 2 | +7 Pass |
| Required-concept coverage | 51.67% | 54.67% | +3.00 pp |
| Average latency | 7.20s | 9.61s | +2.41s |
| P95 latency | 11.25s | 20.44s | +9.19s |

The repair achieved its target: the evidence that reaches generation and the
documents cited to the user are materially more often the expected source. The
small Top-10 change is expected noise because retrieval itself was not changed.

Two benchmark questions remained failures:

- H50-12 — inter-departmental procurement / tender requirement.
- H50-22 — delegated financial power and method selection.

The remaining partials are primarily answer-concept coverage rather than actor
or final-context selection failures. One cache-warmed H50-02 response recorded
0.027s; it should not be used when interpreting latency. A separate cold live
check for the same furniture question completed in 5.86s with the expected
decision-first answer and Store Purchase Rules selected first.

The current harness does not persist API generation diagnostics, so its
`fallbacks: 0` field cannot distinguish Sarvam-generated answers from the
grounded deterministic fallback. Live smoke checks observed a Sarvam
first-token timeout followed by that safe fallback. Therefore, fallback count
must be treated as unmeasured in this report.

## Result

This directly addresses the prior final-context/citation-selection cluster.
The production backend is healthy and the context repair is deployed. The next
separate repair should address Sarvam first-token latency and persist fallback
diagnostics in the evaluator before using latency or fallback rate as release
gates.
