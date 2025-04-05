# scripts/gui/gui.py

import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
from scripts.gui.gui_controller import GUIController
import scripts.utils.gui_helpers as gui_helpers

class ZephyrusLoggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Zephyrus Ideas Logger")
        # With the updated GUIController, no parameters are necessary.
        self.controller = GUIController()
        self._build_widgets()

    def _build_widgets(self):
        # Top Entry Area
        self.entry_box = tk.Text(self.root, height=5, width=80)
        self.entry_box.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        self.category_entry = tk.Entry(self.root, width=20)
        self.category_entry.insert(0, "MainCategory")
        self.category_entry.grid(row=1, column=0, padx=5)

        self.subcategory_entry = tk.Entry(self.root, width=20)
        self.subcategory_entry.insert(0, "Subcategory")
        self.subcategory_entry.grid(row=1, column=1, padx=5)

        self.log_button = tk.Button(self.root, text="Log Entry", command=self._log_entry)
        self.log_button.grid(row=1, column=2, padx=5)

        self.summarize_button = tk.Button(self.root, text="Summarize", command=self._manual_summarize)
        self.summarize_button.grid(row=1, column=3, padx=5)

        # Search Section
        self.search_entry = tk.Entry(self.root, width=50)
        self.search_entry.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        self.search_summary_button = tk.Button(self.root, text="Search Summary", command=self._search_summary)
        self.search_summary_button.grid(row=2, column=2, padx=5)

        self.search_raw_button = tk.Button(self.root, text="Search Raw Log", command=self._search_raw)
        self.search_raw_button.grid(row=2, column=3, padx=5)

        # Log Display Area
        self.log_display = scrolledtext.ScrolledText(self.root, width=80, height=20)
        self.log_display.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

    def _log_entry(self):
        try:
            main = self.category_entry.get()
            sub = self.subcategory_entry.get()
            text = self.entry_box.get("1.0", tk.END).strip()
            if text:
                result = self.controller.log_entry(main, sub, text)
                gui_helpers.display_message("Logged", f"Entry logged successfully: {result}")
                self.entry_box.delete("1.0", tk.END)
            else:
                gui_helpers.display_error("Error", "No text entered.")
        except Exception as e:
            gui_helpers.display_error("Logging Error", str(e))

    def _manual_summarize(self):
        try:
            result = self.controller.force_summarize_all()
            gui_helpers.display_message("Summarize", f"Summarization complete: {result}")
        except Exception as e:
            gui_helpers.display_error("Summarization Error", str(e))

    def _search_summary(self):
        try:
            query = self.search_entry.get()
            result = self.controller.search_summaries(query)
            gui_helpers.display_message("Search Summary", f"Found summaries: {result}")
        except Exception as e:
            gui_helpers.display_error("Search Error", str(e))

    def _search_raw(self):
        try:
            query = self.search_entry.get()
            result = self.controller.search_raw_logs(query)
            gui_helpers.display_message("Search Raw Log", f"Found raw logs: {result}")
        except Exception as e:
            gui_helpers.display_error("Search Error", str(e))
