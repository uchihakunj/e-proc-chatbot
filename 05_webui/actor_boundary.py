"""Dependency-free actor-boundary audit and fallback policy.

This module does not retrieve or rerank documents.  It records which document
families and workflow family are permitted for the already-detected actor, and
provides a state-preserving fallback envelope for provider/retrieval failures.
"""

from dataclasses import asdict, dataclass
import re
from typing import Dict, Tuple

from actor_policy import (
    DEPARTMENT_BUYER,
    DEPARTMENT_OPERATOR,
    GENERAL_INFORMATION_USER,
    VENDOR_BIDDER,
    allowed_workflow_families,
)


def detect_response_language(text: str) -> str:
    """Return the production response language: ``hi``, ``hinglish`` or ``en``."""
    raw = text or ""
    low = raw.lower()

    if "हिंग्लिश" in raw:
        return "hinglish"
    if "हिंदी" in raw or "हिन्दी" in raw:
        return "hi"
    if "अंग्रेज़ी" in raw or "अंग्रेजी" in raw:
        return "en"
    request = re.search(
        r"(?:\b(?:in|into|reply in|answer in|respond in|response in|explain in|"
        r"tell me in|write in|give (?:it )?in|batao in|bolo in)\s+"
        r"(hinglish|hindi|english)\b)"
        r"|(?:\b(hinglish|hindi|english)\s+(?:me|mein|m)\b)",
        low,
    )
    if request:
        requested = request.group(1) or request.group(2)
        return {"hindi": "hi", "english": "en"}.get(requested, requested)
    if re.search(r"[\u0900-\u097f]", raw):
        return "hi"

    hinglish = (
        " kya", "kya ", " hai", "hai?", "kaise", "prakriya", " ka ",
        " ki ", " ke ", "batao", "bataye", "chahiye", "karna", "karne",
        "kaun", "kyun", "nahi", "wala", " kab ", " tak ", " hoga",
        " hogi", " aayega", " padega", " mutabik ", " sath ", " hoti",
        " milta", " milti", " gaya", " gayi", " raha", " rahi", " kare",
        " kijiye", " hamare ", " mujhe ", " main ", " hoon", " mein ",
    )
    return "hinglish" if any(marker in low for marker in hinglish) else "en"


_DEVA_CONSONANTS = {
    "\u0915": "k", "\u0916": "kh", "\u0917": "g", "\u0918": "gh", "\u0919": "ng",
    "\u091a": "ch", "\u091b": "chh", "\u091c": "j", "\u091d": "jh", "\u091e": "ny",
    "\u091f": "t", "\u0920": "th", "\u0921": "d", "\u0922": "dh", "\u0923": "n",
    "\u0924": "t", "\u0925": "th", "\u0926": "d", "\u0927": "dh", "\u0928": "n",
    "\u092a": "p", "\u092b": "ph", "\u092c": "b", "\u092d": "bh", "\u092e": "m",
    "\u092f": "y", "\u0930": "r", "\u0932": "l", "\u0935": "v", "\u0936": "sh",
    "\u0937": "sh", "\u0938": "s", "\u0939": "h", "\u0933": "l",
}
_DEVA_NUKTA_CONSONANTS = {
    "\u0915": "q", "\u0916": "kh", "\u0917": "gh", "\u091c": "z",
    "\u0921": "r", "\u0922": "rh", "\u092b": "f", "\u092f": "y",
}
_DEVA_VOWELS = {
    "\u0905": "a", "\u0906": "aa", "\u0907": "i", "\u0908": "ee",
    "\u0909": "u", "\u090a": "oo", "\u090b": "ri", "\u0960": "ri",
    "\u090c": "li", "\u090f": "e", "\u0910": "ai", "\u0913": "o",
    "\u0914": "au", "\u090d": "e", "\u090e": "e", "\u0911": "o", "\u0912": "o",
}
_DEVA_MATRAS = {
    "\u093e": "aa", "\u093f": "i", "\u0940": "ee", "\u0941": "u",
    "\u0942": "oo", "\u0943": "ri", "\u0944": "ri", "\u0947": "e",
    "\u0948": "ai", "\u094b": "o", "\u094c": "au", "\u0945": "e",
    "\u0949": "o", "\u0946": "e", "\u094a": "o",
}


