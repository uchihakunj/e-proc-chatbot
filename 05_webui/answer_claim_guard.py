"""Narrow pre-stream checks for recurrent unsafe answer claims."""

from __future__ import annotations

import re


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").casefold()).strip()


def _is_simple_definition_question(question: str) -> bool:
    q = _normalise(question)
    asks_definition = any(term in q for term in (
        "what is", "what are", "meaning", "define", "matlab", "samjhao", "kya hai",
    ))
    asks_rule_detail = any(term in q for term in (
        "timeline", "timelines", "first", "second", "third", "minimum", "kitne",
        "kitna", "how many", "how long", "rule ", "days", "din",
    ))
    return asks_definition and not asks_rule_detail


def requires_buffered_claim_validation(question: str, fine_intent: str) -> bool:
    q = _normalise(question)
    return any((
        "payment release" in q,
        fine_intent == "tender_method_definition" and _is_simple_definition_question(question),
        "lowest bidder" in q or "l1 bidder" in q,
        "budget approve" in q or "budget approved" in q,
        bool(re.search(r"\b(?:office|department|hamare office|our office)\b.*\b(projector|printer|furniture|stationery)\b", q)),
    ))


def answer_claim_violations(question: str, answer: str, fine_intent: str = "") -> tuple[str, ...]:
    q, a = _normalise(question), _normalise(answer)
    issues = []
    if "payment release" in q and "bank guarantee" not in q and " bg " not in f" {q} ":
        has_settlement_document = any(term in a for term in ("invoice", "bill"))
        has_receipt_and_acceptance = (
            any(term in a for term in ("delivery", "receipt", "inspection"))
            and "acceptance" in a
        )
        has_payment_artifact = has_settlement_document or has_receipt_and_acceptance
        if "bank guarantee" in a and not has_payment_artifact:
            issues.append("payment_reduced_to_bg_only")
    if fine_intent == "tender_method_definition" and _is_simple_definition_question(question):
        if any(term in a for term in ("📋 process", "key steps", "⚠ important", "⚠ compliance notes", "quotation opened", "prescribed form")):
            issues.append("definition_expanded_into_unasked_workflow")
    if ("lowest bidder" in q or "l1 bidder" in q) and "highest bidder" in a:
        issues.append("l1_answer_mentions_highest_bidder")
    if "budget approve" in q or "budget approved" in q:
        if any(term in a for term in (
            "vendor registration", "registration aur bid", "gem portal par registration",
            "bid submit", "bid submission", "tender notice upload", "nit upload",
        )):
            issues.append("budget_question_leaked_vendor_workflow")
        if re.search(r"\b(?:rs\.?|₹|â‚¹)\s*\d+\s*(?:lakh|crore)?\b", a):
            issues.append("budget_question_invented_threshold")
    if re.search(r"\b(?:office|department|hamare office|our office)\b.*\b(projector|printer|furniture|stationery)\b", q):
        if not any(term in q for term in ("value", "amount", "₹", "rs.", "rupee", "emd")):
            if any(term in a for term in ("₹", "rs.", "emd", "security deposit", "purchase committee")):
                issues.append("generic_commodity_answer_invented_value_workflow")
    return tuple(issues)
