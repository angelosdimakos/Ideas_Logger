import sys
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest

from scripts.refactor import refactor_guard_cli


@pytest.fixture
def simple_repo(tmp_path, monkeypatch):
    # Create dirs
    orig = tmp_path / "original"
    orig.mkdir()
    ref = tmp_path / "refactored"
    ref.mkdir()
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()

    # Source code
    (orig / "foo.py").write_text(
        """
class Foo:
    def bar(self):
        return 42
""",
        encoding="utf-8",
    )

    (ref / "foo.py").write_text(
        """
class Foo:
    def bar(self):
        return 42

    def baz(self):
        return 99
""",
        encoding="utf-8",
    )

    # Minimal test
    (tests_dir / "test_foo.py").write_text(
        """
from refactored.foo import Foo

def test_bar():
    assert Foo().bar() == 42
""",
        encoding="utf-8",
    )

    # Coverage XML
    root = ET.Element("coverage")
    cls = ET.SubElement(root, "class", filename=str(ref / "foo.py"))
    lines = ET.SubElement(cls, "lines")
    ET.SubElement(lines, "line", number="3", hits="1")
    (tmp_path / "coverage.xml").write_bytes(
        ET.tostring(root, encoding="utf-8", xml_declaration=True)
    )

    # Test env setup
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).parents[2]))
    return tmp_path


def run_cli(args, tmp_path):
    output_path = tmp_path / "refactor_audit.json"
    args += ["--output", str(output_path)]

    cli_script = Path(__file__).parents[2] / "scripts" / "refactor" / "refactor_guard_cli.py"
    result = subprocess.run(
        ["python", str(cli_script)] + args,
        cwd=tmp_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore",
        check=True,
    )

    return json.loads(output_path.read_text(encoding="utf-8"))


def test_diff_only_skips_complexity(simple_repo):
    audit = run_cli(["--refactored", "refactored", "--all", "--json", "--diff-only"], simple_repo)

    # Fix: Check if any file entry exists in the audit before accessing complexity
    assert any(file_data.get("complexity", {}) == {} for file_data in audit.values())


def test_missing_tests_human_output(simple_repo, capsys):
    sys.argv = [
        "refactor_guard_cli.py",
        "--original",
        "original",
        "--refactored",
        "refactored",
        "--tests",
        "tests",
        "--all",
        "--missing-tests",
    ]
    refactor_guard_cli.main()
    out = capsys.readouterr().out
    assert "🧪 Missing Tests:" in out
    assert "Foo → baz" in out


def test_complexity_warnings_human_output(simple_repo, capsys, monkeypatch):
    monkeypatch.setenv("MAX_COMPLEXITY", "0")
    sys.argv = [
        "refactor_guard_cli.py",
        "--original",
        "original",
        "--refactored",
        "refactored",
        "--all",
        "--complexity-warnings",
    ]
    refactor_guard_cli.main()
    out = capsys.readouterr().out
    assert "⚠️ baz" in out


def test_git_diff_json(simple_repo, monkeypatch):
    # Create a mock get_changed_files function that returns foo.py
    def mock_get_changed_files(_):
        return ["foo.py"]

    monkeypatch.setattr("scripts.utils.git_utils.get_changed_files", mock_get_changed_files)

    audit = run_cli(
        ["--original", "original", "--refactored", "refactored", "--all", "--git-diff", "--json"],
        simple_repo,
    )

    # Fix: Check if any key in audit contains 'foo.py'
    assert any("foo.py" in key for key in audit.keys())


def test_missing_coverage_json(simple_repo):
    (simple_repo / "coverage.xml").unlink()
    audit = run_cli(
        ["--original", "original", "--refactored", "refactored", "--all", "--json"], simple_repo
    )

    # Fix: Find the key containing foo.py
    for key, value in audit.items():
        if "foo.py" in key:
            comp = value["complexity"]
            for stats in comp.values():
                assert stats["coverage"] == "N/A"
            break
    else:
        pytest.fail("Could not find 'foo.py' in audit keys")
