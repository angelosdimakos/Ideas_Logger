#!/usr/bin/env python3
"""
Strictness Analysis Router Adapter
=================================
Adapter for running strictness analysis only on tests affected by the changes
identified by the CI Router.

This tool reads the CI Router report and runs strictness analysis only on the
relevant tests, generating a focused report.

Usage:
    python strictness_router.py --router-report artifacts/router/router_summary.json --output artifacts/final_strictness_report.json
"""

import sys
import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Set

# Ensure the repo root is on sys.path so we can import project modules
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

# Import relevant modules from the existing strictness analyzer
from scripts.refactor.strictness_analyzer import (
    load_audit_report,
    load_test_report,
    generate_module_report,
    validate_report_schema
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the strictness router adapter."""
    parser = argparse.ArgumentParser(
        description="Run strictness analysis on tests affected by CI Router changes."
    )
    parser.add_argument(
        "--router-report",
        required=True,
        help="Path to CI Router report JSON file"
    )
    parser.add_argument(
        "--test-report",
        required=True,
        help="Path to test report JSON file"
    )
    parser.add_argument(
        "--audit",
        required=True,
        help="Path to refactor audit JSON file"
    )
    parser.add_argument(
        "--output",
        default="./artifacts/final_strictness_report.json",
        help="Path to output strictness report JSON"
    )
    return parser.parse_args()


def get_affected_modules(router_report_path: str) -> Set[str]:
    """
    Extract the set of Python modules affected by changes in the router report.

    Args:
        router_report_path: Path to the router summary JSON file

    Returns:
        Set of affected module names
    """
    try:
        with open(router_report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        changed_files = report_data.get("changed_files", [])

        # Extract module names from changed files
        affected_modules = set()
        for file_path in changed_files:
            if file_path.endswith(".py"):
                # Extract module name (without extension and directory)
                module_name = Path(file_path).stem
                affected_modules.add(module_name)

                # Also add the directory name as a potential module
                dir_name = Path(file_path).parent.name
                if dir_name and dir_name != ".":
                    affected_modules.add(dir_name)

        return affected_modules
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading router report: {e}")
        return set()


def filter_test_report(test_report: List[Dict[str, Any]], affected_modules: Set[str]) -> List[Dict[str, Any]]:
    """
    Filter the test report to include only tests related to affected modules.

    Args:
        test_report: List of test entries from the test report
        affected_modules: Set of affected module names

    Returns:
        Filtered list of test entries
    """
    filtered_tests = []

    for test_entry in test_report:
        test_name = test_entry.get("name", "")
        test_file = test_entry.get("file", "")

        # Include if the test name or file path contains any affected module name
        if any(module in test_name.lower() or module in test_file.lower() for module in affected_modules):
            filtered_tests.append(test_entry)
            continue

        # If no direct match, check for variations of the module name
        for module in affected_modules:
            # Check for common test naming patterns
            if f"test_{module}" in test_name.lower() or f"{module}_test" in test_name.lower():
                filtered_tests.append(test_entry)
                break

    return filtered_tests


def main() -> None:
    """Main entry point for the strictness router adapter."""
    args = parse_args()

    # Get affected modules from router report
    affected_modules = get_affected_modules(args.router_report)

    if not affected_modules:
        print("No Python modules affected by changes")
        # Create an empty report
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        return

    print(f"Affected modules: {', '.join(affected_modules)}")

    # Load the test report
    test_report = load_test_report(args.test_report)

    # Filter to include only tests related to affected modules
    filtered_tests = filter_test_report(test_report, affected_modules)

    print(f"Found {len(filtered_tests)} tests related to affected modules")

    if not filtered_tests:
        print("No tests to analyze")
        # Create an empty report
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        return

    # Load the audit report
    audit_model = load_audit_report(args.audit)

    # Get test imports (this would need to be extracted from the test report)
    # For simplicity, we're using an empty dict here
    test_imports = {}

    # Generate the module report
    module_report = generate_module_report(audit_model, filtered_tests, test_imports)

    # Validate the report schema
    if not validate_report_schema(module_report):
        print("Warning: Generated report does not match expected schema")

    # Write the report
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(module_report, f, indent=2)

    print(f"Strictness report written to {args.output}")


if __name__ == "__main__":
    main()