import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
import json
import os

# Import your existing indexer
from summary_indexer import SummaryIndexer

class ZephyrusLoggerGUI:
    CATEGORIES = {
        "Narrative": ["Narrative Concept", "Emotional Impact", "Romantic Development"],
        "World": ["Worldbuilding Detail", "Faction Dynamics", "Loop Mechanics"],
        "AI / Meta": ["AI System Design", "Tooling & Automation", "Execution Strategy", "Meta Reflection"],
        "Creative": ["Visual or Audio Prompt", "Gameplay Design Insight", "Creative Ops / Org Flow"]
    }

    def __init__(self, logger_core):
        self.logger_core = logger_core
        self.root = tk.Tk()
        self.root.title("Zephyrus Idea Logger (with FAISS Search)")
        self.root.geometry("700x600")
        self.root.attributes("-topmost", True)

        # Status line
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, fg="green")
        self.status_label.pack(pady=2)

        # Scrollable log area
        self.log_frame = tk.Frame(self.root)
        self.log_frame.pack(padx=10, pady=5, fill=tk.X)
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=4, width=70, wrap=tk.WORD)
        self.log_text.pack(fill=tk.X, expand=True)
        self.log_text.config(state=tk.DISABLED)

        # Main text entry
        self.text_entry = tk.Text(self.root, height=8, width=70)
        self.text_entry.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Category selection
        self.selected_category_main = tk.StringVar()
        self.selected_subcategory = tk.StringVar()
        self._create_category_selector()
        self._create_main_buttons()

        # FAISS indexer config
        self.indexer = SummaryIndexer(
            summaries_path="logs/correction_summaries.json",
            index_path="vector_store/summary_index.faiss",
            metadata_path="vector_store/summary_metadata.pkl"
        )

        self._create_faiss_panel()

        self.text_entry.bind("<Control-Return>", lambda event: self._save_entry())

        self.log_message("Zephyrus Idea Logger initialized. Ready for entries.")

    def log_message(self, message):
        """Add a message to the log text area with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _create_category_selector(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=5)

        main_label = tk.Label(frame, text="Category:")
        main_label.pack(side=tk.LEFT, padx=(0, 5))

        main_menu = tk.OptionMenu(
            frame, self.selected_category_main,
            *self.CATEGORIES.keys(),
            command=self._update_subcategories
        )
        main_menu.pack(side=tk.LEFT, padx=(0, 15))

        self.selected_category_main.set(next(iter(self.CATEGORIES)))

        sub_label = tk.Label(frame, text="Subcategory:")
        sub_label.pack(side=tk.LEFT, padx=(0, 5))

        self.sub_menu = tk.OptionMenu(frame, self.selected_subcategory, "")
        self.sub_menu.pack(side=tk.LEFT)

        self._update_subcategories(self.selected_category_main.get())

    def _update_subcategories(self, main_category):
        subcats = self.CATEGORIES[main_category]
        self.selected_subcategory.set(subcats[0])
        menu = self.sub_menu["menu"]
        menu.delete(0, "end")
        for subcat in subcats:
            menu.add_command(
                label=subcat,
                command=lambda sc=subcat: self.selected_subcategory.set(sc)
            )

    def _create_main_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        save_btn = tk.Button(button_frame, text="Log Idea",
                             command=self._save_entry,
                             width=15, height=2, bg="#4CAF50", fg="white")
        save_btn.pack(side=tk.LEFT, padx=10)

        summarize_btn = tk.Button(button_frame, text="Force Summarize",
                                  command=self._manual_summarize,
                                  width=15, height=2, bg="#2196F3", fg="white")
        summarize_btn.pack(side=tk.LEFT, padx=10)

    def _create_faiss_panel(self):
        """Create a panel for building the FAISS index + searching it."""
        faiss_frame = tk.LabelFrame(self.root, text="FAISS Summaries Index & Search", padx=10, pady=10)
        faiss_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Build index button
        build_button = tk.Button(faiss_frame, text="Build FAISS Index", bg="#8BC34A", fg="black",
                                 command=self._build_faiss_index, width=16)
        build_button.pack(pady=5, anchor=tk.W)

        # Search area
        search_label = tk.Label(faiss_frame, text="Search Summaries:")
        search_label.pack(anchor=tk.W)

        search_box_frame = tk.Frame(faiss_frame)
        search_box_frame.pack(fill=tk.X, pady=5)

        self.search_entry = tk.Entry(search_box_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))

        search_button = tk.Button(search_box_frame, text="Search", command=self._search_faiss_index)
        search_button.pack(side=tk.LEFT)

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

        # 1) Load logs
        try:
            logs = json.loads(self.logger_core.json_log_file.read_text(encoding="utf-8"))
        except Exception as e:
            self.log_message(f"[Error] Failed to read logs: {e}")
            messagebox.showwarning("Missing Log File", "zephyrus_log.json is missing or corrupted.")
            return

        # 2) Find all dates that have (main_category → subcategory)
        matching_dates = []
        for date_str, cat_data in logs.items():
            if main_category in cat_data and subcategory in cat_data[main_category]:
                matching_dates.append(date_str)

        if not matching_dates:
            self.log_message(f"No entries found for {main_category} → {subcategory}.")
            messagebox.showwarning("No Data Found", f"No logged entries for {main_category} → {subcategory}.")
            return
    
        # 3) Pick the LATEST date that contains entries for this cat/subcat
        matching_dates.sort()
        latest_date = matching_dates[-1]

        self.log_message(f"Found {len(matching_dates)} date(s). Using latest date: {latest_date}")
    
        # 4) Generate summary for that date
        success = self.logger_core.generate_summary(latest_date, main_category, subcategory)
    
        if success:
            self.log_message(f"✅ Summary generated for {main_category} → {subcategory} (date: {latest_date})")
            self.status_var.set("Summary generated successfully!")
            messagebox.showinfo("✅ AI Summary", f"Summary generated for {main_category} → {subcategory} on {latest_date}")
        else:
            self.log_message(f"⚠️ Failed to summarize {main_category} → {subcategory} on {latest_date}")
            self.status_var.set("Summary generation failed!")
            messagebox.showwarning("⚠️ Summarization Failed", f"Could not summarize {main_category} → {subcategory} on {latest_date}. Check logs for details.")

    def _build_faiss_index(self):
        """Rebuild the FAISS index from correction_summaries.json."""
        # Make sure vector_store/ dir exists
        if not os.path.isdir("vector_store"):
            os.makedirs("vector_store")

        self.log_message("🔨 Building FAISS index from correction_summaries.json...")
        success = self.indexer.build_index()
        if success:
            self.log_message("✅ FAISS index built successfully.")
            self.status_var.set("FAISS index built.")
            messagebox.showinfo("Index Built", "FAISS index has been built and saved.")
        else:
            self.log_message("❌ Failed to build FAISS index.")
            self.status_var.set("Failed to build index.")
            messagebox.showwarning("Index Error", "Unable to build FAISS index.")

    def _search_faiss_index(self):
        """Search the FAISS index for a user query."""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search term.")
            return

        try:
            # Ensure index is loaded
            self.indexer.load_index()
        except Exception as e:
            self.log_message(f"[Error] Could not load FAISS index: {e}")
            messagebox.showerror("Load Error", "Could not load FAISS index. Try rebuilding it.")
            return

        results = self.indexer.search(query, top_k=5)
        if results:
            msg_parts = []
            for r in results:
                scr = r.get("similarity", 0.0)
                msg_parts.append(
                    f"Similarity: {scr:.4f}\n"
                    f"Date: {r['date']}\n"
                    f"{r['main_category']} → {r['subcategory']} (Batch {r['batch']})\n"
                    f"Time: {r['timestamp']}"
                )
            formatted = "\n\n".join(msg_parts)
            messagebox.showinfo("Search Results", formatted)
            self.log_message(f"🔎 Searched: '{query}' → Found {len(results)} results")
        else:
            messagebox.showinfo("No Matches", "No summaries matched your query.")
            self.log_message(f"No matches for '{query}' in FAISS index.")

    def run(self):
        self.root.mainloop()
