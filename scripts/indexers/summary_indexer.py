import json
import os
from pathlib import Path
from typing import List, Dict, Tuple, Any
from scripts.indexers.base_indexer import BaseIndexer
from scripts.config.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)


class SummaryIndexer(BaseIndexer):
    def __init__(self, summaries_path: str = None, index_path: str = None, metadata_path: str = None) -> None:
        """
        Initializes the SummaryIndexer class and sets up paths for summaries, index, and metadata.
        """
        config = ConfigManager.load_config()
        # Use provided paths if given; otherwise, fetch from ConfigManager.
        summaries_path = summaries_path or ConfigManager.get_value("correction_summaries_path",
                                                                   "logs/correction_summaries.json")
        index_path = index_path or ConfigManager.get_value("faiss_index_path", "vector_store/summary_index.faiss")
        metadata_path = metadata_path or ConfigManager.get_value("faiss_metadata_path",
                                                                 "vector_store/summary_metadata.pkl")

        # Resolve paths to absolute paths if necessary.
        if not os.path.isabs(summaries_path):
            summaries_path = str(Path(summaries_path).resolve())
        if not os.path.isabs(index_path):
            index_path = str(Path(index_path).resolve())
        if not os.path.isabs(metadata_path):
            metadata_path = str(Path(metadata_path).resolve())

        super().__init__(summaries_path=summaries_path, index_path=index_path, metadata_path=metadata_path)
        self.use_cosine = True

    def load_entries(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Loads the entries from the correction summaries JSON file.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: Text entries (summaries) and associated metadata.
        """
        try:
            with open(self.summaries_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error("Summaries file not found at %s", self.summaries_path)
            return [], []
        except json.JSONDecodeError as e:
            logger.error("Failed to decode JSON from summaries file: %s", e, exc_info=True)
            return [], []
        except Exception as e:
            logger.error("Unexpected error reading summaries file: %s", e, exc_info=True)
            return [], []

        texts: List[str] = []
        meta: List[Dict[str, Any]] = []
        try:
            for date, categories in data.items():
                texts, meta = self._process_categories(date, categories, texts, meta)
        except Exception as e:
            logger.error("Error processing summary entries: %s", e, exc_info=True)
        return texts, meta

    def _process_categories(self, date: str, categories: dict, texts: List[str], meta: List[Dict[str, Any]]) -> Tuple[
        List[str], List[Dict[str, Any]]]:
        """
        Processes categories and their subcategories.
        """
        for main_cat, subcats in categories.items():
            try:
                texts, meta = self._process_subcategories(date, main_cat, subcats, texts, meta)
            except (KeyError, TypeError, AttributeError) as e:
                logger.warning("Error processing category '%s' on date '%s': %s", main_cat, date, e, exc_info=True)
        return texts, meta

    def _process_subcategories(self, date: str, main_cat: str, subcats: dict, texts: List[str],
                               meta: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Processes subcategories and their batches.
        """
        for subcat, batches in subcats.items():
            try:
                texts, meta = self._process_batches(date, main_cat, subcat, batches, texts, meta)
            except (KeyError, TypeError, AttributeError) as e:
                logger.warning("Error processing subcategory '%s' under '%s' on date '%s': %s", subcat, main_cat, date,
                               e, exc_info=True)
        return texts, meta

    def _process_batches(self, date: str, main_cat: str, subcat: str, batches: list, texts: List[str],
                         meta: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Processes batches within a subcategory.
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
                    logger.warning("Batch in %s → %s → %s has no summary text.", date, main_cat, subcat)
            except (KeyError, TypeError, AttributeError) as e:
                logger.error("Error processing batch in %s → %s → %s: %s", date, main_cat, subcat, e, exc_info=True)
        return texts, meta
