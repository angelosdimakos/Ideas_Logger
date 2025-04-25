"""
gui_controller.py

This module provides the GUIController class for managing the interaction between the GUI
and the logging core of the Zephyrus Logger application. It handles the initialization of
the logger core and facilitates logging entries through the GUI.

Dependencies:
- os
- logging
- scripts.core.core.ZephyrusLoggerCore
"""

import os
import logging
from typing import Optional, Any
from scripts.core.core import ZephyrusLoggerCore

logger = logging.getLogger(__name__)


class GUIController:
    """
    GUIController manages the interaction between the GUI and the logging core.

    Attributes:
        core (ZephyrusLoggerCore): The instance of the ZephyrusLoggerCore used for logging.
    """

    def __init__(
        self, logger_core: Optional[ZephyrusLoggerCore] = None, script_dir: Optional[str] = None
    ) -> None:
        """
        Initializes the GUIController with the given logger core or initializes a new one.

        Args:
            logger_core (Optional[ZephyrusLoggerCore]): The logger core instance. If None, a new instance will be created.
            script_dir (Optional[str]): The directory of the script. Defaults to the current working directory.
        """
        try:
            if logger_core is None:
                script_dir = script_dir or os.getcwd()
                self.core = ZephyrusLoggerCore(script_dir)
            else:
                self.core = logger_core
        except Exception as e:
            logger.error("Failed to initialize ZephyrusLoggerCore: %s", e, exc_info=True)
            raise

    def log_entry(self, main: str, sub: str, text: str) -> Any:
        """
        Logs an entry with the specified main category, subcategory, and text.

        Args:
            main (str): The main category of the log entry.
            sub (str): The subcategory of the log entry.
            text (str): The text content of the log entry.

        Returns:
            Any: The result of the logging operation.
        """
        try:
            return self.core.log_new_entry(main, sub, text)
        except Exception as e:
            raise e

    def force_summarize_all(self) -> Any:
        """
        Forces the summarization of all logs.

        Returns:
            Any: The result of the summarization operation.
        """
        try:
            return self.core.force_summary_all()
        except Exception as e:
            raise e

    def search_summaries(self, query: str) -> Any:
        """
        Searches for summaries matching the given query.

        Args:
            query (str): The search query.

        Returns:
            Any: The result of the search operation.
        """
        try:
            return self.core.search_summaries(query)
        except Exception as e:
            raise e

    def search_raw_logs(self, query: str) -> Any:
        """
        Searches for raw logs matching the given query.

        Args:
            query (str): The search query.

        Returns:
            Any: The result of the search operation.
        """
        try:
            return self.core.search_raw_logs(query)
        except Exception as e:
            raise e

    def rebuild_tracker(self) -> bool:
        """
        Rebuilds the summary tracker and returns True if successful, False otherwise.
        """
        logger.info("[GUI] Manually rebuilding summary tracker.")
        self.core.summary_tracker.rebuild()
        return self.core.summary_tracker.validate()

    def get_tracker_status(self) -> str:
        """
        Returns a user-friendly status string of the summary tracker.
        """
        is_valid = self.core.summary_tracker.validate()
        return "✅ Valid" if is_valid else "❌ Invalid"

    def get_coverage_data(self) -> Any:
        """
        Retrieves coverage data from the tracker for the UI heatmap.
        """
        return self.core.summary_tracker.get_coverage_data()

    def get_logs(self) -> str:
        """
        Retrieves the contents of the plain text log file as a string.
        """
        try:
            txt_log_file = self.core.paths.txt_log_file
            with open(txt_log_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading log file: {e}"
