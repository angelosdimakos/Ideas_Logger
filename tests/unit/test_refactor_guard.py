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

        # Use analyze_module to get differences between original and refactored modules
        result = guard.analyze_module(orig_path, ref_path)

        # Check that method diffs are detected correctly
        assert "method_diff" in result, "Expect method_diff in result"
        method_diff = result["method_diff"]
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

        # Pass the test file path so that the missing tests logic is applied.
        result = guard.analyze_module("", ref_path, test_file_path=test_path)

        # Check for missing tests in the refactored code
        assert len(result["missing_tests"]) == 1, "Expected one missing test"
        missing = result["missing_tests"][0]
        assert missing["class"] == "Foo"
        assert missing["method"] == "bar"

    finally:
        os.remove(ref_path)
        os.remove(test_path)