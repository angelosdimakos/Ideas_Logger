"""
gui_logging.py

This module provides a logging handler that appends log messages to a Tkinter Text widget.
"""

import logging
import tkinter as tk


class GUILogHandler(logging.Handler):
    """
    A logging handler that appends log messages to a Tkinter Text widget.
    """

    def __init__(self, text_widget: tk.Text) -> None:
        """
        :param text_widget: The Text widget where log messages should be appended.
        """
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emits a log message to the associated Text widget.

        :param record: logging.LogRecord
        """
        try:
            msg = self.format(record)
            # Schedule GUI update in the main thread
            self.text_widget.after(0, self.append_message, msg)
        except (AttributeError, RuntimeError):
            self.handleError(record)

    def append_message(self, msg: str) -> None:
        """
        Appends a log message to the associated Text widget.

        This method is designed to be called from the main thread,
        and will block until the message is appended.
        """
        if not self.text_widget.winfo_exists():
            return  # Avoid writing to a destroyed widget

        try:
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", msg + "\n")
            self.text_widget.configure(state="disabled")
            self.text_widget.see("end")
        except (tk.TclError, RuntimeError) as e:
            logging.getLogger(__name__).debug(f"GUI append failed: {e}")
