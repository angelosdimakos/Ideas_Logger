#!/usr/bin/env python3
"""
Test Router Adapter
==================
Adapter for running pytest only on tests affected by changes identified by the CI Router.

This tool reads the CI Router report and determines which tests to run based on:
1. Direct file changes - test files that were modified
2. Implementation changes - tests for modules that were modified
3. Dependency changes - tests that depend on modules that were modified

Usage:
    python test_router.py --router-report artifacts/router/router_summary.json --output artifacts/router/test_results.json
"""

import sys
import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Any

# Ensure the repo root is on sys.path so we can import project modules
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the test router adapter."""
    parser = argparse.ArgumentParser(
        description="Run tests affected by changes identified by the CI Router."
    )
    parser.add_argument(
        "--router-report",
        required=True,
        help="Path to CI Router report JSON file"
    )
    parser.add_argument(
        "--test-dir",
        default="tests",
        help="Directory containing tests"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage"
    )
    parser.add_argument(
        "--output",
        default="artifacts/router/test_results.json",
        help="Path to output test results JSON"
    )
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="Only collect tests, don't run them"
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

        return report_data.get("changed_files", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading router report: {e}")
        return []


def find_affected_test_files(
        changed_files: List[str], test_dir: str
) -> Set[str]:
    """
    Determine which test files are affected by the changed files.

    Args:
        changed_files: List of changed file paths
        test_dir: Directory containing tests

    Returns:
        Set of test file paths to run
    """
    affected_tests = set()
    test_dir_path = Path(test_dir)

    # Helper function to normalize module names
    def normalize_name(path: str) -> str:
        return Path(path).stem.replace("test_", "")

    # Helper function to normalize paths for platform independence
    def normalize_path(path: Path) -> str:
        # Convert to string and ensure forward slashes for consistency
        return str(path).replace('\\', '/')

    # 1. Direct test file changes
    for file_path in changed_files:
        if file_path.endswith(".py") and (
                "test_" in file_path or "/tests/" in file_path
        ):
            # Normalize the path before adding
            affected_tests.add(file_path.replace('\\', '/'))

    # 2. Find tests for changed modules
    for file_path in changed_files:
        if not file_path.endswith(".py") or "test_" in file_path:
            continue

        # Module name without extension
        module_name = normalize_name(file_path)

        # Pattern 1: test_modulename.py
        test_file = test_dir_path / f"test_{module_name}.py"
        if test_file.exists():
            # Use normalize_path for consistent path format
            relative_path = test_file.relative_to(_PROJECT_ROOT)
            affected_tests.add(normalize_path(relative_path))

        # Pattern 2: tests/component/test_modulename.py
        for test_file in test_dir_path.glob(f"*/test_{module_name}.py"):
            # Use normalize_path for consistent path format
            relative_path = test_file.relative_to(_PROJECT_ROOT)
            affected_tests.add(normalize_path(relative_path))

        # Pattern 3: tests/modulename/test_*.py (any tests in module directory)
        module_dir = test_dir_path / module_name
        if module_dir.is_dir():
            for test_file in module_dir.glob("test_*.py"):
                # Use normalize_path for consistent path format
                relative_path = test_file.relative_to(_PROJECT_ROOT)
                affected_tests.add(normalize_path(relative_path))

    # 3. Look for tests that import changed modules (more complex)
    # This would require parsing imports in test files
    # For simplicity, we're skipping this step, but it could be added

    return affected_tests


def run_pytest(
        test_files: Set[str],
        coverage: bool = False,
        collect_only: bool = False
) -> Dict[str, Any]:
    """
    Run pytest on the specified test files.

    Args:
        test_files: Set of test file paths to run
        coverage: Whether to run with coverage
        collect_only: Whether to only collect tests without running them

    Returns:
        Dictionary with test results
    """
    if not test_files:
        print("No tests to run")
        return {"status": "skipped", "reason": "No tests to run"}

    # Convert to list for command line
    test_paths = list(test_files)
    print(f"Running {len(test_paths)} test files")

    # Build pytest command
    cmd = ["pytest", "-v"]

    if collect_only:
        cmd.append("--collect-only")

    if coverage:
        cmd.extend([
            "--cov=scripts",
            "--cov-config=.coveragerc",
            "--cov-report=term",
            "--cov-report=json:artifacts/router/coverage.json"
        ])

    # Add test paths
    cmd.extend(test_paths)

    print(f"Running command: {' '.join(cmd)}")

    try:
        # Run pytest
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        # Prepare results
        results = {
            "status": "success" if process.returncode == 0 else "failure",
            "return_code": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "test_files": list(test_files)
        }

        # Check for coverage report
        if coverage and os.path.exists("artifacts/router/coverage.json"):
            try:
                with open("artifacts/router/coverage.json", 'r') as f:
                    coverage_data = json.load(f)
                results["coverage"] = {
                    "total": coverage_data.get("totals", {}).get("percent_covered", 0),
                    "path": "artifacts/router/coverage.json"
                }
            except Exception as e:
                print(f"Error reading coverage data: {e}")

        return results
    except Exception as e:
        print(f"Error running pytest: {e}")
        return {"status": "error", "error": str(e)}


def main() -> None:
    """Main entry point for the test router adapter."""
    args = parse_args()

    # Get changed files from router report
    changed_files = get_changed_files(args.router_report)

    if not changed_files:
        print("No files changed")
        return

    # Find affected test files
    test_files = find_affected_test_files(changed_files, args.test_dir)

    # Set up output directory
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    if args.collect_only:
        # Just show which tests would be run
        results = {
            "status": "collected",
            "test_files": list(test_files)
        }
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Would run {len(test_files)} test files:")
        for test_file in sorted(test_files):
            print(f"  {test_file}")
    else:
        # Run the tests
        results = run_pytest(test_files, args.coverage)

        # Write results
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        print(f"Test results written to {args.output}")

        # Exit with appropriate code
        if results["status"] != "success":
            sys.exit(1)


if __name__ == "__main__":
    main()