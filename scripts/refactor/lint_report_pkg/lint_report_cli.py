#!/usr/bin/env python3
"""
Lint Report CLI
===============================
This script enriches a RefactorGuard audit file with linting, coverage, and docstring analysis data.

Key points:
- Zero-setup: If the audit JSON is missing, an empty one is created for plugins to populate.
- No --reports argument: Each plugin runs its own tool and saves its report next to the audit file.
- Optional docstring merge: If a docstring summary JSON is present, it is injected under a top-level "docstrings" key in the audit file.

Typical usage:
$ python lint_report_cli.py --audit refactor_audit.json
$ python lint_report_cli.py --audit refactor_audit.json --docstrings docstring_summary.json
"""

import sys
import argparse
from pathlib import Path

# Ensure the repo root is on sys.path so we can import the helper + qc modules
script_path = Path(__file__).resolve()
project_root = script_path.parents[3]
sys.path.insert(0, str(project_root))

from scripts.refactor.lint_report_pkg.helpers import safe_print  # type: ignore
import scripts.refactor.lint_report_pkg.quality_checker as quality_checker  # type: ignore

ENC = "utf-8"

def enrich_refactor_audit(audit_path: str) -> None:
    """
    Enrich *audit_path* with lint, coverage, and optional docstring data.

    Parameters:
    ----------
    audit_path: str
        Path to the RefactorGuard audit JSON file.
    """
    audit_file = Path(audit_path)

    # ------------------------------------------------------------------
    # 1) Bootstrap an empty audit JSON if it does not yet exist
    # ------------------------------------------------------------------
    if not audit_file.exists():
        safe_print(f"[~] Audit file not found; creating {audit_file}")
        audit_file.write_text("{}", encoding=ENC)

    # ------------------------------------------------------------------
    # 2) Delegate report generation + merging to quality_checker
    # ------------------------------------------------------------------
    safe_print(f"[+] Enriching audit file: {audit_file}")
    quality_checker.merge_into_refactor_guard(str(audit_file))
    safe_print("[✓] Lint and coverage data merged.")


# ----------------------------------------------------------------------
# CLI entry‑point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enrich a RefactorGuard audit JSON with lint, coverage, and docstring data.",
    )
    parser.add_argument(
        "--audit",
        type=str,
        default="refactor_audit.json",
        help="Path to audit JSON file.",
    )


    args = parser.parse_args()
    enrich_refactor_audit(args.audit)
