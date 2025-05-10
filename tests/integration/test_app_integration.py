import unittest
import tkinter as tk
import os
import pytest
from scripts.gui.tabs.main_tab import MainTab


# Dummy integration controller that simulates backend behavior
class DummyIntegrationController:
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
        return [{"Category": "IntegrationTest", "Coverage": 90}]


# Define a condition to check if GUI testing is possible
GUI_AVAILABLE = os.environ.get("DISPLAY") is not None or os.name == "nt"


@pytest.mark.skipif(not GUI_AVAILABLE, reason="🛑 Skipping GUI integration tests — no display available")
class TestMainTabIntegration(unittest.TestCase):
    def setUp(self):
        if not GUI_AVAILABLE:
            self.skipTest("No display available for GUI tests")

        self.root = tk.Tk()
        self.root.withdraw()
        self.controller = DummyIntegrationController()
        self.main_tab = MainTab(self.root, controller=self.controller)
        self.main_tab.pack(fill=tk.BOTH, expand=True)

        # Process events to ensure the UI has time to initialize properly
        self.root.update_idletasks()
        self.root.update()

    def tearDown(self):
        if hasattr(self, 'main_tab'):
            self.main_tab.destroy()
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_integration_log_update(self):
        entry_panel = self.main_tab.entry_panel
        entry_panel.entry_text.insert("1.0", "Integration Test Entry")
        entry_panel.on_submit()
        self.root.update()

        log_panel = self.main_tab.log_panel
        log_panel.refresh()
        self.root.update()

        content = log_panel.log_display.get("1.0", tk.END)
        self.assertIn("Integration Test Entry", content)

    @pytest.mark.skipif(not GUI_AVAILABLE, reason=" Skipping GUI tests — Tkinter not available")
    def test_integration_coverage_data(self):
        coverage_panel = self.main_tab.coverage_panel
        coverage_panel.refresh()

        # Process events to ensure the tree gets populated
        self.root.update_idletasks()
        self.root.update()

        items = coverage_panel.tree.get_children()
        # If no items, print debug info to help diagnose
        if not items:
            print("DEBUG: Coverage data returned:", self.controller.get_coverage_data())
            print("DEBUG: Tree children:", coverage_panel.tree.get_children())

        self.assertGreater(len(items), 0, "Coverage tree should contain at least one item")

        # Make sure we have items before trying to access them
        if items:
            first_item = coverage_panel.tree.item(items[0])["values"]
            self.assertEqual(first_item[0], "IntegrationTest")
            self.assertEqual(first_item[1], "90%")

    @pytest.mark.skipif(not GUI_AVAILABLE, reason=" Skipping GUI tests — Tkinter not available")
    def test_integration_action_buttons(self):
        action_panel = self.main_tab.action_panel
        try:
            action_panel.on_summarize()
            action_panel.on_rebuild()
            self.root.update()
        except Exception as e:
            self.fail(f"ActionPanel integration raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()