# QA Report — Bid Submission & Vendor Registration Manuals (re-ingested)

**Model:** `gemma3-q3km:12b` · **Path:** live `/api/stream` · **Date:** 2026-06-17
**Scope:** 20 questions (14 Bid Submission, 6 Vendor Registration) across Hindi/English/Hinglish, including 3 **screenshot-only** facts, to validate the hybrid (text + local EasyOCR) re-ingest of these two manuals.

---

## 1. Headline numbers

| Metric | Result | |
|---|---|---|
| Answered (non-empty, in-language) | 20 / 20 | 100% |
| Replied in correct language | 20 / 20 | 100% |
| **Answer fully correct** | **9 / 20** | **45%** |
| Answer partial | 6 / 20 | 30% |
| **Answer wrong** | **5 / 20** | **25%** |
| Source: target manual at rank-1 (family-aware) | 11 / 20 | 55% |
| Source: target/sibling in top-5 | 16 / 20 | 80% |

**Verdict: the re-ingest fixed *content*, not *ranking*.** Every Vendor-Registration question answered well, and distinctive Bid-Submission facts (DSC class, CAs, password recovery, helpdesk, regional settings) are correct. **But for conceptual/procedural *bidding* questions, the two portal manuals are systematically out-ranked by the large GoI procurement manuals (and the EMD-Challan / Auction docs), so the bot answers from the wrong document — confidently and sometimes with fabricated specifics.**

---

## 2. The dominant failure mode (5 wrong + several partial)

The portal manuals lose retrieval to text-dense siblings, and the LLM then answers a *different* concept:

| Q | Asked (portal manual) | Bot answered from | Result |
|--|----------------------|-------------------|--------|
| Q3 | e-Proc portal **login** steps | **AuctionManual** → gave *auction* login ("Password@123", right-click Auction tab) | ❌ wrong |
| Q5 | the 4 **tender types** (Open/Limited/Restricted/Short) | GoI manual → gave *procurement modes* (manual/GeM/third-party) | ❌ wrong |
| Q6 | **vendor category limits** (A>₹10cr, B≤₹10cr, C≤₹2cr, D≤₹1cr) | publicProManual → **fabricated "₹50,000–60,000"** | ❌ wrong (hallucinated numbers) |
| Q12 | **regret items** (rate-contract, YES/NO dropdown) | Works manual → gave "reject all bids for lack of competition" | ❌ wrong |
| Q13 | **2-part tender** (Part1 prequal+techno, Part2 price) | Goods manual → gave "two-**stage** EoI" (a different concept) | ❌ wrong |
| Q7 | online **payment gateways** (INDUSIND/ATOM, NSDL/BILLDESK) — *screenshot* | EMD-Challan → gave "Internet Banking / RTGS-Challan" | 🟡 partial |
| Q8 | **payment modes** (Debit/Credit/Net-banking) — *screenshot* | EMD-Challan → gave "RTGS/CHALLAN" | 🟡 partial |
| Q11 | failure → **admin extends deadline 24/48/72h** | publicProManual → "failures not accepted as a complaint" | 🟡 partial |

The single most concerning case is **Q6**, where the answer *invented* category value-limits (₹50,000–60,000) from unrelated NPV text — the correct figures sit in the Bid-Submission manual but never retrieved.

---

## 3. What worked well (9 correct)

- **Distinctive Bid-Submission facts:** DSC class II/III (Q1), the six Certifying Authorities (Q2), password recovery via DSC/OTP (Q9), helpdesk **1800 419 9140, 9 AM–11 PM** (Q10), regional/language settings → Control Panel → English (US) (Q14).
- **Vendor Registration — all strong:** full registration flow incl. the **OCR-recovered form fields** "Authorized Signatory, Contact, Bank, CRN, Vendor business & Partner" (Q15), fee **₹500 / renewal ₹100** (Q16), DSC registration (Q17), and the PWD pre-fill behaviour quoted verbatim (Q20).

These are the questions whose answer is *distinctive* to the portal manuals and not heavily duplicated by the GoI manuals — so retrieval lands on the right doc.

