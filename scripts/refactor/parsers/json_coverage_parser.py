import json
from pathlib import Path
from typing import Dict, Tuple, Any, List


def parse_json_coverage(
    json_path: str,
    method_ranges: Dict[str, Tuple[int, int]],
    filepath: str,
) -> Dict[str, Any]:
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
            method: {
                "coverage": sum(1 for line in range(start, end + 1) if line in executed) / (end - start + 1),
                "hits": sum(1 for line in range(start, end + 1) if line in executed),
                "lines": end - start + 1,
                "covered_lines": [l for l in range(start, end + 1) if l in executed],
                "missing_lines": [l for l in range(start, end + 1) if l not in executed],
            }
            for method, (start, end) in method_ranges.items()
        }
    }

    return result
