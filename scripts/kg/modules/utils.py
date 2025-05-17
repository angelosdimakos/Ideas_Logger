"""
Utility functions for the codebase analysis and graph generation.
"""

import json
import logging
from typing import Dict, Any, TypeVar, Optional

# Type definitions
NodeID = str
GraphData = Dict[str, Any]
DocMap = Dict[str, Dict[str, Any]]
ComplexityScores = Dict[str, float]

# Generic type for better type hinting
T = TypeVar("T")


def load_json_file(file_path: str) -> DocMap:
    """
    Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file.

    Returns:
        The parsed JSON content or empty dict on error.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {file_path}")
        return {}
    except Exception as e:
        logging.error(f"Error loading JSON file {file_path}: {e}")
        return {}


def safe_get(data: Dict[str, T], key: str, default: Optional[T] = None) -> Optional[T]:
    """
    Safely get a value from a dictionary.

    Args:
        data: Dictionary to get value from.
        key: Key to lookup.
        default: Default value if key not found.

    Returns:
        The value from the dictionary or default.
    """
    return data.get(key, default)


class DocMapNormalizer:
    """Handles normalization of module path keys in docmap dictionaries."""

    @staticmethod
    def normalize_keys(docmap: DocMap) -> DocMap:
        """
        Normalize all keys to use forward slashes for consistency.

        Args:
            docmap: A dictionary mapping module paths to their respective data.

        Returns:
            A new dictionary with normalized keys.
        """
        return {k.replace("\\", "/"): v for k, v in docmap.items()}
