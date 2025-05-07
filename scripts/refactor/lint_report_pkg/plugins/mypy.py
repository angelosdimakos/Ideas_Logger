"""
Mypy Plugin for Lint Report Package
===============================
This module provides a plugin for the MyPy type checker, implementing the ToolPlugin interface.

It includes functionality to run MyPy on code and parse its output for type checking errors.
"""


from pathlib import Path
from typing import Dict, Any

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report
from ..path_utils import norm


class MypyPlugin(ToolPlugin):
    """
    Plugin for the MyPy type checker.

    Attributes:
        name (str): The name of the plugin.
        default_report (Path): The default report file path.
    """
    name: str = "mypy"
    default_report: Path = Path("mypy.txt")

    def run(self) -> int:
        """
        Run MyPy in strict mode on the scripts directory.

        Returns:
            int: The exit code from the MyPy command.
        """
        return run_cmd(["mypy", "--strict", "--no-color-output", "scripts"], self.default_report)

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        """
        Parse the output report from MyPy and update the destination dictionary.

        Args:
            dst (Dict[str, Dict[str, Any]]): Destination dictionary to update with type checking errors.
        """
        for line in read_report(self.default_report).splitlines():
            if ".py" in line and ": error:" in line:
                key = norm(line.split(":", 1)[0])
                lst = dst.setdefault(key, {}).setdefault("mypy", {"errors": []})["errors"]
                lst.append(line.strip())
