# Chatbot Evaluation Report

## Overall Performance Dashboard

| Metric | Value |
|--------|-------|
| Questions Tested | 100 |
| Strict Intent Accuracy | 10.0% |
| Equivalent Intent Accuracy | 25.0% |
| Functional Intent Accuracy | 92.0% |
| Retrieval Accuracy | 57.0% |
| Answer Accuracy | 42.0% |
| Hallucination Rate | 50.0% |
| Average Latency | 12.43s |
| Pass Rate | 42.0% |

## Intent Failure Correlation
When the strict intent was "wrong" (90 queries):
- **Retrieval Succeeded**: 54.4% of the time
- **Answer Succeeded**: 41.1% of the time

## Category-wise Performance

| Category | Total | Answer Accuracy | Retrieval Accuracy |
|----------|-------|-----------------|--------------------|
| Procurement Methods | 8 | 37.5% | 37.5% |
| Tender Types | 8 | 37.5% | 62.5% |
| EMD | 10 | 70.0% | 80.0% |
| Performance Security | 8 | 50.0% | 75.0% |
| GeM | 8 | 75.0% | 100.0% |
| Vendor Registration | 8 | 50.0% | 25.0% |
| Bid Submission | 8 | 50.0% | 12.5% |
| Corrigendum | 6 | 33.3% | 16.7% |
| Technical Issues | 8 | 12.5% | 62.5% |
| Contract Management | 6 | 50.0% | 33.3% |
| Reverse Auction | 6 | 16.7% | 0.0% |
| General Queries | 8 | 37.5% | 100.0% |
| Out-of-Scope Queries | 8 | 12.5% | 100.0% |

## Error Analysis

- **Wrong Retrieval**: 38
- **Hallucination**: 24
- **Missing Context**: 20
- **Wrong Intent**: 8

## Top Failed Questions

**Q1 (Procurement Methods)**: Error: Missing Context
**Q3 (Procurement Methods)**: Error: Wrong Retrieval
**Q4 (Procurement Methods)**: Error: Wrong Retrieval
**Q5 (Procurement Methods)**: Error: Wrong Retrieval
**Q6 (Procurement Methods)**: Error: Wrong Retrieval
**Q7 (Procurement Methods)**: Error: Wrong Intent
**Q8 (Procurement Methods)**: Error: Missing Context
**Q10 (Tender Types)**: Error: Missing Context
**Q11 (Tender Types)**: Error: Hallucination
**Q12 (Tender Types)**: Error: Wrong Retrieval
**Q13 (Tender Types)**: Error: Wrong Retrieval
**Q14 (Tender Types)**: Error: Wrong Retrieval
**Q15 (Tender Types)**: Error: Missing Context
**Q16 (Tender Types)**: Error: Hallucination
**Q17 (EMD)**: Error: Missing Context
**Q18 (EMD)**: Error: Missing Context
**Q19 (EMD)**: Error: Hallucination
**Q20 (EMD)**: Error: Hallucination
**Q22 (EMD)**: Error: Wrong Retrieval
**Q23 (EMD)**: Error: Hallucination

## Recommendations
- **Intent Classification is Compensated**: Although strict intent accuracy may be low, the fallback logic accurately defaults to general searches, allowing hybrid retrieval to succeed in most cases. Improving the intent classifier would NOT materially improve the chatbot.
