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
    """

    def __init__(self, paths: ZephyrusPaths, autoload: bool = True) -> None:
        super().__init__(paths=paths, index_name="raw")
        self.log_path = paths.json_log_file  # Explicit log file path for clarity

        if autoload:
            try:
                self.load_index()
            except FileNotFoundError:
                logger.warning("Raw log index files not found; skipping autoload.")

    def load_entries(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Loads raw entries from the zephyrus_log.json file.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: Raw entry texts and metadata.
        """
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error("Raw log file not found at %s", self.log_path)
            return [], []
        except json.JSONDecodeError as e:
            logger.error("Failed to decode JSON from raw log file: %s", e, exc_info=True)
            return [], []
        except Exception as e:
            logger.error("Unexpected error while reading raw log file: %s", e, exc_info=True)
            return [], []

        texts, meta = [], []
        try:
            for date, categories in data.items():
                texts, meta = self._process_categories(date, categories, texts, meta)
        except Exception as e:
            logger.error("Error processing raw log entries: %s", e, exc_info=True)

        return texts, meta

    def _process_categories(
        self, date: str, categories: dict, texts: List[str], meta: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Processes categories for a given date, updating the texts and metadata.

        Args:
            date (str): The date of the entries being processed.
            categories (dict): A dictionary of main categories, each containing subcategories.
            texts (List[str]): The list to append entry contents to.
            meta (List[Dict[str, Any]]): The list to append entry metadata to.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: Updated texts and metadata lists with processed categories.
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
        self, date: str, main_cat: str, subcats: dict, texts: List[str], meta: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Processes subcategories within a main category for a given date.

        Args:
            date (str): The date of the entries being processed.
            main_cat (str): The main category of the entries.
            subcats (dict): A dictionary of subcategories, each with their list of entries.
            texts (List[str]): The list to append entry contents to.
            meta (List[Dict[str, Any]]): The list to append entry metadata to.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: Updated texts and metadata lists with processed entries.
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
            entries (List[Any]): A list of entries to process, each containing content and timestamp.
            texts (List[str]): The list to append entry contents to.
            meta (List[Dict[str, Any]]): The list to append entry metadata to.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: Updated texts and metadata lists with processed entries.
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

    def rebuild(self):
        logger.info("Rebuilding raw log index from scratch.")
        success = self.build_index_from_logs()
        if success:
            self.save_index()
        else:
            logger.warning("Raw index rebuild aborted: no entries to index.")
