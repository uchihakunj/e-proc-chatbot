"""
run_full_pipeline.py
====================
Master script that runs the full OCR + chunk + embed pipeline on all
documents in input_pdfs/ and fixes any stage2 OCR failures.

Sequence:
  1. Fix failed stage2 docs (delete broken output, re-run stage1+stage2)
  2. Run stage1+stage2 on any remaining new PDFs in input_pdfs/
  3. Chunk all new/updated stage2 outputs
  4. Index all new chunks into Qdrant

Usage:
    python run_full_pipeline.py               # full run
    python run_full_pipeline.py --no-embed    # skip embeddings
    python run_full_pipeline.py --dry-run     # show plan only
"""

import argparse, json, logging, shutil, subprocess, sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

ROOT       = Path(__file__).resolve().parent
PREPROC    = ROOT / '01_preprocessing'
STAGE1_OUT = PREPROC / 'stage1_output'
STAGE2_OUT = PREPROC / 'stage2_output'
INPUT_PDFS = PREPROC / 'input_pdfs'
USED_FILES = PREPROC / 'used_files'
CHUNK_OUT  = ROOT / '03_chunking' / 'output'
CHUNKER    = ROOT / '03_chunking' / 'docling_chunker.py'
EMBED      = ROOT / '04_embeddings_and_kg' / 'scripts' / 'embeddings_production.py'
RUN1       = PREPROC / 'run_stage1.py'
RUN2       = PREPROC / 'run_stage2.py'


def run_cmd(cmd, cwd=None, timeout=18000):
    log.info('  $ ' + ' '.join(str(c) for c in cmd))
    try:
        r = subprocess.run(cmd, text=True, timeout=timeout,
                           cwd=str(cwd) if cwd else None)
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        log.error('  TIMEOUT'); return False
    except Exception as e:
        log.error(f'  ERROR: {e}'); return False


def has_ocr_failure(doc_dir: Path) -> bool:
    sj = doc_dir / 'structured.json'
    if not sj.exists():
        return False
    try:
        data  = json.loads(sj.read_text(encoding='utf-8', errors='replace'))
        pages = data.get('pages', [])
        return any('[OCR failed' in str(p.get('text', '')) for p in pages)
    except Exception:
        return False


def is_already_good(doc_name: str) -> bool:
    """Return True if stage2 output exists and has no failures."""
    d = STAGE2_OUT / doc_name
    return d.exists() and not has_ocr_failure(d)


# ── Step 1: Fix failed stage2 docs ───────────────────────────────────────────
def fix_failed_docs(dry_run: bool) -> list[str]:
    """Re-run stage1+stage2 for every failed doc whose PDF is available."""
    log.info('\n── Step 1: Fix failed stage2 outputs ──')
    fixed = []
    for doc_dir in sorted(STAGE2_OUT.iterdir()):
        if not doc_dir.is_dir() or not has_ocr_failure(doc_dir):
            continue
        doc_name = doc_dir.name

        # Find the source PDF
        pdf = None
        for d in [INPUT_PDFS, USED_FILES, INPUT_PDFS / 'other']:
            p = d / f'{doc_name}.pdf'
            if p.exists():
                pdf = p; break

        if not pdf:
            log.warning(f'  SKIP (PDF not found): {doc_name}')
            continue

        log.info(f'  RE-RUNNING: {doc_name}  ←  {pdf.name}')
        if dry_run:
            fixed.append(doc_name); continue

        # Copy PDF to input_pdfs if it's elsewhere
        work_pdf = INPUT_PDFS / pdf.name
        copied = False
        if not work_pdf.exists():
            shutil.copy2(str(pdf), str(work_pdf)); copied = True

        # Delete broken stage2 output
        shutil.rmtree(doc_dir)

        # Stage 1
        run_cmd([sys.executable, str(RUN1), str(work_pdf)], cwd=PREPROC)

        stage1_dir = STAGE1_OUT / work_pdf.stem
        if not stage1_dir.exists():
            log.error(f'  Stage 1 output missing for {doc_name}')
            if copied: work_pdf.unlink(missing_ok=True)
            continue

        # Stage 2
        run_cmd([sys.executable, str(RUN2), str(stage1_dir)], cwd=PREPROC, timeout=18000)

        if copied and work_pdf.exists():
            work_pdf.unlink(missing_ok=True)

        fixed.append(doc_name)

    log.info(f'  Fixed: {len(fixed)} doc(s)')
    return fixed


