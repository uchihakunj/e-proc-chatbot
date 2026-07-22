"""
process_remaining.py
====================
One-shot script that:
  1. Finds stage2_output directories that have no corresponding chunk folder
  2. Chunks their structured.md into a doc-specific output subfolder
  3. Finds PDFs/DOCX in input_pdfs not yet chunked, chunks them directly
  4. Runs embeddings_production to index all new chunks into Qdrant

Run from the project root:
    python process_remaining.py

Optional flags:
    --no-embed   Skip the embedding step (chunk only)
    --dry-run    Print what would be processed without doing anything
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import easyocr
    import numpy as np
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# Lazy-loaded EasyOCR reader (Hindi + English)
_easyocr_reader = None

def _get_ocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        log.info('Loading EasyOCR (hi + en)…')
        _easyocr_reader = easyocr.Reader(['hi', 'en'], gpu=False, verbose=False)
    return _easyocr_reader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

SCRIPT_DIR   = Path(__file__).resolve().parent
STAGE2_OUT   = SCRIPT_DIR / '01_preprocessing' / 'stage2_output'
INPUT_PDFS   = SCRIPT_DIR / '01_preprocessing' / 'input_pdfs'
CHUNK_OUT    = SCRIPT_DIR / '03_chunking' / 'output'
CHUNKER      = SCRIPT_DIR / '03_chunking' / 'docling_chunker.py'
EMBED_SCRIPT = SCRIPT_DIR / '04_embeddings_and_kg' / 'scripts' / 'embeddings_production.py'


def already_chunked(doc_name: str) -> bool:
    """Return True if a doc-specific chunk subfolder exists with chunk files."""
    folder = CHUNK_OUT / doc_name
    if folder.exists() and any(folder.rglob('*_chunk_*.txt')):
        return True
    # Also accept flat files named after the doc (e.g. DOCX output)
    if any(CHUNK_OUT.glob(f'{doc_name}_chunk_*.txt')):
        return True
    return False


def run_chunker(input_path: Path, doc_name: str) -> bool:
    """Chunk a single file into CHUNK_OUT/<doc_name>/. Return True on success."""
    out_dir = CHUNK_OUT / doc_name
    log.info(f'[CHUNK] {doc_name}  ←  {input_path.name}')
    try:
        result = subprocess.run(
            [sys.executable, str(CHUNKER),
             '--input',  str(input_path),
             '--output', str(out_dir)],
            text=True, timeout=600
        )
        created = list(out_dir.rglob('*_chunk_*.txt')) if out_dir.exists() else []
        if created:
            log.info(f'  OK → {len(created)} chunk(s)')
            return True
        log.warning(f'  0 chunks from docling (exit {result.returncode}) – trying fallback')
        return False
    except subprocess.TimeoutExpired:
        log.error(f'  TIMEOUT – {doc_name}')
        return False
    except Exception as e:
        log.error(f'  ERROR – {doc_name}: {e}')
        return False


def run_fallback_chunker(input_path: Path, doc_name: str) -> bool:
    """Fallback chunker when docling layout model fails.

    Strategy (in order):
    1. EasyOCR on rendered page images  → handles Krutidev/image-only PDFs
    2. PyMuPDF raw text extraction      → last resort for digital-text PDFs
    """
    if not PYMUPDF_AVAILABLE:
        log.error(f'  PyMuPDF not available for fallback on {doc_name}')
        return False

    out_dir = CHUNK_OUT / doc_name
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. EasyOCR on rendered page images (handles Krutidev + scanned PDFs) ──
    if EASYOCR_AVAILABLE and input_path.suffix.lower() == '.pdf':
        log.info(f'  [FALLBACK] EasyOCR (hi+en) rendering for {doc_name}')
        try:
            reader   = _get_ocr_reader()
            doc      = fitz.open(str(input_path))
            pages_text = []

            for i, page in enumerate(doc):
                # Render at 200 DPI for good OCR quality
                mat = fitz.Matrix(200/72, 200/72)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                    pix.height, pix.width, 3
                )
                results = reader.readtext(img_arr, detail=0, paragraph=True)
                page_text = '\n'.join(results).strip()
                if page_text:
                    pages_text.append(f'[Page {i+1}]\n{page_text}')

            doc.close()
            full_text = '\n\n'.join(pages_text)

            if full_text.strip():
                return _save_chunks(full_text, input_path, doc_name, out_dir, method='EasyOCR')

            log.warning(f'  EasyOCR produced no text for {doc_name}, trying raw extraction')
        except Exception as e:
            log.warning(f'  EasyOCR failed for {doc_name}: {e}, trying raw extraction')

    # ── 2. PyMuPDF raw text extraction (for digital-text PDFs) ──────────────
    log.info(f'  [FALLBACK] PyMuPDF raw text for {doc_name}')
    try:
        if input_path.suffix.lower() == '.pdf':
            doc = fitz.open(str(input_path))
            full_text = '\n\n'.join(
                f'[Page {i+1}]\n{page.get_text().strip()}'
                for i, page in enumerate(doc)
                if page.get_text().strip()
            )
            doc.close()
        else:
            full_text = input_path.read_text(encoding='utf-8', errors='replace')

        if not full_text.strip():
            log.warning(f'  No text extracted from {doc_name}')
            return False

        return _save_chunks(full_text, input_path, doc_name, out_dir, method='PyMuPDF')

    except Exception as e:
        log.error(f'  Fallback error for {doc_name}: {e}')
        return False


def _save_chunks(full_text: str, input_path: Path, doc_name: str,
                 out_dir: Path, method: str = '') -> bool:
    """Split text into ~300-word chunks and save to out_dir."""
    words      = full_text.split()
    chunk_size = 300
    chunks     = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    chunks     = [c for c in chunks if len(c.strip()) > 50]

    for idx, chunk in enumerate(chunks, 1):
        (out_dir / f'{doc_name}_chunk_{idx:03d}.txt').write_text(
            f'Source: {input_path.name}\n---\n{chunk}\n', encoding='utf-8'
        )

    tag = f' [{method}]' if method else ''
    log.info(f'  FALLBACK OK{tag} → {len(chunks)} chunk(s)')
    return len(chunks) > 0


def main():
    parser = argparse.ArgumentParser(description='Process remaining unprocessed documents')
    parser.add_argument('--no-embed', action='store_true', help='Skip embedding step')
    parser.add_argument('--dry-run',  action='store_true', help='Print plan only, do nothing')
    args = parser.parse_args()

    if not CHUNKER.exists():
        log.error(f'Chunker not found: {CHUNKER}')
        sys.exit(1)

    # Each task is (input_path, doc_name, label)
    tasks: list[tuple[Path, str, str]] = []

    # ── 1. stage2_output dirs not yet chunked ─────────────────────────────
    if STAGE2_OUT.exists():
        for doc_dir in sorted(STAGE2_OUT.iterdir()):
            if not doc_dir.is_dir():
                continue
            if already_chunked(doc_dir.name):
                continue
            md_file = doc_dir / 'structured.md'
            if md_file.exists():
                tasks.append((md_file, doc_dir.name, f'stage2/{doc_dir.name}'))

    # ── 2. input_pdfs not yet chunked ─────────────────────────────────────
    if INPUT_PDFS.exists():
        for f in sorted(INPUT_PDFS.iterdir()):
            if f.is_dir() or f.suffix.lower() not in {'.pdf', '.docx'}:
                continue
            if already_chunked(f.stem):
                continue
            tasks.append((f, f.stem, f'input_pdfs/{f.name}'))

    if not tasks:
        log.info('Nothing to process — all files are already chunked.')
        return

    log.info(f'\nFound {len(tasks)} file(s) to process:')
    for _, _, label in tasks:
        log.info(f'  • {label}')

    if args.dry_run:
        log.info('\nDry-run mode — no changes made.')
        return

    CHUNK_OUT.mkdir(parents=True, exist_ok=True)
    succeeded, failed = 0, 0

    for input_path, doc_name, label in tasks:
        ok = run_chunker(input_path, doc_name)
        if not ok and input_path.suffix.lower() in {'.pdf', '.docx', '.txt', '.md'}:
            ok = run_fallback_chunker(input_path, doc_name)
        if ok:
            succeeded += 1
        else:
            failed += 1

    log.info(f'\nChunking complete: {succeeded} succeeded, {failed} failed')

    if args.no_embed:
        log.info('Skipping embeddings (--no-embed)')
        return

    if succeeded == 0:
        log.info('No new chunks to embed.')
        return

    if not EMBED_SCRIPT.exists():
        log.warning(f'Embeddings script not found: {EMBED_SCRIPT}')
        log.info('Run manually:')
        log.info(f'  cd "{EMBED_SCRIPT.parent}" && python {EMBED_SCRIPT.name}')
        return

    log.info('\nRunning embeddings indexer (this may take several minutes)…')
    try:
        result = subprocess.run(
            [sys.executable, str(EMBED_SCRIPT)],
            timeout=3600, cwd=str(EMBED_SCRIPT.parent)
        )
        if result.returncode == 0:
            log.info('Embeddings indexing complete.')
        else:
            log.warning(f'Embeddings exited with code {result.returncode}')
    except subprocess.TimeoutExpired:
        log.error('Embeddings timed out after 1 hour')
    except Exception as e:
        log.error(f'Embeddings error: {e}')


if __name__ == '__main__':
    main()
