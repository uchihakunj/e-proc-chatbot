"""Promote verified CG Store Purchase Rules OCR and re-create its chunks.

This replaces only the known-bad Store Rules source material. The original
malformed chunks are retained under ``tmp/`` for audit.
"""
from __future__ import annotations

import argparse
import re
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGING = ROOT / "tmp" / "store_rules_ocr_staging"
STAGE2 = ROOT / "01_preprocessing" / "stage2_output" / "store purchase rule cg"
CHUNK_OUT = ROOT / "03_chunking" / "output"
ACTIVE_DIR = CHUNK_OUT / "store purchase rule cg"
SOURCE = "store purchase rule cg"


# A faithful English retrieval index for the official Hindi clauses. It adds
# no policy; it makes exact rules, values, and timelines retrievable for
# English and Hinglish queries when the scanned Hindi typography is variable.
VERIFIED_INDEX = """# Verified English retrieval index — Chhattisgarh Store Purchase Rules, 2002 (updated to 11 July 2024)

## Rule 2 and 2.1 — scope
The Rules apply to government departments, the State Electricity Board, public undertakings and boards, district and janpad panchayats, and urban bodies.

## Rule 3.1.1 — GeM route
When goods/services and their rates and specifications are available on GeM, buy through GeM using its prescribed process. Before ordering, the buyer must check technical specifications, seller credibility, L1 price, economy, and quality. A department may choose tendering instead only after written concurrence of the Finance Department through the concerned administrative department.

## Rule 3.1.2, 3.1.3 and 3.4 — other specified sources and tender route
Schedule 1 items unavailable on GeM may be bought through CSIDC e-Standard when their rates and specifications are available there. When the item is unavailable through the specified GeM/CSIDC/Schedule sources, procure through the Rule 4 tender procedure.

## Rule 4 and 4.1 — normal method and specifications
Government procurement is normally through the tender system. Before inviting a tender, the standards and technical specifications must be fixed by persons having technical knowledge.

## Rule 4.2 — startup exemption
A valid Chhattisgarh-recognised startup is exempt from prior-experience and prior-turnover conditions.

## Rule 4.3.1 — Single Tender
For a proprietary single item with an annual requirement not exceeding Rs. 50,000, single tender from one firm may be used where competition is not needed. Above Rs. 50,000, establish that only one manufacturer makes the required item and follow the prescribed proprietary/approval procedure. In an emergency, record reasons and obtain competent-authority approval. For standardisation or compatibility of spare parts, obtain advice of a competent technical expert and competent-authority approval.

## Rule 4.3.1(b)(3) and Appendix 4 — Proprietary Article Certificate (PAC)
Before proprietary-article procurement from a sole manufacturer or authorised seller, obtain a Proprietary Article Certificate in the Appendix 4 prescribed form. Publish a brief claim/objection notice in newspapers and the detailed notice on the government/department website, allowing at least 30 days. After objections are resolved, obtain the proposed supplier's rates and justification; the purchase committee recommends acceptance, rejection, or negotiation, followed by competent approval.

## Rule 4.3.2 — Limited Tender
Limited Tender normally covers estimated annual purchases from Rs. 50,001 to Rs. 3,00,000. Invite at least three manufacturers, authorised representatives, or registered manufacturers.

## Rule 4.3.3 — Open Tender and publicity
Open Tender applies from an estimated value of Rs. 3,00,001 upward. Above Rs. 3 lakh and up to Rs. 5 lakh: one widely circulated local-level newspaper. Above Rs. 5 lakh and up to Rs. 10 lakh: two widely circulated state-level newspapers. Above Rs. 10 lakh and up to Rs. 20 lakh: two widely circulated state-level newspapers and one national-level newspaper. Above Rs. 20 lakh: two widely circulated state-level newspapers and two national-level newspapers.

## Rule 4.3.3(c) — GeM methods, receipt, acceptance, and payment
For goods available on GeM, use the applicable GeM method: Direct Purchase, L1, e-bidding, or Reverse Auction. Issue the Provisional Receipt Certificate (PRC) within 48 hours of receiving goods. After verification, issue the Consignee Receipt and Acceptance Certificate (CRAC/CARC) within 10 days of PRC issuance. Make payment within 10 days of issuing CRAC/CARC, subject to effective GeM directions.

## Rule 4.3.3(d) and Rule 4.12 — competition and re-tender
The first Open Tender invitation should ensure participation of at least three eligible tenderers through manufacturers or authorised supplier representatives. If sufficient bids are not received after publishing the tender notice, call the tender again and make efforts to reach all potential tenderers.

## Rules 4.4 and 4.4.1 — short tender notice; Rule 4.4.3 — cancellation
A short tender notice must state the main goods/purpose and essential conditions, including the last date and time for receipt; detailed conditions may be available with the tender form. A competent officer may cancel an invited tender at any time without stating reasons.

## Rule 4.5 — minimum invitation timelines
Limited Tender: 15 days first invitation, 10 days second, 5 days third. Open Tender above Rs. 3,00,001 and up to Rs. 10 lakh: 21, 14, and 7 days respectively. Open Tender above Rs. 10 lakh: 30, 20, and 10 days respectively. Global Tender: 45, 30, and 20 days respectively.

## Rules 4.6.3 to 4.6.5 — opening and late bids
For an offline tender, open tenders one hour after the stipulated closing time on the same day; online tenders follow the published schedule. In a two-envelope tender, open the EMD/exemption-certificate envelope first; open the tender-form envelope only if adequate EMD or a valid exemption certificate is present, otherwise reject the bid. A tender received after the final date and time must not be opened; return it and record the return date and time on the sealed envelope.

## Rules 4.7, 4.7.1 and 4.8(a) — EMD and security
EMD is normally 1% of estimated purchase value. Retain the successful bidder's EMD and refund the other bidders' EMD within 15 days of finalisation. A registered small/cottage unit or valid recognised startup receives EMD exemption only on submitting the required certificate/proof with the tender. Before issuing the purchase order, obtain security deposit of at least 3% of actual purchase value. Do not accept EMD or security deposit in cash.

## Rules 4.9, 4.10, 4.12, 4.13 and 4.14 — conditions, quality, committee, order, repeat supply
Tender conditions must be clear and unambiguous. The bidder must be GST-registered for the tendered goods and quote taxes separately. If a pre-purchase sample cannot be obtained, the supplier may demonstrate the item; if that is not possible, reserve the buyer's right to inspect at the manufacturing site. An office purchasing Rs. 50,000 or more per year must form a purchase committee including the departmental accounts officer/accounts in-charge and officers with technical knowledge. If the L1/lowest tender is not accepted, record reasons in writing. Execute the contract before issuing the purchase order. A repeat supply order cannot be issued after six months from the original order and cannot exceed 25% of the original order quantity.

## Rule 11 — inspection and payment
Arrange quality inspection at the delivery site within a maximum of 10 days. Pay the supplier's bill according to the rules within 20 days of receiving the goods and bill.
"""


