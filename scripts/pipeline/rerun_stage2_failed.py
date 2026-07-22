"""
rerun_stage2_failed.py
======================
Re-runs Stage 1 + Stage 2 OCR for documents whose stage2_output
shows '[OCR failed' in structured.json.

Only processes documents whose original PDF can be found in:
  - 01_preprocessing/used_files/
  - 01_preprocessing/input_pdfs/

After stage2 succeeds, re-chunks and re-embeds those documents.

Usage:
    python rerun_stage2_failed.py               # re-run + embed
    python rerun_stage2_failed.py --no-embed    # re-run only
    python rerun_stage2_failed.py --dry-run     # show plan only
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

ROOT        = Path(__file__).resolve().parent
PREPROC     = ROOT / '01_preprocessing'
STAGE2_OUT  = PREPROC / 'stage2_output'
USED_FILES  = PREPROC / 'used_files'
INPUT_PDFS  = PREPROC / 'input_pdfs'
CHUNK_OUT   = ROOT / '03_chunking' / 'output'
CHUNKER     = ROOT / '03_chunking' / 'docling_chunker.py'
EMBED       = ROOT / '04_embeddings_and_kg' / 'scripts' / 'embeddings_production.py'
RUN1        = PREPROC / 'run_stage1.py'
RUN2        = PREPROC / 'run_stage2.py'


def find_failed_docs() -> list[str]:
    """Return doc names whose stage2 structured.json has OCR failure text."""
    failed = []
    for doc_dir in sorted(STAGE2_OUT.iterdir()):
        if not doc_dir.is_dir():
            continue
        sj = doc_dir / 'structured.json'
        if not sj.exists():
            continue
        try:
            data  = json.loads(sj.read_text(encoding='utf-8', errors='replace'))
            pages = data.get('pages', [])
            if any('[OCR failed' in str(p.get('text', '')) for p in pages):
                failed.append(doc_dir.name)
        except Exception:
            pass
    return failed


def find_pdf(doc_name: str) -> Path | None:
    """Search known locations for the source PDF of a doc."""
    search_dirs = [USED_FILES, INPUT_PDFS, INPUT_PDFS / 'other']
    for d in search_dirs:
        for ext in ('.pdf', '.PDF'):
            p = d / f'{doc_name}{ext}'
            if p.exists():
                return p
    return None


def run(cmd: list[str], cwd: Path = None, timeout: int = 1200) -> bool:
    """Run a subprocess. Return True on success."""
    log.info(f'  $ {" ".join(str(c) for c in cmd)}')
    try:
        result = subprocess.run(
            cmd, text=True, timeout=timeout,
            cwd=str(cwd) if cwd else None
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        log.error('  TIMEOUT')
        return False
    except Exception as e:
        log.error(f'  ERROR: {e}')
        return False


def rerun_doc(doc_name: str, pdf_path: Path, dry_run: bool) -> bool:
    """Re-run stage1+stage2+chunk for a single document. Return True on success."""
    log.info(f'\n=== {doc_name} ===')
    log.info(f'  PDF: {pdf_path}')

    if dry_run:
        log.info('  [dry-run] would re-run stage1 → stage2 → chunk')
        return True

    # ── Put PDF in input_pdfs so stage1 can find it ──────────────────────
    work_pdf = INPUT_PDFS / pdf_path.name
    if not work_pdf.exists():
        shutil.copy2(str(pdf_path), str(work_pdf))
        log.info(f'  Copied PDF → {work_pdf.name}')
        copied = True
    else:
        copied = False

    try:
        # ── Stage 1: PDF → cleaned images ────────────────────────────────
        log.info('  Stage 1: converting PDF to images…')
        ok = run([sys.executable, str(RUN1), str(work_pdf)], cwd=PREPROC)
        if not ok:
            log.warning('  Stage 1 exited non-zero — continuing anyway')

        stage1_dir = PREPROC / 'stage1_output' / work_pdf.stem
        if not stage1_dir.exists():
            log.error(f'  Stage 1 output not found: {stage1_dir}')
            return False

        # ── Clear old broken stage2 output ───────────────────────────────
        old_stage2 = STAGE2_OUT / doc_name
        if old_stage2.exists():
            shutil.rmtree(old_stage2)
            log.info(f'  Removed old stage2 output: {old_stage2.name}')

        # ── Stage 2: images → OCR text ────────────────────────────────────
        log.info('  Stage 2: running OCR…')
        ok = run([sys.executable, str(RUN2), str(stage1_dir)], cwd=PREPROC, timeout=3600)
        if not ok:
            log.warning('  Stage 2 exited non-zero')

        # ── Verify structured.md was created ─────────────────────────────
        new_stage2 = STAGE2_OUT / work_pdf.stem
        structured_md = new_stage2 / 'structured.md'
        if not structured_md.exists():
            log.error('  structured.md not created — stage2 may have failed')
            return False

        content = structured_md.read_text(encoding='utf-8', errors='replace')
        failed_count = content.count('[OCR failed')
        total_pages  = content.count('<!-- Page')
        log.info(f'  structured.md: {total_pages} pages, {failed_count} still failed')

        # ── Re-chunk ──────────────────────────────────────────────────────
        if CHUNKER.exists():
            # Remove old chunks so they get regenerated
            old_chunks = CHUNK_OUT / doc_name
            if old_chunks.exists():
                shutil.rmtree(old_chunks)
            out_dir = CHUNK_OUT / work_pdf.stem
            log.info('  Chunking structured.md…')
            run([sys.executable, str(CHUNKER),
                 '--input', str(structured_md),
                 '--output', str(out_dir)])
            chunks = list(out_dir.rglob('*_chunk_*.txt')) if out_dir.exists() else []
            log.info(f'  {len(chunks)} chunk(s) created')

        return True

    finally:
        # Remove the copy we made (stage2 moves original to used_files)
        if copied and work_pdf.exists():
            work_pdf.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-embed', action='store_true')
    parser.add_argument('--dry-run',  action='store_true')
    args = parser.parse_args()

    log.info('Scanning for OCR failures in stage2_output…')
    failed_docs = find_failed_docs()
    log.info(f'Found {len(failed_docs)} document(s) with OCR failures')

    available, missing = [], []
    for doc in failed_docs:
        pdf = find_pdf(doc)
        if pdf:
            available.append((doc, pdf))
        else:
            missing.append(doc)

    log.info(f'\nCan re-run: {len(available)}')
    for doc, pdf in available:
        log.info(f'  ✓ {doc}  ←  {pdf.name}')

    log.info(f'\nMissing PDFs (need to upload): {len(missing)}')
    for doc in missing:
        log.info(f'  ✗ {doc}')

    if args.dry_run:
        log.info('\nDry-run mode — no changes made.')
        return

    succeeded, failed = 0, 0
    for doc, pdf in available:
        if rerun_doc(doc, pdf, dry_run=args.dry_run):
            succeeded += 1
        else:
            failed += 1

    log.info(f'\nRe-run complete: {succeeded} succeeded, {failed} failed')

    if args.no_embed or succeeded == 0:
        log.info('Skipping embeddings.')
        return

    if not EMBED.exists():
        log.warning(f'Embeddings script not found: {EMBED}')
        return

    log.info('\nRunning embeddings to update Qdrant…')
    run([sys.executable, str(EMBED)], cwd=EMBED.parent, timeout=3600)
    log.info('Done.')

    if missing:
        log.info('\n⚠  Upload these PDFs to input_pdfs/ then re-run this script:')
        for doc in missing:
            log.info(f'    {doc}.pdf')


if __name__ == '__main__':
    main()
