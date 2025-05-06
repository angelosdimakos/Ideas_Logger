from pathlib import Path
from typing import Dict, Any
import re

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report
from ..path_utils import norm
from collections import defaultdict

class PydocstylePlugin(ToolPlugin):
    """
    A plugin for running the pydocstyle tool.

    This class is responsible for executing the pydocstyle command and parsing its
    output to identify any docstring issues in the specified scripts.
    """

    name = "pydocstyle"
    default_report = Path("pydocstyle.txt")

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
        """
        lines = read_report(self.default_report).splitlines()
        report = [line.strip() for line in lines if line.strip()]

        paired = zip(report[::2], report[1::2])

        for location, detail in paired:
            match = re.match(
                r"^(.*\.py):(\d+)\s+in\s+(?:public|private)?\s*(function|method|class|module)\s+`?([^\s:`]+)`?:?$",
                location
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
            dst.setdefault(key, {}).setdefault("pydocstyle", {}).setdefault("functions", {}).setdefault(label,
                                                                                                        []).append(
                entry)

