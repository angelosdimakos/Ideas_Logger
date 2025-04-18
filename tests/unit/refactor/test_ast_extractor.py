# tests/unit/refactor/test_ast_extractor.py

import pytest
import tempfile
import os
from textwrap import dedent

from scripts.refactor.ast_extractor import (
    ClassMethodInfo,
    extract_class_methods,
    compare_class_methods
)


def test_extract_class_methods_no_classes(tmp_path):
    """No classes in file → empty list."""
    p = tmp_path / "noclass.py"
    p.write_text("print('hi')", encoding="utf-8")

    result = extract_class_methods(str(p))
    assert isinstance(result, list)
    assert result == []


def test_extract_class_methods_single_class(tmp_path):
    """Extract one class with its methods and correct line ranges."""
    code = dedent("""\
        class Foo:
            def bar(self):
                pass

            def baz(self, x):
                return x

            async def qux(self):
                await something()
    """)
    p = tmp_path / "foo.py"
    p.write_text(code, encoding="utf-8")

    result = extract_class_methods(str(p))
    assert len(result) == 1
    info = result[0]
    assert isinstance(info, ClassMethodInfo)
    assert info.class_name == "Foo"

    # Expect exactly these methods
    methods = set(info.methods)
    assert methods == {"bar", "baz", "qux"}

    # Verify start ≤ end for each method
    for name, (start, end) in info.methods.items():
        assert isinstance(start, int) and isinstance(end, int)
        assert start <= end


def test_extract_class_methods_semantic_error(tmp_path):
    """
    Even if the method body is semantically invalid (undefined names),
    extract_class_methods should still parse and return the class/method.
    """
    p = tmp_path / "bad.py"
    # 'this is invalid' is valid syntax (a boolean expression), though 'this'/'invalid' are undefined at runtime
    p.write_text("class Bad:\n    def oops(self):\n        this is invalid\n", encoding="utf-8")

    result = extract_class_methods(str(p))
    # We still get one ClassMethodInfo for 'Bad' with method 'oops'
    assert len(result) == 1
    info = result[0]
    assert info.class_name == "Bad"
    assert "oops" in info.methods


def test_compare_class_methods():
    """compare_class_methods correctly finds added/missing methods."""
    orig = ClassMethodInfo("Test")
    orig.add_method("a", (1, 2))
    orig.add_method("b", (3, 4))

    ref = ClassMethodInfo("Test")
    ref.add_method("b", (3, 4))
    ref.add_method("c", (5, 6))

    diff = compare_class_methods(orig, ref)
    assert diff == {"missing": ["a"], "added": ["c"]}
