from tests.mocks.test_utils import make_raw_indexer
import pytest
pytestmark = [pytest.mark.unit, pytest.mark.indexing]


def test_build_index_success():
    """
    Tests that `RawLogIndexer.build_index` successfully builds an index with
    the provided texts and metadata.
    """
    indexer = make_raw_indexer()
    texts = ["This is a test sentence", "Another idea worth indexing"]
    metadata = [{"id": 1}, {"id": 2}]
    assert indexer.build_index(texts, metadata) is True
    assert indexer.index is not None
    assert indexer.metadata == metadata
    indexer = make_raw_indexer()
    texts = ["This is a test sentence", "Another idea worth indexing"]
    metadata = [{"id": 1}, {"id": 2}]
    assert indexer.build_index(texts, metadata) is True
    assert indexer.index is not None
    assert indexer.metadata == metadata

def test_build_index_empty_input():
    """
    Tests that `RawLogIndexer.build_index` handles empty text and metadata inputs
    and returns False as expected.
    """
    indexer = make_raw_indexer()
    assert indexer.build_index([], []) is False
    indexer = make_raw_indexer()
    assert indexer.build_index([], []) is False

def test_save_and_load_index():
    """
    Tests that `RawLogIndexer.save_index` saves the index and metadata, and
    that `RawLogIndexer.load_index` successfully loads the saved index and
    metadata.
    """
    indexer = make_raw_indexer()
    texts = ["Zephyrus", "Loop memory fragments"]
    metadata = [{"cat": "a"}, {"cat": "b"}]
    indexer.build_index(texts, metadata)
    indexer.save_index()

    new_indexer = make_raw_indexer(embedding_offset=0.2)
    new_indexer.load_index()

    assert new_indexer.index is not None
    assert len(new_indexer.metadata) == 2
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
    """
    Tests that `RawLogIndexer.search` returns the most similar logs entries to
    a query and that the returned results contain the metadata and a
    similarity score.
    """
    indexer = make_raw_indexer()
    texts = ["robotic welding detection", "Mechids unlocking loop memory"]
    metadata = [{"tag": "robot"}, {"tag": "mechid"}]
    indexer.build_index(texts, metadata)

    results = indexer.search("welding", top_k=1)
    assert isinstance(results, list)
    assert results[0]["tag"] == "robot"
    assert "similarity" in results[0]
    indexer = make_raw_indexer()
    texts = ["robotic welding detection", "Mechids unlocking loop memory"]
    metadata = [{"tag": "robot"}, {"tag": "mechid"}]
    indexer.build_index(texts, metadata)

    results = indexer.search("welding", top_k=1)
    assert isinstance(results, list)
    assert results[0]["tag"] == "robot"
    assert "similarity" in results[0]
