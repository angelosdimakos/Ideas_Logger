# tests/integration/test_cli_single_file_json.py
import sys, json
from pathlib import Path
import pytest

from scripts.refactor import refactor_guard_cli

def make_simple_module(tmp_path):
    # Create a one‑file repo: foo.py
    mod = tmp_path / "foo.py"
    mod.write_text("""
class Foo:
    def bar(self):
        return 42
""", encoding="utf-8")
    # No tests, no coverage.xml
    return mod

def test_single_file_json(tmp_path, monkeypatch):
    foo = make_simple_module(tmp_path)

    # chdir into tmp_path so output ends up here
    monkeypatch.chdir(tmp_path)

    # Simulate CLI invocation
    sys.argv[:] = [
        "refactor_guard_cli.py",
        "--original", str(foo),
        "--refactored", str(foo),
        "--json"
    ]

    # Expect SystemExit so pytest won’t think it’s a failure
    with pytest.raises(SystemExit):
        refactor_guard_cli.main()

    # Now load refactor_audit.json
    audit = json.loads((tmp_path / "refactor_audit.json").read_text(encoding="utf-8"))

    # There should be one key, "foo.py", under "summary" (since it's single-file mode)
    assert "foo.py" in audit, f"Expected 'foo.py' in audit, got keys: {list(audit)}"
    summary = audit["foo.py"]

    # Check that method_diff, missing_tests, complexity all exist
    assert "method_diff" in summary
    assert "missing_tests" in summary
    assert "complexity" in summary

    # In this trivial case: no methods originally → no added/missing
    md = summary["method_diff"]["Foo"]
    assert md["missing"] == []
    assert md["added"]   == ["bar"]

    # No tests → missing_tests should flag bar
    assert {"class": "Foo", "method": "bar"} in summary["missing_tests"]

    # Complexity map should include "bar"
    comp = summary["complexity"]
    assert "bar" in comp and comp["bar"]["complexity"] >= 1
