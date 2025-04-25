#!/usr/bin/env python3
"""
enrich_refactor_ci.py

Enriches a RefactorGuard audit file with linting, coverage, and docstring analysis data.

Features:
- Generates missing lint reports if absent
- Collects paths to all quality-related reports
- Merges all data into the audit file using quality_checker
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import json

script_path = Path(__file__).resolve()
project_root = script_path.parents[3]  # should point to your repo root
sys.path.insert(0, str(project_root))

from scripts.refactor.enrich_refactor_pkg.helpers import safe_print
import scripts.refactor.enrich_refactor_pkg.quality_checker as quality_checker
from scripts.refactor.enrich_refactor_pkg.quality_checker import merge_reports

ENC = "utf-8"

def enrich_refactor_audit(
    audit_path: str,
    reports_path: str,
    docstring_path: str = "docstring_summary.json",
) -> None:
    audit_file = Path(audit_path)
    if not audit_file.exists():
        safe_print(f"[!] Audit file not found: {audit_file}")
        sys.exit(1)

    # 1) Ensure all required lint/coverage reports exist
    required_reports = {
        "flake8": ["flake8", "--exit-zero", f"--output-file={reports_path}/flake8.txt", "."],
        "black": ["black", "--check", "--diff", "."],
        "mypy": ["mypy", "--strict", "--no-color-output", "."],
        "pydocstyle": ["pydocstyle", "."],
        "coverage": ["coverage", "xml"],
    }

    for name, cmd in required_reports.items():
        report_file = Path(reports_path) / f"{name}.txt"
        if name == "coverage":
            report_file = Path.cwd() / "coverage.xml"
        if not report_file.exists():
            safe_print(f"[~] Generating: {report_file.name}")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            report_file.write_text(result.stdout if name != "coverage" else "", encoding=ENC)

    # 2) Build a map of tool-name → Path
    report_paths = {
        "black": Path(reports_path) / "black.txt",
        "flake8": Path(reports_path) / "flake8.txt",
        "mypy": Path(reports_path) / "mypy.txt",
        "pydocstyle": Path(reports_path) / "pydocstyle.txt",
        "coverage": Path.cwd() / "coverage.xml",
    }

    safe_print(f"[+] Enriching audit file: {audit_file}")

    # 3) Override the plugins' default_report to point at our CLI's report directory
    for plugin in quality_checker.all_plugins():
        if plugin.name in report_paths:
            plugin.default_report = report_paths[plugin.name]

    # 4) Merge all quality data into the audit JSON
    quality_checker.merge_into_refactor_guard(audit_file)

    safe_print("[✓] Lint and coverage data merged.")

    # 5) Optionally merge docstring data
    docstring_file = Path(docstring_path)
    if docstring_file.exists():
        safe_print(f"[+] Merging docstring data from {docstring_file}")
        try:
            from scripts.refactor.parsers.docstring_parser import DocstringAnalyzer
            doc_data = json.loads(docstring_file.read_text(encoding=ENC))
            # merge doc_data into audit_file here...
        except Exception as e:
            safe_print(f"[!] Error merging docstring data: {e}")
    else:
        safe_print(f"[!] Docstring summary not found at {docstring_file}. Skipping.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich refactor audit with quality data.")
    parser.add_argument("--audit", type=str, default="refactor_audit.json", help="Path to audit JSON file")
    parser.add_argument("--reports", type=str, default="lint-reports", help="Directory for lint report files")
    parser.add_argument("--docstrings", type=str, default="docstring_summary.json", help="Path to docstring summary JSON")
    args = parser.parse_args()

    enrich_refactor_audit(args.audit, args.reports, args.docstrings)
