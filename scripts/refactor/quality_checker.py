import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Sequence, Union
import os
import re

# Project root, used for normalizing paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Report filenames
BLACK_REPORT = Path("black.txt")
FLAKE8_REPORT = Path("flake8.txt")
MYPY_REPORT = Path("mypy.txt")
PYDOCSTYLE_REPORT = Path("pydocstyle.txt")
COVERAGE_XML = Path("coverage.xml")


def _normalize(path: str) -> str:
    """
    Normalize a file path to be relative to the project root.
    """
    try:
        return str(Path(path).resolve().relative_to(PROJECT_ROOT))
    except Exception:
        return str(Path(path).name)


def run_command(
    cmd: Sequence[str],
    output_path: Union[str, os.PathLike]
) -> int:
    """
    Run a command, capture stdout+stderr, write both into output_path.
    """
    result = subprocess.run(cmd, capture_output=True, text=True)
    combined = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    Path(output_path).write_text(combined.strip(), encoding="utf-8")
    return result.returncode


def run_black() -> int:
    """Run Black in check mode."""
    return run_command(["black", "--check", "scripts"], BLACK_REPORT)


def run_flake8() -> int:
    """Run Flake8 in text format."""
    return run_command(["flake8", "scripts"], FLAKE8_REPORT)


def run_mypy() -> int:
    """Run Mypy with strict settings."""
    return run_command(["mypy", "--strict", "--no-color-output", "scripts"], MYPY_REPORT)


def run_pydocstyle() -> int:
    """Run pydocstyle for docstring compliance."""
    return run_command(["pydocstyle", "scripts"], PYDOCSTYLE_REPORT)


def run_coverage_xml() -> int:
    """Generate coverage XML report."""
    return run_command(["coverage", "xml"], COVERAGE_XML)


def _read_report(path: Path) -> str:
    """Return full contents of a report or empty if missing."""
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _add_flake8_quality(quality: Dict[str, Dict[str, Any]]) -> None:
    raw = _read_report(FLAKE8_REPORT)
    for line in raw.splitlines():
        m = re.match(r"([^:]+?):(\d+):(\d+):\s*([A-Z]\d+)\s*(.*)", line)
        if not m:
            continue
        file_path, line_no, col, code, msg = m.groups()
        key = _normalize(file_path)
        entry = quality.setdefault(key, {})
        entry.setdefault("flake8", {"issues": []})
        entry["flake8"]["issues"].append({
            "line": int(line_no),
            "column": int(col),
            "code": code,
            "message": msg
        })


def _add_black_quality(quality: Dict[str, Dict[str, Any]]) -> None:
    raw = _read_report(BLACK_REPORT)
    for line in raw.splitlines():
        if "would reformat" not in line:
            continue
        file_path = line.split()[-1]
        key = _normalize(file_path)
        entry = quality.setdefault(key, {})
        entry["black"] = {"needs_formatting": True}


def _add_mypy_quality(quality: Dict[str, Dict[str, Any]]) -> None:
    raw = _read_report(MYPY_REPORT)
    for l in raw.splitlines():
        if ".py" in l and ": error:" in l:
            file_path = l.split(":")[0]
            key = _normalize(file_path)
            entry = quality.setdefault(key, {}).setdefault("mypy", {"errors": []})
            entry["errors"].append(l.strip())


def _add_pydocstyle_quality(quality: Dict[str, Dict[str, Any]]) -> None:
    raw = _read_report(PYDOCSTYLE_REPORT)
    for line in raw.splitlines():
        if ":" not in line:
            continue
        file_path = line.split(":", 1)[0]
        key = _normalize(file_path)
        entry = quality.setdefault(key, {}).setdefault("pydocstyle", {"issues": []})
        entry["issues"].append(line.strip())


def _add_coverage_quality(quality: Dict[str, Dict[str, Any]]) -> None:
    """
    Parse coverage.xml and record per-file line coverage percentage.
    """
    if not COVERAGE_XML.exists():
        return

    raw = _read_report(COVERAGE_XML)
    try:
        tree = ET.parse(str(COVERAGE_XML))
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"⚠️ Malformed coverage XML: {e}")
        return

    # Each <class> element has filename and line-rate (0.0–1.0)
    for cls in root.findall(".//class"):
        raw_path = cls.attrib.get("filename")
        if not raw_path:
            continue
        key = _normalize(raw_path)
        rate = float(cls.attrib.get("line-rate", "0"))
        entry = quality.setdefault(key, {})["coverage"] = {
            "percent": round(rate * 100, 1)


        }


def merge_into_refactor_guard(audit_path: str = "refactor_audit.json") -> None:
    """
    Enrich refactor_audit.json by inserting a 'quality' dict per file.
    """
    audit_file = Path(audit_path)
    if not audit_file.exists():
        print("❌ Missing refactor audit JSON!")
        return

    try:
        audit = json.loads(audit_file.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        print(f"❌ Corrupt audit JSON: {e}")
        return

    quality_by_file: Dict[str, Dict[str, Any]] = {}

    _add_flake8_quality(quality_by_file)
    _add_black_quality(quality_by_file)
    _add_mypy_quality(quality_by_file)
    _add_pydocstyle_quality(quality_by_file)
    _add_coverage_quality(quality_by_file)

    for file_path, qdata in quality_by_file.items():
        audit.setdefault(file_path, {}).setdefault("quality", {}).update(qdata)

    audit_file.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print("✅ RefactorGuard audit enriched with quality data!")
