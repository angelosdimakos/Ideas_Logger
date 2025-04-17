import argparse
import os
import sys
import json

# 👇 Add parent of 'scripts' to sys.path to avoid import errors
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import io
import xml.etree.ElementTree as ET

# Force UTF-8 stdout if possible (safe fallback for CI)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass  # Silently ignore for CI environments

from scripts.utils.git_utils import get_changed_files
from scripts.refactor.refactor_guard import RefactorGuard
from scripts.refactor.coverage_parser import parse_coverage_xml_to_method_hits
from scripts.refactor.method_line_ranges import extract_method_line_ranges


def safe_collect_method_ranges(path: str) -> dict:
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


def handle_json_output(summary, output_name):
    filename = f"{output_name}.json"
    with open(filename, "w", encoding="utf-8-sig") as f:
        json.dump(summary, f, indent=2)
    print(f"\n📌 Saved audit report to {filename}")

    for method, data in summary.get("complexity", {}).items():
        print(f"Method: {method}, Coverage: {data.get('coverage', 'N/A')}")

    method_count = sum(len(v.get("complexity", {})) for v in summary.values())
    print(f"🧠 Methods analyzed: {method_count}")
    print(f"🔧 Files changed: {len(summary)}")


def print_method_stats(method_complexities, guard):
    if all(isinstance(v, dict) and "complexity" in v for v in method_complexities.values()):
        total_complexity = sum(v["complexity"] for v in method_complexities.values())
    else:
        total_complexity = sum(method_complexities.values())

    print(f"📊 Total Complexity: {total_complexity}")
    print("📊 Method Complexity & Coverage:")

    for method, stats in method_complexities.items():
        if isinstance(stats, dict):
            emoji = "⚠️" if stats["complexity"] > guard.config.get("max_complexity", 10) else "✅"
            coverage = stats.get("coverage")
            coverage_str = f"{coverage * 100:.1f}%" if isinstance(coverage, float) else "N/A"
            print(
                f"  {emoji} {method} | Complexity: {stats['complexity']} | Coverage: {coverage_str} ({stats.get('hits', 'N/A')}/{stats.get('lines', 'N/A')})"
            )
        else:
            emoji = "⚠️" if stats > guard.config.get("max_complexity", 10) else "✅"
            print(f"  {emoji} {method}: {stats}")


def print_summary(summary, guard, args):
    for file, result in summary.items():
        print(f"\n📂 File: {file}")
        if not args.diff_only:
            method_complexities = result.get("complexity", {})
            print_method_stats(method_complexities, guard)


def parse_args():
    parser = argparse.ArgumentParser(description="RefactorGuard CLI: Audit Python refactors.")
    parser.add_argument("--original", type=str, default="", help="Original file/dir")
    parser.add_argument("--refactored", type=str, required=True, help="Refactored file/dir")
    parser.add_argument(
        "--tests", type=str, help="Optional test file to check for missing test coverage"
    )
    parser.add_argument("--all", action="store_true", help="Audit entire scripts dir")
    parser.add_argument("--diff-only", action="store_true", help="Ignore complexity checks")
    parser.add_argument("--missing-tests", action="store_true", help="List methods lacking tests")
    parser.add_argument(
        "--complexity-warnings", action="store_true", help="Show cyclomatic complexity warnings"
    )
    parser.add_argument("--json", action="store_true", help="Export result as structured JSON")
    parser.add_argument(
        "--git-diff", action="store_true", help="Only analyze Git-changed files vs origin/main"
    )
    return parser.parse_args()


def dispatch_mode(args, guard):
    if args.all:
        return handle_full_scan(args, guard)
    else:
        return handle_single_file(args, guard)


def handle_full_scan(args, guard):
    original = args.original or "scripts"
    refactored = args.refactored or "scripts"
    summary = {}

    if args.git_diff:
        changed_files = get_changed_files("origin/main")
        for file in changed_files:
            orig = os.path.join(original, file)
            refac = os.path.join(refactored, file)
            if os.path.exists(refac):
                summary[file] = guard.analyze_module(orig, refac)
    else:
        summary = guard.analyze_directory_recursive(original, refactored)

    return summary


def handle_single_file(args, guard):
    if not os.path.isfile(args.original):
        raise ValueError(f"[handle_single_file] Expected a file for --original, got: {args.original}")
    if not os.path.isfile(args.refactored):
        raise ValueError(f"[handle_single_file] Expected a file for --refactored, got: {args.refactored}")

    result = guard.analyze_module(
        original_path=args.original,
        refactored_path=args.refactored,
    )
    return {"summary": result}




def handle_output(result, args, guard):
    summary = result if args.all else result.get("summary", {})

    if args.json:
        handle_json_output(summary, "refactor_audit")
    else:
        print_summary(summary, guard, args)

    if not args.diff_only and args.complexity_warnings and not args.all:
        complexity = summary.get("complexity", {})
        method_complexities = complexity.get("methods", {})
        if method_complexities:
            print("\n📊 Method Complexity:")
            for method, score in method_complexities.items():
                emoji = "⚠️" if score > guard.config.get("max_complexity", 10) else "✅"
                print(f"  {emoji} {method}: {score}")


def main():
    args = parse_args()
    guard = RefactorGuard()

    method_ranges = safe_collect_method_ranges(args.refactored)
    coverage_hits = parse_coverage_xml_to_method_hits("coverage.xml", method_ranges)

    if coverage_hits:
        guard.coverage_hits = coverage_hits

    result = dispatch_mode(args, guard)
    handle_output(result, args, guard)

    if args.missing_tests and args.tests:
        print("\n🧪 Missing Tests:")
        missing = guard.analyze_tests(args.refactored, args.tests)
        if missing["missing_tests"]:
            for item in missing["missing_tests"]:
                print(f"❌ {item['class']} → {item['method']}")
        else:
            print("✅ All public methods have tests!")


if __name__ == "__main__":
    main()
