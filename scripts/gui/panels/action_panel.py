"""
action_panel.py

This module defines the ActionPanel class, which hosts buttons for actions such as summarizing or rebuilding.

Core features include:
- Creating buttons for summarizing and rebuilding functionality.
- Integrating with the application controller to trigger actions.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from scripts.gui.base.base_panel import BasePanel
from scripts.gui.widget_factory import WidgetFactory


class ActionPanel(BasePanel):
    """
    ActionPanel hosts buttons for actions such as summarizing or rebuilding.

    Attributes:
        frame (Optional[ttk.Frame]): The frame containing the action buttons.
        summarize_button (Optional[ttk.Button]): The button for summarizing logs.
        rebuild_button (Optional[ttk.Button]): The button for rebuilding the tracker.
    """

    def __init__(self, parent: tk.Widget, controller: Optional[object] = None, **kwargs) -> None:
        """
        Initializes the ActionPanel with the specified parent and controller.

        Args:
            parent (tk.Widget): The parent widget for this panel.
            controller (Optional[object]): The controller for handling actions. Defaults to None.
        """
        # Define instance attributes for type checkers
        self.frame: Optional[ttk.Frame] = None
        self.summarize_button: Optional[ttk.Button] = None
        self.rebuild_button: Optional[ttk.Button] = None
        super().__init__(parent, controller, **kwargs)

    def initialize_ui(self) -> None:
        """
        Creates and packs the action buttons into the panel.

        Returns:
            None
        """
        # Use a simple frame for action buttons
        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.X, padx=5, pady=5)

        # Create a Summarize button using the WidgetFactory
        self.summarize_button = WidgetFactory.create_button(
            self.frame, text="Summarize", command=self.on_summarize
        )
        self.summarize_button.pack(side=tk.LEFT, padx=5)

        # Create a Rebuild Tracker button
        self.rebuild_button = WidgetFactory.create_button(
            self.frame, text="Rebuild Tracker", command=self.on_rebuild
        )
        self.rebuild_button.pack(side=tk.LEFT, padx=5)

    def on_summarize(self) -> None:
        """
        Trigger the controller's summarize function if available.

        Returns:
            None
        """
        if self.controller and hasattr(self.controller, "force_summarize_all"):
            try:
                result = self.controller.force_summarize_all()
                print("Summary generated:", result)
            except Exception as e:
                print("Error during summarization:", e)
        else:
            print("Summarize action not available.")

    def on_rebuild(self) -> None:
        """
        Trigger the controller's rebuild_tracker function if available.

        Returns:
            None
        """
        if self.controller and hasattr(self.controller, "rebuild_tracker"):
            try:
                success = self.controller.rebuild_tracker()
                print("Rebuild successful:", success)
            except Exception as e:
                print("Error during rebuild:", e)
        else:
            print("Rebuild action not available.")

    def refresh(self) -> None:
        """
        Action panel may not need refreshing, but this hook is here if needed.

        Returns:
            None
        """
        pass
