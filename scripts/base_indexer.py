# === base_indexer.py ===
import os
import json
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from config_loader import load_config,get_config_value, get_absolute_path

class BaseIndexer:
    def __init__(self, summaries_path, index_path, metadata_path):
        self.summaries_path = get_absolute_path(summaries_path)
        self.index_path = get_absolute_path(index_path)
        self.metadata_path = get_absolute_path(metadata_path)
        config = load_config()
        model_name = get_config_value(config, "embedding_model", "all-MiniLM-L6-v2")
        self.embedding_model = SentenceTransformer(model_name)
        self.index = None
        self.metadata = []

    def build_index(self, texts, meta):
        if not texts:
            print("[WARNING] No texts provided to build FAISS index.")
            return False

        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)
        self.metadata = meta
        self.save_index()
        return True

    def save_index(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def load_index(self):
        if not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
            raise FileNotFoundError("FAISS index or metadata file not found.")

        self.index = faiss.read_index(self.index_path)
        with open(self.metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

    def search(self, query, top_k=5):
        embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        D, I = self.index.search(embedding, top_k)
        results = []
        for i, idx in enumerate(I[0]):
            if idx < len(self.metadata):
                result = dict(self.metadata[idx])
                result["similarity"] = float(1.0 / (1.0 + D[0][i]))  # Convert L2 distance to similarity proxy
                results.append(result)
        return results
