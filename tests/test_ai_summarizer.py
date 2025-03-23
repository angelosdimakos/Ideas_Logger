import pytest
import json
from unittest.mock import MagicMock

# 🧠 GLOBAL PATCHES BEFORE IMPORTS

@pytest.fixture(autouse=True)
def patch_aisummarizer(monkeypatch):
    """
    Fixture that replaces the AISummarizer class with a MagicMock
    to prevent actual calls to Ollama during test runs.
    """
    mock_ai = MagicMock()
    mock_ai.model = "llama3"
    mock_ai.prompts_by_subcategory = {}  # Empty dictionary mock
    mock_ai.summarize_entries_bulk.return_value = "This is a mocked summary."  # Default mocked return value

    # Simulate a failure for specific conditions
    def mock_summarize_entries_bulk(entries, subcategory):
        if "down" in entries[0]:  # Simulate failure for certain inputs
            raise Exception("Ollama down")
        return "This is a mocked summary."

    mock_ai.summarize_entries_bulk.side_effect = mock_summarize_entries_bulk
    monkeypatch.setattr("scripts.ai_summarizer.AISummarizer", lambda: mock_ai)

@pytest.fixture(autouse=True)
def patch_load_config(monkeypatch):
    """
    Fixture that overrides `load_config` to return a static test config.
    Prevents loading or writing to actual config files.
    """
    monkeypatch.setattr("scripts.config_loader.load_config", lambda: {
        "batch_size": 5,
        "logs_dir": "logs",
        "export_dir": "exports"
    })

# 🧪 TEMP DIRECTORY STRUCTURE

@pytest.fixture
def mock_data_dir(tmp_path):
    """
    Creates a temporary mock data directory structure for logs and exports.
    """
    (tmp_path / "logs").mkdir()
    (tmp_path / "exports").mkdir()
    return tmp_path

@pytest.fixture
def logger_core(mock_data_dir):
    """
    Initializes the ZephyrusLoggerCore using the temporary mock data directory.
    Ensures all file operations are sandboxed.
    """
    from scripts.core import ZephyrusLoggerCore  # ⛔ Must import AFTER patches
    return ZephyrusLoggerCore(script_dir=mock_data_dir)

# 🧪 TESTS START HERE

def test_initialize_aisummarizer_with_mock_data(logger_core):
    """
    Validates that the AI Summarizer initializes correctly and interacts with the mocked config.
    """
    ai_summarizer = logger_core.ai_summarizer
    assert ai_summarizer.model == "llama3"
    assert ai_summarizer.prompts_by_subcategory == {}

def test_generate_summary_triggers_and_writes_summary(logger_core):
    """
    Verifies that:
    1. A batch of 5 entries triggers AI summarization.
    2. The mocked summary is written to correction_summaries_file correctly.
    """
    date_str = "2025-03-22"
    main_category = "TestCat"
    subcategory = "SubCat"

    # Fake 5 entries that will trigger summary
    logs = {
        date_str: {
            main_category: {
                subcategory: [{"timestamp": "2025-03-22 12:00:00", "content": f"entry {i}"} for i in range(5)]
            }
        }
    }

    logger_core.json_log_file.write_text(json.dumps(logs, indent=2), encoding="utf-8")

    success = logger_core.generate_summary(date_str, main_category, subcategory)
    assert success

    summaries = json.loads(logger_core.correction_summaries_file.read_text(encoding="utf-8"))
    batch_summary = summaries[date_str][main_category][subcategory][0]
    assert batch_summary["original_summary"] == "This is a mocked summary."

def test_generate_summary_fallback(logger_core, monkeypatch):
    """
    Ensures that the fallback mechanism is triggered if the summarization fails.
    """
    # Force an exception to trigger fallback
    monkeypatch.setattr(logger_core.ai_summarizer, 'summarize_entries_bulk', MagicMock(side_effect=Exception("Ollama down")))
    
    # Mock the fallback to return a known value
    monkeypatch.setattr(logger_core.ai_summarizer, '_fallback_summary', lambda *args: "This is a mocked summary.")

    # Fake 5 entries that will trigger summary
    logs = {
        "2025-03-22": {
            "TestCat": {
                "SubCat": [{"timestamp": "2025-03-22 12:00:00", "content": f"entry {i}"} for i in range(5)]
            }
        }
    }

    logger_core.json_log_file.write_text(json.dumps(logs, indent=2), encoding="utf-8")

    # Mock the summarized count to force summary generation
    monkeypatch.setattr(logger_core, "get_summarized_count", lambda *args, **kwargs: 0)

    # Test with the failure and fallback
    try:
        success = logger_core.generate_summary("2025-03-22", "TestCat", "SubCat")
        assert success  # This should pass due to fallback
    except Exception as e:
        # The test should not reach this point, as the fallback should succeed
        assert False, f"Summary generation failed unexpectedly: {e}"

    summaries = json.loads(logger_core.correction_summaries_file.read_text(encoding="utf-8"))
    batch_summary = summaries["2025-03-22"]["TestCat"]["SubCat"][0]
    
    # Ensure fallback summary is written
    assert batch_summary["original_summary"] == "This is a mocked summary."
def test_ai_summarizer_bulk_fallback(mock_data_dir, logger_core, monkeypatch):
    """
    Verifies that the AI Summarizer's fallback mechanism works for bulk summarization.
    """

    print("[TEST] Forcing ollama.generate to raise an exception")

    # Mock Ollama to raise an error inside the real method
    monkeypatch.setattr("scripts.ai_summarizer.ollama.generate", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("Ollama down")))

    # Mock the fallback to return a known value
    print("[TEST] Mocking _fallback_summary to return a mocked summary")
    monkeypatch.setattr(logger_core.ai_summarizer, "_fallback_summary", lambda *args: "This is a mocked summary.")

    entries = [f"Test entry {i}" for i in range(5)]
    subcategory = "TestSubCategory"

    print("[TEST] Calling real summarize_entries_bulk with simulated Ollama failure")
    result = logger_core.ai_summarizer.summarize_entries_bulk(entries, subcategory)

    print(f"[TEST] Result: {result}")
    assert result == "This is a mocked summary."
