import pytest
import json
from tests.test_utils import make_fake_logs


def test_generate_summary_triggers_and_writes_summary(logger_core):
    """
    Tests the generate_summary method of logger_core to ensure it triggers summary generation
    and accurately writes the summary to the correction_summaries_file.

    Verifies that:
    - The generate_summary method returns a success status.
    - The generated summary file includes the expected hierarchical structure:
      - 'global' category
      - The specified main category within 'global'
      - The specified subcategory within the main category.
    """
    date_str = "2025-03-22"
    category = "CoreCat"
    subcat = "SubCore"
    logs = make_fake_logs(date_str, category, subcat)
    logger_core.json_log_file.write_text(json.dumps(logs, indent=2))

    assert logger_core.generate_summary(date_str, category, subcat)

    summaries = json.loads(logger_core.correction_summaries_file.read_text())
    assert "global" in summaries
    assert category in summaries["global"]
    assert subcat in summaries["global"][category]


def test_generate_summary_fallback(logger_core):
    """
    Verify that generate_summary() will fallback to a simpler summary if the AI fails.
    """
    class Dummy:
        def summarize_entries_bulk(self, entries, subcategory=None):
            raise Exception("Failure")

        def _fallback_summary(self, full_prompt):
            return "Fallback summary."

    logger_core.ai_summarizer = Dummy()
    date = "2025-03-22"
    logs = make_fake_logs(date, "Fallback", "Test")
    logger_core.json_log_file.write_text(json.dumps(logs, indent=2))

    assert logger_core.generate_summary(date, "Fallback", "Test")
