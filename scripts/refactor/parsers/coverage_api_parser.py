"""
Coverage API Parser
===============================
This module provides functionality to parse coverage data from a specified path.

It includes methods for handling file paths and matching coverage data with requested files.
"""


from __future__ import annotations
from coverage import Coverage
from pathlib import Path
from typing import Dict, Tuple, Any, List

# ── helpers ───────────────────────────────────────────────────────────────
def _canonical(p: str | Path) -> str:
    """
    Return the canonical path for the given path.

    Parameters:
    ----------
    p: str | Path
        The path to be canonicalized.

    Returns:
    -------
    str
        The canonical path.
    """
    return str(Path(p).resolve()).replace("\\", "/")

def _best_suffix_match(target: str, candidates: List[str]) -> str | None:
    """
    Find the best suffix match for the target path among the given candidates.

    Parameters:
    ----------
    target: str
        The target path.
    candidates: List[str]
        A list of candidate paths.

    Returns:
    -------
    str | None
        The best suffix match, or None if no match is found.
    """
    tgt = _canonical(target).split("/")
    best, best_len = None, 0
    for c in candidates:
        common = 0
        for a, b in zip(reversed(tgt), reversed(c.split("/"))):
            if a.casefold() != b.casefold():
                break
            common += 1
        if common > best_len:
            best, best_len = c, common
    return best

# ── MAIN ──────────────────────────────────────────────────────────────────
def parse_coverage_with_api(
    coverage_path: str,
    method_ranges: Dict[str, Tuple[int, int]],
    filepath: str,
) -> Dict[str, Any]:
    """
    Parse coverage data from the specified path and return coverage information.

    Parameters:
    ----------
    coverage_path: str
        Path to the coverage data file.
    method_ranges: Dict[str, Tuple[int, int]]
        A dictionary mapping method names to their line ranges.
    filepath: str
        The path of the file for which coverage is being analyzed.

    Returns:
    -------
    Dict[str, Any]
        A dictionary containing coverage information for the specified file.
    """
    cov = Coverage(data_file=coverage_path)
    cov.load()
    data = cov.get_data()

    requested = _canonical(filepath)
    measured = list(map(_canonical, data.measured_files()))

    # 1️⃣ exact / case-insensitive match (pure string compare = no FileNotFoundError)
    matched = next(
        (m for m in measured if m.casefold() == requested.casefold()),
        None,
    ) or _best_suffix_match(requested, measured)

    # Graceful fallback – zero coverage instead of raising
    if not matched:
        return {
            requested: {
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

    covered = set(data.lines(matched) or [])

    return {
        requested: {
            m: {
                "coverage": hits / (end - start + 1) if (end - start + 1) else 0.0,
                "hits": hits,
                "lines": end - start + 1,
                "covered_lines": [ln for ln in range(start, end + 1) if ln in covered],
                "missing_lines": [ln for ln in range(start, end + 1) if ln not in covered],
            }
            for m, (start, end) in method_ranges.items()
            for hits in [sum(1 for ln in range(start, end + 1) if ln in covered)]
        }
    }
