#!/usr/bin/env python3
"""
quality_checker – public API.

• imports all plugins (via plugins.__init__)
• drives tool execution + parsing
• merges results into RefactorGuard audit
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, Any, Set

from scripts.refactor.enrich_refactor_pkg.path_utils import norm
from scripts.refactor.enrich_refactor_pkg.helpers import safe_print
from scripts.refactor.enrich_refactor_pkg.core import all_plugins

# auto-import plugin modules so they register
import scripts.refactor.enrich_refactor_pkg.plugins  # noqa: F401

ENC = "utf-8"


def merge_into_refactor_guard(audit_path: str = "refactor_audit.json") -> None:
    """Enrich *audit_path* with quality data produced by every plugin."""
    audit_file = Path(audit_path)
    if not audit_file.exists():
        safe_print("[!] Missing refactor audit JSON!")
        return

    try:
        audit_raw: Dict[str, Any] = json.loads(audit_file.read_text(encoding=ENC))
    except json.JSONDecodeError as err:
        safe_print(f"[!] Corrupt audit JSON: {err}")
        return

    # 1) Generate and parse plugin reports
    base_dir = audit_file.parent
    q_by_file: Dict[str, Dict[str, Any]] = {}
    generated: Set[str] = set()

    for plugin in all_plugins():
        # point report into audit directory
        report_path = base_dir / plugin.default_report.name
        plugin.default_report = report_path

        # decide if we need to run the tool
        existing = (
            report_path.read_text(encoding=ENC, errors="ignore") if report_path.exists() else ""
        )
        if not existing.strip():
            safe_print(f"[~] Generating report for {plugin.name}")
            plugin.run()
            generated.add(plugin.default_report.name)

        # parse the report into q_by_file
        plugin.parse(q_by_file)

    # 2) Merge quality data into audit
    audit_norm = {norm(k): v for k, v in audit_raw.items()}
    for file_key, qdata in q_by_file.items():
        audit_norm.setdefault(file_key, {}).setdefault("quality", {}).update(qdata)

    # Ensure every file has a quality key
    for fk in list(audit_norm.keys()):
        audit_norm[fk].setdefault("quality", {})

    # Write enriched audit JSON
    audit_file.write_text(json.dumps(audit_norm, indent=2), encoding=ENC)
    safe_print("[OK] RefactorGuard audit enriched with quality data.")

    # 3) Clean up only the reports we generated
    for name in generated:
        try:
            (base_dir / name).unlink()
        except FileNotFoundError:
            pass


def merge_reports(file_a: str, file_b: str) -> Dict[str, Any]:
    """Return merged dict where *b* overrides *a* on duplicate keys."""
    with open(file_a, encoding=ENC) as fa:
        data_a = json.load(fa)
    with open(file_b, encoding=ENC) as fb:
        data_b = json.load(fb)
    return {**data_a, **data_b}
