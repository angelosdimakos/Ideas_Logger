import pytest
import numpy as np
from scripts.base_indexer import BaseIndexer
from scripts.config_loader import get_effective_config, get_config_value
from tests.test_utils import make_raw_indexer

def test_build_index_success():
    indexer = make_raw_indexer()
    texts = ["This is a test sentence", "Another idea worth indexing"]
    metadata = [{"id": 1}, {"id": 2}]
    assert indexer.build_index(texts, metadata) is True
    assert indexer.index is not None
    assert indexer.metadata == metadata

def test_build_index_empty_input():
    indexer = make_raw_indexer()
    assert indexer.build_index([], []) is False

def test_save_and_load_index():
    indexer = make_raw_indexer()
    texts = ["Zephyrus", "Loop memory fragments"]
    metadata = [{"cat": "a"}, {"cat": "b"}]
    indexer.build_index(texts, metadata)
    indexer.save_index()

    new_indexer = make_raw_indexer(embedding_offset=0.2)
    new_indexer.load_index()

    assert new_indexer.index is not None
    assert len(new_indexer.metadata) == 2


def test_search_returns_results():
    indexer = make_raw_indexer()
    texts = ["robotic welding detection", "Mechids unlocking loop memory"]
    metadata = [{"tag": "robot"}, {"tag": "mechid"}]
    indexer.build_index(texts, metadata)

    results = indexer.search("welding", top_k=1)
    assert isinstance(results, list)
    assert results[0]["tag"] == "robot"
    assert "similarity" in results[0]
