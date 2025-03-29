from scripts.utils.file_utils import read_json
from scripts.config.config_loader import get_config_value

# Use the refactored core; ensure the import points to the refactored module.
from scripts.core.core import ZephyrusLoggerCore
import pytest
pytestmark = [pytest.mark.integration]


@pytest.fixture
def logger_core(tmp_path):
    """
    Provides a ZephyrusLoggerCore instance (from the refactored module) in test mode.
    The temporary directory (tmp_path) is used as the script directory.
    """
    # If needed, toggle test mode via your configuration system (or monkeypatch) here.
    # For this example, assume that conftest.py already patches the configuration.
    return ZephyrusLoggerCore(script_dir=tmp_path)

def test_sequential_workflow(logger_core):
    """
    Verifies the full end-to-end workflow:
    1. Log entries to the JSON log file.
    2. Rebuild the summary tracker.
    3. Generate a global summary.
    4. Verify that the correction summaries file is updated.
    """
    date = "2025-03-22"
    ts = f"{date} 12:00:00"
    cat = "SequentialTest"
    sub = "Flow"

    # Log 5 entries.
    for i in range(5):
        logger_core.log_to_json(ts, date, cat, sub, f"Entry {i}")

    # Rebuild summary tracker from the log (simulate tracker initialization).
    logger_core.summary_tracker.rebuild()
    success = logger_core.generate_global_summary(cat, sub)
    assert success, f"Global summarization failed for {cat} → {sub}"

    # Verify that correction summaries file contains the expected summary.
    summaries = read_json(logger_core.paths.correction_summaries_file)
    assert "global" in summaries
    assert cat in summaries["global"]
    assert sub in summaries["global"][cat]

def test_fallback_mechanism(logger_core, monkeypatch):
    """
    Test that when the AI summarization fails, the fallback summary is used.
    """
    class DummySummarizer:
        def summarize_entries_bulk(self, entries, subcategory=None):
            raise Exception("Intentional AI failure")
        def _fallback_summary(self, full_prompt):
            return "Fallback summary used."

    monkeypatch.setattr(logger_core, "ai_summarizer", DummySummarizer())

    date = "2025-03-22"
    ts = f"{date} 10:00:00"
    cat = "FallbackTest"
    sub = "Flow"

    for i in range(5):
        logger_core.log_to_json(ts, date, cat, sub, f"Log {i}")

    logger_core.summary_tracker.rebuild()
    assert logger_core.generate_global_summary(cat, sub), "Fallback summary generation failed"

def test_faiss_index_build_and_search(logger_core):
    """
    Test integration with FAISS index building and searching using generated summaries.
    """
    from scripts.indexers.summary_indexer import SummaryIndexer

    cat = "IntegrationTest"
    sub = "Workflow"
    date = "2025-03-22"
    ts = f"{date} 12:00:00"

    for i in range(5):
        logger_core.log_to_json(ts, date, cat, sub, f"Test entry {i}")

    logger_core.summary_tracker.rebuild()
    success = logger_core.generate_global_summary(cat, sub)
    assert success

    # Build a FAISS index from the generated summaries.
    indexer = SummaryIndexer(
        summaries_path=str(logger_core.paths.correction_summaries_file),
        index_path=get_config_value(logger_core.config, "faiss_index_path", "vector_store/summary_index.faiss"),
        metadata_path=get_config_value(logger_core.config, "faiss_metadata_path", "vector_store/summary_metadata.pkl"),
    )
    texts, metadata = indexer.load_entries()
    assert indexer.build_index(texts, metadata)
    indexer.save_index()
    indexer.load_index()
    results = indexer.search("entry")
    assert isinstance(results, list)
    assert len(results) > 0

def test_raw_log_index_integration(logger_core):
    """
    Tests that the raw log FAISS index is built and searchable based on content.
    """
    from scripts.indexers.raw_log_indexer import RawLogIndexer

    cat = "FAISS"
    sub = "Check"
    date = "2025-03-22"
    ts = f"{date} 12:00:00"

    for i in range(5):
        logger_core.log_to_json(ts, date, cat, sub, f"Indexing log {i}")

    logger_core.summary_tracker.rebuild()
    assert logger_core.generate_global_summary(cat, sub)

    indexer = RawLogIndexer(
        log_path=str(logger_core.paths.json_log_file),
        index_path=get_config_value(logger_core.config, "raw_log_index_path", "vector_store/raw_index.faiss"),
        metadata_path=get_config_value(logger_core.config, "raw_log_metadata_path", "vector_store/raw_metadata.pkl"),
    )
    texts, meta = indexer.load_entries()
    assert indexer.build_index(texts, meta)
    indexer.save_index()
    indexer.load_index()
    results = indexer.search("Indexing")
    assert isinstance(results, list)
    assert len(results) > 0
