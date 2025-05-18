#!/usr/bin/env python3
"""
Quality Checker for Lint Report Package
=======================================
This module serves as the public API for the lint report package.

It imports all plugins, drives tool execution and parsing, and merges results into the RefactorGuard audit.
"""

import json
from pathlib import Path
from typing import Dict, Any, Set

from scripts.refactor.lint_report_pkg.path_utils import norm
from scripts.refactor.lint_report_pkg.helpers import safe_print
from scripts.refactor.lint_report_pkg.core import all_plugins

ENC = "utf-8"


def merge_into_refactor_guard(audit_path: str = "refactor_audit.json", file_filter: Dict[str, str] = None) -> None:
    """
    Enrich *audit_path* with quality data produced by every plugin.

    Parameters
    ----------
    audit_path : str
        Path to the RefactorGuard audit JSON file.
    file_filter : Dict[str, str], optional
        If provided, only process the specified files (module_name -> file_path).
    """
    audit_file = Path(audit_path)

    # Load or initialize audit JSON
    if not audit_file.exists():
        safe_print("[~] No audit JSON found; starting fresh.")
        audit_raw: Dict[str, Any] = {}
    else:
        try:
            audit_raw = json.loads(audit_file.read_text(encoding=ENC))
        except json.JSONDecodeError as err:
            safe_print(f"[~] Audit JSON corrupt ({err}); starting fresh.")
            audit_raw = {}

    # Normalize input structure
    audit_norm = {norm(k): v for k, v in audit_raw.items()}
    q_by_file: Dict[str, Dict[str, Any]] = {}
    generated: Set[str] = set()
    base_dir = audit_file.parent

    # Run and parse each plugin
    for plugin in all_plugins():
        # Configure plugin to respect file_filter if provided
        if file_filter:
            # Save original configuration to restore later
            original_config = getattr(plugin, 'config', {})
            # Set plugin to only process specified files
            # The exact implementation depends on how plugins are configured
            plugin.config = {**original_config, 'files': file_filter}

        report_path = base_dir / plugin.default_report.name
        plugin.default_report = report_path

        existing = (
            report_path.read_text(encoding=ENC, errors="ignore") if report_path.exists() else ""
        )
        if not existing.strip():
            safe_print(f"[~] Generating report for {plugin.name}")
            plugin.run()
            generated.add(plugin.default_report.name)

        safe_print(f"[~] Parsing report for {plugin.name}")
        plugin.parse(q_by_file)

        # Restore original configuration if we modified it
        if file_filter:
            plugin.config = original_config

    # Merge quality results with flexible key matching
    for file_key, qdata in q_by_file.items():
        # If file_filter is provided, only include files in the filter
        if file_filter and file_key not in file_filter.keys():
            continue

        matched_key = next(
            (k for k in audit_norm if k.endswith(file_key) or norm(k) == norm(file_key)), file_key
        )
        audit_norm.setdefault(matched_key, {}).setdefault("quality", {}).update(qdata)

    # Ensure all files have a quality key
    for fk in list(audit_norm.keys()):
        audit_norm[fk].setdefault("quality", {})

    # Save enriched audit JSON
    audit_file.write_text(json.dumps(audit_norm, indent=2), encoding=ENC)
    if file_filter:
        safe_print(f"[OK] RefactorGuard audit enriched with quality data for {len(file_filter)} files.")
    else:
        safe_print("[OK] RefactorGuard audit enriched with quality data.")

    # Clean up temporary reports
    for name in generated:
        try:
            (base_dir / name).unlink()
        except FileNotFoundError:
            pass

def merge_reports(file_a: str, file_b: str) -> Dict[str, Any]:
    """
    Return merged dict where *b* overrides *a* on duplicate keys.

    Parameters
    ----------
    file_a : str
        Path to the first JSON file.
    file_b : str
        Path to the second JSON file.
    """
    with open(file_a, encoding=ENC) as fa:
        data_a = json.load(fa)
    with open(file_b, encoding=ENC) as fb:
        data_b = json.load(fb)
    return {**data_a, **data_b}
