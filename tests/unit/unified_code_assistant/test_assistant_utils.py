# tests/utils_test.py
import json
import tempfile
import os
from scripts.unified_code_assistant.assistant_utils import load_report, extract_code_snippets, get_issue_locations

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
        assert "3 → def bar()" in snippet
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
