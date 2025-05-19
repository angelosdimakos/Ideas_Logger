#!/usr/bin/env python3
"""
Refactor Guard CLI Adapter for CI Router
========================================
This adapter modifies the existing RefactorGuard to work with CI Router output.

It allows RefactorGuard to analyze only files specified in the router report
rather than doing its own git diff analysis.

Usage:
    python refactor_guard_router.py --router-report artifacts/router/router_summary.json --output refactor_audit.json
"""

import sys
import argparse
import json
from pathlib import Path

# Ensure the repo root is on sys.path so we can import project modules
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

# Import the original refactor_guard_cli module
from scripts.refactor.refactor_guard_cli import (
    RefactorGuard,
    print_human_readable,
    _ensure_utf8_stdout,
    handle_single_file
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the router adapter."""
    p = argparse.ArgumentParser(
        prog="refactor_guard_router.py",
        description="Run RefactorGuard on files detected by CI Router"
    )
    p.add_argument("--router-report", required=True, help="Path to CI Router report JSON")
    p.add_argument("--refactored", default="scripts", help="Refactored directory")
    p.add_argument("--tests", default="tests", help="Folder with unit-tests")
    p.add_argument("--coverage-path", default=".coverage", help="Path to coverage DB or JSON")
    p.add_argument("--json", action="store_true", help="Write JSON instead of human output")
    p.add_argument("-o", "--output", default="refactor_audit.json", help="JSON output file")
    return p.parse_args()


def handle_router_based_scan(args: argparse.Namespace, guard: RefactorGuard) -> dict:
    """
    Process files based on CI Router report.

    Args:
        args: Command-line arguments
        guard: RefactorGuard instance

    Returns:
        Dictionary of analysis results
    """
    # Load router report
    try:
        with open(args.router_report, 'r', encoding='utf-8') as f:
            router_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading router report: {e}")
        sys.exit(1)

    # Extract changed files
    changed_files = router_data.get("changed_files", [])

    # Filter Python files
    python_files = [f for f in changed_files if f.endswith(".py")]

    if not python_files:
        print("No Python files to analyze in router report")
        return {}

    ref = args.refactored
    tests = args.tests

    # Process each file
    results = {}
    for file_path in python_files:
        # Skip test files (optional)
        if "test_" in file_path or "/tests/" in file_path:
            continue

        print(f"Analyzing {file_path}...")

        # Find test file path
        test_path = None
        base_name = Path(file_path).name
        if base_name.endswith(".py"):
            test_name = f"test_{base_name}"
            # Look for matching test file
            test_candidates = [
                Path(tests) / test_name,
                Path(tests) / Path(file_path).parent.name / test_name
            ]
            for candidate in test_candidates:
                if candidate.exists():
                    test_path = str(candidate)
                    break

        # Full path to file
        full_path = Path(ref) / file_path if not file_path.startswith(ref) else Path(file_path)

        if full_path.exists():
            # Analyze this specific file
            result = guard.analyze_module("", str(full_path), test_path)
            results[file_path] = result

    # Attach coverage information if available
    if args.coverage_path and Path(args.coverage_path).exists():
        guard.config["coverage_path"] = args.coverage_path
        for file_path, data in results.items():
            try:
                # Update with coverage info
                guard.process_coverage_for_file(str(Path(ref) / file_path), data)
            except Exception as e:
                print(f"⚠️ Coverage processing failed for {file_path}: {e}")

    return results


def main() -> int:
    """Main entry point for the RefactorGuard router adapter."""
    _ensure_utf8_stdout()
    args = parse_args()

    guard = RefactorGuard()
    guard.config["coverage_path"] = args.coverage_path

    # Use the router report to determine which files to process
    audit = handle_router_based_scan(args, guard)

    # Write output
    if args.json:
        Path(args.output).write_text(json.dumps(audit, indent=2), encoding="utf-8")
    else:
        print_human_readable(audit, guard, args)

    return 0


if __name__ == "__main__":
    sys.exit(main())