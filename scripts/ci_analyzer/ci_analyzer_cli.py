import os
import sys

# 👇 Add parent of 'scripts' to sys.path to avoid import errors

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from scripts.ci_analyzer.analyzer import CIInsightReport
from scripts.ci_analyzer.lint_parser import LintParser
from scripts.ci_analyzer.refactor_parser import RefactorParser

if __name__ == "__main__":
    artifacts = {
        "lint": "lint-reports/flake8.txt",
        "refactor": "refactor_audit.json"
    }

    # Manual dispatcher — maps keys to parser classes
    parser_map = {
        "lint": LintParser,
        "refactor": RefactorParser
    }

    report = CIInsightReport()

    for key, path in artifacts.items():
        parser_cls = parser_map.get(key)
        if not parser_cls:
            print(f"❌ No parser defined for: {key}")
            continue

        parser = parser_cls(path)
        summary = parser.parse()

        print(f"\n🔍 {key.upper()} Report:")
        for k, v in summary.items():
            if k != "raw_data":
                print(f"  {k}: {v}")

        report.add_insight(key, summary)

    # Save to Markdown
    report.save("ci_summary.md")
    print("\n✅ CI Summary written to `ci_summary.md`.")
