# e-Procurement Assistant — implementation and validation report

**Date:** 31 July 2026  
**CMITF branch:** `sarvam-only-reports-2026-07-25`  
**Latest implementation commit:** `b73923b` — *Improve semantic follow-ups and reproducible rule indexing*

## Outcome

The chatbot now has a reproducible Chhattisgarh Store Purchase Rules rebuild path, stronger multi-turn follow-up handling, context-aware follow-up suggestions, and verified source/rule grounding. The web-service ports, host bindings, proxy path, and Rocky Linux process configuration were not changed.

## Improvements delivered

### 1. CG Store Purchase Rules corpus and indexing

- The Store Rules OCR promotion script now has a `--verified-index-only` mode.
- Rocky Linux does not need local temporary OCR-staging files to create the audited English retrieval corpus.
- A safe deployment helper was added:

  ```bash
  python scripts/maintenance/deploy_store_rules_index.py
  ```

- It rebuilds only the Store Rules corpus and only that source's Qdrant vectors.
- It does **not** start/stop the application or change any port, host, proxy, or service setting.
- The maintenance health-check root path was corrected so it resolves the repository paths correctly when run from `scripts/maintenance`.

### 2. Semantic retrieval and detailed questions

The application already uses dense + sparse hybrid retrieval, procurement synonym/abbreviation expansion, exact rule-number lookup, and multi-part question decomposition. These were retained.

The Store Rules deterministic answer layer remains active for exact statutory subjects such as tender thresholds, PAC, timelines, EMD, security deposit, PRC/CRAC, repeat orders, and inspection/payment. This prevents a transient generation-provider issue from changing an exact rule answer.

### 3. Multi-turn follow-up context

Follow-up resolution now uses the prior question as well as the remembered topic. For example:

| Turn | User question | Retrieval meaning |
| --- | --- | --- |
| 1 | “Open Tender ke niyam kya hain?” | Open Tender rules and thresholds |
| 2 | “Aur agar 3 lakh se kam ho to?” | Threshold follow-up to the Open Tender question, not a generic search for “3 lakh” |

This applies to pronouns and short contextual forms such as `it`, `this`, `what about`, `below`, `under`, `above`, `se kam`, `se zyada`, and `agar`.

### 4. Follow-up questions in the UI

Rule/tender answers now return relevant clickable next questions:

- What changes if the estimated value is below ₹3 lakh?
- Does GeM have to be checked before inviting a tender?
- What approval, publication, and timeline apply?

These suggestions are emitted after deterministic Store Rules answers as well as normal retrieved answers.

### 5. Grounding safeguards

The existing server-side safeguards were confirmed during the review:

- A rule/section number is removed or neutralised if it does not appear in retrieved evidence.
- Low-confidence answers are not added to the semantic answer cache.
- Exact rule text is attached for applicable rule-based answers.
- The UI receives the real source filename, supports source opening, and can open the highlighted PDF context.

## Test results

### Full CG Store Purchase Rules benchmark

| Metric | Result |
| --- | ---: |
| Questions | 50 |
| Pass | 50 |
| Partial | 0 |
| Fail | 0 |
| Rule correctness | 100% |
| Final source citation | 100% |
| Fallback rate | 0% |
| Average rule coverage | 100% |
| Median response time | 0.022 seconds |
| 95th-percentile response time | 13.151 seconds |

The benchmark includes English and Hinglish questions across scope, GeM, CSIDC, tender methods, PAC, Open/Limited/Single Tender, publicity, timelines, bid opening, EMD, security deposit, purchase committee, repeat order, inspection, and payment.

The full 50 individual prompts, answers, sources, and scoring evidence are in [full_response_report.md](full_response_report.md). Machine-readable output is in `results.json` and the metric summary is in `summary.json`.

### Multi-turn semantic regression tests

All 5 tests passed:

1. Keeps the prior Open Tender question for a “below ₹3 lakh” follow-up.
2. Resolves “what about it?” using the prior EMD-refund question.
3. Leaves a self-contained new question unchanged.
4. Confirms conversation memory retains the prior question.
5. Confirms rule questions receive actionable follow-up suggestions.

### Live API conversation check

The live `POST /api/stream` test used one session with these two turns:

1. `CG store purchase mein open tender ke liye niyam kya kya hai?`
2. `aur agar tender 3 lakh se kam ho toh?`

Both answers cited `store purchase rule cg.pdf`. The second answer correctly returned:

- ₹50,001–₹3,00,000: Limited Tender, minimum three invitations.
- Up to ₹50,000: only permitted Single Tender exceptions.
- GeM route must be checked first where applicable.

Both turns also emitted the three contextual follow-up suggestions above.

## Deployment on Rocky Linux

After pulling the CMITF branch:

```bash
cd /path/to/eProcurement-Project
python scripts/maintenance/deploy_store_rules_index.py
```

Optional safety preview:

```bash
python scripts/maintenance/deploy_store_rules_index.py --dry-run
```

Then verify the data state:

```bash
python scripts/maintenance/health_check.py
```

No port or server-command change is required. Restart the application only through the existing Rocky Linux service procedure if its running process needs to load the updated Python code.

## Files changed in commit `b73923b`

- `05_webui/app.py`
- `05_webui/nlp_features.py`
- `05_webui/test_conversation_features.py`
- `scripts/maintenance/promote_store_rules_ocr.py`
- `scripts/maintenance/deploy_store_rules_index.py`
- `scripts/maintenance/health_check.py`

## Files intentionally not committed

The benchmark output, OCR staging, archived local chunks, and TTS smoke-test file remain local generated artifacts. They are not required for the Rocky Linux application after using the deployed rebuild script.