# ── Step 2: Process new PDFs that have no stage2 output yet ──────────────────
def process_new_pdfs(dry_run: bool) -> list[str]:
    """Run stage1+stage2 for PDFs in input_pdfs with no stage2_output."""
    log.info('\n── Step 2: Process new PDFs ──')
    processed = []

    new_pdfs = [
        p for p in INPUT_PDFS.glob('*.pdf')
        if not (STAGE2_OUT / p.stem / 'structured.md').exists()
    ]

    if not new_pdfs:
        log.info('  Nothing new to process.'); return []

    for pdf in sorted(new_pdfs):
        log.info(f'  NEW: {pdf.name}')
        if dry_run:
            processed.append(pdf.stem); continue

        # Stage 1
        ok = run_cmd([sys.executable, str(RUN1), str(pdf)], cwd=PREPROC)

        stage1_dir = STAGE1_OUT / pdf.stem
        if not stage1_dir.exists():
            log.error(f'  Stage 1 output missing for {pdf.name}'); continue

        # Stage 2
        run_cmd([sys.executable, str(RUN2), str(stage1_dir)], cwd=PREPROC, timeout=18000)
        processed.append(pdf.stem)

    log.info(f'  Processed: {len(processed)} new PDF(s)')
    return processed


# ── Step 3: Chunk all new/updated stage2 outputs ─────────────────────────────
def chunk_updated(updated_docs: list[str], dry_run: bool):
    log.info('\n── Step 3: Chunk updated docs ──')
    if not CHUNKER.exists():
        log.warning('  Chunker not found — skipping'); return

    for doc_name in updated_docs:
        stage2_dir = STAGE2_OUT / doc_name
        md_file    = stage2_dir / 'structured.md'
        if not md_file.exists():
            log.warning(f'  No structured.md for {doc_name}'); continue

        out_dir = CHUNK_OUT / doc_name
        log.info(f'  Chunking {doc_name}')
        if dry_run: continue

        # Remove old chunks first so they get replaced
        if out_dir.exists():
            shutil.rmtree(out_dir)

        run_cmd([sys.executable, str(CHUNKER),
                 '--input', str(md_file),
                 '--output', str(out_dir)])

        chunks = list(out_dir.rglob('*_chunk_*.txt')) if out_dir.exists() else []
        log.info(f'  → {len(chunks)} chunk(s)')


# ── Step 4: Embed ─────────────────────────────────────────────────────────────
def run_embed(dry_run: bool):
    log.info('\n── Step 4: Embedding new chunks ──')
    if dry_run:
        log.info('  [dry-run] would run embeddings_production.py'); return
    if not EMBED.exists():
        log.warning(f'  Embeddings script not found'); return
    run_cmd([sys.executable, str(EMBED)], cwd=EMBED.parent, timeout=18000)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-embed', action='store_true')
    parser.add_argument('--dry-run',  action='store_true')
    args = parser.parse_args()

    if args.dry_run:
        log.info('=== DRY RUN — no changes will be made ===\n')

    fixed_docs     = fix_failed_docs(args.dry_run)
    new_docs       = process_new_pdfs(args.dry_run)
    all_updated    = list(dict.fromkeys(fixed_docs + new_docs))  # dedup, preserve order

    if all_updated:
        chunk_updated(all_updated, args.dry_run)
    else:
        log.info('\nNo documents updated — nothing to chunk.')

    if not args.no_embed and not args.dry_run:
        run_embed(args.dry_run)
    elif args.no_embed:
        log.info('\nSkipping embeddings (--no-embed).')

    log.info('\n=== Pipeline complete ===')
    log.info(f'Fixed failed: {len(fixed_docs)}  |  New PDFs: {len(new_docs)}  |  Total updated: {len(all_updated)}')


if __name__ == '__main__':
    main()
