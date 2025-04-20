import os
import sys
import argparse
import subprocess
from pathlib import Path


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="ignore").decode())


def enrich_refactor_audit(audit_path: str, reports_path: str = "lint-reports"):
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[2]  # Up to repo root
    refactor_path = project_root / "scripts"

    # Add scripts directory to sys.path
    sys.path.insert(0, str(refactor_path))

    try:
        from refactor import quality_checker
    except ImportError as e:
        safe_print(f"[!] Failed to import quality checker: {e}")
        safe_print(f"[i] Tried importing from: {refactor_path}")
        sys.exit(1)

    audit_file = os.path.abspath(audit_path)
    if not os.path.exists(audit_file):
        safe_print(f"[!] Audit file not found: {audit_file}")
        sys.exit(1)

    # Ensure lint report folder exists
    Path(reports_path).mkdir(parents=True, exist_ok=True)

    # Auto-generate missing reports
    required_reports = {
        "black": ["black", "--check", "scripts"],
        "flake8": ["flake8", "scripts"],
        "mypy": ["mypy", "--strict", "--no-color-output", "scripts"],
        "pydocstyle": ["pydocstyle", "scripts"],
    }

    for name, cmd in required_reports.items():
        report_file = Path(reports_path) / f"{name}.txt"
        if not report_file.exists():
            safe_print(f"[~] Generating missing report: {report_file.name}")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            report_file.write_text(result.stdout)

    report_paths = {
        "black": Path(reports_path) / "black.txt",
        "flake8": Path(reports_path) / "flake8.txt",
        "mypy": Path(reports_path) / "mypy.txt",
        "pydocstyle": Path(reports_path) / "pydocstyle.txt",
        "coverage": Path("coverage.xml"),
    }

    safe_print(f"[+] Enriching audit file: {audit_file}")
    quality_checker.merge_into_refactor_guard(audit_file, report_paths=report_paths)
    safe_print("[✓] Audit enriched with lint + coverage data")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich refactor audit with quality data.")
    parser.add_argument("--audit", type=str, default="refactor_audit.json", help="Path to audit JSON file")
    parser.add_argument("--reports", type=str, default="lint-reports", help="Directory containing lint report files")
    args = parser.parse_args()

    enrich_refactor_audit(args.audit, args.reports)
