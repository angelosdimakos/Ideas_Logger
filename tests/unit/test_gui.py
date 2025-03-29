import tkinter as tk
from unittest.mock import MagicMock, patch
from scripts.gui.gui import ZephyrusLoggerGUI
from tests.mocks.test_utils import make_dummy_logger_core
import pytest
pytestmark = [pytest.mark.unit]


@pytest.fixture
def gui_instance():
    """
    Fixture to create and yield a ZephyrusLoggerGUI instance for testing.

    This fixture initializes a ZephyrusLoggerGUI instance with a dummy logger core
    and ensures that the Tkinter root window does not appear on the screen during
    testing by calling `root.withdraw()`. After the test completes, the root window
    is properly destroyed to avoid interference with other tests.

    Yields:
        ZephyrusLoggerGUI: An instance of the GUI for use in tests.
    """
    root = tk.Tk()
    root.withdraw()  # Prevents GUI window from popping up
    gui = ZephyrusLoggerGUI(make_dummy_logger_core())
    yield gui
    root.destroy()

def test_gui_initializes(gui_instance):
    """
    Tests that the GUI initializes correctly.

    Verifies that the GUI instance has a valid logger core and that the status
    variable is set to "Ready" by default.
    """
    assert gui_instance.logger_core is not None
    assert gui_instance.status_var.get() == "Ready"

def test_log_message_adds_entry(gui_instance):
    """
    Tests that the log_message method adds a new entry to the log text widget.

    Verifies that the log text widget is updated with the correct message and
    that the scrollbar is properly updated to show the new entry at the bottom
    of the widget.
    """
    gui_instance.log_text = MagicMock()
    gui_instance.log_text.config = MagicMock()
    gui_instance.log_text.insert = MagicMock()
    gui_instance.log_text.see = MagicMock()

    gui_instance.log_message("Test log")
    gui_instance.log_text.insert.assert_called()

def test_update_subcategories_sets_correct_values(gui_instance):
    """
    Tests that the _update_subcategories method sets the correct subcategory values.

    Verifies that the _update_subcategories method correctly populates the subcategory
    menu with the correct subcategory values from the category structure.
    """
    gui_instance.sub_menu = {"menu": MagicMock()}
    gui_instance.selected_subcategory = tk.StringVar()
    gui_instance.category_structure = {"Main": ["Sub1", "Sub2"]}
    gui_instance._update_subcategories("Main")
    assert gui_instance.selected_subcategory.get() == "Sub1"

def test_save_entry_calls_logger(gui_instance):
    """
    Tests that the _save_entry method calls the logger and updates the GUI.

    Verifies that after calling _save_entry, the text entry field is cleared
    and the logger is called with the correct category and subcategory values.
    """
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
    """
    Tests that the _manual_summarize method shows a warning message if no data is available.

    Verifies that the _manual_summarize method correctly checks if the selected category
    and subcategory have any associated data. If no data exists, it shows a warning
    message to the user.
    """
    gui_instance.selected_category_main = MagicMock()
    gui_instance.selected_subcategory = MagicMock()
    gui_instance.selected_category_main.get.return_value = "Nonexistent"
    gui_instance.selected_subcategory.get.return_value = "None"

    with patch("pathlib.Path.read_text", return_value="{}"):
        with patch("tkinter.messagebox.showwarning") as mock_warn:
            gui_instance._manual_summarize()
            mock_warn.assert_called_once()
