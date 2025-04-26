#!/usr/bin/env python3
"""
refactor_guard_cli.py

This module provides the command-line interface (CLI) for RefactorGuard, a tool for auditing Python code refactors.

Core features include:
- Parsing command-line arguments to configure audit behavior, including file/directory selection, coverage integration, and output options.
- Supporting both single-file and recursive directory analysis modes.
- Integrating with Git to restrict audits to changed files.
- Merging and enriching audit reports with code quality and coverage data.
- Outputting results in both JSON and human-readable formats, with filtering for diffs, missing tests, and complexity warnings.
- Handling coverage XML parsing and per-method coverage enrichment.

Intended for use as a standalone CLI tool or in CI pipelines to automate code quality and test coverage audits during refactoring.
"""
import sys

# ─── Disable all .pyc / __pycache__ writes to avoid PermissionErrors ──────────
sys.dont_write_bytecode = True

import argparse
import os
import io
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any

# allow importing from project root
toplevel = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, toplevel)

from scripts.refactor.refactor_guard import RefactorGuard, print_human_readable
from scripts.refactor.method_line_ranges import extract_method_line_ranges
from scripts.refactor.parsers.coverage_parser import parse_coverage_xml_to_method_hits
import scripts.utils.git_utils as git_utils  # <-- dynamic import
from scripts.refactor.enrich_refactor_pkg.quality_checker import merge_reports, merge_into_refactor_guard

# enforce UTF-8 stdout for CI environments
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass


def parse_args() -> argparse.Namespace:
    """
    Parses command-line arguments for the RefactorGuard CLI.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    p = argparse.ArgumentParser(description="RefactorGuard CLI: Audit Python refactors.")
    p.add_argument("--original", type=str, default="", help="Original file or directory")
    p.add_argument("--refactored", type=str, required=True, help="Refactored file or directory")
    p.add_argument("--coverage-xml", type=str, default="coverage.xml", help="Path to coverage.xml")
    p.add_argument("--tests", type=str, default="", help="Test file or directory")
    p.add_argument("--all", action="store_true", help="Scan entire directory recursively")
    p.add_argument("--diff-only", action="store_true", help="Only method diffs")
    p.add_argument("--missing-tests", action="store_true", help="Only missing tests")
    p.add_argument("--complexity-warnings", action="store_true", help="Only complexity warnings")
    p.add_argument(
        "--coverage-by-basename",
        action="store_true",
        help="Use basename as key for coverage enrich",
    )
    p.add_argument(
        "--merge",
        nargs=3,
        metavar=("SRC1", "SRC2", "DEST"),
        help="Merge two audits (or enrich audit with reports)",
    )
    p.add_argument("--json", action="store_true", help="Output JSON")
    p.add_argument("--git-diff", action="store_true", help="Restrict to git-changed files")
    p.add_argument(
        "-o", "--output", type=str, default="refactor_audit.json", help="JSON output path"
    )
    return p.parse_args()


def handle_merge(args: argparse.Namespace) -> None:
    """
    Handles the merging of audit reports based on the provided arguments.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    src1, src2, dest = args.merge
    if os.path.isfile(src2) and src2.lower().endswith(".json"):
        merged = merge_reports(src1, src2)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2)
    elif os.path.isdir(src2):
        shutil.copy(src1, dest)
        report_dir = Path(src2)
        report_paths = {
            "black": report_dir / "black.txt",
            "flake8": report_dir / "flake8.txt",
            "mypy": report_dir / "mypy.txt",
            "pydocstyle": report_dir / "pydocstyle.txt",
            "coverage": report_dir / "coverage.xml",
        }
        merge_into_refactor_guard(dest, report_paths=report_paths)
    else:
        raise ValueError(f"Cannot merge from {src2}: not JSON or report dir")

    print(f"[OK] Merged audits into {dest}")
    sys.exit(0)


