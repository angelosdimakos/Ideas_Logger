import subprocess
from unittest.mock import patch
from scripts.utils.git_utils import get_changed_files, get_current_branch,interactive_commit_flow
import pytest


@patch("subprocess.run")
def test_get_changed_files_success(mock_run):
    """
    Unit tests for the get_changed_files function from scripts.utils.git_utils.

    These tests verify correct filtering of changed Python files, handling of non-Python files,
    empty outputs, and subprocess errors using mock patches for subprocess.run.
    """
    mock_run.return_value.stdout = "scripts/foo.py\nscripts/bar.txt\n"
    result = get_changed_files()
    assert result == ["scripts/foo.py"]


@patch("subprocess.run")
def test_get_changed_files_no_python_files(mock_run):
    """
    Unit tests for the get_changed_files function in scripts.utils.git_utils.

    These tests use mocking to verify correct behavior when filtering changed Python files,
    handling non-Python files, empty outputs, and subprocess errors.
    """
    mock_run.return_value.stdout = "README.md\nassets/logo.svg\n"
    result = get_changed_files()
    assert result == []


@patch("subprocess.run")
def test_get_changed_files_empty_output(mock_run):
    """
    Unit tests for the get_changed_files function in scripts.utils.git_utils.

    These tests use mocking to verify correct filtering of changed Python files, handling of non-Python files,
    empty outputs, and subprocess errors by patching subprocess.run.
    """
    mock_run.return_value.stdout = ""
    result = get_changed_files()
    assert result == []


@patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, ["git"]))
def test_get_changed_files_git_fails(mock_run):
    """
    Unit tests for the get_changed_files function in scripts.utils.git_utils.

    These tests use mocking to verify correct filtering of changed Python files, handling of non-Python files,
    empty outputs, and subprocess errors by patching subprocess.run.
    """
    result = get_changed_files()
    assert result == []

def test_get_current_branch_success():
    with patch("subprocess.check_output") as mock_output:
        mock_output.return_value = b"feature/test-branch\n"
        branch = get_current_branch()
        assert branch == "feature/test-branch"


def test_get_current_branch_failure(monkeypatch):
    def mock_check_output(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "git")

    monkeypatch.setattr(subprocess, "check_output", mock_check_output)
    with pytest.raises(subprocess.CalledProcessError):
        get_current_branch()


def test_interactive_commit_flow_accept(monkeypatch):
    inputs = iter(["main", "test message"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with patch("subprocess.run") as mock_run, patch("scripts.utils.git_utils.get_current_branch", return_value="feature/test-branch"):
        interactive_commit_flow()
        assert mock_run.call_count == 3
        mock_run.assert_any_call(["git", "add", "."])
        mock_run.assert_any_call(["git", "commit", "-m", "test message"])
        mock_run.assert_any_call(["git", "push", "origin", "main"])


def test_interactive_commit_flow_reject(monkeypatch):
    inputs = iter(["new", "test-branch", "some message"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with patch("subprocess.run") as mock_run, patch("scripts.utils.git_utils.get_current_branch", return_value="feature/test-branch"):
        interactive_commit_flow()
        assert mock_run.call_count == 4
        mock_run.assert_any_call(["git", "checkout", "-b", "test-branch"])
        mock_run.assert_any_call(["git", "add", "."])
        mock_run.assert_any_call(["git", "commit", "-m", "some message"])
        mock_run.assert_any_call(["git", "push", "--set-upstream", "origin", "test-branch"])