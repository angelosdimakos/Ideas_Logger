"""
This module contains unit tests for the GUI helper functions in the Zephyrus application.

These tests validate the functionality of various GUI-related utilities, ensuring that they behave as expected.

Core features include:
- Testing date and timestamp retrieval functions.
- Validating log input for correctness.
- Ensuring category options are correctly retrieved.

Intended for use with pytest to facilitate automated testing in CI/CD workflows.
"""

import pytest
import tkinter.messagebox as messagebox
from scripts.utils.file_utils import read_json, write_json
from scripts.gui.gui_helpers import (
    get_current_date,
    get_current_timestamp,
    get_selected_option,
    append_log_entry,
    get_category_options,
    validate_log_input,
)

pytestmark = [pytest.mark.unit]


def dummy_showwarning(title: str, message: str, **kwargs) -> None:
    """
    A dummy function to replace the messagebox.showwarning function during testing.

    Args:
        title (str): The title of the warning message.
        message (str): The warning message content.
        kwargs: Additional keyword arguments (not used).

    Returns:
        None
    """
    return None


def test_validate_log_input(monkeypatch):
    """
    Test the validate_log_input function to ensure it correctly validates log entries.

    Args:
        monkeypatch: A pytest fixture to modify the behavior of the messagebox during testing.
    """
    monkeypatch.setattr(messagebox, "showwarning", dummy_showwarning)
    assert validate_log_input("Something here") is True
    assert validate_log_input("     ") is False


def test_get_current_date():
    """
    Test the get_current_date function to ensure it returns a valid date string.

    Returns:
        None
    """
    result = get_current_date()
    assert isinstance(result, str)
    assert len(result.split("-")) == 3


def test_get_current_timestamp():
    """
    Test the get_current_timestamp function to ensure it returns a valid timestamp string.

    Returns:
        None
    """
    result = get_current_timestamp()
    assert isinstance(result, str)
    assert " " in result


def test_get_selected_option():
    """
    Test the get_selected_option function to ensure it correctly retrieves the selected option.

    Returns:
        None
    """

    class MockVar:
        def __init__(self, value):
            self._value = value

        def get(self):
            return self._value

    assert get_selected_option(MockVar("Ideas")) == "Ideas"
    assert get_selected_option(MockVar("")) == "General"


def test_append_log_entry(tmp_path):
    """
    Test the append_log_entry function to ensure it correctly appends log entries to the log file.

    Args:
        tmp_path: A pytest fixture to create a temporary directory for testing.
    """
    test_file = tmp_path / "test_log.json"
    write_json(test_file, {})

    append_log_entry(test_file, "2025-03-22", "Ideas", "Testing", "This is a test entry")

    data = read_json(test_file)
    assert "2025-03-22" in data
    assert "Ideas" in data["2025-03-22"]
    assert "Testing" in data["2025-03-22"]["Ideas"]
    assert data["2025-03-22"]["Ideas"]["Testing"][0]["content"] == "This is a test entry"


def test_get_category_options(tmp_path):
    """
    Test the get_category_options function to ensure it correctly retrieves category options from the log file.

    Args:
        tmp_path: A pytest fixture to create a temporary directory for testing.
    """
    valid_file = tmp_path / "valid.json"
    write_json(valid_file, {"categories": {"Ideas": {}, "Logs": {}}})
    assert set(get_category_options(valid_file)) == {"Ideas", "Logs"}

    empty_file = tmp_path / "empty.json"
    write_json(empty_file, {})
    assert get_category_options(empty_file) == []

    broken_file = tmp_path / "broken.json"
    broken_file.write_text("{ this is invalid json", encoding="utf-8")
    assert get_category_options(broken_file) == []


def test_validate_log_input_none(monkeypatch):
    """
    Test the validate_log_input function to ensure it correctly handles None input.

    Args:
        monkeypatch: A pytest fixture to modify the behavior of the messagebox during testing.
    """
    monkeypatch.setattr(messagebox, "showwarning", dummy_showwarning)
    assert validate_log_input(None) is False


def test_append_log_entry_creates_nested_keys(tmp_path):
    """
    Test the append_log_entry function to ensure it correctly creates nested keys in the log file.

    Args:
        tmp_path: A pytest fixture to create a temporary directory for testing.
    """
    test_file = tmp_path / "log.json"
    write_json(test_file, {})  # start with flat file
    append_log_entry(test_file, "2025-03-22", "New", "Topic", "Log this entry")
    data = read_json(test_file)
    assert data["2025-03-22"]["New"]["Topic"][0]["content"] == "Log this entry"


def test_get_category_options_missing_key(tmp_path):
    """
    Test the get_category_options function to ensure it correctly handles missing keys in the log file.

    Args:
        tmp_path: A pytest fixture to create a temporary directory for testing.
    """
    file = tmp_path / "no_categories.json"
    write_json(file, {"not_categories": {}})
    assert get_category_options(file) == []
