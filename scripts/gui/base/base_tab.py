"""
base_tab.py

This module defines the BaseTab class, which provides a common structure for major tabs in the application.

Core features include:
- Providing a base class for tabs with consistent styling.
- Allowing subclasses to implement specific tab components and behavior.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class BaseTab(ttk.Frame):
    """
    BaseTab provides a common structure for major tabs in the application.
    Inherits from ttk.Frame for consistent styling.

    Attributes:
        controller (Optional[object]): The controller for handling tab actions.
    """

    def __init__(self, parent: tk.Widget, controller: Optional[object] = None, **kwargs) -> None:
        """
        Initializes the BaseTab with the specified parent and controller.

        Args:
            parent (tk.Widget): The parent widget for this tab.
            controller (Optional[object]): The controller for handling tab actions. Defaults to None.
        """
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.setup_tab()

    def setup_tab(self) -> None:
        """
        Set up the tab contents.
        Override this method in subclasses to build tab-specific components.

        Returns:
            None
        """
        pass

    def on_show(self) -> None:
        """
        Called when the tab becomes active.
        Override to update or refresh content when the tab is shown.

        Returns:
            None
        """
        pass
