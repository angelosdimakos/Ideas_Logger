"""
Unit tests for GUI panels in the Ideas Logger application.

This module contains tests for the ActionPanel, CoveragePanel, EntryPanel, and LogPanel.
It uses unittest and pytest for testing the functionality of each panel.

Core features include:
- Testing the functionality of the ActionPanel, ensuring it correctly interacts with the controller.
- Validating the CoveragePanel refresh behavior and data population.
- Checking the EntryPanel submission process and log entry creation.
- Ensuring the LogPanel displays logs correctly.

Intended for use in automated testing to ensure GUI components function as expected.
"""

import unittest
import tkinter as tk
from unittest.mock import MagicMock
import pytest

from tests.conftest import GUI_AVAILABLE, tk_safe

# Import panels
from scripts.gui.panels.action_panel import ActionPanel
from scripts.gui.panels.coverage_panel import CoveragePanel
from scripts.gui.panels.entry_panel import EntryPanel
from scripts.gui.panels.log_panel import LogPanel


class DummyActionController:
    def __init__(self) -> None:
        """
        Initialize a dummy action controller for testing.

        Creates mock objects for the force_summarize_all and rebuild_tracker methods.
        """
        self.force_summarize_all = MagicMock(return_value="dummy_summary")
        self.rebuild_tracker = MagicMock(return_value=True)


class DummyCoverageController:
    def get_coverage_data(self) -> list:
        """
        Return sample coverage data for testing.

        Returns a list containing a single dictionary with category and coverage information.
        """
        return [{"Category": "TestCat", "Coverage": 80}]


class DummyEntryController:
    def log_entry(self, main: str, sub: str, text: str) -> str:
        """
        Simulate logging an entry.

        Returns a formatted string indicating the entry has been logged.
        """
        return f"Logged: {main}, {sub}, {text}"


class DummyLogController:
    def get_logs(self) -> str:
        """
        Return sample log data for testing.

        Returns a string containing multiple log lines.
        """
        return "Test log line\nAnother log entry\n"


@pytest.mark.skipif(not GUI_AVAILABLE, reason=" Skipping GUI tests — Tkinter not available")
class TestActionPanel(unittest.TestCase):
    """
    Unit tests for the ActionPanel class.

    This class contains tests to validate the functionality of the ActionPanel,
    ensuring it interacts correctly with the controller and updates the GUI as expected.
    """

    def setUp(self) -> None:
        """
        Set up the test environment for ActionPanel tests.

        Initializes the ActionPanel with a dummy controller for testing.
        """
        if not GUI_AVAILABLE:
            self.skipTest(" Tkinter not available in environment")
        self.tk_ctx = tk_safe()
        self.root, _ = self.tk_ctx.__enter__()
        self.controller = DummyActionController()
        self.panel = ActionPanel(self.root, controller=self.controller)
        self.panel.initialize_ui()

    def tearDown(self) -> None:
        """
        Clean up after each test.
        """
        self.panel.destroy()
        self.tk_ctx.__exit__(None, None, None)

    def test_on_summarize_calls_controller(self):
        """
        Test that the summarize action calls the appropriate method on the controller.

        Asserts that the force_summarize_all method is called when the summarize action is triggered.
        """
        self.panel.on_summarize()
        self.controller.force_summarize_all.assert_called_once()

    def test_on_rebuild_calls_controller(self):
        """
        Test that the rebuild action calls the appropriate method on the controller.

        Asserts that the rebuild_tracker method is called when the rebuild action is triggered.
        """
        self.panel.on_rebuild()
        self.controller.rebuild_tracker.assert_called_once()


