"""
summary_indexer.py

This module defines the SummaryIndexer class for building and managing a FAISS vector index over summarized entries from correction_summaries.json.

Core features include:
- Loading and parsing summarized entries organized by date, main category, and subcategory.
- Extracting summary texts and associated metadata for semantic indexing.
- Building, saving, loading, and rebuilding a FAISS index for semantic search across all summarized corrections.
- Robust error handling and logging for file I/O and data processing.
- Designed for use in the Zephyrus project to enable fast, flexible semantic search over all summarized log data.
"""

import json
import logging
from typing import List, Dict, Tuple, Any

from scripts.paths import ZephyrusPaths
from scripts.indexers.base_indexer import BaseIndexer

logger = logging.getLogger(__name__)


class SummaryIndexer(BaseIndexer):
    """
    Builds a FAISS index from summarized entries in correction_summaries.json.

    Core features include loading and parsing summarized entries, extracting summary texts,
    and managing the FAISS index for semantic search.
    """

    def __init__(self, paths: ZephyrusPaths, autoload: bool = True) -> None:
        """
        Initializes a SummaryIndexer object.

        Args:
            paths (ZephyrusPaths): An instance containing the necessary file paths.
            autoload (bool, optional): Flag indicating whether to load the index automatically. Defaults to True.
        """
        super().__init__(paths=paths, index_name="summary")
        self.summaries_path: str = paths.correction_summaries_file
        self.paths: ZephyrusPaths = paths
        self.autoload: bool = autoload

        if autoload:
            try:
                self.load_index()
                logger.info("Summary FAISS index loaded successfully.")
            except FileNotFoundError:
                logger.warning("Summary index files not found; skipping autoload.")

    def load_entries(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Loads summarized entries from the correction_summaries.json file.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: Summarized entry texts and metadata.
        """
        try:
            with open(self.summaries_path, "r", encoding="utf-8") as f:
                data: Dict[str, Any] = json.load(f)
        except FileNotFoundError:
            logger.error("Summaries file not found at %s", self.summaries_path)
            return [], []
        except json.JSONDecodeError as e:
            logger.error("Failed to decode summaries JSON: %s", e, exc_info=True)
            return [], []
        except Exception as e:
            logger.error("Unexpected error loading summaries: %s", e, exc_info=True)
            return [], []

        texts: List[str] = []
        meta: List[Dict[str, Any]] = []
        try:
            for date, categories in data.items():
                texts, meta = self._process_categories(date, categories, texts, meta)
        except Exception as e:
            logger.error("Error processing summaries: %s", e, exc_info=True)

        return texts, meta

    def _process_categories(
        self, date: str, categories: Dict[str, Any], texts: List[str], meta: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        for main_cat, subcats in categories.items():
            try:
                texts, meta = self._process_subcategories(date, main_cat, subcats, texts, meta)
            except Exception as e:
                logger.warning(
                    "Error in category '%s' on '%s': %s", main_cat, date, e, exc_info=True
                )
        return texts, meta

    def _process_subcategories(
        self, date: str, main_cat: str, subcats: Dict[str, Any], texts: List[str], meta: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        for subcat, batches in subcats.items():
            try:
                texts, meta = self._process_batches(date, main_cat, subcat, batches, texts, meta)
            except Exception as e:
                logger.warning(
                    "Error in subcategory '%s' → '%s' on '%s': %s",
                    main_cat,
                    subcat,
                    date,
                    e,
                    exc_info=True,
                )
        return texts, meta

    def _process_batches(
        self,
        date: str,
        main_cat: str,
        subcat: str,
        batches: List[Any],
        texts: List[str],
        meta: List[Dict[str, Any]],
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        for batch in batches:
            try:
                text = batch.get("corrected_summary") or batch.get("original_summary")
                if text:
                    texts.append(text)
                    meta.append(
                        {
                            "date": date,
                            "main_category": main_cat,
                            "subcategory": subcat,
                            "batch": batch.get("batch"),
                            "timestamp": batch.get("correction_timestamp"),
                        }
                    )
                else:
                    logger.warning("Missing summary in %s → %s → %s", date, main_cat, subcat)
            except Exception as e:
                logger.error(
                    "Failed to process batch %s → %s → %s: %s",
                    date,
                    main_cat,
                    subcat,
                    e,
                    exc_info=True,
                )
        return texts, meta

    def load_index(self) -> None:
        """
        Load the FAISS index and associated metadata from their respective files.

        Raises:
            FileNotFoundError: If the index file or metadata file is not found.
        """
        super().load_index()

    def save_index(self) -> None:
        """
        Save the FAISS index and associated metadata to their respective files.

        This method delegates to the BaseIndexer implementation.
        """
        super().save_index()

    def rebuild_index(self) -> None:
        """
        Rebuild the FAISS index from the summarized entries.

        This method invokes building index from logs and saving it.
        """
        success = self.build_index_from_logs()
        if not success:
            logger.warning("Summary index rebuild aborted: no entries to index.")

    def build_index_from_logs(self) -> bool:
        """
        Loads entries from file and rebuilds FAISS index.

        Returns:
            bool: Whether the index was successfully rebuilt.
        """
        try:
            texts, meta = self.load_entries()
            if not texts:
                logger.warning("No summaries to index.")
                return False

            built = self.build_index(texts, meta)
            if built:
                self.save_index()
                logger.info("Summary FAISS index rebuilt and saved successfully.")
                return True
            return False
        except Exception as e:
            logger.error("Failed to build index from logs: %s", e, exc_info=True)
            return False

    def rebuild(self) -> None:
        """
        Rebuild the summary index from scratch.
        """
        entries, metadata = self.load_entries()
        if entries:
            self.build_index(entries, metadata)
            self.save_index()
        else:
            logger.warning("No entries to index during rebuild.")
