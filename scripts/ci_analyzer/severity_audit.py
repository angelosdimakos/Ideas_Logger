"""
This module provides functionality to generate a CI code quality audit report.

It includes functions to format priority levels and generate summary header blocks based on severity metrics.
"""

import json
import argparse
from pathlib import Path
from typing import Dict

from scripts.ci_analyzer.severity_index import compute_severity_index
from scripts.ci_analyzer.drilldown import generate_top_offender_drilldowns
from scripts.ci_analyzer.metrics_summary import generate_metrics_summary
from scripts.ci_analyzer.visuals import risk_emoji, render_bar


def format_priority(score: float) -> str:
    """
    Format the priority level based on the severity score.

    Args:
        score (float): The severity score to evaluate.

    Returns:
        str: A string representing the priority level (High, Medium, Low).
    """
    if score > 30:  # High priority for scores above 30
        return "🔥 High"
    elif score > 15:  # Medium priority for scores above 15
        return "⚠️ Medium"
    else:  # Low priority for scores 15 and below
        return "✅ Low"


def generate_header_block(severity_df, report_data: Dict[str, Dict]) -> str:
    """
    Generate a header block for the CI code quality audit report.

    Args:
        severity_df: DataFrame containing severity information for files.
        report_data: Dictionary containing report data for each file.

    Returns:
        str: A Markdown formatted string representing the header block.
    """
    total_files = len(report_data)  # Total number of files in the report
    files_with_issues = (
        severity_df.query("`Mypy Errors` > 0 or `Lint Issues` > 0").shape[0]
        if not severity_df.empty
        else 0
    )  # Count files with issues

    # Handle empty DataFrame case
    worst_file = (
        severity_df.iloc[0]["File"] if not severity_df.empty else "None"
    )  # Get the worst file from the severity DataFrame

    # Compute metrics for visual bars
    total_methods = 0  # Initialize total methods count
    missing_tests = 0  # Initialize missing tests count
    missing_docstrings = 0  # Initialize missing docstrings count
    linter_issues = 0  # Initialize linter issues count

    for content in report_data.values():  # Iterate over report data
        complexity = content.get("coverage", {}).get("complexity", {})  # Get complexity data
        total_methods += len(complexity)  # Update total methods count
        missing_tests += sum(
            1 for m in complexity.values() if m.get("coverage", 1.0) == 0
        )  # Update missing tests count

        missing_docstrings += sum(  # Update missing docstrings count
            1
            for f in content.get("docstrings", {}).get("functions", [])
            if not f.get("description") or not f.get("args") or not f.get("returns")
        )

        lint = content.get("linting", {}).get("quality", {})  # Get linting data
        linter_issues += len(lint.get("mypy", {}).get("errors", []))  # Update linter issues count
        linter_issues += sum(
            len(v) for v in lint.get("pydocstyle", {}).get("functions", {}).values()
        )  # Update linter issues count

    pct_docs = (
        100 * (1 - missing_docstrings / total_methods) if total_methods else 100
    )  # Calculate percentage of documented methods
    pct_tests = (
        100 * (1 - missing_tests / total_methods) if total_methods else 100
    )  # Calculate percentage of tested methods
    pct_lint = (
        100 * (1 - linter_issues / total_methods) if total_methods else 100
    )  # Calculate percentage of lint-free methods

    return f"""# 📊 CI Code Quality Audit Report

## Executive Summary

| Metric                     | Value    | Visual |
|----------------------------|----------|--------|
| Files analyzed             | `{total_files}`    |     |
| Files with issues          | `{files_with_issues}`     |     |
| **Top risk file**          | `{worst_file}` |     |
| Methods audited            | `{total_methods}`    |     |
| Missing tests              | `{missing_tests}`    | {render_bar(pct_tests)} {risk_emoji(pct_tests)} |
| Missing docstrings         | `{missing_docstrings}`    | {render_bar(pct_docs)} {risk_emoji(pct_docs)} |
| Linter issues              | `{linter_issues}`    | {render_bar(pct_lint)} {risk_emoji(pct_lint)} |
"""


def generate_severity_table(severity_df) -> str:
    """
    Generate a severity table for the CI code quality audit report.

    Args:
        severity_df: DataFrame containing severity information for files.

    Returns:
        str: A Markdown formatted string representing the severity table.
    """
    table = "\n## 🧨 Severity Rankings (Top 10)\n\n"
    table += "| File | 🔣 Mypy | 🧼 Lint | 📉 Cx | 📊 Cov | 📈 Score | 🎯 Priority |\n"
    table += "|------|--------|--------|------|--------|----------|-------------|\n"

    # Check if DataFrame is empty
    if severity_df.empty:
        table += "| No files found | 0 | 0 | 0 | 0% | 0 | Low |\n"
        return table

    top_df = severity_df.head(10)
    for _, row in top_df.iterrows():
        cov_bar = render_bar(row["Avg Coverage %"])
        cx_emoji = risk_emoji(100 - row["Avg Complexity"])  # invert: lower is better
        table += (
            f"| `{row['File']}` | {row['Mypy Errors']} | {row['Lint Issues']} | "
            f"{row['Avg Complexity']} {cx_emoji} | {row['Avg Coverage %']}% {cov_bar} | "
            f"{row['Severity Score']} | {format_priority(row['Severity Score'])} |\n"
        )
    return table


def main() -> None:
    """
    Generate a CI code quality audit report.

    This function parses command line arguments, loads report data, computes severity metrics,
    and generates a Markdown report.
    """
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
