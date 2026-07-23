# Web UI verification — skipped and remaining scope

## Skipped because already verified

The previously verified production SSE cases were not rerun: procurement methods, department laptop purchase, GeM versus state e-Procurement, post-purchase-order workflow, EMD refund, vendor registration, Limited Tender, bidder Corrigendum tracking, department Corrigendum issuance, cached/uncached consistency, source serving, citation normalization and the 46-test regression suite.

## Newly verified

Query: `I need to pay Rs 50,000 EMD by 15 June 2026. How do I do it?`

- HTTP status: 200 from `POST /api/stream`
- Completion events: exactly 1
- Answer language: English
- User amount preserved: `Rs 50,000`
- User deadline preserved: `15 June 2026`
- Manual screenshot example amounts were explicitly rejected as substitutes
- Final source: `EMD_CHALLAN_PAYMENT_V1.0.pdf`
- Final source was present in retrieved context
- Numbered process: 4 steps
- Backend error events: 0
- Elapsed time reported by backend: 6.21 seconds

## UI automation limitation

The in-app browser runtime failed before navigation with `Cannot redefine property: process`; its recovery attempt then failed with `global.process.on is not a function`. The temporary plugin-line experiment was reverted immediately. Therefore this run does **not** claim fresh visual verification of table rendering, numbered-list CSS, loading-state completion, clickable source links or browser-console errors. Those UI-only checks remain pending in an environment where the browser runtime initializes correctly.

The 120-query benchmark used the exact backend SSE route consumed by the Web UI, but it is not a substitute for DOM and console inspection.
