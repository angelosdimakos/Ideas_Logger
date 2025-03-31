import pytest
from scripts.utils import refactor_guard
import tempfile

pytestmark = [pytest.mark.unit]

def test_detects_added_method(tmp_path):
    original = tmp_path / "original.py"
    refactored = tmp_path / "refactored.py"

    original.write_text("""
class Dummy:
    def foo(self): pass
    def bar(self): pass
""")

    refactored.write_text("""
class Dummy:
    def foo(self): pass
    def bar(self): pass
    def baz(self): pass
""")

    result = refactor_guard.analyze_refactor_changes(original, refactored, as_string=False)
    assert "Dummy" in result["summary"]
    assert "baz" in result["summary"]["Dummy"]["added"]
    assert not result["summary"]["Dummy"]["missing"]

def test_detects_removed_method(tmp_path):
    original = tmp_path / "original.py"
    refactored = tmp_path / "refactored.py"

    original.write_text("""
class Dummy:
    def foo(self): pass
    def old(self): pass
""")

    refactored.write_text("""
class Dummy:
    def foo(self): pass
""")

    result = refactor_guard.analyze_refactor_changes(original, refactored, as_string=False)
    assert "Dummy" in result["summary"]
    assert "old" in result["summary"]["Dummy"]["missing"]
    assert not result["summary"]["Dummy"]["added"]

def test_detects_method_renames():
    original_code = "class Dummy:\n    def do_work(self): pass\n"
    refactored_code = "class Dummy:\n    def execute_task(self): pass\n"

    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".py") as orig_file, \
         tempfile.NamedTemporaryFile("w+", delete=False, suffix=".py") as ref_file:

        orig_file.write(original_code)
        orig_file.seek(0)
        ref_file.write(refactored_code)
        ref_file.seek(0)

        result = refactor_guard.analyze_refactor_changes(orig_file.name, ref_file.name, as_string=False)
        assert "Dummy" in result["summary"]
        assert "do_work" in result["summary"]["Dummy"]["missing"]
        assert "execute_task" in result["summary"]["Dummy"]["added"]

        rename_candidates = result.get("renamed_candidates", [])
        assert any(candidate["from"] == "do_work" and candidate["to"] == "execute_task" for candidate in rename_candidates)

def test_detects_test_coverage(tmp_path):
    original = tmp_path / "original.py"
    refactored = tmp_path / "refactored.py"
    test_file = tmp_path / "test_dummy.py"

    original.write_text("class Dummy:\n    def work(self): pass\n")
    refactored.write_text("class Dummy:\n    def work(self): pass\n    def new_func(self): pass\n")
    test_file.write_text("def test_work(): pass\n")

    result = refactor_guard.analyze_refactor_changes(original, refactored, test_file, as_string=False)
    assert "new_func" in result.get("missing_tests", [])
