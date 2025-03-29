from scripts.utils.gui_helpers import (
    get_current_date,
    get_current_timestamp,
    get_selected_option,
    append_log_entry,
    get_category_options,
)
from scripts.utils.file_utils import read_json, write_json
import tkinter.messagebox as messagebox
import pytest
pytestmark = [pytest.mark.unit]


def dummy_showwarning(title, message, **kwargs):
    """
    Dummy implementation of messagebox.showwarning that simply returns None, to be used in tests
    to avoid any GUI dialog.

    Parameters
    ----------
    title : str
        The title of the warning message
    message : str
        The message to be displayed
    **kwargs : dict
        Additional keyword arguments to be passed to messagebox.showwarning
    """
    return None


# In your test for validate_log_input in test_gui_helpers.py:
def test_validate_log_input(monkeypatch):
    """
    Test the validate_log_input function to ensure it correctly validates log input content.

    The test uses monkeypatch to replace the messagebox.showwarning function with a dummy function
    that does nothing, to avoid any GUI dialog during testing. It asserts that validate_log_input
    returns True for non-empty input and False for input that is only whitespace.
    """
    from scripts.utils.gui_helpers import validate_log_input
    monkeypatch.setattr(messagebox, "showwarning", dummy_showwarning)
    assert validate_log_input("Something here") is True
    assert validate_log_input("     ") is False


def test_get_current_date():
    """
    Test the get_current_date function to ensure it returns the current date as a string in the
    format "YYYY-MM-DD".

    The test asserts that the returned value is a string and that it has three hyphen-separated
    components, which are the year, month, and day of the month, respectively.
    """
    assert isinstance(get_current_date(), str)
    assert len(get_current_date().split("-")) == 3




def test_get_current_timestamp():
    """
    Test the get_current_timestamp function to ensure it returns the current timestamp as a string
    in the format "YYYY-MM-DD HH:MM:SS".

    The test asserts that the returned value is a string and that it contains a single space
    character, which is used to separate the date and time components of the timestamp.
    """
    assert isinstance(get_current_timestamp(), str)
    assert " " in get_current_timestamp()
    assert isinstance(get_current_timestamp(), str)
    assert " " in get_current_timestamp()


def test_get_selected_option():
    """
    Test the get_selected_option function to ensure it returns the correct value or the default
    value "General" when the input is empty.

    The test uses a mock variable class to simulate the OptionMenu variable passed to the
    get_selected_option function. It asserts that the returned value is correct for both a
    non-empty and empty input.
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
    Test the append_log_entry function to ensure it appends the log entry to the correct
    category and subcategory in the log file.

    The test uses a temporary file and the write_json function to create an empty log file.
    It then appends a log entry to the file and asserts that the entry is in the correct
    category and subcategory.
    """
    test_file = tmp_path / "test_log.json"
    write_json(test_file, {})

    append_log_entry(test_file, "2025-03-22", "Ideas", "Testing", "This is a test entry")

    data = read_json(test_file)
    assert "2025-03-22" in data
    assert "Ideas" in data["2025-03-22"]
    assert "Testing" in data["2025-03-22"]["Ideas"]
    assert data["2025-03-22"]["Ideas"]["Testing"][0]["content"] == "This is a test entry"




    # Valid case
def test_get_category_options(tmp_path):
    """
    Test the get_category_options function to ensure it correctly extracts category options
    from a JSON file.

    The test creates a temporary JSON file with a predefined categories structure and verifies
    that get_category_options returns the correct list of category keys. It also tests the
    function's behavior with an empty JSON file, asserting that an empty list is returned.

    Parameters
    ----------
    tmp_path : pathlib.Path
        A temporary path provided by pytest to create and manipulate files for testing.
    """

    # Valid case
    test_file = tmp_path / "categories.json"
    write_json(test_file, {"categories": {"Ideas": {}, "Logs": {}}})

    options = get_category_options(test_file)
    assert set(options) == {"Ideas", "Logs"}

    # Invalid case
    empty_file = tmp_path / "empty.json"
    write_json(empty_file, {})
    assert get_category_options(empty_file) == []

