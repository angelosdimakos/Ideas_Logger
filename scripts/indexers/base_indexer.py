from typing import List, Dict, Tuple, Any
import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from scripts.config.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)


class BaseIndexer:
    def __init__(self, summaries_path: str, index_path: str, metadata_path: str) -> None:
        """
        Initializes the BaseIndexer class and sets up paths for summaries, index, and metadata.

        Args:
            summaries_path (str): Path to the summaries file.
            index_path (str): Path to the FAISS index file.
            metadata_path (str): Path to the metadata file.
        """
        # Assume provided paths are already absolute (or resolved via ZephyrusPaths)
        self.summaries_path: str = summaries_path
        self.index_path: str = index_path
        self.metadata_path: str = metadata_path

        config = ConfigManager.load_config()
        model_name: str = ConfigManager.get_value("embedding_model", "all-MiniLM-L6-v2")
        self.embedding_model: SentenceTransformer = SentenceTransformer(model_name)
        self.index = None
        self.metadata: List[Dict[str, Any]] = []

    def build_index(self, texts: List[str], meta: List[Dict[str, Any]]) -> bool:
        """
        Builds a FAISS index from the provided texts and metadata.

        Args:
            texts (List[str]): The text data to index.
            meta (List[Dict[str, Any]]): The metadata associated with the texts.

        Returns:
            bool: True if the index is successfully built, False otherwise.
        """
        if not texts:
            logger.warning("No texts provided to build FAISS index.")
            return False

        try:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        except (ValueError, RuntimeError) as e:
            logger.error("Embedding generation failed: %s", e, exc_info=True)
            return False

        try:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
            self.index.add(embeddings)
            self.metadata = meta
        except (TypeError, ValueError, RuntimeError, OSError) as e:
            logger.error("FAISS index creation/addition failed: %s", e, exc_info=True)
            return False

        try:
            self.save_index()
        except Exception as e:
            logger.error("Failed to save FAISS index: %s", e, exc_info=True)
            return False

        return True

    def save_index(self) -> None:
        """
        Saves the FAISS index and metadata to their respective files.

        Raises:
            Exception: If there is an error saving the FAISS index or metadata.
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

    def load_index(self) -> None:
        """
        Loads the FAISS index and associated metadata from their respective files.

        Raises:
            FileNotFoundError: If the FAISS index or metadata file does not exist.
            Exception: If there is an error reading the FAISS index or loading the metadata.
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

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches for the most similar entries to a given query using the FAISS index.

        Args:
            query (str): The query text to search for in the index.
            top_k (int): The number of top results to return.

        Returns:
            List[Dict[str, Any]]: The top K results with metadata and a similarity score.
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

        results: List[Dict[str, Any]] = []
        for i, idx in enumerate(I[0]):
            if idx < len(self.metadata):
                result = dict(self.metadata[idx])
                # Convert L2 distance to a similarity proxy.
                result["similarity"] = float(1.0 / (1.0 + D[0][i]))
                results.append(result)
            else:
                logger.warning("Index %d out of range for metadata of length %d", idx, len(self.metadata))
        return results

    def build_index_from_logs(self) -> bool:
        """
        Loads entries and builds the FAISS index from them.

        Returns:
            bool: True if the index is successfully built from the loaded entries, False otherwise.
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

    def load_entries(self) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Subclasses must override this to load text and metadata for indexing.

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: texts and metadata.
        """
        raise NotImplementedError("Subclasses must implement `load_entries()`.")
