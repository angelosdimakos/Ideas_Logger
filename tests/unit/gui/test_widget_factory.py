import pytest
from scripts.gui.widget_factory import WidgetFactory
from tests.fixtures.tkinter_fixtures import tk_safe
import tkinter.ttk as ttk

def test_create_button():
    with tk_safe() as (root, _):
        btn = WidgetFactory.create_button(root, text="Click", command=lambda: None, style="TButton")
        assert isinstance(btn, ttk.Button)
        assert btn["text"] == "Click"
        assert btn["style"] == "TButton"

def test_create_label():
    with tk_safe() as (root, _):
        label = WidgetFactory.create_label(root, text="Hello", style="TLabel")
        assert isinstance(label, ttk.Label)
        assert label["text"] == "Hello"
        assert label["style"] == "TLabel"

def test_create_entry():
    with tk_safe() as (root, _):
        entry = WidgetFactory.create_entry(root)
        assert isinstance(entry, ttk.Entry)

def test_create_frame():
    with tk_safe() as (root, _):
        frame = WidgetFactory.create_frame(root, style="TFrame")
        assert isinstance(frame, ttk.Frame)
        assert frame["style"] == "TFrame"

def test_create_notebook():
    with tk_safe() as (root, _):
        nb = WidgetFactory.create_notebook(root)
        assert isinstance(nb, ttk.Notebook)
