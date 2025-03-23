import os
import pytest
from unittest.mock import patch
from scripts.base_indexer import BaseIndexer
import numpy as np  # import numpy

# Constants for testing using test-specific directories from config.
MOCK_INDEX_PATH = "tests/mock_data/vector_store/test_index.faiss"
MOCK_METADATA_PATH = "tests/mock_data/vector_store/test_metadata.pkl"
MOCK_SUMMARIES_PATH = "tests/mock_data/logs/test_summaries.json"

@pytest.fixture
def base_indexer(tmp_path, monkeypatch):
    # Clean state: Remove existing test files if they exist.
    for path in [MOCK_INDEX_PATH, MOCK_METADATA_PATH, MOCK_SUMMARIES_PATH]:
        p = tmp_path / path
        if p.exists():
            p.unlink()

    # Patch load_config to return test-specific paths.
    monkeypatch.setattr("scripts.config_loader.load_config", lambda config_path=None: {
        "embedding_model": "all-MiniLM-L6-v2",
        "batch_size": 5,
        "raw_log_path": "tests/mock_data/logs/test_raw_log.json",  # For raw log indexer tests
        "raw_log_index_path": "tests/mock_data/vector_store/test_raw_index.faiss",
        "raw_log_metadata_path": "tests/mock_data/vector_store/test_raw_metadata.pkl",
        "correction_summaries_path": MOCK_SUMMARIES_PATH,
        "faiss_index_path": MOCK_INDEX_PATH,
        "faiss_metadata_path": MOCK_METADATA_PATH,
        "logs_dir": "tests/mock_data/logs",
        "export_dir": "tests/mock_data/exports",
        "test_mode": True
    })

    # Patch SentenceTransformer so that it returns predictable (mock) embeddings.
    with patch("scripts.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        # Convert mock output to a numpy array of shape (num_texts, embedding_dim)
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array([[i + 0.1 for i in range(384)] for _ in texts])
        indexer = BaseIndexer(
            summaries_path=MOCK_SUMMARIES_PATH,
            index_path=MOCK_INDEX_PATH,
            metadata_path=MOCK_METADATA_PATH
        )
        yield indexer

def test_build_index_success(base_indexer):
    texts = ["This is a test sentence", "Another idea worth indexing"]
    metadata = [{"id": 1}, {"id": 2}]
    assert base_indexer.build_index(texts, metadata) is True
    assert base_indexer.index is not None
    assert base_indexer.metadata == metadata

def test_build_index_empty_input(base_indexer):
    assert base_indexer.build_index([], []) is False

def test_save_and_load_index(base_indexer, tmp_path):
    texts = ["Zephyrus", "Loop memory fragments"]
    metadata = [{"cat": "a"}, {"cat": "b"}]
    base_indexer.build_index(texts, metadata)
    base_indexer.save_index()

    # Create a new indexer instance for loading.
    from scripts.base_indexer import BaseIndexer
    with patch("scripts.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array([[i + 0.2 for i in range(384)] for _ in texts])
        new_indexer = BaseIndexer(
            summaries_path=MOCK_SUMMARIES_PATH,
            index_path=MOCK_INDEX_PATH,
            metadata_path=MOCK_METADATA_PATH
        )
        new_indexer.load_index()

        assert new_indexer.index is not None
        assert len(new_indexer.metadata) == 2

def test_search_returns_results(base_indexer):
    texts = ["robotic welding detection", "Mechids unlocking loop memory"]
    metadata = [{"tag": "robot"}, {"tag": "mechid"}]
    base_indexer.build_index(texts, metadata)

    results = base_indexer.search("welding", top_k=1)
    assert isinstance(results, list)
    assert results[0]["tag"] == "robot"
    assert "similarity" in results[0]
