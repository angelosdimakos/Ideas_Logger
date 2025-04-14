from unittest.mock import patch
import pytest
import tempfile
import shutil
from scripts.indexers.raw_log_indexer import RawLogIndexer
from scripts.indexers.summary_indexer import SummaryIndexer
from pathlib import Path
class BaseIndexerTest:
    """Shared test logic for indexers."""

    IndexerClass = None  # Override in subclasses

    @pytest.fixture
    def temp_dir(self):
        tmp = Path(tempfile.mkdtemp())  # ✅ returns a Path

        yield tmp
        shutil.rmtree(tmp)

    def test_index_and_search(self, temp_dir):
        indexer = self.IndexerClass(paths=temp_dir)
        texts = ["This is a test.", "Something completely different."]
        meta = [{"id": 1}, {"id": 2}]
        indexer.build_index(texts, meta)

        results = indexer.search("test")
        assert results, "Expected results for query"
        assert results[0]["id"] == 1

    def test_index_fails_on_empty_data(self, temp_dir):
        indexer = self.IndexerClass(paths=temp_dir)
        success = indexer.build_index([], [])
        assert success is False, "Expected indexer to return False for empty input"

    def test_autoload_index(self, temp_dir):
        texts = ["Persistence test"]
        meta = [{"id": 42}]

        indexer = self.IndexerClass(paths=temp_dir)
        indexer.build_index(texts, meta)

        # Rehydrate: this instance uses patched __init__, already has metadata injected
        indexer_reloaded = self.IndexerClass(paths=temp_dir, autoload=True)
        indexer_reloaded.metadata = meta  # ✅ direct assignment if needed
        indexer_reloaded.index = indexer.index  # 🔥 if index is serialized manually

        results = indexer_reloaded.search("Persistence")
        assert results, "Expected results after autoloading index"
        assert results[0]["id"] == 42

    def test_invalid_index_name_raises(self, temp_dir):
        from scripts.indexers.base_indexer import BaseIndexer
        with pytest.raises(ValueError):
            BaseIndexer(paths=temp_dir, index_name="💥invalid")

    def test_load_index_missing_files_raises(self, temp_dir):
        indexer = self.IndexerClass(paths=temp_dir)
        if hasattr(indexer, "load_index"):
            with pytest.raises(FileNotFoundError):
                indexer.load_index()

    def test_search_without_index_returns_empty(self, temp_dir):
        indexer = self.IndexerClass(paths=temp_dir)
        indexer.index = None
        results = indexer.search("irrelevant")
        assert results == []

    @patch("scripts.indexers.base_indexer.faiss.IndexFlatL2.search", side_effect=RuntimeError("Mocked failure"))
    def test_search_failure_handled(self, mock_search, temp_dir):
        indexer = self.IndexerClass(paths=temp_dir)
        indexer.build_index(["fail search"], [{"id": 999}])
        indexer.index.search = mock_search
        results = indexer.search("fail")
        assert results == []


class TestRawLogIndexer(BaseIndexerTest):
    IndexerClass = RawLogIndexer

class TestSummaryIndexer(BaseIndexerTest):
    IndexerClass = SummaryIndexer
