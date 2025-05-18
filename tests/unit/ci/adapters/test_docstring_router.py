#!/usr/bin/env python3
"""
Unit tests for Docstring Router Adapter
======================================
Tests the functionality of the Docstring Router adapter script without
executing actual docstring analysis or touching the filesystem.

Run with:
    pytest -xvs tests/ci/test_docstring_router.py
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from unittest import mock
import pytest

# Add repo root to path so we can import the adapter modules
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

# Import the module to test
from scripts.ci.adapters.docstring_router import (
    get_changed_python_files,
    analyze_changed_files,
    parse_args
)


@pytest.fixture
def sample_router_report():
    """Fixture providing a sample router report JSON."""
    return {
        "changed_files": [
            "scripts/module1.py",
            "scripts/module2.py",
            "tests/test_module1.py",
            "docs/readme.md"
        ],
        "tasks_run": 3,
        "successful_tasks": 3,
        "failed_tasks": 0,
        "task_results": {
            "lint": {"status": "success"},
            "test": {"status": "success"},
            "docs": {"status": "success"}
        }
    }


@pytest.fixture
def temp_router_report(sample_router_report, tmp_path):
    """Fixture providing a temporary router report file."""
    report_path = tmp_path / "router_summary.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(sample_router_report, f)
    return str(report_path)


@pytest.fixture
def mock_docstring_analyzer():
    """Fixture providing a mocked DocstringAnalyzer."""
    with mock.patch('scripts.ci.adapters.docstring_router.DocstringAnalyzer') as mock_analyzer:
        # Configure the mock
        instance = mock_analyzer.return_value
        instance.should_exclude.return_value = False
        instance.extract_docstrings.return_value = {
            "module_doc": {"description": "Sample docstring"},
            "classes": [],
            "functions": []
        }
        yield instance


def test_parse_args():
    """Test argument parsing."""
    # Test with required args only
    with mock.patch('sys.argv', ['docstring_router.py', '--router-report', 'report.json']):
        args = parse_args()
        assert args.router_report == 'report.json'
        assert args.output == 'docstring_summary.json'
        assert 'venv' in args.exclude

    # Test with all args
    with mock.patch('sys.argv', [
        'docstring_router.py',
        '--router-report', 'report.json',
        '--output', 'custom_output.json',
        '--exclude', 'venv', 'build'
    ]):
        args = parse_args()
        assert args.router_report == 'report.json'
        assert args.output == 'custom_output.json'
        assert 'venv' in args.exclude
        assert 'build' in args.exclude


def test_get_changed_python_files(temp_router_report):
    """Test extracting changed Python files from router report."""
    # Test with valid report
    python_files = get_changed_python_files(temp_router_report)
    assert len(python_files) == 2
    assert "scripts/module1.py" in python_files
    assert "scripts/module2.py" in python_files
    # Test files should be excluded
    assert "tests/test_module1.py" not in python_files

    # Test with nonexistent report
    python_files = get_changed_python_files("nonexistent_report.json")
    assert python_files == []


def test_analyze_changed_files(mock_docstring_analyzer):
    """Test analyzing docstrings in changed files."""
    # Setup test files
    python_files = [
        "scripts/module1.py",
        "scripts/module2.py"
    ]

    # Set up all our mocks in a single context
    with mock.patch('scripts.ci.adapters.docstring_router.Path.exists', return_value=True):
        # Happy path test
        mock_docstring_analyzer.extract_docstrings.return_value = {
            "module_doc": {"description": "Sample docstring"},
            "classes": [],
            "functions": []
        }

        # Analyze the files
        results = analyze_changed_files(python_files, mock_docstring_analyzer)

        # Verify the results
        assert len(results) == 2
        assert "scripts/module1.py" in results
        assert "scripts/module2.py" in results
        assert results["scripts/module1.py"]["module_doc"]["description"] == "Sample docstring"

        # Error path test - reset the mock to raise exceptions
        mock_docstring_analyzer.extract_docstrings.side_effect = Exception("Test error")

        # This should not raise an exception
        results = analyze_changed_files(python_files, mock_docstring_analyzer)

        # Results should be empty since all calls raised exceptions
        assert len(results) == 0


@mock.patch("scripts.ci.adapters.docstring_router.analyze_changed_files")
@mock.patch("scripts.ci.adapters.docstring_router.get_changed_python_files")
@mock.patch("scripts.ci.adapters.docstring_router.DocstringAnalyzer")
@mock.patch("scripts.ci.adapters.docstring_router.open", new_callable=mock.mock_open)
@mock.patch("scripts.ci.adapters.docstring_router.json.dump")
def test_main(
        mock_json_dump, mock_open, mock_docstring_analyzer,
        mock_get_changed_python_files, mock_analyze_changed_files
):
    """Test the main function."""
    # Setup mocks
    python_files = ["scripts/module1.py", "scripts/module2.py"]
    mock_get_changed_python_files.return_value = python_files

    analysis_results = {
        "scripts/module1.py": {
            "module_doc": {"description": "Sample docstring"},
            "classes": [],
            "functions": []
        },
        "scripts/module2.py": {
            "module_doc": {"description": "Another docstring"},
            "classes": [],
            "functions": []
        }
    }
    mock_analyze_changed_files.return_value = analysis_results

    # Mock sys.argv
    with mock.patch('sys.argv', [
        'docstring_router.py',
        '--router-report', 'report.json',
        '--output', 'output.json'
    ]):
        # Import main function and run it
        from scripts.ci.adapters.docstring_router import main
        main()

    # Verify get_changed_python_files was called
    mock_get_changed_python_files.assert_called_once_with('report.json')

    # Verify DocstringAnalyzer was instantiated
    mock_docstring_analyzer.assert_called_once()

    # Verify analyze_changed_files was called with the right arguments
    mock_analyze_changed_files.assert_called_once()

    # Verify output was written
    mock_open.assert_called_with('output.json', 'w', encoding='utf-8')
    mock_json_dump.assert_called_once_with(analysis_results, mock_open(), indent=2, ensure_ascii=False)

    # Test with no Python files
    mock_get_changed_python_files.return_value = []
    mock_open.reset_mock()
    mock_json_dump.reset_mock()

    with mock.patch('sys.argv', [
        'docstring_router.py',
        '--router-report', 'report.json',
        '--output', 'output.json'
    ]):
        # Import and run main function
        from scripts.ci.adapters.docstring_router import main
        main()

    # Verify empty output was written
    mock_open.assert_called_with('output.json', 'w', encoding='utf-8')
    mock_json_dump.assert_called_once_with({}, mock_open(), indent=2)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])