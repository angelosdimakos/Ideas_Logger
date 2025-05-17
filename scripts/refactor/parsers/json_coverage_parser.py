import json
import logging
from pathlib import Path
from typing import Dict, Tuple, Any, List, Optional

log = logging.getLogger(__name__)


# ─────────────────────────── helper functions ────────────────────────────
def _load_files(json_path: str) -> Dict[str, Any]:
    """Return the `files` section with all keys normalised to POSIX paths."""
    with open(json_path, "r", encoding="utf-8") as fh:
        raw = json.load(fh).get("files", {})
    return {Path(k).as_posix(): v for k, v in raw.items()}


def _best_suffix_match(files: Dict[str, Any], requested: str) -> Optional[Dict[str, Any]]:
    """
    Find the file-entry whose tail components best match *requested*.
    Returns the matching coverage dict or **None** if nothing plausible found.
    """
    requested_parts = Path(requested).parts
    best_key: Optional[str] = None
    best_len = 0

    for key in files:
        parts = Path(key.replace("\\", "/")).parts  # tolerate “\”
        match_len = sum(1 for a, b in zip(reversed(parts), reversed(requested_parts)) if a == b)

        log.debug("compare key=%s match_len=%d", key, match_len)
        if match_len > best_len:
            best_key, best_len = key, match_len

    return files.get(best_key) if best_key else None


def _fully_uncovered(method_ranges: Dict[str, Tuple[int, int]]) -> Dict[str, Any]:
    """Return a coverage dict that marks every method as 0 % covered."""
    return {
        m: {
            "coverage": 0.0,
            "hits": 0,
            "lines": end - start + 1,
            "covered_lines": [],
            "missing_lines": list(range(start, end + 1)),
        }
        for m, (start, end) in method_ranges.items()
    }


def _coverage_from_summary(summary: Dict[str, Any], total: int) -> Tuple[float, int, List[int]]:
    """Extract coverage %, hits and missing lines list from a summary block."""
    pct = summary.get("percent_covered", 0.0) / 100.0
    hits = summary.get("covered_lines", 0)
    missing = summary.get("missing_lines", [])
    if not isinstance(missing, list):  # summary may store an int
        missing = []
    return pct, hits, missing


def _coverage_from_executed(
    executed: List[int], rng: Tuple[int, int]
) -> Tuple[float, int, List[int]]:
    start, end = rng
    lines = range(start, end + 1)
    covered = [ln for ln in lines if ln in executed]
    missing = [ln for ln in lines if ln not in executed]
    total = len(covered) + len(missing)
    pct = len(covered) / total if total else 0.0
    return pct, len(covered), missing


# ─────────────────────────────── main API ────────────────────────────────
def parse_json_coverage(
    json_path: str,
    method_ranges: Dict[str, Tuple[int, int]],
    filepath: str,
) -> Dict[str, Any]:
    """
    Return per-method coverage data for *filepath* based on a `coverage.py`
    JSON (v5) report previously converted with ``coverage json``.
    """
    requested = Path(filepath).as_posix()
    files = _load_files(json_path)

    # 1️⃣ exact match → 2️⃣ suffix fallback → 3️⃣ fully uncovered
    coverage_info = files.get(requested) or _best_suffix_match(files, requested)
    if coverage_info is None:
        return {requested: _fully_uncovered(method_ranges)}

    executed_lines = coverage_info.get("executed_lines", [])
    summaries = {k: v.get("summary", {}) for k, v in coverage_info.get("functions", {}).items()}

    results: Dict[str, Any] = {}
    for method, rng in method_ranges.items():
        start, end = rng
        total_lines = end - start + 1

        if summaries.get(method):  # prefer function-level summary if present
            pct, hits, missing = _coverage_from_summary(summaries[method], total_lines)
        else:  # fall back to executed_lines slice
            pct, hits, missing = _coverage_from_executed(executed_lines, rng)

        results[method] = {
            "coverage": round(pct, 4),
            "hits": hits,
            "lines": total_lines,
            "covered_lines": [ln for ln in range(start, end + 1) if ln not in missing],
            "missing_lines": missing,
        }

    return {requested: results}
