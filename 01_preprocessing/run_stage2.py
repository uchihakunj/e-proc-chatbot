"""
Stage 2 — OCR and Structure Extraction
Run on Stage 1 output (cleaned images).

Usage:
    python run_stage2.py
    python run_stage2.py path/to/stage1_output/
    python run_stage2.py path/to/stage1_output/ -o my_ocr_output/
"""
import argparse
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Optional, List

# Windows fix: force huggingface_hub to copy files instead of creating symlinks
if os.name == "nt":
    try:
        import huggingface_hub.file_download as _hf_dl
        _hf_dl.are_symlinks_supported = lambda *args, **kwargs: False
    except ImportError:
        pass

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logging

from stage2_ocr import OCRPipeline


logger = setup_logging(__name__)

# ── Config (edit these defaults if needed) ────────────────────────────────────
# Use relative paths for Docker compatibility
_SCRIPT_DIR = Path(__file__).parent
DEFAULT_INPUT  = str(_SCRIPT_DIR / "stage1_output")  # e.g. r"D:\docs\stage1_output"
DEFAULT_OUTPUT = str(_SCRIPT_DIR / "stage2_output")  # e.g. r"D:\docs\stage2_output"


def main() -> int:
    """Main entry point for Stage 2 OCR pipeline.
    
    Returns
    -------
    int
        Exit code (0 = success, 1 = error)
    """
    parser = argparse.ArgumentParser(
        description="Stage 2 — OCR and Structure Extraction"
    )
    parser.add_argument("input", type=str, nargs="?", default=DEFAULT_INPUT,
                        help="Stage 1 output folder (single doc) or root Stage 1 directory")
    parser.add_argument("--output", "-o", type=str,
                        default=DEFAULT_OUTPUT or "stage2_output",
                        help="Output directory (default: stage2_output)")
    args = parser.parse_args()

    logger.info("Stage 2: OCR and Structure Extraction")

    try:
        if not args.input:
            logger.error("No input path provided. Set DEFAULT_INPUT or pass as argument.")
            return 1

        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"Input path not found: {input_path}")
            return 1
        
        logger.info(f"Input:  {input_path}")
        logger.info(f"Output: {args.output}")

        pipeline = OCRPipeline(output_dir=args.output)

        if (input_path / "metadata.json").exists():
            # Single document
            logger.info(f"Processing single document: {input_path.name}")
            result = pipeline.process(input_path)
            _print_summary(result)
            _move_processed_pdf(result.source_pdf)
            _cleanup_stage1_dir(input_path)
        else:
            # Root directory with multiple documents
            logger.info(f"Processing all documents in: {input_path}")
            results = pipeline.process_all(input_path)
            
            if not results:
                logger.error("No documents processed successfully")
                return 1
            
            for result in results:
                _print_summary(result)
                _move_processed_pdf(result.source_pdf)
                doc_dir = input_path / Path(result.source_pdf).stem
                if doc_dir.exists():
                    _cleanup_stage1_dir(doc_dir)
            
            total_pages  = sum(r.total_pages for r in results)
            total_tables = sum(len(r.all_tables) for r in results)
            logger.info(f"✅ COMPLETED — {len(results)} document(s), {total_pages} pages, {total_tables} tables extracted")
        
        return 0
    
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {type(e).__name__}: {e}", exc_info=True)
        return 1


def _print_summary(result) -> None:
    """Print summary of OCR results for a document.
    
    Parameters
    ----------
    result
        DocumentOCRResult object with extraction results
    """
    logger.info(f"  Document : {result.source_pdf}")
    logger.info(f"  Pages    : {result.total_pages}")
    logger.info(f"  Elements : {len(result.all_elements)}")
    logger.info(f"  Tables   : {len(result.all_tables)}")
    logger.info(f"  Text     : {len(result.full_text)} chars")

    headings = [e for e in result.all_elements if e.element_type.value in ("title", "heading")]
    if headings:
        logger.info(f"  Headings (first 10):")
        for h in headings[:10]:
            preview = h.text[:80] if len(h.text) > 80 else h.text
            logger.info(f"    [{h.element_type.value}] {preview}")


def _move_processed_pdf(source_pdf: str) -> None:
    """Move processed PDFs from input_pdfs to used_files.
    
    Parameters
    ----------
    source_pdf : str
        Path to source PDF file
    """
    src = Path(source_pdf)
    if not src.exists():
        logger.debug(f"Source PDF not found: {src}")
        return

    used_dir = Path(__file__).parent / "used_files"
    try:
        used_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.warning(f"Could not create used_files directory: {e}")
        return

    dest = used_dir / src.name
    
    # Handle duplicate filenames
    if dest.exists():
        stem = dest.stem
        suffix = dest.suffix
        counter = 1
        while True:
            candidate = used_dir / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                dest = candidate
                break
            counter += 1

    try:
        shutil.move(str(src), str(dest))
        logger.info(f"Moved source PDF to: {dest}")
    except OSError as e:
        logger.warning(f"Could not move source PDF {src}: {e}")


def _cleanup_stage1_dir(stage1_dir: Path) -> None:
    """Remove Stage 1 output folder after Stage 2 completes.
    
    Parameters
    ----------
    stage1_dir : Path
        Path to Stage 1 output directory to remove
    """
    if not stage1_dir.exists():
        logger.debug(f"Stage 1 directory not found: {stage1_dir}")
        return

    try:
        shutil.rmtree(stage1_dir)
        logger.info(f"Cleaned up Stage 1 output: {stage1_dir}")
    except OSError as e:
        logger.warning(f"Could not remove Stage 1 output {stage1_dir}: {e}")


if __name__ == "__main__":
    sys.exit(main())