"""
gui.py

This module provides the ZephyrusLoggerGUI class, which implements a graphical user interface
for the Zephyrus Ideas Logger application using the tkinter library. It manages the GUI components,
user interactions, and integrates logging functionality.
"""

import tkinter as tk
from tkinter import simpledialog, scrolledtext, ttk
import logging

from scripts.config.config_loader import load_config, get_config_value
from scripts.gui.gui_logging import GUILogHandler
from scripts.gui.gui_controller import GUIController
import scripts.gui.gui_helpers as gui_helpers


class ZephyrusLoggerGUI:
    """
    A class to represent the Zephyrus Ideas Logger GUI.

    This class initializes the GUI components and handles user interactions.

    Attributes:
        controller (GUIController): The controller for managing the application's logic.
        logger (logging.Logger): Logger for tracking GUI events and actions.
        config (dict): Configuration settings loaded from the config file.
        category_structure (dict): Structure of categories for the GUI.
        root (tk.Tk): The main window of the GUI application.
    """

    def __init__(self, controller: GUIController) -> None:
        """
        Initialize the ZephyrusLoggerGUI.

        Args:
            controller (GUIController): The controller for managing the application's logic.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing ZephyrusLoggerGUI...")

        self.controller = controller
        self.config = load_config()
        self.category_structure = get_config_value(self.config, "category_structure", {})

        self.root = tk.Tk()
        self.root.title("Zephyrus Ideas Logger")
        self.root.geometry("1024x1024")

        self._build_widgets()
        self._setup_gui_logging()
        self._update_coverage_display()

    def _setup_gui_logging(self) -> None:
        """
        Set up the logging for the GUI.

        This method configures the logging handler to display logs in the GUI.
        """
        gui_handler = GUILogHandler(self.log_display)
        gui_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        gui_handler.setFormatter(formatter)
        logging.getLogger().addHandler(gui_handler)

    def _build_widgets(self) -> None:
        """
        Build the GUI widgets and layout.

        This method creates and arranges the GUI components, such as frames and buttons.
        """
        # --- Category Selection ---
        category_frame = tk.Frame(self.root)
        category_frame.grid(row=0, column=0, columnspan=6, pady=5)

        self.selected_category_main = tk.StringVar()
        self.selected_subcategory = tk.StringVar()

        tk.Label(category_frame, text="Main Category:").grid(row=0, column=0, sticky=tk.E, padx=5)
        self.main_menu = tk.OptionMenu(category_frame, self.selected_category_main, "")
        self.main_menu.grid(row=0, column=1, sticky=tk.W)

        tk.Label(category_frame, text="Subcategory:").grid(row=0, column=2, sticky=tk.E, padx=5)
        self.sub_menu = tk.OptionMenu(category_frame, self.selected_subcategory, "")
        self.sub_menu.grid(row=0, column=3, sticky=tk.W)

        self._populate_category_dropdown()

        # --- Action Buttons ---
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=1, column=0, columnspan=6, pady=10)

        self.log_button = tk.Button(
            button_frame, text="➕ Log Entry", width=18, height=2, command=self._log_entry
        )
        self.log_button.grid(row=0, column=0, padx=5)

        self.summarize_button = tk.Button(
            button_frame, text="🧠 Summarize", width=18, height=2, command=self._manual_summarize
        )
        self.summarize_button.grid(row=0, column=1, padx=5)

        self.search_summary_button = tk.Button(
            button_frame, text="🔍 Search Summary", width=18, height=2, command=self._search_summary
        )
        self.search_summary_button.grid(row=0, column=2, padx=5)

        self.search_raw_button = tk.Button(
            button_frame, text="📜 Search Raw Log", width=18, height=2, command=self._search_raw
        )
        self.search_raw_button.grid(row=0, column=3, padx=5)

        self.coverage_button = tk.Button(
            button_frame, text="📊 Coverage", width=18, height=2, command=self._show_coverage
        )
        self.coverage_button.grid(row=0, column=4, padx=5)

        self.rebuild_button = tk.Button(
            button_frame,
            text="📁 Rebuild Tracker",
            width=18,
            height=2,
            command=self._rebuild_tracker,
        )
        self.rebuild_button.grid(row=0, column=5, padx=5)

        # --- Tracker Status ---
        self.tracker_status = tk.StringVar()
        self.tracker_status.set(f"Summary Tracker: {self.controller.get_tracker_status()}")
        self.status_label = tk.Label(self.root, textvariable=self.tracker_status, fg="blue")
        self.status_label.grid(row=2, column=0, columnspan=6, pady=(0, 5))

        # --- Coverage Display ---
        tk.Label(self.root, text="📊 Coverage Overview:").grid(row=3, column=0, columnspan=6)
        self.coverage_frame = scrolledtext.ScrolledText(
            self.root, width=120, height=10, state="disabled"
        )
        self.coverage_frame.grid(row=4, column=0, columnspan=6, padx=10, pady=5)

        # --- Logs Display ---
        tk.Label(self.root, text="📋 Logs & Output").grid(row=5, column=0, columnspan=6)
        self.log_display = scrolledtext.ScrolledText(self.root, width=120, height=10)
        self.log_display.grid(row=6, column=0, columnspan=6, padx=10, pady=5)

        # --- Log Entry Box (Bottom Priority) ---
        tk.Label(self.root, text="📝 Log New Entry").grid(row=7, column=0, columnspan=6)
        self.entry_box = tk.Text(self.root, height=5, width=120)
        self.entry_box.grid(row=8, column=0, columnspan=6, padx=10, pady=10)

    def _update_coverage_display(self) -> None:
        """
        Update the coverage display.

        This method retrieves the coverage data from the controller and updates the coverage display.
        """
        try:
            data = self.controller.get_coverage_data()
            self.coverage_frame.configure(state="normal")
            self.coverage_frame.delete("1.0", tk.END)

            for entry in data:
                summarized = entry.get("summarized_total") or entry.get(
                    "estimated_summarized_entries", 0
                )
                percent = entry.get("coverage_percent", 0)
                symbol = "✅" if percent >= 30 else "⚠️" if percent > 0 else "❌"
                line = f"{symbol} {entry['main_category']} > {entry['subcategory']}: {percent}% ({summarized}/{entry['logged_total']})\n"
                self.coverage_frame.insert(tk.END, line)

            self.coverage_frame.configure(state="disabled")
        except Exception as e:
            self.coverage_frame.configure(state="normal")
            self.coverage_frame.delete("1.0", tk.END)
            self.coverage_frame.insert(tk.END, f"Error updating coverage: {str(e)}\n")
            self.coverage_frame.configure(state="disabled")

    def _populate_category_dropdown(self) -> None:
        """
        Populate the category dropdown menu.

        This method retrieves the categories from the controller and populates the dropdown menu.
        """
        categories = list(self.category_structure.keys())
        self.selected_category_main.set(categories[0] if categories else "NoCategories")
        self.main_menu["menu"].delete(0, "end")
        for cat in categories:
            self.main_menu["menu"].add_command(
                label=cat, command=lambda c=cat: self._update_main_category(c)
            )
        self._update_main_category(self.selected_category_main.get())

    def _update_main_category(self, new_main: str) -> None:
        """
        Update the main category.

        This method updates the main category and subcategory dropdown menus.

        Args:
            new_main (str): The new main category.
        """
        self.selected_category_main.set(new_main)
        subcats = self.category_structure.get(new_main, [])
        self.selected_subcategory.set(subcats[0] if subcats else "")
        self.sub_menu["menu"].delete(0, "end")
        for sc in subcats:
            self.sub_menu["menu"].add_command(
                label=sc, command=lambda s=sc: self.selected_subcategory.set(s)
            )

    def _log_entry(self) -> None:
        """
        Log a new entry.

        This method logs a new entry based on the user's input.
        """
        main = self.selected_category_main.get()
        sub = self.selected_subcategory.get()
        text = self.entry_box.get("1.0", tk.END).strip()
        if text:
            try:
                result = self.controller.log_entry(main, sub, text)
                gui_helpers.display_message("Logged", f"Entry logged successfully: {result}")
                self.entry_box.delete("1.0", tk.END)
                self._update_coverage_display()
            except Exception as e:
                gui_helpers.display_error("Logging Error", str(e))
        else:
            gui_helpers.display_error("Error", "No text entered.")

    def _manual_summarize(self) -> None:
        """
        Manually summarize the logs.

        This method generates a summary of the logs based on the user's input.
        """
        main = self.selected_category_main.get()
        sub = self.selected_subcategory.get()
        try:
            result = self.controller.core.generate_global_summary(main, sub)
            gui_helpers.display_message("Summarized", f"Summary generated: {result}")
            self._update_coverage_display()
        except Exception as e:
            gui_helpers.display_error("Summarization Error", str(e))

    def _search_summary(self) -> None:
        """
        Search for summaries.

        This method searches for summaries based on the user's input.
        """
        query = simpledialog.askstring("Search Summaries", "Enter your search query:")
        if query:
            try:
                results = self.controller.search_summaries(query)
                if results:
                    formatted = gui_helpers.format_summary_results(results)
                    gui_helpers.display_message("Search Summary", f"Found summaries:\n{formatted}")
                else:
                    gui_helpers.display_message("Search Summary", "No summaries found.")
            except Exception as e:
                gui_helpers.display_error("Search Error", str(e))

    def _search_raw(self) -> None:
        """
        Search for raw logs.

        This method searches for raw logs based on the user's input.
        """
        query = simpledialog.askstring("Search Raw Logs", "Enter your search query:")
        if query:
            try:
                results = self.controller.search_raw_logs(query)
                if results:
                    formatted = gui_helpers.format_raw_results(results)
                    gui_helpers.display_message("Search Raw Log", f"Found raw logs:\n{formatted}")
                else:
                    gui_helpers.display_message("Search Raw Log", "No raw logs found.")
            except Exception as e:
                gui_helpers.display_error("Search Error", str(e))

    def _rebuild_tracker(self) -> None:
        """
        Rebuild the tracker.

        This method rebuilds the tracker based on the user's input.
        """
        try:
            success = self.controller.rebuild_tracker()
            self.tracker_status.set(
                f"Summary Tracker: {'✅ Valid (After Rebuild)' if success else '❌ Still Invalid'}"
            )
            msg = (
                "Tracker successfully rebuilt."
                if success
                else "Tracker rebuild failed. Still invalid."
            )
            gui_helpers.display_message("Rebuild Tracker", msg)
            self._update_coverage_display()
        except Exception as e:
            gui_helpers.display_error("Tracker Rebuild Error", str(e))

    def _show_coverage(self) -> None:
        """
        Show the coverage.

        This method displays the coverage data.
        """
        try:
            coverage_data = self.controller.get_coverage_data()
            formatted = gui_helpers.format_coverage_data(coverage_data)
            gui_helpers.display_message("Summary Coverage", formatted)
        except Exception as e:
            gui_helpers.display_error("Coverage Error", str(e))

    def run(self) -> None:
        """
        Run the GUI application.

        This method starts the GUI event loop.
        """
        self.root.mainloop()
