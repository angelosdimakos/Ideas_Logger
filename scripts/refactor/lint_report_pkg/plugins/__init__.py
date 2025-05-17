"""
Auto-discover all ToolPlugin subclasses so the orchestrator can `import PLUGINS`.
"""

import sys
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import List

from ..core import ToolPlugin

# ── Add repo root to sys.path to ensure absolute import success ──────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# ── Discovery ────────────────────────────────────────────────────────────────
_PLUGIN_DIR = Path(__file__).parent
_PLUGINS: List[ToolPlugin] = []

for file in _PLUGIN_DIR.glob("*.py"):
    if file.name in {"__init__.py", "__pycache__"}:
        continue

    try:
        mod: ModuleType = import_module(f"{__name__}.{file.stem}")
        for obj in vars(mod).values():
            if isinstance(obj, type) and issubclass(obj, ToolPlugin) and obj is not ToolPlugin:
                plugin = obj()
                _PLUGINS.append(plugin)
                print(f"[plugin loader] ✅ Loaded: {plugin.name} ({plugin.__class__.__name__})")
    except Exception as e:
        print(f"[plugin loader] ❌ Failed to load {file.stem}: {e}")

# ── Export for orchestrator ──────────────────────────────────────────────────
PLUGINS = _PLUGINS
