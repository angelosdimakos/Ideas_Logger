#!/usr/bin/env python3
"""
Docstring Router Adapter
========================
Adapter for running docstring analysis only on files identified by the CI Router.

This tool reads the CI Router report and analyzes docstrings only for changed
Python files, generating a focused report for better analysis.

Usage:
    python docstring_router.py --router-report artifacts/router/router_summary.json --output docstring_summary.json
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

# Ensure the repo root is on sys.path so we can import project modules
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

# Import the DocstringAnalyzer from the existing docstring parser
from scripts.refactor.parsers.docstring_parser import DocstringAnalyzer, DEFAULT_EXCLUDES


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the docstring router adapter."""
    parser = argparse.ArgumentParser(
        description="Run docstring analysis on files identified by the CI Router."
    )
    parser.add_argument(
        "--router-report",
        required=True,
        help="Path to CI Router report JSON file"
    )
    parser.add_argument(
        "--output",
        default="docstring_summary.json",
        help="Path to save the docstring analysis JSON"
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=list(DEFAULT_EXCLUDES),
        help="Directories to exclude from scan"
    )
    return parser.parse_args()


def get_changed_python_files(router_report_path: str) -> List[str]:
    """
    Extract the list of changed Python files from the router report.

    Args:
        router_report_path: Path to the router summary JSON file

    Returns:
        List of changed Python file paths
    """
    try:
        with open(router_report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        changed_files = report_data.get("changed_files", [])
        # Filter for Python files only, excluding tests
        python_files = [
            f for f in changed_files
            if f.endswith(".py") and "test_" not in f and "/tests/" not in f
        ]
        return python_files
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading router report: {e}")
        return []


def analyze_changed_files(
        changed_files: List[str], analyzer: DocstringAnalyzer
) -> Dict[str, Any]:
    """
    Analyze docstrings in the specified Python files.

    Args:
        changed_files: List of Python file paths to analyze
        analyzer: DocstringAnalyzer instance

    Returns:
        Dictionary mapping file paths to their docstring analysis
    """
    results = {}

    for file_path in changed_files:
        # Create full Path object for the file
        full_path = Path(_PROJECT_ROOT) / file_path

        if full_path.exists() and not analyzer.should_exclude(full_path):
            print(f"Analyzing docstrings in {file_path}")
            try:
                # Extract docstrings from this file
                file_results = analyzer.extract_docstrings(full_path)
                results[file_path] = file_results
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

    return results


def main() -> None:
    """Main entry point for the docstring router adapter."""
    args = parse_args()

    # Initialize the analyzer
    analyzer = DocstringAnalyzer(args.exclude)

    # Get changed files from router report
    changed_files = get_changed_python_files(args.router_report)

    if not changed_files:
        print("No Python files to analyze")
        # Write an empty report
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        return

    print(f"Analyzing docstrings in {len(changed_files)} changed files")

    # Analyze changed files
    results = analyze_changed_files(changed_files, analyzer)

    # Write results
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Docstring analysis written to {args.output}")

    # Check for missing docstrings if requested
    missing_docstrings = any(
        not info["module_doc"]["description"]
        or any(not cls["description"] for cls in info["classes"])
        or any(not fn["description"] for fn in info["functions"])
        for info in results.values()
    )

    if missing_docstrings:
        print("⚠️ Missing docstrings detected in changed files")


if __name__ == "__main__":
    main()