#!/usr/bin/env python3
"""
RefactorGuard CLI – audit Python refactors from the command line.

Core features
─────────────
* directory-wide or single-file analysis
* Git-diff-only mode
* merge / enrich existing JSON reports
* optional coverage integration
"""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True  # avoid __pycache__ PermissionErrors in CI

import argparse
import io
import json
import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict

# ─── make “scripts.” imports work when executed as a script ────────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.refactor.refactor_guard import RefactorGuard, print_human_readable
from scripts.refactor.method_line_ranges import extract_method_line_ranges
from scripts.refactor.parsers.coverage_parser import parse_coverage_xml_to_method_hits
import scripts.utils.git_utils as git_utils  # noqa:  E402  (late import ok)

# ───────────────────────────────────────────────────────────────────────────
# utility
# ───────────────────────────────────────────────────────────────────────────
def _ensure_utf8_stdout() -> None:
    """
    Force UTF-8 stdout on *interactive* consoles / CI logs.

    Skipped automatically when running under Pytest (because the capture
    plugin already monkey-patches ``sys.stdout``).
    """
    if os.getenv("PYTEST_CURRENT_TEST"):
        return  # pytest capture in progress – leave streams alone
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        else:  # Py < 3.7
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        # Never crash just for logging – swallow anything unexpected
        pass


# ───────────────────────────────────────────────────────────────────────────
# CLI parsing helpers
# ───────────────────────────────────────────────────────────────────────────
def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="refactor_guard_cli.py",
                                description="Audit Python refactors and enrich reports.")
    p.add_argument("--original", default="", help="Original file / dir (for diff)")
    p.add_argument("--refactored", required=True, help="Refactored file / dir")
    p.add_argument("--tests", default="", help="Folder with unit-tests")
    p.add_argument("--coverage-xml", default="coverage.xml", help="Path to coverage.xml")
    p.add_argument("--all", action="store_true", help="Recurse through directories")
    p.add_argument("--git-diff", action="store_true", help="Analyse only Git-changed files")
    p.add_argument("--diff-only", action="store_true", help="Drop complexity section in JSON")
    p.add_argument("--missing-tests", action="store_true", help="Only show missing tests")
    p.add_argument("--complexity-warnings", action="store_true", help="Only show high complexity")
    p.add_argument("--coverage-by-basename", action="store_true",
                   help="Key coverage hits by basename")
    p.add_argument("--json", action="store_true", help="Write JSON instead of human output")
    p.add_argument("-o", "--output", default="refactor_audit.json", help="JSON output file")

    return p.parse_args()





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
        norm_path = path.replace("\\", "/")  # Normalize for consistency
        summary[norm_path] = info

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


def main() -> int:  # noqa: C901  (complexity irrelevant for CLI wrapper)
    _ensure_utf8_stdout()        # ← moved here (= after Pytest capture)
    args = _parse_args()
    guard = RefactorGuard()

    # env override for CI scripts
    if os.getenv("MAX_COMPLEXITY"):
        try:
            guard.config["max_complexity"] = int(os.getenv("MAX_COMPLEXITY"))
        except ValueError:
            pass

    # 1) merge mode short-circuit

    # 2) choose scan mode
    if args.all or os.path.isdir(args.refactored):
        audit = handle_full_scan(args, guard)
    else:
        audit = handle_single_file(args, guard)

    # 3) emit report
    if args.json:
        if args.diff_only:
            for v in audit.values():
                v["complexity"] = {}
        Path(args.output).write_text(json.dumps(audit, indent=2), encoding="utf-8")
        return 0  # ← explicit success exit code

    print_human_readable(audit, guard, args)
    return 0  # ← also explicit

if __name__ == "__main__":
    sys.exit(main())
