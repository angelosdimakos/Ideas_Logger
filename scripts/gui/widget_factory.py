import tkinter as tk
from tkinter import ttk

class WidgetFactory:
    """
    Factory for creating common widgets with standardized styling.
    """
    @staticmethod
    def create_button(parent, text, command, style="TButton", **options):
        """
        Create and return a styled ttk Button.
        """
        return ttk.Button(parent, text=text, command=command, style=style, **options)

    @staticmethod
    def create_label(parent, text, style="TLabel", **options):
        """
        Create and return a styled ttk Label.
        """
        return ttk.Label(parent, text=text, style=style, **options)

    @staticmethod
    def create_entry(parent, textvariable=None, **options):
        """
        Create and return a ttk Entry widget.
        """
        return ttk.Entry(parent, textvariable=textvariable, **options)

    @staticmethod
    def create_frame(parent, style="TFrame", **options):
        """
        Create and return a ttk Frame widget.
        """
        return ttk.Frame(parent, style=style, **options)

    @staticmethod
    def create_notebook(parent, **options):
        """
        Create and return a ttk Notebook widget.
        """
        return ttk.Notebook(parent, **options)
