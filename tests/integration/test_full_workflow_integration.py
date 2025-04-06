import pytest
from scripts.utils.file_utils import read_json


def test_sequential_workflow(logger_core):
    cat, sub = "SequentialTest", "Flow"
    # Log enough entries to trigger a summary generation.
    for i in range(5):
        logger_core.log_new_entry(cat, sub, f"Sequential message {i + 1}")
    logger_core.generate_global_summary(cat, sub)

    data = read_json(logger_core.paths.summary_tracker_file)
    # Verify that the tracker has our category and subcategory.
    assert cat in data, f"Category {cat} not found in summary tracker."
    assert sub in data[cat], f"Subcategory {sub} not found in summary tracker for {cat}."
    # Check that the summaries were generated.
    assert data[cat][sub].get("summarized_total", 0) > 0, f"No summaries generated for {cat} → {sub}."


def test_fallback_mechanism(logger_core, monkeypatch):
    def fail_bulk_summary(*args, **kwargs):
        raise Exception("Simulated failure")

    # Force bulk summarization to fail.
    logger_core.ai_summarizer.summarize_entries_bulk = fail_bulk_summary
    # Patch individual summarization to return a fallback summary.
    monkeypatch.setattr(
        logger_core.ai_summarizer,
        "summarize_entry",
        lambda entry: f"Fallback summary for: {entry['content']}"
    )
    cat, sub = "FallbackTest", "Flow"
    for i in range(5):
        logger_core.log_new_entry(cat, sub, f"Fallback test message {i + 1}")
    logger_core.generate_global_summary(cat, sub)

    data = read_json(logger_core.paths.summary_tracker_file)
    assert cat in data, f"Category {cat} not found in summary tracker (fallback)."
    assert sub in data[cat], f"Subcategory {sub} not found in summary tracker (fallback)."
    assert data[cat][sub].get("summarized_total", 0) > 0, f"No fallback summaries generated for {cat} → {sub}."


def test_faiss_index_build_and_search(logger_core):
    cat, sub = "IntegrationTest", "Workflow"
    for i in range(5):
        logger_core.log_new_entry(cat, sub, f"Index test message {i + 1}")
    logger_core.generate_global_summary(cat, sub)

    data = read_json(logger_core.paths.summary_tracker_file)
    assert cat in data, f"Category {cat} not found in summary tracker for FAISS indexing."
    assert sub in data[cat], f"Subcategory {sub} not found in summary tracker for {cat} during FAISS indexing."
    assert data[cat][sub].get("summarized_total", 0) > 0, "Failed to generate summary before FAISS indexing."

    results = logger_core.search_summaries("index test", top_k=3)
    assert isinstance(results, list) and len(results) > 0, "Expected at least one FAISS search result."


def test_raw_log_index_integration(logger_core):
    cat, sub = "FAISS", "Check"
    for i in range(5):
        logger_core.log_new_entry(cat, sub, f"Raw log entry {i + 1}")
    logger_core.generate_global_summary(cat, sub)

    data = read_json(logger_core.paths.summary_tracker_file)
    assert cat in data, f"Category {cat} not found in summary tracker for raw log indexing."
    assert sub in data[cat], f"Subcategory {sub} not found in summary tracker for {cat} during raw log indexing."
    assert data[cat][sub].get("summarized_total", 0) > 0, "Summary required before raw log indexing."

    # Instead of accessing a raw_log_indexer attribute, use the core's search_raw_logs method.
    results = logger_core.search_raw_logs("raw log", top_k=2)
    assert isinstance(results, list) and len(results) > 0, "Expected at least one raw log search result."
