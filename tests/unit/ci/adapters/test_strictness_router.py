#!/usr/bin/env python3
"""
Unit tests for Strictness Router Adapter
======================================
Tests the functionality of the Strictness Router adapter script without
executing actual strictness analysis or touching the filesystem.

Run with:
    pytest -xvs tests/ci/test_strictness_router.py
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
from scripts.ci.adapters.strictness_router import (
    parse_args,
    get_affected_modules,
    filter_test_report
)


@pytest.fixture
def sample_router_report():
    """Fixture providing a sample router report JSON."""
    return {
        "changed_files": [
            "scripts/module1.py",
            "scripts/module2.py",
            "scripts/subdir/module3.py",
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
def sample_test_report():
    """Fixture providing a sample test report."""
    return [
        {
            "name": "test_function1",
            "file": "tests/test_module1.py",
            "strictness_score": 0.8,
            "severity_score": 0.5
        },
        {
            "name": "TestModule1.test_method",
            "file": "tests/test_module1.py",
            "strictness_score": 0.9,
            "severity_score": 0.6
        },
        {
            "name": "test_function2",
            "file": "tests/test_module2.py",
            "strictness_score": 0.7,
            "severity_score": 0.4
        },
        {
            "name": "test_module3_function",
            "file": "tests/test_module3.py",
            "strictness_score": 0.6,
            "severity_score": 0.3
        }
    ]


@pytest.fixture
def temp_router_report(sample_router_report, tmp_path):
    """Fixture providing a temporary router report file."""
    report_path = tmp_path / "router_summary.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(sample_router_report, f)
    return str(report_path)


@pytest.fixture
def temp_test_report(sample_test_report, tmp_path):
    """Fixture providing a temporary test report file."""
    report_path = tmp_path / "test_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({"tests": sample_test_report}, f)
    return str(report_path)


def test_parse_args():
    """Test argument parsing."""
    # Test with required args only
    with mock.patch('sys.argv', [
        'strictness_router.py',
        '--router-report', 'router_report.json',
        '--test-report', 'test_report.json',
        '--audit', 'audit.json'
    ]):
        args = parse_args()
        assert args.router_report == 'router_report.json'
        assert args.test_report == 'test_report.json'
        assert args.audit == 'audit.json'
        assert args.output == './artifacts/final_strictness_report.json'

    # Test with all args
    with mock.patch('sys.argv', [
        'strictness_router.py',
        '--router-report', 'router_report.json',
        '--test-report', 'test_report.json',
        '--audit', 'audit.json',
        '--output', 'custom_output.json'
    ]):
        args = parse_args()
        assert args.router_report == 'router_report.json'
        assert args.test_report == 'test_report.json'
        assert args.audit == 'audit.json'
        assert args.output == 'custom_output.json'


@mock.patch("scripts.ci.adapters.strictness_router.print")  # Silence the print statements
def test_get_affected_modules(mock_print, temp_router_report):
    """Test getting affected modules from router report."""
    # Test with valid report
    affected_modules = get_affected_modules(temp_router_report)
    # Don't assert exact count, just check important entries
    assert "module1" in affected_modules
    assert "module2" in affected_modules
    assert "module3" in affected_modules
    assert "subdir" in affected_modules
    assert "test_module1" in affected_modules

    # Test with nonexistent report
    affected_modules = get_affected_modules("nonexistent_report.json")
    assert len(affected_modules) == 0

    # Test with invalid JSON
    with mock.patch("scripts.ci.adapters.strictness_router.open", mock.mock_open(read_data="invalid json")):
        affected_modules = get_affected_modules("invalid.json")
        assert len(affected_modules) == 0


def test_filter_test_report(sample_test_report):
    """Test filtering test report based on affected modules."""
    # Setup affected modules
    affected_modules = {"module1", "subdir"}

    # Filter test report
    filtered_tests = filter_test_report(sample_test_report, affected_modules)

    assert len(filtered_tests) == 2
    assert filtered_tests[0]["name"] == "test_function1"
    assert filtered_tests[1]["name"] == "TestModule1.test_method"

    # Test with additional patterns
    affected_modules = {"module3"}
    filtered_tests = filter_test_report(sample_test_report, affected_modules)

    assert len(filtered_tests) == 1
    assert filtered_tests[0]["name"] == "test_module3_function"

    # Test with no matching modules
    affected_modules = {"nonexistent_module"}
    filtered_tests = filter_test_report(sample_test_report, affected_modules)

    assert len(filtered_tests) == 0

    # Test with empty affected modules
    affected_modules = set()
    filtered_tests = filter_test_report(sample_test_report, affected_modules)

    assert len(filtered_tests) == 0


@mock.patch("scripts.ci.adapters.strictness_router.load_audit_report")
@mock.patch("scripts.ci.adapters.strictness_router.load_test_report")
@mock.patch("scripts.ci.adapters.strictness_router.generate_module_report")
@mock.patch("scripts.ci.adapters.strictness_router.validate_report_schema")
@mock.patch("scripts.ci.adapters.strictness_router.get_affected_modules")
@mock.patch("scripts.ci.adapters.strictness_router.filter_test_report")
@mock.patch("scripts.ci.adapters.strictness_router.os.makedirs")
@mock.patch("scripts.ci.adapters.strictness_router.open", new_callable=mock.mock_open)
@mock.patch("scripts.ci.adapters.strictness_router.json.dump")
def test_main(
        mock_json_dump, mock_open, mock_makedirs, mock_filter_test_report,
        mock_get_affected_modules, mock_validate, mock_generate_report,
        mock_load_test_report, mock_load_audit_report
):
    """Test the main function."""
    # Setup mocks
    affected_modules = {"module1", "module2"}
    mock_get_affected_modules.return_value = affected_modules

    filtered_tests = [
        {
            "name": "test_function1",
            "file": "tests/test_module1.py",
            "strictness_score": 0.8,
            "severity_score": 0.5
        }
    ]
    mock_filter_test_report.return_value = filtered_tests

    test_report = [
        {
            "name": "test_function1",
            "file": "tests/test_module1.py",
            "strictness_score": 0.8,
            "severity_score": 0.5
        }
    ]
    mock_load_test_report.return_value = test_report

    audit_model = mock.Mock()
    mock_load_audit_report.return_value = audit_model

    mock_validate.return_value = True

    module_report = {
        "module1.py": {
            "module_coverage": 0.8,
            "methods": [],
            "tests": []
        }
    }
    mock_generate_report.return_value = module_report

    # Mock sys.argv
    with mock.patch('sys.argv', [
        'strictness_router.py',
        '--router-report', 'router_report.json',
        '--test-report', 'test_report.json',
        '--audit', 'audit.json',
        '--output', 'output.json'
    ]):
        # Import and run main function
        from scripts.ci.adapters.strictness_router import main
        main()

    # Verify get_affected_modules was called
    mock_get_affected_modules.assert_called_once_with('router_report.json')

    # Verify load_test_report was called
    mock_load_test_report.assert_called_once_with('test_report.json')

    # Verify filter_test_report was called
    mock_filter_test_report.assert_called_once_with(test_report, affected_modules)

    # Verify load_audit_report was called
    mock_load_audit_report.assert_called_once_with('audit.json')

    # Verify generate_module_report was called
    mock_generate_report.assert_called_once()

    # Verify validate_report_schema was called
    mock_validate.assert_called_once_with(module_report)

    # Verify makedirs was called
    mock_makedirs.assert_called_once()

    # Verify output was written
    mock_open.assert_called_with('output.json', 'w', encoding='utf-8')
    mock_json_dump.assert_called_once_with(module_report, mock_open(), indent=2)

    # Test with no affected modules
    mock_get_affected_modules.return_value = set()
    mock_filter_test_report.return_value = []
    mock_open.reset_mock()
    mock_json_dump.reset_mock()
    mock_generate_report.reset_mock()

    with mock.patch('sys.argv', [
        'strictness_router.py',
        '--router-report', 'router_report.json',
        '--test-report', 'test_report.json',
        '--audit', 'audit.json',
        '--output', 'output.json'
    ]):
        # Import and run main function
        from scripts.ci.adapters.strictness_router import main
        main()

    # Verify empty output was written
    mock_open.assert_called_with('output.json', 'w', encoding='utf-8')
    mock_json_dump.assert_called_once_with({}, mock_open(), indent=2)
    mock_generate_report.assert_not_called()


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])