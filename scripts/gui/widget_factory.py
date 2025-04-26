"""
widget_factory.py

This module defines the WidgetFactory class for creating common widgets with standardized styling.

Core features include:
- Creating styled buttons, labels, entries, frames, and notebooks for Tkinter applications.
- Providing a consistent look and feel across the application.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any


class WidgetFactory:
    """
    Factory for creating common widgets with standardized styling.

    This class provides static methods to create buttons, labels, entries, frames, and notebooks with consistent styles.
    """

    @staticmethod
    def create_button(
        parent: tk.Widget, text: str, command: callable, style: str = "TButton", **options: Any
    ) -> ttk.Button:
        """
        Create and return a styled ttk Button.

        Args:
            parent (tk.Widget): The parent widget.
            text (str): The text to display on the button.
            command (callable): The function to call when the button is clicked.
            style (str): The style to apply to the button. Defaults to 'TButton'.
            **options: Additional options to configure the button.

        Returns:
            ttk.Button: The created button widget.
        """
        return ttk.Button(parent, text=text, command=command, style=style, **options)

    @staticmethod
    def create_label(
        parent: tk.Widget, text: str, style: str = "TLabel", **options: Any
    ) -> ttk.Label:
        """
        Create and return a styled ttk Label.

        Args:
            parent (tk.Widget): The parent widget.
            text (str): The text to display on the label.
            style (str): The style to apply to the label. Defaults to 'TLabel'.
            **options: Additional options to configure the label.

        Returns:
            ttk.Label: The created label widget.
        """
        return ttk.Label(parent, text=text, style=style, **options)

    @staticmethod
    def create_entry(parent: tk.Widget, textvariable: Any = None, **options: Any) -> ttk.Entry:
        """
        Create and return a ttk Entry widget.

        Args:
            parent (tk.Widget): The parent widget.
            textvariable (Any): The variable to associate with the entry. Defaults to None.
            **options: Additional options to configure the entry.

        Returns:
            ttk.Entry: The created entry widget.
        """
        return ttk.Entry(parent, textvariable=textvariable, **options)

    @staticmethod
    def create_frame(parent: tk.Widget, style: str = "TFrame", **options: Any) -> ttk.Frame:
        """
        Create and return a ttk Frame widget.

        Args:
            parent (tk.Widget): The parent widget.
            style (str): The style to apply to the frame. Defaults to 'TFrame'.
            **options: Additional options to configure the frame.

        Returns:
            ttk.Frame: The created frame widget.
        """
        return ttk.Frame(parent, style=style, **options)

    @staticmethod
    def create_notebook(parent: tk.Widget, **options: Any) -> ttk.Notebook:
        """
        Create and return a ttk Notebook widget.

        Args:
            parent (tk.Widget): The parent widget.
            **options: Additional options to configure the notebook.

        Returns:
            ttk.Notebook: The created notebook widget.
        """
        return ttk.Notebook(parent, **options)
