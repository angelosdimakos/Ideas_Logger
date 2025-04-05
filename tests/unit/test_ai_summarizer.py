import json
import pytest
from scripts.utils.file_utils import read_json
from scripts.ai.ai_summarizer import AISummarizer

pytestmark = [pytest.mark.unit, pytest.mark.ai_mocked]


def test_generate_summary_triggers_and_writes_summary(logger_core):
    date_str = "2025-03-22"
    main_category = "TestCat"
    subcategory = "SubCat"
    logs = {
        date_str: {
            main_category: {
                subcategory: [{"timestamp": f"{date_str} 12:00:00", "content": f"entry {i}"} for i in range(5)]
            }
        }
    }
    # Write test log data to the raw log file.
    logger_core.log_manager.json_log_file.write_text(json.dumps(logs, indent=2))
    success = logger_core.generate_summary(date_str, main_category, subcategory)
    assert success
    summaries = read_json(logger_core.log_manager.correction_summaries_file)
    assert "global" in summaries
    assert main_category in summaries["global"]
    assert subcategory in summaries["global"][main_category]


def test_generate_summary_fallback(logger_core, monkeypatch):
    class DummySummarizer:
        def summarize_entries_bulk(self, entries, subcategory=None):
            raise Exception("Mock failure")
        def _fallback_summary(self, full_prompt):
            return "This is a mocked summary."

    logger_core.ai_summarizer = DummySummarizer()
    date_str = "2025-03-22"
    logs = {
        date_str: {
            "TestCat": {
                "SubCat": [{"timestamp": f"{date_str} 12:00:00", "content": f"entry {i}"} for i in range(5)]
            }
        }
    }
    logger_core.log_manager.json_log_file.write_text(json.dumps(logs, indent=2))
    success = logger_core.generate_summary(date_str, "TestCat", "SubCat")
    assert success


def test_summarize_entry_with_mock(monkeypatch):
    class MockOllama:
        @staticmethod
        def generate(model, prompt):
            return {"response": "[MOCKED] Summary"}

    monkeypatch.setattr("scripts.ai.ai_summarizer.ollama", MockOllama)
    summarizer = AISummarizer()
    result = summarizer.summarize_entry("This is a test log entry.")
    assert "[MOCKED] Summary" in result


def test_bulk_summary_with_empty_input():
    summarizer = AISummarizer()
    result = summarizer.summarize_entries_bulk([])
    assert result == "No entries provided"


def test_bulk_summary_with_subcategory(monkeypatch):
    class MockOllama:
        @staticmethod
        def generate(model, prompt):
            return {"response": f"Summary with subcategory context: {prompt}"}

    monkeypatch.setattr("scripts.ai.ai_summarizer.ollama", MockOllama)
    summarizer = AISummarizer()
    result = summarizer.summarize_entries_bulk(
        ["First entry.", "Second entry."],
        subcategory="Creative:Visual or Audio Prompt"
    )
    assert "subcategory context" in result
    assert result.startswith("Summary with subcategory context:")


def test_empty_entries_bulk(monkeypatch):
    class MockSummarizer:
        def summarize_entries_bulk(self, entries, subcategory=None):
            return "No entries provided"
    monkeypatch.setattr("scripts.ai.ai_summarizer.AISummarizer", lambda: MockSummarizer())
    summarizer = AISummarizer()
    result = summarizer.summarize_entries_bulk([])
    assert result == "No entries provided"


def test_batch_less_than_required(monkeypatch):
    summarizer = AISummarizer()

    def dummy_bulk(entries, subcategory=None):
        return f"Summary: {entries[0]}"
    monkeypatch.setattr(summarizer, "summarize_entries_bulk", dummy_bulk)
    entries = ["Only one."]
    result = summarizer.summarize_entries_bulk(entries)
    assert "Only one" in result


def test_subcategory_vs_default_summary(monkeypatch):
    summarizer = AISummarizer()
    responses = iter([
        "Subcategory summary.",
        "Default summary."
    ])
    def dummy_bulk(entries, subcategory=None):
        return next(responses)
    monkeypatch.setattr(summarizer, "summarize_entries_bulk", dummy_bulk)
    entries = ["Compare me."]
    result_sub = summarizer.summarize_entries_bulk(entries, subcategory="Meta Reflection")
    result_default = summarizer.summarize_entries_bulk(entries)
    assert result_sub != result_default


def test_summary_fallback(monkeypatch):
    summarizer = AISummarizer()
    def broken_summary(*args, **kwargs):
        raise Exception("Mocked failure")
    def mock_fallback(text):
        return "- One\n- Two\n- Three"
    monkeypatch.setattr(summarizer, "summarize_entries_bulk", broken_summary)
    monkeypatch.setattr(summarizer, "_fallback_summary", mock_fallback)
    result = summarizer._fallback_summary("One\nTwo\nThree")
    assert "- One" in result
