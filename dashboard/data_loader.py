import os
import json
import gzip
import fnmatch
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
    """
    Determines whether a file path should be excluded based on predefined patterns.
    
    Returns:
        True if the path matches any exclusion pattern or is an '__init__.py' file; otherwise, False.
    """
    filename = os.path.basename(path)
    return filename == "__init__.py" or any(fnmatch.fnmatch(path, pat) for pat in EXCLUDE_PATTERNS)

def load_artifact(path: str) -> Dict[str, Any]:
    """
    Loads a JSON artifact from disk, handling compressed formats and filtering excluded entries.
    
    Attempts to load the artifact from a gzip-compressed, compressed, or plain JSON file in order of preference. Applies specialized decompression for merged or strictness reports if detected, and removes top-level keys matching exclusion criteria.
    
    Args:
        path: The base path to the artifact file (without compression extensions).
    
    Returns:
        A dictionary representing the processed artifact, or an empty dictionary if no file is found.
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

        # run any specialized decompression based on blob content
    if isinstance(blob, dict):
        # merged report compressor outputs 'doc' & 'files'
        if "doc" in blob and "files" in blob:
            blob = decompress_merged(blob)
        # strictness report compressor outputs 'modules'
        elif "modules" in blob:
            blob = load_strictness_comp(blob)

    # filter out excluded top-level entries
    if isinstance(blob, dict):
        return {k: v for k, v in blob.items() if not is_excluded(k)}
    return blob

def weighted_coverage(func_dict: Dict[str, Any]) -> float:
    """
    Calculates the lines-of-code weighted coverage from a dictionary of function coverage entries.
    
    Each entry should contain a "lines" key for the number of lines (defaulting to 1) and a "coverage" key for the coverage value (defaulting to 0.0). The function returns the total covered lines divided by the total lines, or 0.0 if there are no lines.
    
    Args:
        func_dict: A dictionary where each value is a mapping with "lines" and "coverage" keys.
    
    Returns:
        The LOC-weighted coverage as a float between 0.0 and 1.0.
    """
    covered, total = 0.0, 0
    for entry in func_dict.values():
        loc      = entry.get("lines", 1)
        coverage = entry.get("coverage", 0.0)
        covered += coverage * loc
        total   += loc
    return covered / total if total else 0.0
