"""
Black Plugin for Lint Report Package
===============================
This module provides a plugin for the Black code formatter, implementing the ToolPlugin interface.

It includes functionality to run Black on code and parse its output for formatting issues.
"""

from pathlib import Path
from typing import Dict, Any

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report
from ..path_utils import norm


class BlackPlugin(ToolPlugin):
    """
    Plugin for the Black code formatter.

    Attributes:
        name (str): The name of the plugin.
        default_report (Path): The default report file path.
    """
    name = "black"
    default_report = Path("black.txt")

    def run(self) -> int:
        """
        Run Black in check mode on the scripts directory.

        Returns:
            int: The exit code from the Black command.
        """
        return run_cmd(["black", "--check", "scripts"], self.default_report)

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        """
        Parse the output report from Black and update the destination dictionary.

        Args:
            dst (Dict[str, Dict[str, Any]]): Destination dictionary to update with formatting needs.
        """
        for line in read_report(self.default_report).splitlines():
            if "would reformat" in line:
                key = norm(line.split()[-1])
                dst.setdefault(key, {})["black"] = {"needs_formatting": True}
