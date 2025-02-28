"""
File handling utilities for the xtract library.
"""

import os
import json
from typing import Any


def save_json(data: Any, filepath: str) -> None:
    """
    Utility to save data as JSON with consistent formatting.
    
    Args:
        data: Data to save as JSON
        filepath: Path where to save the file
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to create
    """
    os.makedirs(directory, exist_ok=True) 