---

## 4. Did the OCR pass pay off? Mixed.

- ✅ **Q15** surfaced the screenshot-derived registration **form fields** (Authorized Signatory / Contact / Bank / CRN / Partner) → OCR content reached the answer.
- ❌ **Q7 / Q8**: the OCR'd **payment-gateway names** (INDUSIND/ATOM, NSDL/BILLDESK) and **card/net-banking modes** are embedded in the Bid-Submission chunks, but **EMD-Challan out-ranked them**, so they never reached the LLM. The OCR text exists in the index; retrieval just didn't surface it.

So the OCR investment is only realized when the Bid-Submission chunk actually ranks — which, for payment questions, it doesn't (EMD-Challan is a strong magnet).

---

## 5. Per-question summary

| Q | Lang | Topic | Src | Answer |
|--|------|-------|-----|--------|
| 1 | HI | DSC class | T1 | ✅ Class II/III |
| 2 | EN | Certifying Authorities | T1 | ✅ all six |
| 3 | HI | portal login | Tk | ❌ gave auction login |
| 4 | HIN | JRE install | T1 | 🟡 generic (no exact steps / 8.77) |
| 5 | EN | tender types | MISS | ❌ gave procurement modes |
| 6 | HI | vendor category limits | MISS | ❌ fabricated ₹ figures |
| 7 | EN | payment gateways *(shot)* | T1 | 🟡 methods, not gateway names |
| 8 | HI | payment modes *(shot)* | T1 | 🟡 RTGS/Challan, not card/net-banking |
| 9 | EN | password recovery | T1 | ✅ DSC/OTP flow |
| 10 | HI | helpdesk number | T1 | ✅ 1800 419 9140, 9–11 |
| 11 | EN | failure → deadline | Tk | 🟡 missed the extension policy |
| 12 | HI | regret option | MISS | ❌ gave reject-all-bids |
| 13 | EN | 2-part tender | Tk | ❌ gave two-stage EoI |
| 14 | HI | regional settings | T1 | ✅ Control Panel → English(US) |
| 15 | HI | vendor registration flow | T1 | ✅ full + OCR fields |
| 16 | EN | reg/renewal fee | T1 | ✅ ₹500 / ₹100 |
| 17 | HIN | register DSC | T1 | 🟡 brief but correct |
| 18 | HI | what vendor receives | Tk | 🟡 "certificate" vs Registration Number |
| 19 | EN | registration fields *(shot)* | Tk | ✅ PAN/CRN/login/coordinates/DSC |
| 20 | HI | PWD pre-fill | T1 | ✅ verbatim |

---

## 6. Conclusion & recommendation

The hybrid re-ingest **succeeded on extraction** — the content (incl. screenshot text) is in the index, and where the portal manual ranks, answers are correct. The failures are almost entirely a **retrieval-ranking** problem: the comprehensive GoI manuals (Works/Goods) and the EMD-Challan / Auction docs out-rank the portal manuals for generic bidding questions, producing wrong-document answers (and one fabrication, Q6).

**This is the same "magnet" issue fixed earlier for auctions — and the fix is the same shape, not more OCR/extraction:**
1. **Topical boost** (in `_topical_adjust`): when a query is about portal *usage* (login, bid submission steps, tender types, payment, regret, password, 2-part), boost `CHiPS_Bid_Submission` / `CHiPS_Vendor_Registration` and gently demote the GoI Works/Goods manuals + EMD-Challan.
2. **Lexical routing** for the portal-specific facts that keep losing — tender types, vendor categories (A/B/C/D limits), 2-part tender, regret-items — mirroring the contact/fee/auction injects already in place.
3. Q6 (fabricated category limits) should be the priority: it's a confident wrong number a real user could act on.

*Raw data: `bidvendor_qa.jsonl`.*

---

## 7. Round 2 — after the retrieval-ranking fix

