import tkinter as tk
from tkinter import ttk


class BasePanel(ttk.Frame):
    """
    BasePanel provides common functionality for all UI panels.
    Inherits from ttk.Frame to leverage consistent styling.
    """

    def __init__(self, parent, controller=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.initialize_ui()

    def initialize_ui(self):
        """
        Set up UI components for the panel.
        Override this method in subclasses to build specific panel content.
        """
        pass

    def refresh(self):
        """
        Refresh the panel content.
        Override this method in subclasses if needed.
        """
        pass
