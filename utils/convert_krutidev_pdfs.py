"""
convert_krutidev_pdfs.py
========================
For Hindi PDFs typed in the Kruti Dev legacy font, the embedded text layer is
ASCII gibberish. This script:
  1. extracts the text layer with PyMuPDF,
  2. converts Kruti Dev -> Unicode Devanagari (kruti_to_unicode),
  3. writes ~300-word chunk .txt files into 03_chunking/output/<doc_name>/
     in the same format the rest of the pipeline expects.

After running this, `process_remaining.py` will see these docs as already
chunked (so docling won't re-extract the gibberish) and will just embed them.

Usage:
    python utils/convert_krutidev_pdfs.py "FileA.pdf" "FileB.pdf"
"""

import sys
from pathlib import Path

import fitz  # PyMuPDF

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kruti_to_unicode import kruti_to_unicode  # noqa: E402

ROOT      = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "01_preprocessing" / "input_pdfs"
CHUNK_OUT = ROOT / "03_chunking" / "output"
CHUNK_WORDS = 300


def convert_pdf(pdf_name: str) -> int:
    pdf_path = INPUT_DIR / pdf_name
    if not pdf_path.exists():
        print(f"  !! not found: {pdf_path}")
        return 0

    doc_name = pdf_path.stem
    out_dir  = CHUNK_OUT / doc_name
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    full = []
    for page in doc:
        txt = page.get_text()
        if txt.strip():
            full.append(kruti_to_unicode(txt))
    doc.close()

    words = " ".join(full).split()
    chunks = [" ".join(words[i:i + CHUNK_WORDS]) for i in range(0, len(words), CHUNK_WORDS)]
    chunks = [c for c in chunks if len(c.strip()) > 50]

    for idx, chunk in enumerate(chunks, 1):
        (out_dir / f"{doc_name}_chunk_{idx:03d}.txt").write_text(
            f"Source: {pdf_path.name}\n---\n{chunk}\n", encoding="utf-8"
        )

    print(f"  OK  {doc_name}: {doc.page_count if not doc.is_closed else '?'} pages "
          f"-> {len(chunks)} Unicode chunks  ({out_dir})")
    return len(chunks)


def main():
    files = sys.argv[1:] or [
        "GFR2017_HINDI.pdf",
        "Vigilance Manual 2021 (Hindi).pdf",
    ]
    print("Converting Kruti Dev Hindi PDFs -> Unicode chunks ...")
    total = 0
    for f in files:
        total += convert_pdf(f)
    print(f"Done. {total} chunk(s) written. Now run process_remaining.py to embed.")


if __name__ == "__main__":
    main()
