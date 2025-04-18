# tests/integration/test_cli_additional_modes.py

import sys
import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest

from scripts.refactor import refactor_guard_cli
from scripts.refactor.quality_checker import merge_into_refactor_guard

def run_cli(args, tmp_path):
    sys.argv = ["refactor_guard_cli.py"] + args
    with pytest.raises(SystemExit):
        refactor_guard_cli.main()
    return json.loads((tmp_path / "refactor_audit.json").read_text(encoding="utf-8"))


@pytest.fixture
def tmp_repo(tmp_path, monkeypatch):
    # Create original/refactored/tests directories
    orig = tmp_path / "original"; orig.mkdir()
    ref  = tmp_path / "refactored"; ref.mkdir()
    tests = tmp_path / "tests"; tests.mkdir()

    # chdir and PYTHONPATH for CLI imports
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).parents[2]))
    return orig, ref, tests, tmp_path


def test_removed_method_detection(tmp_repo):
    orig, ref, tests_dir, root = tmp_repo

    # original/foo.py has 'old' and 'kept'
    (orig / "foo.py").write_text(
        """
class Foo:
    def old(self): return 1
    def kept(self): return 2
""", encoding="utf-8")

    # refactored/foo.py only has 'kept'
    (ref / "foo.py").write_text(
        """
class Foo:
    def kept(self): return 2
""", encoding="utf-8")

    audit = run_cli(
        ["--original", "original", "--refactored", "refactored", "--all", "--json"],
        root
    )
    md = audit["foo.py"]["method_diff"]["Foo"]
    assert md["missing"] == ["old"]
    assert md["added"]   == []


def test_test_file_fallback(tmp_repo):
    orig, ref, tests_dir, root = tmp_repo

    # both original and refactored foo.py have methods keep & miss
    source = """
class Foo:
    def keep(self): pass
    def miss(self): pass
"""
    (orig / "foo.py").write_text(source, encoding="utf-8")
    (ref  / "foo.py").write_text(source, encoding="utf-8")

    # place test under tests/foo.py (fallback)
    (tests_dir / "foo.py").write_text(
        """
from refactored.foo import Foo

def test_keep():
    assert Foo().keep() is None
""", encoding="utf-8")

    audit = run_cli(
        ["--original", "original", "--refactored", "refactored",
         "--tests", "tests", "--all", "--json"],
        root
    )
    missing = audit["foo.py"]["missing_tests"]
    assert {"class":"Foo","method":"miss"} in missing


def test_coverage_by_basename(tmp_repo):
    orig, ref, tests_dir, root = tmp_repo

    # both original & ref foo.py have a()
    source = """
class Foo:
    def a(self): return 1
"""
    (orig / "foo.py").write_text(source, encoding="utf-8")
    (ref  / "foo.py").write_text(source, encoding="utf-8")

    # coverage.xml refers to a different path
    cov = ET.Element("coverage")
    cls = ET.SubElement(cov, "class", filename="/some/other/dir/foo.py")
    lines = ET.SubElement(cls, "lines")
    ET.SubElement(lines, "line", number="3", hits="1")
    (root / "coverage.xml").write_bytes(
        ET.tostring(cov, encoding="utf-8", xml_declaration=True)
    )

    audit = run_cli(
        ["--original", "original", "--refactored", "refactored", "--all", "--json"],
        root
    )
    comp = audit["foo.py"]["complexity"]
    assert comp["a"]["coverage"] == pytest.approx(1.0)


def test_malformed_coverage_warning(tmp_repo, capsys):
    orig, ref, tests_dir, root = tmp_repo

    # both original & ref foo.py have x()
    source = """
class Foo:
    def x(self): return 1
"""
    (orig / "foo.py").write_text(source, encoding="utf-8")
    (ref  / "foo.py").write_text(source, encoding="utf-8")

    # write malformed coverage.xml
    (root / "coverage.xml").write_text("<coverage><class></coverage>", encoding="utf-8")

    sys.argv = [
        "refactor_guard_cli.py",
        "--original", "original",
        "--refactored", "refactored",
        "--all"
    ]
    refactor_guard_cli.main()
    out = capsys.readouterr().out
    assert "⚠️  Coverage parsing failed" in out
    assert "📂 File: foo.py" in out


def test_quality_merge_round_trip(tmp_repo):
    orig, ref, tests_dir, root = tmp_repo

    # minimal foo.py
    (ref / "foo.py").write_text(
        """
class Foo:
    def x(self): return 1
""", encoding="utf-8")

    audit = run_cli(["--refactored", "refactored", "--all", "--json"], root)
    (root / "refactor_audit.json").write_text(
        json.dumps(audit), encoding="utf-8"
    )

    # fake lint report
    (root / "flake8.txt").write_text("foo.py:1:1: F401 unused import", encoding="utf-8")

    # fake coverage.xml with line-rate
    cov = ET.Element("coverage")
    ET.SubElement(cov, "class", filename="foo.py", **{"line-rate":"0.5"})
    (root / "coverage.xml").write_bytes(
        ET.tostring(cov, encoding="utf-8", xml_declaration=True)
    )

    merge_into_refactor_guard(str(root / "refactor_audit.json"))
    merged = json.loads((root / "refactor_audit.json").read_text(encoding="utf-8"))
    q = merged["foo.py"]["quality"]
    assert "flake8" in q and "coverage" in q


def test_missing_tests_json_flag(tmp_repo):
    orig, ref, tests_dir, root = tmp_repo

    # both original & ref foo.py have a() & b()
    source = """
class Foo:
    def a(self): pass
    def b(self): pass
"""
    (orig / "foo.py").write_text(source, encoding="utf-8")
    (ref  / "foo.py").write_text(source, encoding="utf-8")

    # no tests => all methods missing
    audit = run_cli(
        ["--original", "original", "--refactored", "refactored",
         "--all", "--missing-tests", "--json"],
        root
    )
    mts = audit["foo.py"]["missing_tests"]
    assert {"class":"Foo","method":"a"} in mts
    assert {"class":"Foo","method":"b"} in mts

