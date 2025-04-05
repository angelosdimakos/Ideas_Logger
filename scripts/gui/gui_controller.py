# scripts/gui/gui_controller.py

import os
from scripts.core.core import ZephyrusLoggerCore

class GUIController:
    def __init__(self, logger_core=None, script_dir=None):
        """
        If no logger_core is provided, create one using ZephyrusLoggerCore.
        :param logger_core: An instance of ZephyrusLoggerCore, or None.
        :param script_dir: Directory to use for initializing the core if logger_core is None.
        """
        if logger_core is None:
            # Use provided script_dir or default to current working directory
            if script_dir is None:
                script_dir = os.getcwd()
            logger_core = ZephyrusLoggerCore(script_dir)
        self.core = logger_core

    def log_entry(self, main, sub, text):
        try:
            return self.core.log_new_entry(main, sub, text)
        except Exception as e:
            # Optionally log or handle the error here
            raise e

    def force_summarize_all(self):
        try:
            return self.core.force_summary_all()
        except Exception as e:
            raise e

    def search_summaries(self, query):
        try:
            return self.core.search_summaries(query)
        except Exception as e:
            raise e

    def search_raw_logs(self, query):
        try:
            return self.core.search_raw_logs(query)
        except Exception as e:
            raise e
