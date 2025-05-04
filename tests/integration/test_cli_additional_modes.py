import sys
import json
from pathlib import Path
import pytest
from scripts.refactor import refactor_guard_cli
from scripts.refactor.enrich_refactor_pkg.quality_checker import merge_into_refactor_guard


def run_cli(args, tmp_path, monkeypatch):
    output = tmp_path / "refactor_audit.json"
    sys.argv = ["refactor_guard_cli.py"] + args + ["--output", str(output)]

    # Patch internals for speedup
    monkeypatch.setattr(refactor_guard_cli, "merge_into_refactor_guard", lambda *a, **k: None)

    try:
        exit_code = refactor_guard_cli.main()
        assert exit_code == 0
    except Exception as e:
        print(f"CLI execution failed: {e}")
        if output.exists():
            print(f"Output content: {output.read_text(encoding='utf-8')}")
        raise
    return json.loads(output.read_text(encoding="utf-8"))


@pytest.fixture
def tmp_repo(tmp_path, monkeypatch):
    orig = tmp_path / "original"
    orig.mkdir()
    ref = tmp_path / "refactored"
    ref.mkdir()
    tests = tmp_path / "tests"
    tests.mkdir()

    # Create a separate directory structure for quality reports
    reports = tmp_path / "reports"
    reports.mkdir()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).parents[2]))
    return orig, ref, tests, tmp_path, reports


def find_file_in_audit(audit, basename):
    """Helper to find a file in the audit regardless of path format."""
    for key in audit:
        if basename in key or key == basename:
            return audit[key]
    pytest.fail(f"Could not find {basename} in audit keys: {list(audit.keys())}")


def test_removed_method_detection(tmp_repo, monkeypatch):
    orig, ref, _, root, _ = tmp_repo
    (orig / "foo.py").write_text(
        "class Foo:\n def old(self): return 1\n def kept(self): return 2", encoding="utf-8"
    )
    (ref / "foo.py").write_text("class Foo:\n def kept(self): return 2", encoding="utf-8")

    audit = run_cli(["--original", str(orig), "--refactored", str(ref), "--json"], root, monkeypatch)
    file_data = find_file_in_audit(audit, "foo.py")
    md = file_data["method_diff"]["Foo"]

    assert md["missing"] == ["old"]
    assert md["added"] == []


def test_test_file_fallback(tmp_repo, monkeypatch):
    orig, ref, tests_dir, root, _ = tmp_repo
    code = "class Foo:\n def keep(self): pass\n def miss(self): pass"
    (orig / "foo.py").write_text(code, encoding="utf-8")
    (ref / "foo.py").write_text(code, encoding="utf-8")
    (tests_dir / "foo.py").write_text(
        "from refactored.foo import Foo\n\ndef test_keep(): assert Foo().keep() is None",
        encoding="utf-8",
    )

    audit = run_cli(
        ["--original", str(orig), "--refactored", str(ref), "--tests", str(tests_dir), "--json"],
        root,
        monkeypatch,
    )

    file_data = find_file_in_audit(audit, "foo.py")
    missing = file_data["missing_tests"]

    assert {"class": "Foo", "method": "miss"} in missing


def test_missing_tests_json_flag(tmp_repo, monkeypatch):
    orig, ref, _, root, _ = tmp_repo
    (orig / "foo.py").write_text(
        "class Foo:\n def a(self): pass\n def b(self): pass", encoding="utf-8"
    )
    (ref / "foo.py").write_text(
        "class Foo:\n def a(self): pass\n def b(self): pass", encoding="utf-8"
    )

    audit = run_cli(
        ["--original", str(orig), "--refactored", str(ref), "--missing-tests", "--json"],
        root,
        monkeypatch
    )

    file_data = find_file_in_audit(audit, "foo.py")
    mts = file_data["missing_tests"]

    assert {"class": "Foo", "method": "a"} in mts
    assert {"class": "Foo", "method": "b"} in mts
