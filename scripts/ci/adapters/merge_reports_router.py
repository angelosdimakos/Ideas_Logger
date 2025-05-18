#!/usr/bin/env python3
"""
Report Merger Router Adapter
===========================
Adapter for merging reports produced by the CI Router workflow.

This tool intelligently merges the available reports (linting, coverage, docstring)
based on which tasks were executed by the CI Router. It ensures proper report structure
is maintained even when some reports are missing or incomplete.

Usage:
    python merge_reports_router.py --router-report artifacts/router/router_summary.json --output artifacts/merged_report.json
"""

import sys
import argparse
import json
import os
import logging
from pathlib import Path
import tempfile
from typing import Dict, Any, List, Optional, Set

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("MergeReportsRouter")

# Ensure the repo root is on sys.path so we can import project modules
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the report merger adapter."""
    parser = argparse.ArgumentParser(
        description="Merge reports based on CI Router execution."
    )
    parser.add_argument(
        "--router-report",
        required=True,
        help="Path to CI Router report JSON file"
    )
    parser.add_argument(
        "--docstrings",
        help="Path to docstring summary JSON file",
        default="artifacts/docstring-summary/docstring_summary.json"
    )
    parser.add_argument(
        "--coverage",
        help="Path to refactor audit JSON file",
        default="artifacts/refactor-audit/refactor_audit.json"
    )
    parser.add_argument(
        "--linting",
        help="Path to linting report JSON file",
        default="artifacts/lint-report/linting_report.json"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to output merged report JSON file",
        default="artifacts/merged_report.json"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    return parser.parse_args()


def get_router_data(router_report_path: str) -> Dict[str, Any]:
    """
    Extract data from the router report.

    Args:
        router_report_path: Path to the router summary JSON file

    Returns:
        Dictionary with router report data
    """
    try:
        if not os.path.exists(router_report_path):
            logger.warning(f"Router report not found: {router_report_path}")
            return {"task_results": {}, "changed_files": []}

        with open(router_report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing router report: {e}")
        return {"task_results": {}, "changed_files": []}
    except Exception as e:
        logger.error(f"Error reading router report: {e}")
        return {"task_results": {}, "changed_files": []}


def load_json_report(file_path: str, verbose: bool = False) -> Optional[Dict[str, Any]]:
    """
    Load a JSON report file if it exists.

    Args:
        file_path: Path to the JSON file
        verbose: Whether to log verbose details

    Returns:
        Dictionary with report data or None if the file doesn't exist or is invalid
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if verbose:
                    logger.info(f"Loaded report from {file_path} with {len(data)} entries")
                return data
        else:
            logger.warning(f"Report file not found: {file_path}")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading report from {file_path}: {e}")
        return None


def get_changed_file_paths(router_data: Dict[str, Any]) -> Set[str]:
    """
    Extract the set of changed file paths from router data.

    Args:
        router_data: Router report data

    Returns:
        Set of changed file paths
    """
    changed_files = set(router_data.get("changed_files", []))

    # Also extract file paths from task results (might contain more specific detail)
    for task_name, task_result in router_data.get("task_results", {}).items():
        if isinstance(task_result, dict) and "test_files" in task_result:
            changed_files.update(task_result.get("test_files", []))

    return changed_files


def merge_docstring_data(
        merged_report: Dict[str, Dict[str, Any]],
        docstrings_data: Optional[Dict[str, Any]],
        changed_files: Set[str],
        verbose: bool = False
) -> None:
    """
    Merge docstring data into the report.

    Args:
        merged_report: Dictionary to update with merged report data
        docstrings_data: Dictionary with docstring data
        changed_files: Set of changed file paths
        verbose: Whether to log verbose details
    """
    if not docstrings_data:
        if verbose:
            logger.info("No docstring data to merge")
        return

    merged_count = 0
    for file_path, doc_data in docstrings_data.items():
        # Check if this file was changed or we should include all files
        if not changed_files or file_path in changed_files:
            if file_path not in merged_report:
                merged_report[file_path] = {}
            merged_report[file_path]["docstrings"] = doc_data
            merged_count += 1

    if verbose:
        logger.info(f"Merged docstring data for {merged_count} files")


