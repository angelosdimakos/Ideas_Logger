import pytest
from scripts.core import ZephyrusLoggerCore
from utils.file_utils import read_json
from tests.test_utils import toggle_test_mode, reset_logger_state
from scripts.config_loader import get_config_value

@pytest.fixture
def logger_core():
    toggle_test_mode(True)
    try:
        logger = ZephyrusLoggerCore(".")
        reset_logger_state(logger)
        yield logger
    finally:
        toggle_test_mode(False)

def test_sequential_workflow(logger_core):
    date = "2025-03-22"
    ts = f"{date} 12:00:00"
    cat = "SequentialTest"
    sub = "Flow"

    for i in range(5):
        logger_core.log_to_json(ts, date, cat, sub, f"Entry {i}")

    logger_core.initialize_summary_tracker_from_log()
    success = logger_core.generate_global_summary(cat, sub)
    assert success, f"Global summarization failed for {cat} → {sub}"

    summaries = read_json(logger_core.correction_summaries_file)
    assert cat in summaries["global"]
    assert sub in summaries["global"][cat]

def test_fallback_mechanism(logger_core, monkeypatch):
    class DummySummarizer:
        def summarize_entries_bulk(self, entries, subcategory=None):
            raise Exception("Intentional AI failure")

        def _fallback_summary(self, full_prompt):
            return "Fallback summary used."

    with monkeypatch.context() as m:
        m.setattr(logger_core, "ai_summarizer", DummySummarizer())

        date = "2025-03-22"
        ts = f"{date} 10:00:00"
        cat = "FallbackTest"
        sub = "Flow"

        for i in range(5):
            logger_core.log_to_json(ts, date, cat, sub, f"Log {i}")

        logger_core.initialize_summary_tracker_from_log()
        assert logger_core.generate_global_summary(cat, sub), "Fallback summary failed"

def test_faiss_index_build_and_search(logger_core):
    from scripts.summary_indexer import SummaryIndexer

    cat = "IntegrationTest"
    sub = "Workflow"
    date = "2025-03-22"
    ts = f"{date} 12:00:00"

    for i in range(5):
        logger_core.log_to_json(ts, date, cat, sub, f"Test entry {i}")

    logger_core.initialize_summary_tracker_from_log()
    success = logger_core.generate_global_summary(cat, sub)
    assert success

    # ✅ Manually build & save index now that summary was generated
    indexer = SummaryIndexer(
        summaries_path=str(logger_core.correction_summaries_file),
        index_path=get_config_value(logger_core.config, "faiss_index_path", "vector_store/summary_index.faiss"),
        metadata_path=get_config_value(logger_core.config, "faiss_metadata_path", "vector_store/summary_metadata.pkl"),
    )
    texts, metadata = indexer.load_entries()
    assert indexer.build_index(texts, metadata)
    indexer.save_index()

    # ✅ Now test that load/search work as expected
    indexer.load_index()
    results = indexer.search("entry")
    assert isinstance(results, list)
    assert len(results) > 0


def test_raw_log_index_integration(logger_core):
    from scripts.raw_log_indexer import RawLogIndexer

    cat = "FAISS"
    sub = "Check"
    date = "2025-03-22"
    ts = f"{date} 12:00:00"

    for i in range(5):
        logger_core.log_to_json(ts, date, cat, sub, f"Indexing log {i}")

    logger_core.initialize_summary_tracker_from_log()
    assert logger_core.generate_global_summary(cat, sub)

    # ✅ Correct indexing logic
    indexer = RawLogIndexer(
        log_path=str(logger_core.json_log_file),
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

