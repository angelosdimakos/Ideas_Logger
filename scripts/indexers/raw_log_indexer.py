import json
from scripts.config.config_loader import load_config, get_config_value, get_absolute_path
from scripts.indexers.base_indexer import BaseIndexer
import logging

logger = logging.getLogger(__name__)

class RawLogIndexer(BaseIndexer):
    """
    Builds a FAISS index from raw entries in zephyrus_log.json.
    Used for full-text vector search across all logged ideas (not just summaries).
    """

    def __init__(self, log_path=None, index_path=None, metadata_path=None):
        """
        Initializes the RawLogIndexer by setting up paths for the log file, FAISS index, 
        and metadata files. It uses the `BaseIndexer` for FAISS logic.
        
        Args:
            log_path (str): Path to the raw log file (default: "logs/zephyrus_log.json").
            index_path (str): Path to the FAISS index file (default: "vector_store/raw_index.faiss").
            metadata_path (str): Path to the metadata file (default: "vector_store/raw_metadata.pkl").
        """
        config = load_config()
        try:
            self.log_path = get_absolute_path(
                log_path or get_config_value(config, "raw_log_path", "logs/zephyrus_log.json")
            )
        except Exception as e:
            logger.error("Error obtaining raw log path: %s", e, exc_info=True)
            raise

        index_path = index_path or get_config_value(config, "raw_log_index_path", "vector_store/raw_index.faiss")
        metadata_path = metadata_path or get_config_value(config, "raw_log_metadata_path", "vector_store/raw_metadata.pkl")

        # Use self.log_path as summaries_path for BaseIndexer.
        super().__init__(summaries_path=self.log_path, index_path=index_path, metadata_path=metadata_path)

    def load_entries(self):
        """
        Loads raw entries from the `zephyrus_log.json` file and extracts the relevant data.

        Reads through the log file, extracting the `content` and `timestamp` for each entry.
        Organizes them into `texts` (list of content) and `meta` (list of metadata dictionaries).

        Returns:
            tuple: 
                - list of str: Raw entry texts.
                - list of dict: Metadata for each entry.
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

        texts, meta = [], []

        try:
            for date, categories in data.items():
                texts, meta = self._process_categories(date, categories, texts, meta)
        except Exception as e:
            logger.error("Error processing raw log entries: %s", e, exc_info=True)
            # Return what we have so far (or decide to return empty lists)
        return texts, meta

    def _process_categories(self, date, categories, texts, meta):
        """
        Processes categories in the log file and delegates processing of subcategories.

        Args:
            date (str): Date of the entry.
            categories (dict): The categories containing subcategories and their entries.
            texts (list): List of raw entry texts.
            meta (list): List of metadata for each entry.
        
        Returns:
            tuple:
                - list of str: Updated list of texts.
                - list of dict: Updated list of metadata.
        """
        for main_cat, subcats in categories.items():
            try:
                texts, meta = self._process_subcategories(date, main_cat, subcats, texts, meta)
            except (KeyError, TypeError, AttributeError) as e:
                logger.warning("Error processing category '%s' on date '%s': %s", main_cat, date, e, exc_info=True)
        return texts, meta

    def _process_subcategories(self, date, main_cat, subcats, texts, meta):
        """
        Processes subcategories and delegates processing of entries within each subcategory.

        Args:
            date (str): The date of the entry.
            main_cat (str): The main category under which the entries fall.
            subcats (dict): The subcategories and their respective entries.
            texts (list): List of raw entry texts.
            meta (list): List of metadata for each entry.
        
        Returns:
            tuple:
                - list of str: Updated list of texts.
                - list of dict: Updated list of metadata.
        """
        for subcat, entries in subcats.items():
            try:
                texts, meta = self._process_entries(date, main_cat, subcat, entries, texts, meta)
            except (KeyError, TypeError, AttributeError) as e:
                logger.warning("Error processing subcategory '%s' under '%s' on date '%s': %s", subcat, main_cat, date, e, exc_info=True)
        return texts, meta

    def _process_entries(self, date, main_cat, subcat, entries, texts, meta):
        """
        Processes the entries in each subcategory and extracts relevant data.
        
        Args:
            date (str): The date of the entry.
            main_cat (str): The main category of the entries.
            subcat (str): The subcategory of the entries.
            entries (list): List of entries within the subcategory.
            texts (list): List of raw entry texts.
            meta (list): List of metadata for each entry.
        
        Returns:
            tuple:
                - list of str: Updated list of texts.
                - list of dict: Updated list of metadata.
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
                    logger.warning("Missing content in an entry on date %s, category %s, subcategory %s.", date, main_cat, subcat)
            except (KeyError, TypeError, AttributeError) as e:
                logger.error("Error processing an entry in %s → %s → %s: %s", date, main_cat, subcat, e, exc_info=True)
        return texts, meta
