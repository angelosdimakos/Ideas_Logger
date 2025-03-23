from scripts.base_indexer import BaseIndexer
import json
from scripts.config_loader import load_config, get_config_value, get_absolute_path
import faiss
import numpy as np


class SummaryIndexer(BaseIndexer):
    def __init__(self, summaries_path=None, index_path=None, metadata_path=None):
        """
        Initializes the SummaryIndexer class and sets up paths for summaries, index, and metadata.
        
        Args:
            summaries_path (str): Path to the summaries file (default: "logs/correction_summaries.json").
            index_path (str): Path to the FAISS index file (default: "vector_store/summary_index.faiss").
            metadata_path (str): Path to the metadata file (default: "vector_store/summary_metadata.pkl").
        """
        config = load_config()
        summaries_path = summaries_path or get_config_value(config, "correction_summaries_path", "logs/correction_summaries.json")
        index_path = index_path or get_config_value(config, "faiss_index_path", "vector_store/summary_index.faiss")
        metadata_path = metadata_path or get_config_value(config, "faiss_metadata_path", "vector_store/summary_metadata.pkl")

        self.summaries_path = get_absolute_path(summaries_path)  # ✅ Must store for later loading
        super().__init__(summaries_path=summaries_path, index_path=index_path, metadata_path=metadata_path)
        self.use_cosine = True

    def load_entries(self):
        """
        Loads the entries from the correction summaries JSON file.
        
        Reads through the JSON file, extracting the "corrected_summary" or "original_summary" 
        for each batch and creating a list of texts and their corresponding metadata.
        
        Returns:
            tuple: 
                - list of str: Text entries (summaries).
                - list of dict: Metadata associated with each text entry.
        """
        with open(self.summaries_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        texts, meta = [], []

        for date, categories in data.items():
            texts, meta = self._process_categories(date, categories, texts, meta)

        return texts, meta

    def _process_categories(self, date, categories, texts, meta):
        """
        Helper function to process categories and their subcategories.
        
        Args:
            date (str): The date of the entries.
            categories (dict): The categories and subcategories with their batches.
            texts (list): The current list of texts.
            meta (list): The current list of metadata.
        
        Returns:
            tuple:
                - list of str: Updated texts.
                - list of dict: Updated metadata.
        """
        for main_cat, subcats in categories.items():
            texts, meta = self._process_subcategories(date, main_cat, subcats, texts, meta)

        return texts, meta

    def _process_subcategories(self, date, main_cat, subcats, texts, meta):
        """
        Helper function to process subcategories and their batches.
        
        Args:
            date (str): The date of the entries.
            main_cat (str): The main category of the entries.
            subcats (dict): The subcategories with their batches.
            texts (list): The current list of texts.
            meta (list): The current list of metadata.
        
        Returns:
            tuple:
                - list of str: Updated texts.
                - list of dict: Updated metadata.
        """
        for subcat, batches in subcats.items():
            texts, meta = self._process_batches(date, main_cat, subcat, batches, texts, meta)

        return texts, meta

    def _process_batches(self, date, main_cat, subcat, batches, texts, meta):
        """
        Helper function to process batches within a subcategory.
        
        Args:
            date (str): The date of the entries.
            main_cat (str): The main category of the entries.
            subcat (str): The subcategory of the entries.
            batches (list): The list of batches.
            texts (list): The current list of texts.
            meta (list): The current list of metadata.
        
        Returns:
            tuple:
                - list of str: Updated texts.
                - list of dict: Updated metadata.
        """
        for batch in batches:
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

        return texts, meta
