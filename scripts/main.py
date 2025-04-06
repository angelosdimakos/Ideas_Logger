import logging
from scripts.config.config_loader import load_config, setup_logging
from scripts.core.core import ZephyrusLoggerCore
from scripts.gui.gui import ZephyrusLoggerGUI
from scripts.gui.gui_controller import GUIController
from scripts.gui.gui_logging import GUILogHandler

if __name__ == "__main__":
    # 1. Setup logging
    setup_logging()

    # 2. Load config and print mode
    config = load_config()
    IS_TEST_MODE = config.get("test_mode", False)
    logger = logging.getLogger(__name__)
    logger.info("Running in %s mode.", "TEST" if IS_TEST_MODE else "PRODUCTION")

    try:
        # 3. Initialize core and GUI controller
        logger_core = ZephyrusLoggerCore(script_dir=".")
        controller = GUIController(logger_core=logger_core)

        # NEW: Explicit log validation feedback after core is ready
        if controller.core.summary_tracker.validate():
            logger.info("[INIT] Summary tracker validated successfully.")
        else:
            logger.warning("[INIT] Summary tracker may have inconsistencies. Review logs.")

        # 4. Start the GUI
        app = ZephyrusLoggerGUI(controller)

        logger.info("[GUI] ZephyrusLoggerGUI launched. Awaiting user interaction.")

        # 6. Run the GUI event loop
        app.run()

    except Exception as e:
        logger.critical("Fatal error during startup: %s", e, exc_info=True)
