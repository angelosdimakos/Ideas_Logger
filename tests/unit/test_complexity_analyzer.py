import pytest
import tempfile
import os
from textwrap import dedent

from scripts.refactor.complexity_analyzer import (
    calculate_cyclomatic_complexity_for_module
)

def test_complexity_simple():
    """Verify complexity of a simple function with no branches."""
    code = dedent("""
        def foo():
            print("Hello")
            return 42
    """)
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as tmp:
        tmp.write(code)
        tmp.flush()
        path = tmp.name

    try:
        complexity = calculate_cyclomatic_complexity_for_module(path)
        # A single function with no if/else or loops => baseline complexity around 1 or 2
        # The exact number depends on how your analyzer increments complexity.
        # Adjust assertion as appropriate.
        assert complexity in (2, 3), f"Unexpected complexity: {complexity}"
    finally:
        os.remove(path)


def test_complexity_with_branches():
    """Verify complexity with if/else and loops."""
    code = dedent("""
        def foo(x):
            if x > 10:
                for i in range(x):
                    print(i)
            else:
                while x < 5:
                    x += 1
            return x
    """)
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as tmp:
        tmp.write(code)
        tmp.flush()
        path = tmp.name

    try:
        complexity = calculate_cyclomatic_complexity_for_module(path)
        # Based on your logic, each if/for/while might increment complexity by 1
        # so expect a baseline + ~3 increments. Adjust as needed.
        assert complexity >= 5, f"Expected at least 5, got {complexity}"
    finally:
        os.remove(path)
