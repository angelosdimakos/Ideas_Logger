from core import ZephyrusLoggerCore
from gui import ZephyrusLoggerGUI
from config_loader import load_config
from ai_summarizer import AISummarizer

if __name__ == "__main__":
    config = load_config()
    logger_core = ZephyrusLoggerCore(script_dir=".")
    app = ZephyrusLoggerGUI(logger_core)
    app.run()