def devanagari_to_roman(text: str) -> str:
    """Transliterate model drift to readable Roman script for Hinglish replies."""
    chars = list(text or "")
    out = []
    index = 0
    while index < len(chars):
        char = chars[index]
        if char in _DEVA_CONSONANTS:
            consonant = _DEVA_CONSONANTS[char]
            next_index = index + 1
            if next_index < len(chars) and chars[next_index] == "\u093c":
                consonant = _DEVA_NUKTA_CONSONANTS.get(char, consonant)
                next_index += 1
            out.append(consonant)
            if next_index < len(chars) and chars[next_index] == "\u094d":
                index = next_index + 1
                continue
            if next_index < len(chars) and chars[next_index] in _DEVA_MATRAS:
                out.append(_DEVA_MATRAS[chars[next_index]])
                index = next_index + 1
                continue
            out.append("a")
            index = next_index
            continue
        if char in _DEVA_VOWELS:
            out.append(_DEVA_VOWELS[char])
        elif char in _DEVA_MATRAS:
            out.append(_DEVA_MATRAS[char])
        elif char in ("\u0902", "\u0901"):
            out.append("n")
        elif char == "\u0903":
            out.append("h")
        elif char == "\u0950":
            out.append("om")
        elif char in ("\u0964", "\u0965"):
            out.append(".")
        elif "\u0966" <= char <= "\u096f":
            out.append(str(ord(char) - ord("\u0966")))
        elif char not in ("\u093c", "\u200c", "\u200d", "\u094d"):
            out.append(char)
        index += 1
    return "".join(out)


_VENDOR_DOCUMENTS = {
    "VENDOR_REGISTRATION": ("vendor_registration_manual",),
    "DSC": ("vendor_registration_manual", "bid_submission_manual"),
    "EMD_PAYMENT": ("emd_payment_manual",),
    "EMD_REFUND": ("emd_refund_notice",),
    "EMD_GENERAL": ("bid_security_guidance",),
    "BID_SUBMISSION": ("bid_submission_manual",),
    "CORRIGENDUM_TRACKING": ("bid_submission_manual", "tender_notices"),
    "AUCTION": ("auction_manual",),
    "TENDER_ELIGIBILITY": ("tender_documents", "bid_submission_manual"),
}

_OPERATOR_DOCUMENTS = {
    "TENDER_CREATION": ("department_tender_creation_manual",),
    "TENDER_PUBLICATION": ("department_tender_publication_manual",),
    "CORRIGENDUM_MANAGEMENT": ("department_corrigendum_manual",),
    "BID_OPENING": ("department_bid_opening_manual",),
    "OPERATOR_EMD_REFUND": ("department_emd_refund_manual",),
    "OFFLINE_TENDER_UPLOAD": ("offline_tender_manual",),
}

_GENERAL_DOCUMENTS = {
    "PROCUREMENT_METHODS": ("chhattisgarh_procurement_rules",),
    "GEM_EPROC_COMPARISON": ("gem_rules", "eprocurement_portal_manuals"),
    "LIMITED_TENDER_DEFINITION": ("procurement_rules",),
    "SINGLE_TENDER_DEFINITION": ("procurement_rules",),
    "EMD_GENERAL": ("procurement_rules", "bid_security_guidance"),
}


def selected_document_families(actor: str, intent: str, commodity: str = "unspecified") -> Tuple[str, ...]:
    """Return actor-safe document families to prefer during retrieval."""
    if actor == DEPARTMENT_BUYER:
        base = ["chhattisgarh_store_purchase_rules", "procurement_manual"]
        if commodity in ("software", "amc_services"):
            base.append("services_or_it_procurement_guidance")
        else:
            base.append("goods_procurement_guidance")
        base.append("gem_rules")
        return tuple(base)
    if actor == VENDOR_BIDDER:
        return _VENDOR_DOCUMENTS.get(intent, ("vendor_portal_manuals",))
    if actor == DEPARTMENT_OPERATOR:
        return _OPERATOR_DOCUMENTS.get(intent, ("department_portal_manuals",))
    return _GENERAL_DOCUMENTS.get(intent, ("procurement_information_sources",))


