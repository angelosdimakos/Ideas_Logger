
from scripts.core.core import ZephyrusLoggerCore
from scripts.gui.gui import ZephyrusLoggerGUI,GUILogHandler
from scripts.config.config_loader import load_config, setup_logging
import logging

if __name__ == "__main__":
    """
    Main entry point for the Zephyrus Logger application.

    This script initializes the logging system, loads the configuration,
    and creates the GUI application.

    The application is started in either TEST or PRODUCTION mode,
    depending on the "test_mode" setting in the configuration file.
    """
    # Set up centralized logging for the application.
    setup_logging()
    
    config = load_config()
    IS_TEST_MODE = config.get("test_mode", False)
    logger = logging.getLogger(__name__)
    logger.info("Running in %s mode.", "TEST" if IS_TEST_MODE else "PRODUCTION")
    
    # Initialize the core logger component.
    logger_core = ZephyrusLoggerCore(script_dir=".")
    
    # Create the GUI application.
    app = ZephyrusLoggerGUI(logger_core)
    
    # After the GUI (and its log_text widget) has been created,
    # add the GUI logging handler so that log messages also appear in the GUI.
    root_logger = logging.getLogger()
    gui_handler = GUILogHandler(app.log_text)
    gui_handler.setLevel(logging.ERROR)  # Change to a lower level (e.g., INFO) if you want more messages.
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    gui_handler.setFormatter(formatter)
    root_logger.addHandler(gui_handler)
    
    # Run the GUI event loop.
    app.run()
