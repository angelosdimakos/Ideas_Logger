from base_indexer import BaseIndexer
import json
from config_loader import load_config, get_config_value, get_absolute_path
import faiss
import numpy as np


class SummaryIndexer(BaseIndexer):
    def __init__(self, summaries_path=None, index_path=None, metadata_path=None):
        config = load_config()
        summaries_path = summaries_path or get_config_value(config, "correction_summaries_path", "logs/correction_summaries.json")
        index_path = index_path or get_config_value(config, "faiss_index_path", "vector_store/summary_index.faiss")
        metadata_path = metadata_path or get_config_value(config, "faiss_metadata_path", "vector_store/summary_metadata.pkl")

        self.summaries_path = get_absolute_path(summaries_path)  # ✅ Must store for later loading
        super().__init__(summaries_path=summaries_path, index_path=index_path, metadata_path=metadata_path)
        self.use_cosine = True

    def load_entries(self):
        with open(self.summaries_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        texts = []
        meta = []

        for date, categories in data.items():
            for main_cat, subcats in categories.items():
                for subcat, batches in subcats.items():
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
