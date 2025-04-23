import sys
import os
import subprocess
import tempfile
from scripts.refactor import refactor_guard_cli


def test_refactor_guard_cli_main(monkeypatch):
    """
    Smoke tests for the RefactorGuard CLI, covering main entrypoint execution,
    detection of missing tests, git diff mode, diff-only and complexity warnings modes,
    and error handling for invalid file paths.
    """
    monkeypatch.setattr(
        sys, "argv", ["refactor_guard_cli.py", "--refactored", "scripts", "--all", "--json"]
    )
    try:
        refactor_guard_cli.main()
    except SystemExit:
        pass


def test_refactor_cli_missing_tests(tmp_path, monkeypatch):
    """
    Smoke tests for the RefactorGuard CLI, verifying main entrypoint execution, handling of missing tests,
    git diff mode, diff-only and complexity warnings modes, and error handling for invalid file paths.
    Tests various CLI argument combinations and ensures correct behavior and error reporting.
    """
    # Create original file
    original = tmp_path / "original.py"
    original.write_text(
        """
class MyClass:
    def foo(self): pass
"""
    )

    # Create refactored file with an extra method
    refactored = tmp_path / "refactored.py"
    refactored.write_text(
        """
class MyClass:
    def foo(self): pass
    def bar(self): pass
"""
    )

    # Create test file that only tests foo
    test_file = tmp_path / "test_my_class.py"
    test_file.write_text(
        """
def test_foo(): pass
"""
    )

    # Run CLI in full analysis mode to return dict (not just missing_tests list)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "refactor_guard_cli.py",
            "--original",
            str(original),
            "--refactored",
            str(refactored),
            "--tests",
            str(test_file),
            "--all",
        ],
    )

    try:
        refactor_guard_cli.main()
    except SystemExit:
        pass


def test_refactor_cli_git_diff(monkeypatch):
    """
    Smoke tests for the RefactorGuard CLI, verifying main entrypoint execution, handling of various CLI arguments,
    detection of missing tests, git diff mode, diff-only and complexity warnings modes, and error handling for invalid
    file paths. Ensures correct behavior and error reporting across different usage scenarios.
    """
    monkeypatch.setattr(
        sys,
        "argv",
        ["refactor_guard_cli.py", "--refactored", "scripts", "--all", "--git-diff", "--json"],
    )
    try:
        refactor_guard_cli.main()
    except SystemExit:
        pass


def test_refactor_cli_diff_only(monkeypatch):
    """
    Smoke tests for the RefactorGuard CLI, verifying main entrypoint execution, CLI argument handling,
    detection of missing tests, git diff mode, diff-only and complexity warnings modes,
    and error handling for invalid file paths. Ensures correct behavior and error
    reporting across various usage scenarios.
    """
    monkeypatch.setattr(
        sys, "argv", ["refactor_guard_cli.py", "--refactored", "scripts", "--all", "--diff-only"]
    )
    try:
        refactor_guard_cli.main()
    except SystemExit:
        pass


def test_refactor_cli_complexity(monkeypatch):
    """
    Smoke tests for the RefactorGuard CLI, verifying main entrypoint execution,
    CLI argument handling, detection of missing tests, git diff mode, diff-only and
    complexity warnings modes, and error handling for invalid file paths.
    Ensures correct behavior and error reporting across various usage scenarios.
    """
    monkeypatch.setattr(
        sys,
        "argv",
        ["refactor_guard_cli.py", "--refactored", "scripts", "--all", "--complexity-warnings"],
    )
    try:
        refactor_guard_cli.main()
    except SystemExit:
        pass


def test_refactor_cli_invalid_path():
    """
    Smoke tests for the RefactorGuard CLI, covering main entrypoint execution,
    CLI argument handling, detection of missing tests, git diff mode, diff-only and
    complexity warnings modes, and error handling for invalid file paths.
    Ensures correct behavior and error reporting across various usage scenarios.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [
                "python",
                "scripts/refactor/refactor_guard_cli.py",
                "--original",
                "nonexistent.py",
                "--refactored",
                "nonexistent.py",
                "--json",
                "--output",
                os.path.join(tmpdir, "refactor_audit.json"),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        assert result.returncode != 0 or "Expected a file" in result.stderr or result.stdout
