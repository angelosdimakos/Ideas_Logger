from pathlib import Path
from typing import Dict, Any
import re

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report
from ..path_utils import norm

# Hardened regex and ANSI cleaner
_RGX = re.compile(r"^(.+?):(\d+):(\d+):\s+([A-Z]\d+)\s+(.*)$")
_ANSI = re.compile(r"\x1b\[[0-9;]*m")  # Matches terminal color codes


class Flake8Plugin(ToolPlugin):
    name: str = "flake8"
    default_report: Path = Path("flake8.txt")

    def run(self) -> int:
        # Force color off and safe config
        return run_cmd(
            ["flake8", "--color=never", "--config=.flake8", "scripts"], self.default_report
        )

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        # Read + clean up flake8 output
        raw_lines = read_report(self.default_report).splitlines()
        clean_lines = [
            _ANSI.sub("", line).strip().replace("\\", "/") for line in raw_lines if line.strip()
        ]

        for line in clean_lines:
            m = _RGX.match(line)
            if not m:
                continue  # Skip unparseable lines
            fp, ln, col, code, msg = m.groups()
            key = norm(fp)
            issues = dst.setdefault(key, {}).setdefault("flake8", {"issues": []})["issues"]
            issues.append(
                {
                    "line": int(ln),
                    "column": int(col),
                    "code": code,
                    "message": msg,
                }
            )
