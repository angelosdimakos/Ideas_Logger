import unittest
import tkinter as tk
from unittest.mock import MagicMock

from scripts.gui.tabs.main_tab import MainTab


# Dummy controller that simulates errors in some methods
class DummyErrorController:
    def __init__(self):
        self.logs = "Initial logs\n"

    def log_entry(self, main, sub, text):
        self.logs += f"{text}\n"
        return "Log Entry Successful"

    def get_logs(self):
        # Simulate an error condition in log retrieval
        raise Exception("Failed to retrieve logs")

    def force_summarize_all(self):
        raise Exception("Summarization failed")

    def rebuild_tracker(self):
        raise Exception("Tracker rebuild error")

    def get_coverage_data(self):
        # Simulate an error condition in coverage data retrieval
        raise Exception("Coverage data error")


class TestMainTabCascade(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

        # Create a dummy controller that works normally
        class DummyController:
            def __init__(self):
                self.logs = "Initial logs\n"

            def log_entry(self, main, sub, text):
                self.logs += f"{text}\n"
                return "Log Entry Successful"

            def get_logs(self):
                return self.logs

            def force_summarize_all(self):
                return "Summary generated"

            def rebuild_tracker(self):
                return True

            def get_coverage_data(self):
                return [{"Category": "CascadeTest", "Coverage": 85}]

        self.controller = DummyController()
        self.main_tab = MainTab(self.root, controller=self.controller)
        self.main_tab.pack(fill=tk.BOTH, expand=True)

        # Instrument refresh methods with MagicMock to track calls
        self.main_tab.log_panel.refresh = MagicMock(name="log_refresh")
        self.main_tab.coverage_panel.refresh = MagicMock(name="coverage_refresh")
        self.main_tab.entry_panel.refresh = MagicMock(name="entry_refresh")
        self.main_tab.action_panel.refresh = MagicMock(name="action_refresh")

    def tearDown(self):
        self.main_tab.destroy()
        self.root.destroy()

    def test_main_tab_on_show_calls_child_refresh(self):
        # Call the on_show method of MainTab
        self.main_tab.on_show()
        # Check that each child panel's refresh was called
        self.main_tab.log_panel.refresh.assert_called_once()
        self.main_tab.coverage_panel.refresh.assert_called_once()
        self.main_tab.entry_panel.refresh.assert_called_once()
        self.main_tab.action_panel.refresh.assert_called_once()


class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = DummyErrorController()
        self.main_tab = MainTab(self.root, controller=self.controller)
        self.main_tab.pack(fill=tk.BOTH, expand=True)

    def tearDown(self):
        self.main_tab.destroy()
        self.root.destroy()

    def test_log_panel_error_handling(self):
        # Test that LogPanel handles error from get_logs()
        log_panel = self.main_tab.log_panel
        log_panel.refresh()
        content = log_panel.log_display.get("1.0", tk.END)
        self.assertIn("Error retrieving logs", content)

    def test_coverage_panel_error_handling(self):
        # Test that CoveragePanel prints an error message when get_coverage_data() fails
        coverage_panel = self.main_tab.coverage_panel
        # Capture printed output (if needed) or simply verify that no items are added
        coverage_panel.refresh()
        items = coverage_panel.tree.get_children()
        self.assertEqual(len(items), 0)

    def test_action_panel_error_handling(self):
        # For ActionPanel, simply call the methods and check that they handle errors without crashing
        action_panel = self.main_tab.action_panel
        try:
            action_panel.on_summarize()
            action_panel.on_rebuild()
        except Exception as e:
            self.fail(f"ActionPanel did not handle errors gracefully: {e}")


if __name__ == '__main__':
    unittest.main()
