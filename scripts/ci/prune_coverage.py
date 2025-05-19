#!/usr/bin/env python3
"""
Prune coverage.json to include only specified files.

This script filters a coverage.json file to only include entries for
files that were changed in the current PR/commit, and additionally
removes entries with zero coverage.

Usage:
  python scripts/ci/prune_coverage.py coverage.json cleaned_coverage.json [--only-changed]
"""
import sys
import json
import argparse
import os
from pathlib import Path


def prune_coverage(input_path, output_path, only_changed=False):
    """
    Prune the coverage.json file.

    Args:
        input_path: Path to the input coverage.json file
        output_path: Path to the output coverage.json file
        only_changed: If True, only include files that were changed
    """
    with open(input_path, 'r') as f:
        data = json.load(f)

    # Get the list of changed files from environment variables if available
    changed_files = []
    if only_changed and "CHANGED_FILES" in os.environ:
        changed_files = os.environ["CHANGED_FILES"].split()
        print(f"Filtering coverage to only include {len(changed_files)} changed files")

    if "files" in data:
        # Filter out files with zero coverage
        if changed_files:
            # Only include files that were changed and have coverage
            data["files"] = {
                k: v for k, v in data["files"].items()
                if v["summary"].get("covered_lines", 0) > 0 and
                   any(k.endswith(file) for file in changed_files)
            }
        else:
            # Include all files with coverage
            data["files"] = {
                k: v for k, v in data["files"].items()
                if v["summary"].get("covered_lines", 0) > 0
            }

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Trimmed coverage.json → {output_path}")
    print(f"   - Entries remaining: {len(data.get('files', {}))}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prune coverage.json file")
    parser.add_argument("input", help="Input coverage.json file")
    parser.add_argument("output", help="Output coverage.json file")
    parser.add_argument("--only-changed", action="store_true",
                        help="Only include files that were changed")

    args = parser.parse_args()
    prune_coverage(args.input, args.output, args.only_changed)