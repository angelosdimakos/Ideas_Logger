import tkinter as tk
from tkinter import ttk
from typing import Optional

from scripts.gui.base.base_panel import BasePanel
from scripts.gui.widget_factory import WidgetFactory


class EntryPanel(BasePanel):
    """
    EntryPanel provides the interface for creating new log entries.
    """

    def __init__(self, parent, controller=None, **kwargs):
        # Declare instance attributes for type checkers
        self.frame: Optional[ttk.LabelFrame] = None
        self.entry_text: Optional[tk.Text] = None
        self.submit_button: Optional[ttk.Button] = None
        super().__init__(parent, controller, **kwargs)

    def initialize_ui(self):
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

    def on_submit(self):
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

    def refresh(self):
        # Clear the text area when refreshing, if needed
        self.entry_text.delete("1.0", tk.END)
