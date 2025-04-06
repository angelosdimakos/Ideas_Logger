import pytest
import tempfile
import os
from textwrap import dedent

from scripts.refactor.refactor_guard import RefactorGuard

def test_refactor_guard_module_comparison():
    """Test analyzing two modules that differ slightly."""
    original_code = dedent("""
        class Foo:
            def bar(self):
                pass
    """)
    refactored_code = dedent("""
        class Foo:
            def baz(self):
                pass
    """)

    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as orig, \
         tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as ref:
        orig.write(original_code)
        ref.write(refactored_code)
        orig.flush()
        ref.flush()

        orig_path = orig.name
        ref_path = ref.name

    try:
        guard = RefactorGuard()
        result = guard.analyze_refactor_changes(orig_path, ref_path, as_string=False)
        # result is a dict with "summary", "missing_tests", etc.

        assert "summary" in result
        # Because we used single-file mode, "summary" should be a dict with method diffs
        summary = result["summary"]
        assert "method_diff" in summary, "Expect method_diff for single-file analysis"
        method_diff = summary["method_diff"]
        assert "Foo" in method_diff, "Class Foo should be recognized"
        diff = method_diff["Foo"]
        assert diff["missing"] == ["bar"]
        assert diff["added"] == ["baz"]

    finally:
        os.remove(orig_path)
        os.remove(ref_path)


def test_refactor_guard_missing_tests():
    """Check that the guard detects missing tests for refactored methods."""
    refactored_code = dedent("""
        class Foo:
            def bar(self):
                pass
    """)
    # Updated test code: removed any mention of 'bar'
    test_code = dedent("""
        import pytest

        def test_something_else():
            assert True
    """)

    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as ref, \
         tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as test:
        ref.write(refactored_code)
        test.write(test_code)
        ref.flush()
        test.flush()
        ref_path = ref.name
        test_path = test.name

    try:
        guard = RefactorGuard()
        # Pass an empty string for original_path to focus on missing test logic.
        result = guard.analyze_refactor_changes("", ref_path, test_file_path=test_path, as_string=False)
        assert len(result["missing_tests"]) == 1, "Expected one missing test"
        missing = result["missing_tests"][0]
        assert missing["class"] == "Foo"
        assert missing["method"] == "bar"
    finally:
        os.remove(ref_path)
        os.remove(test_path)