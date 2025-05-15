"""
Core Module for Lint Report Package
=====================================
This module provides the base class for tool plugins and functions for plugin discovery.

It includes the abstract base class ToolPlugin that all plugins must implement,
and a utility to access all discovered plugins.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List


# ── 1. Plugin base class ───────────────────────────────────────────────────
class ToolPlugin(ABC):
    """
    Abstract base class for tool plugins.

    All subclasses must define:
    - name: str (unique plugin name)
    - default_report: Path (where output is written)
    - run(): run the tool
    - parse(dst): enrich the lint result dictionary
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier (e.g., 'flake8')."""
        ...

    @property
    @abstractmethod
    def default_report(self) -> Path:
        """Path where the tool writes its report (txt/json/xml)."""
        ...

    @abstractmethod
    def run(self) -> int:
        """Execute the tool, writing to `default_report`; return exit code."""
        ...

    @abstractmethod
    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        """Read `default_report` and update `dst` with findings."""
        ...


# ── 2. Plugin discovery ─────────────────────────────────────────────────────
from scripts.refactor.lint_report_pkg.plugins import PLUGINS as _PLUGINS


def all_plugins() -> List[ToolPlugin]:
    """
    Return all ToolPlugin instances registered by plugin modules.
    """
    return _PLUGINS
