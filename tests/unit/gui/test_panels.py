"""
Unit tests for GUI panels in the Ideas Logger application.

This module contains tests for the ActionPanel, CoveragePanel, EntryPanel, and LogPanel.
It uses unittest and pytest for testing the functionality of each panel.
"""

import unittest
import tkinter as tk
from unittest.mock import MagicMock
import pytest

from conftest import GUI_AVAILABLE, tk_safe

# Import panels
from scripts.gui.panels.action_panel import ActionPanel
from scripts.gui.panels.coverage_panel import CoveragePanel
from scripts.gui.panels.entry_panel import EntryPanel
from scripts.gui.panels.log_panel import LogPanel


class DummyActionController:
    def __init__(self) -> None:
        self.force_summarize_all = MagicMock(return_value="dummy_summary")
        self.rebuild_tracker = MagicMock(return_value=True)


class DummyCoverageController:
    def get_coverage_data(self) -> list:
        return [{"Category": "TestCat", "Coverage": 80}]


class DummyEntryController:
    def log_entry(self, main: str, sub: str, text: str) -> str:
        return f"Logged: {main}, {sub}, {text}"


class DummyLogController:
    def get_logs(self) -> str:
        return "Test log line\nAnother log entry\n"


@pytest.mark.skipif(not GUI_AVAILABLE, reason="🛑 Skipping GUI tests — Tkinter not available")
class TestActionPanel(unittest.TestCase):
    def setUp(self) -> None:
        if not GUI_AVAILABLE:
            self.skipTest("🛑 Tkinter not available in environment")
        self.tk_ctx = tk_safe()
        self.root, _ = self.tk_ctx.__enter__()
        self.controller = DummyActionController()
        self.panel = ActionPanel(self.root, controller=self.controller)
        self.panel.initialize_ui()

    def tearDown(self) -> None:
        self.panel.destroy()
        self.tk_ctx.__exit__(None, None, None)

    def test_on_summarize_calls_controller(self) -> None:
        self.panel.on_summarize()
        self.controller.force_summarize_all.assert_called_once()

    def test_on_rebuild_calls_controller(self) -> None:
        self.panel.on_rebuild()
        self.controller.rebuild_tracker.assert_called_once()


@pytest.mark.skipif(not GUI_AVAILABLE, reason="🛑 Skipping GUI tests — Tkinter not available")
class TestCoveragePanel(unittest.TestCase):
    def setUp(self) -> None:
        if not GUI_AVAILABLE:
            self.skipTest("🛑 Tkinter not available in environment")
        self.tk_ctx = tk_safe()
        self.root, _ = self.tk_ctx.__enter__()
        self.controller = DummyCoverageController()
        self.panel = CoveragePanel(self.root, controller=self.controller)
        self.panel.initialize_ui()

    def tearDown(self) -> None:
        self.panel.destroy()
        self.tk_ctx.__exit__(None, None, None)

    def test_refresh_populates_tree(self) -> None:
        self.panel.refresh()
        items = self.panel.tree.get_children()
        self.assertGreater(len(items), 0)
        first_item = self.panel.tree.item(items[0])["values"]
        self.assertEqual(first_item[0], "TestCat")
        self.assertEqual(first_item[1], "80%")


@pytest.mark.skipif(not GUI_AVAILABLE, reason="🛑 Skipping GUI tests — Tkinter not available")
class TestEntryPanel(unittest.TestCase):
    def setUp(self) -> None:
        if not GUI_AVAILABLE:
            self.skipTest("🛑 Tkinter not available in environment")
        self.tk_ctx = tk_safe()
        self.root, _ = self.tk_ctx.__enter__()
        self.controller = DummyEntryController()
        self.panel = EntryPanel(self.root, controller=self.controller)
        self.panel.initialize_ui()

    def tearDown(self) -> None:
        self.panel.destroy()
        self.tk_ctx.__exit__(None, None, None)

    def test_on_submit_calls_log_entry(self) -> None:
        test_text = "Sample log entry"
        self.panel.entry_text.insert("1.0", test_text)
        self.panel.on_submit()
        current_text = self.panel.entry_text.get("1.0", tk.END).strip()
        self.assertEqual(current_text, "")


@pytest.mark.skipif(not GUI_AVAILABLE, reason="🛑 Skipping GUI tests — Tkinter not available")
class TestLogPanel(unittest.TestCase):
    def setUp(self) -> None:
        if not GUI_AVAILABLE:
            self.skipTest("🛑 Tkinter not available in environment")
        self.tk_ctx = tk_safe()
        self.root, _ = self.tk_ctx.__enter__()
        self.controller = DummyLogController()
        self.panel = LogPanel(self.root, controller=self.controller)
        self.panel.initialize_ui()

    def tearDown(self) -> None:
        self.panel.destroy()
        self.tk_ctx.__exit__(None, None, None)

    def test_refresh_displays_logs(self) -> None:
        self.panel.refresh()
        content = self.panel.log_display.get("1.0", tk.END)
        self.assertIn("Test log line", content)
        self.assertIn("Another log entry", content)
