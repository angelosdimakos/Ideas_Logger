"""
Core module for Zephyrus Logger
================================
This refactored **core.py** wires together the new, slimmer helper
modules we just introduced (`EnvironmentBootstrapper`, `LogManager`,
`MarkdownLogger`, `SummaryTracker`, `SummaryEngine`). It restores the
public surface that the unit & integration tests expect while keeping
the implementation focused and declarative.

Key public methods / attributes re-exposed
-----------------------------------------
* **save_entry**          – add a new idea to JSON + Markdown & update tracker
* **log_new_entry**       – alias of *save_entry* (used by integration tests)
* **generate_global_summary** – force batch summarisation via `SummaryEngine`
* **generate_summary**    – backward-compat shim (date arg ignored)
* **search_summaries** / **search_raw_logs** – thin wrappers around the FAISS
  indexers (gracefully degrade to empty list when indices are disabled in
tests)
* **BATCH_SIZE**          – pulled from config with sane default so tests can
  use it directly.

Everything else (bootstrap, validation, etc.) stays untouched aside from
swapping our bespoke `_initialize_environment` with the clearer
`EnvironmentBootstrapper`.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Union, List, Dict, Any

from scripts.ai.ai_summarizer import AISummarizer
from scripts.config.config_loader import get_effective_config, get_config_value
from scripts.core.environment_bootstrapper import EnvironmentBootstrapper
from scripts.core.markdown_logger import MarkdownLogger
from scripts.paths import ZephyrusPaths
from scripts.utils.file_utils import read_json
from scripts.core.log_manager import LogManager
from scripts.core.summary_tracker import SummaryTracker
from scripts.core.summary_engine import SummaryEngine

logger = logging.getLogger(__name__)

class ZephyrusLoggerCore:  # pylint: disable=too-many-instance-attributes
    """
    High-level façade that ties together logging, summarizing, and search functionalities.

       This class serves as the main interface for managing logs, generating summaries,
       and searching through entries within the Zephyrus Logger application. It initializes
       various components necessary for logging and summarization, ensuring the environment
       is properly set up.

       Attributes:
           TIMESTAMP_FORMAT (str): Format for timestamps in logs.
           DATE_FORMAT (str): Format for dates in logs.
           BATCH_KEY (str): Key for batch processing.
           ORIGINAL_SUMMARY_KEY (str): Key for original summaries.
           CORRECTED_SUMMARY_KEY (str): Key for corrected summaries.
           CORRECTION_TIMESTAMP_KEY (str): Key for correction timestamps.
           CONTENT_KEY (str): Key for content in logs.
           TIMESTAMP_KEY (str): Key for timestamps in logs.
           BATCH_SIZE (int): Number of entries to process in a batch.
           ai_summarizer (AISummarizer): Instance of the AI summarizer.
           log_manager (LogManager): Instance of the log manager.
           md_logger (MarkdownLogger): Instance of the markdown logger.
           summary_tracker (SummaryTracker): Instance of the summary tracker.
           summary_engine (SummaryEngine): Instance of the summary engine.
       """
    # ------------------------------------------------------------------
    # 🗂  Static schema / defaults
    # ------------------------------------------------------------------
    # Define timestamp and date formats
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"  # Format for timestamps in logs
    DATE_FORMAT = "%Y-%m-%d"  # Format for dates in logs

    # JSON keys (kept public for backwards-compat)
    BATCH_KEY = "batch"  # Key for batch processing
    ORIGINAL_SUMMARY_KEY = "original_summary"  # Key for original summaries
    CORRECTED_SUMMARY_KEY = "corrected_summary"  # Key for corrected summaries
    CORRECTION_TIMESTAMP_KEY = "correction_timestamp"  # Key for correction timestamps
    CONTENT_KEY = "content"  # Key for content in logs
    TIMESTAMP_KEY = "timestamp"  # Key for timestamps in logs

    # ------------------------------------------------------------------
    # 🚀 Construction
    # ------------------------------------------------------------------
    def __init__(self, script_dir: Union[str, Path]):
        """
        Initializes the ZephyrusLoggerCore with necessary configurations and collaborators.

        Args:
            script_dir (Union[str, Path]): The directory of the script, used to resolve paths.

        This constructor performs the following actions:
        1) Loads the effective configuration and resolves all required paths using ZephyrusPaths.
        2) Ensures the necessary on-disk environment (directories and baseline files) is set up.
        3) Instantiates core runtime collaborators including AISummarizer, LogManager, MarkdownLogger,
           SummaryTracker, and SummaryEngine, with configurations like batch size and timestamp format.
        4) Validates the SummaryTracker and optionally rebuilds it if configured to do so or if validation fails.
        """
        self.script_dir = Path(script_dir)  # Store script directory
        self.config = get_effective_config()  # Load effective configuration
        self.paths = ZephyrusPaths.from_config(self.script_dir)  # Resolve required paths

        # 1) Ensure on-disk environment exists (dirs / baseline files)
        EnvironmentBootstrapper(self.paths).bootstrap()  # Bootstrap environment

        # 2) Core runtime collaborators
        self.BATCH_SIZE: int = max(1, int(get_config_value(self.config, "batch_size", 5)))  # Get batch size from config
        self.ai_summarizer = AISummarizer()  # Instantiate AI summarizer
        self.log_manager = LogManager(
            self.paths.json_log_file,
            self.paths.txt_log_file,
            self.paths.correction_summaries_file,
            self.TIMESTAMP_FORMAT,
            self.CONTENT_KEY,
            self.TIMESTAMP_KEY,
        )  # Instantiate log manager
        self.md_logger = MarkdownLogger(self.paths.export_dir)  # Instantiate markdown logger
        self.summary_tracker = SummaryTracker(paths=self.paths)  # Instantiate summary tracker
        self.summary_engine = SummaryEngine(
            self.ai_summarizer,
            self.log_manager,
            self.summary_tracker,
            self.TIMESTAMP_FORMAT,
            self.CONTENT_KEY,
            self.TIMESTAMP_KEY,
            self.BATCH_SIZE,
        )  # Instantiate summary engine

        # 3) Validate / rebuild tracker once on start-up
        if get_config_value(self.config, "force_summary_tracker_rebuild", False) or not self.summary_tracker.validate():
            logger.warning("[INIT] Rebuilding summary tracker from scratch …")
            self.summary_tracker.rebuild()  # Rebuild summary tracker
            if not self.summary_tracker.validate():
                raise RuntimeError("SummaryTracker rebuild failed validation – data is inconsistent.")

    # ------------------------------------------------------------------
    # ✍️  Public logging helpers
    # ------------------------------------------------------------------
    def save_entry(self, main_category: str, subcategory: str, entry: str) -> bool:
        """
        Saves a new log entry to the JSON log and Markdown export (if enabled).

        Args:
            main_category (str): The main category of the log entry.
            subcategory (str): The subcategory of the log entry.
            entry (str): The content of the log entry.

        Returns:
            bool: True if the Markdown export succeeded, False otherwise.
        """
        date_str = datetime.now().strftime(self.DATE_FORMAT)  # Get current date string
        try:
            self.log_manager.append_entry(date_str, main_category, subcategory, entry)  # Append entry to log
            md_ok = self.md_logger.log(date_str, main_category, subcategory, entry)  # Log to markdown
            self.summary_tracker.update(main_category, subcategory, new_entries=1)  # Update summary tracker
            return md_ok  # Return markdown export success
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Failed to save entry: %s", exc, exc_info=True)  # Log error
            return False  # Return failure

    # alias used by integration tests
    log_new_entry = save_entry  # Alias for save_entry

    # ------------------------------------------------------------------
    # 🧠  Summarisation API
    # ------------------------------------------------------------------
    def generate_global_summary(self, main_category: str, subcategory: str) -> bool:
        """
        Force a batch summarisation for *main_category → subcategory*.

        Args:
            main_category (str): The main category.
            subcategory (str): The subcategory.

        Returns:
            bool: The success flag.
        """
        return self.summary_engine.summarize(main_category, subcategory)  # Summarize using summary engine

    # backwards-compat shim for unit-tests that still pass a *date* arg
    def generate_summary(self, _date_str: str, main_category: str, subcategory: str) -> bool:
        """
        Backwards-compatibility shim for unit-tests that still pass a *date* arg.

        Force a batch summarisation for *main_category → subcategory*.
        """
        return self.generate_global_summary(main_category, subcategory)  # Call generate_global_summary

    # ------------------------------------------------------------------
    # 🔍  Search helpers (gracefully degrade when FAISS indexers are stubbed)
    # ------------------------------------------------------------------
    def _safe_search(self, indexer_attr: str, query: str, top_k: int) -> List[Any]:
        """
        Perform a search against a FAISS indexer safely, ignoring any exceptions.

        Args:
            indexer_attr (str): The attribute name of the SummaryIndexer instance to query.
            query (str): The search query.
            top_k (int): The number of results to return.

        Returns:
            List[Any]: A list of search results, possibly empty.
        """
        indexer = getattr(self.summary_tracker, indexer_attr, None)  # Get indexer attribute
        if indexer and hasattr(indexer, "search"):  # Check if indexer has search method
            try:
                return indexer.search(query, top_k=top_k)  # type: ignore[attr-defined]  # Perform search
            except Exception as exc:  # pragma: no cover
                logger.error("Search via %s failed: %s", indexer_attr, exc, exc_info=True)  # Log error
        return []  # Return empty list if search fails

    def search_summaries(self, query: str, top_k: int = 5) -> List[Any]:
        """
        Performs a vector search over summary entries using the FAISS index.

        Args:
            query (str): The search query.
            top_k (int, optional): The number of top results to return. Defaults to 5.

        Returns:
            List[Any]: A list of the top-k search results.
        """
        return self._safe_search("summary_indexer", query, top_k)  # Search summaries

    def search_raw_logs(self, query: str, top_k: int = 5) -> List[Any]:
        """
        Performs a vector search over raw log entries using the FAISS index.

        Args:
            query (str): The search query.
            top_k (int, optional): The number of top results to return. Defaults to 5.

        Returns:
            List[Any]: A list of the top-k search results.
        """
        return self._safe_search("raw_indexer", query, top_k)  # Search raw logs

    # ------------------------------------------------------------------
    # 🛠  Internal helpers (only the bare minimum kept public for tests)
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_read_json(filepath: Path) -> Dict[str, Any]:
        """
        Robustly reads a JSON file into a dictionary, returning an empty dict if any errors occur.

        This helper is used internally, e.g. when loading the tracker's state from disk.

        :param filepath: Path to the JSON file to read.
        :return: The deserialised JSON data as a dictionary.
        """
        try:
            return read_json(filepath)  # Read JSON file
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Failed to read JSON from %s: %s", filepath, exc, exc_info=True)  # Log error
            return {}  # Return empty dictionary if read fails
