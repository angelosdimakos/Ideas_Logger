import argparse
import json
import os
import sys
from scripts.refactor.refactor_guard import RefactorGuard


def print_header(title: str):
    print(f"\n🔍 {title}\n" + "-" * (len(title) + 4))


def main():
    parser = argparse.ArgumentParser(description="🛡 RefactorGuard CLI – Audit Python Refactors Like a Boss")

    parser.add_argument("--original", type=str, help="Path to the original file or directory", default="")
    parser.add_argument("--refactored", type=str, required=True, help="Path to the refactored file or directory")
    parser.add_argument("--tests", type=str, help="Optional test file to check for missing test coverage")

    # Modes
    parser.add_argument("--all", action="store_true", help="Audit entire scripts directory non-recursively")
    parser.add_argument("--json", action="store_true", help="Output result as structured JSON")

    # Output Filtering
    parser.add_argument("--diff-only", action="store_true", help="Only show method diffs, skip complexity")
    parser.add_argument("--missing-tests", action="store_true", help="Show missing test methods")
    parser.add_argument("--complexity-warnings", action="store_true", help="Show cyclomatic complexity info")

    # Enforcement (for CI)
    parser.add_argument("--enforce", action="store_true", help="Fail if issues exceed thresholds")
    parser.add_argument("--max-complexity", type=int, default=10, help="Max complexity allowed before failing")
    parser.add_argument("--max-missing-tests", type=int, default=5, help="Max number of missing tests allowed")

    args = parser.parse_args()
    guard = RefactorGuard()

    fail_ci = False
    summary = {}

    try:
        if args.all:
            original = args.original or "scripts"
            refactored = args.refactored or "scripts"

            summary = guard.analyze_directory(original, refactored)
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                for file, result in summary.items():
                    print_header(f"File: {file}")
                    if not args.diff_only:
                        complexity = result.get("complexity", {}).get(os.path.join(refactored, file), None)
                        if args.complexity_warnings:
                            print(f"🧠 Complexity: {complexity}")
                        if args.enforce and complexity is not None and complexity > args.max_complexity:
                            print(f"🚨 Complexity threshold exceeded: {complexity} > {args.max_complexity}")
                            fail_ci = True
                    print(f"🛠 Method Changes:\n{json.dumps(result.get('method_diff', {}), indent=2)}")

        else:
            result = guard.analyze_refactor_changes(
                original_path=args.original,
                refactored_path=args.refactored,
                test_file_path=args.tests,
                as_string=not args.json
            )
            print(result if not args.json else json.dumps(result, indent=2))

            if args.enforce and isinstance(result, dict):
                complexity = result.get("complexity", {}).get(args.refactored, None)
                if args.complexity_warnings and complexity is not None:
                    print(f"🧠 Complexity: {complexity}")
                if complexity is not None and complexity > args.max_complexity:
                    print(f"🚨 Complexity too high: {complexity} > {args.max_complexity}")
                    fail_ci = True

    except Exception as e:
        print(f"❌ Refactor analysis failed: {e}")
        sys.exit(1)

    # ✅ Check for missing tests
    if args.missing_tests and args.tests:
        test_report = guard.analyze_tests(args.refactored, args.tests)
        missing = test_report.get("missing_tests", [])

        print_header("Missing Tests")
        if missing:
            for item in missing:
                print(f"❌ {item['class']} → {item['method']}")
            if args.enforce and len(missing) > args.max_missing_tests:
                print(f"🚨 Missing test count exceeds limit: {len(missing)} > {args.max_missing_tests}")
                fail_ci = True
        else:
            print("✅ All methods covered!")

    if fail_ci:
        print("\n❌ RefactorGuard failed thresholds. CI will exit with code 1.")
        sys.exit(1)
    else:
        print("\n✅ RefactorGuard audit complete. No blocking issues.")


if __name__ == "__main__":
    main()