def merge_coverage_data(
        merged_report: Dict[str, Dict[str, Any]],
        coverage_data: Optional[Dict[str, Any]],
        changed_files: Set[str],
        verbose: bool = False
) -> None:
    """
    Merge coverage data into the report.

    Args:
        merged_report: Dictionary to update with merged report data
        coverage_data: Dictionary with coverage data
        changed_files: Set of changed file paths
        verbose: Whether to log verbose details
    """
    if not coverage_data:
        if verbose:
            logger.info("No coverage data to merge")
        return

    merged_count = 0
    for file_path, cov_data in coverage_data.items():
        # Check if this file was changed or we should include all files
        if not changed_files or file_path in changed_files:
            if file_path not in merged_report:
                merged_report[file_path] = {}

            # Handle complexity data
            if "complexity" in cov_data:
                if "complexity" not in merged_report[file_path]:
                    merged_report[file_path]["complexity"] = {}

                merged_report[file_path]["complexity"].update(cov_data["complexity"])

            # Handle complexity score if available
            if "complexity_score" in cov_data:
                merged_report[file_path]["complexity_score"] = cov_data["complexity_score"]

            merged_count += 1

    if verbose:
        logger.info(f"Merged coverage data for {merged_count} files")


def merge_linting_data(
        merged_report: Dict[str, Dict[str, Any]],
        linting_data: Optional[Dict[str, Any]],
        changed_files: Set[str],
        verbose: bool = False
) -> None:
    """
    Merge linting data into the report.

    Args:
        merged_report: Dictionary to update with merged report data
        linting_data: Dictionary with linting data
        changed_files: Set of changed file paths
        verbose: Whether to log verbose details
    """
    if not linting_data:
        if verbose:
            logger.info("No linting data to merge")
        return

    merged_count = 0
    for file_path, lint_data in linting_data.items():
        # Check if this file was changed or we should include all files
        if not changed_files or file_path in changed_files:
            if file_path not in merged_report:
                merged_report[file_path] = {}

            # Add linting data
            if "linting" in lint_data:
                merged_report[file_path]["linting"] = lint_data["linting"]
            else:
                merged_report[file_path]["linting"] = lint_data

            merged_count += 1

    if verbose:
        logger.info(f"Merged linting data for {merged_count} files")


def route_merge_reports(
    router_data: dict,
    doc_path: str,
    cov_path: str,
    lint_path: str,
    verbose: bool = False
) -> dict:
    """
    Routes and conditionally merges audit reports based on router summary.
    """
    from scripts.refactor.merge_audit_reports import merge_reports

    # Determine which tasks ran
    task_results = router_data.get("task_results", {})
    changed_files = set(router_data.get("changed_files", []))

    # Prepare output path (dummy, since we return the result directly)
    import tempfile
    output_path = Path(tempfile.mkdtemp()) / "merged_temp.json"

    merge_reports(
        doc_path=Path(doc_path),
        cov_path=Path(cov_path),
        lint_path=Path(lint_path),
        output_path=output_path,
        changed_files=changed_files,
        task_results=task_results,  # 👈 Critical line
        verbose=verbose
    )

    return json.loads(output_path.read_text(encoding="utf-8"))



def main() -> None:
    """Main entry point for the report merger adapter."""
    args = parse_args()

    # Set log level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Get router data
    router_data = get_router_data(args.router_report)

    # Merge reports based on router data
    merged_report = route_merge_reports(
        router_data,
        args.docstrings,
        args.coverage,
        args.linting,
        args.verbose
    )

    # Create output directory if needed
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Write merged report
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(merged_report, f, indent=2)

    logger.info(f"Merged report written to {args.output}")
    logger.info(f"Included data from {len(merged_report)} files")

    # Return success
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)