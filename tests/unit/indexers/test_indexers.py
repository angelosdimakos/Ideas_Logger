from unittest.mock import patch
import pytest
import tempfile
import shutil
import json
from pathlib import Path
import faiss

from scripts.indexers.raw_log_indexer import RawLogIndexer
from scripts.indexers.summary_indexer import SummaryIndexer
from tests.mocks.test_utils import (
    make_raw_indexer,
    make_summary_indexer,
    make_fake_logs,
    make_fake_paths,
)


class BaseIndexerTest:
    """Shared test logic for indexers."""
    IndexerClass = None

    @pytest.fixture
    def temp_dir(self):
        tmp = Path(tempfile.mkdtemp())
        yield tmp
        shutil.rmtree(tmp)

    def test_index_and_search(self, temp_dir):
        paths = make_fake_paths(temp_dir)
        indexer = self.IndexerClass(paths=paths)
        texts = ["This is a test.", "Something completely different."]
        meta = [{"id": 1}, {"id": 2}]
        indexer.build_index(texts, meta)
        results = indexer.search("test")
        assert results
        assert results[0]["id"] == 1

    def test_index_fails_on_empty_data(self, temp_dir):
        paths = make_fake_paths(temp_dir)
        indexer = self.IndexerClass(paths=paths)
        success = indexer.build_index([], [])
        assert success is False

    def test_autoload_index(self, temp_dir):
        texts = ["Persistence test"]
        meta = [{"id": 42}]
        paths = make_fake_paths(temp_dir)

        indexer = self.IndexerClass(paths=paths)
        indexer.build_index(texts, meta)

        reloaded = self.IndexerClass(paths=paths, autoload=True)
        reloaded.metadata = meta
        reloaded.index = indexer.index

        results = reloaded.search("Persistence")
        assert results
        assert results[0]["id"] == 42

    def test_invalid_index_name_raises(self, temp_dir):
        from scripts.indexers.base_indexer import BaseIndexer
        with pytest.raises(ValueError):
            BaseIndexer(paths=make_fake_paths(temp_dir), index_name="💥invalid")

    def test_load_index_missing_files_raises(self, temp_dir):
        indexer = self.IndexerClass(paths=make_fake_paths(temp_dir))
        if hasattr(indexer, "load_index"):
            with pytest.raises(FileNotFoundError):
                indexer.load_index()

    def test_search_without_index_returns_empty(self, temp_dir):
        indexer = self.IndexerClass(paths=make_fake_paths(temp_dir))
        indexer.index = None
        results = indexer.search("irrelevant")
        assert results == []

    @patch("scripts.indexers.base_indexer.faiss.IndexFlatL2.search", side_effect=RuntimeError("Mocked failure"))
    def test_search_failure_handled(self, mock_search, temp_dir):
        indexer = self.IndexerClass(paths=make_fake_paths(temp_dir))
        indexer.build_index(["fail search"], [{"id": 999}])
        indexer.index.search = mock_search
        results = indexer.search("fail")
        assert results == []

    def test_base_indexer_save_fail(self, monkeypatch, temp_dir):
        from scripts.indexers.base_indexer import BaseIndexer

        paths = make_fake_paths(temp_dir)
        indexer = BaseIndexer(paths=paths, index_name="summary")
        indexer.index = faiss.IndexFlatL2(384)
        indexer.metadata = []

        monkeypatch.setattr("faiss.write_index", lambda *a, **k: (_ for _ in ()).throw(OSError("fail")))
        with pytest.raises(OSError):
            indexer.save_index()


class TestRawLogIndexer(BaseIndexerTest):
    IndexerClass = RawLogIndexer


class TestSummaryIndexer(BaseIndexerTest):
    IndexerClass = SummaryIndexer


# ----------------- Edge & Integration -----------------

def test_raw_indexer_build_index_from_logs_success(mock_raw_log_file, temp_dir):
    logs = make_fake_logs("2024-01-01", "Ideas", "General", 3)
    mock_raw_log_file.write_text(json.dumps(logs), encoding="utf-8")
    paths = make_fake_paths(temp_dir)
    indexer = make_raw_indexer(paths)
    assert indexer.build_index_from_logs() is True
    results = indexer.search("idea")
    assert results
    assert all("date" in r and "main_category" in r for r in results)

