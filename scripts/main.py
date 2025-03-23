
from scripts.core import ZephyrusLoggerCore
from scripts.gui import ZephyrusLoggerGUI
from scripts.config_loader import load_config
from scripts.ai_summarizer import AISummarizer
from scripts.config_loader import load_config

if __name__ == "__main__":
    config = load_config()
    IS_TEST_MODE = config.get("test_mode", False)
    print(f"[INFO] Running in {'TEST' if IS_TEST_MODE else 'PRODUCTION'} mode.")
    logger_core = ZephyrusLoggerCore(script_dir=".")
    app = ZephyrusLoggerGUI(logger_core)
    app.run()
