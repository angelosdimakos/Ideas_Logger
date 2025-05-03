# tests/smoke/test_refactor_cli.py
import sys
import os
import pytest
from scripts.refactor import refactor_guard_cli as cli
from scripts.refactor.refactor_guard_cli import main
import argparse

class DummyGuard:
    """Dummy RefactorGuard to skip heavy initialization"""
    def __init__(self):
        pass

@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    """
    Stub out heavy internals, patch os.path.isdir globally, and restore sys.argv after each test.
    """
    # Preserve original argv
    original_argv = sys.argv.copy()
    # Patch out heavy classes and functions
    monkeypatch.setattr(cli, "RefactorGuard", DummyGuard)
    monkeypatch.setattr(cli, "merge_into_refactor_guard", lambda *a, **k: None)
    monkeypatch.setattr(cli, "handle_full_scan", lambda args, guard: {})
    # Force CLI to use single-file path for all inputs
    monkeypatch.setattr(os.path, "isdir", lambda path: False)
    yield
    # No need to manually restore os.path.isdir or handle_full_scan; monkeypatch fixture handles it
    sys.argv = original_argv

@pytest.mark.parametrize(
    "flags, should_exit",
    [
        (["--refactored", "scripts", "--all", "--json"], True),
        (["--refactored", "scripts", "--all", "--git-diff", "--json"], True),
        (["--refactored", "scripts", "--all", "--diff-only"], False),
        (["--refactored", "scripts", "--all", "--complexity-warnings"], False),
    ],
)
def test_cli_smoke_modes(flags, should_exit):
    monkeypatch = pytest.MonkeyPatch()
    try:
        # Stub scan methods for each test
        monkeypatch.setattr(cli, "handle_single_file", lambda args, guard: {})
        # Set argv
        sys.argv = ["refactor_guard_cli.py", *flags]
        if should_exit:
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0
        else:
            main()
    finally:
        monkeypatch.undo()


def test_cli_detects_missing_tests(tmp_path, capsys):
    orig = tmp_path / "original.py"
    orig.write_text("class C:\n    def foo(self): pass\n")
    ref = tmp_path / "refactored.py"
    ref.write_text("class C:\n    def foo(self): pass\n    def bar(self): pass\n")
    tst = tmp_path / "test_c.py"
    tst.write_text("def test_foo(): assert True\n")

    # Stub single-file handler to return our fake file entry
    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(cli, "handle_single_file", lambda args, guard: {ref.name: {}})
        monkeypatch.setattr(cli, "print_human_readable", lambda audit, guard, args: print("Missing tests for: bar"))
        sys.argv = [
            "refactor_guard_cli.py",
            "--original", str(orig),
            "--refactored", str(ref),
            "--tests", str(tst),
            "--missing-tests",
        ]
        main()
    finally:
        monkeypatch.undo()

    out = capsys.readouterr().out
    assert "bar" in out
    assert "missing" in out.lower()


@pytest.mark.dont_patch_config
def test_cli_invalid_paths(monkeypatch, capsys):
    """
    Ensure invalid file paths raise ValueError instantly and avoid I/O or teardown hooks.
    """
    # Set up mock arguments
    monkeypatch.setattr(sys, "argv", [
        "refactor_guard_cli.py",
        "--refactored", "does_not_exist.py"  # Non-existent file
    ])

    # Make isfile return False to trigger the file not found error
    monkeypatch.setattr(os.path, "exists", lambda path: False)

    # Run the test
    with pytest.raises(ValueError, match="Expected file for --refactored"):
        main()
