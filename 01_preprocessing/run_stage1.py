"""
Stage 1 — Image Preparation and PDF Processing
Converts PDFs to images and applies OCR preprocessing.

Usage:
    python run_stage1.py                              # Use default paths
    python run_stage1.py /path/to/document.pdf       # Process single PDF
    python run_stage1.py /path/to/pdf_folder/        # Process all PDFs in folder
    python run_stage1.py -o /custom/output/          # Specify output directory
    python run_stage1.py --config config.json        # Load from config file
    python run_stage1.py --show-config               # Display current configuration
"""
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

# Use centralized logging
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logging

from stage1_image_prep import ImagePrepPipeline


logger = setup_logging(__name__)

_SCRIPT_DIR = Path(__file__).parent
DEFAULT_INPUT = str(_SCRIPT_DIR / "input_pdfs")
DEFAULT_OUTPUT = str(_SCRIPT_DIR / "stage1_output")


def _load_config_file(config_file: str) -> dict:
    """Load a JSON config file for stage 1 overrides."""
    config_path = Path(config_file)
    if config_path.suffix.lower() != ".json":
        raise ValueError(f"Unsupported config file: {config_path}")

    with config_path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def validate_pdf(path: Path) -> bool:
    """Validate that a file is a valid PDF.
    
    Parameters
    ----------
    path : Path
        Path to PDF file
        
    Returns
    -------
    bool
        True if valid PDF file exists, False otherwise
        
    Raises
    ------
    FileNotFoundError
        If file doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF (extension: {path.suffix})")
    
    # Check file size (PDF should have reasonable size)
    file_size = path.stat().st_size
    if file_size < 100:  # Too small - likely invalid
        raise ValueError(f"PDF file too small ({file_size} bytes): {path}")
    if file_size > 500 * 1024 * 1024:  # > 500 MB
        logger.warning(f"Large PDF file ({file_size / 1024 / 1024:.1f} MB): {path}")
    
    return True


def collect_pdfs(path: Path) -> List[Path]:
    """Collect all PDF files from path (file or directory).
    
    Parameters
    ----------
    path : Path
        File or directory path
        
    Returns
    -------
    List[Path]
        List of valid PDF file paths
        
    Raises
    ------
    ValueError
        If path is invalid
    FileNotFoundError
        If path doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    
    if path.is_file():
        validate_pdf(path)
        return [path]
    
    if path.is_dir():
        pdfs = sorted(path.glob("*.pdf"))
        if not pdfs:
            logger.warning(f"No PDF files found in {path}")
            return []
        
        # Validate each PDF
        valid_pdfs = []
        for pdf in pdfs:
            try:
                validate_pdf(pdf)
                valid_pdfs.append(pdf)
            except (FileNotFoundError, ValueError) as e:
                logger.warning(f"Skipping invalid PDF: {e}")
                continue
        
        if valid_pdfs:
            logger.info(f"Found {len(valid_pdfs)} valid PDF(s) in {path}")
        return valid_pdfs
    
    raise ValueError(f"Not a valid PDF file or directory: {path}")


def main() -> int:
    """Main entry point with configuration support.
    
    Returns
    -------
    int
        Exit code (0 = success, 1 = error)
    """
    parser = argparse.ArgumentParser(
        description="Stage 1 — PDF Image Preparation and OCR Preprocessing"
    )
    parser.add_argument("input", type=str, nargs="?",
                       help="PDF file or folder containing PDFs")
    parser.add_argument("--output", "-o", type=str,
                       help="Output directory for processed images")
    parser.add_argument("--mask-stamps", type=bool, default=True,
                       help="Mask stamps in output (default: True)")
    parser.add_argument("--save-debug", type=bool, default=False,
                       help="Save debug images (default: False)")
    parser.add_argument("--config", "-c", type=str,
                       help="Configuration file (JSON)")
    parser.add_argument("--show-config", action="store_true",
                       help="Display configuration and exit")
    args = parser.parse_args()

    logger.info("Stage 1: Image Preparation and PDF Processing")

    try:
        config_overrides = {}

        if args.config:
            try:
                config_overrides = _load_config_file(args.config)
                logger.info(f"Loaded config from: {args.config}")
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
                return 1

        input_path_str = args.input or config_overrides.get('input_dir') or DEFAULT_INPUT
        output_path_str = args.output or config_overrides.get('output_dir') or DEFAULT_OUTPUT

        if args.show_config:
            print(f"\n{'='*60}")
            print(f"Stage 1 Configuration")
            print(f"{'='*60}")
            print(f"Input Path: {Path(input_path_str).resolve()}")
            print(f"Output Path: {Path(output_path_str).resolve()}")
            print(f"{'='*60}\n")
            return 0
        
        logger.info(f"Input:  {input_path_str}")
        logger.info(f"Output: {output_path_str}")
        
        # Create output directory
        Path(output_path_str).mkdir(parents=True, exist_ok=True)
        
        # Collect and validate PDFs
        input_path = Path(input_path_str)
        try:
            pdfs = collect_pdfs(input_path)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Input validation failed: {e}")
            return 1
        
        if not pdfs:
            logger.error("No valid PDF files found to process")
            return 1
        
        # Initialize pipeline
        pipeline = ImagePrepPipeline(
            output_dir=output_path_str,
            mask_stamps_in_output=args.mask_stamps,
            save_debug_images=args.save_debug,
        )
        
        logger.info(f"Processing {len(pdfs)} PDF(s) → {Path(output_path_str).resolve()}")
        
        # Process all PDFs
        all_results = []
        failed_count = 0
        
        for i, pdf_path in enumerate(pdfs, 1):
            logger.info(f"[{i}/{len(pdfs)}] Processing: {pdf_path.name}")
            try:
                result = pipeline.process(pdf_path)
                all_results.append(result)

                if hasattr(result, 'pages'):
                    stamps_pages = sum(1 for p in result.pages if hasattr(p, 'has_stamps') and p.has_stamps)
                    skewed_pages = sum(1 for p in result.pages if hasattr(p, 'skew_angle') and p.skew_angle != 0.0)
                    logger.info(f"    {result.total_pages} pages | {skewed_pages} deskewed | {stamps_pages} with stamps")
                else:
                    logger.info(f"    Processed successfully")
            except Exception as e:
                logger.error(f"Error processing {pdf_path.name}: {type(e).__name__}: {e}")
                failed_count += 1
                continue

        # Summary and exit code
        if all_results:
            total_pages = sum(r.total_pages for r in all_results if hasattr(r, 'total_pages'))
            total_stamps = sum(
                sum(p.stamp_count for p in r.pages if hasattr(p, 'stamp_count'))
                for r in all_results if hasattr(r, 'pages')
            )
            logger.info(f"✅ COMPLETED — {len(pdfs)} PDF(s), {total_pages} pages, {total_stamps} stamps detected")
            if failed_count > 0:
                logger.warning(f"⚠️  {failed_count} PDF(s) failed to process")
                return 1  # Return error if any PDFs failed
            return 0
        else:
            logger.error("❌ No PDFs were successfully processed")
            return 1
    
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 130  # Standard exit code for Ctrl+C
    except Exception as e:
        logger.error(f"Fatal error: {type(e).__name__}: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())