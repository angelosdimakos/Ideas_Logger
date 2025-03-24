import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock

# 🧠 GLOBAL PATCHES BEFORE IMPORTS

@pytest.fixture(autouse=True)
def patch_aisummarizer(monkeypatch):
    """
    Fixture that replaces the AISummarizer class with a MagicMock
    to prevent actual calls to Ollama during test runs.
    """
    mock_ai = MagicMock()
    mock_ai.summarize_entries_bulk.return_value = "This is a mocked summary."
    monkeypatch.setattr("scripts.ai_summarizer.AISummarizer", lambda: mock_ai)

@pytest.fixture(autouse=True)
def patch_get_absolute_path(monkeypatch, temp_dir):
    # Force get_absolute_path to resolve paths relative to the temporary directory.
    monkeypatch.setattr("scripts.config_loader.get_absolute_path", lambda x: str(temp_dir / x))


@pytest.fixture(autouse=True)
def patch_load_config(monkeypatch):
    """
    Fixture that overrides `load_config` to return a static test config.
    Prevents loading or writing to actual config files.
    """
    monkeypatch.setattr("scripts.config_loader.load_config", lambda: {
        "batch_size": 5,
        "logs_dir": "tests/mock_data/logs",
        "export_dir": "tests/mock_data/exports",
        "correction_summaries_path": "tests/mock_data/logs/correction_summaries.json",
        "raw_log_path": "tests/mock_data/logs/zephyrus_log.json",
        "test_logs_dir": "tests/mock_data/logs",
        "test_vector_store_dir": "tests/mock_data/vector_store",
        "test_export_dir": "tests/mock_data/exports"
    })

# 🧪 TEMP DIRECTORY STRUCTURE

@pytest.fixture
def temp_dir(tmp_path):
    """
    Creates a temporary directory structure for logs, vector store, and exports during tests.
    """
    (tmp_path / "tests/mock_data/logs").mkdir(parents=True)
    (tmp_path / "tests/mock_data/vector_store").mkdir(parents=True)
    (tmp_path / "tests/mock_data/exports").mkdir(parents=True)
    return tmp_path

@pytest.fixture
def logger_core(temp_dir):
    """
    Initializes the ZephyrusLoggerCore using the temporary directory.
    Ensures all file operations are sandboxed.
    """
    from scripts.core import ZephyrusLoggerCore  # ⛔ Must import AFTER patches
    return ZephyrusLoggerCore(script_dir=temp_dir)

# 🧪 TESTS START HERE

def test_initialization_creates_files(logger_core):
    """
    Ensures all required files are created on initialization:
    - JSON log file
    - TXT log file
    - Correction summaries file
    """
    assert logger_core.json_log_file.exists()
    assert logger_core.txt_log_file.exists()
    assert logger_core.correction_summaries_file.exists()

def test_safe_filename():
    """
    Verifies that unsafe characters are removed by sanitize_filename.
    """
    from utils.file_utils import sanitize_filename
    unsafe = "inva*lid:/fi|le?name.txt"
    safe = sanitize_filename(unsafe)
    assert "*" not in safe
    assert ":" not in safe
    assert "|" not in safe
    assert "?" not in safe

def test_log_to_json_creates_nested_structure(logger_core):
    """
    Verifies that log_to_json correctly creates a nested structure:
    date → main_category → subcategory → list of entries.
    """
    timestamp = "2025-03-22 12:00:00"
    date_str = "2025-03-22"
    main_category = "TestCategory"
    subcategory = "SubTest"
    entry = "This is a test entry."

    success = logger_core.log_to_json(timestamp, date_str, main_category, subcategory, entry)
    assert success

    logs = json.loads(logger_core.json_log_file.read_text(encoding="utf-8"))
    assert date_str in logs
    assert main_category in logs[date_str]
    assert subcategory in logs[date_str][main_category]
    assert logs[date_str][main_category][subcategory][0]["content"] == entry

