"""Deterministic retrieval metadata derived from an ingested chunk.

Keep this dependency-free: it is used both while indexing new embeddings and
when backfilling an existing Qdrant collection.
"""

from __future__ import annotations

import re
from typing import Dict


def _contains(value: str, *terms: str) -> bool:
    return any(term in value for term in terms)


def derive_retrieval_metadata(source: str, text: str) -> Dict[str, object]:
    """Classify a chunk conservatively for retrieval filtering.

    Values are intentionally broad.  An uncertain chunk remains ``general``;
    it must never be incorrectly marked as a department purchase procedure.
    """
    src = (source or "").casefold()
    body = (text or "").casefold()
    combined = f"{src}\n{body}"

    if _contains(src, "store purchase rule", "store_purhase"):
        family, jurisdiction, audience = "state_procurement_rules", "chhattisgarh", "department_buyer"
    elif _contains(src, "publicpromanual", "manual_for_procurement"):
        family, jurisdiction, audience = "goods_procurement_manual", "india", "department_buyer"
    elif _contains(src, "gfr"):
        family, jurisdiction, audience = "central_financial_rules", "india", "department_buyer"
    elif _contains(src, "bid_submission", "vendor_registration", "auctionmanual", "guidelines_to_bidders"):
        family, jurisdiction, audience = "vendor_portal_manual", "chhattisgarh", "vendor_bidder"
    elif _contains(src, "offline_tender", "corrigendum", "emd_challan"):
        family, jurisdiction, audience = "department_portal_manual", "chhattisgarh", "department_operator"
    elif _contains(src, "cvc", "vigilance"):
        family, jurisdiction, audience = "oversight_guidance", "india", "department_buyer"
    elif _contains(src, "medical", "medicine", "pharma", "hospital"):
        family, jurisdiction, audience = "specialized_medical_guidance", "india", "general"
    elif _contains(src, "forensic", "information technology act", "it act"):
        family, jurisdiction, audience = "specialized_technical_guidance", "india", "general"
    else:
        family, jurisdiction, audience = "general_reference", "unknown", "general"

    if _contains(combined, "need assessment", "purchase indent", "budgetary sanction",
                 "administrative approval", "technical specification", "requirement"):
        stage = "procurement_planning"
    elif _contains(combined, "bid evaluation", "technical evaluation", "financial evaluation"):
        stage = "bid_evaluation"
    elif _contains(combined, "purchase order", "contract award", "letter of acceptance"):
        stage = "purchase_order"
    elif _contains(combined, "inspection", "acceptance", "asset register", "stock register"):
        stage = "inspection_acceptance"
    elif _contains(combined, "bid submission", "submit bid", "upload bid"):
        stage = "bid_submission"
    else:
        stage = "general"

    if _contains(combined, "laptop", "computer", "computer system", "it equipment", "hardware"):
        commodity = "it_equipment"
    elif _contains(combined, "medical device", "medicine", "drug", "hospital"):
        commodity = "medical"
    else:
        commodity = "general_goods"

    return {
        "document_family": family,
        "jurisdiction": jurisdiction,
        "audience": audience,
        "procurement_stage": stage,
        "commodity": commodity,
        "metadata_version": 1,
    }
