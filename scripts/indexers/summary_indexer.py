from scripts.indexers.base_indexer import BaseIndexer
import json
from scripts.config.config_loader import load_config, get_config_value, get_absolute_path
import logging
import os

logger = logging.getLogger(__name__)

class SummaryIndexer(BaseIndexer):
    def __init__(self, summaries_path=None, index_path=None, metadata_path=None):

            """
            Initializes the SummaryIndexer class and sets up paths for summaries, index, and metadata.

            If paths are not provided, they are read from the configuration and resolved
            using get_absolute_path. This ensures that all paths are absolute and correctly
            configured for the indexing and summarization process.

            Args:
                summaries_path (str, optional): Path to the summaries file. Defaults to the path specified in the config.
                index_path (str, optional): Path to the FAISS index file. Defaults to the path specified in the config.
                metadata_path (str, optional): Path to the metadata file. Defaults to the path specified in the config.
            """
            config = load_config()
            # Use the provided paths if given; otherwise, use config values.
            summaries_path = summaries_path or get_config_value(config, "correction_summaries_path", "logs/correction_summaries.json")
            index_path = index_path or get_config_value(config, "faiss_index_path", "vector_store/summary_index.faiss")
            metadata_path = metadata_path or get_config_value(config, "faiss_metadata_path", "vector_store/summary_metadata.pkl")
            
            # Check: if the supplied path is already absolute (or for testing), use it directly.
            # Otherwise, resolve it using get_absolute_path.
            if not os.path.isabs(summaries_path):
                self.summaries_path = get_absolute_path(summaries_path)
            else:
                self.summaries_path = summaries_path

            if not os.path.isabs(index_path):
                self.index_path = get_absolute_path(index_path)
            else:
                self.index_path = index_path

            if not os.path.isabs(metadata_path):
                self.metadata_path = get_absolute_path(metadata_path)
            else:
                self.metadata_path = metadata_path

            super().__init__(summaries_path=self.summaries_path, index_path=self.index_path, metadata_path=self.metadata_path)
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

        texts, meta = [], []
        try:
            for date, categories in data.items():
                texts, meta = self._process_categories(date, categories, texts, meta)
        except Exception as e:
            logger.error("Error processing summary entries: %s", e, exc_info=True)
        return texts, meta

    def _process_categories(self, date, categories, texts, meta):
        """
        Processes categories and their subcategories.
        
        Args:
            date (str): The date of the entries.
            categories (dict): The categories and their subcategories with batches.
            texts (list): The current list of texts.
            meta (list): The current list of metadata.
        
        Returns:
            tuple:
                - list of str: Updated texts.
                - list of dict: Updated metadata.
        """
        for main_cat, subcats in categories.items():
            try:
                texts, meta = self._process_subcategories(date, main_cat, subcats, texts, meta)
            except (KeyError, TypeError, AttributeError) as e:
                logger.warning("Error processing category '%s' on date '%s': %s", main_cat, date, e, exc_info=True)
        return texts, meta

    def _process_subcategories(self, date, main_cat, subcats, texts, meta):
        """
        Processes subcategories and their batches.
        
        Args:
            date (str): The date of the entries.
            main_cat (str): The main category.
            subcats (dict): The subcategories and batches.
            texts (list): The current list of texts.
            meta (list): The current list of metadata.
        
        Returns:
            tuple:
                - list of str: Updated texts.
                - list of dict: Updated metadata.
        """
        for subcat, batches in subcats.items():
            try:
                texts, meta = self._process_batches(date, main_cat, subcat, batches, texts, meta)
            except (KeyError, TypeError, AttributeError) as e:
                logger.warning("Error processing subcategory '%s' under '%s' on date '%s': %s", subcat, main_cat, date, e, exc_info=True)
        return texts, meta

    def _process_batches(self, date, main_cat, subcat, batches, texts, meta):
        """
        Processes batches within a subcategory.
        
        Args:
            date (str): The date of the entries.
            main_cat (str): The main category.
            subcat (str): The subcategory.
            batches (list): The list of batches.
            texts (list): The current list of texts.
            meta (list): The current list of metadata.
        
        Returns:
            tuple:
                - list of str: Updated texts.
                - list of dict: Updated metadata.
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
