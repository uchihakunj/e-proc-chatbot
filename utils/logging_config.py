"""
Centralized logging configuration for CHiPS pipeline.

Usage:
    from utils.logging_config import setup_logging
    logger = setup_logging("module_name")
    logger.info("Message")
"""

import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(
    name: str,
    level: str | None = None,
    log_dir: str | None = None,
    enable_file: bool | None = None,
) -> logging.Logger:
    """Setup logging for a module.
    
    Parameters
    ----------
    name : str
        Logger name (usually __name__)
    level : str, optional
        Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        Defaults to LOG_LEVEL env var, or INFO.
    log_dir : str, optional
        Directory for log files. Defaults to LOG_DIR env var or 'logs/'.
    enable_file : bool, optional
        Whether to enable file logging. Defaults to LOG_FILE_ENABLED env var.
    
    Returns
    -------
    logging.Logger
        Configured logger instance
    """
    # Get configuration from environment
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
    if log_dir is None:
        log_dir = os.getenv("LOG_DIR", "logs")
    if enable_file is None:
        enable_file = os.getenv("LOG_FILE_ENABLED", "true").lower() == "true"
    
    # Create logs directory if needed
    if enable_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Avoid duplicate handlers
    if logger.hasHandlers():
        return logger
    
    # Format: timestamp | level | logger | message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if enable_file:
        log_file = Path(log_dir) / f"{name.replace('.', '_')}.log"
        try:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(getattr(logging, level))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to setup file logging to {log_file}: {e}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger for a module.
    
    Parameters
    ----------
    name : str
        Logger name (usually __name__)
    
    Returns
    -------
    logging.Logger
        Logger instance
    """
    return logging.getLogger(name)
