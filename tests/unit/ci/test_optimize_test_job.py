# tests/test_optimize_test_job.py
"""
Test suite for CI workflow optimization in optimize_test_job.py.

Tests generation of GitHub Actions commands and output variables.
"""
import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock
import tempfile

# Import the CI optimization scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/ci')))
from scripts.ci.optimize_test_job import (
    create_optimized_workflow,
    generate_github_output
)


class TestOptimizeTestJob:
    """Tests for GitHub Actions workflow optimization."""

    @patch('scripts.ci.optimize_test_job.update_github_workflow_test_job')
    def test_create_optimized_workflow_all(self, mock_update):
        """Test creating workflow step for running all tests."""
        mock_update.return_value = {
            "run_all": True,
            "test_command": "xvfb-run -a pytest -n auto -c pytest.ini"
        }

        workflow = create_optimized_workflow("origin/main", "HEAD")

        assert "Running ALL tests" in workflow
        assert "xvfb-run -a pytest" in workflow

    @patch('scripts.ci.optimize_test_job.update_github_workflow_test_job')
    def test_create_optimized_workflow_targeted(self, mock_update):
        """Test creating workflow step for targeted tests."""
        mock_update.return_value = {
            "run_all": False,
            "test_commands": [
                "pytest -n auto tests/test_module.py",
                "xvfb-run -a pytest -n auto tests/ui/test_widget.py"
            ],
            "has_regular": True,
            "has_gui": True
        }

        workflow = create_optimized_workflow("origin/main", "HEAD")

        assert "Running TARGETED tests" in workflow
        assert "test_module.py" in workflow
        assert "test_widget.py" in workflow

    # tests/unit/ci/test_optimize_test_job.py

    @patch('scripts.ci.optimize_test_job.update_github_workflow_test_job')
    def test_generate_github_output_all(self, mock_update):
        """Test generating GitHub output variables for all tests."""
        mock_update.return_value = {
            "run_all": True,
            "test_command": "xvfb-run -a pytest -n auto -c pytest.ini"
        }

        # Use our own temp file directly instead of NamedTemporaryFile
        temp_file = os.path.join(tempfile.gettempdir(), f"github_output_{os.getpid()}.txt")
        try:
            generate_github_output("origin/main", "HEAD", temp_file)

            # Read the file
            with open(temp_file, 'r') as f:
                content = f.read()

            # Check output variables
            assert "run_all=true" in content
            assert "test_commands=" in content
            assert "has_regular=false" in content
            assert "has_gui=false" in content
            assert "command_count=1" in content
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    @patch('scripts.ci.optimize_test_job.update_github_workflow_test_job')
    def test_generate_github_output_targeted(self, mock_update):
        """Test generating GitHub output variables for targeted tests."""
        mock_update.return_value = {
            "run_all": False,
            "test_commands": [
                "pytest -n auto tests/test_module.py",
                "xvfb-run -a pytest -n auto tests/ui/test_widget.py"
            ],
            "has_regular": True,
            "has_gui": True
        }

        # Use our own temp file directly
        temp_file = os.path.join(tempfile.gettempdir(), f"github_output_{os.getpid()}_2.txt")
        try:
            generate_github_output("origin/main", "HEAD", temp_file)

            # Read the file
            with open(temp_file, 'r') as f:
                content = f.read()

            # Check output variables
            assert "run_all=false" in content
            assert "test_commands=" in content
            assert "has_regular=true" in content
            assert "has_gui=true" in content
            assert "command_count=2" in content
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)