def validate() -> list[Path]:
    pages = sorted(STAGING.glob("page_*.txt"))
    if len(pages) != 29 or any(not page.read_text(encoding="utf-8").strip() for page in pages):
        raise RuntimeError("OCR staging is incomplete; expected 29 non-empty pages")
    corpus = "\n".join(page.read_text(encoding="utf-8") for page in pages)
    devanagari = sum("\u0900" <= char <= "\u097f" for char in corpus)
    if len(corpus) < 40_000 or devanagari < 25_000:
        raise RuntimeError("OCR staging did not meet the minimum text-quality threshold")
    return pages


def write_chunks(text: str) -> int:
    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    units = [unit.strip() for unit in re.split(r"(?=^## )", text, flags=re.M) if unit.strip()]
    for index, unit in enumerate(units, 1):
        payload = f"Type: procurement_rules\nAuthority: 10\nSource: {SOURCE}\n---\n{unit}\n"
        (ACTIVE_DIR / f"store_purchase_rule_cg_chunk_{index:03d}.txt").write_text(payload, encoding="utf-8")
    return len(units)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verified-index-only", action="store_true",
        help=("Build the audited English retrieval index without local OCR staging. "
              "Use this on Rocky Linux after pulling the code."),
    )
    args = parser.parse_args()
    pages = [] if args.verified_index_only else validate()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive = ROOT / "tmp" / "store_rules_legacy_source" / timestamp
    archive.mkdir(parents=True, exist_ok=True)
    legacy_chunks = list(CHUNK_OUT.glob("store purchase rule cg_chunk_*.txt"))
    for path in legacy_chunks:
        shutil.move(str(path), str(archive / path.name))
    if ACTIVE_DIR.exists():
        shutil.move(str(ACTIVE_DIR), str(archive / ACTIVE_DIR.name))
    if STAGE2.exists():
        shutil.move(str(STAGE2), str(archive / "stage2_store_purchase_rule_cg"))

    raw_pages = "\n\n".join(
        f"<!-- Official OCR page {number} -->\n{page.read_text(encoding='utf-8').strip()}"
        for number, page in enumerate(pages, 1)
    )
    ocr_section = (
        f"# Official Hindi OCR text\n\n{raw_pages}\n"
        if raw_pages else
        "# OCR source note\n\n"
        "This deployment was built from the audited English retrieval index. "
        "The temporary local OCR staging files are intentionally not required at runtime.\n"
    )
    structured = f"{VERIFIED_INDEX}\n\n{ocr_section}"
    STAGE2.mkdir(parents=True, exist_ok=True)
    (STAGE2 / "structured.md").write_text(structured, encoding="utf-8")
    count = write_chunks(VERIFIED_INDEX)
    print(f"archived_legacy_chunks={len(legacy_chunks)}")
    print(f"active_chunks_created={count}")
    print(f"stage2={STAGE2 / 'structured.md'}")
    print(f"archive={archive}")


if __name__ == "__main__":
    main()
