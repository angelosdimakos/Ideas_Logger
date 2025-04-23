"""
orchestrator.py

This module orchestrates the CI audit summary generation workflow.

Core features include:
- Loading audit data from a JSON file, with automatic timestamped backups for traceability.
- Aggregating insights from multiple analysis modules (overview, complexity, testing, quality, diff coverage, and top issues).
- Generating a comprehensive Markdown-formatted CI summary report with visual and emoji risk indicators.
- Command-line interface for specifying input audit files and output summary paths.
- Saving the generated summary to a file for reporting or further processing.

Intended for use in CI pipelines to automate code quality and coverage reporting.
"""

import json
from pathlib import Path
from typing import Any, Dict
from datetime import datetime
import shutil
import argparse

from scripts.ci_analyzer.insights.overview import generate_overview_insights
from scripts.ci_analyzer.insights.descriptive_insights import (
    generate_complexity_insights,
    generate_diff_insights,
    generate_quality_insights,
    generate_testing_insights,
)

from scripts.ci_analyzer.insights.prime_suspects import generate_prime_insights


# Add this function to create a backup
def backup_audit_file(path: str = "refactor_audit.json") -> None:
    """
    Creates a timestamped backup of the specified audit file in the 'audit_backups' directory.
    Prints a warning if the file does not exist.

    Args:
        path (str): Path to the audit file to back up. Defaults to 'refactor_audit.json'.

    Returns:
        None
    """

    audit_path = Path(path)
    if not audit_path.exists():
        print(f"Warning: Cannot backup {path} - file not found")
        return

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("audit_backups")
    backup_dir.mkdir(exist_ok=True)

    backup_path = backup_dir / f"refactor_audit_{timestamp}.json"
    shutil.copy2(audit_path, backup_path)
    print(f"✅ Audit backup created at {backup_path}")


def load_audit(path: str = "refactor_audit.json") -> Dict[str, Any]:
    """
    Loads audit data from a JSON file after creating a timestamped backup.

    Args:
        path (str): Path to the audit JSON file. Defaults to 'refactor_audit.json'.

    Returns:
        Dict[str, Any]: Parsed audit data as a dictionary.
    """
    # First create a backup before loading
    backup_audit_file(path)
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def header_block() -> str:
    """
    Returns a formatted Markdown header block for the CI audit summary,
    including metric summaries, emoji risk indicators, and visual bar indicators.
    """
    return """
## 🔍 CI Audit Summary

Each section includes:
- 📊 Metric summaries
- 🚨 Emoji Risk Indicators (🟢 Low, 🟡 Medium, 🔴 High)
- ▓▓ Visual bar indicators (Markdown style)
"""


def generate_ci_summary(audit: Dict[str, Any]) -> str:
    """
    Generate a comprehensive CI audit summary report as a Markdown-formatted string.

    Aggregates insights from audit data, including overview, top issues, complexity, testing, quality, and diff coverage.

    Args:
        audit (Dict[str, Any]): Audit data for the codebase.

    Returns:
        str: Markdown-formatted CI summary report.
    """
    parts = [header_block()]
    parts.extend(generate_overview_insights(audit))
    parts.extend(generate_prime_insights(audit))
    parts.extend(generate_complexity_insights(audit))
    parts.extend(generate_testing_insights(audit))
    parts.extend(generate_quality_insights(audit))
    parts.extend(generate_diff_insights(audit))
    return "\n".join(parts)


def save_summary(markdown: str, out_path: str = "ci_summary.md") -> None:
    """
    Saves the provided markdown string to a file at the specified path.

    Args:
        markdown (str): The markdown content to save.
        out_path (str, optional): The output file path. Defaults to "ci_summary.md".
    """
    Path(out_path).write_text(markdown, encoding="utf-8")


def main():
    """
    Parses command-line arguments to load audit data, generate a CI summary report, and save it as a Markdown file.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", default="refactor_audit.json", help="Path to audit JSON file")
    parser.add_argument("--output", default="ci_summary.md", help="Path to markdown output")
    args = parser.parse_args()

    audit = load_audit(args.audit)
    summary = generate_ci_summary(audit)
    save_summary(summary, args.output)
    print(f"✅ CI Summary saved to {args.output}")


if __name__ == "__main__":
    main()
