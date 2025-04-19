import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Sequence, Union
import os
import re

# Default report filenames
DEFAULT_REPORT_PATHS = {
    "black": Path("black.txt"),
    "flake8": Path("flake8.txt"),
    "mypy": Path("mypy.txt"),
    "pydocstyle": Path("pydocstyle.txt"),
    "coverage": Path("coverage.xml"),
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def _normalize(path: str) -> str:
    try:
        return str(Path(path).resolve().relative_to(PROJECT_ROOT))
    except Exception:
        return str(Path(path).name)

def run_command(cmd: Sequence[str], output_path: Union[str, os.PathLike]) -> int:
    result = subprocess.run(cmd, capture_output=True, text=True)
    combined = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    Path(output_path).write_text(combined.strip(), encoding="utf-8")
    return result.returncode

def run_black() -> int:
    return run_command(["black", "--check", "scripts"], DEFAULT_REPORT_PATHS["black"])

def run_flake8() -> int:
    return run_command(["flake8", "scripts"], DEFAULT_REPORT_PATHS["flake8"])

def run_mypy() -> int:
    return run_command(["mypy", "--strict", "--no-color-output", "scripts"], DEFAULT_REPORT_PATHS["mypy"])

def run_pydocstyle() -> int:
    return run_command(["pydocstyle", "scripts"], DEFAULT_REPORT_PATHS["pydocstyle"])

def run_coverage_xml() -> int:
    return run_command(["coverage", "xml"], DEFAULT_REPORT_PATHS["coverage"])

def _read_report(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def _add_flake8_quality(quality: Dict[str, Dict[str, Any]], report_paths) -> None:
    raw = _read_report(report_paths["flake8"])
    for line in raw.splitlines():
        m = re.match(r"([^:]+?):(\d+):(\d+):\s*([A-Z]\d+)\s*(.*)", line)
        if not m:
            continue
        file_path, line_no, col, code, msg = m.groups()
        key = _normalize(file_path)
        entry = quality.setdefault(key, {})
        entry.setdefault("flake8", {"issues": []})
        entry["flake8"]["issues"].append({
            "line": int(line_no), "column": int(col), "code": code, "message": msg
        })

def _add_black_quality(quality: Dict[str, Dict[str, Any]], report_paths) -> None:
    raw = _read_report(report_paths["black"])
    for line in raw.splitlines():
        if "would reformat" not in line:
            continue
        file_path = line.split()[-1]
        key = _normalize(file_path)
        entry = quality.setdefault(key, {})
        entry["black"] = {"needs_formatting": True}

def _add_mypy_quality(quality: Dict[str, Dict[str, Any]], report_paths) -> None:
    raw = _read_report(report_paths["mypy"])
    for l in raw.splitlines():
        if ".py" in l and ": error:" in l:
            file_path = l.split(":")[0]
            key = _normalize(file_path)
            entry = quality.setdefault(key, {}).setdefault("mypy", {"errors": []})
            entry["errors"].append(l.strip())

def _add_pydocstyle_quality(quality: Dict[str, Dict[str, Any]], report_paths) -> None:
    raw = _read_report(report_paths["pydocstyle"])
    for line in raw.splitlines():
        if ":" not in line:
            continue
        file_path = line.split(":", 1)[0]
        key = _normalize(file_path)
        entry = quality.setdefault(key, {}).setdefault("pydocstyle", {"issues": []})
        entry["issues"].append(line.strip())

def _add_coverage_quality(quality: Dict[str, Dict[str, Any]], report_paths) -> None:
    if not report_paths["coverage"].exists():
        return

    try:
        tree = ET.parse(str(report_paths["coverage"]))
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"⚠️ Malformed coverage XML: {e}")
        return

    for cls in root.findall(".//class"):
        raw_path = cls.attrib.get("filename")
        if not raw_path:
            continue
        key = _normalize(raw_path)
        rate = float(cls.attrib.get("line-rate", "0"))
        entry = quality.setdefault(key, {})["coverage"] = {"percent": round(rate * 100, 1)}

def merge_into_refactor_guard(audit_path: str = "refactor_audit.json", report_paths=None) -> None:
    audit_file = Path(audit_path)
    if not audit_file.exists():
        print("❌ Missing refactor audit JSON!")
        return

    try:
        audit = json.loads(audit_file.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        print(f"❌ Corrupt audit JSON: {e}")
        return

    report_paths = report_paths or DEFAULT_REPORT_PATHS
    quality_by_file: Dict[str, Dict[str, Any]] = {}

    _add_flake8_quality(quality_by_file, report_paths)
    _add_black_quality(quality_by_file, report_paths)
    _add_mypy_quality(quality_by_file, report_paths)
    _add_pydocstyle_quality(quality_by_file, report_paths)
    _add_coverage_quality(quality_by_file, report_paths)

    for file_path, qdata in quality_by_file.items():
        audit.setdefault(file_path, {}).setdefault("quality", {}).update(qdata)

    audit_file.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print("✅ RefactorGuard audit enriched with quality data!")