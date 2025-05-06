#!/usr/bin/env python3
"""
merge_audit_reports.py – bespoke normalizer

Merges docstring, coverage/complexity, and linting JSON reports into a unified output.
Uses **custom normalization logic per input source** to ensure accurate matching.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any


def normalize_path(path: str) -> str:
    """Normalize any report path by stripping everything up to and including the project 'scripts' directory
and converting to a forward‑slash relative path."""
    # unify all separators
    normalized = path.replace('\\', '/')
    parts = Path(normalized).parts
    try:
        idx = parts.index('scripts')
        rel_parts = parts[idx + 1:]
    except ValueError:
        # no 'scripts' in path; use as given, but strip leading slashes or drive letters
        rel_parts = parts
    # join with forward slashes
    return '/'.join(rel_parts).lstrip('/')


def load_and_normalize(path: Path) -> Dict[str, Any]:
    """Load JSON and normalize its keys using a common path normalizer."""
    with path.open(encoding='utf-8') as f:
        raw = json.load(f)
    return {normalize_path(k): v for k, v in raw.items()}


def merge_reports(doc_path: Path, cov_path: Path, lint_path: Path, output_path: Path) -> None:
    doc_data = load_and_normalize(doc_path)
    cov_data = load_and_normalize(cov_path)
    lint_data = load_and_normalize(lint_path)

    all_keys = set(doc_data) | set(cov_data) | set(lint_data)
    merged: Dict[str, Any] = {}

    for key in sorted(all_keys):
        merged[key] = {
            'docstrings': doc_data.get(key, {}),
            'coverage': cov_data.get(key, {}),
            'linting': lint_data.get(key, {}),
        }

    output_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"✅ Final merged report written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Merge audit JSONs with unified normalization.")
    parser.add_argument("--docstrings", required=True, type=Path, help="Path to docstring JSON")
    parser.add_argument("--coverage", required=True, type=Path, help="Path to coverage JSON")
    parser.add_argument("--linting", required=True, type=Path, help="Path to linting JSON")
    parser.add_argument(
        "-o", "--output",
        default="final_merged_refactor_report.json",
        type=Path,
        help="Output file path"
    )
    args = parser.parse_args()
    merge_reports(args.docstrings, args.coverage, args.linting, args.output)


if __name__ == "__main__":
    main()
