"""
coverage_panel.py

This module defines the CoveragePanel class, which displays coverage metrics in a tree view.

Core features include:
- Displaying coverage metrics for various categories.
- Integrating with the application controller to fetch coverage data.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from scripts.gui.base.base_panel import BasePanel


class CoveragePanel(BasePanel):
    """
    CoveragePanel displays coverage metrics in a tree view.

    Attributes:
        frame (Optional[ttk.LabelFrame]): The frame containing the coverage metrics.
        tree (Optional[ttk.Treeview]): The tree view for displaying coverage data.
    """

    def __init__(self, parent: tk.Widget, controller: Optional[object] = None, **kwargs) -> None:
        """
        Initializes the CoveragePanel with the specified parent and controller.

        Args:
            parent (tk.Widget): The parent widget for this panel.
            controller (Optional[object]): The controller for handling coverage data. Defaults to None.
        """
        # Define instance attributes for type checkers
        self.frame: Optional[ttk.LabelFrame] = None
        self.tree: Optional[ttk.Treeview] = None
        super().__init__(parent, controller, **kwargs)

    def initialize_ui(self) -> None:
        """
        Creates and packs the user interface components for the coverage panel.

        Returns:
            None
        """
        # Create a labeled frame for coverage overview
        self.frame = ttk.LabelFrame(self, text="Coverage Overview")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Define columns for the tree view
        columns = ("Category", "Coverage")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Coverage", text="Coverage %")
        self.tree.column("Category", width=120)
        self.tree.column("Coverage", width=80)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def refresh(self) -> None:
        """
        Refreshes the coverage data displayed in the tree view.

        Returns:
            None
        """
        # Clear existing items in the tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Check if the controller is available and has the required method
        if self.controller and hasattr(self.controller, "get_coverage_data"):
            try:
                # Retrieve coverage data from the controller
                data = self.controller.get_coverage_data()
                # Assume data is a list of dictionaries with keys "Category" and "Coverage"
                for entry in data:
                    category = entry.get("Category", "N/A")
                    coverage = entry.get("Coverage", "N/A")
                    self.tree.insert("", "end", values=(category, f"{coverage}%"))
            except Exception as e:
                print("Error retrieving coverage data:", e)
        else:
            print("Controller not available or does not implement get_coverage_data.")
