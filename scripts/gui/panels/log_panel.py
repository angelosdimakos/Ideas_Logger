import tkinter as tk
from tkinter import scrolledtext, ttk
from scripts.gui.base.base_panel import BasePanel

class LogPanel(BasePanel):
    """
    LogPanel manages the display area for logs.
    """

    def __init__(self, parent, controller=None, **kwargs):
        # Optional: Initialize instance variables for type checkers
        self.frame: ttk.LabelFrame = None
        self.log_display: scrolledtext.ScrolledText = None
        super().__init__(parent, controller, **kwargs)

    def initialize_ui(self):
        # Create a labeled frame for logs
        self.frame = ttk.LabelFrame(self, text="Logs")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a scrolled text widget to display log entries
        self.log_display = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, height=8)
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def refresh(self):
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
