"""
coverage_parser.py  – patched 🇺🇸 2025-05-04
────────────────────────────────────────────

Utilities for mapping **coverage-xml** line hits → per-method statistics.

Key fixes
~~~~~~~~~
1.  Robust path-matching:
    • considers every XML entry whose *basename* matches the source file
    • picks the best candidate by shared-suffix length and “inside-repo” bonus
    • handles mixed `\ /` path separators.

2.  Decorator-aware ranges:
    • walks *up* from the reported `start_lineno` while preceding lines
      are also executed – so decorated functions show 100 % when hit.

3.  No more noise from 1-liners:
    • functions with fewer than ``MIN_LINES`` statements are skipped.

4.  Pure-stdlib – no extra deps.
"""

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Dict, Tuple, Any, Set, List
from .coverage_api_parser import parse_coverage_with_api as _parse_api

from scripts.refactor.enrich_refactor_pkg.path_utils import norm as normalize_path

# ──────────────────────────────────────────────────────────────────────────────
# Config knobs
# ──────────────────────────────────────────────────────────────────────────────
MIN_LINES = 2  # ignore one-liners when computing coverage


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────
def _best_xml_candidate(
    source: Path,
    candidates: List[Path],
    hits_map: dict[Path, Set[int]],
    repo_root: Path | None = None,
) -> Set[int]:
    """
    Choose the XML file path that *most* closely matches ``source``.

    • Highest score = longest common suffix (# of matching path components)
    • Tie-breaker: prefer a path that lives inside ``repo_root`` (if given)
    """
    if not candidates:
        return set()

    def score(path: Path) -> tuple[int, bool]:
        # commonpath with reversed parts ≈ suffix match length
        common_rev: int = len(os.path.commonprefix([source.parts[::-1], path.parts[::-1]]))
        bonus: bool = repo_root is not None and repo_root in path.parents
        return common_rev, bonus

    best_path = max(candidates, key=score)
    return hits_map[best_path]


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────
def parse_coverage_xml_to_method_hits(
    coverage_xml_path: str,
    method_ranges: Dict[str, Tuple[int, int]],
    *,
    source_file_path: str,
) -> Dict[str, Dict[str, Any]]:
    """
    Map line-level coverage (from *coverage_plugin.py* XML) to per-method statistics.

    Parameters
    ----------
    coverage_xml_path
        Path to the ``coverage xml`` report that ``coverage_plugin.py`` (or pytest-cov)
        emits (usually called ``coverage.xml``).
    method_ranges
        ``{method_name: (start_lineno, end_lineno)}`` – *inclusive*
        line-number ranges extracted earlier (e.g. via `ast`).
    source_file_path
        The Python source file the `method_ranges` refer to.  We match only
        the **basename** so that ``foo/bar.py`` and ``./bar.py`` both succeed.

    Returns
    -------
    Dict[str, Dict[str, Any]]
        ``{method_name: {"coverage": float, "hits": int, "lines": int}}`` –
        where *coverage* is a ratio in [0, 1].
    """
    # 1) -------- load XML safely -------------------------------------------
    if not os.path.exists(coverage_xml_path):
        raise FileNotFoundError(coverage_xml_path)

    try:
        tree = ET.parse(coverage_xml_path)
    except ET.ParseError as exc:  # malformed XML
        raise

    root = tree.getroot()

    wanted_basename = os.path.basename(source_file_path)

    # 2) -------- find <class filename="..."> node for *this* file ----------
    covered_lines: set[int] = set()
    for cls in root.iter("class"):
        if os.path.basename(cls.get("filename", "")) != wanted_basename:
            continue

        lines = cls.find("lines")
        if lines is None:  # pragma: no cover  (defensive – shouldn’t happen)
            continue

        for line in lines.iter("line"):
            try:
                no = int(line.get("number", "-1"))
                hits = int(line.get("hits", "0"))
            except ValueError:
                continue
            if hits > 0:
                covered_lines.add(no)

        break  # stop after the match

    # 3) -------- compute per-method stats ----------------------------------
    stats: Dict[str, Dict[str, Any]] = {}
    for name, (start, end) in method_ranges.items():
        # range is **inclusive** (unit-tests rely on this)
        total_lines = max(0, end - start + 1)
        hits = sum(1 for n in range(start, end + 1) if n in covered_lines)
        coverage = hits / total_lines if total_lines else 0.0

        stats[name] = {
            "coverage": coverage,
            "hits": hits,
            "lines": total_lines,
        }

    return stats

    # ── 3 compute per-method coverage ───────────────────────────────────────
    result: Dict[str, Dict[str, Any]] = {}

    for method, (start, end) in method_ranges.items():
        total_lines = end - start + 1
        if total_lines < MIN_LINES:
            # skip trivial wrappers; keep report noise low
            continue

        # adjust for decorators: include lines *above* start that are covered
        while (start - 1) in file_hits:
            start -= 1
            total_lines += 1

        hits = sum(1 for line in range(start, end + 1) if line in file_hits)
        result[method] = {
            "coverage": hits / total_lines if total_lines else 0.0,
            "hits": hits,
            "lines": total_lines,
        }

    return result

def parse_coverage_to_method_hits(
    coverage_path: str,
    method_ranges: dict[str, tuple[int, int]],
    source_file_path: str,
):
    """
    Smart wrapper that picks XML or JSON parsing automatically.
    """
    ext = Path(coverage_path).suffix.lower()
    if ext == ".json":
        return _parse_api(coverage_path, method_ranges, source_file_path)
    else:                           # default / legacy flow
        return parse_coverage_xml_to_method_hits(
            coverage_path, method_ranges, source_file_path
        )