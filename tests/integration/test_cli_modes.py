# tests/integration/test_cli_modes.py
import sys
import json
import os
from pathlib import Path
import pytest

from scripts.refactor import refactor_guard_cli

# Helper to create a simple repo structure
@pytest.fixture
def simple_repo(tmp_path, monkeypatch):
    # Create original and refactored directories
    orig = tmp_path / "original"; orig.mkdir()
    ref = tmp_path / "refactored"; ref.mkdir()
    tests_dir = tmp_path / "tests"; tests_dir.mkdir()

    # Write a simple module
    (orig / "foo.py").write_text("""
class Foo:
    def bar(self):
        return 42
""", encoding="utf-8")
    (ref / "foo.py").write_text("""
class Foo:
    def bar(self):
        return 42

    def baz(self):
        return 99
""", encoding="utf-8")

    # Write test file exercising only bar
    (tests_dir / "test_foo.py").write_text("""
from refactored.foo import Foo

def test_bar():
    assert Foo().bar() == 42
""", encoding="utf-8")

    # Write coverage.xml covering only line 3 of baz
    import xml.etree.ElementTree as ET
    root = ET.Element("coverage")
    cls = ET.SubElement(root, "class", filename=str(ref / "foo.py"))
    lines = ET.SubElement(cls, "lines")
    ET.SubElement(lines, "line", number="3", hits="1")
    (tmp_path / "coverage.xml").write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))

    # chdir and PYTHONPATH
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).parents[2]))
    return tmp_path


def run_cli(args, tmp_path, monkeypatch):
    sys.argv = ["refactor_guard_cli.py"] + args
    with pytest.raises(SystemExit):
        refactor_guard_cli.main()
    return json.loads((tmp_path / "refactor_audit.json").read_text(encoding="utf-8"))


def test_diff_only_skips_complexity(simple_repo, monkeypatch):
    audit = run_cli(
        ["--original", "original",
         "--refactored", "refactored",
         "--all", "--diff-only", "--json"],
        simple_repo,
        monkeypatch
    )
    summary = audit["foo.py"]
    assert "method_diff" in summary
    assert "missing_tests" in summary
    # complexity should be empty dict
    assert summary.get("complexity", {}) == {}


def test_missing_tests_human_output(simple_repo, capsys, monkeypatch):
    # human missing-tests requires --all
    sys.argv = [
        "refactor_guard_cli.py",
        "--original", "original",
        "--refactored", "refactored",
        "--tests", "tests",
        "--all",
        "--missing-tests"
    ]
    refactor_guard_cli.main()
    out = capsys.readouterr().out
    assert "🧪 Missing Tests:" in out
    assert "Foo → baz" in out


def test_complexity_warnings_human_output(simple_repo, capsys, monkeypatch):
    # human complexity-warnings requires --all
    # set max_complexity low to force warning for baz
    monkeypatch.setenv("MAX_COMPLEXITY", "0")
    sys.argv = [
        "refactor_guard_cli.py",
        "--original", "original",
        "--refactored", "refactored",
        "--all",
        "--complexity-warnings"
    ]
    refactor_guard_cli.main()
    out = capsys.readouterr().out
    assert "⚠️ baz" in out


def test_git_diff_json(simple_repo, monkeypatch):
    # stub get_changed_files to only include foo.py
    monkeypatch.setattr(
        "scripts.utils.git_utils.get_changed_files",
        lambda _: ["foo.py"]
    )
    audit = run_cli(
        ["--original", "original",
         "--refactored", "refactored",
         "--all", "--git-diff", "--json"],
        simple_repo,
        monkeypatch
    )
    # Only foo.py should be present
    assert set(audit.keys()) == {"foo.py"}


def test_missing_coverage_json(simple_repo, tmp_path, monkeypatch):
    # remove coverage.xml to simulate missing
    (simple_repo / "coverage.xml").unlink()
    audit = run_cli(
        ["--original", "original",
         "--refactored", "refactored",
         "--all", "--json"],
        simple_repo,
        monkeypatch
    )
    comp = audit["foo.py"]["complexity"]
    for stats in comp.values():
        assert stats["coverage"] == "N/A"
