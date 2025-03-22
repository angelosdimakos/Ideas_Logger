from sentence_transformers import SentenceTransformer
import faiss
import json
from pathlib import Path
import pickle

class SummaryIndexer:
    def __init__(self, summaries_path, index_path, metadata_path):
        self.summaries_path = Path(summaries_path)
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
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
        texts, metadata = self.load_summaries()
        if not texts:
            print("❌ No summaries found to index.")
            return False

        print(f"🔍 Indexing {len(texts)} summaries...")

        embeddings = self.model.encode(texts, show_progress_bar=True)
        dimension = embeddings[0].shape[0]

        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        self.metadata = metadata

        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

        print(f"✅ FAISS index saved to {self.index_path}")
        return True

    def load_index(self):
        self.index = faiss.read_index(str(self.index_path))
        with open(self.metadata_path, "rb") as f:
            self.metadata = pickle.load(f)
        print("📦 FAISS index + metadata loaded.")

    def search(self, query, top_k=5):
        if self.index is None or not self.metadata:
            print("⚠️ Load the index first using load_index()")
            return []

        query_vec = self.model.encode([query])
        distances, indices = self.index.search(query_vec, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results