# base_indexer.py
import os
import json
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from scripts.config_loader import load_config, get_config_value, get_absolute_path
import logging

logger = logging.getLogger(__name__)

class BaseIndexer:
    def __init__(self, summaries_path, index_path, metadata_path):
        """
        Initializes the BaseIndexer class and sets up paths for summaries, index, and metadata.
        
        Args:
            summaries_path (str): Path to the summaries file.
            index_path (str): Path to the FAISS index file.
            metadata_path (str): Path to the metadata file.
        """
        self.summaries_path = get_absolute_path(summaries_path)
        self.index_path = get_absolute_path(index_path)
        self.metadata_path = get_absolute_path(metadata_path)
        config = load_config()
        model_name = get_config_value(config, "embedding_model", "all-MiniLM-L6-v2")
        self.embedding_model = SentenceTransformer(model_name)
        self.index = None
        self.metadata = []

    def build_index(self, texts, meta):
        """
        Builds a FAISS index from the provided texts and metadata.
        
        Args:
            texts (list of str): The text data to index.
            meta (list of dict): The metadata associated with the texts.
        
        Returns:
            bool: True if the index is successfully built, False if no texts are provided.
        """
        if not texts:
            logger.warning("No texts provided to build FAISS index.")
            return False

        try:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        except Exception as e:
            logger.error("Error generating embeddings: %s", e, exc_info=True)
            return False

        try:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
            self.index.add(embeddings)
            self.metadata = meta
            self.save_index()
        except Exception as e:
            logger.error("Error building FAISS index: %s", e, exc_info=True)
            return False

        return True

    def save_index(self):
        """
        Saves the FAISS index and metadata to their respective files.
        """
        try:
            faiss.write_index(self.index, self.index_path)
        except Exception as e:
            logger.error("Failed to save FAISS index: %s", e, exc_info=True)
            raise

        try:
            with open(self.metadata_path, "wb") as f:
                pickle.dump(self.metadata, f)
        except Exception as e:
            logger.error("Failed to save metadata: %s", e, exc_info=True)
            raise

    def load_index(self):
        """
        Loads the FAISS index and metadata from their respective files.
        
        Raises:
            FileNotFoundError: If the index or metadata file doesn't exist.
        """
        if not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
            error_msg = "FAISS index or metadata file not found."
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            self.index = faiss.read_index(self.index_path)
        except Exception as e:
            logger.error("Failed to read FAISS index: %s", e, exc_info=True)
            raise

        try:
            with open(self.metadata_path, "rb") as f:
                self.metadata = pickle.load(f)
        except Exception as e:
            logger.error("Failed to load metadata: %s", e, exc_info=True)
            raise

    def search(self, query, top_k=5):
        """
        Searches for the most similar entries to a given query using the FAISS index.
        
        Args:
            query (str): The query text to search for in the index.
            top_k (int): The number of top results to return.
        
        Returns:
            list of dict: The top K results with metadata and a similarity score.
        """
        try:
            embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        except Exception as e:
            logger.error("Failed to encode query: %s", e, exc_info=True)
            return []

        try:
            D, I = self.index.search(embedding, top_k)
        except Exception as e:
            logger.error("Search failed: %s", e, exc_info=True)
            return []

        results = []
        for i, idx in enumerate(I[0]):
            if idx < len(self.metadata):
                result = dict(self.metadata[idx])
                # Convert L2 distance to a similarity proxy.
                result["similarity"] = float(1.0 / (1.0 + D[0][i]))
                results.append(result)
            else:
                logger.warning("Index %d out of range for metadata of length %d", idx, len(self.metadata))
        return results

    def build_index_from_logs(self):
        """
        Loads entries using self.load_entries() and builds the FAISS index from them.
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            texts, meta = self.load_entries()
        except AttributeError:
            logger.error("This indexer does not implement a `load_entries()` method.")
            return False

        if not texts:
            logger.warning("No entries found to build index from.")
            return False

        return self.build_index(texts, meta)
