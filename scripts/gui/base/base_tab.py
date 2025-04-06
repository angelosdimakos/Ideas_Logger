import tkinter as tk
from tkinter import ttk

class BaseTab(ttk.Frame):
    """
    BaseTab provides a common structure for major tabs in the application.
    Inherits from ttk.Frame for consistent styling.
    """
    def __init__(self, parent, controller=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.setup_tab()

    def setup_tab(self):
        """
        Set up the tab contents.
        Override this method in subclasses to build tab-specific components.
        """
        pass

    def on_show(self):
        """
        Called when the tab becomes active.
        Override to update or refresh content when the tab is shown.
        """
        pass
