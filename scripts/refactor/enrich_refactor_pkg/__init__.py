"""
Plugin-based quality-checker package.

`core.merge_into_refactor_guard()` is the only public entry-point most
code ever needs.
"""
from importlib import import_module
from pathlib import Path

_PLUGIN_REGISTRY = {}          # str → ToolPlugin

def register(name: str):
    """Decorator used by each plugin module."""
    def _inner(cls):
        _PLUGIN_REGISTRY[name] = cls()
        return cls
    return _inner


# --- auto-import everything inside plugins/ once ----------------
def _discover_plugins():
    pkg_dir = Path(__file__).with_suffix("") / "plugins"
    for f in pkg_dir.glob("*.py"):
        if f.name.startswith("_"):
            continue
        import_module(f"scripts.refactor.enrich_refactor_pkg.plugins.{f.stem}")

_discover_plugins()
# ----------------------------------------------------------------

from .quality_checker import merge_into_refactor_guard, merge_reports  # re-export
