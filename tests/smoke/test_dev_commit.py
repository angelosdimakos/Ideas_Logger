import pytest
from unittest.mock import patch, MagicMock
from scripts.dev_commit import (
    get_current_branch,
    get_modified_files,
    is_valid_branch_name,
    generate_suggested_branch_name,
    switch_to_new_branch
)

def test_is_valid_branch_name():
    assert is_valid_branch_name("feature/add-logging")
    assert is_valid_branch_name("fix/core/refactor")
    assert not is_valid_branch_name("bad branch name!")

@patch("scripts.dev_commit.get_modified_files", return_value=["core/core_utils.py", "refactor/audit.py"])
@patch("scripts.dev_commit.datetime")
def test_generate_suggested_branch_name(mock_datetime, mock_get_files):
    mock_datetime.now.return_value.strftime.return_value = "2025-04-14"
    name = generate_suggested_branch_name()
    assert name.startswith("fix/")
    assert name.endswith("2025-04-14")

@patch("builtins.input", return_value="test-branch")
@patch("subprocess.run")
def test_switch_to_new_branch_success(mock_run, mock_input):
    mock_run.return_value = MagicMock(stdout="test-branch\n", returncode=0)
    switch_to_new_branch()
    mock_run.assert_any_call(["git", "checkout", "-b", "test-branch"], check=True)

@patch("builtins.input", return_value="bad branch name!")
def test_switch_to_new_branch_invalid_name(monkeypatch):
    with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
        switch_to_new_branch()
        # ✅ Ensure it was called once and *only* once
        mock_exit.assert_any_call(1)
        assert mock_exit.call_count == 1
        mock_print.assert_any_call("❌ Invalid branch name. Use only letters, numbers, dashes, slashes, and underscores.")

