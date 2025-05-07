"""
JSON Coverage Parser
===============================
This module provides functionality to parse coverage data from a specified JSON file.

It includes methods for matching coverage data with requested files and handling potential mismatches.
"""


import json
from pathlib import Path
from typing import Dict, Tuple, Any, List


def parse_json_coverage(
    json_path: str,
    method_ranges: Dict[str, Tuple[int, int]],
    filepath: str,
) -> Dict[str, Any]:
    """
    Parse JSON coverage data from the specified path and return coverage information.

    Parameters:
    ----------
    json_path: str
        Path to the JSON coverage data file.
    method_ranges: Dict[str, Tuple[int, int]]
        A dictionary mapping method names to their line ranges.
    filepath: str
        The path of the file for which coverage is being analyzed.

    Returns:
    -------
    Dict[str, Any]
        A dictionary containing coverage information for the specified file.
    """
    requested_path = str(Path(filepath).as_posix())

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    files = data.get("files", {})

    # Try exact match, else fuzzy suffix match
    coverage_info = files.get(requested_path)
    if not coverage_info:
        # fallback: longest matching suffix
        requested_parts = Path(requested_path).parts
        best_match = None
        best_len = 0
        for key in files:
            parts = Path(key).parts
            match_len = sum(1 for a, b in zip(reversed(parts), reversed(requested_parts)) if a == b)
            if match_len > best_len:
                best_match = key
                best_len = match_len
        if best_match:
            coverage_info = files[best_match]

    if not coverage_info:
        return {
            requested_path: {
                m: {
                    "coverage": 0.0,
                    "hits": 0,
                    "lines": end - start + 1,
                    "covered_lines": [],
                    "missing_lines": list(range(start, end + 1)),
                }
                for m, (start, end) in method_ranges.items()
            }
        }

    executed = set(coverage_info.get("executed_lines", []))
    result = {
        requested_path: {
            m: {
                "coverage": len(executed) / (end - start + 1) if (end - start + 1) > 0 else 0.0,
                "hits": len(executed),
                "lines": end - start + 1,
                "covered_lines": list(executed),
                "missing_lines": list(set(range(start, end + 1)) - executed),
            }
            for m, (start, end) in method_ranges.items()
        }
    }
    return result
