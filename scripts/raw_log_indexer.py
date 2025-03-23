import os
import json
from scripts.config_loader import load_config, get_config_value, get_absolute_path
from scripts.base_indexer import BaseIndexer


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
    
        self.log_path = get_absolute_path(
            log_path or get_config_value(config, "raw_log_path", "logs/zephyrus_log.json")
        )
        index_path = index_path or get_config_value(config, "raw_log_index_path", "vector_store/raw_index.faiss")
        metadata_path = metadata_path or get_config_value(config, "raw_log_metadata_path", "vector_store/raw_metadata.pkl")


        # ✅ Use self.log_path as summaries_path (so base indexer can use it to load)
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
        with open(self.log_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        texts, meta = [], []

        for date, categories in data.items():
            texts, meta = self._process_categories(date, categories, texts, meta)

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
            texts, meta = self._process_subcategories(date, main_cat, subcats, texts, meta)

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
            texts, meta = self._process_entries(date, main_cat, subcat, entries, texts, meta)

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
        return texts, meta
