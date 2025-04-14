from tkinter import ttk


class StyleManager:
    """
    Manages application-wide styles for tkinter and ttk.
    This class can be extended to handle dynamic theme changes.
    """

    def __init__(self, root):
        self.root = root
        self.style = ttk.Style(root)
        self.initialize_styles()

    def initialize_styles(self):
        # Define default colors and fonts
        self.primary_color = "#3f51b5"  # Deep blue
        self.secondary_color = "#f5f5f5"  # Light gray
        self.accent_color = "#4caf50"  # Green for success
        self.text_color = "#212121"  # Dark text

        # Configure ttk styles
        self.style.configure("TFrame", background=self.secondary_color)
        self.style.configure("TLabel", background=self.secondary_color, foreground=self.text_color)
        self.style.configure(
            "TButton", background=self.primary_color, foreground="white", padding=6, relief="flat"
        )
        self.style.map("TButton", background=[("active", "#303f9f"), ("disabled", "#bdbdbd")])

    def update_style(self, style_name, options):
        """
        Update a specific style.
        :param style_name: str, e.g. 'TButton'
        :param options: dict of style options (e.g., {'background': 'red'})
        """
        self.style.configure(style_name, **options)
