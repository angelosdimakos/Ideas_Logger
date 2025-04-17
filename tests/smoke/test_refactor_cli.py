import sys
import pytest
from scripts.refactor import refactor_guard_cli


def test_refactor_guard_cli_main(monkeypatch):
    monkeypatch.setattr(sys, "argv", [
        "refactor_guard_cli.py",
        "--refactored", "scripts",
        "--all",
        "--json"
    ])
    try:
        refactor_guard_cli.main()
    except SystemExit:
        pass


def test_refactor_cli_missing_tests(tmp_path, monkeypatch):
    # Create original file
    original = tmp_path / "original.py"
    original.write_text("""
class MyClass:
    def foo(self): pass
""")

    # Create refactored file with an extra method
    refactored = tmp_path / "refactored.py"
    refactored.write_text("""
class MyClass:
    def foo(self): pass
    def bar(self): pass
""")

    # Create test file that only tests foo
    test_file = tmp_path / "test_my_class.py"
    test_file.write_text("""
def test_foo(): pass
""")

    # Run CLI in full analysis mode to return dict (not just missing_tests list)
    monkeypatch.setattr(sys, "argv", [
        "refactor_guard_cli.py",
        "--original", str(original),
        "--refactored", str(refactored),
        "--tests", str(test_file),
        "--all"
    ])

    try:
        refactor_guard_cli.main()
    except SystemExit:
        pass


def test_refactor_cli_git_diff(monkeypatch):
    monkeypatch.setattr(sys, "argv", [
        "refactor_guard_cli.py",
        "--refactored", "scripts",
        "--all",
        "--git-diff",
        "--json"
    ])
    try:
        refactor_guard_cli.main()
    except SystemExit:
        pass


def test_refactor_cli_diff_only(monkeypatch):
    monkeypatch.setattr(sys, "argv", [
        "refactor_guard_cli.py",
        "--refactored", "scripts",
        "--all",
        "--diff-only"
    ])
    try:
        refactor_guard_cli.main()
    except SystemExit:
        pass


def test_refactor_cli_complexity(monkeypatch):
    monkeypatch.setattr(sys, "argv", [
        "refactor_guard_cli.py",
        "--refactored", "scripts",
        "--all",
        "--complexity-warnings"
    ])
    try:
        refactor_guard_cli.main()
    except SystemExit:
        pass


def test_refactor_cli_invalid_path(monkeypatch):
    monkeypatch.setattr(sys, "argv", [
        "refactor_guard_cli.py",
        "--refactored", "nonexistent_path",
        "--all"
    ])
    try:
        refactor_guard_cli.main()
    except Exception:
        pass
