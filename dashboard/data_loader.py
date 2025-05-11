import os
import json
import gzip
import fnmatch
from pathlib import Path
from typing import Any, Dict

# these come from your existing compressor modules
from scripts.refactor.compressor.merged_report_squeezer import decompress_obj as decompress_merged
from scripts.refactor.compressor.strictness_report_squeezer import decompress_obj as load_strictness_comp

# mirror your .coveragerc omit
EXCLUDE_PATTERNS = [
    "tests/*",
    "dashboard/*",
    "gui/**",
    "*/__init__.py",
]

def is_excluded(path: str) -> bool:
    filename = os.path.basename(path)
    return filename == "__init__.py" or any(fnmatch.fnmatch(path, pat) for pat in EXCLUDE_PATTERNS)

def load_artifact(path: str) -> Dict[str, Any]:
    """
    Load JSON (or .comp.json / .comp.json.gz) and automatically
    decompress & filter out excluded keys at the top level.
    """
    base, _ = os.path.splitext(path)
    comp = f"{base}.comp.json"
    gz   = f"{comp}.gz"

    # pick the right file
    if os.path.exists(gz):
        raw = gzip.decompress(open(gz, "rb").read()).decode()
        blob = json.loads(raw)
    elif os.path.exists(comp):
        blob = json.load(open(comp, "r", encoding="utf-8"))
    elif os.path.exists(path):
        blob = json.load(open(path, "r", encoding="utf-8"))
    else:
        return {}

    # run any specialized decompression
    if path.endswith("merged_report.json"):
        blob = decompress_merged(blob)
    elif path.endswith("final_strictness_report.json"):
        blob = load_strictness_comp(blob)

    # filter out excluded top-level entries
    if isinstance(blob, dict):
        return {k: v for k, v in blob.items() if not is_excluded(k)}
    return blob

def weighted_coverage(func_dict: Dict[str, Any]) -> float:
    """
    Compute LOC-weighted coverage: sum(cov_i * loc_i) / sum(loc_i).
    """
    covered, total = 0.0, 0
    for entry in func_dict.values():
        loc      = entry.get("lines", 1)
        coverage = entry.get("coverage", 0.0)
        covered += coverage * loc
        total   += loc
    return covered / total if total else 0.0
