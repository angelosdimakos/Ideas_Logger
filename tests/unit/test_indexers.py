import pytest
from scripts.indexers.raw_log_indexer import RawLogIndexer
from scripts.indexers.summary_indexer import SummaryIndexer
from scripts.paths import ZephyrusPaths

# === Shared base for indexer tests ===
class BaseIndexerTest:
    indexer_class = None  # Must be overridden
    index_name = ""       # "raw" or "summary"

    @pytest.fixture(autouse=True)
    def _setup(self, temp_dir, patch_config_and_paths):
        self.paths = ZephyrusPaths.from_config(temp_dir)
        self.indexer = self.indexer_class(paths=self.paths, autoload=False)

    def test_can_load_entries(self):
        texts, meta = self.indexer.load_entries()
        assert isinstance(texts, list)
        assert isinstance(meta, list)
        assert len(texts) > 0, "No entries were loaded for indexing"
        assert len(meta) == len(texts), "Metadata and text lengths mismatch"

    def test_can_build_index(self):
        texts, meta = self.indexer.load_entries()
        success = self.indexer.build_index(texts, meta)
        assert success is True, f"{self.index_name} index build failed"

    def test_can_save_and_load_index(self):
        texts, meta = self.indexer.load_entries()
        self.indexer.build_index(texts, meta)
        self.indexer.save_index()

        # Load again to verify
        self.indexer.load_index()
        assert self.indexer.index is not None, "Index was not reloaded"
        assert isinstance(self.indexer.metadata, list)

    def test_can_search_index(self):
        texts, meta = self.indexer.load_entries()
        self.indexer.build_index(texts, meta)
        self.indexer.save_index()
        self.indexer.load_index()
        results = self.indexer.search("test")
        assert isinstance(results, list)
        assert len(results) > 0, f"{self.index_name} search returned no results"

# === SummaryIndexer Tests ===
class TestSummaryIndexer(BaseIndexerTest):
    indexer_class = SummaryIndexer
    index_name = "summary"

# === RawLogIndexer Tests ===
class TestRawLogIndexer(BaseIndexerTest):
    indexer_class = RawLogIndexer
    index_name = "raw"
