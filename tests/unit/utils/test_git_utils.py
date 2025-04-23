import subprocess
from unittest.mock import patch
from scripts.utils.git_utils import get_changed_files


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
