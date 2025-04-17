import pytest
from scripts.ci_analyzer.lint_parser import LintParser
from tests.mocks.test_utils import create_temp_file_with_content

def test_parse_black(tmp_path):
    sample_lint_file = create_temp_file_with_content(tmp_path, "scripts/gui/gui.py:1:1: E265 block comment should start with '# '\n")
    parser = LintParser(path=sample_lint_file)
    result = parser.parse()
    assert result["issue_count"] == 1
    assert "block comment" in result["issues"][0]

def test_parse_flake8(tmp_path):
    sample_lint_file = create_temp_file_with_content(tmp_path, "scripts/core/core.py:10:5: F401 unused import\n")
    parser = LintParser(path=sample_lint_file)
    result = parser.parse()
    assert result["issue_count"] == 1
    assert "unused import" in result["issues"][0]

def test_parse_mypy(tmp_path):
    sample_lint_file = create_temp_file_with_content(tmp_path, "scripts/gui/panels/log_panel.py: error: Incompatible return value type (got \"str\", expected \"None\")\n")
    parser = LintParser(path=sample_lint_file)
    result = parser.parse()
    assert result["issue_count"] == 1
    assert "Incompatible return value type" in result["issues"][0]

def test_parse_pydocstyle(tmp_path):
    sample_lint_file = create_temp_file_with_content(tmp_path, "scripts/core/core.py:1 in public module\nMissing docstring in public module\n")
    parser = LintParser(path=sample_lint_file)
    result = parser.parse()
    assert result["issue_count"] == 2
