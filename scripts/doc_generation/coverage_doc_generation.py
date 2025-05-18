#!/usr/bin/env python3
"""
Split-by-Folder Coverage Documentation Generator
===============================================
Creates one Markdown file per folder:
- ai.md, core.md, etc.
Also generates:
- index.md with folder links
"""
from __future__ import annotations

import sys
import argparse
import json
from pathlib import Path
from collections import defaultdict

# ─── make "scripts." imports work when executed as a script ────────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

# Import rendering functions
from scripts.doc_generation.doc_renderers import render_folder_coverage, render_coverage_index


def generate_split_coverage_docs(coverage_data: dict, output_dir: Path):
    """
    Generates Markdown coverage reports for each source folder and an index file.
    
    Groups coverage data by folder (excluding those starting with "tests" or "artifacts"), writes a Markdown report for each folder, and creates an index file summarizing coverage and linking to each folder report.
    """
    grouped = defaultdict(list)
    IGNORED_PREFIXES = ("tests", "artifacts")

    for file_path, file_data in coverage_data.get("files", {}).items():
        folder = Path(file_path).parent.as_posix()

        if any(folder == p or folder.startswith(f"{p}/") for p in IGNORED_PREFIXES):
            continue

        grouped[folder].append((file_path, file_data))

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate individual folder files
    folders = []
    for folder in sorted(grouped):
        safe_name = folder.replace("/", "_")
        output_file = output_dir / f"{safe_name}.md"
        content = render_folder_coverage(folder, grouped[folder])
        output_file.write_text(content, encoding="utf-8")
        folders.append(folder)

    # Write index file
    totals = coverage_data.get("totals", {})
    index_lines = render_coverage_index(folders, totals)
    index_path = output_dir / "index.md"
    index_path.write_text("\n".join(index_lines), encoding="utf-8")

    print(f"✅ Split coverage reports written to: {output_dir}/")


def main():
    """
    Parses command-line arguments and generates folder-based Markdown coverage reports.
    
    Expects paths to a coverage JSON file and an output directory as arguments. Validates
    inputs, loads coverage data, and invokes documentation generation. Exits with an error
    message if the coverage file is missing or invalid.
    """
    parser = argparse.ArgumentParser(description="Generate folder-based coverage documentation.")
    parser.add_argument("--coverage", required=True, help="Path to coverage.json file")
    parser.add_argument("--output", required=True, help="Output folder for markdown reports")

    args = parser.parse_args()

    coverage_path = Path(args.coverage)
    output_dir = Path(args.output)

    if not coverage_path.exists():
        print(f"❌ Coverage file not found at {coverage_path}")
        exit(1)

    try:
        with open(coverage_path, 'r') as f:
            coverage_data = json.load(f)
    except json.JSONDecodeError:
        print("❌ Failed to parse coverage.json.")
        exit(1)

    generate_split_coverage_docs(coverage_data, output_dir)


if __name__ == "__main__":
    main()