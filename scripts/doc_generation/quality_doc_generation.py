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

import argparse
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any


def render_folder_report(folder: str, section: dict, verbose: bool = False) -> str:
    """Renders the markdown content for a single folder."""
    md = [f"# Code Quality Report for `{folder}/`\n"]

    totals = section["totals"]
    total_issues = sum(totals.values())
    md.append(f"**Folder Totals:** {total_issues} issues "
              f"(Critical: {totals['critical']}, High: {totals['high']}, "
              f"Medium: {totals['medium']}, Low: {totals['low']})\n")

    # Docstring Table
    if section["docs"]:
        md += [
            "## 📄 Missing Documentation",
            "| File | Module Doc | Missing Classes | Missing Functions |",
            "| ---- | -----------| ----------------| ------------------ |"
        ]
        for doc in section["docs"]:
            md.append(f"| {doc['file']} | {doc['module']} | {doc['classes']} | {doc['functions']} |")
        md.append("")

    # Linting Table
    if section["lint"]:
        md += [
            "## 🧹 Linting Issues",
            "| File | Critical | High | Medium | Low | Total |",
            "| ---- | -------- | ---- | ------ | --- | ----- |"
        ]
        for item in section["lint"]:
            i = item["issues"]
            md.append(f"| {item['file']} | {i['critical']} | {i['high']} | "
                      f"{i['medium']} | {i['low']} | {item['total']} |")
        md.append("")

    # MyPy Dump
    if verbose and section["mypy"]:
        md.append("## 📋 MyPy Errors")
        for path, errors in section["mypy"].items():
            md.append(f"#### {path}\n```\n" + "\n".join(errors) + "\n```")

    return "\n".join(md)


def generate_split_reports(report_data: Dict[str, Dict[str, Any]], output_dir: Path, verbose: bool = False):
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
    index_lines = ["# Code Quality Report Index\n"]

    for folder in sorted(grouped):
        safe_name = folder.replace("/", "_")
        output_file = output_dir / f"{safe_name}.md"
        content = render_folder_report(folder, grouped[folder], verbose=verbose)
        output_file.write_text(content, encoding="utf-8")
        index_lines.append(f"- [{folder}/](./{safe_name}.md)")

    # Write index file
    index_path = output_dir / "index.md"
    index_path.write_text("\n".join(index_lines), encoding="utf-8")
    print(f"✅ Split reports written to: {output_dir}/")


def main():
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
