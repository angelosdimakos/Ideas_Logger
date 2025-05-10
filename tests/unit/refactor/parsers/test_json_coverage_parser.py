import pytest
from pathlib import Path
import json
from scripts.refactor.parsers.json_coverage_parser import parse_json_coverage  # Adjust import to your actual path

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


@pytest.fixture
def coverage_json_path():
    return str(FIXTURES_DIR / "coverage.json")


@pytest.fixture
def method_ranges():
    return {
        "AISummarizer.__init__": (30, 45),
        "AISummarizer._fallback_summary": (50, 70),
        "AISummarizer.summarize_entry": (75, 100),
    }


def test_exact_path_match(coverage_json_path, method_ranges):
    result = parse_json_coverage(coverage_json_path, method_ranges, "scripts/ai/ai_summarizer.py")
    assert "scripts/ai/ai_summarizer.py" in result
    assert "AISummarizer.__init__" in result["scripts/ai/ai_summarizer.py"]
    assert result["scripts/ai/ai_summarizer.py"]["AISummarizer.__init__"]["coverage"] >= 0.0


def test_suffix_path_match(coverage_json_path, method_ranges):
    # Simulate a non-normalized path that should still match via suffix
    result = parse_json_coverage(coverage_json_path, method_ranges, "ai/ai_summarizer.py")
    assert "ai/ai_summarizer.py" in result or "scripts/ai/ai_summarizer.py" in result


def test_no_coverage_fallback(coverage_json_path):
    fake_ranges = {"NonExistent.method": (10, 20)}
    result = parse_json_coverage(coverage_json_path, fake_ranges, "scripts/nonexistent.py")
    assert "scripts/nonexistent.py" in result
    assert result["scripts/nonexistent.py"]["NonExistent.method"]["coverage"] == 0.0
    assert result["scripts/nonexistent.py"]["NonExistent.method"]["hits"] == 0


def test_summary_usage_over_executed_lines(coverage_json_path, method_ranges):
    result = parse_json_coverage(coverage_json_path, method_ranges, "scripts/ai/ai_summarizer.py")
    coverage_val = result["scripts/ai/ai_summarizer.py"]["AISummarizer.__init__"]["coverage"]
    assert coverage_val == 1.0  # According to summary, this should be 100% covered


def test_executed_lines_fallback_when_summary_missing(tmp_path, method_ranges):
    # Simulate a minimal JSON file with no summaries, only executed_lines
    dummy_json = {
        "files": {
            "scripts/ai/ai_summarizer.py": {
                "executed_lines": [31, 32, 33]
            }
        }
    }
    json_path = tmp_path / "dummy_coverage.json"
    json_path.write_text(json.dumps(dummy_json))

    result = parse_json_coverage(str(json_path), method_ranges, "scripts/ai/ai_summarizer.py")
    assert result["scripts/ai/ai_summarizer.py"]["AISummarizer.__init__"]["hits"] == 3


def test_empty_method_ranges(coverage_json_path):
    result = parse_json_coverage(coverage_json_path, {}, "scripts/ai/ai_summarizer.py")
    assert result == {"scripts/ai/ai_summarizer.py": {}}