def test_get_summarized_count_defaults_to_zero(logger_core):
    """
    Ensures that get_summarized_count returns 0 if no summary data exists
    for the given date/category/subcategory combination.
    """
    count = logger_core.get_summarized_count("2025-03-22", "NonExistentCategory", "SubCat")
    assert count == 0

def test_generate_summary_triggers_and_writes_summary(logger_core, monkeypatch):
    date_str = "2025-03-22"
    main_category = "TestCat"
    subcategory = "SubCat"

    logs = {
        date_str: {
            main_category: {
                subcategory: [{"timestamp": "2025-03-22 12:00:00", "content": f"entry {i}"} for i in range(5)]
            }
        }
    }
    logger_core.json_log_file.write_text(json.dumps(logs, indent=2), encoding="utf-8")

    # ✅ Patch summary count to 0 to trigger summarization
    monkeypatch.setattr(logger_core, "get_summarized_count", lambda *_: 0)

    success = logger_core.generate_summary(date_str, main_category, subcategory)
    assert success

    summaries = json.loads(logger_core.correction_summaries_file.read_text(encoding="utf-8"))
    batch_summary = summaries[date_str][main_category][subcategory][0]
    assert batch_summary["original_summary"] == "This is a mocked summary."


def test_generate_summary_fallback(logger_core, monkeypatch):
    """
    Ensures that the fallback mechanism is triggered if the summarization fails.
    """
    # Replace the ai_summarizer with a dummy that always fails but supports fallback.
    class DummySummarizer:
        def summarize_entries_bulk(self, entries, subcategory=None):
            raise Exception("Ollama down")
        def _fallback_summary(self, full_prompt):
            return "This is a mocked summary."
    
    logger_core.ai_summarizer = DummySummarizer()
    
    # Fake 5 entries that will trigger summary
    logs = {
        "2025-03-22": {
            "TestCat": {
                "SubCat": [{"timestamp": "2025-03-22 12:00:00", "content": f"entry {i}"} for i in range(5)]
            }
        }
    }
    
    logger_core.json_log_file.write_text(json.dumps(logs, indent=2), encoding="utf-8")
    
    # Force summarized count to return 0 to trigger summary generation
    monkeypatch.setattr(logger_core, "get_summarized_count", lambda *args, **kwargs: 0)
    
    # Call generate_summary, which should now fall back to a default summary
    success = logger_core.generate_summary("2025-03-22", "TestCat", "SubCat")
    assert success
    
    summaries = json.loads(logger_core.correction_summaries_file.read_text(encoding="utf-8"))
    batch_summary = summaries["2025-03-22"]["TestCat"]["SubCat"][0]
    assert batch_summary["original_summary"] == "This is a mocked summary."


def test_generate_summary_across_days(logger_core, monkeypatch):
    day_1 = "2025-03-22"
    day_2 = "2025-03-23"
    main_category = "CrossDayCat"
    subcategory = "SubCross"

    logs_day1 = [{"timestamp": f"{day_1} 10:00:00", "content": f"entry {i}"} for i in range(3)]
    logs_day2 = [{"timestamp": f"{day_2} 11:00:00", "content": f"entry {i}"} for i in range(5)]

    full_logs = {
        day_1: {main_category: {subcategory: logs_day1}},
        day_2: {main_category: {subcategory: logs_day2}},
    }
    logger_core.json_log_file.write_text(json.dumps(full_logs, indent=2), encoding="utf-8")

    # ✅ Correct conditional patching
    def fake_summarized_count(date_str, *_):
        return 3 if date_str == day_1 else 0
    monkeypatch.setattr(logger_core, "get_summarized_count", fake_summarized_count)

    summary_day1 = logger_core.generate_summary(day_1, main_category, subcategory)
    assert summary_day1 is False

    summary_day2 = logger_core.generate_summary(day_2, main_category, subcategory)
    assert summary_day2 is True

    summaries = json.loads(logger_core.correction_summaries_file.read_text(encoding="utf-8"))
    assert day_1 not in summaries or not summaries[day_1].get(main_category, {}).get(subcategory)
    assert summaries[day_2][main_category][subcategory][0]["original_summary"] == "This is a mocked summary."
