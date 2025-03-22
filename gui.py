import tkinter as tk
from tkinter import messagebox
from datetime import datetime  # Required for timestamp display

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
        self.root.title("Zephyrus Idea Logger")
        self.root.geometry("500x400")
        self.root.attributes("-topmost", True)

        self.text_entry = tk.Text(self.root, height=8, width=60)
        self.text_entry.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.selected_category_main = tk.StringVar()
        self.selected_subcategory = tk.StringVar()

        self._create_category_selector()
        self._create_buttons()

        self.text_entry.bind("<Control-Return>", lambda event: self._save_entry())

    def _create_category_selector(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=5)

        main_menu = tk.OptionMenu(
            frame, self.selected_category_main,
            *self.CATEGORIES.keys(),
            command=self._update_subcategories
        )
        main_menu.pack(side=tk.LEFT)

        self.selected_category_main.set(next(iter(self.CATEGORIES)))

        self.sub_menu = tk.OptionMenu(frame, self.selected_subcategory, "")
        self.sub_menu.pack(side=tk.LEFT, padx=5)

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

    def _create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        save_btn = tk.Button(button_frame, text="Log Idea", command=self._save_entry)
        save_btn.pack()

    def _save_entry(self):
        entry = self.text_entry.get("1.0", tk.END).strip()
        if not entry:
            messagebox.showwarning("Empty", "Please type something before saving.")
            return

        main_category = self.selected_category_main.get()
        subcategory = self.selected_subcategory.get()

        success = self.logger_core.save_entry(main_category, subcategory, entry)

        if success:
            messagebox.showinfo("Success", f"Idea logged under {main_category} → {subcategory}")
            self.text_entry.delete("1.0", tk.END)
        else:
            messagebox.showerror("Error", "Logging failed. Check logs for details.")

    def run(self):
        self.root.mainloop()
