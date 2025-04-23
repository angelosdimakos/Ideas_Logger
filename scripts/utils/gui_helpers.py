"""
gui_helpers.py

This module provides utility functions for building and customizing the
Zephyrus Logger application's graphical user interface (GUI).

Core features include:
- Validating user input for logging and searching.
- Creating and customizing Tkinter widgets (e.g. scrolled text, buttons).
- Displaying alerts and messages using Tkinter's messagebox module.
- Utility functions for reading and writing JSON files.

Intended to provide a set of reusable functions for the GUI components of
the Zephyrus Logger application.
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from scripts.utils.file_utils import read_json, write_json
from tkinter import scrolledtext


def validate_log_input(content: str) -> bool:
    """
    Validates the log input content.

    Displays a warning message if the input is empty or only whitespace.
    Returns True if the input is valid, otherwise False.
    """
    if not content.strip():
        messagebox.showwarning("Input Error", "Log entry cannot be empty.")
        return False
    return True


def get_current_date():
    """
    Returns the current date as a string in 'YYYY-MM-DD' format.

    :return: Current date as a string.
    :rtype: str
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_current_timestamp():
    """
    Returns the current date and time as a formatted string (YYYY-MM-DD HH:MM:SS).
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def clear_text_input(entry_widget):
    """
    Clears all text from the given Tkinter text entry widget.

    Args:
        entry_widget: The Tkinter text widget to be cleared.
    """
    entry_widget.delete("1.0", tk.END)


def update_status_label(label, message, color="blue"):
    """
    Update the text and foreground color of a Tkinter label widget.

    Args:
        label (tk.Label): The label widget to update.
        message (str): The text to display on the label.
        color (str, optional): The text color. Defaults to "blue".
    """
    label.config(text=message, fg=color)


def get_selected_option(menu_var, default="General"):
    """
    Returns the currently selected option from a Tkinter menu variable, or a default value if none is selected.

    Args:
        menu_var: A Tkinter variable associated with a menu widget.
        default (str, optional): The value to return if no option is selected. Defaults to "General".

    Returns:
        str: The selected option or the default value.
    """
    return menu_var.get() or default


def append_log_entry(log_file, date, category, subcategory, entry_text):
    """
    Appends a log entry with a timestamp and content to the specified log file, organizing entries by date, category, and subcategory.

    Args:
        log_file (str): Path to the JSON log file.
        date (str): Date key for the log entry (YYYY-MM-DD).
        category (str): Category under which to store the entry.
        subcategory (str): Subcategory under the category.
        entry_text (str): The content of the log entry.
    """
    data = read_json(log_file)
    if date not in data:
        data[date] = {}
    if category not in data[date]:
        data[date][category] = {}
    if subcategory not in data[date][category]:
        data[date][category][subcategory] = []

    data[date][category][subcategory].append(
        {"timestamp": get_current_timestamp(), "content": entry_text}
    )
    write_json(log_file, data)


def get_category_options(categories_json_path):
    """
    Retrieves a list of category names from a JSON file at the given path.

    Args:
        categories_json_path (str): Path to the JSON file containing categories.

    Returns:
        list: List of category names, or an empty list if reading fails.
    """
    try:
        categories_data = read_json(categories_json_path)
        return list(categories_data.get("categories", {}).keys())
    except Exception:
        return []


def create_status_label(root, status_var):
    """
    Create and pack a status label widget in the given root window.

    Args:
        root: The parent Tkinter widget.
        status_var: A Tkinter StringVar to display as the label's text.

    Returns:
        The created Label widget.
    """
    label = tk.Label(root, textvariable=status_var, fg="green")
    label.pack(pady=2)
    return label


def create_log_frame(root):
    """
    Creates and returns a disabled scrolled text widget within a frame for logging purposes in a Tkinter GUI.

    Args:
        root: The parent Tkinter widget.

    Returns:
        tuple: (log_text, log_frame) where log_text is the ScrolledText widget and log_frame is the containing Frame.
    """
    log_frame = tk.Frame(root)
    log_frame.pack(padx=10, pady=5, fill=tk.X)
    log_text = scrolledtext.ScrolledText(log_frame, height=4, width=70, wrap=tk.WORD)
    log_text.pack(fill=tk.X, expand=True)
    log_text.config(state=tk.DISABLED)
    return log_text, log_frame


def log_message(log_text_widget, message):
    """
    Appends a timestamped message to the provided Tkinter text widget for logging purposes.

    Args:
        log_text_widget (tkinter.Text): The text widget where the log message will be displayed.
        message (str): The message to log.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_text_widget.config(state=tk.NORMAL)
    log_text_widget.insert(tk.END, f"[{timestamp}] {message}\n")
    log_text_widget.see(tk.END)
    log_text_widget.config(state=tk.DISABLED)