def handle_full_scan(args: argparse.Namespace, guard: RefactorGuard) -> Dict[str, Dict[str, Any]]:
    """
    Performs a full scan of the specified directories or files.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
        guard (RefactorGuard): An instance of the RefactorGuard class for auditing.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary containing the audit results.
    """
    orig = args.original or "scripts"
    ref = args.refactored
    tests = args.tests or None

    if not os.path.isdir(orig) and os.path.isdir(ref):
        orig = ref
    # 1) Gather changed files (or do a full recursive scan)
    if args.git_diff:
        raw: Dict[str, Dict[str, Any]] = {}
        for rel in git_utils.get_changed_files("origin/main"):
            if not rel.endswith(".py"):
                continue
            o = os.path.join(orig, rel)
            r = os.path.join(ref, rel)
            if os.path.exists(r):
                raw[rel] = guard.analyze_module(o, r, test_file_path=None)
    else:
        raw = guard.analyze_directory_recursive(orig, ref, test_dir=tests)

    # 2) Normalize keys down to basenames
    summary = {}
    for path, info in raw.items():
        basename = os.path.basename(path)
        summary[basename] = info

    # 3) Inject coverage per file (if coverage.xml exists)
    if os.path.exists(args.coverage_xml):
        for basename, data in summary.items():
            src_path = os.path.join(ref, basename)
            if not os.path.exists(src_path):
                for root, _, files in os.walk(ref):
                    if basename in files:
                        src_path = os.path.join(root, basename)
                        break
            if not os.path.exists(src_path):
                continue
            try:
                mr = extract_method_line_ranges(src_path)
                ch = parse_coverage_xml_to_method_hits(
                    args.coverage_xml, mr, source_file_path=src_path
                )
                if args.coverage_by_basename:
                    ch = {os.path.basename(k): v for k, v in ch.items()}
                for method_name, method_info in data.get("complexity", {}).items():
                    cov = ch.get(method_name, {})
                    method_info["coverage"] = cov.get("coverage", "N/A")
                    method_info["hits"] = cov.get("hits", "N/A")
                    method_info["lines"] = cov.get("lines", "N/A")
            except (FileNotFoundError, ET.ParseError) as e:
                print(f"⚠️  Coverage parsing failed for {basename}: {e}")
                continue

    return summary


def handle_single_file(args: argparse.Namespace, guard: RefactorGuard) -> Dict[str, Dict[str, Any]]:
    """
    Handles the analysis of a single file for auditing.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
        guard (RefactorGuard): An instance of the RefactorGuard class for auditing.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary containing the audit results.
    """
    if args.original and not os.path.exists(args.original):
        print(f"⚠️ Original file not found: {args.original}")
        args.original = ""

    if not os.path.exists(args.refactored):
        raise ValueError(f"Expected file for --refactored, got: {args.refactored}")

    try:
        mr = extract_method_line_ranges(args.refactored)
        ch = parse_coverage_xml_to_method_hits(
            args.coverage_xml, mr, source_file_path=args.refactored
        )
        if args.coverage_by_basename:
            ch = {os.path.basename(k): v for k, v in ch.items()}
        guard.attach_coverage_hits(ch)
    except (FileNotFoundError, ET.ParseError) as e:
        print(f"⚠️  Coverage parsing failed, continuing without coverage: {e}")

    tf = args.tests or None
    res = guard.analyze_module(args.original, args.refactored, test_file_path=tf)
    basename = os.path.basename(args.refactored)
    return {basename: res}


def main() -> None:
    """
    Main entry point for the RefactorGuard CLI.

    This function orchestrates the command-line interface operations, including
    parsing arguments and executing the appropriate audit functions.
    """
    args = parse_args()
    guard = RefactorGuard()

    # Override max complexity from environment, if set
    if os.getenv("MAX_COMPLEXITY"):
        try:
            guard.config["max_complexity"] = int(os.getenv("MAX_COMPLEXITY"))
        except ValueError:
            pass

    # Handle merge mode first
    if args.merge:
        handle_merge(args)

    # Choose scan mode: full directory scan if --all or refactored is a directory,
    # otherwise single‐file mode
    if args.all or os.path.isdir(args.refactored):
        audit = handle_full_scan(args, guard)
    else:
        audit = handle_single_file(args, guard)

    # JSON output mode
    if args.json:
        if args.diff_only:
            for info in audit.values():
                info["complexity"] = {}
        with open(args.output, "w", encoding="utf-8") as out:
            json.dump(audit, out, indent=2)
        merge_into_refactor_guard(args.output)
        sys.exit(0)

    # Human‑readable output
    print_human_readable(audit, guard, args)


if __name__ == "__main__":
    main()
