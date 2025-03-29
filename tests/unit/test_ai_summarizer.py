import json
from scripts.utils.file_utils import read_json
import pytest
pytestmark = [pytest.mark.unit, pytest.mark.ai_mocked]




def test_generate_summary_triggers_and_writes_summary(logger_core):
    """
    Tests that the generate_summary method on logger_core triggers the summary generation
    and writes the summary correctly to the correction_summaries_file.

    This test ensures that:
    - The generate_summary method returns a success status.
    - The generated summary file contains the expected hierarchical structure:
      - 'global' category
      - The specified main category within 'global'
      - The specified subcategory within the main category.
    """
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
    logger_core.log_manager.json_log_file.write_text(json.dumps(logs, indent=2))
    success = logger_core.generate_summary(date_str, main_category, subcategory)
    assert success
    summaries = read_json(logger_core.log_manager.correction_summaries_file)
    assert "global" in summaries
    assert main_category in summaries["global"]
    assert subcategory in summaries["global"][main_category]

def test_generate_summary_fallback(logger_core, monkeypatch):
    """
    Verify that generate_summary() will fallback to a simpler summary if the AI fails.
    """
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