import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Any

from scripts.paths import ZephyrusPaths
from scripts.indexers.base_indexer import BaseIndexer

logger = logging.getLogger(__name__)


class SummaryIndexer(BaseIndexer):
    """
    Builds a FAISS index from summarized entries in correction_summaries.json.
    """

    def __init__(self, paths: ZephyrusPaths, autoload: bool = True) -> None:

        """
        Initializes a SummaryIndexer object.

        :param paths: An instance of ZephyrusPaths containing the necessary file paths.
        :type paths: ZephyrusPaths
        :param autoload: Flag indicating whether to load the index automatically.
        :type autoload: bool

        Initializes the SummaryIndexer, setting the path to the summaries file.
        If autoload is True, attempts to load the FAISS index. Logs a warning if
        the index files are not found.
        """
        super().__init__(paths=paths, index_name="summary")
        self.summaries_path = paths.correction_summaries_file

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
                data = json.load(f)
        except FileNotFoundError:
            logger.error("Summaries file not found at %s", self.summaries_path)
            return [], []
        except json.JSONDecodeError as e:
            logger.error("Failed to decode summaries JSON: %s", e, exc_info=True)
            return [], []
        except Exception as e:
            logger.error("Unexpected error loading summaries: %s", e, exc_info=True)
            return [], []

        texts, meta = [], []
        try:
            for date, categories in data.items():
                texts, meta = self._process_categories(date, categories, texts, meta)
        except Exception as e:
            logger.error("Error processing summaries: %s", e, exc_info=True)

        return texts, meta

    def _process_categories(self, date: str, categories: dict, texts: List[str],
                            meta: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Process a dictionary of categories and their subcategories.

        Goes through each main category and its subcategories for a given date.
        Calls `_process_subcategories` for each subcategory, and appends the results to the texts
        and meta lists.

        Args:
            date: str, the date that the summaries were written on.
            categories: dict, a dictionary of main categories and their subcategories.
            texts: List[str], a list of all the summary texts.
            meta: List[Dict[str, Any]], a list of the metadata for each summary.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: The updated texts and meta lists.
        """
        for main_cat, subcats in categories.items():
            try:
                texts, meta = self._process_subcategories(date, main_cat, subcats, texts, meta)
            except Exception as e:
                logger.warning("Error in category '%s' on '%s': %s", main_cat, date, e, exc_info=True)
        return texts, meta

    def _process_subcategories(self, date: str, main_cat: str, subcats: dict, texts: List[str],
                               meta: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]]]:

        """
        Process a dictionary of subcategories and their batches of summaries.

        Goes through each subcategory and its batches of summaries for a given date and main category.
        Calls `_process_batches` for each batch of summaries, and appends the results to the texts
        and meta lists.

        Args:
            date: str, the date that the summaries were written on.
            main_cat: str, the main category of the summaries.
            subcats: dict, a dictionary of subcategories and their batches of summaries.
            texts: List[str], a list of all the summary texts.
            meta: List[Dict[str, Any]], a list of the metadata for each summary.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: The updated texts and meta lists.
        """
        for subcat, batches in subcats.items():
            try:
                texts, meta = self._process_batches(date, main_cat, subcat, batches, texts, meta)
            except Exception as e:
                logger.warning("Error in subcategory '%s' → '%s' on '%s': %s", main_cat, subcat, date, e, exc_info=True)
        return texts, meta

    def _process_batches(self, date: str, main_cat: str, subcat: str, batches: list, texts: List[str],
                         meta: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Process a list of batches of summaries.

        Goes through each batch of summaries for a given date, main category, and subcategory.
        Extracts the corrected or original summary text from each batch, and appends it to the
        texts list. Also appends the corresponding metadata to the meta list.

        Args:
            date: str, the date that the summaries were written on.
            main_cat: str, the main category of the summaries.
            subcat: str, the subcategory of the summaries.
            batches: list, a list of batches of summaries.
            texts: List[str], a list of all the summary texts.
            meta: List[Dict[str, Any]], a list of the metadata for each summary.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: The updated texts and meta lists.
        """
        for batch in batches:
            try:
                text = batch.get("corrected_summary") or batch.get("original_summary")
                if text:
                    texts.append(text)
                    meta.append({
                        "date": date,
                        "main_category": main_cat,
                        "subcategory": subcat,
                        "batch": batch.get("batch"),
                        "timestamp": batch.get("correction_timestamp")
                    })
                else:
                    logger.warning("Missing summary in %s → %s → %s", date, main_cat, subcat)
            except Exception as e:
                logger.error("Failed to process batch %s → %s → %s: %s", date, main_cat, subcat, e, exc_info=True)
        return texts, meta

    def build_index_from_logs(self) -> bool:
        """
        Loads entries from file and rebuilds FAISS index.
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

    def rebuild(self):
        logger.info("Rebuilding summary index from scratch.")
        entries, metadata = self.load_entries()
        if entries:
            self.build_index(entries, metadata)
            self.save_index()
        else:
            logger.warning("No entries to index during rebuild.")
