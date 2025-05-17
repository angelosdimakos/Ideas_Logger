# tests/utils_test.py
import json
import tempfile
import os
from scripts.unified_code_assistant.assistant_utils import load_report, extract_code_snippets, get_issue_locations
from scripts.unified_code_assistant.prompt_builder import build_contextual_prompt, build_enhanced_contextual_prompt
from scripts.unified_code_assistant.module_summarizer import summarize_modules
from scripts.unified_code_assistant.analysis import analyze_report
from scripts.unified_code_assistant.strategy import generate_strategy
from scripts.config.config_manager import ConfigManager
import pytest
from types import SimpleNamespace

@pytest.fixture(autouse=True)
def patch_mock_config(monkeypatch):
    mock_config = SimpleNamespace(
        persona="test",
        prompts_by_subcategory={"_default": "Summarize the function briefly."}
    )
    monkeypatch.setattr("scripts.config.config_manager.ConfigManager.load_config", lambda: mock_config)


class MockSummarizer:
    def summarize_entry(self, text, subcategory=None):
        return "Summary for: " + text[:30]

def test_load_report():
    mock_data = {"some": "data"}
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json") as f:
        json.dump(mock_data, f)
        f.seek(0)
        path = f.name

    try:
        result = load_report(path)
        assert result == mock_data
    finally:
        os.remove(path)

def test_extract_code_snippets():
    test_lines = ["def foo():\n", "    pass\n", "def bar():\n", "    return 42\n", "# end\n"]
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".py") as f:
        f.writelines(test_lines)
        f.flush()
        file_path = f.name

    issues = [{"type": "mypy", "line_number": 3}]
    try:
        snippets = extract_code_snippets(file_path, issues, context_lines=1)
        assert "mypy_3" in snippets
        snippet = snippets["mypy_3"]
        assert "pass" in snippet
        assert "→ def bar():" in snippet
        assert "return 42" in snippet
    finally:
        os.remove(file_path)



def test_analyze_report():
    report_data = {
        "file_a.py": {
            "mypy": {"errors": ["e1"]},
            "lint": {"issues": ["l1"]},
            "complexity": {"functions": []},
            "coverage": {
                "complexity": {
                    "foo": {"complexity": 5},
                    "bar": {"complexity": 3}
                }
            }
        },
        "file_b.py": {
            "mypy": {"errors": []},
            "lint": {"issues": []},
            "complexity": {"functions": []},
            "coverage": {
                "complexity": {
                    "baz": {"complexity": 2}
                }
            }
        }
    }
    result = analyze_report(report_data, top_n=2)
    assert "top_offenders" in result
    assert "severity_data" in result
    assert "summary_metrics" in result
    assert isinstance(result["top_offenders"], list)
    assert isinstance(result["severity_data"], list)
    assert isinstance(result["summary_metrics"], dict)

def test_generate_strategy():
    severity_data = [
    {
        "Full Path": "file_a.py",
        "Severity Score": 0.9
    },
    {
        "Full Path": "file_b.py",
        "Severity Score": 0.7
    }
]


    summary_metrics = {"coverage": 82, "missing_docs": 5}
    response = generate_strategy(
        severity_data=severity_data,
        summary_metrics=summary_metrics,
        limit=2,
        persona="planner",
        summarizer=MockSummarizer()
    )
    assert response.startswith("Summary for: ")
