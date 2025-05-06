import json
import argparse
from pathlib import Path

from severity_index import compute_severity_index
from drilldown import generate_top_offender_drilldowns
from metrics_summary import generate_metrics_summary
from visuals import risk_emoji, render_bar


def format_priority(score: float) -> str:
    if score > 30:
        return "🔥 High"
    elif score > 15:
        return "⚠️ Medium"
    else:
        return "✅ Low"


def generate_header_block(severity_df, report_data) -> str:
    total_files = len(report_data)
    files_with_issues = severity_df.query("`Mypy Errors` > 0 or `Lint Issues` > 0").shape[0]
    worst_file = severity_df.iloc[0]["File"]

    # Compute metrics for visual bars
    total_methods = 0
    missing_tests = 0
    missing_docstrings = 0
    linter_issues = 0

    for content in report_data.values():
        complexity = content.get("coverage", {}).get("complexity", {})
        total_methods += len(complexity)
        missing_tests += sum(1 for m in complexity.values() if m.get("coverage", 1.0) == 0)

        missing_docstrings += sum(
            1 for f in content.get("docstrings", {}).get("functions", [])
            if not f.get("description") or not f.get("args") or not f.get("returns")
        )

        lint = content.get("linting", {}).get("quality", {})
        linter_issues += len(lint.get("mypy", {}).get("errors", []))
        linter_issues += sum(len(v) for v in lint.get("pydocstyle", {}).get("functions", {}).values())

    pct_docs = 100 * (1 - missing_docstrings / total_methods) if total_methods else 100
    pct_tests = 100 * (1 - missing_tests / total_methods) if total_methods else 100
    pct_lint = 100 * (1 - linter_issues / total_methods) if total_methods else 100

    return f"""# 📊 CI Code Quality Audit Report

## 🔍 Executive Summary

| Metric                     | Value    | Visual |
|----------------------------|----------|--------|
| Files analyzed             | `{total_files}`    | 📦     |
| Files with issues          | `{files_with_issues}`     | ⚠️     |
| **Top risk file**          | `{worst_file}` | 🔥     |
| Methods audited            | `{total_methods}`    | 🧮     |
| Missing tests              | `{missing_tests}`    | {render_bar(pct_tests)} {risk_emoji(pct_tests)} |
| Missing docstrings         | `{missing_docstrings}`    | {render_bar(pct_docs)} {risk_emoji(pct_docs)} |
| Linter issues              | `{linter_issues}`    | {render_bar(pct_lint)} {risk_emoji(pct_lint)} |
"""


def generate_severity_table(severity_df) -> str:
    table = "\n## 🧨 Severity Rankings (Top 10)\n\n"
    table += "| File | 🔣 Mypy | 🧼 Lint | 📉 Cx | 📊 Cov | 📈 Score | 🎯 Priority |\n"
    table += "|------|--------|--------|------|--------|----------|-------------|\n"
    top_df = severity_df.head(10)
    for _, row in top_df.iterrows():
        cov_bar = render_bar(row['Avg Coverage %'])
        cx_emoji = risk_emoji(100 - row['Avg Complexity'])  # invert: lower is better
        table += (
            f"| `{row['File']}` | {row['Mypy Errors']} | {row['Lint Issues']} | "
            f"{row['Avg Complexity']} {cx_emoji} | {row['Avg Coverage %']}% {cov_bar} | "
            f"{row['Severity Score']} | {format_priority(row['Severity Score'])} |\n"
        )
    return table


def main():
    parser = argparse.ArgumentParser(description="Generate a CI code quality audit report")
    parser.add_argument("--audit", required=True, help="Path to merged_report.json")
    parser.add_argument("--output", default="ci_severity_report.md", help="Markdown output path")
    parser.add_argument("--top", type=int, default=3, help="Number of top offenders to detail")
    args = parser.parse_args()

    with open(args.audit, "r", encoding="utf-8") as f:
        report_data = json.load(f)

    severity_df = compute_severity_index(report_data)

    report_parts = [
        generate_header_block(severity_df, report_data),
        generate_severity_table(severity_df),
        generate_metrics_summary(report_data),
        generate_top_offender_drilldowns(severity_df, report_data, top_n=args.top),
    ]

    final_md = "\n\n".join(report_parts)
    Path(args.output).write_text(final_md, encoding="utf-8")
    print(f"✅ CI audit report written to: {args.output}")


if __name__ == "__main__":
    main()
