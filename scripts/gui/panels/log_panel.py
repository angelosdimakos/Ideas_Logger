"""
log_panel.py

This module defines the LogPanel class, which manages the display area for logs.

Core features include:
- Displaying log entries in a scrollable text area.
- Integrating with the application controller to fetch log data.
"""

import tkinter as tk
from tkinter import scrolledtext, ttk
from scripts.gui.base.base_panel import BasePanel
from typing import Optional


class LogPanel(BasePanel):
    """
    LogPanel manages the display area for logs.

    Attributes:
        frame (ttk.LabelFrame): The frame containing the log display.
        log_display (scrolledtext.ScrolledText): The text area for displaying log entries.
    """

    def __init__(self, parent: tk.Widget, controller: Optional[object] = None, **kwargs) -> None:
        """
        Initializes the LogPanel with the specified parent and controller.

        Args:
            parent (tk.Widget): The parent widget for this panel.
            controller (Optional[object]): The controller for handling log data. Defaults to None.
        """
        # Optional: Initialize instance variables for type checkers
        self.frame: ttk.LabelFrame = None
        self.log_display: scrolledtext.ScrolledText = None
        super().__init__(parent, controller, **kwargs)

    def initialize_ui(self) -> None:
        """
        Creates and packs the user interface components for the log panel.

        Returns:
            None
        """
        # Create a labeled frame for logs
        self.frame = ttk.LabelFrame(self, text="Logs")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a scrolled text widget to display log entries
        self.log_display = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, height=8)
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def refresh(self) -> None:
        """
        Refreshes the log display area by fetching logs from the controller.

        Returns:
            None
        """
        # Clear the log display
        self.log_display.delete("1.0", tk.END)
        # Use the controller's get_logs method to retrieve and display logs.
        if self.controller and hasattr(self.controller, "get_logs"):
            try:
                logs = self.controller.get_logs()
                self.log_display.insert(tk.END, logs)
            except Exception as e:
                self.log_display.insert(tk.END, f"Error retrieving logs: {e}")
        else:
            print("Controller does not provide a get_logs method.")
