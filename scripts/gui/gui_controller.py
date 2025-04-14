import os
import logging
from scripts.core.core import ZephyrusLoggerCore

logger = logging.getLogger(__name__)


class GUIController:
    def __init__(self, logger_core=None, script_dir=None):
        try:
            if logger_core is None:
                script_dir = script_dir or os.getcwd()
                self.core = ZephyrusLoggerCore(script_dir)
            else:
                self.core = logger_core
        except Exception as e:
            logger.error("Failed to initialize ZephyrusLoggerCore: %s", e, exc_info=True)
            raise

    def log_entry(self, main, sub, text):
        try:
            return self.core.log_new_entry(main, sub, text)
        except Exception as e:
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

    def rebuild_tracker(self):
        """
        Rebuilds the summary tracker and returns True if successful, False otherwise.
        """
        logger.info("[GUI] Manually rebuilding summary tracker.")
        self.core.summary_tracker.rebuild()
        return self.core.summary_tracker.validate()

    def get_tracker_status(self):
        """
        Returns a user-friendly status string of the summary tracker.
        """
        is_valid = self.core.summary_tracker.validate()
        return "✅ Valid" if is_valid else "❌ Invalid"

    def get_coverage_data(self):
        """
        Retrieves coverage data from the tracker for the UI heatmap.
        """
        return self.core.summary_tracker.get_coverage_data()

    def get_logs(self):
        """
        Retrieves the contents of the plain text log file as a string.
        """
        try:
            txt_log_file = self.core.paths.txt_log_file
            with open(txt_log_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading log file: {e}"
