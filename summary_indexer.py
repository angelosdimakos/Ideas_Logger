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
        """Extracts corrected or original summaries with metadata."""
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
                                "batch": batch.get("batch", "N/A"),
                                "timestamp": batch.get("correction_timestamp", "")
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

        self.save_index()
        return True

    def save_index(self):
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"✅ FAISS index saved to {self.index_path}")

    def load_index(self):
        self.index = faiss.read_index(str(self.index_path))
        with open(self.metadata_path, "rb") as f:
            self.metadata = pickle.load(f)
        print("📦 FAISS index + metadata loaded.")

    def search(self, query, top_k=5):
        if self.index is None or not self.metadata:
            print("⚠️ Index not loaded. Call load_index() first.")
            return []

        query_vec = self.model.encode([query])
        distances, indices = self.index.search(query_vec, top_k)

        results = []
        for i, neighbor_idx in enumerate(indices[0]):
            if neighbor_idx < len(self.metadata):
                raw_distance = distances[0][i]
                similarity = 1 / (1 + raw_distance)
                record = self.metadata[neighbor_idx].copy()
                record["similarity"] = round(similarity, 4)
                results.append(record)

        return results

# === Optional Standalone Execution ===
if __name__ == "__main__":
    indexer = SummaryIndexer(
        summaries_path="logs/correction_summaries.json",
        index_path="vector_store/summary_index.faiss",
        metadata_path="vector_store/summary_metadata.pkl"
    )
    indexer.build_index()
