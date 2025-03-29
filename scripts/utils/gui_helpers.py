import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from scripts.utils.file_utils import read_json, write_json
from tkinter import scrolledtext


def validate_log_input(content):
    if not content.strip():
        messagebox.showwarning("Input Error", "Log entry cannot be empty.")
        return False
    return True

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def clear_text_input(entry_widget):
    entry_widget.delete("1.0", tk.END)

def update_status_label(label, message, color="blue"):
    label.config(text=message, fg=color)

def get_selected_option(menu_var, default="General"):
    return menu_var.get() or default

def append_log_entry(log_file, date, category, subcategory, entry_text):
    data = read_json(log_file)
    if date not in data:
        data[date] = {}
    if category not in data[date]:
        data[date][category] = {}
    if subcategory not in data[date][category]:
        data[date][category][subcategory] = []

    data[date][category][subcategory].append({
        "timestamp": get_current_timestamp(),
        "content": entry_text
    })
    write_json(log_file, data)

def get_category_options(categories_json_path):
    try:
        categories_data = read_json(categories_json_path)
        return list(categories_data.get("categories", {}).keys())
    except Exception:
        return []
    
def create_status_label(root, status_var):
    label = tk.Label(root, textvariable=status_var, fg="green")
    label.pack(pady=2)
    return label

def create_log_frame(root):
    log_frame = tk.Frame(root)
    log_frame.pack(padx=10, pady=5, fill=tk.X)
    log_text = scrolledtext.ScrolledText(log_frame, height=4, width=70, wrap=tk.WORD)
    log_text.pack(fill=tk.X, expand=True)
    log_text.config(state=tk.DISABLED)
    return log_text, log_frame

def log_message(log_text_widget, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_text_widget.config(state=tk.NORMAL)
    log_text_widget.insert(tk.END, f"[{timestamp}] {message}\n")
    log_text_widget.see(tk.END)
    log_text_widget.config(state=tk.DISABLED)

def create_dropdown_menu(frame, label_text, variable, options):
    label = tk.Label(frame, text=label_text)
    label.pack(side=tk.LEFT, padx=(0, 5))
    menu = tk.OptionMenu(frame, variable, *options)
    menu.pack(side=tk.LEFT, padx=(0, 15))
    return menu

def create_button(frame, text, command, width=15, height=2, bg="#4CAF50", fg="white"):
    return tk.Button(frame, text=text, command=command, width=width, height=height, bg=bg, fg=fg)

def show_messagebox(icon, title, message):
    if icon == "info":
        messagebox.showinfo(title, message)
    elif icon == "warning":
        messagebox.showwarning(title, message)
    elif icon == "error":
        messagebox.showerror(title, message)
        

def create_text_entry(root, height=8, width=70):
    """
    Creates a text entry widget for user input.
    
    Args:
        root (tk.Tk or tk.Frame): The parent widget.
        height (int): Number of lines tall.
        width (int): Number of characters wide.
    
    Returns:
        tk.Text: A configured Text widget.
    """
    text_entry = tk.Text(root, height=height, width=width)
    text_entry.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    return text_entry