# scripts/utils/enrich_refactor.py
import os
import sys
import argparse
from pathlib import Path


def enrich_refactor_audit(audit_path: str, reports_path: str = "lint-reports"):
    """Wrapper to ensure merge_into_refactor_guard runs from any context."""
    scripts_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, scripts_root)

    try:
        from refactor import quality_checker
    except ImportError as e:
        print(f"❌ Failed to import quality checker: {e}")
        sys.exit(1)

    audit_file = os.path.abspath(audit_path)
    if not os.path.exists(audit_file):
        print(f"❌ Audit file not found: {audit_file}")
        sys.exit(1)

    report_paths = {
        "black": Path(reports_path) / "black.txt",
        "flake8": Path(reports_path) / "flake8.txt",
        "mypy": Path(reports_path) / "mypy.txt",
        "pydocstyle": Path(reports_path) / "pydocstyle.txt",
        "coverage": Path("coverage.xml"),
    }

    print(f"🔍 Enriching audit file: {audit_file}")
    quality_checker.merge_into_refactor_guard(audit_file, report_paths=report_paths)
    print("✅ Audit enriched with lint + coverage data")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich refactor audit with quality data.")
    parser.add_argument("--audit", type=str, default="refactor_audit.json", help="Path to audit JSON file")
    parser.add_argument("--reports", type=str, default="lint-reports", help="Directory containing lint report files")
    args = parser.parse_args()

    enrich_refactor_audit(args.audit, args.reports)
