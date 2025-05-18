#!/usr/bin/env python3
"""
Unit tests for RefactorGuard Router Adapter
=========================================
Tests the functionality of the RefactorGuard Router adapter script without
executing actual refactor guard analysis or touching the filesystem.

Run with:
    pytest -xvs tests/ci/test_refactor_guard_router.py
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
from scripts.ci.adapters.refactor_guard_router import (
    parse_args,
    handle_router_based_scan
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


def test_parse_args():
    """Test argument parsing."""
    # Test with required args only
    with mock.patch('sys.argv', ['refactor_guard_router.py', '--router-report', 'report.json']):
        args = parse_args()
        assert args.router_report == 'report.json'
        assert args.refactored == 'scripts'
        assert args.tests == 'tests'
        assert args.coverage_path == '.coverage'
        assert not args.json
        assert args.output == 'refactor_audit.json'

    # Test with all args
    with mock.patch('sys.argv', [
        'refactor_guard_router.py',
        '--router-report', 'report.json',
        '--refactored', 'custom_scripts',
        '--tests', 'custom_tests',
        '--coverage-path', 'custom_coverage.json',
        '--json',
        '--output', 'custom_output.json'
    ]):
        args = parse_args()
        assert args.router_report == 'report.json'
        assert args.refactored == 'custom_scripts'
        assert args.tests == 'custom_tests'
        assert args.coverage_path == 'custom_coverage.json'
        assert args.json
        assert args.output == 'custom_output.json'


@mock.patch("scripts.ci.adapters.refactor_guard_router.Path.exists")
@mock.patch("scripts.ci.adapters.refactor_guard_router.open", new_callable=mock.mock_open)
@mock.patch("scripts.ci.adapters.refactor_guard_router.json.load")
@mock.patch("scripts.ci.adapters.refactor_guard_router.print")  # Silence the print statements
def test_handle_router_based_scan(
        mock_print, mock_json_load, mock_open, mock_exists
):
    """Test handle_router_based_scan function."""
    # Setup mocks
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "changed_files": [
            "scripts/module1.py",
            "scripts/module2.py",
            "tests/test_module1.py"
        ]
    }

    # Create mock args
    args = mock.Mock()
    args.router_report = "report.json"
    args.refactored = "scripts"
    args.tests = "tests"
    args.coverage_path = "coverage.json"

    # Create mock guard
    guard = mock.Mock()
    guard.analyze_module.return_value = {"complexity": {}, "diff": {}}
    guard.config = {}

    # Run the function
    results = handle_router_based_scan(args, guard)

    # Verify json.load was called to read the router report
    mock_json_load.assert_called_once()

    # Verify analyze_module was called for each Python file
    assert guard.analyze_module.call_count == 2  # For module1.py and module2.py

    # Verify the results - should have results for Python files, excluding test files
    assert len(results) == 2

    # Test with nonexistent router report
    mock_json_load.reset_mock()
    mock_json_load.side_effect = FileNotFoundError

    with pytest.raises(SystemExit):
        handle_router_based_scan(args, guard)


@mock.patch("scripts.ci.adapters.refactor_guard_router.handle_router_based_scan")
@mock.patch("scripts.ci.adapters.refactor_guard_router.RefactorGuard")
@mock.patch("scripts.ci.adapters.refactor_guard_router.Path.write_text")
def test_main(mock_write_text, mock_refactor_guard, mock_handle_router_based_scan):
    """Test the main function."""
    # Setup mocks
    mock_guard_instance = mock.Mock()
    # Make config a dictionary to support item assignment
    mock_guard_instance.config = {}
    mock_refactor_guard.return_value = mock_guard_instance

    mock_handle_router_based_scan.return_value = {
        "module1.py": {"complexity": {}, "diff": {}},
        "module2.py": {"complexity": {}, "diff": {}}
    }

    # Mock sys.argv
    with mock.patch('sys.argv', [
        'refactor_guard_router.py',
        '--router-report', 'report.json',
        '--json',
        '--output', 'output.json'
    ]):
        # Import and run main function
        from scripts.ci.adapters.refactor_guard_router import main
        result = main()

    # Verify RefactorGuard was instantiated
    mock_refactor_guard.assert_called_once()

    # Verify handle_router_based_scan was called with the right arguments
    mock_handle_router_based_scan.assert_called_once()

    # Verify output was written
    mock_write_text.assert_called_once()

    # Verify function returned success
    assert result == 0

    # Test without json output
    mock_write_text.reset_mock()

    with mock.patch('sys.argv', [
        'refactor_guard_router.py',
        '--router-report', 'report.json'
    ]):
        # Import and run main function
        from scripts.ci.adapters.refactor_guard_router import main
        with mock.patch('scripts.ci.adapters.refactor_guard_router.print_human_readable') as mock_print:
            result = main()
            mock_print.assert_called_once()

    # Verify no JSON output was written
    mock_write_text.assert_not_called()

    # Verify function returned success
    assert result == 0


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])