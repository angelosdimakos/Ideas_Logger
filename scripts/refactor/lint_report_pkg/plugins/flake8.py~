"""
Flake8 Plugin for Lint Report Package
===============================
This module provides a plugin for the Flake8 linter, implementing the ToolPlugin interface.

It includes functionality to run Flake8 on code and parse its output for linting issues.
"""

from pathlib import Path
from typing import Dict, Any
import re

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report
from ..path_utils import norm

_RGX = re.compile(r"([^:]+):(\d+):(\d+):\s*([A-Z]\d+)\s*(.*)")


class Flake8Plugin(ToolPlugin):
    """
    Plugin for the Flake8 linter.

    Attributes:
        name (str): The name of the plugin.
        default_report (Path): The default report file path.
    """
    name: str = "flake8"
    default_report: Path = Path("flake8.txt")

    def run(self) -> int:
        """
        Run Flake8 on the scripts directory.

        Returns:
            int: The exit code from the Flake8 command.
        """
        return run_cmd(["flake8", "scripts"], self.default_report)

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        """
        Parse the output report from Flake8 and update the destination dictionary.

        Args:
            dst (Dict[str, Dict[str, Any]]): Destination dictionary to update with linting issues.
        """
        for m in map(_RGX.match, read_report(self.default_report).splitlines()):
            if not m:
                continue
            fp, ln, col, code, msg = m.groups()
            key = norm(fp)
            issues = dst.setdefault(key, {}).setdefault("flake8", {"issues": []})["issues"]
            issues.append({"line": int(ln), "column": int(col), "code": code, "message": msg})
