"""
Direct PDF chunker using PyMuPDF — for digital (non-scanned) PDFs.
Extracts embedded text and saves chunks in the format expected by embeddings_production.py.

Usage:
    python pdf_direct_chunker.py --input <pdf_folder> --output <output_dir>
"""

import argparse
import sys
from pathlib import Path

import fitz  # PyMuPDF


MAX_TOKENS = 1024  # approx chars per chunk (rough estimate: 1 token ≈ 4 chars)
CHUNK_CHARS = MAX_TOKENS * 4


def extract_pages(pdf_path: Path) -> list[str]:
    """Extract text from each page of a digital PDF."""
    doc = fitz.open(str(pdf_path))
    pages = []
    for page in doc:
        text = page.get_text("text").strip()
        if text:
            pages.append(text)
    doc.close()
    return pages


def split_into_chunks(pages: list[str], chunk_chars: int = CHUNK_CHARS) -> list[str]:
    """Split pages into roughly equal-sized chunks by character count."""
    full_text = "\n\n".join(pages)
    paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]

    chunks = []
    current = []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) > chunk_chars and current:
            chunks.append("\n\n".join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += len(para)

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def chunk_pdf(pdf_path: Path, output_dir: Path) -> int:
    """Extract and chunk a single PDF. Returns number of chunks created."""
    doc_name = pdf_path.stem
    doc_output = output_dir / doc_name
    doc_output.mkdir(parents=True, exist_ok=True)

    print(f"Processing: {pdf_path.name}")
    pages = extract_pages(pdf_path)

    if not pages:
        print(f"  WARNING: No text extracted from {pdf_path.name} (may be scanned)")
        return 0

    total_text = sum(len(p) for p in pages)
    print(f"  {len(pages)} pages, {total_text} chars")

    chunks = split_into_chunks(pages)
    print(f"  {len(chunks)} chunks created")

    for i, chunk_text in enumerate(chunks, 1):
        filename = doc_output / f"{doc_name}_chunk_{i:03d}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Source: {doc_name}\n")
            f.write(f"---\n")
            f.write(chunk_text + "\n")

    return len(chunks)


def main():
    parser = argparse.ArgumentParser(description="Direct PDF to chunks (PyMuPDF)")
    parser.add_argument("--input", "-i", required=True, help="PDF file or folder")
    parser.add_argument("--output", "-o", default=str(Path(__file__).parent / "output"),
                        help="Output directory for chunks")
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

    print(f"Found {len(pdfs)} PDF(s)")
    total_chunks = 0
    for pdf in pdfs:
        total_chunks += chunk_pdf(pdf, output_dir)

    print(f"\nDone — {total_chunks} total chunks saved to {output_dir}")


if __name__ == "__main__":
    main()
