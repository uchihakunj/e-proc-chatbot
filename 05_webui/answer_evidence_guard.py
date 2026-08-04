"""Final-context applicability checks for answer safety.

Retrieval remains intentionally broad for the source drawer. This module runs
after normal retrieval/reranking/context selection and prevents a selected
passage from answering a materially different question merely because it shares
a generic procurement word.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class EvidenceAssessment:
    usable_results: tuple[dict, ...]
    evidence_present: bool
    reason_code: str = ""
    excluded_sources: tuple[str, ...] = ()


def _payload(result: dict) -> dict:
    point = result.get("point", {}) if isinstance(result, dict) else {}
    return getattr(point, "payload", {}) or {}


def _source(result: dict) -> str:
    return str(_payload(result).get("source", "") or "")


def _text(result: dict) -> str:
    return str(_payload(result).get("text", "") or "")


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").casefold()).strip()


def _query_requires_concept(query: str, *terms: str) -> bool:
    q = _normalise(query)
    return any(term in q for term in terms)


def _payment_release_evidence_present(query: str, corpus: str) -> bool:
    """Payment-release guidance needs a settlement artifact, not an incidental BG mention."""
    q = _normalise(query)
    if "bank guarantee" in q or re.search(r"\bbg\b", q):
        return "bank guarantee" in corpus or re.search(r"\bbg\b", corpus) is not None
    return any(term in corpus for term in (
        "invoice", "bill", "receipt", "acceptance", "delivery", "inspection",
    ))


def _evidence_terms(query: str, fine_intent: str) -> tuple[str, ...]:
    q = _normalise(query)
    if _query_requires_concept(q, "payment", "invoice", "bill", "release payment", "भुगतान"):
        return ("__payment_release_artifact__",)
    if _query_requires_concept(q, "lowest bidder", "l1", "lowest quotation", "lowest price"):
        return ("lowest", "l1", "responsive", "technical", "evaluation", "eligible")
    if _query_requires_concept(q, "budget", "financial sanction", "administrative approval", "approval"):
        return ("budget", "fund", "sanction", "approval", "estimate", "procurement")
    if _query_requires_concept(q, "amc", "maintenance contract", "maintenance"):
        return ("amc", "maintenance", "service", "scope", "contract")
    if fine_intent in ("procurement_planning", "procurement_method_selection"):
        return ("procurement", "purchase", "tender", "gem", "specification", "estimate")
    return ()


def _result_has_required_evidence(query: str, terms: tuple[str, ...], result: dict) -> bool:
    text = _normalise(_text(result))
    if terms == ("__payment_release_artifact__",):
        return _payment_release_evidence_present(query, text)
    return any(term in text for term in terms)


def _is_unrelated_project_material(query: str, result: dict) -> bool:
    q = _normalise(query)
    if "project" in q or "implementation" in q or "2.0" in q or "3.0" in q:
        return False
    source = _normalise(_source(result))
    text = _normalise(_text(result))
    source_marks_project = "précis" in source or "precis" in source or "project" in source
    text_marks_project = sum(term in text for term in ("project 2.0", "project 3.0", "dpr", "implementation")) >= 2
    return source_marks_project or text_marks_project


def assess_final_context(query: str, fine_intent: str,
                         selected_results: Sequence[dict]) -> EvidenceAssessment:
    """Remove obvious non-applicable passages and require question-specific evidence.

    This is deliberately conservative: it never fetches new content, adjusts a
    retrieval score, or reclassifies the user. It only decides whether the exact
    source text already selected can safely support an answer.
    """
    usable, excluded = [], []
    for result in selected_results or ():
        if _is_unrelated_project_material(query, result):
            excluded.append(_source(result))
            continue
        usable.append(result)

    terms = _evidence_terms(query, fine_intent)
    if not usable:
        return EvidenceAssessment((), False, "no_applicable_final_context", tuple(excluded))
    if not terms:
        return EvidenceAssessment(tuple(usable), True, "", tuple(excluded))

    evidence_rows = [
        result for result in usable if _result_has_required_evidence(query, terms, result)
    ]
    if not evidence_rows:
        return EvidenceAssessment(tuple(usable), False, "required_evidence_concept_missing", tuple(excluded))
    excluded.extend(_source(result) for result in usable if result not in evidence_rows)
    return EvidenceAssessment(tuple(evidence_rows), True, "", tuple(excluded))


def render_evidence_gap_answer(language: str, question: str) -> str:
    """Safe response when final context cannot support the exact request."""
    if language == "hi":
        return (
            "💡 उत्तर\nउपलब्ध दस्तावेज़ इस सटीक स्थिति के लिए प्रत्यक्ष मार्गदर्शन नहीं देते। "
            "असंबंधित Tender, portal या project सामग्री को विकल्प के रूप में उपयोग नहीं किया गया है। "
            "कृपया खरीद/सेवा का विषय, लागू प्रक्रिया या Tender/GeM संदर्भ साझा करें।"
        )
    if language == "hinglish":
        return (
            "💡 Answer\nUploaded documents mein is exact scenario ke liye direct guidance nahi milti. "
            "Unrelated Tender, portal ya project material ko substitute ke roop mein use nahi kiya gaya hai. "
            "Please purchase/service ka subject, applicable process, ya Tender/GeM reference share karein."
        )
    return (
        "💡 Answer\nThe uploaded documents do not explicitly provide guidance for this exact scenario. "
        "Unrelated tender, portal, or project material has not been used as a substitute. "
        "Please provide the purchase/service subject, applicable process, or Tender/GeM reference."
    )