def department_operator_evidence(intent: str) -> Tuple[Dict[str, object], ...]:
    """Return concise operator-side passages verified in the ingested corpus."""
    manual_source = "publicProManual-1755343081262-715558279"
    common = {
        "audience": DEPARTMENT_OPERATOR,
        "user_role": "tender_owner_or_department_admin",
        "document_type": "guidelines",
        "jurisdiction": "India_supplementary",
        "authority": 8,
    }
    evidence = {
        "TENDER_CREATION": ({
            **common, "source": manual_source, "procurement_stage": "tender_creation",
            "rule_or_section": "Appendix 3: Electronic Procurement",
            "text": (
                "Manual for Procurement of Goods 2024, Appendix 3: while creating and "
                "publishing an online tender, the procuring entity identifies the authorised "
                "bid openers, publishes the NIT and records the tender schedule and conditions."
            ),
        },),
        "TENDER_PUBLICATION": ({
            **common, "source": manual_source, "procurement_stage": "tender_publication",
            "rule_or_section": "Appendix 3: Electronic Procurement",
            "text": (
                "Manual for Procurement of Goods 2024, Appendix 3: the NIT is e-published on "
                "the designated portal and the procuring entity's website; target suppliers "
                "are also informed for limited or single-source tenders as applicable."
            ),
        },),
        "CORRIGENDUM_MANAGEMENT": ({
            **common, "source": manual_source, "procurement_stage": "corrigendum_management",
            "rule_or_section": "Paragraph 5.1.5, Amendment of Tender Documents",
            "text": (
                "Manual for Procurement of Goods 2024, paragraph 5.1.5: before the bid deadline, "
                "the procuring entity may amend the tender documents by issuing a formal "
                "corrigendum. Upload the amendment on the e-publishing portal and the procuring "
                "entity's website. If the requirement changes significantly or bidders need more "
                "time, extend the submission deadline suitably and use fresh publication where required."
            ),
        },),
        "BID_OPENING": ({
            **common, "source": manual_source, "procurement_stage": "bid_opening",
            "rule_or_section": "Appendix 3: Electronic Procurement",
            "text": (
                "Manual for Procurement of Goods 2024, Appendix 3: authorised bid openers open "
                "the techno-commercial and price bids online. The system generates scrutiny "
                "reports and a price comparative statement; the bid openers download and sign "
                "the reports for further processing. Price bids are opened only after technical shortlisting."
            ),
        },),
        "OPERATOR_EMD_REFUND": ({
            **common, "source": "Online_EMD_Refund_Notice", "procurement_stage": "emd_refund",
            "rule_or_section": "Department refund workflow",
            "text": (
                "Online EMD Refund Notice: the tender owner/department admin initiates the EMD "
                "remittance/refund for unsuccessful bidders after the applicable opening and "
                "evaluation stages, sends it to the Department Approver, and the e-Procurement "
                "system sends the approved refund instruction to the bank."
            ),
        },),
    }
    return evidence.get(intent, ())


def final_workflow_family(actor: str, intent: str, query: str = "") -> str:
    """Resolve one primary workflow family while enforcing the actor allow-list."""
    low = (query or "").lower()
    if actor == DEPARTMENT_BUYER:
        if "gem" in low and any(term in low for term in ("direct", "सीधे", "प्रत्यक्ष")):
            family = "gem_procurement"
        elif any(term in low for term in ("open tender", "limited tender", "निविदा")):
            family = "tender_creation"
        elif any(term in low for term in ("emergency", "आपातकाल")):
            family = "approvals"
        else:
            family = "need_assessment"
    elif actor == VENDOR_BIDDER:
        family = {
            "VENDOR_REGISTRATION": "registration", "DSC": "dsc",
            "EMD_PAYMENT": "emd", "EMD_REFUND": "emd",
            "EMD_GENERAL": "emd",
            "BID_SUBMISSION": "bid_submission",
            "CORRIGENDUM_TRACKING": "corrigendum_tracking",
            "AUCTION": "auction_participation",
            "TENDER_ELIGIBILITY": "bid_submission",
        }.get(intent, "bid_submission")
    elif actor == DEPARTMENT_OPERATOR:
        family = {
            "TENDER_CREATION": "tender_creation",
            "TENDER_PUBLICATION": "tender_publication",
            "CORRIGENDUM_MANAGEMENT": "corrigendum_management",
            "BID_OPENING": "bid_opening",
            "OPERATOR_EMD_REFUND": "emd_refund_or_remittance",
            "OFFLINE_TENDER_UPLOAD": "portal_administration",
        }.get(intent, "portal_administration")
    else:
        family = {
            "PROCUREMENT_METHODS": "procurement_methods",
            "GEM_EPROC_COMPARISON": "document_explanation",
            "LIMITED_TENDER_DEFINITION": "definitions",
            "SINGLE_TENDER_DEFINITION": "definitions",
            "EMD_GENERAL": "definitions",
        }.get(intent, "document_explanation")
    if family not in allowed_workflow_families(actor):
        raise ValueError(f"workflow {family!r} is prohibited for actor {actor!r}")
    return family


