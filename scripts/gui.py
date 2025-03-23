import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
import json
import os
from scripts.summary_indexer import SummaryIndexer
from scripts.raw_log_indexer import RawLogIndexer
from scripts.config_loader import load_config, get_config_value, get_absolute_path
import utils.gui_helpers as gui_helpers

class ZephyrusLoggerGUI:
    def __init__(self, logger_core):
        self.logger_core = logger_core
        self._init_state()
        self._init_ui()
        self._init_faiss()
        self._bind_events()
        self.log_message("Zephyrus Idea Logger initialized. Ready for entries.")

    def _init_state(self):
        self.root = tk.Tk()
        self.root.title("Zephyrus Idea Logger (with FAISS Search)")
        self.root.geometry("700x650")
        self.root.attributes("-topmost", True)

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")

        config = load_config()
        self.category_structure = get_config_value(config, "category_structure", {})
        self.selected_category_main = tk.StringVar()
        self.selected_subcategory = tk.StringVar()

        self.indexer = SummaryIndexer()
        self.raw_indexer = RawLogIndexer()

    def _init_ui(self):
        self.status_label = gui_helpers.create_status_label(self.root, self.status_var)
        self.log_text, self.log_frame = gui_helpers.create_log_frame(self.root)
        self.text_entry = gui_helpers.create_text_entry(self.root)

        self._create_category_selector()
        self._create_main_buttons()
        self._create_faiss_panel()
        self._create_rawlog_panel()

    def _init_faiss(self):
        pass  # Reserved for future FAISS setup

    def _bind_events(self):
        self.text_entry.bind("<Control-Return>", lambda event: self._save_entry())

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _create_category_selector(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=5)

        tk.Label(frame, text="Category:").pack(side=tk.LEFT, padx=(0, 5))
        default_main = next(iter(self.category_structure), "")
        self.selected_category_main.set(default_main)

        main_menu = tk.OptionMenu(frame, self.selected_category_main, *self.category_structure.keys())
        main_menu.pack(side=tk.LEFT, padx=(0, 15))

        self.selected_category_main.trace_add("write", lambda *args: self._update_subcategories(self.selected_category_main.get()))

        tk.Label(frame, text="Subcategory:").pack(side=tk.LEFT, padx=(0, 5))
        self.sub_menu = tk.OptionMenu(frame, self.selected_subcategory, "")
        self.sub_menu.pack(side=tk.LEFT)

        self._update_subcategories(default_main)

    def _update_subcategories(self, main_category):
        subcats = self.category_structure.get(main_category, [])
        if subcats:
            self.selected_subcategory.set(subcats[0])
        menu = self.sub_menu["menu"]
        menu.delete(0, "end")
        for subcat in subcats:
            menu.add_command(label=subcat, command=lambda sc=subcat: self.selected_subcategory.set(sc))

    def _create_main_buttons(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Button(frame, text="Log Idea", command=self._save_entry, width=15, height=2, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(frame, text="Force Summarize", command=self._manual_summarize, width=15, height=2, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=10)

    def _create_faiss_panel(self):
        frame = tk.LabelFrame(self.root, text="FAISS Summaries Index & Search", padx=10, pady=10)
        frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Button(frame, text="Build FAISS Index", bg="#8BC34A", fg="black", command=self._build_faiss_index, width=16).pack(pady=5, anchor=tk.W)

        tk.Label(frame, text="Search Summaries:").pack(anchor=tk.W)
        search_frame = tk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=5)

        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(search_frame, text="Search", command=self._search_faiss_index).pack(side=tk.LEFT)

    def _create_rawlog_panel(self):
        frame = tk.LabelFrame(self.root, text="FAISS Raw Log Search", padx=10, pady=10)
        frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(frame, text="Build Raw Log Index", bg="#CDDC39", fg="black", command=self._build_raw_index, width=20).pack(pady=5, anchor=tk.W)

        tk.Label(frame, text="Search Logs:").pack(anchor=tk.W)
        search_frame = tk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=5)

        self.raw_search_entry = tk.Entry(search_frame, width=40)
        self.raw_search_entry.pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(search_frame, text="Search Logs", command=self._search_raw_index).pack(side=tk.LEFT)

    def _build_faiss_index(self):
        if not os.path.isdir("vector_store"):
            os.makedirs("vector_store")

        self.log_message("🔨 Building FAISS index from correction_summaries.json...")
        texts, meta = self.indexer.load_entries()
        success = self.indexer.build_index(texts, meta)
        if success:
            self.log_message("✅ FAISS index built successfully.")
            self.status_var.set("FAISS index built.")
            messagebox.showinfo("Index Built", "FAISS index has been built and saved.")
        else:
            self.log_message("❌ Failed to build FAISS index.")
            self.status_var.set("Failed to build index.")
            messagebox.showwarning("Index Error", "Unable to build FAISS index.")

    def _search_faiss_index(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search term.")
            return

        try:
            self.indexer.load_index()
        except Exception as e:
            self.log_message(f"[Error] Could not load FAISS index: {e}")
            messagebox.showerror("Load Error", "Could not load FAISS index. Try rebuilding it.")
            return

        results = self.indexer.search(query, top_k=5)
        if results:
            formatted = gui_helpers.format_summary_results(results)
            messagebox.showinfo("Search Results", formatted)
            self.log_message(f"🔎 Searched: '{query}' → Found {len(results)} results")
        else:
            messagebox.showinfo("No Matches", "No summaries matched your query.")
            self.log_message(f"No matches for '{query}' in FAISS index.")

    def _build_raw_index(self):
        self.log_message("🛠 Building FAISS index from raw logs...")
        texts, meta = self.raw_indexer.load_entries()
        success = self.raw_indexer.build_index(texts, meta)
        if success:
            self.log_message("✅ Raw log FAISS index built successfully.")
            self.status_var.set("Raw log index built.")
            messagebox.showinfo("Raw Log Index Built", "FAISS index from raw logs has been built.")
        else:
            self.log_message("❌ Failed to build FAISS index.")
            self.status_var.set("Raw log index failed.")
            messagebox.showwarning("Index Error", "Unable to build FAISS index from raw logs.")

    def _search_raw_index(self):
        query = self.raw_search_entry.get().strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search term.")
            return

        try:
            self.raw_indexer.load_index()
        except Exception as e:
            self.log_message(f"[Error] Could not load raw log FAISS index: {e}")
            messagebox.showerror("Load Error", "Could not load raw log FAISS index. Try rebuilding it.")
            return

        results = self.raw_indexer.search(query, top_k=5)
        if results:
            formatted = gui_helpers.format_raw_results(results)
            messagebox.showinfo("Raw Search Results", formatted)
            self.log_message(f"🔍 Raw log searched: '{query}' → Found {len(results)} results")
        else:
            messagebox.showinfo("No Matches", "No raw log entries matched your query.")
            self.log_message(f"No matches for '{query}' in raw log index.")

    def _save_entry(self):
        entry = self.text_entry.get("1.0", tk.END).strip()
        if not entry:
            messagebox.showwarning("Empty", "Please type something before saving.")
            return

        main_category = self.selected_category_main.get()
        subcategory = self.selected_subcategory.get()

        self.status_var.set(f"Saving entry to {main_category} → {subcategory}...")
        self.root.update()

        success = self.logger_core.save_entry(main_category, subcategory, entry)
        if success:
            self.log_message(f"✅ Idea logged under {main_category} → {subcategory}")
            self.status_var.set("Entry saved successfully!")
            self.text_entry.delete("1.0", tk.END)
        else:
            self.log_message(f"❌ Error logging idea to {main_category} → {subcategory}")
            self.status_var.set("Error saving entry!")
            messagebox.showerror("Error", "Logging failed. Check logs for details.")

    def _manual_summarize(self):
        main_category = self.selected_category_main.get()
        subcategory = self.selected_subcategory.get()

        self.status_var.set(f"Summarizing {main_category} → {subcategory}...")
        self.log_message(f"🔄 Force summarizing {main_category} → {subcategory}...")
        self.root.update()

        try:
            logs = json.loads(self.logger_core.json_log_file.read_text(encoding="utf-8"))
        except Exception as e:
            self.log_message(f"[Error] Failed to read logs: {e}")
            messagebox.showwarning("Missing Log File", "zephyrus_log.json is missing or corrupted.")
            return

        matching_dates = [date_str for date_str in logs if main_category in logs[date_str] and subcategory in logs[date_str][main_category]]
        if not matching_dates:
            self.log_message(f"No entries found for {main_category} → {subcategory}.")
            messagebox.showwarning("No Data Found", f"No logged entries for {main_category} → {subcategory}.")
            return

        latest_date = sorted(matching_dates)[-1]
        self.log_message(f"Found {len(matching_dates)} date(s). Using latest date: {latest_date}")

        success = self.logger_core.generate_summary(latest_date, main_category, subcategory)
        if success:
            self.log_message(f"✅ Summary generated for {main_category} → {subcategory} (date: {latest_date})")
            self.status_var.set("Summary generated successfully!")
            messagebox.showinfo("✅ AI Summary", f"Summary generated for {main_category} → {subcategory} on {latest_date}")
        else:
            self.log_message(f"⚠️ Failed to summarize {main_category} → {subcategory} on {latest_date}")
            self.status_var.set("Summary generation failed!")
            messagebox.showwarning("⚠️ Summarization Failed", f"Could not summarize {main_category} → {subcategory} on {latest_date}. Check logs for details.")

    def run(self):
        config_file = get_absolute_path("config/config.json")
        config = load_config(config_file)
        if config:
            self.config_json_file = open(config_file, "r", encoding="utf-8")
        else:
            self.config_json_file = None
        self.root.mainloop()
