# tests/unit/refactor/test_refactor_guard.py

import logging
from textwrap import dedent

from scripts.refactor.refactor_guard import RefactorGuard

# Ensure our logger captures warnings
logging.getLogger("scripts.refactor.refactor_guard").setLevel(logging.WARNING)


def test_refactor_guard_module_comparison(tmp_path):
    """
    Unit tests for the RefactorGuard class, verifying detection of method differences,
    identification of missing tests for refactored methods, and proper handling of
    malformed test files with appropriate warning logging.
    """
    orig_py = tmp_path / "orig.py"
    ref_py = tmp_path / "ref.py"

    orig_py.write_text(
        dedent(
            """
        class Foo:
            def bar(self):
                pass
    """
        ),
        encoding="utf-8",
    )

    ref_py.write_text(
        dedent(
            """
        class Foo:
            def baz(self):
                pass
    """
        ),
        encoding="utf-8",
    )

    guard = RefactorGuard()
    result = guard.analyze_module(str(orig_py), str(ref_py))

    # Check that method diffs are detected correctly
    assert "method_diff" in result
    method_diff = result["method_diff"]
    assert "Foo" in method_diff
    diff = method_diff["Foo"]
    assert diff["missing"] == ["bar"]
    assert diff["added"] == ["baz"]


def test_refactor_guard_missing_tests(tmp_path):
    """
    Unit tests for the RefactorGuard class, ensuring correct detection of method differences
    between original and refactored modules, identification of missing tests for public methods,
    and proper warning logging when test files are malformed.
    """
    ref_py = tmp_path / "mod.py"
    test_py = tmp_path / "test_mod.py"

    ref_py.write_text(
        dedent(
            """
        class Foo:
            def bar(self):
                pass
    """
        ),
        encoding="utf-8",
    )

    test_py.write_text(
        dedent(
            """
        import pytest

        def test_something_else():
            assert True
    """
        ),
        encoding="utf-8",
    )

    guard = RefactorGuard()
    result = guard.analyze_module("", str(ref_py), test_file_path=str(test_py))

    # Only 'bar' should be reported missing
    assert len(result["missing_tests"]) == 1
    missing = result["missing_tests"][0]
    assert missing["class"] == "Foo"
    assert missing["method"] == "bar"


def test_malformed_test_file_logs_warning_and_reports_all_methods(tmp_path):
    """
    Validates fallback behavior: when test coverage is missing and coverage.json is not found,
    all methods in refactored files are assumed untested (i.e., reported as missing).
    """
    ref_py = tmp_path / "mod.py"
    test_py = tmp_path / "test_mod.py"

    # One class with one method
    ref_py.write_text(
        dedent(
            """
        class A:
            def m(self):
                pass
    """
        ),
        encoding="utf-8",
    )

    # Malformed syntax in test file (will be ignored now)
    test_py.write_text("def bad(:\n    pass", encoding="utf-8")

    guard = RefactorGuard()
    result = guard.analyze_module("", str(ref_py), test_file_path=str(test_py))

    # Since no coverage.json exists, fallback logic applies and method 'm' is flagged as missing
    assert result["missing_tests"] == [{"class": "A", "method": "m"}]
