"""
core.py

This module provides the core functionality for the Zephyrus Logger application. It includes
the [ZephyrusLoggerCore](cci:2://file:///C:/Users/Angelos%20Dimakos/PycharmProjects/Ideas_Logger/scripts/core/core.py:15:0-382:65) class, which manages logging, summarization, and search capabilities
for categorized entries stored in JSON and Markdown files. The module handles the initialization
of the environment, batch summarization using AI, and maintains tracking of summaries. It also
offers search functionality across both summaries and raw logs, integrating with organization-specific
modules for configuration, file management, and AI summarization.

Key functionalities include:
- Initialization of logging and summarization environments.
- Batch processing of logs for summarization.
- Search capabilities for retrieving categorized entries.
- Integration with configuration and file management utilities.

Dependencies:
- pathlib
- datetime
- logging
- re
- scripts.ai.ai_summarizer
- scripts.config.config_loader
- scripts.utils.file_utils
- scripts.core.summary_tracker
- scripts.core.log_manager
- scripts.paths.ZephyrusPaths
"""

from pathlib import Path
from datetime import datetime
import logging
import re
from typing import Union, List, Dict, Any

from scripts.ai.ai_summarizer import AISummarizer
from scripts.config.config_loader import get_config_value, get_effective_config
from scripts.utils.file_utils import sanitize_filename, write_json, read_json, make_backup
from scripts.core.summary_tracker import SummaryTracker
from scripts.core.log_manager import LogManager
from scripts.paths import ZephyrusPaths

logger = logging.getLogger(__name__)


