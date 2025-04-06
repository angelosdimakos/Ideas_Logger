import argparse
import os
import sys
import json

# 👇 Add parent of 'scripts' to sys.path to avoid import errors
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from scripts.refactor.refactor_guard import RefactorGuard

def main():
    parser = argparse.ArgumentParser(description="RefactorGuard CLI: Audit Python refactors.")

    parser.add_argument("--original", type=str, help="Path to the original file or directory", default="")
    parser.add_argument("--refactored", type=str, required=True, help="Path to the refactored file or directory")
    parser.add_argument("--tests", type=str, help="Optional test file to check for missing test coverage")
    parser.add_argument("--all", action="store_true", help="Audit entire scripts directory recursively")
    parser.add_argument("--diff-only", action="store_true", help="Only show method diffs, ignore complexity")
    parser.add_argument("--missing-tests", action="store_true", help="List methods lacking tests")
    parser.add_argument("--complexity-warnings", action="store_true", help="Show cyclomatic complexity warnings")
    parser.add_argument("--json", action="store_true", help="Output result as structured JSON")

    args = parser.parse_args()
    guard = RefactorGuard()

    if args.all:
        # Default to scripts/ if --all is enabled
        original = args.original or "scripts"
        refactored = args.refactored or "scripts"
        summary = guard.analyze_directory_recursive(original, refactored)

        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            for file, result in summary.items():
                print(f"\n📂 File: {file}")
                if not args.diff_only:
                    print("📊 Total Complexity:", result.get("complexity", {}).get(refactored, "N/A"))

                    if args.complexity_warnings:
                        method_complexities = result.get("complexity", {}).get("methods", {})
                        for method, score in method_complexities.items():
                            emoji = "⚠️" if score > guard.config.get("max_complexity", 10) else "✅"
                            print(f"  {emoji} {method}: {score}")
                print("🔧 Method Changes:", result.get("method_diff"))

    else:
        result = guard.analyze_refactor_changes(
            original_path=args.original,
            refactored_path=args.refactored,
            test_file_path=args.tests,
            as_string=not args.json
        )
        if args.json:
            print(json.dumps(result, indent=2) if isinstance(result, dict) else result)
        else:
            print(result)

        if not args.diff_only and args.complexity_warnings and isinstance(result, dict):
            complexity = result.get("summary", {}).get("complexity", {})
            method_complexities = complexity.get("methods", {})
            print("\n📊 Method Complexity:")
            for method, score in method_complexities.items():
                emoji = "⚠️" if score > guard.config.get("max_complexity", 10) else "✅"
                print(f"  {emoji} {method}: {score}")

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