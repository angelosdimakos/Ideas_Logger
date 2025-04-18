# tests/unit/refactor/test_quality_checker.py

import json
import subprocess
from pathlib import Path
import pytest
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring

from scripts.refactor.quality_checker import (
    run_command,
    _read_report,
    _add_flake8_quality,
    _add_black_quality,
    _add_mypy_quality,
    _add_pydocstyle_quality,
    _add_coverage_quality,
    merge_into_refactor_guard,
    run_flake8,
    run_pydocstyle,
    run_coverage_xml,
    BLACK_REPORT,
    FLAKE8_REPORT,
    MYPY_REPORT,
    PYDOCSTYLE_REPORT,
    COVERAGE_XML,
)


@pytest.fixture(autouse=True)
def change_working_dir(tmp_path, monkeypatch):
    # Run each test in its own temp directory so report files land predictably
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_run_command_captures_stdout_and_stderr(tmp_path, monkeypatch):
    out_path = tmp_path / "out.txt"

    class FakeResult:
        stdout = "STDOUT_CONTENT"
        stderr = "STDERR_CONTENT"
        returncode = 42

    def fake_run(cmd, capture_output, text):
        return FakeResult()

    monkeypatch.setattr(subprocess, "run", fake_run)
    rc = run_command(["dummy"], str(out_path))
    assert rc == 42
    content = out_path.read_text(encoding="utf-8")
    assert "STDOUT_CONTENT" in content
    assert "STDERR_CONTENT" in content


def test_read_report(tmp_path):
    # Missing file -> empty string
    assert _read_report(Path("nofile.txt")) == ""

    # Existing file -> returns contents
    p = Path("report.txt")
    p.write_text("hello world", encoding="utf-8")
    assert _read_report(p) == "hello world"


def test_add_flake8_quality(change_working_dir):
    raw = "src/f1.py:10:5: E1 msg"
    Path(FLAKE8_REPORT.name).write_text(raw, encoding="utf-8")

    quality = {}
    _add_flake8_quality(quality)

    # key is normalized to 'f1.py'
    assert "f1.py" in quality
    entry = quality["f1.py"]["flake8"]
    assert entry["issues"] == [{"line": 10, "column": 5, "code": "E1", "message": "msg"}]
    assert entry["raw"] == raw


def test_add_black_quality(change_working_dir):
    raw = "would reformat scripts/a.py\n"
    Path(BLACK_REPORT.name).write_text(raw, encoding="utf-8")

    quality = {}
    _add_black_quality(quality)

    # path normalized to 'a.py'
    assert "a.py" in quality
    entry = quality["a.py"]["black"]
    assert entry["needs_formatting"] is True
    assert entry["raw"] == raw


def test_add_mypy_quality(change_working_dir):
    lines = [
        "scripts/x.py:5: error: oops",
        "not an error line",
    ]
    Path(MYPY_REPORT.name).write_text("\n".join(lines), encoding="utf-8")

    quality = {}
    _add_mypy_quality(quality)

    # key normalized to 'x.py'
    assert "x.py" in quality
    assert quality["x.py"]["mypy"]["errors"] == ["scripts/x.py:5: error: oops"]
    assert quality["x.py"]["mypy"]["raw"] == "\n".join(lines)


def test_add_pydocstyle_quality(change_working_dir):
    raw = "scripts/a.py:1 D100: Missing doc\nscripts/a.py:2 D102: Bad"
    Path(PYDOCSTYLE_REPORT.name).write_text(raw, encoding="utf-8")

    quality = {}
    _add_pydocstyle_quality(quality)

    # key normalized to 'a.py'
    assert "a.py" in quality
    issues = quality["a.py"]["pydocstyle"]["issues"]
    assert issues == raw.splitlines()
    assert quality["a.py"]["pydocstyle"]["raw"] == raw


def _write_xml(tmp_path, root):
    xml_bytes = tostring(root, encoding="utf-8", xml_declaration=True)
    p = tmp_path / "coverage.xml"
    p.write_bytes(xml_bytes)
    return str(p)


def test_add_coverage_quality_xml(change_working_dir):
    # Build coverage.xml with one class entry
    root = Element("coverage")
    cls = SubElement(root, "class", filename="src/foo.py", **{"line-rate": "0.75"})
    xml_path = _write_xml(change_working_dir, root)

    quality = {}
    _add_coverage_quality(quality)

    # key normalized to 'foo.py'
    assert "foo.py" in quality
    cov = quality["foo.py"]["coverage"]
    assert cov["percent"] == 75.0
    # raw contains the xml declaration
    assert "<?xml" in cov["raw"]


def test_merge_with_new_reports(change_working_dir):
    # Prepare audit JSON
    audit = {"a.py": {}}
    p = Path("refactor_audit.json")
    p.write_text(json.dumps(audit), encoding="utf-8")

    # Flake8
    fl = "a.py:1:2: E1 msg"
    Path(FLAKE8_REPORT.name).write_text(fl, encoding="utf-8")
    # Black
    Path(BLACK_REPORT.name).write_text("would reformat a.py\n", encoding="utf-8")
    # Mypy
    Path(MYPY_REPORT.name).write_text("a.py:2: error: bad\n", encoding="utf-8")
    # Pydocstyle
    Path(PYDOCSTYLE_REPORT.name).write_text("a.py:3: D100: Doc\n", encoding="utf-8")
    # Coverage XML
    root = Element("coverage")
    SubElement(root, "class", filename="a.py", **{"line-rate": "0.5"})
    _write_xml(change_working_dir, root)

    merge_into_refactor_guard()
    merged = json.loads(p.read_text(encoding="utf-8"))
    qual = merged["a.py"]["quality"]

    assert qual["flake8"]["issues"][0]["code"] == "E1"
    assert qual["black"]["needs_formatting"]
    assert qual["mypy"]["errors"][0].startswith("a.py:2")
    assert "pydocstyle" in qual
    assert "coverage" in qual
    assert qual["coverage"]["percent"] == 50.0


def test_run_flake8_and_others(monkeypatch, change_working_dir):
    calls = []

    def fake_run(cmd, output_path):
        calls.append((tuple(cmd), output_path))
        return 7

    import scripts.refactor.quality_checker as qc_mod
    monkeypatch.setattr(qc_mod, "run_command", fake_run)

    assert run_flake8() == 7
    assert run_pydocstyle() == 7
    assert run_coverage_xml() == 7

    assert calls[0][0] == ('flake8', 'scripts') and calls[0][1] == FLAKE8_REPORT
    assert calls[1][0] == ('pydocstyle', 'scripts') and calls[1][1] == PYDOCSTYLE_REPORT
    assert calls[2][0] == ('coverage', 'xml') and calls[2][1] == COVERAGE_XML
