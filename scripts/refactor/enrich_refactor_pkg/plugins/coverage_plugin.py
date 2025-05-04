from __future__ import annotations
"""
Collect line-coverage percentages and inject them into the quality-checker
report. Skips execution when the current process is itself a pytest run
(to avoid closing sys.stdout while pytest is capturing).
"""

import os
import math
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict

from scripts.utils.file_utils import read_json
from ..core import ToolPlugin
from ..helpers import safe_print, run_cmd
from ..path_utils import norm


class CoveragePlugin(ToolPlugin):
    name = "coverage"
    default_report = Path("coverage.xml")  # default fallback

    def run(self) -> int:
        # Use JSON mode if explicitly requested via env var
        if os.getenv("COVERAGE_JSON") == "1":
            self.default_report = Path("coverage.json")
            return run_cmd(["coverage", "json"], self.default_report)
        return run_cmd(["coverage", "xml"], self.default_report)

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        if not self.default_report.exists():
            return

        if self.default_report.suffix == ".json":
            try:
                data = read_json(self.default_report)
                for file_rec in data.get("files", {}).values():
                    key   = norm(file_rec["filename"])
                    hits  = file_rec["summary"]["covered_lines"]
                    total = file_rec["summary"]["num_statements"] or 1
                    pct   = round(hits / total * 100, 1)
                    dst.setdefault(key, {})["coverage"] = {"percent": pct}
            except Exception as err:
                safe_print(f"⚠️  Failed to read JSON coverage report: {err}")
            return

        # ─── XML fallback ───
        try:
            root = ET.parse(self.default_report).getroot()
            for cls in root.findall(".//class"):
                fname = cls.get("filename")
                if not fname:
                    continue
                key = norm(fname)
                line_rate = float(cls.get("line-rate", "0.0"))
                percent = round(line_rate * 100, 1)
                dst.setdefault(key, {})["coverage"] = {"percent": percent}
        except Exception as err:
            safe_print(f"⚠️  Failed to parse XML coverage report: {err}")