def create_dropdown_menu(frame, label_text, variable, options):
    """
    Creates a labeled dropdown menu (OptionMenu) in the given Tkinter frame.

    Args:
        frame: The parent Tkinter frame to place the dropdown menu in.
        label_text: The text to display as the label next to the dropdown.
        variable: A Tkinter variable to store the selected option.
        options: A list of options to display in the dropdown menu.

    Returns:
        The created Tkinter OptionMenu widget.
    """
    label = tk.Label(frame, text=label_text)
    label.pack(side=tk.LEFT, padx=(0, 5))
    menu = tk.OptionMenu(frame, variable, *options)
    menu.pack(side=tk.LEFT, padx=(0, 15))
    return menu


def create_button(frame, text, command, width=15, height=2, bg="#4CAF50", fg="white"):
    """
    Creates and returns a Tkinter Button widget with customizable text, command, size, and colors.

    Args:
        frame: The parent widget where the button will be placed.
        text (str): The label displayed on the button.
        command (callable): The function to be called when the button is clicked.
        width (int, optional): The width of the button. Defaults to 15.
        height (int, optional): The height of the button. Defaults to 2.
        bg (str, optional): The background color of the button. Defaults to "#4CAF50".
        fg (str, optional): The text color of the button. Defaults to "white".

    Returns:
        tk.Button: The configured Button widget.
    """
    return tk.Button(frame, text=text, command=command, width=width, height=height, bg=bg, fg=fg)


def show_messagebox(icon, title, message):
    """
    Displays a message box with the specified icon, title, and message using tkinter.

    Args:
        icon (str): Type of message box to display ('info', 'warning', or 'error').
        title (str): The title of the message box window.
        message (str): The message to display in the message box.
    """
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


def format_summary_results(results):
    """
    Formats a list of result items into a readable summary string.

    Each result can be a dict with 'score' and 'text' keys, a tuple/list with score and text,
    or any other type, which will be converted to string with a default score of 0.0.
    Handles exceptions gracefully and includes error information in the output.

    Args:
        results (list): List of result items to format.

    Returns:
        str: Formatted summary string with scores and texts.
    """
    formatted = []
    for r in results:
        try:
            if isinstance(r, dict):
                score = r.get("score", 0.0)
                text = r.get("text", str(r))
            elif isinstance(r, (list, tuple)) and len(r) >= 2:
                score, text = r[0], r[1]
            else:
                score, text = 0.0, str(r)
            formatted.append(f"Score: {score:.2f}\n{text}")
        except Exception as e:
            formatted.append(f"[ERROR displaying result]: {str(e)}\nRaw: {str(r)}")
    return "\n\n".join(formatted)


def format_raw_results(results):
    """
    Formats a list of raw result items into a readable string.

    Each result is processed based on its type (dict, list/tuple, or other),
    and formatted with a '[RAW LOG MATCH]' prefix. Handles exceptions by
    including error details in the output.

    Args:
        results (list): List of raw result items to format.

    Returns:
        str: Formatted string representation of all results.
    """
    formatted = []
    for r in results:
        try:
            if isinstance(r, dict):
                text = r.get("text", str(r))
            elif isinstance(r, (list, tuple)):
                text = r[0]
            else:
                text = str(r)
            formatted.append(f"[RAW LOG MATCH]\n{text}")
        except Exception as e:
            formatted.append(f"[ERROR displaying result]: {str(e)}\nRaw: {str(r)}")
    return "\n\n".join(formatted)


def display_message(title, message):
    """
    Displays an informational message box.
    """
    messagebox.showinfo(title, message)


def display_error(title, message):
    """
    Displays an error message box.
    """
    messagebox.showerror(title, message)


def format_coverage_data(data: list[dict]) -> str:
    """
    Formats the structured coverage data into a readable string grouped by main category.

    Args:
        data (list[dict]): List of coverage data entries.

    Returns:
        str: A nicely formatted string for displaying coverage stats.
    """
    from collections import defaultdict

    grouped = defaultdict(list)
    for entry in data:
        grouped[entry["main_category"]].append(entry)

    lines = []
    for main_cat, entries in grouped.items():
        lines.append(f"📘 {main_cat}")
        for e in entries:
            summarized = e.get("estimated_summarized_entries", e.get("summarized_total", 0))
            lines.append(
                f"  - {e['subcategory']}: {summarized}/{e['logged_total']} ({e['coverage_percent']}%)"
            )

    return "\n".join(lines)