def test_summary_indexer_build_index_from_logs_success(mock_correction_summaries_file, temp_dir):
    summaries = {
        "2024-01-01": {
            "Ideas": {
                "General": [
                    {"corrected_summary": "A summary about AI.", "batch": 1, "correction_timestamp": "2024-01-01T12:00:00"}
                ]
            }
        }
    }
    mock_correction_summaries_file.write_text(json.dumps(summaries), encoding="utf-8")
    paths = make_fake_paths(temp_dir)
    indexer = make_summary_indexer(paths)
    assert indexer.build_index_from_logs() is True
    results = indexer.search("AI")
    assert results
    assert all("date" in r and "main_category" in r and "batch" in r for r in results)

def test_raw_indexer_handles_corrupted_log_file(mock_raw_log_file, temp_dir):
    mock_raw_log_file.write_text("{ this is not valid json }", encoding="utf-8")
    paths = make_fake_paths(temp_dir)
    indexer = make_raw_indexer(paths)
    assert indexer.build_index_from_logs() is False

def test_raw_indexer_handles_missing_content(mock_raw_log_file, temp_dir):
    logs = {
        "2024-01-01": {
            "Ideas": {
                "General": [
                    {"timestamp": "2024-01-01T12:00:00"}
                ]
            }
        }
    }
    mock_raw_log_file.write_text(json.dumps(logs), encoding="utf-8")
    paths = make_fake_paths(temp_dir)
    indexer = make_raw_indexer(paths)
    assert indexer.build_index_from_logs() is False

def test_summary_indexer_metadata_persistence(mock_correction_summaries_file, temp_dir):
    summaries = {
        "2024-01-01": {
            "Ideas": {
                "General": [
                    {"corrected_summary": "Persistent summary.", "batch": 1, "correction_timestamp": "2024-01-01T12:00:00"}
                ]
            }
        }
    }
    mock_correction_summaries_file.write_text(json.dumps(summaries), encoding="utf-8")
    paths = make_fake_paths(temp_dir)
    indexer = make_summary_indexer(paths)
    indexer.build_index_from_logs()
    reloaded = make_summary_indexer(paths)
    reloaded.load_index()
    assert reloaded.metadata == indexer.metadata

def test_raw_indexer_search_top_k(mock_raw_log_file, temp_dir):
    logs = make_fake_logs("2024-01-01", "Ideas", "General", 10)
    mock_raw_log_file.write_text(json.dumps(logs), encoding="utf-8")
    paths = make_fake_paths(temp_dir)
    indexer = make_raw_indexer(paths)
    indexer.build_index_from_logs()
    results = indexer.search("idea", top_k=3)
    assert len(results) == 3

@pytest.mark.parametrize("top_k", [1, 5, 20])
def test_summary_indexer_search_various_top_k(mock_correction_summaries_file, temp_dir, top_k):
    summaries = {
        "2024-01-01": {
            "Ideas": {
                "General": [
                    {
                        "corrected_summary": f"Summary {i}",
                        "batch": i,
                        "correction_timestamp": f"2024-01-01T12:00:{i:02d}"
                    }
                    for i in range(10)
                ]
            }
        }
    }
    mock_correction_summaries_file.write_text(json.dumps(summaries), encoding="utf-8")
    paths = make_fake_paths(temp_dir)
    indexer = make_summary_indexer(paths)
    indexer.build_index_from_logs()
    results = indexer.search("Summary", top_k=top_k)
    assert len(results) <= top_k

def test_summary_indexer_handles_missing_file(temp_dir):
    from scripts.indexers.summary_indexer import SummaryIndexer
    from scripts.paths import ZephyrusPaths

    # Ensure the file does NOT exist
    missing_path = temp_dir / "logs" / "correction_summaries.json"
    if missing_path.exists():
        missing_path.unlink()

    paths = ZephyrusPaths.from_config(temp_dir)
    paths.correction_summaries_file = missing_path

    indexer = SummaryIndexer(paths, autoload=False)
    texts, meta = indexer.load_entries()
    assert texts == []
    assert meta == []

def test_summary_indexer_handles_corrupt_json(mock_correction_summaries_file):
    mock_correction_summaries_file.write_text("{ not valid json", encoding="utf-8")
    from scripts.indexers.summary_indexer import SummaryIndexer
    from scripts.paths import ZephyrusPaths

    paths = ZephyrusPaths.from_config(mock_correction_summaries_file.parent.parent)
    paths.correction_summaries_file = mock_correction_summaries_file
    indexer = SummaryIndexer(paths, autoload=False)
    texts, meta = indexer.load_entries()
    assert texts == []
    assert meta == []
