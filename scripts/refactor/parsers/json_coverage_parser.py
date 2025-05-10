import json
from pathlib import Path
from typing import Dict, Tuple, Any


def parse_json_coverage(
    json_path: str,
    method_ranges: Dict[str, Tuple[int, int]],
    filepath: str,
) -> Dict[str, Any]:
    """
    Parse JSON coverage data from the specified path and return coverage information.

    Parameters
    ----------
    json_path: str
        Path to the JSON coverage data file.
    method_ranges: Dict[str, Tuple[int, int]]
        A dictionary mapping method names to their line ranges.
    filepath: str
        The path of the file for which coverage is being analyzed.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing accurate coverage information for the specified file.
    """
    requested_path = str(Path(filepath).as_posix())

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_files = data.get("files", {})
    files = {Path(k).as_posix(): v for k, v in raw_files.items()}

    # Try exact match, else fallback to best suffix match
    coverage_info = files.get(requested_path)
    if not coverage_info:
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

    # No coverage data found; assume fully uncovered
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

    # Properly use function-level summaries if available
    func_summaries = coverage_info.get("functions", {})
    result = {}

    for m, (start, end) in method_ranges.items():
        func_cov = func_summaries.get(m, {})
        summary = func_cov.get("summary", {})

        coverage_percent = summary.get("percent_covered", 0.0)
        hits = summary.get("covered_lines", 0)
        total_lines = summary.get("num_statements", end - start + 1)
        missing_lines = summary.get("missing_lines", total_lines - hits)

        # If no detailed summary, fall back to executed_lines analysis
        if not summary:
            executed = set(coverage_info.get("executed_lines", []))
            covered_lines = [ln for ln in range(start, end + 1) if ln in executed]
            missing_lines_list = [ln for ln in range(start, end + 1) if ln not in executed]

            coverage_percent = (
                100.0 * len(covered_lines) / max(1, end - start + 1)
            )
            hits = len(covered_lines)
            total_lines = end - start + 1
            missing_lines = missing_lines_list

        result[m] = {
            "coverage": round(coverage_percent / 100.0, 4),  # Normalize to [0.0, 1.0]
            "hits": hits,
            "lines": total_lines,
            "covered_lines": func_cov.get("executed_lines", []),
            "missing_lines": missing_lines if isinstance(missing_lines, list) else [],
        }

    return {requested_path: result}
