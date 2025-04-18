import argparse
import os
import sys
import io
import json
import xml.etree.ElementTree as ET

# 👇 Add parent of 'scripts' to sys.path to avoid import errors when run as a module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Force UTF-8 stdout if possible (safe fallback for CI)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

import scripts.utils.git_utils as git_utils
from scripts.refactor.refactor_guard import RefactorGuard
from scripts.refactor.coverage_parser import parse_coverage_xml_to_method_hits
from scripts.refactor.method_line_ranges import extract_method_line_ranges


def safe_collect_method_ranges(path: str) -> dict:
    """Recursively collect all method ranges from .py files under path."""
    method_ranges = {}
    if os.path.isfile(path):
        method_ranges = extract_method_line_ranges(path)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in files:
                if f.endswith(".py"):
                    full_path = os.path.join(root, f)
                    try:
                        method_ranges.update(extract_method_line_ranges(full_path))
                    except Exception as e:
                        print(f"⚠️ Failed to parse {full_path}: {e}")
    return method_ranges


def handle_json_output(summary, output_name, out_dir=None):
    filename = f"{output_name}.json"
    path = os.path.join(out_dir or ".", filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\n📌 Saved audit report to {path}")
    total_methods = sum(len(v.get("complexity", {})) for v in summary.values())
    print(f"🧠 Methods analyzed: {total_methods}")
    print(f"🔧 Files changed: {len(summary)}")


def print_method_stats(method_complexities, guard):
    """Print the complexity and coverage for each method in human‑readable form."""
    total_complexity = sum(
        (v["complexity"] if isinstance(v, dict) else v)
        for v in method_complexities.values()
    )
    print(f"📊 Total Complexity: {total_complexity}")
    print("📊 Method Complexity & Coverage:")
    for method, stats in method_complexities.items():
        if isinstance(stats, dict):
            emoji = "⚠️" if stats["complexity"] > guard.config.get("max_complexity", 10) else "✅"
            cov = stats.get("coverage")
            cov_str = f"{cov*100:.1f}%" if isinstance(cov, float) else "N/A"
            hits = stats.get("hits", "N/A")
            lines = stats.get("lines", "N/A")
            print(f"  {emoji} {method} | Complexity: {stats['complexity']} | Coverage: {cov_str} ({hits}/{lines})")
        else:
            emoji = "⚠️" if stats > guard.config.get("max_complexity", 10) else "✅"
            print(f"  {emoji} {method}: {stats}")


def print_summary(summary, guard, args):
    """Print the per‑file summaries."""
    for fname, data in summary.items():
        print(f"\n📂 File: {fname}")
        if not args.diff_only:
            print_method_stats(data.get("complexity", {}), guard)


def parse_args():
    p = argparse.ArgumentParser(description="RefactorGuard CLI: Audit Python refactors.")
    p.add_argument("--original",   type=str, default="", help="Original file/dir")
    p.add_argument("--refactored", type=str, required=True, help="Refactored file/dir")
    p.add_argument("--tests",      type=str, help="Optional test file or dir to check for missing tests")
    p.add_argument("--all",        action="store_true", help="Audit entire scripts dir")
    p.add_argument("--diff-only",  action="store_true", help="Ignore complexity checks")
    p.add_argument("--missing-tests", action="store_true", help="List methods lacking tests")
    p.add_argument("--complexity-warnings", action="store_true", help="Show complexity warnings")
    p.add_argument("--json",       action="store_true", help="Export result as structured JSON")
    p.add_argument("--git-diff",   action="store_true", help="Analyze only Git‑changed files")
    return p.parse_args()


def dispatch_mode(args, guard):
    if args.all:
        return handle_full_scan(args, guard)
    return handle_single_file(args, guard)


def handle_full_scan(args, guard):
    original   = args.original or "scripts"
    refactored = args.refactored or "scripts"
    if args.git_diff:
        summary = {}
        for file in git_utils.get_changed_files("origin/main"):
            orig = os.path.join(original, file)
            refa = os.path.join(refactored, file)
            if os.path.exists(refa):
                summary[file] = guard.analyze_module(orig, refa, test_file_path=None)
        return summary
    return guard.analyze_directory_recursive(original, refactored, test_dir=args.tests)


def handle_single_file(args, guard):
    if not os.path.isfile(args.original):
        raise ValueError(f"[handle_single_file] Expected a file for --original, got: {args.original}")
    if not os.path.isfile(args.refactored):
        raise ValueError(f"[handle_single_file] Expected a file for --refactored, got: {args.refactored}")
    summary = guard.analyze_module(args.original, args.refactored, test_file_path=args.tests)
    fname = os.path.basename(args.refactored)
    # Emit the same shape as full-scan: filename → summary dict
    return {fname: summary}


def handle_output(result, args, guard):
    # JSON mode: result is always { filename: summary_dict }
    if args.json:
        # In JSON mode, if --diff-only is set, drop complexity entirely
        if args.diff_only:
            for file_summary in result.values():
                file_summary["complexity"] = {}
        handle_json_output(result, "refactor_audit")
        return

    # non‑JSON mode: print human summary
    print_summary(result, guard, args)

    if args.missing_tests:
        print("\n🧪 Missing Tests:")
        for _, data in result.items():
            for m in data.get("missing_tests", []):
                print(f"❌ {m['class']} → {m['method']}")

    if args.complexity_warnings:
        print("\n⚠️ Complexity Warnings:")
        for _, data in result.items():
            for method, stats in data.get("complexity", {}).items():
                score = stats["complexity"] if isinstance(stats, dict) else stats
                if score > guard.config.get("max_complexity", 10):
                    print(f"  ⚠️ {method}: {score}")


def main():
    args = parse_args()
    guard = RefactorGuard()

    # Allow MAX_COMPLEXITY override via environment
    max_env = os.getenv("MAX_COMPLEXITY")
    if max_env is not None:
        try:
            guard.config["max_complexity"] = int(max_env)
        except ValueError:
            pass

    # PRELOAD coverage hits with the correct signature
    mr = safe_collect_method_ranges(args.refactored)
    try:
        ch = parse_coverage_xml_to_method_hits("coverage.xml", mr, source_file_path=args.refactored)
        guard.coverage_hits = ch
    except (FileNotFoundError, ET.ParseError) as e:
        print(f"⚠️  Coverage parsing failed, continuing without coverage: {e}")

    result = dispatch_mode(args, guard)
    handle_output(result, args, guard)

    # exit(0) in JSON mode so tests expecting SystemExit pass
    if args.json:
        sys.exit(0)


if __name__ == "__main__":
    main()
