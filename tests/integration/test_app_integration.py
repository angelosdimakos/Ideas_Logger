import unittest
import tkinter as tk
from unittest.mock import MagicMock

from scripts.gui.tabs.main_tab import MainTab


# Dummy integration controller that simulates backend behavior
class DummyIntegrationController:
    def __init__(self):
        self.logs = "Initial logs\n"

    def log_entry(self, main, sub, text):
        # Simulate logging by appending text to logs
        self.logs += f"{text}\n"
        return "Log Entry Successful"

    def get_logs(self):
        return self.logs

    def force_summarize_all(self):
        return "Summary generated"

    def rebuild_tracker(self):
        return True

    def get_coverage_data(self):
        # Return a list of dictionaries for coverage data
        return [{"Category": "IntegrationTest", "Coverage": 90}]


class TestMainTabIntegration(unittest.TestCase):
    def setUp(self):
        # Create a hidden Tkinter root window for testing
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = DummyIntegrationController()
        # Instantiate MainTab with the dummy controller
        self.main_tab = MainTab(self.root, controller=self.controller)
        self.main_tab.pack(fill=tk.BOTH, expand=True)

    def tearDown(self):
        self.main_tab.destroy()
        self.root.destroy()

    def test_integration_log_update(self):
        # Simulate a user entering a log entry
        entry_panel = self.main_tab.entry_panel
        entry_panel.entry_text.insert("1.0", "Integration Test Entry")
        entry_panel.on_submit()

        # Refresh the LogPanel to fetch updated logs
        log_panel = self.main_tab.log_panel
        log_panel.refresh()
        content = log_panel.log_display.get("1.0", tk.END)
        self.assertIn("Integration Test Entry", content)

    def test_integration_coverage_data(self):
        # Refresh the CoveragePanel and check that it gets populated correctly
        coverage_panel = self.main_tab.coverage_panel
        coverage_panel.refresh()
        items = coverage_panel.tree.get_children()
        self.assertGreater(len(items), 0)
        first_item = coverage_panel.tree.item(items[0])["values"]
        self.assertEqual(first_item[0], "IntegrationTest")
        self.assertEqual(first_item[1], "90%")

    def test_integration_action_buttons(self):
        # Ensure that the action buttons in the ActionPanel execute without error
        action_panel = self.main_tab.action_panel
        try:
            action_panel.on_summarize()
            action_panel.on_rebuild()
        except Exception as e:
            self.fail(f"ActionPanel integration raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()
