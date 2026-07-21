"""Ground broad Chhattisgarh procurement-method questions in the state rules.

The Store Purchase Rules PDF has a table of contents whose chapter headings rank
highly for broad questions such as "what are the different ways of government
procurement?". A small model can mistake those headings for an exhaustive list of
procurement methods. This module supplies a concise, hand-verified synthesis of
the relevant provisions so retrieval can still be used without that ambiguity.
"""

from __future__ import annotations

import re


STORE_RULES_SOURCE = "store purchase rule cg"
STORE_RULES_FRIENDLY_NAME = (
    "Chhattisgarh Store Purchase Rules (updated 11 July 2024)"
)


_STATE_TERMS = (
    "chhattisgarh",
    "chattisgarh",
    "chhatisgarh",
    "chhattisgadh",
    "छत्तीसगढ़",
    "छत्तीसगढ़",
)
_PROCUREMENT_TERMS = (
    "procurement",
    "government purchase",
    "govt purchase",
    "store purchase",
    "purchase method",
    "purchase mode",
    "सरकारी खरीद",
    "शासकीय क्रय",
    "भंडार क्रय",
    "भण्डार क्रय",
)
_LIST_TERMS = (
    "different way",
    "ways of",
    "what ways",
    "method",
    "mode",
    "type",
    "kind",
    "how can",
    "किन तरीकों",
    "कौन से तरीके",
    "विधियां",
    "विधियाँ",
    "प्रकार",
)


def is_chhattisgarh_procurement_methods_query(query: str) -> bool:
    """Return True only for broad, state-specific procurement-method queries."""
    q = re.sub(r"\s+", " ", (query or "").strip().lower())
    if not q:
        return False
    has_state = any(term in q for term in _STATE_TERMS)
    has_state = has_state or bool(re.search(r"\bcg\b", q))
    has_procurement = any(term in q for term in _PROCUREMENT_TERMS)
    has_list_intent = any(term in q for term in _LIST_TERMS)
    has_list_intent = has_list_intent or any(
        term in q for term in ("alag tarike", "alag tareeke", "kaunse tarike", "kitne tarike")
    )
    return has_state and has_procurement and has_list_intent


def chhattisgarh_procurement_methods_context(query: str) -> str | None:
    """Return a source-grounded clarification for the matching broad query.

    Monetary thresholds are deliberately omitted. They can change through
    amendments and should be copied from an operative provision when a user asks
    for them explicitly.
    """
    if not is_chhattisgarh_procurement_methods_query(query):
        return None
    return """Chhattisgarh government procurement — classification from the
Chhattisgarh Store Purchase Rules, updated through 11 July 2024:

Do not treat portal names and tender methods as the same category. GeM and the
state e-Procurement system are procurement channels. Single tender, limited
tender and open tender are tender methods.

The routes and methods expressly covered by the rules are:
1. GeM procurement. Where the applicable goods or services are available on GeM,
   procurement follows the GeM process. The rules mention Direct Purchase, L1,
   e-bidding and Reverse Auction as available GeM processes.
2. Tender procurement under Rule 4. Its tender methods are single tender,
   limited tender and open tender.
3. Foreign purchase or import, including a global tender where the prescribed
   conditions and approvals apply.
4. Direct purchase from specified government departments, undertakings or other
   eligible bodies where the rules expressly permit purchase without a separate
   tender.
5. Inter-departmental procurement.
6. Special procurement in natural-disaster or law-and-order emergencies.

For a broad question about "different ways", answer with these routes and show
the tender methods as subtypes of tender procurement. Do not use the document's
table-of-contents headings as an exhaustive three-item list. Do not describe this
source as updated later than 11 July 2024."""


def render_chhattisgarh_procurement_methods_answer(query: str, lang: str) -> str | None:
    """Render the broad answer deterministically after source retrieval.

    This prevents a small local model from flattening channels and tender methods
    into one list, and also avoids its occasional zero-token response on long Hindi
    source chunks. Detailed threshold questions continue through normal RAG.
    """
    if not is_chhattisgarh_procurement_methods_query(query):
        return None

    if lang == "hi":
        return f"""छत्तीसगढ़ में सरकारी खरीद के प्रमुख मार्ग और उनके अंतर्गत विधियाँ इस प्रकार हैं:

| खरीद मार्ग | विधि/उपयोग |
|---|---|
| GeM | Direct Purchase, L1, e-bidding और Reverse Auction |
| Tender के माध्यम से खरीद | Single Tender, Limited Tender और Open Tender |
| विदेश से खरीद/आयात | निर्धारित शर्तों और अनुमोदन के अधीन Global Tender सहित |
| अनुमत प्रत्यक्ष खरीद | नियमों में निर्दिष्ट सरकारी विभागों, उपक्रमों या पात्र संस्थाओं से |
| अंतर-विभागीय खरीद | एक सरकारी विभाग/उपक्रम से दूसरे द्वारा खरीद |
| विशेष/आपात खरीद | प्राकृतिक आपदा या कानून-व्यवस्था की आपात स्थिति में |

GeM और राज्य e-Procurement portal खरीद के channel हैं; Single, Limited और Open Tender, Tender की विधियाँ हैं।

📘 स्रोत: {STORE_RULES_FRIENDLY_NAME}"""

    if lang == "hinglish":
        return f"""Chhattisgarh mein government procurement ke main routes aur unke methods ye hain:

| Procurement route | Method / use |
|---|---|
| GeM | Direct Purchase, L1, e-bidding aur Reverse Auction |
| Tender procurement | Single Tender, Limited Tender aur Open Tender |
| Foreign purchase/import | Prescribed conditions aur approvals ke under Global Tender bhi |
| Permitted direct purchase | Rules mein specified departments, undertakings ya eligible bodies se |
| Inter-departmental procurement | Ek government department/undertaking se doosre ke liye purchase |
| Special/emergency procurement | Natural disaster ya law-and-order emergency mein |

GeM aur state e-Procurement portal channels hain; Single, Limited aur Open Tender, Tender methods hain.

📘 Source: {STORE_RULES_FRIENDLY_NAME}"""

    return f"""Chhattisgarh government procurement can use the following routes and methods:

| Procurement route | Methods / use |
|---|---|
| GeM | Direct Purchase, L1, e-bidding and Reverse Auction |
| Tender procurement | Single Tender, Limited Tender and Open Tender |
| Foreign purchase/import | May include a Global Tender, subject to prescribed conditions and approvals |
| Permitted direct purchase | From specified government departments, undertakings or eligible bodies |
| Inter-departmental procurement | Purchase by one government department/undertaking from another |
| Special/emergency procurement | For natural-disaster or law-and-order emergencies |

GeM and the state e-Procurement portal are procurement channels; Single, Limited and Open Tender are tender methods.

📘 Source: {STORE_RULES_FRIENDLY_NAME}"""
