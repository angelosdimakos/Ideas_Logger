"""
Tkinter Environment Management Fixtures

This module provides fixtures for managing Tkinter in headless environments
and patching Tkinter components during testing.
"""
import sys
import os
import pytest
import tkinter as _tk
from unittest.mock import MagicMock
from contextlib import contextmanager


# ── 1. force_headless_tk  ─────────────────────────────────────
def _force_headless_tk() -> bool:
    """
    Ensure Tk works in headless CI.
    • If $DISPLAY exists → no-op.
    • If not, try xvfb :0; if that fails, monkey-patch tk.Tk with MagicMock.
    Returns True if *real* GUI is available, False if mocked.
    """
    if sys.platform.startswith("linux") and "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"  # let xvfb-run claim :0
    try:
        _tk.Tk().destroy()
        return True  # real GUI
    except Exception:
        _tk.Tk = MagicMock()
        return False  # GUI mocked


GUI_AVAILABLE = _force_headless_tk()


# ── 2. Context helper for ad-hoc tests (optional use) ─────────
@contextmanager
def tk_safe():
    """
    Yields (root, gui_ok):
        root   -> a Tk() instance (real or mocked)
        gui_ok -> bool flag (True if real GUI)
    """
    root = _tk.Tk()
    try:
        yield root, GUI_AVAILABLE
    finally:
        try:
            root.destroy()
        except Exception:
            pass


# ── 3. Auto-fixture: flush Tk event-loop between tests ────────
@pytest.fixture(autouse=True)
def flush_tk_events():
    yield
    try:
        if _tk._default_root:
            _tk._default_root.update_idletasks()
    except Exception:
        pass


# ── 4. Auto-fixture: stub blocking dialogs / file pickers ─────
@pytest.fixture(autouse=True)
def patch_blocking_dialogs(monkeypatch):
    import tkinter.messagebox as mb
    import tkinter.filedialog as fd

    monkeypatch.setattr(mb, "showwarning", lambda *a, **k: None)
    monkeypatch.setattr(fd, "askopenfilename", lambda *a, **k: "/tmp/dummy.txt")
    yield