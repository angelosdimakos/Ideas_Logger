from pathlib import Path
from typing import Dict, Any

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report
from ..path_utils import norm


class MypyPlugin(ToolPlugin):
    name = "mypy"
    default_report = Path("mypy.txt")

    def run(self) -> int:
        return run_cmd(["mypy", "--strict", "--no-color-output", "scripts"], self.default_report)

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        for line in read_report(self.default_report).splitlines():
            if ".py" in line and ": error:" in line:
                key = norm(line.split(":", 1)[0])
                lst = dst.setdefault(key, {}).setdefault("mypy", {"errors": []})["errors"]
                lst.append(line.strip())
