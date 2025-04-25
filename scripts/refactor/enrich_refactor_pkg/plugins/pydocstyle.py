from pathlib import Path
from typing import Dict, Any

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report
from ..path_utils import norm

class PydocstylePlugin(ToolPlugin):
    name           = "pydocstyle"
    default_report = Path("pydocstyle.txt")

    def run(self) -> int:
        return run_cmd(["pydocstyle", "scripts"], self.default_report)

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        for line in read_report(self.default_report).splitlines():
            if ":" not in line:
                continue
            key = norm(line.split(":", 1)[0])
            issues = dst.setdefault(key, {}).setdefault("pydocstyle", {"issues": []})["issues"]
            issues.append(line.strip())