class ZephyrusLoggerCore:
    """
    ZephyrusLoggerCore manages logging, summarization, and search for categorized entries using JSON and Markdown files. It initializes the environment, handles batch summarization with AI, maintains summary tracking, and provides search functionality across summaries and raw logs. Integrates with organization-specific modules for configuration, file management, and AI summarization.
    """

    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT = "%Y-%m-%d"
    BATCH_KEY = "batch"
    ORIGINAL_SUMMARY_KEY = "original_summary"
    CORRECTED_SUMMARY_KEY = "corrected_summary"
    CORRECTION_TIMESTAMP_KEY = "correction_timestamp"
    CONTENT_KEY = "content"
    TIMESTAMP_KEY = "timestamp"

    def __init__(self, script_dir: Union[str, Path]) -> None:
        """
        Initializes the ZephyrusLoggerCore instance by loading configuration, setting up paths, environment, AI summarizer, summary tracker, and log manager. Validates or rebuilds the summary tracker as needed, and configures batch size and logging behavior based on the current configuration.

        Args:
            script_dir (str or Path): The directory containing the script, used to resolve paths and configuration.
        """
        self.script_dir = Path(script_dir)
        self.config = get_effective_config()
        self.paths = ZephyrusPaths.from_config(self.script_dir)

        if self.config.get("test_mode", False):
            logger.warning("[TEST MODE: ACTIVE] Using test directories from config")

        self._initialize_environment()

        self.ai_summarizer = AISummarizer()
        self.summary_tracker = SummaryTracker(paths=self.paths)

        force_rebuild = get_config_value(self.config, "force_summary_tracker_rebuild", False)
        is_tracker_valid = self.summary_tracker.validate()

        if force_rebuild:
            logger.info("[CONFIG] Force rebuild enabled; rebuilding summary tracker.")
            self.summary_tracker.rebuild()
        elif not is_tracker_valid:
            logger.warning("[RECOVERY] Tracker invalid or empty; rebuilding from logs.")
            self.summary_tracker.rebuild()

            if not self.summary_tracker.validate():
                logger.critical("[FATAL] Rebuild failed validation. Check logs and data integrity.")
                raise RuntimeError("SummaryTracker rebuild failed validation.")
        else:
            logger.info("[VALIDATION] Summary tracker loaded successfully and valid.")

        self.BATCH_SIZE = max(1, int(get_config_value(self.config, "batch_size", 5)))

        self.log_manager = LogManager(
            self.paths.json_log_file,
            self.paths.txt_log_file,
            self.paths.correction_summaries_file,
            self.TIMESTAMP_FORMAT,
            self.CONTENT_KEY,
            self.TIMESTAMP_KEY,
        )

    def _safe_read_json(self, filepath: Path) -> Dict[str, Any]:
        """
        Safely reads a JSON file and returns its contents as a dictionary.

        Args:
            filepath (Path): The path to the JSON file to be read.

        Returns:
            Dict[str, Any]: The contents of the JSON file. Returns an empty dictionary if an error occurs during reading.
        """
        try:
            return read_json(filepath)
        except Exception as e:
            logger.error("Failed to read JSON from %s: %s", filepath, e, exc_info=True)
            return {}

    def _initialize_environment(self) -> None:
        """
        Ensures the environment is initialized by creating base directories, log files, and other necessary files.

        This method is called during the constructor of the `ZephyrusCore` class. It ensures that the following files/directories exist:

        - The log directory (`self.paths.log_dir`)
        - The export directory (`self.paths.export_dir`)
        - The JSON log file (`self.paths.json_log_file`)
        - The plain text log file (`self.paths.txt_log_file`)
        - The correction summaries file (`self.paths.correction_summaries_file`)
        - The configuration file (`self.paths.config_file`)

        If any of these files/directories do not exist, they are created. If the JSON log file or correction summaries file exist but are empty, they are initialized to an empty JSON object.

        If the configuration file does not exist, a minimal configuration is recreated with a batch size of 5.
        """
        self.paths.log_dir.mkdir(parents=True, exist_ok=True)
        self.paths.export_dir.mkdir(parents=True, exist_ok=True)

        # Create log file only if summarization or logging is required
        if self.paths.json_log_file.exists():
            logger.debug("Log file already exists: %s", self.paths.json_log_file)
        else:
            logger.info("Creating empty log file at: %s", self.paths.json_log_file)
            write_json(self.paths.json_log_file, {})

        if not self.paths.txt_log_file.exists():
            self.paths.txt_log_file.write_text("=== Zephyrus Idea Logger ===\n", encoding="utf-8")

        # Correction summaries
        if not self.paths.correction_summaries_file.exists():
            logger.info(
                "Creating empty correction summaries file at: %s",
                self.paths.correction_summaries_file,
            )
            write_json(self.paths.correction_summaries_file, {})
        elif self.paths.correction_summaries_file.stat().st_size == 0:
            logger.warning("correction_summaries_file is empty. Initializing to empty JSON.")
            write_json(self.paths.correction_summaries_file, {})

        # Config safety net (should already exist in prod)
        if not self.paths.config_file.exists():
            logger.warning(
                "Missing config file at %s — recreating minimal config.", self.paths.config_file
            )
            self.paths.config_file.parent.mkdir(parents=True, exist_ok=True)
            write_json(self.paths.config_file, {"batch_size": 5})

    def _get_summary_for_batch(self, batch_entries: List[Dict[str, Any]], subcategory: str) -> str:
        """
        Gets a summary for a batch of log entries.

        Args:
            batch_entries (List[Dict[str, Any]]): A list of log entries to summarize.
            subcategory (str): The subcategory of the log entries.

        Returns:
            str: The summary of the batch of entries, or None if summarization failed.
        """
        try:
            summary = self.ai_summarizer.summarize_entries_bulk(
                [entry[self.CONTENT_KEY] for entry in batch_entries], subcategory=subcategory
            )
        except Exception as e:
            logger.error("AI summarization failed: %s", e, exc_info=True)
            try:
                summary = self.ai_summarizer._fallback_summary(
                    "\n".join(entry[self.CONTENT_KEY] for entry in batch_entries)
                )
            except Exception as fallback_e:
                logger.error("Fallback summarization failed: %s", fallback_e, exc_info=True)
                return None
        return summary.strip() if summary and summary.strip() else None

    def log_to_json(
        self, timestamp: str, date_str: str, main_category: str, subcategory: str, entry: str
    ) -> bool:
        """
        Logs an entry to the JSON log file and updates the summary tracker.

        Args:
            timestamp (str): The timestamp of the log entry.
            date_str (str): The date string of the log entry.
            main_category (str): The main category of the log entry.
            subcategory (str): The subcategory of the log entry.
            entry (str): The log entry to be logged.

        Returns:
            bool: True if the entry was logged successfully, False otherwise.
        """
        try:
            # Delegate the append operation to LogManager.
            self.log_manager.append_entry(date_str, main_category, subcategory, entry)
            self.summary_tracker.update(main_category, subcategory, new_entries=1)
            tracker = self.summary_tracker.tracker.get(main_category, {}).get(subcategory, {})
            unsummarized = tracker.get("logged_total", 0) - tracker.get("summarized_total", 0)
            if unsummarized >= self.BATCH_SIZE:
                logger.info(
                    "[BATCH READY] %d unsummarized entries in %s → %s",
                    unsummarized,
                    main_category,
                    subcategory,
                )
                self.generate_global_summary(main_category, subcategory)
            else:
                needed = self.BATCH_SIZE - unsummarized
                logger.info(
                    "[LOGGED] Entry added for %s → %s. Need %d more entries to trigger summary.",
                    main_category,
                    subcategory,
                    needed,
                )
            return True
        except Exception as e:
            logger.error("Error in log_to_json: %s", e, exc_info=True)
            return False

    def generate_global_summary(self, main_category: str, subcategory: str) -> bool:
        """
        Generates a global summary for the given main category and subcategory.

        Args:
            main_category (str): The main category of the log entries.
            subcategory (str): The subcategory of the log entries.

        Returns:
            bool: True if the global summary was generated successfully, False otherwise.
        """
        batch_entries = self.log_manager.get_unsummarized_batch(
            main_category,
            subcategory,
            self.summary_tracker.get_summarized_count(main_category, subcategory),
            self.BATCH_SIZE,
        )
        if len(batch_entries) < self.BATCH_SIZE:
            logger.info(
                "[SKIP] Not enough unsummarized entries for %s → %s", main_category, subcategory
            )
            return False

        summary = self._get_summary_for_batch(batch_entries, subcategory)
        if not summary:
            logger.error("[ERROR] AI summary returned empty after attempts.")
            return False

        start_ts = batch_entries[0][self.TIMESTAMP_KEY]
        end_ts = batch_entries[-1][self.TIMESTAMP_KEY]
        batch_label = f"{start_ts} → {end_ts}"

        new_data = {
            "batch": batch_label,
            self.ORIGINAL_SUMMARY_KEY: summary,
            self.CORRECTED_SUMMARY_KEY: "",
            self.CORRECTION_TIMESTAMP_KEY: datetime.now().strftime(self.TIMESTAMP_FORMAT),
            "start": start_ts,
            "end": end_ts,
        }

        try:
            self.log_manager.update_correction_summaries(main_category, subcategory, new_data)
            self.summary_tracker.update(main_category, subcategory, summarized=self.BATCH_SIZE)
            logger.info(
                "[SUCCESS] Global summary written for %s → %s (Batch: %s)",
                main_category,
                subcategory,
                batch_label,
            )
            return True
        except Exception as e:
            logger.error("[ERROR] Failed to write global summary or tracker: %s", e, exc_info=True)
            return False

    def generate_summary(self, date_str: str, main_category: str, subcategory: str) -> bool:
        """
        Generates a summary for the given date, main category, and subcategory.

        Args:
            date_str (str): The date of the log entries.
            main_category (str): The main category of the log entries.
            subcategory (str): The subcategory of the log entries.

        Returns:
            bool: True if the summary was generated successfully, False otherwise.
        """
        return self.generate_global_summary(main_category, subcategory)

    def log_to_markdown(
        self, date_str: str, main_category: str, subcategory: str, entry: str
    ) -> bool:
        """
        Logs an entry to a Markdown file, organizing by date and subcategory.

        Args:
            date_str (str): The date string for the log entry.
            main_category (str): The main category of the log entry.
            subcategory (str): The subcategory of the log entry.
            entry (str): The content of the log entry to be written.

        Returns:
            bool: True if the entry was logged successfully, False otherwise.

        This method creates or updates a Markdown file for the given main category, adding
        the entry under the appropriate date header. If the file or date header does not exist,
        they are created. An error is logged and False is returned if an exception occurs.
        """
        try:
            md_filename = sanitize_filename(main_category) + ".md"
            md_path = self.paths.export_dir / md_filename
            date_header = f"## {date_str}"
            md_content = f"- **{subcategory}**: {entry}\n"
            if md_path.exists():
                content = md_path.read_text(encoding="utf-8")
                if date_header in content:
                    updated_content = re.sub(
                        f"({date_header}\\n)", f"\\1{md_content}", content, count=1
                    )
                else:
                    updated_content = f"{content}\n{date_header}\n\n{md_content}"
            else:
                updated_content = f"# {main_category}\n\n{date_header}\n\n{md_content}"
            md_path.write_text(updated_content, encoding="utf-8")
            return True
        except Exception as e:
            logger.error("Error in log_to_markdown: %s", e, exc_info=True)
            return False

    def force_summary_all(self) -> None:
        """
        Forces summarization for all log entries across all dates, main categories, and subcategories.
        Iterates until no more unsummarized batches are available.
        """
        logs = self.log_manager.read_logs()
        for date in sorted(logs.keys()):
            for main_cat, subcats in logs[date].items():
                for sub_cat in subcats.keys():
                    # Continue generating summary for each (main_cat, sub_cat) until no more batches are ready.
                    while self.generate_global_summary(main_cat, sub_cat):
                        pass

    def save_entry(self, main_category: str, subcategory: str, entry: str) -> bool:
        """
        Wrapper for log_to_json to support the GUI controller interface.
        """
        if not main_category or not subcategory or not entry:
            logger.error("Invalid input: main_category, subcategory, and entry must not be empty")
            return False
        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        date_str = datetime.now().strftime(self.DATE_FORMAT)
        json_success = self.log_to_json(timestamp, date_str, main_category, subcategory, entry)
        md_success = self.log_to_markdown(date_str, main_category, subcategory, entry)
        return json_success and md_success

    def search_summaries(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches through all summaries (across all dates, main categories, and subcategories)
        and returns the top-k most relevant results based on the query.

        Args:
            query (str): The search query.
            top_k (int, optional): The number of results to return. Defaults to 5.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the search results.
        """
        return self.summary_tracker.summary_indexer.search(query, top_k)

    def search_raw_logs(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches through the raw logs using the specified query and returns the top-k most relevant results.

        Args:
            query (str): The search query.
            top_k (int, optional): The number of top results to return. Defaults to 5.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the search results.
        """
        return self.summary_tracker.raw_indexer.search(query, top_k)

    def log_new_entry(self, main_category: str, subcategory: str, entry: str) -> bool:
        """
        Logs a new entry, saving it to both the JSON log and the Markdown file.

        Args:
            main_category (str): The main category of the log entry.
            subcategory (str): The subcategory of the log entry.
            entry (str): The content of the log entry.

        Returns:
            bool: Whether the log entry was saved successfully.

        """
        return self.save_entry(main_category, subcategory, entry)
