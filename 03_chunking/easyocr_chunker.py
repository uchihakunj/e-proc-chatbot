"""
EasyOCR-based chunker for scanned PDFs.
Renders pages with PyMuPDF, OCRs with EasyOCR, saves chunks for Stage 4.

Usage:
    python easyocr_chunker.py --input <pdf_file_or_folder> --output <output_dir>
    python easyocr_chunker.py --input Store_Purhase_Rules_28.01.2021.pdf
"""

import argparse
import sys
import tempfile
from pathlib import Path

import fitz          # PyMuPDF
import easyocr
import numpy as np
from PIL import Image

# Characters per chunk (approx 1024 tokens * 4 chars/token)
CHUNK_CHARS = 4096
# OCR DPI for rendering pages
RENDER_DPI = 200
# EasyOCR languages
OCR_LANGUAGES = ["en", "hi"]


def render_page(page: fitz.Page, dpi: int = RENDER_DPI) -> np.ndarray:
    """Render a PDF page to a numpy array for EasyOCR."""
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
    img = Image.frombytes("L", [pix.width, pix.height], pix.samples)
    return np.array(img)


def ocr_pdf(pdf_path: Path, reader: easyocr.Reader) -> list[str]:
    """OCR all pages of a PDF, returning per-page text strings."""
    doc = fitz.open(str(pdf_path))
    page_texts = []

    print(f"  OCR-ing {doc.page_count} pages...")
    for i, page in enumerate(doc, 1):
        print(f"    Page {i}/{doc.page_count}", end="\r", flush=True)
        try:
            img_array = render_page(page)
            results = reader.readtext(img_array, detail=0, paragraph=True)
            text = "\n".join(results).strip()
            page_texts.append(text)
        except Exception as e:
            print(f"\n    Page {i} failed: {e}")
            page_texts.append("")

    doc.close()
    print()  # newline after carriage-return progress
    return page_texts


def split_into_chunks(page_texts: list[str], chunk_chars: int = CHUNK_CHARS) -> list[str]:
    """Join pages and split into fixed-size chunks."""
    full_text = "\n\n".join(t for t in page_texts if t.strip())
    paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]

    chunks, current, current_len = [], [], 0
    for para in paragraphs:
        if current_len + len(para) > chunk_chars and current:
            chunks.append("\n\n".join(current))
            current, current_len = [para], len(para)
        else:
            current.append(para)
            current_len += len(para)

    if current:
        chunks.append("\n\n".join(current))
    return chunks


def chunk_scanned_pdf(pdf_path: Path, output_dir: Path, reader: easyocr.Reader) -> int:
    """OCR and chunk a single scanned PDF. Returns chunk count."""
    doc_name = pdf_path.stem
    doc_output = output_dir / doc_name
    doc_output.mkdir(parents=True, exist_ok=True)

    print(f"\nProcessing: {pdf_path.name}")
    page_texts = ocr_pdf(pdf_path, reader)

    total_chars = sum(len(t) for t in page_texts)
    non_empty = sum(1 for t in page_texts if t.strip())
    print(f"  {non_empty}/{len(page_texts)} pages with text, {total_chars} total chars")

    if total_chars < 50:
        print(f"  WARNING: Very little text extracted — document may not be OCR-able.")
        return 0

    chunks = split_into_chunks(page_texts)
    print(f"  {len(chunks)} chunks created")

    for i, chunk_text in enumerate(chunks, 1):
        filepath = doc_output / f"{doc_name}_chunk_{i:03d}.txt"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Source: {doc_name}\n")
            f.write(f"---\n")
            f.write(chunk_text + "\n")

    return len(chunks)


def main():
    parser = argparse.ArgumentParser(description="EasyOCR chunker for scanned PDFs")
    parser.add_argument("--input", "-i", required=True, help="PDF file or folder")
    parser.add_argument("--output", "-o",
                        default=str(Path(__file__).parent / "output"),
                        help="Output directory for chunks")
    parser.add_argument("--lang", nargs="+", default=OCR_LANGUAGES,
                        help=f"EasyOCR language codes (default: {OCR_LANGUAGES})")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_file():
        pdfs = [input_path]
    elif input_path.is_dir():
        pdfs = sorted(input_path.glob("*.pdf"))
    else:
        print(f"ERROR: {input_path} not found")
        sys.exit(1)

    if not pdfs:
        print("No PDFs found.")
        sys.exit(1)

    print(f"Initializing EasyOCR with languages: {args.lang}")
    reader = easyocr.Reader(args.lang, gpu=False)
    print("EasyOCR ready.\n")

    total_chunks = 0
    for pdf in pdfs:
        total_chunks += chunk_scanned_pdf(pdf, output_dir, reader)

    print(f"\nDone — {total_chunks} total chunks saved to {output_dir}")


if __name__ == "__main__":
    main()
