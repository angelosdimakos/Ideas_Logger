import tkinter as tk
from tkinter import ttk

from scripts.gui.style_manager import StyleManager
from scripts.gui.gui_controller import GUIController  # Import your controller
from scripts.gui.tabs.main_tab import MainTab  # Concrete implementation of MainTab


class ZephyrusLoggerApp:
    """
    Core Application Class that initializes the main window,
    sets up the style manager, creates the main notebook, and
    integrates the concrete tabs.
    """

    def __init__(self, controller):
        self.controller = controller

        # Set up the root window
        self.root = tk.Tk()
        self.root.title("Zephyrus Logger")
        self.root.geometry("1200x900")

        # Initialize the style manager to apply application-wide styles
        self.style_manager = StyleManager(self.root)

        # Create the main notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create the MainTab as an instance of the concrete MainTab class
        self.main_tab = MainTab(self.notebook, controller=self.controller)
        self.notebook.add(self.main_tab, text="Logger")

        # For now, create placeholder tabs for Search and Analytics
        self.search_tab = ttk.Frame(self.notebook)
        self.analytics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="Search")
        self.notebook.add(self.analytics_tab, text="Analytics")

        self._create_status_bar()

    def _create_status_bar(self):
        """Creates a basic status bar at the bottom of the main window."""
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_message = tk.StringVar()
        self.status_message.set("Application started...")
        status_label = ttk.Label(status_bar, textvariable=self.status_message, padding=(5, 2))
        status_label.pack(side=tk.LEFT)

    def run(self):
        """Starts the main event loop."""
        self.root.mainloop()


# For testing purposes, instantiate and run the app:
if __name__ == "__main__":
    controller = GUIController()  # Create your controller instance
    app = ZephyrusLoggerApp(controller=controller)
    app.run()
