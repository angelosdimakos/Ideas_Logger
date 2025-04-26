from pathlib import Path
from typing import Dict, Any
import xml.etree.ElementTree as ET

from ..core import ToolPlugin
from ..helpers import run_cmd, read_report, safe_print
from ..path_utils import norm


class CoveragePlugin(ToolPlugin):
    name = "coverage"
    default_report = Path("coverage.xml")

    def run(self) -> int:
        return run_cmd(["coverage", "xml"], self.default_report)

    def parse(self, dst: Dict[str, Dict[str, Any]]) -> None:
        if not self.default_report.exists():
            return
        try:
            root = ET.parse(self.default_report).getroot()
        except ET.ParseError as err:
            safe_print(f"⚠️  Malformed coverage XML: {err}")
            return

        for cls in root.findall(".//class"):
            fname = cls.get("filename")
            if not fname:
                continue
            key = norm(fname)
            percent = round(float(cls.get("line-rate", "0")) * 100, 1)
            dst.setdefault(key, {})["coverage"] = {"percent": percent}
