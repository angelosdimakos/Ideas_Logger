"""
style_manager.py

This module defines the StyleManager class for managing application-wide styles for tkinter and ttk.

Core features include:
- Managing application-wide styles for tkinter and ttk.
- Defining default colors and fonts.
- Configuring ttk styles.
- Updating specific styles with new options.
"""

from tkinter import ttk
from typing import Dict, Any


class StyleManager:
    """
    Manages application-wide styles for tkinter and ttk.

    This class can be extended to handle dynamic theme changes.

    Attributes:
        root (Tk): The root Tkinter window.
        style (ttk.Style): The ttk style manager instance.
    """

    def __init__(self, root: ttk.Tk) -> None:
        """
        Initializes the StyleManager with the specified root window.

        Args:
            root (Tk): The root Tkinter window.
        """
        self.root = root
        self.style = ttk.Style(root)
        self.initialize_styles()

    def initialize_styles(self) -> None:
        """
        Defines default colors and fonts and configures ttk styles.

        Returns:
            None
        """
        # Define default colors and fonts
        self.primary_color = "#3f51b5"  # Deep blue
        self.secondary_color = "#f5f5f5"  # Light gray
        self.accent_color = "#4caf50"  # Green for success
        self.text_color = "#212121"  # Dark text

        # Configure ttk styles
        self.style.configure("TFrame", background=self.secondary_color)
        self.style.configure("TLabel", background=self.secondary_color, foreground=self.text_color)
        self.style.configure(
            "TButton", background=self.primary_color, foreground="white", padding=6, relief="flat"
        )
        self.style.map("TButton", background=[("active", "#303f9f"), ("disabled", "#bdbdbd")])

    def update_style(self, style_name: str, options: Dict[str, Any]) -> None:
        """
        Update a specific style with new options.

        Args:
            style_name (str): The name of the style to update (e.g., 'TButton').
            options (Dict[str, Any]): A dictionary of style options (e.g., {'background': 'red'}).

        Returns:
            None
        """
        self.style.configure(style_name, **options)
