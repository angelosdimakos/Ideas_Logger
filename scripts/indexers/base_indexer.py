from typing import List, Dict, Tuple, Any
import os, pickle, faiss
from sentence_transformers import SentenceTransformer
from scripts.config.config_loader import get_config_value
from scripts.config.config_manager import ConfigManager
import logging
from scripts.paths import ZephyrusPaths

logger = logging.getLogger(__name__)


class BaseIndexer:
    def __init__(self, paths: ZephyrusPaths, index_name: str) -> None:
        """
        Initializes the BaseIndexer using ZephyrusPaths.
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
        self.embedding_model: SentenceTransformer = SentenceTransformer(model_name)
        self.index = None
        self.metadata: List[Dict[str, Any]] = []

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
