import pytest
from scripts.gui.style_manager import StyleManager
from tests.fixtures.tkinter_fixtures import tk_safe  # Use shared fixture

def test_initializes_styles():
    with tk_safe() as (root, _):
        manager = StyleManager(root)
        style = manager.style

        # Test default color assignments
        assert manager.primary_color == "#3f51b5"
        assert manager.secondary_color == "#f5f5f5"
        assert manager.accent_color == "#4caf50"
        assert manager.text_color == "#212121"

        # Test ttk style configuration
        assert style.lookup("TFrame", "background") == manager.secondary_color
        assert style.lookup("TLabel", "foreground") == manager.text_color
        assert style.lookup("TButton", "foreground") == "white"

def test_update_style_applies_changes():
    with tk_safe() as (root, _):
        manager = StyleManager(root)
        manager.update_style("TLabel", {"foreground": "red"})
        assert manager.style.lookup("TLabel", "foreground") == "red"
