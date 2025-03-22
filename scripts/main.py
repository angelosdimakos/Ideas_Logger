from core import ZephyrusLoggerCore
from gui import ZephyrusLoggerGUI
from config_loader import load_config
from ai_summarizer import AISummarizer
from config_loader import load_config

if __name__ == "__main__":
    config = load_config()
    IS_TEST_MODE = config.get("test_mode", False)
    print(f"[INFO] Running in {'TEST' if IS_TEST_MODE else 'PRODUCTION'} mode.")
    logger_core = ZephyrusLoggerCore(script_dir=".")
    app = ZephyrusLoggerGUI(logger_core)
    app.run()