_LEAK_PATTERNS: Dict[str, Tuple[str, ...]] = {
    DEPARTMENT_BUYER: (
        "register as a vendor", "vendor registration complete", "new user registration complete",
        "register your dsc", "bidder dsc setup", "respond to tender/nit",
        "add quotation", "submit your bid", "emd challan payment",
    ),
    VENDOR_BIDDER: (
        "obtain budget sanction", "budget sanction lein", "create purchase indent",
        "purchase indent banaye", "create and publish the tender", "tender create karega",
        "approve the purchase order", "purchase order approval",
    ),
    DEPARTMENT_OPERATOR: (
        "register as a vendor", "vendor registration complete", "buy for personal use",
        "personal purchase", "need assessment for your purchase", "purchase indent banaye",
    ),
    GENERAL_INFORMATION_USER: (
        "you must log in", "aapko login karna hoga", "you must register",
        "aap registration complete karein", "submit your bid now", "purchase indent banaye",
    ),
}


def prohibited_workflow_leaks(actor: str, answer: str) -> Tuple[str, ...]:
    """Return actor-prohibited operational phrases found in an answer."""
    low = (answer or "").lower()
    return tuple(pattern for pattern in _LEAK_PATTERNS.get(actor, ()) if pattern in low)


def language_is_consistent(language: str, answer: str) -> bool:
    """Check script-level consistency without rejecting unchanged technical terms."""
    text = answer or ""
    has_devanagari = bool(re.search(r"[\u0900-\u097f]", text))
    if language == "hi":
        return has_devanagari
    if language == "hinglish":
        return not has_devanagari
    return not has_devanagari


@dataclass(frozen=True)
class FallbackEnvelope:
    original_question: str
    actor: str
    intent: str
    commodity: str
    language: str
    reason: str
    workflow_family: str
    document_families: Tuple[str, ...]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def build_fallback_envelope(original_question: str, actor: str, intent: str,
                            commodity: str, language: str, reason: str) -> FallbackEnvelope:
    """Capture all routing state before any timeout/empty/low-confidence fallback."""
    return FallbackEnvelope(
        original_question=original_question,
        actor=actor,
        intent=intent,
        commodity=commodity,
        language=language,
        reason=reason,
        workflow_family=final_workflow_family(actor, intent, original_question),
        document_families=selected_document_families(actor, intent, commodity),
    )


def render_actor_safe_fallback(envelope: FallbackEnvelope) -> str:
    """Render a non-operational, actor-preserving fallback in the user's language."""
    q = envelope.original_question
    actor = envelope.actor
    if envelope.language == "hi":
        return (
            "💡 उत्तर\n"
            f"आपका मूल प्रश्न “{q}” सुरक्षित रखा गया है। इसे {actor} के अनुरोध के रूप में "
            f"{envelope.intent} विषय पर देखा जा रहा है। पर्याप्त विश्वसनीय सामग्री नहीं मिली या "
            "उत्तर सेवा उपलब्ध नहीं हुई, इसलिए किसी दूसरे उपयोगकर्ता की प्रक्रिया नहीं दी गई है। "
            "कृपया दोबारा प्रयास करें या संबंधित आधिकारिक दस्तावेज़ देखें।"
        )
    if envelope.language == "hinglish":
        return (
            "💡 Answer\n"
            f"Aapka original question “{q}” preserve kiya gaya hai. Is request ko {actor} ke "
            f"roop mein {envelope.intent} ke liye handle kiya ja raha hai. Reliable context ya "
            "generation available nahi hui, isliye kisi doosre actor ka operational workflow "
            "nahi diya gaya. Please dobara try karein ya relevant official document check karein."
        )
    return (
        "💡 Answer\n"
        f"Your original question “{q}” has been preserved and is being handled as a {actor} "
        f"request for {envelope.intent}. Reliable context or generation was unavailable, so no "
        "other actor's operational workflow has been substituted. Please retry or consult the "
        "relevant official document."
    )


def render_fallback_for_envelope(envelope: FallbackEnvelope) -> str:
    """Choose the actor-safe production fallback without losing envelope state."""
    if (envelope.actor == DEPARTMENT_BUYER
            and envelope.intent == "PROCUREMENT_PLANNING_OR_PURCHASE_PROCEDURE"):
        from purchase_workflow import render_department_purchase_answer
        return render_department_purchase_answer(
            envelope.language, commodity=envelope.commodity
        )
    if envelope.actor == VENDOR_BIDDER and envelope.intent == "BID_SUBMISSION":
        from purchase_workflow import render_vendor_bid_submission_answer
        return render_vendor_bid_submission_answer(envelope.language)
    return render_actor_safe_fallback(envelope)
