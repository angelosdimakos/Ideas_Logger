# scripts/refactor/quality_registry.py
from typing import Callable, Dict, Any, List
from pathlib import Path

Plugin = Callable[[Dict[str, Dict[str, Any]], Dict[str, Path]], None]
_PLUGINS: List[Plugin] = []


def register(func: Plugin) -> Plugin:
    """Decorator to register a quality plug-in."""
    _PLUGINS.append(func)
    return func


def run_all(quality: Dict[str, Dict[str, Any]], report_paths: Dict[str, Path]) -> None:
    """Invoke every registered plug-in in order."""
    for plugin in _PLUGINS:
        plugin(quality, report_paths)
