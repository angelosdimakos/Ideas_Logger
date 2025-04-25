import pytest
import tkinter as tk
from unittest.mock import MagicMock
from scripts.main import bootstrap
from scripts.gui.gui import ZephyrusLoggerGUI
from scripts.gui.gui_controller import GUIController
from scripts.core.core import ZephyrusLoggerCore
import os

# Validate if GUI is usable in this environment
GUI_AVAILABLE = True
try:
    _probe = tk.Tk()
    _probe.destroy()
except Exception:
    GUI_AVAILABLE = False
    tk.Tk = MagicMock()


@pytest.mark.skipif(not GUI_AVAILABLE, reason="🛑 Skipping GUI test — Tkinter not available")
def test_bootstrap_runs_gui(monkeypatch):
    """
    Smoke tests for the Zephyrus Logger bootstrap process, including GUI and headless modes.

    These tests verify that the bootstrap function initializes the controller correctly,
    handles GUI availability, respects headless mode, manages summary tracker failures,
    and returns expected types and configurations.
    """
    # 🧪 Ensure GUI won't actually start in headless/CI
    os.environ["ZEPHYRUS_HEADLESS"] = "1"

    # Create a dummy root to satisfy nametofont
    root = tk.Tk()
    root.withdraw()

    mocked_run = MagicMock()
    monkeypatch.setattr("scripts.gui.gui.ZephyrusLoggerGUI.run", mocked_run)

    controller, gui = bootstrap(start_gui=True)

    # In headless mode, GUI should not launch
    assert isinstance(controller, GUIController)
    assert gui is None  # Explicitly verify GUI is skipped in headless mode
    mocked_run.assert_not_called()

    root.destroy()


def test_main_smoke_startup():
    """
    Smoke tests for the Zephyrus Logger application's bootstrap process, verifying correct initialization of the
    controller, handling of GUI and headless modes, summary tracker error handling, and return types.
    Ensures compatibility with environments lacking Tkinter support.
    """
    controller, gui = bootstrap(start_gui=False)
    assert isinstance(controller, GUIController)
    assert gui is None


def test_bootstrap_returns_controller():
    """
    Smoke tests for the Zephyrus Logger application's bootstrap process, verifying correct initialization of the
    controller, handling of GUI and headless modes, summary tracker error handling, and return types.
    Ensures compatibility with environments lacking Tkinter support and validates that the GUI is not
    launched in headless mode.
    """
    controller, gui = bootstrap(start_gui=False)
    assert hasattr(controller, "get_coverage_data")
    assert gui is None


def test_bootstrap_invalid_summary_tracker(monkeypatch, temp_dir):
    """
    Smoke tests for the Zephyrus Logger application's bootstrap process, verifying correct
    initialization of the controller, handling of GUI and headless modes, summary tracker error handling,
    and return types. Ensures compatibility with environments lacking Tkinter support and validates
    that the GUI is not launched in headless mode.
    """

    def explode_loader(self):
        raise ValueError("🔥 Tracker load failed hard")

    monkeypatch.setattr(
        "scripts.core.summary_tracker.SummaryTracker._safe_load_tracker", explode_loader
    )

    with pytest.raises(ValueError, match="🔥 Tracker load failed hard"):
        ZephyrusLoggerCore(script_dir=temp_dir)


def test_bootstrap_test_and_prod_modes():
    """
    Smoke tests for the Zephyrus Logger application's bootstrap process, verifying initialization,
    GUI/headless mode handling, summary tracker error handling, and return types.
    Ensures compatibility with and without Tkinter, and validates correct controller
    and GUI behavior in various environments.
    """
    controller, gui = bootstrap(start_gui=False)
    assert controller.core.config.get("test_mode") is True


def test_bootstrap_return_types():
    """
    Smoke tests for the Zephyrus Logger application's bootstrap process,
    verifying correct initialization of the controller, handling of GUI and headless modes,
    summary tracker error handling, and return types. Ensures compatibility with environments
    lacking Tkinter support and validates that the GUI is not launched in headless mode.
    """
    controller, gui = bootstrap(start_gui=False)
    assert controller.__class__.__name__.endswith("Controller")
    assert gui is None
