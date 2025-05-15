from __future__ import annotations

import sys
import argparse
import io
import json
import os
from pathlib import Path
from typing import Any, Dict

# ─── make "scripts." imports work when executed as a script ────────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.refactor.refactor_guard import RefactorGuard, print_human_readable
from scripts.refactor.method_line_ranges import extract_method_line_ranges
from scripts.refactor.parsers.json_coverage_parser import parse_json_coverage
import scripts.utils.git_utils as git_utils

sys.dont_write_bytecode = True  # avoid __pycache__ issues in CI


def _ensure_utf8_stdout() -> None:
    if os.getenv("PYTEST_CURRENT_TEST"):
        return
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        pass


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="refactor_guard_cli.py", description="Audit Python refactors and enrich reports."
    )
    p.add_argument("--original", default="", help="Original file / dir (for diff)")
    p.add_argument("--refactored", required=True, help="Refactored file / dir")
    p.add_argument("--tests", default="", help="Folder with unit-tests")
    p.add_argument("--all", action="store_true", help="Recurse through directories")
    p.add_argument("--git-diff", action="store_true", help="Analyse only Git-changed files")
    p.add_argument("--diff-only", action="store_true", help="Drop complexity section in JSON")
    p.add_argument("--missing-tests", action="store_true", help="Only show missing tests")
    p.add_argument("--complexity-warnings", action="store_true", help="Only show high complexity")
    p.add_argument(
        "--coverage-by-basename", action="store_true", help="Key coverage hits by basename"
    )
    p.add_argument("--coverage-path", default=".coverage", help="Path to coverage DB or JSON")
    p.add_argument("--json", action="store_true", help="Write JSON instead of human output")
    p.add_argument("-o", "--output", default="refactor_audit.json", help="JSON output file")
    return p.parse_args()


def _merge_coverage(summary: dict, ref: str, args: argparse.Namespace) -> None:
    if not os.path.exists(args.coverage_path):
        return

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
            ch = parse_json_coverage(args.coverage_path, mr, filepath=src_path)
            ch = next(iter(ch.values())) if len(ch) == 1 else ch
            if args.coverage_by_basename:
                ch = {os.path.basename(k): v for k, v in ch.items()}
            for method_name, method_info in data.get("complexity", {}).items():
                cov = ch.get(method_name, {})
                method_info.update(
                    {
                        "coverage": cov.get("coverage", "N/A"),
                        "hits": cov.get("hits", "N/A"),
                        "lines": cov.get("lines", "N/A"),
                        "covered_lines": cov.get("covered_lines", []),
                        "missing_lines": cov.get("missing_lines", []),
                    }
                )
        except Exception as e:
            print(f"⚠️  Coverage parsing failed for {basename}: {e}")


def handle_full_scan(args: argparse.Namespace, guard: RefactorGuard) -> Dict[str, Dict[str, Any]]:
    orig = args.original or "scripts"
    ref = args.refactored
    tests = args.tests or None

    if not os.path.isdir(orig) and os.path.isdir(ref):
        orig = ref

    if args.git_diff:
        raw = {
            rel: guard.analyze_module(os.path.join(orig, rel), os.path.join(ref, rel), None)
            for rel in git_utils.get_changed_files("origin/main")
            if rel.endswith(".py") and os.path.exists(os.path.join(ref, rel))
        }
    else:
        raw = guard.analyze_directory_recursive(orig, ref, test_dir=tests)

    summary = {path.replace("\\", "/"): info for path, info in raw.items()}
    _merge_coverage(summary, ref, args)
    return summary


def handle_single_file(args: argparse.Namespace, guard: RefactorGuard) -> Dict[str, Dict[str, Any]]:
    if args.original and not os.path.exists(args.original):
        print(f"⚠️ Original file not found: {args.original}")
        args.original = ""

    if not os.path.exists(args.refactored):
        raise ValueError(f"Expected file for --refactored, got: {args.refactored}")

    try:
        mr = extract_method_line_ranges(args.refactored)
        ch = parse_json_coverage(args.coverage_path, mr, filepath=args.refactored)
        ch = next(iter(ch.values())) if len(ch) == 1 else ch
        if args.coverage_by_basename:
            ch = {os.path.basename(k): v for k, v in ch.items()}
        guard.attach_coverage_hits(ch)
    except Exception as e:
        print(f"⚠️  Coverage parsing failed, continuing without coverage: {e}")

    tf = args.tests or None
    res = guard.analyze_module(args.original, args.refactored, test_file_path=tf)
    return {os.path.basename(args.refactored): res}


def main() -> int:
    _ensure_utf8_stdout()
    args = _parse_args()
    guard = RefactorGuard()
    guard.config["coverage_path"] = args.coverage_path

    if os.getenv("MAX_COMPLEXITY"):
        try:
            guard.config["max_complexity"] = int(os.getenv("MAX_COMPLEXITY"))
        except ValueError:
            pass

    audit = (
        handle_full_scan(args, guard)
        if (args.all or os.path.isdir(args.refactored))
        else handle_single_file(args, guard)
    )

    if args.json:
        if args.diff_only:
            for v in audit.values():
                v["complexity"] = {}
        Path(args.output).write_text(json.dumps(audit, indent=2), encoding="utf-8")
        return 0

    print_human_readable(audit, guard, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
