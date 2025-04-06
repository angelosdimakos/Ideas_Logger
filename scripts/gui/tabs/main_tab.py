import tkinter as tk
from tkinter import ttk

from scripts.gui.base.base_tab import BaseTab
from scripts.gui.panels.log_panel import LogPanel
from scripts.gui.panels.coverage_panel import CoveragePanel
from scripts.gui.panels.entry_panel import EntryPanel
from scripts.gui.panels.action_panel import ActionPanel

class MainTab(BaseTab):
    """
    MainTab is the primary tab for logging functionality.
    It organizes child panels: LogPanel, CoveragePanel, EntryPanel, and ActionPanel.
    """
    def setup_tab(self):
        # Create a container frame to hold the child panels
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create and pack the LogPanel
        self.log_panel = LogPanel(container, controller=self.controller)
        self.log_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 2))

        # Create and pack the CoveragePanel
        self.coverage_panel = CoveragePanel(container, controller=self.controller)
        self.coverage_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # Create and pack the EntryPanel
        self.entry_panel = EntryPanel(container, controller=self.controller)
        self.entry_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # Create and pack the ActionPanel (for action buttons)
        self.action_panel = ActionPanel(container, controller=self.controller)
        self.action_panel.pack(fill=tk.X, padx=5, pady=(2, 5))

    def on_show(self):
        """
        Called when the MainTab becomes active. This refreshes all child panels.
        """
        if hasattr(self, 'log_panel'):
            self.log_panel.refresh()
        if hasattr(self, 'coverage_panel'):
            self.coverage_panel.refresh()
        if hasattr(self, 'entry_panel'):
            self.entry_panel.refresh()
        if hasattr(self, 'action_panel'):
            self.action_panel.refresh()
