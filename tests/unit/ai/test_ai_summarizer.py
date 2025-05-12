import json
import pytest
from unittest.mock import patch
from scripts.utils.file_utils import read_json
from scripts.ai.ai_summarizer import AISummarizer
from tests.mocks.test_helpers import make_dummy_aisummarizer, make_fake_logs

pytestmark = [pytest.mark.unit, pytest.mark.ai_mocked]

class TestAISummarizer:

    @pytest.fixture
    def summarizer(self):
        return AISummarizer()

    def test_generate_summary_triggers_and_writes_summary(self, logger_core):
        date_str = "2025-03-22"
        main_category = "TestCat"
        subcategory = "SubCat"
        logs = {
            date_str: {
                main_category: {
                    subcategory: [
                        {"timestamp": f"{date_str} 12:00:00", "content": f"entry {i}"} for i in range(5)
                    ]
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

    def test_generate_summary_fallback(self, logger_core, monkeypatch):
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
                    "SubCat": [
                        {"timestamp": f"{date_str} 12:00:00", "content": f"entry {i}"} for i in range(5)
                    ]
                }
            }
        }
        logger_core.log_manager.json_log_file.write_text(json.dumps(logs, indent=2))
        success = logger_core.generate_summary(date_str, "TestCat", "SubCat")
        assert success

    def test_summarize_entry_with_mock(self, monkeypatch):
        class MockOllama:
            @staticmethod
            def generate(model, prompt):
                return {"response": "[MOCKED] Summary"}

        monkeypatch.setattr("scripts.ai.ai_summarizer.ollama", MockOllama)
        summarizer = AISummarizer()
        result = summarizer.summarize_entry("This is a test log entry.")
        assert "[MOCKED] Summary" in result

    def test_bulk_summary_with_empty_input(self):
        summarizer = AISummarizer()
        result = summarizer.summarize_entries_bulk([])
        assert result == "No entries provided"

    def test_bulk_summary_with_subcategory(self, monkeypatch):
        class MockOllama:
            @staticmethod
            def generate(model, prompt):
                return {"response": f"Summary with subcategory context: {prompt}"}

        monkeypatch.setattr("scripts.ai.ai_summarizer.ollama", MockOllama)
        summarizer = AISummarizer()
        result = summarizer.summarize_entries_bulk(
            ["First entry.", "Second entry."], subcategory="Creative:Visual or Audio Prompt"
        )
        assert "subcategory context" in result
        assert result.startswith("Summary with subcategory context:")

    def test_bulk_summary_with_none_input(self):
        summarizer = AISummarizer()
        result = summarizer.summarize_entries_bulk(None)
        assert result == "No entries provided"

    def test_summarize_entry_returns_empty_string(self, monkeypatch):
        summarizer = AISummarizer()

        class MockOllama:
            @staticmethod
            def generate(model, prompt):
                return {"response": ""}

        monkeypatch.setattr("scripts.ai.ai_summarizer.ollama", MockOllama)
        result = summarizer.summarize_entry("Some input")
        assert result == ""

    def test_summarize_entry_returns_non_string(self, monkeypatch):
        from scripts.ai import ai_summarizer
        monkeypatch.setattr(ai_summarizer.ollama, "generate", lambda *a, **kw: {"response": None})
        summarizer = AISummarizer()
        result = summarizer.summarize_entry("Some input")
        assert result == "Mock fallback summary"

    def test_generate_summary_file_io_error(self, logger_core, tmp_path):
        summary_file = tmp_path / "summary.json"
        summary_file.write_text("{}")
        summary_file.chmod(0o400)  # Read-only

        logger_core.log_manager.correction_summaries_file = summary_file
        date_str = "2025-03-22"
        logs = make_fake_logs(date_str, "TestCat", "SubCat")
        logger_core.log_manager.json_log_file.write_text(json.dumps(logs, indent=2))
        logger_core.ai_summarizer = make_dummy_aisummarizer()

        success = logger_core.generate_summary(date_str, "TestCat", "SubCat")
        assert not success

    # ======================= Advanced Robustness Tests =========================

    def test_bulk_summary_token_overflow(self, monkeypatch):
        summarizer = AISummarizer()
        entries = ["Very long log entry " * 1000 for _ in range(100)]

        with patch("scripts.ai.ai_summarizer.ollama.generate") as mock_generate, \
             patch.object(summarizer, "_fallback_summary", return_value="[OVERSIZED FALLBACK]") as mock_fallback:

            mock_generate.side_effect = Exception("Token limit exceeded")
            result = summarizer.summarize_entries_bulk(entries)

            mock_fallback.assert_called_once()
            assert "[OVERSIZED FALLBACK]" in result

    def test_bulk_summary_malformed_response(self, monkeypatch):
        summarizer = AISummarizer()
        entries = ["Log entry A", "Log entry B"]

        with patch("scripts.ai.ai_summarizer.ollama.generate") as mock_generate, \
             patch.object(summarizer, "_fallback_summary", return_value="[MALFORMED FALLBACK]") as mock_fallback:

            mock_generate.return_value = {"invalid_key": "missing response field"}
            result = summarizer.summarize_entries_bulk(entries)

            mock_fallback.assert_called_once()
            assert "[MALFORMED FALLBACK]" in result

    def test_bulk_summary_api_timeout(self, monkeypatch):
        summarizer = AISummarizer()
        entries = ["Log entry A", "Log entry B"]

        with patch("scripts.ai.ai_summarizer.ollama.generate") as mock_generate, \
             patch.object(summarizer, "_fallback_summary", return_value="[TIMEOUT FALLBACK]") as mock_fallback:

            mock_generate.side_effect = TimeoutError("LLM API timed out")
            result = summarizer.summarize_entries_bulk(entries)

            mock_fallback.assert_called_once()
            assert result == "[TIMEOUT FALLBACK]"
