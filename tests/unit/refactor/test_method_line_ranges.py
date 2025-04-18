# tests/unit/refactor/test_method_line_ranges.py

import pytest
from textwrap import dedent
import os

from scripts.refactor.method_line_ranges import extract_method_line_ranges


def test_no_functions(tmp_path):
    """When no functions or methods exist, the result should be empty."""
    code = "x = 1\nprint(x)\n"
    p = tmp_path / "nofunc.py"
    p.write_text(code, encoding="utf-8")
    result = extract_method_line_ranges(str(p))
    assert result == {}


def test_top_level_function(tmp_path):
    """A top-level function’s start and end lines are correctly recorded."""
    code = dedent("""\
        def foo():
            a = 1
            b = 2
            return a + b
    """)
    p = tmp_path / "foo.py"
    p.write_text(code, encoding="utf-8")
    result = extract_method_line_ranges(str(p))

    # Only 'foo' should be present
    assert set(result.keys()) == {"foo"}
    start, end = result["foo"]

    # Lines are 1-based: definition is on line 1; body ends on line 4
    assert start == 1
    assert end == 4


def test_class_methods_and_async(tmp_path):
    """Sync and async methods inside a class are captured with correct ranges."""
    code = dedent("""\
        class A:
            def sync(self):
                if True:
                    return 1
                return 0

            async def async_m(self):
                await self.do()
                await self.done()
    """)
    p = tmp_path / "a.py"
    p.write_text(code, encoding="utf-8")
    result = extract_method_line_ranges(str(p))

    # Expect two methods: A.sync and A.async_m
    assert set(result.keys()) == {"A.sync", "A.async_m"}

    sync_start, sync_end = result["A.sync"]
    async_start, async_end = result["A.async_m"]

    # 'sync' defined on line 2, ends on line 5
    assert sync_start == 2
    assert sync_end == 5

    # 'async_m' defined on line 7, ends on line 9
    assert async_start == 7
    assert async_end == 9


def test_nested_function_definitions_ignored(tmp_path):
    """Nested inner functions should not be recorded as top-level methods."""
    code = dedent("""\
        def outer():
            x = 1
            def inner():
                return x + 1
            return inner()
    """)
    p = tmp_path / "nested.py"
    p.write_text(code, encoding="utf-8")
    result = extract_method_line_ranges(str(p))

    # Only 'outer' should be recorded; 'inner' is nested and ignored
    assert set(result.keys()) == {"outer"}
    start, end = result["outer"]
    assert start == 1
    assert end == 5


def test_missing_file_raises(tmp_path):
    """Nonexistent file should raise FileNotFoundError."""
    missing = tmp_path / "does_not_exist.py"
    with pytest.raises(FileNotFoundError):
        extract_method_line_ranges(str(missing))


def test_syntax_error_raises(tmp_path):
    """Malformed Python should raise SyntaxError."""
    p = tmp_path / "bad.py"
    p.write_text("def bad(:\n    pass", encoding="utf-8")
    with pytest.raises(SyntaxError):
        extract_method_line_ranges(str(p))


def test_nested_classes(tmp_path):
    """Nested classes should both have their methods recorded."""
    code = dedent("""\
        class Outer:
            def foo(self):
                return 1

            class Inner:
                def bar(self):
                    return 2
    """)
    p = tmp_path / "nestedclass.py"
    p.write_text(code, encoding="utf-8")
    result = extract_method_line_ranges(str(p))

    # Expect both Outer.foo and Inner.bar
    assert set(result.keys()) == {"Outer.foo", "Inner.bar"}
    assert result["Outer.foo"][0] == 2  # 'def foo' is on line 2
    assert result["Inner.bar"][0] == 6  # 'def bar' is on line 6