# tests/integration/test_git_test_router_integration.py
"""
Integration tests for Git utilities and test router.

Tests the end-to-end flow from detecting changes to running tests.
"""
import os
import pytest
import subprocess
import tempfile
import shutil
import time
import platform
from scripts.utils.git_utils import get_added_modified_py_files
from scripts.utils.test_router import map_files_to_tests, run_targeted_tests
from pathlib import Path


@pytest.mark.integration
class TestGitTestRouterIntegration:
    """Integration tests for Git and test routing."""



    @pytest.fixture
    def mock_project(self):
        """Create a mock project with Git and test files."""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        original_dir = os.getcwd()

        try:
            # Change to the temporary directory
            os.chdir(temp_dir)
            print(f"Created temp dir: {temp_dir}")

            # Create project structure with pathlib for better cross-platform support
            project_structure = {
                'app/ui/widget.py': 'def render(): return "UI Widget"',
                'app/core/logic.py': 'def process(): return "Core Logic"',
                'tests/ui/test_widget.py': 'def test_widget():\n    from app.ui.widget import render\n    assert render() == "UI Widget"',
                'tests/core/test_logic.py': 'def test_logic():\n    from app.core.logic import process\n    assert process() == "Core Logic"',
                'pytest.ini': '[pytest]\n'
            }

            # Create all files using pathlib
            for filepath, content in project_structure.items():
                path = Path(temp_dir) / filepath
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)

            # Initialize git with explicit config to avoid global config issues
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "config", "--local", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "config", "--local", "user.name", "Test User"], check=True)
            # Disable autocrlf to avoid line ending issues
            subprocess.run(["git", "config", "--local", "core.autocrlf", "false"], check=True)

            # Stage and commit initial files
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

            # Create main branch explicitly (for newer Git versions that use 'main' instead of 'master')
            subprocess.run(["git", "branch", "-M", "master"], check=True)

            # Create and checkout feature branch
            subprocess.run(["git", "checkout", "-b", "feature"], check=True)

            # Make changes to test
            widget_path = Path(temp_dir) / 'app/ui/widget.py'
            widget_path.write_text('def render(): return "Modified UI Widget"')

            new_module_path = Path(temp_dir) / 'app/core/new_module.py'
            new_module_path.write_text('def new_function(): return "New Module"')

            new_test_path = Path(temp_dir) / 'tests/core/test_new_module.py'
            new_test_path.write_text(
                'def test_new_module():\n    from app.core.new_module import new_function\n    assert new_function() == "New Module"')

            # Stage and commit changes
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Modify widget and add new module"], check=True)

            # Verify the commits were made
            log_output = subprocess.check_output(["git", "log", "--oneline"]).decode()
            print(f"Git log:\n{log_output}")

            yield temp_dir
        except Exception as e:
            print(f"Error in mock_project setup: {e}")
            raise
        finally:
            # Change back to original directory
            os.chdir(original_dir)

            # Windows-specific cleanup handling
            if platform.system() == 'Windows':
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "git.exe"],
                                   stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)
                    time.sleep(0.5)
                except:
                    pass

                # Try to clean up with ignore_errors=True
                shutil.rmtree(temp_dir, ignore_errors=True)
            else:
                shutil.rmtree(temp_dir, ignore_errors=True)

    def test_end_to_end_flow(self, mock_project):
        """Test the end-to-end flow from detecting changes to mapping tests."""
        os.chdir(mock_project)

        # Wait for Git operations to complete and print debug info
        print(f"Current directory: {os.getcwd()}")
        print(f"Git status:")
        subprocess.run(["git", "status"], check=False)
        print(f"Git log:")
        subprocess.run(["git", "log", "--oneline"], check=False)
        print(f"Git branch:")
        subprocess.run(["git", "branch"], check=False)

        # Explicitly check if we're on feature branch
        current_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
        print(f"Current branch: {current_branch}")

        # Force checkout to feature branch if needed
        if current_branch != "feature":
            subprocess.run(["git", "checkout", "feature"], check=True)

        # Use a try-except to provide better error info
        try:
            # Get changed files - use 'master' explicitly instead of relying on 'origin/main'
            changed_files = get_added_modified_py_files("master", "feature")

            print(f"Found changed files: {changed_files}")

            # Verify we found the right files
            assert len(changed_files) > 0, "No changed files found! Git diff failed."
            assert "app/ui/widget.py" in changed_files, "Modified widget file not detected"
            assert "app/core/new_module.py" in changed_files, "New module file not detected"

            # Map files to tests
            test_mapping = map_files_to_tests(changed_files)

            # Check that mapping worked correctly
            assert "regular" in test_mapping
            assert "gui" in test_mapping

            # Print test mapping for debugging
            print(f"Test mapping: {test_mapping}")

            # The GUI tests should include the widget test
            gui_test_modules = test_mapping.get("gui", [])
            assert any("test_widget" in test for test in gui_test_modules), "Widget test not found in GUI tests"

        except Exception as e:
            print(f"Test failed with error: {e}")
            # Print git diff output for debugging
            print("Git diff output:")
            subprocess.run(["git", "diff", "--name-only", "master", "feature"], check=False)
            raise

    @pytest.mark.skip(reason="This test actually runs pytest and might be slow")
    def test_run_targeted_tests_integration(self, mock_project):
        """Integration test for running targeted tests."""
        os.chdir(mock_project)

        # Install pytest for the test
        subprocess.run(["pip", "install", "pytest", "pytest-cov"], check=True)

        # Run targeted tests
        result = run_targeted_tests("master", "feature", "coverage.json", py_only=True)

        # Check that tests ran successfully
        assert result is True
        assert os.path.exists("coverage.json")