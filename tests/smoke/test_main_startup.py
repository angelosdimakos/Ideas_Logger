import pytest
import logging
from unittest.mock import patch

from scripts.config.config_loader import load_config
from scripts.core.core import ZephyrusLoggerCore
from scripts.gui.gui_controller import GUIController


def test_main_smoke_startup():
    """🚀 Smoke test: Ensure main startup logic boots core systems without launching full GUI."""
    # Mock the GUI class and run method to avoid launching a window
    with patch("scripts.gui.gui.ZephyrusLoggerGUI") as MockGUI:
        try:
            # 1. Logging and config
            logging.basicConfig(level=logging.INFO)
            config = load_config()
            assert isinstance(config, dict), "Config should be a dictionary"

            # 2. Core systems
            core = ZephyrusLoggerCore(script_dir=".")
            controller = GUIController(logger_core=core)

            # 3. Tracker check
            assert controller.core.summary_tracker.validate() is not None, "Tracker validation failed."

            # 4. GUI placeholder should still be initialized
            app = MockGUI(controller)
            assert app is not None, "GUI mock not initialized."

        except Exception as e:
            pytest.fail(f"Smoke test failed during main-like init: {e}")
