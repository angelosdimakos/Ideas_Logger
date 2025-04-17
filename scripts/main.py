import os
import logging
from scripts.config.config_loader import load_config, setup_logging
from scripts.core.core import ZephyrusLoggerCore
from scripts.gui.gui import ZephyrusLoggerGUI
from scripts.gui.gui_controller import GUIController
from scripts.gui.gui_logging import GUILogHandler


def bootstrap(start_gui: bool = True) -> tuple[GUIController, ZephyrusLoggerGUI | None]:
    """
    Bootstraps the Zephyrus Logger application.

    Args:
        start_gui (bool, optional): Whether to launch the GUI. Defaults to True.

    Returns:
        Tuple[GUIController, ZephyrusLoggerGUI | None]: The controller and GUI instance (None if headless).

    Raises:
        Exception: Propagates any fatal errors encountered during initialization.
    """
    # 1. Setup logging
    setup_logging()

    # 2. Load config and print mode
    config = load_config()
    IS_TEST_MODE = config.get("test_mode", False)
    HEADLESS_MODE = os.getenv("ZEPHYRUS_HEADLESS", "0") == "1"

    logger = logging.getLogger(__name__)
    logger.info("Running in %s mode.", "TEST" if IS_TEST_MODE else "PRODUCTION")

    try:
        # 3. Initialize core and controller
        logger_core = ZephyrusLoggerCore(script_dir=".")
        controller = GUIController(logger_core=logger_core)

        # 4. Validate summary tracker
        if controller.core.summary_tracker.validate():
            logger.info("[INIT] Summary tracker validated successfully.")
        else:
            logger.warning("[INIT] Summary tracker may have inconsistencies. Review logs.")

        # 5. Optionally start GUI (honors ZEPHYRUS_HEADLESS)
        app = None
        if start_gui and not HEADLESS_MODE:
            try:
                import tkinter as tk
                _root = tk.Tk()
                _root.withdraw()
                app = ZephyrusLoggerGUI(controller)
                logger.info("[GUI] ZephyrusLoggerGUI launched. Awaiting user interaction.")
                app.run()
            except (tk.TclError, RuntimeError) as e:
                logger.warning("⚠️ GUI startup skipped — no display available: %s", e)

        return controller, app

    except Exception as e:
        logger.critical("Fatal error during startup: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    bootstrap()
