# tests/unit/refactor/test_complexity_analyzer.py

import os
import tempfile
import pytest
from textwrap import dedent

from scripts.refactor.complexity.complexity_analyzer import (
    calculate_function_complexity_map,
    calculate_module_complexity,
    calculate_cyclomatic_complexity_for_module,
)


def _write_temp_file(code: str) -> str:
    """Helper to write code to a temp file and return its path."""
    tf = tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8")
    try:
        tf.write(code)
        tf.flush()
    finally:
        tf.close()
    return tf.name


def test_calculate_function_complexity_map_simple():
    """
    Unit tests for the complexity analyzer module.

    Tests calculation of cyclomatic complexity for functions, methods, and modules,
    including handling of nested functions, class methods, syntax errors, and
    deprecation warnings.
    """
    code = dedent(
        """
        def foo():
            return 42
    """
    )
    path = _write_temp_file(code)
    try:
        scores = calculate_function_complexity_map(path)
        assert isinstance(scores, dict)
        # Only 'foo' should be present with complexity 1
        assert list(scores.keys()) == ["foo"]
        assert scores["foo"] == 1
    finally:
        os.remove(path)


def test_calculate_module_complexity_simple():
    """
    Unit tests for the complexity analyzer module.

    Covers calculation of cyclomatic complexity for functions, methods, and modules,
    including handling of nested functions, class methods, syntax errors, and
    deprecation warnings. Ensures correct labeling and complexity values, and verifies
    behavior on parse errors.
    """
    code = dedent(
        """
        def foo():
            return

        def bar():
            if True:
                pass
    """
    )
    path = _write_temp_file(code)
    try:
        # foo complexity = 1, bar complexity = 2 => sum = 3, plus overhead = 4
        complexity = calculate_module_complexity(path)
        assert complexity == 4
    finally:
        os.remove(path)


def test_calculate_cyclomatic_alias_emits_warning_and_matches():
    """
    Unit tests for the complexity analyzer module.

    Tests calculation and labeling of cyclomatic complexity for functions, methods, and modules,
    including handling of nested functions, class methods, syntax errors, and deprecation warnings.
    """
    code = dedent(
        """
        def foo():
            for i in range(3):
                if i % 2 == 0:
                    pass
    """
    )
    path = _write_temp_file(code)
    try:
        with pytest.warns(DeprecationWarning):
            alias_value = calculate_cyclomatic_complexity_for_module(path)
        expected = calculate_module_complexity(path)
        assert alias_value == expected
    finally:
        os.remove(path)


def test_nested_functions_are_ignored():
    """
    Unit tests for the complexity analyzer module.

    Tests calculation and labeling of cyclomatic complexity for functions, methods, and modules,
    including handling of nested functions, class methods, syntax errors, and deprecation warnings.
    Ensures correct complexity values, proper labeling, and expected behavior on parse errors.
    """
    code = dedent(
        """
        def outer():
            def inner():
                if True:
                    pass
            if True:
                pass
    """
    )
    path = _write_temp_file(code)
    try:
        scores = calculate_function_complexity_map(path)
        # Only 'outer' should appear, 'inner' is skipped
        assert "outer" in scores and "inner" not in scores
        # Complexity of outer: baseline 1 + one 'if' = 2
        assert scores["outer"] == 2
    finally:
        os.remove(path)


def test_class_method_labels_and_complexity():
    """
    Unit tests for the complexity analyzer module.

    Covers calculation of cyclomatic complexity for functions, methods, and modules,
    including handling of nested functions, class methods, syntax errors, and
    deprecation warnings. Ensures correct complexity values, labeling, and expected
    behavior on parse errors.
    """
    code = dedent(
        """
        class A:
            def m1(self):
                if True:
                    pass

            async def m2(self):
                for i in []:
                    pass
    """
    )
    path = _write_temp_file(code)
    try:
        scores = calculate_function_complexity_map(path)
        # Expect two entries: 'A.m1' and 'A.m2'
        assert set(scores.keys()) == {"A.m1", "A.m2"}
        # m1: baseline 1 + if = 2; m2: baseline 1 + for = 2
        assert scores["A.m1"] == 2
        assert scores["A.m2"] == 2
    finally:
        os.remove(path)


def test_syntax_error_returns_empty_and_module_negative_one(capsys):
    """
    Unit tests for the complexity analyzer module.

    Tests calculation of cyclomatic complexity for functions, methods, and modules,
    including handling of nested functions, class methods, syntax errors, and
    deprecation warnings. Ensures correct complexity values, labeling, and expected
    behavior on parse errors.
    """
    code = "def oops(:\n    pass"
    path = _write_temp_file(code)
    try:
        # calculate_function_complexity_map prints warning and returns {}
        scores = calculate_function_complexity_map(path)
        assert scores == {}
        # calculate_module_complexity returns -1 on error
        complexity = calculate_module_complexity(path)
        assert complexity == -1
        # Warning should be printed to stdout
        captured = capsys.readouterr()
        assert "⚠️ Failed to parse for complexity" in captured.out
    finally:
        os.remove(path)
