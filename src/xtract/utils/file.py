"""
File handling utilities for the xtract library.
"""

import os
import json
from typing import Any

from xtract.config.logging import get_logger

# Get a logger for this module
logger = get_logger(__name__)


def save_json(data: Any, filepath: str) -> None:
    """
    Utility to save data as JSON with consistent formatting.

    Args:
        data: Data to save as JSON
        filepath: Path where to save the file
    """
    logger.debug(f"Saving JSON data to {filepath}")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.debug(f"Successfully saved JSON data to {filepath}")


def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Directory path to create
    """
    if not os.path.exists(directory):
        logger.debug(f"Creating directory: {directory}")
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Successfully created directory: {directory}")
    else:
        logger.debug(f"Directory already exists: {directory}")
