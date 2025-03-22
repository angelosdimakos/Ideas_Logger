import os
import json
from config_loader import load_config, get_config_value, get_absolute_path
from base_indexer import BaseIndexer


class RawLogIndexer(BaseIndexer):
    """
    Builds a FAISS index from raw entries in zephyrus_log.json.
    Used for full-text vector search across all logged ideas (not just summaries).
    """

    def __init__(self, log_path=None, index_path=None, metadata_path=None):
        config = load_config()
    
        self.log_path = get_absolute_path(
            log_path or get_config_value(config, "json_log_file", "logs/zephyrus_log.json")
        )
        index_path = index_path or get_config_value(config, "faiss_raw_index_path", "vector_store/raw_index.faiss")
        metadata_path = metadata_path or get_config_value(config, "faiss_raw_metadata_path", "vector_store/raw_metadata.pkl")

        # ✅ Use self.log_path as summaries_path (so base indexer can use it to load)
        super().__init__(summaries_path=self.log_path, index_path=index_path, metadata_path=metadata_path)



    def load_entries(self):
        """Extract all raw entry texts and metadata from zephyrus_log.json."""
        with open(self.log_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        texts = []
        meta = []

        for date, categories in data.items():
            for main_cat, subcats in categories.items():
                for subcat, entries in subcats.items():
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
