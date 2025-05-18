#!/usr/bin/env python3
"""
Unit tests for Merge Reports Router Adapter
=========================================
Tests the functionality of the Merge Reports Router adapter script without
touching the filesystem.

Run with:
    pytest -xvs tests/ci/test_merge_reports_router.py
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from unittest import mock
import pytest
import logging

# Add repo root to path so we can import the adapter modules
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

# Import the module to test
from scripts.ci.adapters.merge_reports_router import (
    parse_args,
    get_router_data,
    load_json_report,
    get_changed_file_paths,
    merge_docstring_data,
    merge_coverage_data,
    merge_linting_data,
    route_merge_reports
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
            "test": {"status": "success", "test_files": ["tests/test_module1.py"]},
            "docstring": {"status": "success"}
        }
    }


@pytest.fixture
def sample_docstring_data():
    """Fixture providing sample docstring data."""
    return {
        "scripts/module1.py": {
            "module_doc": {"description": "Module 1 docstring"},
            "classes": [],
            "functions": []
        },
        "scripts/module2.py": {
            "module_doc": {"description": "Module 2 docstring"},
            "classes": [],
            "functions": []
        }
    }


@pytest.fixture
def sample_coverage_data():
    """Fixture providing sample coverage data."""
    return {
        "scripts/module1.py": {
            "complexity": {
                "function1": {
                    "complexity": 3,
                    "coverage": 80.0,
                    "hits": 8,
                    "lines": 10,
                    "covered_lines": [1, 2, 3, 4, 5, 6, 7, 8],
                    "missing_lines": [9, 10]
                }
            },
            "complexity_score": 3
        },
        "scripts/module2.py": {
            "complexity": {
                "function2": {
                    "complexity": 2,
                    "coverage": 100.0,
                    "hits": 5,
                    "lines": 5,
                    "covered_lines": [1, 2, 3, 4, 5],
                    "missing_lines": []
                }
            },
            "complexity_score": 2
        }
    }


@pytest.fixture
def sample_linting_data():
    """Fixture providing sample linting data."""
    return {
        "scripts/module1.py": {
            "linting": {
                "quality": {
                    "pylint": {
                        "score": 8.5,
                        "messages": []
                    },
                    "mypy": {
                        "errors": []
                    }
                }
            }
        },
        "scripts/module2.py": {
            "linting": {
                "quality": {
                    "pylint": {
                        "score": 9.0,
                        "messages": []
                    },
                    "mypy": {
                        "errors": []
                    }
                }
            }
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
def temp_docstring_data(sample_docstring_data, tmp_path):
    """Fixture providing a temporary docstring data file."""
    docstring_path = tmp_path / "docstring_summary.json"
    with open(docstring_path, 'w', encoding='utf-8') as f:
        json.dump(sample_docstring_data, f)
    return str(docstring_path)


@pytest.fixture
def temp_coverage_data(sample_coverage_data, tmp_path):
    """Fixture providing a temporary coverage data file."""
    coverage_path = tmp_path / "refactor_audit.json"
    with open(coverage_path, 'w', encoding='utf-8') as f:
        json.dump(sample_coverage_data, f)
    return str(coverage_path)


@pytest.fixture
def temp_linting_data(sample_linting_data, tmp_path):
    """Fixture providing a temporary linting data file."""
    linting_path = tmp_path / "linting_report.json"
    with open(linting_path, 'w', encoding='utf-8') as f:
        json.dump(sample_linting_data, f)
    return str(linting_path)


def test_parse_args():
    """Test argument parsing."""
    # Test with required args only
    with mock.patch('sys.argv', ['merge_reports_router.py', '--router-report', 'report.json']):
        args = parse_args()
        assert args.router_report == 'report.json'
        assert args.docstrings == 'artifacts/docstring-summary/docstring_summary.json'
        assert args.coverage == 'artifacts/refactor-audit/refactor_audit.json'
        assert args.linting == 'artifacts/lint-report/linting_report.json'
        assert args.output == 'artifacts/merged_report.json'
        assert not args.verbose

    # Test with all args
    with mock.patch('sys.argv', [
        'merge_reports_router.py',
        '--router-report', 'report.json',
        '--docstrings', 'custom_docstrings.json',
        '--coverage', 'custom_coverage.json',
        '--linting', 'custom_linting.json',
        '-o', 'custom_output.json',
        '--verbose'
    ]):
        args = parse_args()
        assert args.router_report == 'report.json'
        assert args.docstrings == 'custom_docstrings.json'
        assert args.coverage == 'custom_coverage.json'
        assert args.linting == 'custom_linting.json'
        assert args.output == 'custom_output.json'
        assert args.verbose


@mock.patch("scripts.ci.adapters.merge_reports_router.logger")  # Mock the logger to prevent output
def test_get_router_data(mock_logger, temp_router_report, sample_router_report):
    """Test extracting data from router report."""
    # Test with valid report
    data = get_router_data(temp_router_report)
    assert data == sample_router_report

    # Test with nonexistent report
    data = get_router_data("nonexistent_report.json")
    assert "task_results" in data
    assert "changed_files" in data
    assert len(data["changed_files"]) == 0

    # Test with invalid JSON
    with mock.patch("scripts.ci.adapters.merge_reports_router.open", mock.mock_open(read_data="invalid json")):
        data = get_router_data("invalid.json")
        assert "task_results" in data
        assert "changed_files" in data
        assert len(data["changed_files"]) == 0


@mock.patch("scripts.ci.adapters.merge_reports_router.logger")  # Mock the logger to prevent output
def test_load_json_report(mock_logger, temp_docstring_data, sample_docstring_data):
    """Test loading JSON report."""
    # Test with valid report
    data = load_json_report(temp_docstring_data)
    assert data == sample_docstring_data

    # Test with nonexistent report
    data = load_json_report("nonexistent_report.json")
    assert data is None

    # Test with invalid JSON
    with mock.patch("scripts.ci.adapters.merge_reports_router.open", mock.mock_open(read_data="invalid json")):
        data = load_json_report("invalid.json")
        assert data is None


def test_get_changed_file_paths(sample_router_report):
    """Test extracting changed file paths from router data."""
    # Test with valid router data
    changed_files = get_changed_file_paths(sample_router_report)

    # Update expectation: 4 instead of 5 due to deduplication
    assert len(changed_files) == 4  # Changed from 5 to 4

    # Verify specific files are included
    assert "scripts/module1.py" in changed_files
    assert "scripts/module2.py" in changed_files
    assert "tests/test_module1.py" in changed_files
    assert "docs/readme.md" in changed_files

    # Test with empty router data
    changed_files = get_changed_file_paths({})
    assert len(changed_files) == 0

    # Test with no task_results
    changed_files = get_changed_file_paths({"changed_files": ["file1.py"]})
    assert len(changed_files) == 1
    assert "file1.py" in changed_files

def test_merge_docstring_data(sample_docstring_data):
    """Test merging docstring data."""
    # Initialize merged report
    merged_report = {}

    # Test with valid docstring data and changed files
    changed_files = {"scripts/module1.py"}
    merge_docstring_data(merged_report, sample_docstring_data, changed_files, verbose=True)

    assert len(merged_report) == 1
    assert "scripts/module1.py" in merged_report
    assert "docstrings" in merged_report["scripts/module1.py"]
    assert merged_report["scripts/module1.py"]["docstrings"]["module_doc"]["description"] == "Module 1 docstring"

    # Test with all files (empty changed_files set)
    merged_report = {}
    merge_docstring_data(merged_report, sample_docstring_data, set(), verbose=True)

    assert len(merged_report) == 2
    assert "scripts/module1.py" in merged_report
    assert "scripts/module2.py" in merged_report

    # Test with no docstring data
    merged_report = {}
    merge_docstring_data(merged_report, None, changed_files, verbose=True)

    assert len(merged_report) == 0


def test_merge_coverage_data(sample_coverage_data):
    """Test merging coverage data."""
    # Initialize merged report
    merged_report = {}

    # Test with valid coverage data and changed files
    changed_files = {"scripts/module1.py"}
    merge_coverage_data(merged_report, sample_coverage_data, changed_files, verbose=True)

    assert len(merged_report) == 1
    assert "scripts/module1.py" in merged_report
    assert "complexity" in merged_report["scripts/module1.py"]
    assert "function1" in merged_report["scripts/module1.py"]["complexity"]
    assert merged_report["scripts/module1.py"]["complexity_score"] == 3

    # Test with all files (empty changed_files set)
    merged_report = {}
    merge_coverage_data(merged_report, sample_coverage_data, set(), verbose=True)

    assert len(merged_report) == 2
    assert "scripts/module1.py" in merged_report
    assert "scripts/module2.py" in merged_report

    # Test with no coverage data
    merged_report = {}
    merge_coverage_data(merged_report, None, changed_files, verbose=True)

    assert len(merged_report) == 0


def test_merge_linting_data(sample_linting_data):
    """Test merging linting data."""
    # Initialize merged report
    merged_report = {}

    # Test with valid linting data and changed files
    changed_files = {"scripts/module1.py"}
    merge_linting_data(merged_report, sample_linting_data, changed_files, verbose=True)

    assert len(merged_report) == 1
    assert "scripts/module1.py" in merged_report
    assert "linting" in merged_report["scripts/module1.py"]
    assert "quality" in merged_report["scripts/module1.py"]["linting"]
    assert merged_report["scripts/module1.py"]["linting"]["quality"]["pylint"]["score"] == 8.5

    # Test with all files (empty changed_files set)
    merged_report = {}
    merge_linting_data(merged_report, sample_linting_data, set(), verbose=True)

    assert len(merged_report) == 2
    assert "scripts/module1.py" in merged_report
    assert "scripts/module2.py" in merged_report

    # Test with no linting data
    merged_report = {}
    merge_linting_data(merged_report, None, changed_files, verbose=True)

    assert len(merged_report) == 0

    # Test with alternative linting data format (no nested "linting" key)
    alternative_linting_data = {
        "scripts/module1.py": {
            "quality": {
                "pylint": {
                    "score": 8.5,
                    "messages": []
                }
            }
        }
    }

    merged_report = {}
    merge_linting_data(merged_report, alternative_linting_data, changed_files, verbose=True)

    assert len(merged_report) == 1
    assert "scripts/module1.py" in merged_report
    assert "linting" in merged_report["scripts/module1.py"]


def test_merge_reports(
        sample_router_report,
        temp_docstring_data,
        temp_coverage_data,
        temp_linting_data
):
    """Test merging all reports using the router adapter logic."""

    # ✅ Case 1: Docstring + Linting (no test → no coverage)
    router_data = {
        "changed_files": ["scripts/module1.py"],
        "task_results": {
            "docstring": {"status": "success"},
            "lint": {"status": "success"}
        }
    }

    merged_report = route_merge_reports(
        router_data,
        temp_docstring_data,
        temp_coverage_data,
        temp_linting_data,
        verbose=True
    )

    assert len(merged_report) == 1
    assert "module1.py" in merged_report
    assert "docstrings" in merged_report["module1.py"]
    assert "coverage" not in merged_report["module1.py"]
    assert "complexity_score" not in merged_report["module1.py"]
    assert "linting" in merged_report["module1.py"]

    # ✅ Case 2: All files should be included (empty changed_files)
    router_data["changed_files"] = []

    merged_report = route_merge_reports(
        router_data,
        temp_docstring_data,
        temp_coverage_data,
        temp_linting_data,
        verbose=True
    )

    assert len(merged_report) == 2
    assert "module1.py" in merged_report
    assert "module2.py" in merged_report

    # ✅ Case 3: Only docstring task present (no lint or test)
    router_data = {
        "changed_files": ["scripts/module1.py"],
        "task_results": {
            "docstring": {"status": "success"}
        }
    }

    merged_report = route_merge_reports(
        router_data,
        temp_docstring_data,
        temp_coverage_data,
        temp_linting_data,
        verbose=True
    )

    assert len(merged_report) == 1
    assert "module1.py" in merged_report
    assert "docstrings" in merged_report["module1.py"]
    assert "coverage" not in merged_report["module1.py"]
    assert "complexity_score" not in merged_report["module1.py"]
    assert "linting" not in merged_report["module1.py"]




@mock.patch("scripts.ci.adapters.merge_reports_router.route_merge_reports")
@mock.patch("scripts.ci.adapters.merge_reports_router.get_router_data")
@mock.patch("scripts.ci.adapters.merge_reports_router.os.makedirs")
@mock.patch("scripts.ci.adapters.merge_reports_router.open", new_callable=mock.mock_open)
@mock.patch("scripts.ci.adapters.merge_reports_router.json.dump")
def test_main(
        mock_json_dump, mock_open, mock_makedirs,
        mock_get_router_data, mock_merge_reports
):
    """Test the main function."""
    # Setup mocks
    router_data = {
        "changed_files": ["scripts/module1.py"],
        "task_results": {
            "docstring": {"status": "success"},
            "test": {"status": "success"},
            "lint": {"status": "success"}
        }
    }
    mock_get_router_data.return_value = router_data

    merged_report = {
        "scripts/module1.py": {
            "docstrings": {},
            "complexity": {},
            "linting": {}
        }
    }
    mock_merge_reports.return_value = merged_report

    # Mock sys.argv
    with mock.patch('sys.argv', [
        'merge_reports_router.py',
        '--router-report', 'report.json',
        '--output', 'output.json'
    ]):
        # Import main function and run it
        from scripts.ci.adapters.merge_reports_router import main
        result = main()

    # Verify get_router_data was called
    mock_get_router_data.assert_called_once_with('report.json')

    # Verify merge_reports was called with the right arguments
    mock_merge_reports.assert_called_once()

    # Verify os.makedirs was called to create output directory
    mock_makedirs.assert_called_once()

    # Verify output was written
    mock_open.assert_called_with('output.json', 'w', encoding='utf-8')
    mock_json_dump.assert_called_once_with(merged_report, mock_open(), indent=2)

    # Verify function returned success
    assert result == 0


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])