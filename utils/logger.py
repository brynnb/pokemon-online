"""
Shared logging configuration for export scripts.

This module provides a consistent logging setup across all export scripts,
with both file and console output.
"""

import logging
import os
from datetime import datetime

def setup_logger(name, log_level=logging.INFO):
    """
    Set up a logger with file and console handlers.

    Args:
        name: The name of the logger (typically __name__ from the calling module)
        log_level: The logging level (default: logging.INFO)

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Avoid adding handlers multiple times if logger already exists
    if logger.handlers:
        return logger

    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # File handler - logs to export_scripts/logs/export.log
    log_file = os.path.join(log_dir, 'export.log')
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    # Console handler - logs to stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def log_script_start(logger, script_name):
    """
    Log the start of a script execution.

    Args:
        logger: Logger instance
        script_name: Name of the script being executed
    """
    logger.info("=" * 80)
    logger.info(f"Starting {script_name}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

def log_script_end(logger, script_name, success=True):
    """
    Log the end of a script execution.

    Args:
        logger: Logger instance
        script_name: Name of the script being executed
        success: Whether the script completed successfully
    """
    status = "COMPLETED SUCCESSFULLY" if success else "FAILED"
    logger.info("=" * 80)
    logger.info(f"{script_name} {status}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
