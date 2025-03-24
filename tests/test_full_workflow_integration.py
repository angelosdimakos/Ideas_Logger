import pytest
from scripts.core import ZephyrusLoggerCore


def reset_logger_state(logger_core):
    for path in [
        logger_core.json_log_file,
        logger_core.summary_tracker_file,
        logger_core.correction_summaries_file
    ]:
        if path.exists():
            path.write_text("{}", encoding="utf-8")

def test_sequential_workflow(logger_core):
    reset_logger_state(logger_core)
    date = "2025-03-22"
    ts = f"{date} 12:00:00"
    cat = "SequentialTest"
    sub = "Flow"

    for i in range(5):
        logger_core.log_to_json(ts, date, cat, sub, f"Entry {i}")

    # Ensure tracker rebuilt properly
    logger_core.initialize_summary_tracker_from_log()

    success = logger_core.generate_global_summary(cat, sub)
    assert success, f"Global summarization failed for {cat} → {sub}"


def test_fallback_mechanism(logger_core, monkeypatch):
    reset_logger_state(logger_core)

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
    reset_logger_state(logger_core)

    main_category = "IntegrationTest"
    subcategory = "Workflow"
    date = "2025-03-22"
    timestamp = f"{date} 12:00:00"

    for i in range(5):
        logger_core.log_to_json(timestamp, date, main_category, subcategory, f"Test entry {i}")

    logger_core.initialize_summary_tracker_from_log()
    success = logger_core.generate_global_summary(main_category, subcategory)
    assert success, "Global summarization did not succeed for FAISS workflow test"


def test_raw_log_index_integration(logger_core):
    reset_logger_state(logger_core)

    main_category = "FAISS"
    subcategory = "Check"
    date = "2025-03-22"
    timestamp = date + " 12:00:00"

    for i in range(5):
        logger_core.log_to_json(timestamp, date, main_category, subcategory, f"Indexing log {i}")

    logger_core.initialize_summary_tracker_from_log()
    result = logger_core.generate_global_summary(main_category, subcategory)
    assert result, f"Raw log index integration summary failed for {main_category} → {subcategory}"
