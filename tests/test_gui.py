import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from scripts.gui import ZephyrusLoggerGUI
from tests.test_utils import make_dummy_logger_core

@pytest.fixture
def gui_instance():
    root = tk.Tk()
    root.withdraw()  # Prevents GUI window from popping up
    gui = ZephyrusLoggerGUI(make_dummy_logger_core())
    yield gui
    root.destroy()

def test_gui_initializes(gui_instance):
    assert gui_instance.logger_core is not None
    assert gui_instance.status_var.get() == "Ready"

def test_log_message_adds_entry(gui_instance):
    gui_instance.log_text = MagicMock()
    gui_instance.log_text.config = MagicMock()
    gui_instance.log_text.insert = MagicMock()
    gui_instance.log_text.see = MagicMock()

    gui_instance.log_message("Test log")
    gui_instance.log_text.insert.assert_called()

def test_update_subcategories_sets_correct_values(gui_instance):
    gui_instance.sub_menu = {"menu": MagicMock()}
    gui_instance.selected_subcategory = tk.StringVar()
    gui_instance.category_structure = {"Main": ["Sub1", "Sub2"]}
    gui_instance._update_subcategories("Main")
    assert gui_instance.selected_subcategory.get() == "Sub1"

def test_save_entry_calls_logger(gui_instance):
    gui_instance.text_entry = MagicMock()
    gui_instance.text_entry.get.return_value = "Test Idea"
    gui_instance.selected_category_main = MagicMock()
    gui_instance.selected_category_main.get.return_value = "Main"
    gui_instance.selected_subcategory = MagicMock()
    gui_instance.selected_subcategory.get.return_value = "Sub"
    gui_instance.status_var = MagicMock()
    gui_instance.text_entry.delete = MagicMock()
    gui_instance.root = MagicMock()

    gui_instance._save_entry()
    gui_instance.text_entry.delete.assert_called()

def test_manual_summarize_shows_message_on_no_data(gui_instance):
    gui_instance.selected_category_main = MagicMock()
    gui_instance.selected_subcategory = MagicMock()
    gui_instance.selected_category_main.get.return_value = "Nonexistent"
    gui_instance.selected_subcategory.get.return_value = "None"

    with patch("pathlib.Path.read_text", return_value="{}"):
        with patch("tkinter.messagebox.showwarning") as mock_warn:
            gui_instance._manual_summarize()
            mock_warn.assert_called_once()
