import tkinter as tk
from tkinter import simpledialog, scrolledtext, ttk, font
import logging
from tkinter import PhotoImage

from scripts.config.config_loader import load_config, get_config_value
from scripts.gui.gui_logging import GUILogHandler
from scripts.gui.gui_controller import GUIController
import scripts.utils.gui_helpers as gui_helpers


class ZephyrusLoggerGUI:
    def __init__(self, controller: GUIController):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing ZephyrusLoggerGUI...")

        self.controller = controller
        self.config = load_config()
        self.category_structure = get_config_value(self.config, "category_structure", {})

        # Set up the root window with modern styling
        self.root = tk.Tk()
        self.root.title("Zephyrus Ideas Logger")
        self.root.geometry("1200x900")
        self.root.configure(bg="#f0f2f5")

        # Configure default font
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)
        self.root.option_add("*Font", default_font)

        # Define colors
        self.colors = {
            "primary": "#3f51b5",  # Deep blue
            "secondary": "#f5f5f5",  # Light gray
            "accent": "#4caf50",  # Green for success
            "warning": "#ff9800",  # Orange for warnings
            "error": "#f44336",  # Red for errors
            "text": "#212121",  # Dark text
            "light_text": "#757575",  # Light text
            "border": "#e0e0e0",  # Border color
        }

        # Configure ttk styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.colors["secondary"])
        self.style.configure(
            "TLabel", background=self.colors["secondary"], foreground=self.colors["text"]
        )
        self.style.configure(
            "TButton",
            background=self.colors["primary"],
            foreground="white",
            padding=6,
            relief="flat",
        )
        self.style.map("TButton", background=[("active", "#303f9f"), ("disabled", "#bdbdbd")])

        # Create primary notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create main tabs
        self.main_tab = ttk.Frame(self.notebook)
        self.search_tab = ttk.Frame(self.notebook)
        self.analytics_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.main_tab, text="Logger")
        self.notebook.add(self.search_tab, text="Search")
        self.notebook.add(self.analytics_tab, text="Analytics")

        self._build_main_tab()
        self._build_search_tab()
        self._build_analytics_tab()

        self._setup_gui_logging()
        self._update_coverage_display()

        # Add status bar at bottom of window
        self._create_status_bar()

    def _setup_gui_logging(self):
        gui_handler = GUILogHandler(self.log_display)
        gui_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        gui_handler.setFormatter(formatter)
        logging.getLogger().addHandler(gui_handler)

    def _build_main_tab(self):
        # Create paned window for resizable sections
        paned_window = ttk.PanedWindow(self.main_tab, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Top section - Logs
        logs_frame = ttk.LabelFrame(paned_window, text="Logs and Outputs")
        logs_frame.pack(fill=tk.BOTH, expand=True)

        self.log_display = scrolledtext.ScrolledText(
            logs_frame,
            width=120,
            height=8,
            bg=self.colors["secondary"],
            fg=self.colors["text"],
            font=("Consolas", 10),
        )
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add logs frame to paned window
        paned_window.add(logs_frame, weight=1)

        # Middle section - Coverage and Entry split
        middle_paned = ttk.PanedWindow(paned_window, orient=tk.HORIZONTAL)

        # Left side - Coverage overview
        coverage_frame = ttk.LabelFrame(middle_paned, text="Coverage Overview")

        # Replace scrolledtext with a proper Treeview for coverage data
        columns = ("Category", "Subcategory", "Coverage", "Progress")
        self.coverage_tree = ttk.Treeview(
            coverage_frame, columns=columns, show="headings", height=10
        )

        # Configure columns
        self.coverage_tree.heading("Category", text="Main Category")
        self.coverage_tree.heading("Subcategory", text="Subcategory")
        self.coverage_tree.heading("Coverage", text="Coverage %")
        self.coverage_tree.heading("Progress", text="Entries")

        self.coverage_tree.column("Category", width=120)
        self.coverage_tree.column("Subcategory", width=120)
        self.coverage_tree.column("Coverage", width=80, anchor="center")
        self.coverage_tree.column("Progress", width=80, anchor="center")

        # Add scrollbar to treeview
        coverage_scrollbar = ttk.Scrollbar(
            coverage_frame, orient="vertical", command=self.coverage_tree.yview
        )
        self.coverage_tree.configure(yscrollcommand=coverage_scrollbar.set)

        coverage_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.coverage_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        middle_paned.add(coverage_frame, weight=1)

        # Right side - New entry
        entry_frame = ttk.LabelFrame(middle_paned, text="Log New Entry")

        # Entry content
        self.entry_box = tk.Text(
            entry_frame,
            height=10,
            width=60,
            bg="white",
            fg=self.colors["text"],
            font=("Segoe UI", 10),
            padx=5,
            pady=5,
            wrap=tk.WORD,
        )
        self.entry_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Entry placeholder and focus events
        self.entry_placeholder = "Type your entry here..."
        self.entry_box.insert("1.0", self.entry_placeholder)
        self.entry_box.configure(fg=self.colors["light_text"])

        self.entry_box.bind("<FocusIn>", self._on_entry_focus_in)
        self.entry_box.bind("<FocusOut>", self._on_entry_focus_out)

        # Categories and submit button frame
        cat_frame = ttk.Frame(entry_frame)
        cat_frame.pack(fill=tk.X, padx=5, pady=5)

        # Main category selection with improved dropdown
        cat_label_frame = ttk.Frame(cat_frame)
        cat_label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(cat_label_frame, text="Main Category:").pack(side=tk.LEFT, padx=(0, 5))
        self.selected_category_main = tk.StringVar()
        self.main_combobox = ttk.Combobox(
            cat_label_frame, textvariable=self.selected_category_main, state="readonly", width=20
        )
        self.main_combobox.pack(side=tk.LEFT, padx=5)
        self.main_combobox.bind(
            "<<ComboboxSelected>>",
            lambda e: self._update_main_category(self.selected_category_main.get()),
        )

        ttk.Label(cat_label_frame, text="Subcategory:").pack(side=tk.LEFT, padx=(10, 5))
        self.selected_subcategory = tk.StringVar()
        self.sub_combobox = ttk.Combobox(
            cat_label_frame, textvariable=self.selected_subcategory, state="readonly", width=20
        )
        self.sub_combobox.pack(side=tk.LEFT, padx=5)

        # Log button
        log_button = ttk.Button(
            cat_frame, text="Log Entry", command=self._log_entry, style="Accent.TButton"
        )
        log_button.pack(side=tk.RIGHT, padx=5)

        # Populate category dropdowns
        self._populate_category_dropdown()

        middle_paned.add(entry_frame, weight=1)

        # Add middle paned window to main paned window
        paned_window.add(middle_paned, weight=2)

        # Add action buttons at the bottom
        action_frame = ttk.Frame(self.main_tab)
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        # Create buttons with icons (using text for now, can be replaced with actual icons)
        self.summarize_button = ttk.Button(
            action_frame, text="🧠 Summarize", command=self._manual_summarize
        )
        self.summarize_button.pack(side=tk.LEFT, padx=5)

        self.coverage_button = ttk.Button(
            action_frame, text="📊 Coverage", command=self._show_coverage
        )
        self.coverage_button.pack(side=tk.LEFT, padx=5)

        self.rebuild_button = ttk.Button(
            action_frame, text="📁 Rebuild Tracker", command=self._rebuild_tracker
        )
        self.rebuild_button.pack(side=tk.LEFT, padx=5)

    def _build_search_tab(self):
        search_container = ttk.Frame(self.search_tab)
        search_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create notebook for search types
        search_notebook = ttk.Notebook(search_container)
        search_notebook.pack(fill=tk.BOTH, expand=True)

        # Create frames for each search type
        summary_search_frame = ttk.Frame(search_notebook)
        raw_search_frame = ttk.Frame(search_notebook)
        advanced_search_frame = ttk.Frame(search_notebook)

        search_notebook.add(summary_search_frame, text="Summary Search")
        search_notebook.add(raw_search_frame, text="Raw Log Search")
        search_notebook.add(advanced_search_frame, text="Advanced Search")

        # Build Summary Search tab
        self._build_summary_search(summary_search_frame)
        self._build_raw_search(raw_search_frame)
        self._build_advanced_search(advanced_search_frame)

    def _build_summary_search(self, parent):
        # Search box with label
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_frame, text="Search Term:").pack(side=tk.LEFT, padx=(0, 10))
        self.summary_search_entry = ttk.Entry(search_frame, width=40)
        self.summary_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        search_button = ttk.Button(
            search_frame, text="Search", command=self._search_summary_from_entry
        )
        search_button.pack(side=tk.RIGHT, padx=5)

        # Results area with a better display
        results_frame = ttk.LabelFrame(parent, text="Search Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Use Text widget with better formatting for JSON display
        self.summary_results = tk.Text(
            results_frame,
            wrap=tk.WORD,
            bg="white",
            fg=self.colors["text"],
            font=("Consolas", 10),
            padx=5,
            pady=5,
        )
        results_scrollbar = ttk.Scrollbar(
            results_frame, orient="vertical", command=self.summary_results.yview
        )
        self.summary_results.configure(yscrollcommand=results_scrollbar.set)

        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.summary_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add tags for syntax highlighting
        self.summary_results.tag_configure("key", foreground="#0d47a1")
        self.summary_results.tag_configure("value", foreground="#1a237e")
        self.summary_results.tag_configure("number", foreground="#1b5e20")
        self.summary_results.tag_configure("string", foreground="#b71c1c")

    def _build_raw_search(self, parent):
        # Search box with label
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_frame, text="Search Term:").pack(side=tk.LEFT, padx=(0, 10))
        self.raw_search_entry = ttk.Entry(search_frame, width=40)
        self.raw_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        search_button = ttk.Button(search_frame, text="Search", command=self._search_raw_from_entry)
        search_button.pack(side=tk.RIGHT, padx=5)

        # Results area with a better display
        results_frame = ttk.LabelFrame(parent, text="Search Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Use Text widget with better formatting
        self.raw_results = tk.Text(
            results_frame,
            wrap=tk.WORD,
            bg="white",
            fg=self.colors["text"],
            font=("Consolas", 10),
            padx=5,
            pady=5,
        )
        results_scrollbar = ttk.Scrollbar(
            results_frame, orient="vertical", command=self.raw_results.yview
        )
        self.raw_results.configure(yscrollcommand=results_scrollbar.set)

        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.raw_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add tags for syntax highlighting
        self.raw_results.tag_configure("key", foreground="#0d47a1")
        self.raw_results.tag_configure("value", foreground="#1a237e")
        self.raw_results.tag_configure("number", foreground="#1b5e20")
        self.raw_results.tag_configure("string", foreground="#b71c1c")
        self.raw_results.tag_configure(
            "header", foreground="#880e4f", font=("Consolas", 10, "bold")
        )

    def _build_advanced_search(self, parent):
        # Placeholder for advanced search (can be implemented later)
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Advanced search options coming soon...").pack(pady=20)

        # Add other widgets and functionality as needed

    def _build_analytics_tab(self):
        analytics_container = ttk.Frame(self.analytics_tab)
        analytics_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Charts section
        charts_frame = ttk.LabelFrame(analytics_container, text="Analytics Overview")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Placeholder for charts (would integrate with matplotlib or other charting library)
        ttk.Label(charts_frame, text="Analytics visualizations will appear here").pack(pady=20)

        # Controls for analytics
        controls_frame = ttk.Frame(analytics_container)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(controls_frame, text="Generate Reports", command=lambda: None).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(controls_frame, text="Export Data", command=lambda: None).pack(
            side=tk.LEFT, padx=5
        )

    def _create_status_bar(self):
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Tracker status
        self.tracker_status = tk.StringVar()
        self.tracker_status.set(f"Summary Tracker: {self.controller.get_tracker_status()}")

        status_label = ttk.Label(status_bar, textvariable=self.tracker_status, padding=(5, 2))
        status_label.pack(side=tk.LEFT)

        # Version info
        version_label = ttk.Label(status_bar, text="v1.0.0", padding=(5, 2))
        version_label.pack(side=tk.RIGHT)

    def _populate_category_dropdown(self):
        categories = list(self.category_structure.keys())

        # Configure main category dropdown
        self.main_combobox["values"] = categories
        if categories:
            self.selected_category_main.set(categories[0])
            self._update_main_category(categories[0])
        else:
            self.selected_category_main.set("NoCategories")

    def _update_main_category(self, new_main):
        self.selected_category_main.set(new_main)
        subcats = self.category_structure.get(new_main, [])

        # Configure subcategory dropdown
        self.sub_combobox["values"] = subcats
        if subcats:
            self.selected_subcategory.set(subcats[0])
        else:
            self.selected_subcategory.set("")

    def _update_coverage_display(self):
        try:
            data = self.controller.get_coverage_data()

            # Clear existing items
            for item in self.coverage_tree.get_children():
                self.coverage_tree.delete(item)

            # Add new data
            for i, entry in enumerate(data):
                summarized = entry.get("summarized_total") or entry.get(
                    "estimated_summarized_entries", 0
                )
                percent = entry.get("coverage_percent", 0)

                # Set row colors based on coverage percent
                tag = f"coverage_{i}"
                if percent >= 70:
                    self.coverage_tree.tag_configure(tag, background="#c8e6c9")  # Light green
                elif percent >= 30:
                    self.coverage_tree.tag_configure(tag, background="#fff9c4")  # Light yellow
                else:
                    self.coverage_tree.tag_configure(tag, background="#ffcdd2")  # Light red

                self.coverage_tree.insert(
                    "",
                    "end",
                    values=(
                        entry["main_category"],
                        entry["subcategory"],
                        f"{percent}%",
                        f"{summarized}/{entry['logged_total']}",
                    ),
                    tags=(tag,),
                )

        except Exception as e:
            self.logger.error(f"Error updating coverage: {str(e)}")

    def _on_entry_focus_in(self, event):
        if self.entry_box.get("1.0", "end-1c") == self.entry_placeholder:
            self.entry_box.delete("1.0", tk.END)
            self.entry_box.configure(fg=self.colors["text"])

    def _on_entry_focus_out(self, event):
        if not self.entry_box.get("1.0", "end-1c").strip():
            self.entry_box.insert("1.0", self.entry_placeholder)
            self.entry_box.configure(fg=self.colors["light_text"])

    def _log_entry(self):
        main = self.selected_category_main.get()
        sub = self.selected_subcategory.get()
        text = self.entry_box.get("1.0", tk.END).strip()

        # Don't submit if it's just the placeholder
        if text and text != self.entry_placeholder:
            try:
                result = self.controller.log_entry(main, sub, text)
                gui_helpers.display_message("Success", f"Entry logged successfully: {result}")
                self.entry_box.delete("1.0", tk.END)
                self._on_entry_focus_out(None)
                self._update_coverage_display()
            except Exception as e:
                gui_helpers.display_error("Error", f"Failed to log entry: {str(e)}")
        else:
            gui_helpers.display_error("Error", "Please enter text for your log entry.")

    def _format_json_for_display(self, text_widget, json_text):
        """Helper function to display formatted JSON with syntax highlighting"""
        import json

        try:
            # Parse and re-stringify the JSON with nice formatting
            parsed = json.loads(json_text) if isinstance(json_text, str) else json_text
            formatted = json.dumps(parsed, indent=2)

            # Clear the widget
            text_widget.delete("1.0", tk.END)

            # Insert with syntax highlighting
            import re

            lines = formatted.split("\n")
            for line in lines:
                # Highlight keys
                key_match = re.search(r'"([^"]+)"\s*:', line)
                if key_match:
                    pre = line[: key_match.start()]
                    key = line[key_match.start() : key_match.end()]
                    post = line[key_match.end() :]

                    text_widget.insert(tk.END, pre)
                    text_widget.insert(tk.END, key, "key")

                    # Handle values
                    if ":" in post:
                        value_part = post.split(":", 1)[1].strip()
                        colon_part = post.split(":", 1)[0] + ": "

                        text_widget.insert(tk.END, colon_part)

                        # Number value
                        if re.match(r"^-?\d+(\.\d+)?$", value_part) or value_part in [
                            "true",
                            "false",
                            "null",
                        ]:
                            text_widget.insert(tk.END, value_part, "number")
                        # String value
                        elif re.match(r'^"[^"]*"', value_part):
                            text_widget.insert(tk.END, value_part, "string")
                        else:
                            text_widget.insert(tk.END, value_part)
                    else:
                        text_widget.insert(tk.END, post)
                else:
                    text_widget.insert(tk.END, line)

                text_widget.insert(tk.END, "\n")

            return True
        except Exception as e:
            text_widget.delete("1.0", tk.END)
            text_widget.insert(tk.END, f"Error formatting JSON: {str(e)}\n\n{json_text}")
            return False

    def _search_summary_from_entry(self):
        query = self.summary_search_entry.get().strip()
        if query:
            try:
                results = self.controller.search_summaries(query)
                if results:
                    # Use JSON formatter to display results
                    self._format_json_for_display(self.summary_results, results[0])
                else:
                    self.summary_results.delete("1.0", tk.END)
                    self.summary_results.insert(tk.END, "No summaries found.")
            except Exception as e:
                self.summary_results.delete("1.0", tk.END)
                self.summary_results.insert(tk.END, f"Error: {str(e)}")
        else:
            self.summary_results.delete("1.0", tk.END)
            self.summary_results.insert(tk.END, "Please enter a search term")

    def _search_raw_from_entry(self):
        query = self.raw_search_entry.get().strip()
        if query:
            try:
                results = self.controller.search_raw_logs(query)
                self.raw_results.delete("1.0", tk.END)
                if results:
                    # Add header
                    self.raw_results.insert(tk.END, "[RAW LOG MATCH]\n", "header")
                    # Use JSON formatter
                    self._format_json_for_display(self.raw_results, results[0])
                else:
                    self.raw_results.insert(tk.END, "No raw logs found.")
            except Exception as e:
                self.raw_results.delete("1.0", tk.END)
                self.raw_results.insert(tk.END, f"Error: {str(e)}")
        else:
            self.raw_results.delete("1.0", tk.END)
            self.raw_results.insert(tk.END, "Please enter a search term")

    def _manual_summarize(self):
        main = self.selected_category_main.get()
        sub = self.selected_subcategory.get()
        try:
            result = self.controller.core.generate_global_summary(main, sub)
            gui_helpers.display_message("Success", f"Summary generated: {result}")
            self._update_coverage_display()
        except Exception as e:
            gui_helpers.display_error("Error", f"Summarization failed: {str(e)}")

    def _rebuild_tracker(self):
        try:
            success = self.controller.rebuild_tracker()
            self.tracker_status.set(
                f"Summary Tracker: {'✅ Valid (Rebuilt)' if success else '❌ Still Invalid'}"
            )
            msg = (
                "Tracker successfully rebuilt."
                if success
                else "Tracker rebuild failed. Still invalid."
            )
            gui_helpers.display_message("Tracker Status", msg)
            self._update_coverage_display()
        except Exception as e:
            gui_helpers.display_error("Error", f"Tracker rebuild failed: {str(e)}")

    def _show_coverage(self):
        try:
            coverage_data = self.controller.get_coverage_data()
            formatted = gui_helpers.format_coverage_data(coverage_data)
            gui_helpers.display_message("Coverage Report", formatted)
        except Exception as e:
            gui_helpers.display_error("Error", f"Failed to show coverage: {str(e)}")

    def run(self):
        self.root.mainloop()
