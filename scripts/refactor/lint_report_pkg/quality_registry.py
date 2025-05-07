# scripts/refactor/quality_registry.py
"""
Quality Registry for Lint Report Package
===============================
This module provides functionality to register and run quality plugins.

It includes decorators for registering plugins and a method to invoke all registered plugins.
"""

from typing import Callable, Dict, Any, List
from pathlib import Path

Plugin = Callable[[Dict[str, Dict[str, Any]], Dict[str, Path]], None]
_PLUGINS: List[Plugin] = []


def register(func: Plugin) -> Plugin:
    """
    Decorator to register a quality plug-in.

    Args:
        func (Plugin): The plugin function to register.

    Returns:
        Plugin: The registered plugin function.
    """
    _PLUGINS.append(func)
    return func


def run_all(quality: Dict[str, Dict[str, Any]], report_paths: Dict[str, Path]) -> None:
    """
    Invoke every registered plug-in in order.

    Args:
        quality (Dict[str, Dict[str, Any]]): The quality data to pass to plugins.
        report_paths (Dict[str, Path]): The paths to the reports.
    """
    for plugin in _PLUGINS:
        plugin(quality, report_paths)
