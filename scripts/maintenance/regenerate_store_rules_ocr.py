"""Create a clean, reviewable OCR staging corpus for the CG Store Purchase Rules.

The source PDF has a KrutiDev text layer, so its embedded extraction must not be
used for retrieval.  This script renders each page and uses Hindi+English OCR.
It deliberately writes to a staging directory; promotion/re-indexing is a
separate verified step.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import easyocr
import fitz
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "01_preprocessing" / "input_pdfs" / "store purchase rule cg.pdf"
DEFAULT_OUT = ROOT / "tmp" / "store_rules_ocr_staging"


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--scale", type=float, default=2.0)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    reader = easyocr.Reader(["hi", "en"], gpu=False, verbose=False)
    pdf = fitz.open(PDF)
    pages = []
    for number, page in enumerate(pdf, 1):
        pix = page.get_pixmap(matrix=fitz.Matrix(args.scale, args.scale), colorspace=fitz.csGRAY)
        image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        lines = [clean(value) for value in reader.readtext(image, detail=0, paragraph=False)]
        text = "\n".join(line for line in lines if line)
        page_path = args.output / f"page_{number:03d}.txt"
        page_path.write_text(text + "\n", encoding="utf-8")
        pages.append(text)
        print(f"page {number:02d}/{pdf.page_count}: {len(text)} chars", flush=True)
    pdf.close()

    corpus = "\n\n".join(f"<!-- Page {i} -->\n{text}" for i, text in enumerate(pages, 1))
    (args.output / "structured.md").write_text(corpus, encoding="utf-8")
    devanagari = sum("\u0900" <= char <= "\u097f" for char in corpus)
    rules = len(re.findall(r"(?:नियम|Rule)\s*\d", corpus, flags=re.I))
    summary = (
        f"pages={len(pages)}\ncharacters={len(corpus)}\n"
        f"devanagari_characters={devanagari}\nrule_heading_matches={rules}\n"
    )
    (args.output / "quality.txt").write_text(summary, encoding="utf-8")
    print(summary, flush=True)


if __name__ == "__main__":
    main()
