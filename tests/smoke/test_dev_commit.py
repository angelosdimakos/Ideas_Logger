import os
import subprocess
from unittest.mock import patch, MagicMock

import pytest

from scripts.dev_commit import (
    get_current_branch,
    get_modified_files,
    is_valid_branch_name,
    generate_suggested_branch_name,
    switch_to_new_branch
)


class TestDevCommit:
    """
    Test suite for validating Git branch utilities in scripts.dev_commit, including branch name validation, suggested branch name generation, branch switching, and current branch retrieval. Covers both normal and edge cases using mocking and patching.
    """

    # ────────────────────────────
    # ✅ Branch Name Validation
    # ────────────────────────────
    def test_is_valid_branch_name(self):
        """
        Tests that is_valid_branch_name correctly identifies valid and invalid Git branch names.
        """
        assert is_valid_branch_name("feature/add-logging")
        assert is_valid_branch_name("fix/core/refactor")
        assert not is_valid_branch_name("bad branch name!")

    # ────────────────────────────
    # 🧠 Suggested Branch Name Logic
    # ────────────────────────────
    @patch("scripts.dev_commit.get_modified_files", return_value=["core/core_utils.py", "refactor/audit.py"])
    @patch("scripts.dev_commit.datetime")
    def test_generate_suggested_branch_name(self, mock_datetime, mock_get_files):
        """
        Tests that generate_suggested_branch_name returns a branch name starting with 'fix/' and ending with the mocked date, using mocked modified files and date.
        """
        mock_datetime.now.return_value.strftime.return_value = "2025-04-14"
        name = generate_suggested_branch_name()
        assert name.startswith("fix/")
        assert name.endswith("2025-04-14")

    # ────────────────────────────
    # 🌿 Branch Switching Logic
    # ────────────────────────────
    @patch("builtins.input", return_value="test-branch")
    @patch("subprocess.run")
    def test_switch_to_new_branch_success(self, mock_run, mock_input):
        """
        Tests that switch_to_new_branch successfully creates and switches to a new branch
        when a valid branch name is provided by the user.
        """
        mock_run.return_value = MagicMock(stdout="test-branch\n", returncode=0)
        switch_to_new_branch()
        mock_run.assert_any_call(["git", "checkout", "-b", "test-branch"], check=True)

    @patch("builtins.input", return_value="bad branch name!")
    def test_switch_to_new_branch_invalid_name(self, _):
        """
        Tests that switch_to_new_branch exits and prints an error message when an invalid branch name is provided by the user.
        """
        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            switch_to_new_branch()
            mock_exit.assert_called_once_with(1)
            mock_print.assert_any_call(
                "❌ Invalid branch name. Use only letters, numbers, dashes, slashes, and underscores."
            )

    # ────────────────────────────
    # 🧪 Git Branch Info Handling
    # ────────────────────────────
    def test_returns_correct_branch_name(self):
        """
        Tests that get_current_branch returns the correct current Git branch name by comparing it to the output of a direct Git command.
        """
        expected_branch = "main"
        actual_branch_process = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True
        )
        actual_branch = actual_branch_process.stdout.strip()

        result = get_current_branch()

        assert result == actual_branch
        assert result == expected_branch or actual_branch == result, (
            f"Expected '{expected_branch}' or actual '{actual_branch}', but got '{result}'"
        )

    def test_handles_not_in_git_repository(self):
        """
        Tests that get_current_branch raises a CalledProcessError when executed outside of a Git repository.
        """
        original_dir = os.getcwd()
        temp_dir = os.path.join(os.path.dirname(original_dir), "temp_non_git_dir")
        os.makedirs(temp_dir, exist_ok=True)
        os.chdir(temp_dir)

        try:
            with pytest.raises(subprocess.CalledProcessError):
                get_current_branch()
        finally:
            os.chdir(original_dir)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

    @patch("scripts.dev_commit.subprocess.run")
    def test_get_modified_files_returns_files(self,mock_run):
        # Simulate git diff output
        mock_run.return_value = MagicMock(stdout="file1.py\nfile2.py\n", returncode=0)
        files = get_modified_files()
        assert files == ["file1.py", "file2.py"]

    @patch("scripts.dev_commit.subprocess.run")
    def test_get_modified_files_returns_empty_when_no_changes(self,mock_run):
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        files = get_modified_files()
        assert files == []

    @patch("scripts.dev_commit.subprocess.run", side_effect=subprocess.CalledProcessError(1, "git"))
    def test_get_modified_files_handles_subprocess_error(self,mock_run):
        files = get_modified_files()
        assert files == []

    @patch("builtins.input", return_value="test-branch")
    @patch("scripts.dev_commit.generate_suggested_branch_name", return_value="test-branch")
    @patch("scripts.dev_commit.is_valid_branch_name", return_value=True)
    @patch("scripts.dev_commit.subprocess.run", side_effect=subprocess.CalledProcessError(1, "git"))
    def test_switch_to_new_branch_handles_git_error(self,mock_run, mock_valid, mock_suggested, mock_input):
        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            switch_to_new_branch()
            mock_exit.assert_any_call(1)
            assert mock_exit.call_count == 1
            mock_print.assert_any_call("❌ Git error: Command 'git' returned non-zero exit status 1.")
