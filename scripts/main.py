
from scripts.core import ZephyrusLoggerCore
from scripts.gui import ZephyrusLoggerGUI
from scripts.config_loader import load_config, setup_logging
from scripts.ai_summarizer import AISummarizer
from scripts.gui_logging import GUILogHandler
import logging

if __name__ == "__main__":
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
