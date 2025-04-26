"""
This module defines the RawLogIndexer class for building and managing a FAISS vector index
over raw log entries from zephyrus_log.json.

Core features:
- Loading and parsing raw log entries by date, main category, and subcategory.
- Extracting entry content and metadata for semantic indexing.
- Building, saving, loading, and rebuilding a FAISS index for full-text vector search.
- Robust error handling and logging for file I/O and data processing.
- Designed for use in the Zephyrus project to enable fast, flexible semantic search.
"""

import json
import logging
from typing import List, Dict, Tuple, Any
from scripts.paths import ZephyrusPaths
from scripts.indexers.base_indexer import BaseIndexer

logger = logging.getLogger(__name__)


class RawLogIndexer(BaseIndexer):
    """
    Builds a FAISS index from raw entries in zephyrus_log.json.

    Used for full-text vector search across all logged ideas (not just summaries).

    Attributes:
        log_path (str): The path to the JSON log file.
    """

    def __init__(self, paths: ZephyrusPaths, autoload: bool = True) -> None:
        """
        Initializes the RawLogIndexer with the specified paths and optionally loads the index.

        Args:
            paths (ZephyrusPaths): The paths configuration for the indexer.
            autoload (bool): Whether to automatically load the index on initialization.
            Defaults to True.

        Raises:
            FileNotFoundError: If the index files are not found during autoload.
        """
        super().__init__(paths=paths, index_name="raw")
        self.log_path: str = paths.json_log_file  # Explicit log file path for clarity

        if autoload:
            try:
                self.load_index()
            except FileNotFoundError:
                logger.warning("Raw log index files not found; skipping autoload.")

    def load_entries(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Loads raw entries from the zephyrus_log.json file.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: A tuple containing a list of entry contents
            and a list of metadata dictionaries.

        Raises:
            FileNotFoundError: If the log file does not exist.
            json.JSONDecodeError: If the JSON file is malformed.
        """
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                data: Dict[str, Any] = json.load(f)
        except FileNotFoundError:
            logger.error("Raw log file not found at %s", self.log_path)
            return [], []
        except json.JSONDecodeError as e:
            logger.error("Failed to decode JSON from raw log file: %s", e, exc_info=True)
            return [], []
        except Exception as e:
            logger.error("Unexpected error while reading raw log file: %s", e, exc_info=True)
            return [], []

        texts: List[str] = []
        meta: List[Dict[str, Any]] = []
        try:
            for date, categories in data.items():
                texts, meta = self._process_categories(date, categories, texts, meta)
        except Exception as e:
            logger.error("Error processing raw log entries: %s", e, exc_info=True)

        return texts, meta

    def _process_categories(
        self, date: str, categories: Dict[str, Any], texts: List[str], meta: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Processes categories for a given date, updating the texts and metadata.

        Args:
            date (str): The date of the entries being processed.
            categories (Dict[str, Any]): A dictionary of main categories.
            texts (List[str]): The list to append entry contents to.
            meta (List[Dict[str, Any]]): The list to append entry metadata to.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: Updated texts and metadata lists.
        """
        for main_cat, subcats in categories.items():
            try:
                texts, meta = self._process_subcategories(date, main_cat, subcats, texts, meta)
            except Exception as e:
                logger.warning(
                    "Error processing category '%s' on date '%s': %s",
                    main_cat,
                    date,
                    e,
                    exc_info=True,
                )
        return texts, meta

    def _process_subcategories(
        self,
        date: str,
        main_cat: str,
        subcats: Dict[str, Any],
        texts: List[str],
        meta: List[Dict[str, Any]],
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Processes subcategories within a main category for a given date.

        Args:
            date (str): The date of the entries being processed.
            main_cat (str): The main category of the entries.
            subcats (Dict[str, Any]): A dictionary of subcategories.
            texts (List[str]): The list to append entry contents to.
            meta (List[Dict[str, Any]]): The list to append entry metadata to.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: Updated texts and metadata lists.
        """
        for subcat, entries in subcats.items():
            try:
                texts, meta = self._process_entries(date, main_cat, subcat, entries, texts, meta)
            except Exception as e:
                logger.warning(
                    "Error processing subcategory '%s' under '%s' on date '%s': %s",
                    subcat,
                    main_cat,
                    date,
                    e,
                    exc_info=True,
                )
        return texts, meta

    def _process_entries(
        self,
        date: str,
        main_cat: str,
        subcat: str,
        entries: List[Any],
        texts: List[str],
        meta: List[Dict[str, Any]],
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Processes a list of entries for a given date, main category, and subcategory.

        Args:
            date (str): The date of the entries being processed.
            main_cat (str): The main category of the entries.
            subcat (str): The subcategory of the entries.
            entries (List[Any]): A list of entries to process.
            texts (List[str]): The list to append entry contents to.
            meta (List[Dict[str, Any]]): The list to append entry metadata to.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: Updated texts and metadata lists.
        """
        for entry in entries:
            try:
                content = entry.get("content")
                timestamp = entry.get("timestamp")
                if content:
                    texts.append(content)
                    meta.append(
                        {
                            "date": date,
                            "main_category": main_cat,
                            "subcategory": subcat,
                            "timestamp": timestamp,
                        }
                    )
                else:
                    logger.warning(
                        "Missing content in entry (%s → %s → %s)", date, main_cat, subcat
                    )
            except Exception as e:
                logger.error(
                    "Failed to process entry (%s → %s → %s): %s",
                    date,
                    main_cat,
                    subcat,
                    e,
                    exc_info=True,
                )
        return texts, meta

    def build_index_from_logs(self) -> bool:
        """
        Loads entries from file and rebuilds FAISS index.

        Returns:
            bool: Whether the index was successfully rebuilt.

        Raises:
            Exception: If an error occurs while building the index.
        """
        try:
            texts, meta = self.load_entries()
            if not texts:
                logger.warning("No entries found to build index from.")
                return False
            return self.build_index(texts, meta)
        except Exception as e:
            logger.error("Failed to build index from logs: %s", e, exc_info=True)
            return False

    def rebuild(self) -> None:
        """
        Rebuilds the raw log index from scratch.

        This method loads entries from the log file, rebuilds the FAISS index, and saves the new index.

        Raises:
            Exception: If an error occurs while rebuilding the index.
        """
        logger.info("Rebuilding raw log index from scratch.")
        success = self.build_index_from_logs()
        if success:
            self.save_index()
        else:
            logger.warning("Raw index rebuild aborted: no entries to index.")
