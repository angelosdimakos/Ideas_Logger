import os
import sys
import argparse
from pathlib import Path


def safe_print(msg: str):
    """Print safely in environments that may not support Unicode emoji (e.g. Windows CP1252)."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="ignore").decode())


def enrich_refactor_audit(audit_path: str, reports_path: str = "lint-reports"):
    """Wrapper to ensure merge_into_refactor_guard runs from any context."""

    # Resolve script location (real path for local, temp for pytest)
    script_path = Path(__file__).resolve()
    if "tmp" in str(script_path).lower():
        project_root = script_path.parents[2]
    else:
        project_root = script_path.parent.parent

    sys.path.insert(0, str(project_root / "scripts"))

    try:
        from refactor import quality_checker
    except ImportError as e:
        safe_print(f"[!] Failed to import quality checker: {e}")
        sys.exit(1)

    audit_file = os.path.abspath(audit_path)
    if not os.path.exists(audit_file):
        safe_print(f"[!] Audit file not found: {audit_file}")
        sys.exit(1)

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
