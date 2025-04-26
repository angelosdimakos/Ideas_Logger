from pathlib import Path
from typing import Dict, Any
import re

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report
from ..path_utils import norm


class BlackPlugin(ToolPlugin):
    name = "black"
    default_report = Path("black.txt")

    def run(self) -> int:
        return run_cmd(["black", "--check", "scripts"], self.default_report)

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        for line in read_report(self.default_report).splitlines():
            if "would reformat" in line:
                key = norm(line.split()[-1])
                dst.setdefault(key, {})["black"] = {"needs_formatting": True}
