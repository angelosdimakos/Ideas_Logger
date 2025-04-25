"""
entry_panel.py

This module defines the EntryPanel class, which provides the interface for creating new log entries.

Core features include:
- Allowing users to enter and submit new log entries.
- Integrating with the application controller to handle log submission.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from scripts.gui.base.base_panel import BasePanel
from scripts.gui.widget_factory import WidgetFactory


class EntryPanel(BasePanel):
    """
    EntryPanel provides the interface for creating new log entries.

    Attributes:
        frame (Optional[ttk.LabelFrame]): The frame containing the entry interface.
        entry_text (Optional[tk.Text]): The text widget for entering log content.
        submit_button (Optional[ttk.Button]): The button for submitting the log entry.
    """

    def __init__(self, parent: tk.Widget, controller: Optional[object] = None, **kwargs) -> None:
        """
        Initializes the EntryPanel with the specified parent and controller.

        Args:
            parent (tk.Widget): The parent widget for this panel.
            controller (Optional[object]): The controller for handling log submissions. Defaults to None.
        """
        # Declare instance attributes for type checkers
        self.frame: Optional[ttk.LabelFrame] = None
        self.entry_text: Optional[tk.Text] = None
        self.submit_button: Optional[ttk.Button] = None
        super().__init__(parent, controller, **kwargs)

    def initialize_ui(self) -> None:
        """
        Creates and packs the user interface components for the entry panel.

        Returns:
            None
        """
        # Create a labeled frame for the entry area
        self.frame = ttk.LabelFrame(self, text="New Log Entry")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a text widget for entering new log content
        self.entry_text = tk.Text(self.frame, height=5)
        self.entry_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a submit button using WidgetFactory
        self.submit_button = WidgetFactory.create_button(
            self.frame, text="Submit Log", command=self.on_submit
        )
        self.submit_button.pack(pady=5)

    def on_submit(self) -> None:
        """
        Handles the submission of a new log entry.

        Retrieves text from the text widget and submits it to the controller if available.

        Returns:
            None
        """
        # Retrieve text from the text widget and strip extra whitespace
        text = self.entry_text.get("1.0", tk.END).strip()
        if text:
            if self.controller and hasattr(self.controller, "log_entry"):
                try:
                    # For this example, we're using placeholder values for main and sub categories.
                    # Replace "default_main" and "default_sub" with the appropriate values if needed.
                    result = self.controller.log_entry("default_main", "default_sub", text)
                    print("Log entry submitted:", result)
                    # Clear the text area after submission
                    self.entry_text.delete("1.0", tk.END)
                except Exception as e:
                    print("Error submitting log entry:", e)
            else:
                print("Controller or log_entry method not available.")
        else:
            print("No log entry text provided.")

    def refresh(self) -> None:
        """
        Clears the text area when refreshing, if needed.

        Returns:
            None
        """
        # Clear the text area when refreshing, if needed
        self.entry_text.delete("1.0", tk.END)
