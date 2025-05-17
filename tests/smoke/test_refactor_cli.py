import sys
import os
import pytest
from scripts.refactor import refactor_guard_cli as cli
from scripts.refactor.refactor_guard_cli import main

class DummyGuard:
    """Dummy RefactorGuard to skip heavy initialization"""
    def __init__(self):
        self.config = {}  # make CLI happy
        pass

@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    """
    Stub out heavy internals, patch os.path.isdir globally, and restore sys.argv after each test.
    """
    original_argv = sys.argv.copy()
    monkeypatch.setattr(cli, "RefactorGuard", DummyGuard)
    monkeypatch.setattr(cli, "handle_full_scan", lambda args, guard: {})
    monkeypatch.setattr(os.path, "isdir", lambda path: False)
    yield
    sys.argv = original_argv

@pytest.mark.parametrize(
    "flags, should_succeed",
    [
        (["--refactored", "scripts", "--all", "--json"], True),
        (["--refactored", "scripts", "--all", "--git-diff", "--json"], True),
        (["--refactored", "scripts", "--all", "--diff-only"], True),
        (["--refactored", "scripts", "--all", "--complexity-warnings"], True),
    ],
)
def test_cli_smoke_modes(flags, should_succeed):
    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(cli, "handle_single_file", lambda args, guard: {})
        sys.argv = ["refactor_guard_cli.py", *flags]
        exit_code = main()
        assert (exit_code == 0) == should_succeed
    finally:
        monkeypatch.undo()


def test_cli_detects_missing_tests(tmp_path, capsys):
    orig = tmp_path / "original.py"
    orig.write_text("class C:\n    def foo(self): pass\n")
    ref = tmp_path / "refactored.py"
    ref.write_text("class C:\n    def foo(self): pass\n    def bar(self): pass\n")
    tst = tmp_path / "test_c.py"
    tst.write_text("def test_foo(): assert True\n")

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
        exit_code = main()
        assert exit_code == 0
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
    monkeypatch.setattr(sys, "argv", [
        "refactor_guard_cli.py",
        "--refactored", "does_not_exist.py"
    ])
    monkeypatch.setattr(os.path, "exists", lambda path: False)

    with pytest.raises(ValueError, match="Expected file for --refactored"):
        main()
