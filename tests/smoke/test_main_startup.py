import pytest
import logging
from unittest.mock import patch
from scripts.main import bootstrap

from scripts.config.config_loader import load_config
from scripts.core.core import ZephyrusLoggerCore
from scripts.gui.gui_controller import GUIController


def test_main_smoke_startup():
    """🚀 Smoke test: Ensure main startup logic boots core systems without launching full GUI."""
    with patch("scripts.gui.gui.ZephyrusLoggerGUI") as MockGUI:
        try:
            logging.basicConfig(level=logging.INFO)
            config = load_config()
            assert isinstance(config, dict)

            core = ZephyrusLoggerCore(script_dir=".")
            controller = GUIController(logger_core=core)

            assert controller.core.summary_tracker.validate() is not None
            app = MockGUI(controller)
            assert app is not None

        except Exception as e:
            pytest.fail(f"Smoke test failed during bootstrap init: {e}")


def test_main_bootstrap_without_gui(monkeypatch):
    """🧪 Test main.bootstrap when GUI is disabled."""
    monkeypatch.setattr("scripts.config.config_loader.setup_logging", lambda: None)

    controller = bootstrap(start_gui=False)

    assert isinstance(controller, GUIController)
    assert hasattr(controller, "log_entry")  # pick any actual method that matters

