"""
Centralized configuration management for the CHiPS pipeline.

Provides Config and PathManager used by all pipeline stages.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Project root is the directory that contains this file
_PROJECT_ROOT = Path(__file__).resolve().parent

# Stage-specific default configurations
_STAGE_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "preprocessing": {
        "input_dir": str(_PROJECT_ROOT / "01_preprocessing" / "input_pdfs"),
        "output_dir": str(_PROJECT_ROOT / "01_preprocessing" / "stage1_output"),
    },
    "ocr": {
        "input_dir": str(_PROJECT_ROOT / "01_preprocessing" / "stage1_output"),
        "output_dir": str(_PROJECT_ROOT / "01_preprocessing" / "stage2_output"),
    },
    "optimization": {
        "input_dir": str(_PROJECT_ROOT / "01_preprocessing" / "stage2_output"),
        "output_dir": str(_PROJECT_ROOT / "02_optimization" / "output"),
    },
    "chunking": {
        "input_dir": str(_PROJECT_ROOT / "02_optimization" / "output"),
        "output_dir": str(_PROJECT_ROOT / "03_chunking" / "output"),
        "model": "BAAI/bge-m3",
        "max_tokens": 400,
    },
    "embeddings": {
        "chunk_dir": str(_PROJECT_ROOT / "03_chunking" / "output"),
        "qdrant_path": str(_PROJECT_ROOT / "04_embeddings_and_kg" / "db" / "qdrant_local"),
        "collection": "db3",
        "batch_size": 8,
    },
    "retrieval": {
        "top_k_retrieval": 50,
        "final_context": 8,
        "rerank_truncation": 1500,
        "max_faq_results": 2,
        "authority_weight": 0.20,
        "semantic_weight": 0.70,
        "hybrid_weight": 0.10,
        "verify_low_confidence": 0.55,
        "verify_high_risk_intents": True,
        "verify_on_mixed_documents": True,
    },
}


class Config:
    """Stage-level configuration with environment-variable and file overrides."""

    def __init__(self, stage: str = "chunking", config_dict: Optional[Dict[str, Any]] = None):
        self.stage = stage
        self.config_dict: Dict[str, Any] = dict(_STAGE_DEFAULTS.get(stage, {}))
        if config_dict:
            self.config_dict.update(config_dict)

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    @staticmethod
    def load_from_file(path: str) -> Dict[str, Any]:
        """Load a JSON config file and return the dict."""
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with config_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    # ------------------------------------------------------------------
    # Path accessors
    # ------------------------------------------------------------------

    def get_input_path(self, as_str: bool = False):
        raw = self.config_dict.get("input_dir", ".")
        p = Path(os.path.expandvars(raw))
        return str(p) if as_str else p

    def get_output_path(self, as_str: bool = False):
        raw = self.config_dict.get("output_dir", "output")
        p = Path(os.path.expandvars(raw))
        return str(p) if as_str else p

    def get(self, key: str, default: Any = None) -> Any:
        return self.config_dict.get(key, default)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def log_config(self) -> None:
        logger.info("Configuration [stage=%s]:", self.stage)
        for k, v in self.config_dict.items():
            logger.info("  %-20s = %s", k, v)


class PathManager:
    """Static helpers for creating and validating paths."""

    @staticmethod
    def ensure_dirs(*paths: str) -> None:
        """Create directories if they don't exist."""
        for path in paths:
            Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def validate_input(path: str) -> Path:
        """Raise FileNotFoundError if path does not exist."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Input path not found: {p}")
        return p

    @staticmethod
    def project_root() -> Path:
        return _PROJECT_ROOT
