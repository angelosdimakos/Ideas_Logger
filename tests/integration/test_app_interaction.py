"""
Unit tests for GUI application interaction in the Ideas Logger project.

This module contains integration tests for the MainTab and error handling scenarios.
It uses unittest for testing the functionality of the application.
"""

import unittest
import tkinter as tk
from unittest.mock import MagicMock
import os

from scripts.gui.tabs.main_tab import MainTab


class DummyErrorController:
    """
    Simulates a controller that raises errors for testing error handling.
    """

    def __init__(self) -> None:
        self.logs = "Initial logs\n"

    def log_entry(self, main: str, sub: str, text: str) -> str:
        """
        Logs an entry and returns a success message.
        """
        self.logs += f"{text}\n"
        return "Log Entry Successful"

    def get_logs(self) -> str:
        """
        Raises an exception to simulate log retrieval failure.
        """
        raise Exception("Failed to retrieve logs")

    def force_summarize_all(self) -> None:
        """
        Raises an exception to simulate summarization failure.
        """
        raise Exception("Summarization failed")

    def rebuild_tracker(self) -> None:
        """
        Raises an exception to simulate tracker rebuild error.
        """
        raise Exception("Tracker rebuild error")

    def get_coverage_data(self) -> None:
        """
        Raises an exception to simulate coverage data retrieval failure.
        """
        raise Exception("Coverage data error")


@unittest.skipIf(
    not os.environ.get("DISPLAY") and os.name != "nt",
    "🛑 Skipping GUI integration tests — no display available",
)
class TestMainTabCascade(unittest.TestCase):
    """
    Tests the MainTab functionality in the GUI application.
    """

    def setUp(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw()

        class DummyController:
            """
            Simulates a controller for the MainTab during testing.
            """

            def __init__(self) -> None:
                self.logs = "Initial logs\n"

            def log_entry(self, main: str, sub: str, text: str) -> str:
                """
                Logs an entry and returns a success message.
                """
                self.logs += f"{text}\n"
                return "Log Entry Successful"

            def get_logs(self) -> str:
                """
                Returns the logs.
                """
                return self.logs

            def force_summarize_all(self) -> str:
                """
                Returns a success message for summarization.
                """
                return "Summary generated"

            def rebuild_tracker(self) -> bool:
                """
                Returns True to simulate successful tracker rebuild.
                """
                return True

            def get_coverage_data(self) -> list:
                """
                Returns mock coverage data.
                """
                return [{"Category": "CascadeTest", "Coverage": 85}]

        self.controller = DummyController()
        self.main_tab = MainTab(self.root, controller=self.controller)
        self.main_tab.pack(fill=tk.BOTH, expand=True)

        self.main_tab.log_panel.refresh = MagicMock(name="log_refresh")
        self.main_tab.coverage_panel.refresh = MagicMock(name="coverage_refresh")
        self.main_tab.entry_panel.refresh = MagicMock(name="entry_refresh")
        self.main_tab.action_panel.refresh = MagicMock(name="action_refresh")

    def tearDown(self) -> None:
        self.main_tab.destroy()
        self.root.destroy()

    def test_main_tab_on_show_calls_child_refresh(self) -> None:
        """
        Tests that showing the main tab calls refresh on child panels.
        """
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
    """
    Tests error handling in the MainTab functionality.
    """

    def setUp(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = DummyErrorController()
        self.main_tab = MainTab(self.root, controller=self.controller)
        self.main_tab.pack(fill=tk.BOTH, expand=True)

    def tearDown(self) -> None:
        self.main_tab.destroy()
        self.root.destroy()

    def test_log_panel_error_handling(self) -> None:
        """
        Tests that the log panel handles errors gracefully.
        """
        log_panel = self.main_tab.log_panel
        log_panel.refresh()
        content = log_panel.log_display.get("1.0", tk.END)
        self.assertIn("Error retrieving logs", content)

    def test_coverage_panel_error_handling(self) -> None:
        """
        Tests that the coverage panel handles errors gracefully.
        """
        coverage_panel = self.main_tab.coverage_panel
        coverage_panel.refresh()
        items = coverage_panel.tree.get_children()
        self.assertEqual(len(items), 0)

    def test_action_panel_error_handling(self) -> None:
        """
        Tests that the action panel handles errors gracefully.
        """
        action_panel = self.main_tab.action_panel
        try:
            action_panel.on_summarize()
            action_panel.on_rebuild()
        except Exception as e:
            self.fail(f"ActionPanel did not handle errors gracefully: {e}")


if __name__ == "__main__":
    unittest.main()
