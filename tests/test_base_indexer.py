import pytest
import logging
import numpy as np
from unittest.mock import patch
from scripts.base_indexer import BaseIndexer
from scripts.config_loader import get_config_value,get_effective_config


@pytest.fixture
def base_indexer(temp_dir):

    config = get_effective_config()

    with patch("scripts.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array([[i + 0.1 for i in range(384)] for _ in texts])

        indexer = BaseIndexer(
            summaries_path=get_config_value(config, "correction_summaries_path", temp_dir / "logs" / "correction_summaries.json"),
            index_path=get_config_value(config, "faiss_index_path", temp_dir / "vector_store" / "summary_index.faiss"),
            metadata_path=get_config_value(config, "faiss_metadata_path", temp_dir / "vector_store" / "summary_metadata.pkl")
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

    config = get_effective_config()

    with patch("scripts.base_indexer.SentenceTransformer") as MockModel:
        mock_model = MockModel.return_value
        mock_model.encode.side_effect = lambda texts, **kwargs: np.array([[i + 0.2 for i in range(384)] for _ in texts])

        new_indexer = BaseIndexer(
            summaries_path=get_config_value(config, "correction_summaries_path", None),
            index_path=get_config_value(config, "faiss_index_path", None),
            metadata_path=get_config_value(config, "faiss_metadata_path", None)
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


def test_build_index_failure_due_to_empty_texts(base_indexer, caplog):
    with caplog.at_level(logging.WARNING):
        result = base_indexer.build_index([], [])
        assert result is False
        assert "No texts provided" in caplog.text


def test_save_index_failure(caplog, base_indexer, monkeypatch):
    monkeypatch.setattr("faiss.write_index", lambda index, path: (_ for _ in ()).throw(Exception("Write error")))
    with caplog.at_level(logging.ERROR):
        result = base_indexer.build_index(["Test"], [{"id": 1}])
        assert result is False
        assert "Error building FAISS index" in caplog.text
