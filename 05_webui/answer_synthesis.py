"""Answer-presentation policy for the normal LLM generation path.

This module deliberately does not classify actors, choose an intent, retrieve
documents, or select context. It converts the already-decided request shape
into a narrowly scoped instruction for the answer writer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


_COMPARISON_TERMS = (
    "difference", "compare", "comparison", " vs ", " versus ", "antar", "fark",
    "अंतर", "फर्क",
)
_DECISION_TERMS = (
    "should i", "should we", "can i", "can we", "is it allowed", "which method",
    "which route", "gem or tender", "what should i do first", "what should we do first",
    "kya ", "kaunsa", "kaun sa", "kaise decide", "kar sakte", "karna chahiye",
    "milta hai kya",
)
_WORKFLOW_TERMS = (
    "complete process", "full process", "process batao", "procedure", "how should we start",
    "where do we start", "start karna", "kahan se start", "kya process", "workflow",
)
_DEFINITION_TERMS = (
    "what is ", "what are ", "meaning", "matlab", "simple language", "samjhao",
    "define ",
)


@dataclass(frozen=True)
class SynthesisPlan:
    """Presentation-only plan for an answer that already has routing/context."""

    answer_shape: str
    directive: str


def _normalise(question: str) -> str:
    return re.sub(r"\s+", " ", (question or "").casefold()).strip()


def _has_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def determine_answer_shape(question: str, actor: str, intent: str,
                           answer_structure: str = "") -> str:
    """Choose presentation depth without changing routing or answer-mode policy."""
    q = _normalise(question)
    structure = (answer_structure or "").casefold()

    if "comparison" in structure or _has_any(q, _COMPARISON_TERMS):
        return "comparison"
    if _has_any(q, _DECISION_TERMS):
        return "decision"
    if actor == "department_buyer" and _has_any(q, _WORKFLOW_TERMS):
        return "department_workflow"
    if _has_any(q, _DEFINITION_TERMS):
        return "definition"
    return "focused_answer"


def build_answer_synthesis_directive(question: str, actor: str, intent: str,
                                     commodity: str, answer_structure: str = "") -> SynthesisPlan:
    """Return a source-grounded presentation instruction for the LLM.

    The instruction is intentionally about wording and answer order only. The
    existing actor policy, fine-intent policy, retrieval and final-context
    selection remain the authority for what may be said.
    """
    shape = determine_answer_shape(question, actor, intent, answer_structure)
    commodity_note = ""
    if commodity and commodity != "unspecified":
        commodity_note = (
            f"- Commodity is `{commodity}`. Tailor wording to it only when the supplied "
            "Context supports that detail. Do not invent warranties, SLAs, licence terms, "
            "installation, compatibility, inspections, or any other commodity requirement.\n"
        )

    common = (
        "\n\nANSWER-SYNTHESIS POLICY — STRICT:\n"
        "- This is presentation guidance only; do not change the classified actor, intent, "
        "workflow boundary, or the selected evidence.\n"
        "- Use only the supplied Context. Treat an exact rule/clause as stronger evidence than "
        "a general explanatory paragraph. Never replace a Chhattisgarh-specific provision with "
        "a GFR provision.\n"
        "- Combine documents only when each selected document directly supports a compatible "
        "part of the answer. Do not blend conflicting provisions or cite a document that does "
        "not support a stated claim.\n"
        "- Before drafting, silently check that each fact answers this question's actual subject. "
        "Do not turn a generic tender paragraph, an unrelated project paper, or a neighbouring "
        "rule into an answer to this question.\n"
        "- Ignore retrieval artefacts such as isolated rule numbers, page headers, duplicate text, "
        "table fragments, and OCR noise unless they directly establish a claim needed for the answer. "
        "Do not reproduce raw OCR or extracted-rule wording when a plain-language paraphrase is possible.\n"
        "- Do not introduce amounts, percentages, deadlines, committees, EMD, security deposits, "
        "or portal steps merely because they appear in Context. Include them only when they are "
        "directly applicable to the user's question and the supporting condition is explicit.\n"
        "- If the Context does not expressly cover the precise scenario, say: “The uploaded "
        "documents do not explicitly state this exact scenario. The closest applicable guidance is …” "
        "Then provide only that grounded guidance; do not guess.\n"
        "- Use a compact format: start with `💡 Answer`; add `📋 Process` or `📋 Decision checklist` "
        "only where steps help; add `⚠ Important points` only for source-supported exceptions. "
        "End with the required source line. Avoid boilerplate and repeated content.\n"
        "- Write like an experienced government procurement officer: clear, neutral, practical and "
        "conversational. Prefer natural procurement language over literal translations or copied rule text.\n"
        "- Add one short explanatory sentence only when the Context supports the explanation or practical "
        "consequence. Do not invent a policy rationale simply to make an answer sound richer.\n"
        + commodity_note
    )

    shape_rules = {
        "comparison": (
            "- This is a comparison. Start with a compact Markdown comparison table whose cells "
            "are all filled. Then give a short conclusion that answers the user's practical "
            "choice and, where supported, one important distinction. Do not begin with a generic procurement lifecycle.\n"
        ),
        "decision": (
            "- This is a decision/permission question. The first paragraph must answer the "
            "decision directly before any steps. State only the source-supported factors that "
            "control the choice, then give a short decision checklist. Do not invent a threshold.\n"
        ),
        "department_workflow": (
            "- This is a department-buyer process question. Start at the true first step: need "
            "identification and requirement definition. Then include specifications, estimate, "
            "budget/approvals, route selection, evaluation, award, inspection and payment only "
            "to the extent each stage is supported by Context.\n"
        ),
        "definition": (
            "- This is a definition/overview question. Explain the term in plain language first, "
            "then give only its practical implication or when it is used. Keep it to one concise paragraph "
            "unless the Context requires an exception. Do not add a Process section or an unrelated operational workflow.\n"
            "- Do not append quotation-opening details, prescribed forms, supplier-registration steps, "
            "or other tender-document mechanics to a simple definition unless the user explicitly asks for them.\n"
        ),
        "focused_answer": (
            "- This is a focused question. Answer that operation or policy directly and do not "
            "add a full procurement lifecycle unless the user explicitly asks for it. Use one concise paragraph; "
            "add steps only when the selected evidence establishes an actual procedure.\n"
        ),
    }
    intent_rules = _intent_specific_synthesis_rules(question, intent)
    return SynthesisPlan(shape, common + shape_rules[shape] + intent_rules)


def _intent_specific_synthesis_rules(question: str, intent: str) -> str:
    """Prevent common synthesis overreach for existing fine intents.

    These are answer-writing constraints, not alternate intent classification or
    retrieval contracts. They deliberately contain no thresholds or workflow
    rules of their own.
    """
    rules = {
        "procurement_method_selection": (
            "- Do not declare Tender, GeM, Direct Purchase, Limited Tender, or Open Tender "
            "mandatory unless the Context establishes its exact condition. Give the route decision "
            "first; a general need to buy an item is not by itself a tender decision.\n"
        ),
        "procurement_planning": (
            "- For a general departmental purchase or service request, begin with requirement, "
            "scope/specification, estimate, budget and approval. Do not add a particular Tender, "
            "EMD, committee, security-deposit, receipt-certificate, or portal workflow unless the "
            "question and Context make it applicable.\n"
        ),
        "purchase_order": (
            "- For a post-Purchase-Order question, keep the answer at delivery, inspection/acceptance, "
            "contract documents and payment processing as supported by Context. Do not restart the "
            "procurement method-selection workflow. For a payment-release question, do not reduce "
            "the answer to Bank Guarantee verification merely because a BG passage is present.\n"
        ),
        "payment_processing": (
            "- For a payment-verification question, do not reduce the answer to Bank Guarantee "
            "verification merely because a BG passage is present. Cover only the payment controls "
            "that the Context directly supports, such as contract/order, delivery or acceptance, "
            "invoice and required records.\n"
        ),
        "bid_evaluation": (
            "- Never state that the highest bidder wins. Price does not by itself establish award: "
            "explain eligibility, responsiveness and technical compliance only where supported by "
            "Context, then apply the published evaluation basis.\n"
        ),
        "payment_and_asset_entry": (
            "- For a payment-release question, first cover the applicable delivery/receipt, inspection or acceptance, "
            "invoice/bill and required approval/record checks supported by Context. Do not answer with Bank Guarantee "
            "verification unless the user specifically asks about a Bank Guarantee or security instrument.\n"
        ),
    }
    return rules.get(intent or "", "")
