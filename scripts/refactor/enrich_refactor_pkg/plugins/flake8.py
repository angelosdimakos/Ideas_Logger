from pathlib import Path
from typing import Dict, Any
import re

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report
from ..path_utils import norm

_RGX = re.compile(r"([^:]+):(\d+):(\d+):\s*([A-Z]\d+)\s*(.*)")

class Flake8Plugin(ToolPlugin):
    name           = "flake8"
    default_report = Path("flake8.txt")

    def run(self) -> int:
        return run_cmd(["flake8", "scripts"], self.default_report)

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        for m in map(_RGX.match, read_report(self.default_report).splitlines()):
            if not m:
                continue
            fp, ln, col, code, msg = m.groups()
            key = norm(fp)
            issues = dst.setdefault(key, {}).setdefault("flake8", {"issues": []})["issues"]
            issues.append(
                {"line": int(ln), "column": int(col), "code": code, "message": msg}
            )
