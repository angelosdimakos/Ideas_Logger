"""
pydocstyle.py

This module provides the PydocstylePlugin class, which integrates the pydocstyle tool
for checking compliance with Python docstring conventions. It runs the tool and parses
its output for reporting issues.
"""
from pathlib import Path
from typing import Dict, Any

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report
from ..path_utils import norm

class PydocstylePlugin(ToolPlugin):
    """
       A plugin for running the pydocstyle tool.

       This class is responsible for executing the pydocstyle command and parsing its
       output to identify any docstring issues in the specified scripts.
       """

    name           = "pydocstyle"
    default_report = Path("pydocstyle.txt")

    def run(self) -> int:
        """
        Execute the pydocstyle tool on the scripts directory.

        Returns:
            int: The exit code from the pydocstyle command.
        """
        return run_cmd(["pydocstyle", "scripts"], self.default_report)

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        """
        Parse the output report from pydocstyle.

        Args:
            dst (Dict[str, Dict[str, Any]]): The destination dictionary to populate with issues.
        """
        for line in read_report(self.default_report).splitlines():
            if ":" not in line:
                continue
            key = norm(line.split(":", 1)[0])
            issues = dst.setdefault(key, {}).setdefault("pydocstyle", {"issues": []})["issues"]
            issues.append(line.strip())