def test_quality_merge_ci_structure(tmp_repo):
    import shutil
    orig, ref, tests_dir, root = tmp_repo

    # minimal foo.py in refactored
    (ref / "foo.py").write_text(
        """
class Foo:
    def x(self): return 1
""", encoding="utf-8")

    # run CLI to produce initial audit
    audit = run_cli(["--refactored", "refactored", "--all", "--json"], root)

    # create lint-reports directory as in CI
    lint = root / "lint-reports"; lint.mkdir()
    # fake black report
    (lint / "black.txt").write_text(
        "would reformat scripts/foo.py", encoding="utf-8"
    )
    # fake flake8 report
    (lint / "flake8.txt").write_text(
        "foo.py:1:1: F401 unused import", encoding="utf-8"
    )
    # fake mypy report
    (lint / "mypy.txt").write_text(
        "foo.py:1: error: Something wrong", encoding="utf-8"
    )
    # fake pydocstyle report
    (lint / "pydocstyle.txt").write_text(
        "foo.py:1: D100: Missing docstring", encoding="utf-8"
    )
    # fake coverage.xml with line-rate
    cov = ET.Element("coverage")
    ET.SubElement(cov, "class", filename="foo.py", **{"line-rate": "0.5"})
    (root / "coverage.xml").write_bytes(
        ET.tostring(cov, encoding="utf-8", xml_declaration=True)
    )

    # emulate CI step: copy reports to project root
    for fname in ["black.txt", "flake8.txt", "mypy.txt", "pydocstyle.txt"]:
        shutil.copy(lint / fname, root / fname)

    # merge quality data
    merge_into_refactor_guard(str(root / "refactor_audit.json"))
    merged = json.loads((root / "refactor_audit.json").read_text(encoding="utf-8"))
    q = merged["foo.py"]["quality"]
    assert "black" in q
    assert "flake8" in q
    assert "mypy" in q
    assert "pydocstyle" in q
    assert "coverage" in q

def test_nested_async_methods(tmp_repo):
    orig, ref, tests_dir, root = tmp_repo

    # original has nested class A.B.qux
    orig_source = """
class A:
    class B:
        def qux(self):
            if True:
                return 1
"""
    (orig / "foo.py").write_text(orig_source, encoding="utf-8")

    # refactored adds async quux with a comprehension
    ref_source = """
class A:
    class B:
        def qux(self):
            if True:
                return 1

        async def quux(self):
            return [x for x in range(3)]
"""
    (ref / "foo.py").write_text(ref_source, encoding="utf-8")

    # test only qux
    (tests_dir / "test_foo.py").write_text(
        """
from refactored.foo import A

def test_qux():
    assert A.B().qux() == 1
""", encoding="utf-8")

    # coverage.xml covers only qux's inner line
    cov = ET.Element("coverage")
    cls = ET.SubElement(cov, "class", filename=str(ref / "foo.py"))
    lines = ET.SubElement(cls, "lines")
    ET.SubElement(lines, "line", number="5", hits="1")
    (root / "coverage.xml").write_bytes(
        ET.tostring(cov, encoding="utf-8", xml_declaration=True)
    )

    audit = run_cli([
        "--original", "original",
        "--refactored", "refactored",
        "--tests", "tests",
        "--all", "--json"
    ], root)

    # method_diff for nested B should detect quux
    md = audit["foo.py"]["method_diff"]["B"]
    assert md["added"] == ["quux"]

    # missing_tests should flag quux
    mts = audit["foo.py"]["missing_tests"]
    assert {"class":"B","method":"quux"} in mts

    # complexity entries for both methods
    comp = audit["foo.py"]["complexity"]
    assert set(comp) == {"qux","quux"}
    # coverage: qux > 0, quux == 0
    assert comp["qux"]["coverage"] > 0.0
    assert comp["quux"]["coverage"] == 0.0
    assert comp["quux"]["complexity"] >= 1


def test_human_diff_only_mode(tmp_repo, capsys):
    orig, ref, tests_dir, root = tmp_repo

    # create foo.py with two methods
    source = """
class Foo:
    def x(self): return 1
    def y(self): return 2
"""
    (orig / "foo.py").write_text(source, encoding="utf-8")
    (ref / "foo.py").write_text(source, encoding="utf-8")

    # run human diff-only (no JSON)
    sys.argv = [
        "refactor_guard_cli.py",
        "--original", "original",
        "--refactored", "refactored",
        "--all", "--diff-only"
    ]
    refactor_guard_cli.main()
    out = capsys.readouterr().out

    # should show File header
    assert "📂 File: foo.py" in out
    # should NOT show complexity stats
    assert "📊 Total Complexity" not in out
    # method_diff still present in JSON only; human diff-only prints no details beyond header
    # but at minimum ensure no complexity lines

    orig, ref, tests_dir, root = tmp_repo

    # both original & ref foo.py have a() & b()
    source = """
class Foo:
    def a(self): pass
    def b(self): pass
"""
    (orig / "foo.py").write_text(source, encoding="utf-8")
    (ref / "foo.py").write_text(source, encoding="utf-8")

    # no tests => all methods missing
    audit = run_cli(
        ["--original", "original", "--refactored", "refactored",
         "--all", "--missing-tests", "--json"],
        root
    )
    mts = audit["foo.py"]["missing_tests"]
    assert {"class":"Foo","method":"a"} in mts
    assert {"class":"Foo","method":"b"} in mts