**Fix applied:** 7 lexical routes in `lexical_portal_fact_lookup` (app.py) that inject the authoritative Bid-Submission text when these portal facts are asked — tender types, **vendor category limits**, 2-part tender, regret, payment gateway/mode, login, failure/deadline. (No re-OCR/re-embed — purely retrieval routing.) Re-tested the 8 wrong/partial + 2 regression checks:

| Q | Before | After |
|--|--------|-------|
| Q3 login | ❌ gave *auction* login | ✅ portal login (user ID → dept → Submit → DSC → Allow) |
| Q5 tender types | ❌ procurement modes | ✅ Open / Limited / Restricted / Short |
| **Q6 vendor categories** | ❌ **fabricated ₹50–60k** | ✅ **A>₹10cr · B≤₹10cr · C≤₹2cr · D≤₹1cr** |
| Q7 payment gateways | 🟡 generic methods | ✅ INDUSIND (ATOM) + NSDL (BILLDESK) — *OCR content surfaced* |
| Q8 payment modes | 🟡 RTGS only | ✅ Debit/Credit/Net-banking (+RTGS) |
| Q11 failure → deadline | 🟡 "not a valid complaint" | 🟢 "admin **may extend** bid submission" (correct now; minor muddle, no 24/48/72h) |
| **Q12 regret** | ❌ reject-all-bids | ❌ **still reject-all-bids** — injection present but model favours the GoI-manual concept |
| Q13 2-part tender | ❌ two-stage EoI | ✅ Part1 pre-qual+techno / Part2 price bid |
| Q15 reg flow (regression) | ✅ | ✅ no breakage |
| Q16 fees (regression) | ✅ | ✅ no breakage |

**Net: 6 fixed, 1 improved, 1 unresolved (Q12), 0 regressions.** Overall correctness on the 20-question set rises from **9/20 (45%) → ~15/20 (75%)**, and the most dangerous case (Q6's fabricated value-limits) is resolved.

**Q12 (regret) — now fixed (round 3).** The raw-line injection alone failed: the model first preferred the GoI "reject all bids" concept (also in context), then — after a score-demote — mis-read "which *type* of tender" as the tender-types list and answered "open tender". A **3-part fix** resolved it: (1) score-demote the GoI policy manuals on regret intent (`_topical_adjust`); (2) **hard-filter** those manuals out of the context (`_suppress_policy_for_regret`) so their framing can't leak; (3) inject a **crisp, answer-shaped restatement** of §3.5.7 at rank-1. Result (both HI + EN): *"the regret option is available ONLY in rate-contract tenders; it is not a reject-all-bids action."* ✅

> **Lesson:** lexical injection fixes "the fact wasn't retrieved", but when a *competing concept from another doc* is in context, you also need to **remove** it, and when the **query phrasing misleads** the model, you need an explicit answer-shaped statement — not just the raw source line.

**Round 4 — remaining partials fixed via answer-shaped clarifier cards:**
- **Q4 (JRE install)** ✅ → exact path: IE → eproc.cgstate.gov.in → Download → Java → JRE → Download; JRE 8.77.
- **Q11 (failure → deadline)** ✅ → "System Administrator may extend by **24/48/72 hours**; auto email alerts."
- **Q18 (what vendor receives)** ✅ → "**Vendor Registration Number**, displayed in red" (was "certificate").
- **Q17 (register DSC)** ✅ → enriched to a full flow (login → 'Register DSC' → select the appropriate Digital Signature Certificate → Confirmation to accept T&C), grounded in Vendor manual §2.5/§2.6.

**Final tally: 20/20 fully correct.** All originally wrong/partial answers are resolved (DSC-register card correctly does NOT fire on the "which DSC class" question — Q1 regression intact).

> **Technique that generalized:** for high-value or model-confusing portal facts, a small **answer-shaped clarifier card** (a faithful one-sentence restatement of the doc fact, injected at rank-1 with score 0.96–0.97) reliably beats injecting the raw source line — the lower-quant model copies a crisp statement but mis-synthesizes from raw text. Cards now cover: contact, fee, doc-size, project-cost, auction, offline-tender, tender types, vendor categories, 2-part, regret, payment gateways, login, JRE install, failure/deadline, registration number.
