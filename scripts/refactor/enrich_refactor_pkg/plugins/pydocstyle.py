from pathlib import Path
from typing import Dict, Any
import re

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report
from ..path_utils import norm


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
        return run_cmd(["pydocstyle", "--add-ignore=D204,D400,D401", "scripts"], self.default_report)

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        """
        Parse the output report from pydocstyle. Falls back to raw dump if parsing fails.

        Args:
            dst (Dict[str, Dict[str, Any]]): The destination dictionary to populate with issues.
        """
        issue_pattern = re.compile(r"^(.*\.py):(\d+):\s*(D\d+):\s*(.*)$")

        for line in read_report(self.default_report).splitlines():
            line = line.strip()
            match = issue_pattern.match(line)
            if match:
                path, lineno, code, msg = match.groups()
                key = norm(path)
                issue = {
                    "line": int(lineno),
                    "code": code,
                    "message": msg.strip(),
                    "raw": line
                }
            else:
                # fallback to raw dump, assign to "_unparsed"
                key = norm(line.split(":", 1)[0]) if ":" in line else "UNKNOWN"
                issue = {"raw": line}

            issues = dst.setdefault(key, {}).setdefault("pydocstyle", {}).setdefault("issues", [])
            issues.append(issue)
