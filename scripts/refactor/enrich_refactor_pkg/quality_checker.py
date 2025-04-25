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
from typing import Dict, Any

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

    # 1) Have each plugin generate & parse its report
    q_by_file: Dict[str, Dict[str, Any]] = {}
    for plugin in all_plugins():
        rpt = plugin.default_report
        if not rpt.exists() or not rpt.read_text(errors="ignore").strip():
            safe_print(f"[~] Generating report for {plugin.name}")
            plugin.run()
        plugin.parse(q_by_file)

    # 2) Merge quality data into audit (normalize keys once)
    audit_norm = {norm(k): v for k, v in audit_raw.items()}
    for file_key, qdata in q_by_file.items():
        audit_norm.setdefault(file_key, {}).setdefault("quality", {}).update(qdata)

    audit_file.write_text(json.dumps(audit_norm, indent=2), encoding=ENC)
    safe_print("[OK] RefactorGuard audit enriched with quality data.")


def merge_reports(file_a: str, file_b: str) -> Dict[str, Any]:
    """Return merged dict where *b* overrides *a* on duplicate keys."""
    with open(file_a, encoding=ENC) as fa:
        data_a = json.load(fa)
    with open(file_b, encoding=ENC) as fb:
        data_b = json.load(fb)
    return {**data_a, **data_b}
