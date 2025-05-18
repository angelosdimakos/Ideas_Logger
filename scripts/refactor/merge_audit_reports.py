#!/usr/bin/env python3
"""
merge_audit_reports.py – bespoke normalizer

Merges docstring, coverage/complexity, and linting JSON reports into a unified output.
Uses **custom normalization logic per input source** to ensure accurate matching.

Author: Your Name
Version: 1.0
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, Set


def normalize_path(path: str) -> str:
    """
    Normalize any report path by stripping everything up to and including the project 'scripts' directory
    and converting to a forward‑slash relative path.

    Args:
        path (str): The original file path.

    Returns:
        str: The normalized relative path.
    """
    # unify all separators
    normalized = path.replace("\\", "/")
    parts = Path(normalized).parts
    try:
        idx = parts.index("scripts")
        rel_parts = parts[idx + 1 :]
    except ValueError:
        # no 'scripts' in path; use as given, but strip leading slashes or drive letters
        rel_parts = parts
    # join with forward slashes
    return "/".join(rel_parts).lstrip("/")


def load_and_normalize(path: Path) -> Dict[str, Any]:
    """
    Load JSON and normalize its keys using a common path normalizer.

    Args:
        path (Path): The path to the JSON file.

    Returns:
        Dict[str, Any]: A dictionary with normalized keys and their corresponding values.
    """
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    return {normalize_path(k): v for k, v in raw.items()}


# In merge_audit_reports.py:
def merge_reports(
    doc_path: Path,
    cov_path: Path,
    lint_path: Path,
    output_path: Path,
    changed_files: Set[str] = None,
    task_results: Dict[str, Any] = None,
    verbose: bool = False,
    return_data: bool = False
) -> Dict[str, Any] | None:
    """
    Merge docstring, coverage, and linting reports into a single JSON output.

    Args:
        doc_path (Path): Path to the docstring JSON file.
        cov_path (Path): Path to the coverage JSON file.
        lint_path (Path): Path to the linting JSON file.
        output_path (Path): Path where the merged output will be saved.
        changed_files (Set[str], optional): If provided, only include files in this set.
        task_results (Dict[str, Any], optional): CI task routing results. Filters what data to merge.
        verbose (bool): If True, prints summary output.
        return_data (bool): If True, returns the merged dictionary instead of writing to file.

    Returns:
        Optional[Dict[str, Any]]: Merged report, if return_data is True.
    """
    doc_data = load_and_normalize(doc_path)
    cov_data = load_and_normalize(cov_path)
    lint_data = load_and_normalize(lint_path)

    all_keys = set(doc_data) | set(cov_data) | set(lint_data)

    if changed_files:
        all_keys = {
            k for k in all_keys if any(changed_file in k or k in changed_file for changed_file in changed_files)
        }

    include_doc = not task_results or "docstring" in task_results
    include_cov = not task_results or "test" in task_results
    include_lint = not task_results or "lint" in task_results

    merged: Dict[str, Any] = {}
    for key in sorted(all_keys):
        entry = {}
        if include_doc and key in doc_data:
            entry["docstrings"] = doc_data[key]
        if include_cov and key in cov_data:
            coverage_entry = cov_data[key]
            entry["coverage"] = coverage_entry
            if "complexity_score" in coverage_entry:
                entry["complexity_score"] = coverage_entry["complexity_score"]
        if include_lint and key in lint_data:
            entry["linting"] = lint_data[key]

        if entry:
            merged[key] = entry

    output_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
    if verbose:
        print(f"✅ Merged report written with {len(merged)} files to {output_path}")

    if return_data:
        return merged



def main() -> None:
    """
    Main entry point for the script.
    """
    parser = argparse.ArgumentParser(description="Merge audit JSONs with unified normalization.")
    parser.add_argument("--docstrings", required=True, type=Path, help="Path to docstring JSON")
    parser.add_argument("--coverage", required=True, type=Path, help="Path to coverage JSON")
    parser.add_argument("--linting", required=True, type=Path, help="Path to linting JSON")
    parser.add_argument(
        "-o",
        "--output",
        default="final_merged_refactor_report.json",
        type=Path,
        help="Output file path",
    )
    args = parser.parse_args()
    merge_reports(args.docstrings, args.coverage, args.linting, args.output)


if __name__ == "__main__":
    main()
