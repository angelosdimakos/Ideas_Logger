import os
import json
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from config_loader import load_config, get_config_value, get_absolute_path


class SummaryIndexer:
    def __init__(self, summaries_path=None, index_path=None, metadata_path=None):
        config = load_config()
        self.summaries_path = get_absolute_path(summaries_path or get_config_value(config, "correction_summaries_path", "logs/correction_summaries.json"))
        self.index_path = get_absolute_path(index_path or get_config_value(config, "faiss_index_path", "vector_store/summary_index.faiss"))
        self.metadata_path = get_absolute_path(metadata_path or get_config_value(config, "faiss_metadata_path", "vector_store/summary_metadata.pkl"))

        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.metadata = []

    def load_summaries(self):
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

    def build_index(self):
        try:
            texts, meta = self.load_summaries()
            if not texts:
                print("[FAISS] No summaries to index.")
                return False

            embeddings = self.model.encode(texts, convert_to_numpy=True)
            faiss.normalize_L2(embeddings)
            index = faiss.IndexFlatIP(embeddings.shape[1])
            index.add(embeddings)

            with open(self.metadata_path, "wb") as f:
                pickle.dump(meta, f)

            faiss.write_index(index, self.index_path)
            print(f"[FAISS] Index built with {len(texts)} entries.")
            return True
        except Exception as e:
            print(f"[FAISS] Failed to build index: {e}")
            return False

    def load_index(self):
        if not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
            raise FileNotFoundError("Index or metadata not found. Please build the index first.")
        self.index = faiss.read_index(self.index_path)
        with open(self.metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

    def search(self, query, top_k=5):
        if self.index is None:
            self.load_index()
        query_vec = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_vec)
        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result["similarity"] = float(score)
                results.append(result)
        return results
