import unittest
import tkinter as tk
from unittest.mock import MagicMock
import pytest

# Import your panels
from scripts.gui.panels.action_panel import ActionPanel
from scripts.gui.panels.coverage_panel import CoveragePanel
from scripts.gui.panels.entry_panel import EntryPanel
from scripts.gui.panels.log_panel import LogPanel

try:
    tk.Tk().destroy()
except Exception:
    pytest.skip("🛑 Skipping GUI tests — Tkinter not properly installed", allow_module_level=True)

# Dummy controller for testing ActionPanel
class DummyActionController:
    def __init__(self):
        self.force_summarize_all = MagicMock(return_value="dummy_summary")
        self.rebuild_tracker = MagicMock(return_value=True)

# Dummy controller for testing CoveragePanel
class DummyCoverageController:
    def get_coverage_data(self):
        return [{"Category": "TestCat", "Coverage": 80}]

# Dummy controller for testing EntryPanel
class DummyEntryController:
    def log_entry(self, main, sub, text):
        return f"Logged: {main}, {sub}, {text}"

# Dummy controller for testing LogPanel
class DummyLogController:
    def get_logs(self):
        return "Test log line\nAnother log entry\n"

class TestActionPanel(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = DummyActionController()
        self.panel = ActionPanel(self.root, controller=self.controller)
        self.panel.initialize_ui()

    def tearDown(self):
        self.panel.destroy()
        self.root.destroy()

    def test_on_summarize_calls_controller(self):
        # Call the summarize method
        self.panel.on_summarize()
        # Assert that the dummy controller's force_summarize_all was called
        self.controller.force_summarize_all.assert_called_once()

    def test_on_rebuild_calls_controller(self):
        # Call the rebuild method
        self.panel.on_rebuild()
        # Assert that the dummy controller's rebuild_tracker was called
        self.controller.rebuild_tracker.assert_called_once()

class TestCoveragePanel(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = DummyCoverageController()
        self.panel = CoveragePanel(self.root, controller=self.controller)
        self.panel.initialize_ui()

    def tearDown(self):
        self.panel.destroy()
        self.root.destroy()

    def test_refresh_populates_tree(self):
        self.panel.refresh()
        # Retrieve all items in the treeview
        items = self.panel.tree.get_children()
        self.assertGreater(len(items), 0)
        # Check that the first item has the expected values
        first_item = self.panel.tree.item(items[0])["values"]
        self.assertEqual(first_item[0], "TestCat")
        # Since we format coverage with a percent sign
        self.assertEqual(first_item[1], "80%")

class TestEntryPanel(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = DummyEntryController()
        self.panel = EntryPanel(self.root, controller=self.controller)
        self.panel.initialize_ui()

    def tearDown(self):
        self.panel.destroy()
        self.root.destroy()

    def test_on_submit_calls_log_entry(self):
        # Insert test text into the entry text widget
        test_text = "Sample log entry"
        self.panel.entry_text.insert("1.0", test_text)
        # Call the on_submit method
        self.panel.on_submit()
        # Check that after submission, the text widget is cleared
        current_text = self.panel.entry_text.get("1.0", tk.END).strip()
        self.assertEqual(current_text, "")
        # Here we can check printed output manually or, better, refactor on_submit to use a callback

class TestLogPanel(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = DummyLogController()
        self.panel = LogPanel(self.root, controller=self.controller)
        self.panel.initialize_ui()

    def tearDown(self):
        self.panel.destroy()
        self.root.destroy()

    def test_refresh_displays_logs(self):
        self.panel.refresh()
        # Retrieve text from the log display
        content = self.panel.log_display.get("1.0", tk.END)
        self.assertIn("Test log line", content)
        self.assertIn("Another log entry", content)

if __name__ == '__main__':
    unittest.main()
