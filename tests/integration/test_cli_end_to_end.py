import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from textwrap import dedent

import pytest

from scripts.refactor import refactor_guard_cli

@pytest.fixture
def sample_repo(tmp_path, monkeypatch):
    # Set up directories
    orig = tmp_path / "original"; orig.mkdir()
    ref  = tmp_path / "refactored"; ref.mkdir()
    tst  = tmp_path / "tests";    tst.mkdir()

    # original/foo.py
    (orig/"foo.py").write_text(dedent("""
        class Foo:
            def kept(self):
                return 1
    """), encoding="utf-8")

    # refactored/foo.py (added new())
    (ref/"foo.py").write_text(dedent("""
        class Foo:
            def kept(self):
                return 1

            def added(self):
                return 2
    """), encoding="utf-8")

    # tests/test_foo.py (only tests kept)
    (tst/"test_foo.py").write_text(dedent("""
        import pytest
        from refactored.foo import Foo

        def test_kept():
            assert Foo().kept() == 1
    """), encoding="utf-8")

    # tiny coverage.xml covering only line numbers 2–3 of refactored/foo.py
    root = ET.Element("coverage")
    cls  = ET.SubElement(root, "class", filename=str(ref/"foo.py"))
    lines = ET.SubElement(cls, "lines")
    # simulate coverage on 'kept' but not on 'added'
    ET.SubElement(lines, "line", number="3", hits="1")
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    (tmp_path/"coverage.xml").write_bytes(xml_bytes)

    # chdir into tmp_path so CLI writes here
    monkeypatch.chdir(tmp_path)
    # ensure our project root is on PYTHONPATH
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).parents[3]))
    return tmp_path

def test_cli_end_to_end(sample_repo):
    # Run the CLI
    sys.argv[:] = [
        "refactor_guard_cli.py",
        "--original",   "original",
        "--refactored", "refactored",
        "--tests",      "tests",
        "--all",
        "--json",
    ]
    with pytest.raises(SystemExit):
        refactor_guard_cli.main()

    # Load the output JSON
    audit = json.loads((sample_repo / "refactor_audit.json").read_text(encoding="utf-8-sig"))    # There should be exactly one file: "foo.py"
    assert "foo.py" in audit, "Expected foo.py in audit"
    summary = audit["foo.py"]

    # 1) method_diff picks up the added method
    md = summary["method_diff"]["Foo"]
    assert md["missing"] == [],            "No missing methods"
    assert md["added"]   == ["added"],     "Should detect 'added' method"

    # 2) missing_tests should flag the new method
    mt = summary["missing_tests"]
    assert {"class":"Foo","method":"added"} in mt

    # 3) complexity entries for both methods
    comp = summary["complexity"]
    assert set(comp) == {"kept","added"}
    # complexity of kept ≥ 1, of added ≥ 1
    assert comp["added"]["complexity"] >= 1

    # 4) coverage on 'kept' but not on 'added'
    assert comp["kept"]["coverage"] == pytest.approx(0.5)
    assert comp["added"]["coverage"] == 0.0

