import json
from pathlib import Path
from typing import List, Dict, Tuple, Any
from scripts.config.config_manager import ConfigManager
from scripts.indexers.base_indexer import BaseIndexer
import logging

logger = logging.getLogger(__name__)


class RawLogIndexer(BaseIndexer):
    """
    Builds a FAISS index from raw entries in zephyrus_log.json.
    Used for full-text vector search across all logged ideas (not just summaries).
    """

    def __init__(self, log_path: str = None, index_path: str = None, metadata_path: str = None) -> None:
        """
        Initializes the RawLogIndexer by setting up paths for the log file, FAISS index,
        and metadata files.
        """
        config = ConfigManager.load_config()
        try:
            default_log_path = ConfigManager.get_value("raw_log_path", "logs/zephyrus_log.json")
            self.log_path: str = log_path or default_log_path
        except Exception as e:
            logger.error("Error obtaining raw log path: %s", e, exc_info=True)
            raise

        index_path = index_path or ConfigManager.get_value("raw_log_index_path", "vector_store/raw_index.faiss")
        metadata_path = metadata_path or ConfigManager.get_value("raw_log_metadata_path",
                                                                 "vector_store/raw_metadata.pkl")

        # Pass log_path as summaries_path to BaseIndexer.
        super().__init__(summaries_path=self.log_path, index_path=index_path, metadata_path=metadata_path)

    def load_entries(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Loads raw entries from the zephyrus_log.json file and extracts the relevant data.

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
        except OSError as e:
            logger.error("OS error while reading raw log file: %s", e, exc_info=True)
            return [], []

        texts: List[str] = []
        meta: List[Dict[str, Any]] = []

        try:
            for date, categories in data.items():
                texts, meta = self._process_categories(date, categories, texts, meta)
        except Exception as e:
            logger.error("Error processing raw log entries: %s", e, exc_info=True)
        return texts, meta

    def _process_categories(self, date: str, categories: dict, texts: List[str], meta: List[Dict[str, Any]]) -> Tuple[
        List[str], List[Dict[str, Any]]]:
        """
        Processes categories in the log file and delegates processing of subcategories.
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
        Processes subcategories and delegates processing of entries within each subcategory.
        """
        for subcat, entries in subcats.items():
            try:
                texts, meta = self._process_entries(date, main_cat, subcat, entries, texts, meta)
            except (KeyError, TypeError, AttributeError) as e:
                logger.warning("Error processing subcategory '%s' under '%s' on date '%s': %s", subcat, main_cat, date,
                               e, exc_info=True)
        return texts, meta

    def _process_entries(self, date: str, main_cat: str, subcat: str, entries: List[Any], texts: List[str],
                         meta: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Processes the entries in each subcategory and extracts relevant data.
        """
        for entry in entries:
            try:
                content = entry.get("content")
                timestamp = entry.get("timestamp")
                if content:
                    texts.append(content)
                    meta.append({
                        "date": date,
                        "main_category": main_cat,
                        "subcategory": subcat,
                        "timestamp": timestamp
                    })
                else:
                    logger.warning("Missing content in an entry on date %s, category %s, subcategory %s.", date,
                                   main_cat, subcat)
            except (KeyError, TypeError, AttributeError) as e:
                logger.error("Error processing an entry in %s → %s → %s: %s", date, main_cat, subcat, e, exc_info=True)
        return texts, meta
