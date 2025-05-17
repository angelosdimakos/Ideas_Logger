"""
base_indexer.py

This module defines the BaseIndexer class, which provides core functionality for building, saving, loading, and searching FAISS vector indexes over log and summary data.

Core features include:
- Initializing index and metadata paths based on project configuration and index type (summary or raw).
- Building a FAISS index from text data using SentenceTransformer embeddings.
- Saving and loading both the FAISS index and associated metadata.
- Performing semantic search over indexed data, returning the most relevant results with similarity scores.
- Supporting flexible configuration and robust error handling for index operations.

Intended for use as a base class for specialized indexers in the Zephyrus project, enabling fast and flexible semantic search over structured logs and summaries.
"""

from typing import List, Dict, Any
import pickle
import faiss
from scripts.config.config_loader import get_config_value
from scripts.config.config_manager import ConfigManager
import logging
from scripts.paths import ZephyrusPaths

logger = logging.getLogger(__name__)


class BaseIndexer:
    def __init__(self, paths: ZephyrusPaths, index_name: str) -> None:
        """
        Initializes the BaseIndexer object.

        Sets the paths to the summaries file, FAISS index file, and metadata file based on the
        provided `index_name` and the `ZephyrusPaths` object.  If `index_name` is "summary",
        the paths are set to the correction summaries file, FAISS index file, and metadata file.
        If `index_name` is "raw", the paths are set to the JSON log file, raw log index file,
        and raw log metadata file.  In all other cases, a ValueError is raised.

        Also, loads the SentenceTransformer model specified by the "embedding_model"
        configuration key, or defaults to "all-MiniLM-L6-v2" if the key is missing.

        Args:
            paths (ZephyrusPaths): The paths configuration for the indexer.
            index_name (str): The name of the index to create, either "summary" or "raw".
        Raises:
            ValueError: If `index_name` is not "summary" or "raw".
        """

        if index_name == "summary":
            self.summaries_path = paths.correction_summaries_file
            self.index_path = paths.faiss_index_path
            self.metadata_path = paths.faiss_metadata_path
        elif index_name == "raw":
            self.summaries_path = paths.json_log_file
            self.index_path = paths.raw_log_index_path
            self.metadata_path = paths.raw_log_metadata_path
        else:
            raise ValueError(f"Unsupported index_name: {index_name}")

        model_name = get_config_value(
            ConfigManager.load_config(), "embedding_model", "all-MiniLM-L6-v2"
        )
        self.embedding_model = self._load_model()
        self.index = None
        self.metadata: List[Dict[str, Any]] = []

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("sentence-transformers is not installed.")

        model_name = get_config_value(
            ConfigManager.load_config(), "embedding_model", "all-MiniLM-L6-v2"
        )
        return SentenceTransformer(model_name)

    def load_index(self) -> None:
        """
        Loads the FAISS index and associated metadata from their respective files.

        This method reads the index from the file specified by `self.index_path` and loads
        the metadata from the file specified by `self.metadata_path`. If either file does not
        exist, a FileNotFoundError is raised.

        Raises:
            FileNotFoundError: If the index file or metadata file is not found.
        """
        if not self.index_path.exists() or not self.metadata_path.exists():
            raise FileNotFoundError("FAISS index or metadata file not found.")
        self.index = faiss.read_index(str(self.index_path))
        with open(self.metadata_path, "rb") as f:
            self.metadata = pickle.load(f)
        if not self.index_path.exists() or not self.metadata_path.exists():
            raise FileNotFoundError("FAISS index or metadata file not found.")
        self.index = faiss.read_index(str(self.index_path))
        with open(self.metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches the FAISS index for the given query and returns the top-k most relevant results.

        Args:
            query (str): The search query.
            top_k (int, optional): The number of top results to return. Defaults to 5.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the search results. Each dictionary includes the
            following keys:

            - "date"
            - "main_category"
            - "subcategory"
            - "timestamp"
            - "similarity" (the similarity score, computed as 1.0 / (1.0 + distance))
        """
        if self.index is None:
            logger.error("Search attempted before index was loaded!")
            return []

        try:
            embedding = self.embedding_model.encode([query], convert_to_numpy=True)
            D, I = self.index.search(embedding, top_k)
        except Exception as e:
            logger.error("Search failed: %s", e, exc_info=True)
            return []

        results = []
        for i, idx in enumerate(I[0]):
            if idx < len(self.metadata):
                result = dict(self.metadata[int(idx)])
                result["similarity"] = float(1.0 / (1.0 + D[0][i]))
                results.append(result)
        return results

    def build_index(
        self, texts: List[str], meta: List[Dict[str, Any]], fail_on_empty: bool = False
    ) -> bool:
        """
        Builds a FAISS index from provided texts and metadata.

        Args:
            texts (List[str]): A list of texts to encode and index.
            meta (List[Dict[str, Any]]): Metadata per text entry.
            fail_on_empty (bool): Raise ValueError if input is empty (useful for tests).

        Returns:
            bool: True if successful, False otherwise.
        """
        if not texts:
            logger.warning("No data to build index.")
            if fail_on_empty:
                raise ValueError("Cannot build index with empty data.")
            return False

        try:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
            self.index.add(embeddings)
            self.metadata = meta
            self.save_index()
            return True
        except Exception as e:
            logger.error("Failed to build index: %s", e, exc_info=True)
            return False

    def save_index(self) -> None:
        """
        Saves the FAISS index to a file, and the associated metadata.

        This method must be called after `build_index` or `load_index` has been called.
        """
        # Ensure parent directory exists
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)
