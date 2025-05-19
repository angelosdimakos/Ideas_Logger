import subprocess
from scripts.utils.git_utils import (
    get_changed_files,
    get_current_branch,
    interactive_commit_flow,
    get_added_modified_files,
    get_added_modified_py_files,
    get_changed_files_as_dict,
)

import pytest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import os
import platform
import time


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

    with (
        patch("subprocess.run") as mock_run,
        patch("scripts.utils.git_utils.get_current_branch", return_value="feature/test-branch"),
    ):
        interactive_commit_flow()
        assert mock_run.call_count == 3
        mock_run.assert_any_call(["git", "add", "."])
        mock_run.assert_any_call(["git", "commit", "-m", "test message"])
        mock_run.assert_any_call(["git", "push", "origin", "main"])


def test_interactive_commit_flow_reject(monkeypatch):
    inputs = iter(["new", "test-branch", "some message"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with (
        patch("subprocess.run") as mock_run,
        patch("scripts.utils.git_utils.get_current_branch", return_value="feature/test-branch"),
    ):
        interactive_commit_flow()
        assert mock_run.call_count == 4
        mock_run.assert_any_call(["git", "checkout", "-b", "test-branch"])
        mock_run.assert_any_call(["git", "add", "."])
        mock_run.assert_any_call(["git", "commit", "-m", "some message"])
        mock_run.assert_any_call(["git", "push", "--set-upstream", "origin", "test-branch"])


class TestGitUtils:
    """Tests for git utility functions."""

    @pytest.fixture
    def setup_git_repo(self):
        """Create a temporary git repository for testing."""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        original_dir = os.getcwd()

        try:
            # Change to the temporary directory
            os.chdir(temp_dir)

            # Initialize git
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], check=True)

            # Create and commit a file
            with open("initial.py", "w") as f:
                f.write("# Initial file")
            subprocess.run(["git", "add", "initial.py"], check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

            # Create a branch
            subprocess.run(["git", "checkout", "-b", "test-branch"], check=True)

            # Add a new file
            with open("added.py", "w") as f:
                f.write("# Added file")

            # Modify the initial file
            with open("initial.py", "w") as f:
                f.write("# Initial file - modified")

            # Add a non-python file
            with open("other.txt", "w") as f:
                f.write("Other file")

            # Commit changes
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Add and modify files"], check=True)

            yield temp_dir
        finally:
            # Change back to original directory
            os.chdir(original_dir)

            # Windows-specific cleanup to avoid permission errors
            if platform.system() == 'Windows':
                # First, try to close any git processes that might be holding files
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "git.exe"],
                                   stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)
                except:
                    pass

                # Wait a moment for file handles to be released
                time.sleep(0.5)

                # Try to clean up files with most restrictive permissions first
                try:
                    # Make files writable first
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                os.chmod(file_path, 0o666)
                            except:
                                pass

                    # Then try cleanup
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    # If cleanup fails, just ignore - the OS will clean up temp dirs eventually
                    pass
            else:
                # Non-Windows cleanup
                shutil.rmtree(temp_dir)

    def test_get_changed_files_original(self, setup_git_repo):
        """Test the original get_changed_files function still works."""
        temp_dir = setup_git_repo
        os.chdir(temp_dir)

        # Should find all changed Python files compared to master
        files = get_changed_files("master")
        assert len(files) == 2
        assert "added.py" in files
        assert "initial.py" in files
        assert "other.txt" not in files  # Should not include non-Python files

    def test_get_added_modified_files(self, setup_git_repo):
        """Test get_added_modified_files function."""
        temp_dir = setup_git_repo
        os.chdir(temp_dir)

        # Should find all added and modified files
        files = get_added_modified_files("master", "HEAD")
        assert len(files) == 3  # Should include added.py, initial.py, and other.txt
        assert "added.py" in files
        assert "initial.py" in files
        assert "other.txt" in files  # Should include non-Python files

    def test_get_added_modified_py_files(self, setup_git_repo):
        """Test get_added_modified_py_files function."""
        temp_dir = setup_git_repo
        os.chdir(temp_dir)

        # Should find only Python files that were added or modified
        files = get_added_modified_py_files("master", "HEAD")
        assert len(files) == 2
        assert "added.py" in files
        assert "initial.py" in files
        assert "other.txt" not in files  # Should not include non-Python files

    def test_get_changed_files_as_dict(self, setup_git_repo):
        """Test get_changed_files_as_dict function."""
        temp_dir = setup_git_repo
        os.chdir(temp_dir)

        # Should return a dictionary with changed_files key
        result = get_changed_files_as_dict("master", "HEAD")
        assert isinstance(result, dict)
        assert "changed_files" in result
        assert len(result["changed_files"]) == 3
        assert "added.py" in result["changed_files"]
        assert "initial.py" in result["changed_files"]
        assert "other.txt" in result["changed_files"]

    # In test_error_handling
    @patch('subprocess.run')
    def test_error_handling(self, mock_run):
        """Test error handling in git utility functions."""
        # Mock subprocess.run to raise an exception properly
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")  # Remove stdout, stderr args

        # All functions should return empty lists/dicts on error
        assert get_added_modified_files() == []
        assert get_added_modified_py_files() == []
        assert get_changed_files_as_dict() == {"changed_files": []}

