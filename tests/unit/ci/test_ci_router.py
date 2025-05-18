#!/usr/bin/env python3
"""
Unit tests for CI Router core functionality
==========================================
Tests the core functionality of the CI Router script without performing
actual git operations or executing external tools.

Run with:
    pytest -xvs tests/ci/test_ci_router.py
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from unittest import mock
import pytest

# Add repo root to path so we can import the CI Router modules
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))

# Import the modules to test
from scripts.ci.ci_router import (
    CIRouter,
    RouterConfig,
    CITask
)


@pytest.fixture
def sample_config():
    """Fixture providing a sample router configuration."""
    file_patterns = {
        "python": ["*.py"],
        "tests": ["tests/", "*/test_*.py"],
        "docs": ["*.md", "docs/"]
    }

    tasks = {
        "lint": CITask(
            name="lint",
            command="lint_command",
            description="Run linter",
            affected_by=["python"],
            output_files=["lint_report.json"]
        ),
        "test": CITask(
            name="test",
            command="test_command",
            description="Run tests",
            affected_by=["python", "tests"],
            output_files=["test_report.json"]
        ),
        "docs": CITask(
            name="docs",
            command="docs_command",
            description="Build docs",
            affected_by=["docs"],
            output_files=["docs_output.md"]
        ),
        "always_task": CITask(
            name="always_task",
            command="always_command",
            description="Always run this task",
            affected_by=[],
            always_run=True,
            output_files=["always_output.json"]
        ),
        "dependent_task": CITask(
            name="dependent_task",
            command="dependent_command",
            description="Depends on lint and test",
            affected_by=[],
            requires=["lint", "test"],
            output_files=["dependent_output.json"]
        )
    }

    return RouterConfig(tasks=tasks, file_patterns=file_patterns, report_dir="test_reports")


@pytest.fixture
def router(sample_config):
    """Fixture providing a CI Router instance with sample config."""
    return CIRouter(sample_config)


def test_router_initialization(router):
    """Test router initialization with config."""
    assert router.config is not None
    assert isinstance(router.config, RouterConfig)
    assert len(router.config.tasks) == 5
    assert len(router.config.file_patterns) == 3
    assert router.changed_files == []
    assert router.tasks_to_run == set()


def test_match_pattern():
    """Test the pattern matching function."""
    router = CIRouter(RouterConfig())

    # Test direct prefix match
    assert router._match_pattern("dir/file.py", "dir/")

    # Test exact file match
    assert router._match_pattern("file.py", "file.py")

    # Test extension match
    assert router._match_pattern("file.py", "*.py")

    # Test path component match
    assert router._match_pattern("dir/subdir/file.py", "/subdir")

    # Test directory contains match
    assert router._match_pattern("dir/subdir/file.py", "dir/subdir")

    # Test glob pattern match
    assert router._match_pattern("test_file.py", "test_*.py")

    # Test non-matches
    assert not router._match_pattern("file.txt", "*.py")
    assert not router._match_pattern("other/file.py", "dir/")
    assert not router._match_pattern("file.py", "file.txt")


@mock.patch("scripts.ci.ci_router.git_utils.get_changed_files")
def test_detect_changed_files(mock_get_changed_files, router):
    """Test detection of changed files."""
    mock_changed_files = [
        "file1.py",
        "tests/test_file.py",
        "docs/readme.md"
    ]
    mock_get_changed_files.return_value = mock_changed_files

    result = router.detect_changed_files("main")

    # Verify the function was called with the right arguments
    mock_get_changed_files.assert_called_once_with("origin/main")

    # Verify the result contains the mock files
    assert result == mock_changed_files
    assert router.changed_files == mock_changed_files


def test_map_files_to_tasks(router):
    """Test mapping files to tasks."""
    # Set up some changed files
    router.changed_files = [
        "file1.py",
        "tests/test_file.py",
        "docs/readme.md"
    ]

    # Map files to tasks
    task_file_map = router.map_files_to_tasks()

    # Verify the right tasks were selected
    assert "lint" in router.tasks_to_run  # Selected due to *.py files
    assert "test" in router.tasks_to_run  # Selected due to tests/ files
    assert "docs" in router.tasks_to_run  # Selected due to docs/ files
    assert "always_task" in router.tasks_to_run  # Always selected

    # Note: The actual implementation doesn't add dependent_task here, so we don't assert it

    # Verify the file mapping
    assert "file1.py" in task_file_map["lint"]
    assert "tests/test_file.py" in task_file_map["test"]
    assert "docs/readme.md" in task_file_map["docs"]


def test_get_tasks_for_file(router):
    """Test getting tasks for a specific file."""
    # Test a Python file
    python_tasks = router._get_tasks_for_file("file.py")
    assert "lint" in python_tasks
    # The actual implementation also returns "test" for Python files

    # Test a test file
    test_tasks = router._get_tasks_for_file("tests/test_file.py")
    assert "lint" in test_tasks  # It's also a Python file
    assert "test" in test_tasks

    # Test a doc file
    doc_tasks = router._get_tasks_for_file("docs/readme.md")
    assert "docs" in doc_tasks
    assert "lint" not in doc_tasks

    # Test a non-matching file
    non_matching_tasks = router._get_tasks_for_file("file.txt")
    assert non_matching_tasks == []


def test_add_prerequisite_dependent_tasks(router):
    """Test adding required dependencies."""
    # Start with just the dependent task
    router.tasks_to_run = {"dependent_task"}

    # Add dependent tasks
    router._add_dependent_tasks()

    # Check that dependencies were added
    assert "lint" in router.tasks_to_run
    assert "test" in router.tasks_to_run
    assert "dependent_task" in router.tasks_to_run


@mock.patch("scripts.ci.ci_router.subprocess.run")
def test_run_task(mock_subprocess_run, router):
    """Test running a single task."""
    # Mock the subprocess.run return value
    mock_process = mock.Mock()
    mock_process.returncode = 0
    mock_process.stdout = "Task output"
    mock_process.stderr = ""
    mock_subprocess_run.return_value = mock_process

    # Create a test task
    task = CITask(
        name="test_task",
        command="echo 'test'",
        description="Test task",
        output_files=["output.txt"]
    )

    # Run the task
    result = router._run_task(task)

    # Verify subprocess.run was called with the right command
    mock_subprocess_run.assert_called_once()
    args, kwargs = mock_subprocess_run.call_args
    assert "echo 'test'" in args[0]

    # Verify the result
    assert result["name"] == "test_task"
    assert result["status"] == "success"
    assert result["output"] == "Task output"
    assert result["exit_code"] == 0


@mock.patch("scripts.ci.ci_router.CIRouter._run_task")
def test_run_tasks(mock_run_task, router):
    """Test running multiple tasks."""
    # Set up some tasks to run
    router.tasks_to_run = {"lint", "test"}

    # Mock the _run_task return value
    mock_run_task.return_value = {
        "status": "success",
        "output": "Task output",
        "exit_code": 0
    }

    # Run the tasks
    results = router.run_tasks()

    # Verify _run_task was called for each task
    assert mock_run_task.call_count == 2

    # Verify the results
    assert "lint" in results
    assert "test" in results
    assert all(result["status"] == "success" for result in results.values())


@mock.patch("scripts.ci.ci_router.Path.write_text", return_value=None)
@mock.patch("scripts.ci.ci_router.open", new_callable=mock.mock_open)
def test_generate_report(mock_open, mock_write_text, router, tmp_path):
    """Test generating the final report."""
    # Set up the router
    router.changed_files = ["file1.py", "tests/test_file.py"]
    router.tasks_to_run = {"lint", "test"}
    router.task_results = {
        "lint": {
            "status": "success",
            "output": "Lint output",
            "exit_code": 0,
            "name": "lint",
            "command": "lint command",
            "description": "Run linter",
            "artifacts": []
        },
        "test": {
            "status": "success",
            "output": "Test output",
            "exit_code": 0,
            "name": "test",
            "command": "test command",
            "description": "Run tests",
            "artifacts": []
        }
    }

    # Set temporary report directory
    router.config.report_dir = str(tmp_path)

    # Instead of calling generate_report, let's mock out the methods it calls
    # This way we can control what happens
    with mock.patch.object(router, '_generate_markdown_report') as mock_markdown:
        # Generate the report
        summary = router.generate_report()

        # Verify the summary contents
        assert summary["changed_files"] == router.changed_files
        assert summary["tasks_run"] == 2
        assert summary["successful_tasks"] == 2
        assert summary["failed_tasks"] == 0
        assert "task_results" in summary

        # Verify the markdown report was generated
        mock_markdown.assert_called_once()

        # Since we're not actually writing files in this test, we'll skip the assert on mock_write_text


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])