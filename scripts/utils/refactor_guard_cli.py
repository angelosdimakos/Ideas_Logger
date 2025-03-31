import argparse
import json
from scripts.utils.refactor_guard import analyze_refactor_changes


def main():
    parser = argparse.ArgumentParser(
        description="🛡 Analyze refactor changes and detect method-level diffs or missing tests.")

    parser.add_argument(
        "--original", "-o", required=True,
        help="Original .py file or directory path"
    )
    parser.add_argument(
        "--refactored", "-r", required=True,
        help="Refactored .py file or directory path"
    )
    parser.add_argument(
        "--test", "-t",
        help="(Optional) Path to test file to check for missing test coverage"
    )
    parser.add_argument(
        "--json", "-j", action="store_true",
        help="Output result as JSON instead of pretty print"
    )

    args = parser.parse_args()

    result = analyze_refactor_changes(
        original_path=args.original,
        refactored_path=args.refactored,
        test_file_path=args.test,
        as_string=not args.json
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result)


if __name__ == "__main__":
    main()
