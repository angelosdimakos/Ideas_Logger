#!/usr/bin/env python3
"""
Split-by-Folder Code Quality Markdown Generator
===============================================
Creates one Markdown file per top-level folder:
- ai.md, core.md, etc.
Each file includes:
- Missing documentation
- Linting issues
- Optional: MyPy errors (--verbose)
"""

from __future__ import annotations

import sys
import argparse
import json
from pathlib import Path
from collections import defaultdict

# ─── make "scripts." imports work when executed as a script ────────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

# Import rendering functions
from scripts.doc_generation.doc_renderers import render_folder_report, render_quality_index


def generate_split_reports(report_data: dict, output_dir: Path, verbose: bool = False):
    """
    Generates Markdown code quality reports for each top-level folder from a combined JSON report.
    
    Groups documentation and linting issues by folder, excluding folders starting with "tests" or "artifacts". For each folder, creates a Markdown file summarizing missing documentation and categorized linting issues, and writes an index file listing all folders.
    
    Args:
        report_data: Parsed JSON data containing code quality information.
        output_dir: Directory where the Markdown report files will be created.
        verbose: If True, includes detailed MyPy error blocks in the reports.
    """
    grouped = defaultdict(lambda: {
        "docs": [],
        "lint": [],
        "mypy": {},
        "totals": {"critical": 0, "high": 0, "medium": 0, "low": 0}
    })

    # Group by folder (excluding tests/)
    for file_path, data in report_data.items():
        file = Path(file_path)
        folder = file.parent.as_posix()
        filename = file.name

        IGNORED_PREFIXES = ("tests", "artifacts")

        if any(folder == p or folder.startswith(f"{p}/") for p in IGNORED_PREFIXES):
            continue

        # Docstring section
        doc = data.get("docstrings")
        if doc:
            module_missing = not doc.get("module_doc", {}).get("description")
            classes_missing = [cls["name"] for cls in doc.get("classes", []) if not cls.get("description")]
            functions_missing = [fn["name"] for fn in doc.get("functions", []) if not fn.get("description")]

            if module_missing or classes_missing or functions_missing:
                grouped[folder]["docs"].append({
                    "file": filename,
                    "module": "Missing" if module_missing else "Present",
                    "classes": ", ".join(classes_missing) if classes_missing else "All Documented",
                    "functions": ", ".join(functions_missing) if functions_missing else "All Documented"
                })

        # Linting issues
        lint = data.get("linting", {}).get("quality", {})
        file_issues = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        has_issues = False

        mypy_errors = lint.get("mypy", {}).get("errors", [])
        if mypy_errors:
            file_issues["high"] += len(mypy_errors)
            grouped[folder]["mypy"][file_path] = mypy_errors
            has_issues = True

        for issues in lint.get("pydocstyle", {}).get("functions", {}).values():
            if issues:
                file_issues["medium"] += len(issues)
                has_issues = True

        if has_issues:
            grouped[folder]["lint"].append({
                "file": filename,
                "issues": file_issues,
                "total": sum(file_issues.values())
            })
            for k in file_issues:
                grouped[folder]["totals"][k] += file_issues[k]

    # Generate markdown files
    output_dir.mkdir(parents=True, exist_ok=True)
    folders = []

    for folder in sorted(grouped):
        safe_name = folder.replace("/", "_")
        output_file = output_dir / f"{safe_name}.md"
        content = render_folder_report(folder, grouped[folder], verbose=verbose)
        output_file.write_text(content, encoding="utf-8")
        folders.append(folder)

    # Write index file
    index_lines = render_quality_index(folders)
    index_path = output_dir / "index.md"
    index_path.write_text("\n".join(index_lines), encoding="utf-8")
    print(f"✅ Split reports written to: {output_dir}/")


def main():
    """
    Parses command-line arguments and generates split Markdown code quality reports.
    
    This function handles argument parsing, validates the input report file, loads the JSON report data, and invokes the report generation process. Exits with an error message if the report file is missing or the JSON is invalid.
    """
    parser = argparse.ArgumentParser(description="Split quality report by folder into multiple markdown files.")
    parser.add_argument("--report", required=True, help="Path to combined JSON report")
    parser.add_argument("--output-dir", required=True, help="Directory to write markdown files")
    parser.add_argument("--verbose", action="store_true", help="Include detailed MyPy error blocks")

    args = parser.parse_args()
    report_path = Path(args.report)
    output_dir = Path(args.output_dir)

    if not report_path.exists():
        print(f"❌ Report not found: {report_path}")
        exit(1)

    try:
        report_data = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("❌ Invalid JSON report format.")
        exit(1)

    generate_split_reports(report_data, output_dir, verbose=args.verbose)


if __name__ == "__main__":
    main()