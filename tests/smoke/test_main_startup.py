import pytest
from unittest.mock import MagicMock
from scripts.main import bootstrap
from scripts.gui.gui import ZephyrusLoggerGUI
from scripts.gui.gui_controller import GUIController
from scripts.core.core import ZephyrusLoggerCore

def test_bootstrap_runs_gui(monkeypatch):
    import tkinter as tk
    try:
        # Create root to avoid "Too early to use font"
        root = tk.Tk()
        root.withdraw()
        root.update_idletasks()
        root.destroy()
    except (tk.TclError, RuntimeError):
        pytest.skip("🛑 Skipping GUI test — no GUI support available")

    # 🔁 Create dummy root so ZephyrusLoggerGUI doesn’t crash
    root = tk.Tk()
    root.withdraw()

    # 👇 Mock `run()` so we don't launch the GUI loop
    mocked_run = MagicMock()
    monkeypatch.setattr("scripts.gui.gui.ZephyrusLoggerGUI.run", mocked_run)

    controller, gui = bootstrap(start_gui=True)
    assert isinstance(controller, GUIController)
    assert isinstance(gui, ZephyrusLoggerGUI)
    mocked_run.assert_called_once()

    root.destroy()  # ✅ Clean up manually



def test_main_smoke_startup():
    controller, gui = bootstrap(start_gui=False)
    assert isinstance(controller, GUIController)
    assert gui is None

def test_bootstrap_returns_controller():
    controller, gui = bootstrap(start_gui=False)
    assert hasattr(controller, "get_coverage_data")
    assert gui is None

def test_bootstrap_invalid_summary_tracker(monkeypatch, temp_dir):
    def explode_loader(self):
        raise ValueError("🔥 Tracker load failed hard")

    monkeypatch.setattr(
        "scripts.core.summary_tracker.SummaryTracker._safe_load_tracker",
        explode_loader
    )

    with pytest.raises(ValueError, match="🔥 Tracker load failed hard"):
        ZephyrusLoggerCore(script_dir=temp_dir)

def test_bootstrap_test_and_prod_modes():
    controller, gui = bootstrap(start_gui=False)
    assert controller.core.config.get("test_mode") is True

def test_bootstrap_return_types():
    controller, gui = bootstrap(start_gui=False)
    assert controller.__class__.__name__.endswith("Controller")
    assert gui is None
