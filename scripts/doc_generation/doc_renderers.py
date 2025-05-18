#!/usr/bin/env python3
"""
Documentation Rendering Module
=============================
Contains rendering functions for coverage, code quality, and docstring reports.
Separates presentation logic from data processing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional


def render_folder_coverage(folder: str, entries: list) -> str:
    """
    Generates a markdown report summarizing test coverage for a folder.
    
    The report includes the overall line coverage percentage for the folder and a table listing each file's line and branch coverage. Files with no branch coverage data display "N/A" for branch coverage.
    
    Args:
        folder: The folder name or path being reported.
        entries: A list of (file_path, file_data) tuples, where file_data contains coverage summaries.
    
    Returns:
        A markdown-formatted string representing the folder's coverage report.
    """
    md = [f"# Test Coverage Report for `{folder}/`\n"]

    total_lines = sum(e[1]['summary'].get('num_statements', 0) for e in entries)
    covered_lines = sum(e[1]['summary'].get('covered_lines', 0) for e in entries)
    pct = (covered_lines / total_lines * 100) if total_lines > 0 else 0

    md.append(f"**Folder Coverage:** {pct:.2f}% ({covered_lines} of {total_lines} lines covered)\n")

    md += [
        "## 📄 File Coverage",
        "| File | Line Coverage | Branch Coverage |",
        "| ---- | ------------- | ---------------- |"
    ]

    for file_path, file_data in sorted(entries):
        summary = file_data.get("summary", {})
        line_cov = f"{summary.get('percent_covered', 0):.2f}%"
        if summary.get("num_branches", 0) > 0:
            branch_cov = f"{summary.get('percent_covered_branches', 0):.2f}%"
        else:
            branch_cov = "N/A"

        md.append(f"| {Path(file_path).name} | {line_cov} | {branch_cov} |")

    return "\n".join(md)


def render_coverage_index(folders: List[str], totals: Dict[str, Any]) -> List[str]:
    """
    Generates markdown lines for a test coverage index report.
    
    Creates a summary table displaying overall coverage metrics and lists links to individual folder coverage reports. Returns the assembled markdown lines as a list of strings.
    """
    pct = f"{totals.get('percent_covered', 0):.2f}%"
    covered_lines = totals.get("covered_lines", 0)
    total_lines = totals.get("num_statements", 0)
    branches = totals.get("covered_branches", 0)
    total_branches = totals.get("num_branches", 0)

    index_lines = ["# Test Coverage Report Index\n", "## Summary\n"]
    index_lines += [
        "| Metric | Coverage |",
        "|--------|----------|",
        f"| Overall Coverage | {pct} |",
        f"| Lines Covered | {covered_lines} of {total_lines} |"
    ]
    if total_branches > 0:
        index_lines.append(f"| Branches Covered | {branches} of {total_branches} |")
    index_lines.append("")

    for folder in sorted(folders):
        safe_name = folder.replace("/", "_")
        index_lines.append(f"- [{folder}/](./{safe_name}.md)")

    return index_lines


def render_folder_report(folder: str, section: dict, verbose: bool = False) -> str:
    """
    Generates a markdown report summarizing code quality issues for a folder.
    
    The report includes total issue counts by severity, tables for missing documentation and linting issues, and optionally detailed MyPy error listings when verbose mode is enabled.
    
    Args:
        folder: The folder name for which the report is generated.
        section: A dictionary containing code quality data, including totals, documentation, linting, and MyPy errors.
        verbose: If True, includes detailed MyPy error dumps in the report.
    
    Returns:
        A markdown-formatted string representing the code quality report for the folder.
    """
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


def render_quality_index(folders: List[str]) -> List[str]:
    """
    Generates markdown lines for an index of code quality reports.
    
    Each folder is listed with a link to its corresponding report, with folder names sanitized for filenames.
    
    Returns:
        A list of markdown lines representing the index.
    """
    index_lines = ["# Code Quality Report Index\n"]

    for folder in sorted(folders):
        safe_name = folder.replace("/", "_")
        index_lines.append(f"- [{folder}/](./{safe_name}.md)")

    return index_lines


def render_module_docs(file_path: str, docstrings: Dict[str, Any]) -> str:
    """
    Generates a markdown report summarizing the docstrings for a Python module.
    
    The report includes the module's description, arguments, and return values in a summary table, followed by detailed sections for each class and function with their respective descriptions, parameters, and return information. Missing descriptions are replaced with placeholder text.
    
    Args:
        file_path: Path to the Python module file.
        docstrings: Parsed docstring information for the module, including module, classes, and functions.
    
    Returns:
        A markdown-formatted string documenting the module's docstrings.
    """
    module_name = file_path.replace(".py", "").replace("/", ".")
    doc = docstrings.get("module_doc", {})

    description = str(doc.get("description") or "*No module description available.*")
    args = str(doc.get("args") or "—")
    returns = str(doc.get("returns") or "—")

    md = [f"## `{module_name}`\n"]

    md.append("**🧠 Docstring Summary**\n")
    md += [
        "| Section | Content |",
        "|---------|---------|",
        f"| Description | {description} |",
        f"| Args | {args} |",
        f"| Returns | {returns} |",
        ""
    ]

    # Classes
    classes = docstrings.get("classes", [])
    if classes:
        md.append("### 📦 Classes")
        for cls in classes:
            md.append(f"#### `{cls.get('name', 'UnnamedClass')}`")
            md.append(str(cls.get("description") or "*No description available.*"))

            cls_args = cls.get("args")
            if cls_args:
                md.append(f"**Parameters:**\n{str(cls_args)}")

            cls_returns = cls.get("returns")
            if cls_returns:
                md.append(f"**Returns:**\n{str(cls_returns)}")

            md.append("")

    # Functions
    functions = docstrings.get("functions", [])
    if functions:
        md.append("### 🛠️ Functions")
        for fn in functions:
            md.append(f"#### `{fn.get('name', 'unnamed_function')}`")
            md.append(str(fn.get("description") or "*No description available.*"))

            fn_args = fn.get("args")
            if fn_args:
                md.append(f"**Parameters:**\n{str(fn_args)}")

            fn_returns = fn.get("returns")
            if fn_returns:
                md.append(f"**Returns:**\n{str(fn_returns)}")

            md.append("")

    return "\n".join(md)



def render_docstring_index(sections: List[Tuple[str, List[Tuple[str, str]]]]) -> List[str]:
    """
    Generates markdown lines for a docstring report index.
    
    Each section is listed with a link to its corresponding markdown file, using display names with slashes instead of underscores.
    
    Args:
        sections: A list of tuples, each containing a section name and a list of module entries.
    
    Returns:
        A list of markdown-formatted lines for the docstring index.
    """
    index_lines = ["# Docstring Report Index\n"]

    for section, _ in sorted(sections):
        display = section.replace("_", "/")  # reverse folder name flattening
        index_lines.append(f"- [{display}/]({section}.md)")

    return index_lines
