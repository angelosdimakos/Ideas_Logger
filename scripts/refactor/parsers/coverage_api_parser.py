from coverage import CoverageData
from pathlib import Path
from typing import Dict, Tuple, Any, Set
import logging

logger = logging.getLogger(__name__)

def parse_coverage_with_api(
    coverage_path: str,
    method_ranges: Dict[str, Tuple[int, int]],
    source_file_path: str,
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Use Coverage.py API to parse line coverage and compute method-level stats.

    Returns:
        Dict[source_file][method] = { coverage stats }
    """
    cov_data = CoverageData()
    cov_data.read_file(coverage_path)

    resolved_path = Path(source_file_path).resolve()
    try:
        covered_lines: Set[int] = set(cov_data.lines(str(resolved_path)) or [])
    except Exception as e:
        logger.warning(f"[Coverage] Failed to retrieve lines for {resolved_path}: {e}")
        return {}

    method_coverage: Dict[str, Dict[str, Any]] = {}
    for method, (start, end) in method_ranges.items():
        total_lines = end - start + 1
        hits = sum(1 for ln in range(start, end + 1) if ln in covered_lines)
        method_coverage[method] = {
            "coverage": hits / total_lines if total_lines > 0 else 0.0,
            "hits": hits,
            "lines": total_lines,
        }

    return {str(resolved_path): method_coverage}
