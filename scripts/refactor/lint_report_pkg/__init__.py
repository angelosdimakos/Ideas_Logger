"""
Plugin-based quality-checker package.

`core.merge_into_refactor_guard()` is the only public entry-point most
code ever needs.
"""

from importlib import import_module
from pathlib import Path
from typing import Type, Callable, Dict

_PLUGIN_REGISTRY: Dict[str, "ToolPlugin"] = {}  # str → ToolPlugin


def register(name: str) -> Callable[[Type], Type]:
    """
    Decorator used by each plugin module to register it in the plugin registry.

    Args:
        name (str): The name to register the plugin under.

    Returns:
        Callable[[Type], Type]: A decorator that registers the class in the plugin registry.
    """

    def _inner(cls: Type) -> Type:
        _PLUGIN_REGISTRY[name] = cls()
        return cls

    return _inner


def _discover_plugins() -> None:
    """
    Discovers and imports all plugin modules in the 'plugins' directory.

    This function automatically imports all Python files in the 'plugins' directory,
    excluding those that start with an underscore.
    """
    pkg_dir = Path(__file__).with_suffix("") / "plugins"
    for f in pkg_dir.glob("*.py"):
        if f.name.startswith("_"):
            continue
        import_module(f"scripts.refactor.lint_report_pkg.plugins.{f.stem}")


_discover_plugins()

from .quality_checker import merge_into_refactor_guard, merge_reports  # re-export
