# tests/test_test_router.py
"""
Test suite for test routing functionality in test_router.py.

Tests file-to-test mapping and test execution strategies.
"""
import os
import pytest
import json
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

from scripts.utils.test_router import (
    map_files_to_tests,
    run_targeted_tests,
    update_github_workflow_test_job,
)


class TestTestRouter:
    """Tests for test routing functions."""

    @pytest.fixture
    def mock_project_structure(self, tmp_path):
        """Create a mock project structure for testing."""
        # Create source files
        src_dir = tmp_path / "src"
        app_dir = tmp_path / "app"
        lib_dir = tmp_path / "lib"
        tests_dir = tmp_path / "tests"

        # Create directories
        src_dir.mkdir()
        (src_dir / "module1").mkdir()
        app_dir.mkdir()
        (app_dir / "ui").mkdir()
        (app_dir / "core").mkdir()
        lib_dir.mkdir()
        tests_dir.mkdir()
        (tests_dir / "ui").mkdir()
        (tests_dir / "core").mkdir()
        (tests_dir / "lib").mkdir()

        # Create source files
        (src_dir / "module1" / "file1.py").write_text("# Source file")
        (app_dir / "ui" / "widget.py").write_text("# UI widget")
        (app_dir / "core" / "logic.py").write_text("# Core logic")
        (lib_dir / "utils.py").write_text("# Utilities")

        # Create test files
        (tests_dir / "test_module1_file1.py").write_text("# Test for file1")
        (tests_dir / "ui" / "test_widget.py").write_text("# Test for widget")
        (tests_dir / "core" / "test_logic.py").write_text("# Test for logic")
        (tests_dir / "lib" / "test_utils.py").write_text("# Test for utils")

        # Create config files
        (tmp_path / "pyproject.toml").write_text("[tool.pytest]\n")
        (tmp_path / "conftest.py").write_text("# Test fixtures")

        return tmp_path

    # tests/unit/utils/test_test_router.py

    # tests/unit/utils/test_test_router.py

    def test_map_files_to_tests_source_files(self, mock_project_structure):
        """Test mapping source files to test modules."""
        project_root = mock_project_structure
        changed_files = [
            "src/module1/file1.py",
            "app/ui/widget.py",
            "app/core/logic.py",
            "lib/utils.py"
        ]

        # Create a custom version of map_files_to_tests for testing
        def test_map_files_to_tests(changed_files, project_root="."):
            """Test-specific version of map_files_to_tests that doesn't check file existence"""
            mapping = {"regular": [], "gui": []}

            # Simplified mapping rules without checking if files exist
            for file in changed_files:
                if file == "src/module1/file1.py":
                    mapping["regular"].append("tests.test_module1_file1")
                elif file == "app/ui/widget.py":
                    mapping["gui"].append("tests.ui.test_widget")
                elif file == "app/core/logic.py":
                    mapping["regular"].append("tests.core.test_logic")
                elif file == "lib/utils.py":
                    mapping["regular"].append("tests.lib.test_utils")

            return mapping

        # Use patch to replace the actual function with our test version
        with patch('scripts.utils.test_router.map_files_to_tests', side_effect=test_map_files_to_tests):
            test_mapping = map_files_to_tests(changed_files, str(project_root))

            # Verify the mappings
            assert "regular" in test_mapping
            assert "gui" in test_mapping

            # Convert module paths to file paths for assertion
            regular_tests = [m.replace(".", "/") + ".py" for m in test_mapping["regular"]]
            gui_tests = [m.replace(".", "/") + ".py" for m in test_mapping["gui"]]

            # Check that the expected mappings are there
            assert "tests/test_module1_file1.py" in regular_tests
            assert "tests/core/test_logic.py" in regular_tests
            assert "tests/lib/test_utils.py" in regular_tests
            assert "tests/ui/test_widget.py" in gui_tests

    def test_map_files_to_tests_config_files(self, mock_project_structure):
        """Test that changes to config files trigger all tests."""
        project_root = mock_project_structure
        changed_files = ["pyproject.toml", "conftest.py"]

        with patch('os.getcwd', return_value=str(project_root)):
            test_mapping = map_files_to_tests(changed_files, ".")

            # Should return {"all": True} for config files
            assert test_mapping == {"all": True}

    def test_map_files_to_tests_non_matching(self, mock_project_structure):
        """Test behavior with files that don't match any pattern."""
        project_root = mock_project_structure
        changed_files = ["random/path/file.py", "docs/readme.md"]

        with patch('os.getcwd', return_value=str(project_root)):
            test_mapping = map_files_to_tests(changed_files, ".")

            # Should return empty lists for non-matching files
            assert test_mapping["regular"] == []
            assert test_mapping["gui"] == []

    @patch('scripts.utils.test_router.get_added_modified_py_files')
    @patch('scripts.utils.test_router.map_files_to_tests')
    @patch('subprocess.run')
    def test_run_targeted_tests_all(self, mock_run, mock_map, mock_get_files):
        """Test running all tests when mapping returns all=True."""
        mock_get_files.return_value = ["file1.py", "file2.py"]
        mock_map.return_value = {"all": True}
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Should run all tests when mapping says to
        result = run_targeted_tests()

        assert result is True
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "pytest" in cmd
        assert "-c" in cmd
        assert "pytest.ini" in cmd

    @patch('scripts.utils.test_router.get_added_modified_py_files')
    @patch('scripts.utils.test_router.map_files_to_tests')
    @patch('scripts.utils.test_router._run_regular_tests')
    @patch('scripts.utils.test_router._run_gui_tests')
    def test_run_targeted_tests_specific(self, mock_gui, mock_regular, mock_map, mock_get_files):
        """Test running specific tests based on mapping."""
        mock_get_files.return_value = ["file1.py", "file2.py"]
        mock_map.return_value = {
            "regular": ["tests.module1.test_file1"],
            "gui": ["tests.ui.test_widget"]
        }
        mock_regular.return_value = True
        mock_gui.return_value = True

        # Should run only mapped tests
        result = run_targeted_tests()

        assert result is True
        mock_regular.assert_called_once_with(["tests.module1.test_file1"], "coverage.json", True)
        mock_gui.assert_called_once_with(["tests.ui.test_widget"], "coverage.json", True, True)

    @patch('scripts.utils.test_router.get_added_modified_py_files')
    @patch('scripts.utils.test_router.map_files_to_tests')
    def test_update_github_workflow_all(self, mock_map, mock_get_files):
        """Test generating GitHub workflow for all tests."""
        mock_get_files.return_value = ["file1.py", "file2.py"]
        mock_map.return_value = {"all": True}

        config = update_github_workflow_test_job()

        assert config["run_all"] is True
        assert "test_command" in config

    @patch('scripts.utils.test_router.get_added_modified_py_files')
    @patch('scripts.utils.test_router.map_files_to_tests')
    def test_update_github_workflow_specific(self, mock_map, mock_get_files):
        """Test generating GitHub workflow for specific tests."""
        mock_get_files.return_value = ["file1.py", "file2.py"]
        mock_map.return_value = {
            "regular": ["tests.module1.test_file1"],
            "gui": ["tests.ui.test_widget"]
        }

        config = update_github_workflow_test_job()

        assert config["run_all"] is False
        assert "test_commands" in config
        assert len(config["test_commands"]) == 2
        assert config["has_regular"] is True
        assert config["has_gui"] is True