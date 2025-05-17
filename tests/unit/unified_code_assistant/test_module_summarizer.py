# tests/utils_test.py
import json
import tempfile
import os
from scripts.unified_code_assistant.assistant_utils import load_report, extract_code_snippets, get_issue_locations
from scripts.unified_code_assistant.prompt_builder import build_contextual_prompt, build_enhanced_contextual_prompt
from scripts.unified_code_assistant.module_summarizer import summarize_modules
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

def test_get_issue_locations():
    mock_report = {
        "file.py": {
            "mypy": {
                "errors": [{"line": 10, "message": "Type error"}]
            },
            "lint": {
                "issues": [{"line": 12, "message": "Style issue", "severity": "warning"}]
            },
            "complexity": {
                "functions": [{"line_number": 15, "complexity": 12, "name": "complex_func"}]
            }
        }
    }

    issues = get_issue_locations("file.py", mock_report)
    assert len(issues) == 3

    expected = {
        ('mypy', 10),
        ('lint', 12),
        ('complexity', 15)
    }
    result = {(issue['type'], issue['line_number']) for issue in issues}
    assert result == expected

def test_build_contextual_prompt():
    top_offenders = [
        ("file_a.py", None, [1, 2], 3, 5, 0.75),
        ("file_b.py", None, [], 1, 4, 0.9)
    ]
    summary_metrics = {"coverage": "80%"}
    prompt = build_contextual_prompt("How do I improve this?", top_offenders, summary_metrics, "mentor")
    assert "file_a.py" in prompt
    assert "coverage" in prompt
    assert "How do I improve this?" in prompt

def test_build_enhanced_contextual_prompt():
    top_offenders = [
        ("module1.py", None, [1, 2], 2, 3, 0.8)
    ]
    summary_metrics = {"coverage": "85%"}
    module_summaries = {"module1.py": "Handles user input."}
    file_issues = {
        "module1.py": {
            "mypy_errors": ["error1"],
            "lint_issues": ["lint1"]
        }
    }
    file_recommendations = {"module1.py": "Refactor large function."}
    prompt = build_enhanced_contextual_prompt(
        "What should we fix first?",
        top_offenders,
        summary_metrics,
        module_summaries,
        file_issues,
        file_recommendations,
        "planner"
    )
    assert "module1.py" in prompt
    assert "Refactor large function." in prompt
    assert "What should we fix first?" in prompt

def test_summarize_modules():
    report_data = {
        "src/module1.py": {
            "docstrings": {
                "functions": [{"name": "foo", "docstring": "Does something"}]
            }
        },
        "src/module2.py": {
            "docstrings": {
                "functions": []
            }
        },
        "src/ignore.py": {
            "docstrings": {}
        }
    }
    config = ConfigManager.load_config()
    summaries = summarize_modules(report_data, MockSummarizer(), config=config)
    assert "src/module1.py" in summaries
    assert "Summary for: " in summaries["src/module1.py"]
    assert summaries["src/module2.py"] == "Docstrings exist but no functions parsed."
    assert "src/ignore.py" not in summaries

