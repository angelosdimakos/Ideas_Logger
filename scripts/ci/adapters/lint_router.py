#!/usr/bin/env python3
"""
Linting Router Adapter
======================
Adapter for running linting tools only on files identified by the CI Router.

This tool reads the CI Router report and runs linting checks only on changed
Python files, generating a filtered report for better analysis.

Usage:
    python lint_router.py --router-report artifacts/router/router_summary.json --output linting_report.json
"""

import sys
import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Any

# Ensure the repo root is on sys.path so we can import project modules
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

# Import relevant modules from the existing linting tools
from scripts.refactor.lint_report_pkg.helpers import safe_print
import scripts.refactor.lint_report_pkg.quality_checker as quality_checker


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the linting router adapter."""
    parser = argparse.ArgumentParser(
        description="Run linting checks on files identified by CI Router.",
    )
    parser.add_argument(
        "--router-report",
        required=True,
        help="Path to CI Router report JSON file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="linting_report.json",
        help="Path to output lint report JSON file",
    )
    parser.add_argument(
        "--all-tools",
        action="store_true",
        help="Run all linting tools, not just the minimal set",
    )
    return parser.parse_args()


def get_changed_files(router_report_path: str) -> List[str]:
    """
    Extract the list of changed files from the router report.

    Args:
        router_report_path: Path to the router summary JSON file

    Returns:
        List of changed file paths
    """
    try:
        with open(router_report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        changed_files = report_data.get("changed_files", [])
        # Filter for Python files only
        python_files = [f for f in changed_files if f.endswith(".py")]
        return python_files
    except (FileNotFoundError, json.JSONDecodeError) as e:
        safe_print(f"[!] Error reading router report: {e}")
        return []


def create_targeted_lint_config(python_files: List[str]) -> Dict[str, Any]:
    """
    Create a configuration for running specific linting tools on selected files.

    Args:
        python_files: List of Python files to lint

    Returns:
        Configuration dictionary for the linting tools
    """
    # Map filepaths to "module_name": file_path for the linting tools
    file_map = {}
    for file_path in python_files:
        module_name = Path(file_path).stem
        file_map[module_name] = file_path

    return {
        "files": file_map,
        "tools": {
            "pylint": {"enabled": True},
            "pydocstyle": {"enabled": True},
            "mypy": {"enabled": True},
            "flake8": {"enabled": True}
        }
    }


def run_targeted_linting(python_files: List[str], output_path: str, all_tools: bool) -> None:
    """
    Run targeted linting on the specified Python files.

    Args:
        python_files: List of Python files to lint
        output_path: Path to write the lint report
        all_tools: Whether to run all linting tools or just a minimal set
    """
    if not python_files:
        safe_print("[!] No Python files to lint")
        # Create an empty report
        Path(output_path).write_text("{}", encoding="utf-8")
        return

    safe_print(f"[+] Running targeted linting on {len(python_files)} files")

    # Create the file filter for merge_into_refactor_guard
    file_filter = {}
    for file_path in python_files:
        module_name = Path(file_path).stem
        file_filter[module_name] = file_path

    # Run merge_into_refactor_guard with file filtering
    quality_checker.merge_into_refactor_guard(output_path, file_filter)

    # The function above will have already written the output file,
    # so we're done!
    safe_print(f"[✓] Lint report written to {output_path}")


def main() -> None:
    """Main entry point for the linting router adapter."""
    args = parse_args()

    # Get changed files from router report
    python_files = get_changed_files(args.router_report)

    # Run targeted linting
    run_targeted_linting(python_files, args.output, args.all_tools)


if __name__ == "__main__":
    main()