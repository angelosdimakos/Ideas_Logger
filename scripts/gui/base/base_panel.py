"""
base_panel.py

This module defines the BasePanel class, which provides common functionality for all UI panels.

Core features include:
- Providing a base class for panels with consistent styling.
- Allowing subclasses to implement specific UI components and refresh logic.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class BasePanel(ttk.Frame):
    """
    BasePanel provides common functionality for all UI panels.
    Inherits from ttk.Frame to leverage consistent styling.

    Attributes:
        controller (Optional[object]): The controller for handling panel actions.
    """

    def __init__(self, parent: tk.Widget, controller: Optional[object] = None, **kwargs) -> None:
        """
        Initializes the BasePanel with the specified parent and controller.

        Args:
            parent (tk.Widget): The parent widget for this panel.
            controller (Optional[object]): The controller for handling panel actions. Defaults to None.
        """
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.initialize_ui()

    def initialize_ui(self) -> None:
        """
        Set up UI components for the panel.
        Override this method in subclasses to build specific panel content.

        Returns:
            None
        """
        pass

    def refresh(self) -> None:
        """
        Refresh the panel content.
        Override this method in subclasses if needed.

        Returns:
            None
        """
        pass
