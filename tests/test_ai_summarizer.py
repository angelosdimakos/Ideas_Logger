import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock



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
    logger_core.json_log_file.write_text(json.dumps(logs, indent=2))
    success = logger_core.generate_summary(date_str, main_category, subcategory)
    assert success
    summaries = json.loads(logger_core.correction_summaries_file.read_text())
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
    logger_core.json_log_file.write_text(json.dumps(logs, indent=2))
    success = logger_core.generate_summary(date_str, "TestCat", "SubCat")
    assert success