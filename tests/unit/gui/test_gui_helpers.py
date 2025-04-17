import pytest
import tkinter.messagebox as messagebox
from scripts.utils.file_utils import read_json, write_json
from scripts.utils.gui_helpers import (
    get_current_date,
    get_current_timestamp,
    get_selected_option,
    append_log_entry,
    get_category_options,
    validate_log_input,
)

pytestmark = [pytest.mark.unit]

# ------------------- Dummy Messagebox Patcher -------------------

def dummy_showwarning(title, message, **kwargs):
    return None


# ----------------------- Unit Tests -----------------------

def test_validate_log_input(monkeypatch):
    monkeypatch.setattr(messagebox, "showwarning", dummy_showwarning)
    assert validate_log_input("Something here") is True
    assert validate_log_input("     ") is False


def test_get_current_date():
    result = get_current_date()
    assert isinstance(result, str)
    assert len(result.split("-")) == 3


def test_get_current_timestamp():
    result = get_current_timestamp()
    assert isinstance(result, str)
    assert " " in result


def test_get_selected_option():
    class MockVar:
        def __init__(self, value): self._value = value
        def get(self): return self._value

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
    valid_file = tmp_path / "valid.json"
    write_json(valid_file, {"categories": {"Ideas": {}, "Logs": {}}})
    assert set(get_category_options(valid_file)) == {"Ideas", "Logs"}

    empty_file = tmp_path / "empty.json"
    write_json(empty_file, {})
    assert get_category_options(empty_file) == []

    broken_file = tmp_path / "broken.json"
    broken_file.write_text("{ this is invalid json", encoding="utf-8")
    assert get_category_options(broken_file) == []
