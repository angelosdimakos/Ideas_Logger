import os
import pytest
from unittest.mock import patch, MagicMock
from scripts.base_indexer import BaseIndexer

# Constants for testing
MOCK_INDEX_PATH = "tests/mock_data/exports/test_index"
MOCK_METADATA_PATH = "tests/mock_data/exports/test_metadata.pkl"

@pytest.fixture
def base_indexer():
    # Clean state
    if os.path.exists(MOCK_INDEX_PATH):
        os.remove(MOCK_INDEX_PATH)
    if os.path.exists(MOCK_METADATA_PATH):
        os.remove(MOCK_METADATA_PATH)

    with patch("scripts.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts: [[i + 0.1 for i in range(384)] for _ in texts]

        indexer = BaseIndexer(
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

def test_save_and_load_index(base_indexer):
    texts = ["Zephyrus", "Loop memory fragments"]
    metadata = [{"cat": "a"}, {"cat": "b"}]
    base_indexer.build_index(texts, metadata)
    base_indexer.save_index()

    with patch("scripts.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts: [[i + 0.2 for i in range(384)] for _ in texts]

        new_indexer = BaseIndexer(
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
