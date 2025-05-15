"""
Pydocstyle Plugin for Lint Report Package
===============================
This module provides a plugin for the pydocstyle tool, implementing the ToolPlugin interface.

It includes functionality to run pydocstyle on code and parse its output for docstring issues.
"""

from pathlib import Path
from typing import Dict, Any
import re

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report
from ..path_utils import norm


class PydocstylePlugin(ToolPlugin):
    """
    Plugin for the pydocstyle tool.

    Attributes:
        name (str): The name of the plugin.
        default_report (Path): The default report file path.
    """

    name: str = "pydocstyle"
    default_report: Path = Path("pydocstyle.txt")

    def run(self) -> int:
        """
        Execute the pydocstyle tool on the scripts directory.

        Returns:
            int: The exit code from the pydocstyle command.
        """
        return run_cmd(
            ["pydocstyle", "--add-ignore=D202, D204,D400,D401", "scripts"], self.default_report
        )

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        """
        Parse pydocstyle output and inject docstring issues grouped by symbol with full detail.

        Args:
            dst (Dict[str, Dict[str, Any]]): Destination dictionary to update with docstring issues.
        """
        lines = read_report(self.default_report).splitlines()
        report = [line.strip() for line in lines if line.strip()]

        paired = zip(report[::2], report[1::2])

        for location, detail in paired:
            match = re.match(
                r"^(.*\.py):(\d+)\s+in\s+(?:public|private)?\s*(function|method|class|module)\s+`?([^\s:`]+)`?:?$",
                location,
            )
            if not match:
                continue

            path, lineno, scope, symbol = match.groups()
            key = norm(path)
            label = symbol if symbol else "<module>"

            code_match = re.match(r"^(D\d+):\s+(.*)$", detail)
            if not code_match:
                continue

            code, message = code_match.groups()

            entry = {"code": code, "message": message.strip()}
            dst.setdefault(key, {}).setdefault("pydocstyle", {}).setdefault(
                "functions", {}
            ).setdefault(label, []).append(entry)
