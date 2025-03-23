import pytest
import tempfile
import os
from pathlib import Path
from utils.gui_helpers import (
    validate_log_input,
    get_current_date,
    get_current_timestamp,
    get_selected_option,
    append_log_entry,
    get_category_options,
)
from utils.file_utils import read_json, write_json


def test_validate_log_input():
    assert validate_log_input("Something here") is True
    assert validate_log_input("     ") is False


def test_get_current_date():
    assert isinstance(get_current_date(), str)
    assert len(get_current_date().split("-")) == 3


def test_get_current_timestamp():
    assert isinstance(get_current_timestamp(), str)
    assert " " in get_current_timestamp()


def test_get_selected_option():
    class MockVar:
        def __init__(self, value):
            self._value = value
        def get(self):
            return self._value

    assert get_selected_option(MockVar("Ideas")) == "Ideas"
    assert get_selected_option(MockVar("")) == "General"


def test_append_log_entry(tmp_path):
    test_file = tmp_path / "test_log.json"
    write_json(test_file, {})

    append_log_entry(test_file, "2025-03-22", "Ideas", "Testing", "This is a test entry")

    data = read_json(test_file)
    assert "2025-03-22" in data
    assert "Ideas" in data["2025-03-22"]
    assert "Testing" in data["2025-03-22"]["Ideas"]
    assert data["2025-03-22"]["Ideas"]["Testing"][0]["content"] == "This is a test entry"


def test_get_category_options(tmp_path):
    # Valid case
    test_file = tmp_path / "categories.json"
    write_json(test_file, {"categories": {"Ideas": {}, "Logs": {}}})

    options = get_category_options(test_file)
    assert set(options) == {"Ideas", "Logs"}

    # Invalid case
    empty_file = tmp_path / "empty.json"
    write_json(empty_file, {})
    assert get_category_options(empty_file) == []
