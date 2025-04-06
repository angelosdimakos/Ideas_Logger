import pytest
import tempfile
import os
from textwrap import dedent

from scripts.refactor.ast_extractor import (
    ClassMethodInfo,
    extract_class_methods,
    compare_class_methods
)

def test_extract_class_methods_no_classes():
    """Ensure no classes are found if the file contains none."""
    code = "print('Hello, world!')"
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as tmp:
        tmp.write(code)
        tmp.flush()
        path = tmp.name

    try:
        result = extract_class_methods(path)
        assert len(result) == 0, "No classes => empty list"
    finally:
        os.remove(path)


def test_extract_class_methods_single_class():
    """Check extraction of a single class with methods."""
    code = dedent("""
        class Foo:
            def bar(self):
                pass

            def baz(self, x):
                return x
    """)
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as tmp:
        tmp.write(code)
        tmp.flush()
        path = tmp.name

    try:
        result = extract_class_methods(path)
        assert len(result) == 1, "Should find exactly one class"
        cls_info = result[0]
        assert cls_info.class_name == "Foo"
        assert set(cls_info.methods.keys()) == {"bar", "baz"}, "Expected methods not found"
    finally:
        os.remove(path)


def test_compare_class_methods():
    """Test comparing two ClassMethodInfo objects."""
    original = ClassMethodInfo("TestClass")
    original.add_method("old_method", 10)
    original.add_method("shared_method", 15)

    refactored = ClassMethodInfo("TestClass")
    refactored.add_method("shared_method", 15)
    refactored.add_method("new_method", 20)

    diff = compare_class_methods(original, refactored)
    assert diff["missing"] == ["old_method"]
    assert diff["added"] == ["new_method"]
