"""Auto-discover all ToolPlugin subclasses so the orchestrator can `import PLUGINS`."""

from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import List

from ..core import ToolPlugin

_PLUGIN_DIR = Path(__file__).parent
_PLUGINS: List[ToolPlugin] = []

for file in _PLUGIN_DIR.glob("*.py"):
    if file.name in {"__init__.py", "__pycache__"}:
        continue
    mod: ModuleType = import_module(f"{__name__}.{file.stem}")
    for obj in vars(mod).values():
        if isinstance(obj, type) and issubclass(obj, ToolPlugin) and obj is not ToolPlugin:
            _PLUGINS.append(obj())  # instantiate

# re-export
PLUGINS = _PLUGINS
