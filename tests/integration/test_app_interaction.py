import unittest
import tkinter as tk
from unittest.mock import MagicMock
import os

from scripts.gui.tabs.main_tab import MainTab


# Dummy controller that simulates errors in some methods
class DummyErrorController:
    def __init__(self):
        self.logs = "Initial logs\n"

    def log_entry(self, main, sub, text):
        self.logs += f"{text}\n"
        return "Log Entry Successful"

    def get_logs(self):
        raise Exception("Failed to retrieve logs")

    def force_summarize_all(self):
        raise Exception("Summarization failed")

    def rebuild_tracker(self):
        raise Exception("Tracker rebuild error")

    def get_coverage_data(self):
        raise Exception("Coverage data error")


@unittest.skipIf(
    not os.environ.get("DISPLAY") and os.name != "nt",
    "🛑 Skipping GUI integration tests — no display available",
)
class TestMainTabCascade(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

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

        self.main_tab.log_panel.refresh = MagicMock(name="log_refresh")
        self.main_tab.coverage_panel.refresh = MagicMock(name="coverage_refresh")
        self.main_tab.entry_panel.refresh = MagicMock(name="entry_refresh")
        self.main_tab.action_panel.refresh = MagicMock(name="action_refresh")

    def tearDown(self):
        self.main_tab.destroy()
        self.root.destroy()

    def test_main_tab_on_show_calls_child_refresh(self):
        self.main_tab.on_show()
        self.main_tab.log_panel.refresh.assert_called_once()
        self.main_tab.coverage_panel.refresh.assert_called_once()
        self.main_tab.entry_panel.refresh.assert_called_once()
        self.main_tab.action_panel.refresh.assert_called_once()


@unittest.skipIf(
    not os.environ.get("DISPLAY") and os.name != "nt",
    "🛑 Skipping GUI integration tests — no display available",
)
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
        log_panel = self.main_tab.log_panel
        log_panel.refresh()
        content = log_panel.log_display.get("1.0", tk.END)
        self.assertIn("Error retrieving logs", content)

    def test_coverage_panel_error_handling(self):
        coverage_panel = self.main_tab.coverage_panel
        coverage_panel.refresh()
        items = coverage_panel.tree.get_children()
        self.assertEqual(len(items), 0)

    def test_action_panel_error_handling(self):
        action_panel = self.main_tab.action_panel
        try:
            action_panel.on_summarize()
            action_panel.on_rebuild()
        except Exception as e:
            self.fail(f"ActionPanel did not handle errors gracefully: {e}")


if __name__ == "__main__":
    unittest.main()
