# tests/unit/refactor/test_ast_extractor.py

import pytest
import tempfile
import os
from textwrap import dedent

from scripts.refactor.ast_extractor import (
    ClassMethodInfo,
    extract_class_methods,
    compare_class_methods,
)


def test_extract_class_methods_no_classes(tmp_path):
    """
    Unit tests for the ast_extractor module, covering extraction of class methods and their line ranges,
    handling of files with no classes or semantic errors, and comparison of method sets between class versions.
    """
    p = tmp_path / "noclass.py"
    p.write_text("print('hi')", encoding="utf-8")

    result = extract_class_methods(str(p))
    assert isinstance(result, list)
    assert result == []


def test_extract_class_methods_single_class(tmp_path):
    """
    Unit tests for the ast_extractor module, verifying extraction of class methods and their line ranges,
    handling of files with no classes or with semantic errors, and comparison of method sets between class versions.
    """
    code = dedent(
        """\
        class Foo:
            def bar(self):
                pass

            def baz(self, x):
                return x

            async def qux(self):
                await something()
    """
    )
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
    Unit tests for the ast_extractor module, ensuring correct extraction of class methods and their line ranges,
    handling of files with no classes or semantic errors, and accurate comparison of method sets between class versions.
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
    """
    Unit tests for the ast_extractor module, verifying extraction of class methods and comparison of method sets.
    Tests include handling files with no classes, single classes with multiple methods, files with semantic errors,
    and comparison of method differences between class versions.
    """
    orig = ClassMethodInfo("Test")
    orig.add_method("a", (1, 2))
    orig.add_method("b", (3, 4))

    ref = ClassMethodInfo("Test")
    ref.add_method("b", (3, 4))
    ref.add_method("c", (5, 6))

    diff = compare_class_methods(orig, ref)
    assert diff == {"missing": ["a"], "added": ["c"]}