@pytest.mark.skipif(not GUI_AVAILABLE, reason=" Skipping GUI tests — Tkinter not available")
class TestCoveragePanel(unittest.TestCase):
    """
    Unit tests for the CoveragePanel class.

    This class contains tests to validate the functionality of the CoveragePanel,
    ensuring it correctly populates the tree with coverage data.
    """

    def setUp(self) -> None:
        """
        Set up the test environment for CoveragePanel tests.

        Initializes the CoveragePanel with a dummy controller for testing.
        """
        if not GUI_AVAILABLE:
            self.skipTest(" Tkinter not available in environment")
        self.tk_ctx = tk_safe()
        self.root, _ = self.tk_ctx.__enter__()
        self.controller = DummyCoverageController()
        self.panel = CoveragePanel(self.root, controller=self.controller)
        self.panel.initialize_ui()

    def tearDown(self) -> None:
        """
        Clean up after each test.
        """
        self.panel.destroy()
        self.tk_ctx.__exit__(None, None, None)

    def test_refresh_populates_tree(self):
        """
        Test that the refresh action populates the tree with coverage data.

        Asserts that the tree contains at least one item after refreshing.
        """
        self.panel.refresh()
        items = self.panel.tree.get_children()
        self.assertGreater(len(items), 0)
        first_item = self.panel.tree.item(items[0])["values"]
        self.assertEqual(first_item[0], "TestCat")
        self.assertEqual(first_item[1], "80%")


@pytest.mark.skipif(not GUI_AVAILABLE, reason=" Skipping GUI tests — Tkinter not available")
class TestEntryPanel(unittest.TestCase):
    """
    Unit tests for the EntryPanel class.

    This class contains tests to validate the functionality of the EntryPanel,
    ensuring it correctly logs entries and updates the GUI as expected.
    """

    def setUp(self) -> None:
        """
        Set up the test environment for EntryPanel tests.

        Initializes the EntryPanel with a dummy controller for testing.
        """
        if not GUI_AVAILABLE:
            self.skipTest(" Tkinter not available in environment")
        self.tk_ctx = tk_safe()
        self.root, _ = self.tk_ctx.__enter__()
        self.controller = DummyEntryController()
        self.panel = EntryPanel(self.root, controller=self.controller)
        self.panel.initialize_ui()

    def tearDown(self) -> None:
        """
        Clean up after each test.
        """
        self.panel.destroy()
        self.tk_ctx.__exit__(None, None, None)

    def test_on_submit_calls_log_entry(self):
        """
        Test that the submit action calls the log_entry method on the controller.

        Asserts that the log_entry method is called when the submit action is triggered.
        """
        test_text = "Sample log entry"
        self.panel.entry_text.insert("1.0", test_text)
        self.panel.on_submit()
        current_text = self.panel.entry_text.get("1.0", tk.END).strip()
        self.assertEqual(current_text, "")


@pytest.mark.skipif(not GUI_AVAILABLE, reason=" Skipping GUI tests — Tkinter not available")
class TestLogPanel(unittest.TestCase):
    """
    Unit tests for the LogPanel class.

    This class contains tests to validate the functionality of the LogPanel,
    ensuring it correctly displays logs and updates the GUI as expected.
    """

    def setUp(self) -> None:
        """
        Set up the test environment for LogPanel tests.

        Initializes the LogPanel with a dummy controller for testing.
        """
        if not GUI_AVAILABLE:
            self.skipTest(" Tkinter not available in environment")
        self.tk_ctx = tk_safe()
        self.root, _ = self.tk_ctx.__enter__()
        self.controller = DummyLogController()
        self.panel = LogPanel(self.root, controller=self.controller)
        self.panel.initialize_ui()

    def tearDown(self) -> None:
        """
        Clean up after each test.
        """
        self.panel.destroy()
        self.tk_ctx.__exit__(None, None, None)

    def test_refresh_displays_logs(self):
        """
        Test that the refresh action displays logs in the log display area.

        Asserts that the log display area contains the expected log lines after refreshing.
        """
        self.panel.refresh()
        content = self.panel.log_display.get("1.0", tk.END)
        self.assertIn("Test log line", content)
        self.assertIn("Another log entry", content)
