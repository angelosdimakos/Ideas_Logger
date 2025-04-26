from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List


# ── 1. Plugin base class ───────────────────────────────────────────────────
class ToolPlugin(ABC):
    """
    Abstract base class for tool plugins.
    Subclasses must implement `name`, `default_report`, `run`, and `parse`.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier (e.g., "black")."""
        ...

    @property
    @abstractmethod
    def default_report(self) -> Path:
        """Filesystem path where the tool writes its report (txt/xml)."""
        ...

    @abstractmethod
    def run(self) -> int:
        """Execute the tool, writing output to `default_report`; return exit code."""
        ...

    @abstractmethod
    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        """Read `default_report` and merge quality findings into `dst`."""
        ...


# ── 2. Plugin discovery ───────────────────────────────────────────────────────
from scripts.refactor.enrich_refactor_pkg.plugins import PLUGINS as _PLUGINS


def all_plugins() -> List[ToolPlugin]:
    """Return the list of ToolPlugin instances auto-registered via plugins package."""
    return _PLUGINS
