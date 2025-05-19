# tests/fixtures/git_fixtures.py
"""
Git Repository Testing Fixtures

This module provides fixtures for creating and cleaning up Git repositories for testing.
"""
import os
import pytest
import subprocess
import tempfile
import shutil
import time
import platform
from pathlib import Path


@pytest.fixture
def git_repo():
    """
    Creates a temporary Git repository for testing.

    Takes care of proper cleanup on all platforms, especially Windows
    where Git can keep file handles open.

    Returns:
        Path: The path to the created temporary Git repository.
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()

    try:
        # Change to the temporary directory
        os.chdir(temp_dir)

        # Initialize git
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)

        yield Path(temp_dir)
    finally:
        # Change back to original directory
        os.chdir(original_dir)

        # Windows-specific cleanup to avoid permission errors
        if platform.system() == 'Windows':
            # First, try to close any git processes that might be holding files
            try:
                subprocess.run(["taskkill", "/F", "/IM", "git.exe"],
                               stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)
            except:
                pass

            # Wait a moment for file handles to be released
            time.sleep(0.5)

            # Try to clean up files with most restrictive permissions first
            try:
                # Make files writable first
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.chmod(file_path, 0o666)
                        except:
                            pass

                # Then try cleanup
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                # If cleanup fails, just ignore - the OS will clean up temp dirs eventually
                pass
        else:
            # Non-Windows cleanup
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


@pytest.fixture
def simple_git_project(git_repo):
    """
    Creates a simple Git project with some files and commits.

    Args:
        git_repo (Path): The Git repository fixture.

    Returns:
        Path: The path to the repository with the project set up.
    """
    repo_path = git_repo

    # Create and commit initial file
    (repo_path / "initial.py").write_text("# Initial file")
    subprocess.run(["git", "add", "initial.py"], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

    # Create a branch
    subprocess.run(["git", "checkout", "-b", "test-branch"], check=True)

    # Add a new file
    (repo_path / "added.py").write_text("# Added file")

    # Modify the initial file
    (repo_path / "initial.py").write_text("# Initial file - modified")

    # Add a non-python file
    (repo_path / "other.txt").write_text("Other file")

    # Commit changes
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Add and modify files"], check=True)

    return repo_path


@pytest.fixture
def mock_python_project(git_repo):
    """
    Creates a more complex Python project structure with Git.

    Args:
        git_repo (Path): The Git repository fixture.

    Returns:
        Path: The path to the repository with the project set up.
    """
    repo_path = git_repo

    # Create project structure
    folders = [
        "app/ui",
        "app/core",
        "src/module1",
        "lib",
        "tests/ui",
        "tests/core",
        "tests/lib"
    ]

    for folder in folders:
        (repo_path / folder).mkdir(parents=True, exist_ok=True)

    # Create source files
    (repo_path / "app/ui/widget.py").write_text('def render(): return "UI Widget"')
    (repo_path / "app/core/logic.py").write_text('def process(): return "Core Logic"')
    (repo_path / "src/module1/file1.py").write_text('def function1(): return "Function 1"')
    (repo_path / "lib/utils.py").write_text('def utility(): return "Utility"')

    # Create test files
    (repo_path / "tests/ui/test_widget.py").write_text(
        'def test_widget():\n'
        '    from app.ui.widget import render\n'
        '    assert render() == "UI Widget"'
    )
    (repo_path / "tests/core/test_logic.py").write_text(
        'def test_logic():\n'
        '    from app.core.logic import process\n'
        '    assert process() == "Core Logic"'
    )
    (repo_path / "tests/test_module1_file1.py").write_text(
        'def test_function1():\n'
        '    from src.module1.file1 import function1\n'
        '    assert function1() == "Function 1"'
    )
    (repo_path / "tests/lib/test_utils.py").write_text(
        'def test_utility():\n'
        '    from lib.utils import utility\n'
        '    assert utility() == "Utility"'
    )

    # Create pytest config
    (repo_path / "pytest.ini").write_text('[pytest]\n')

    # Commit the initial state
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial project structure"], check=True)

    # Create and checkout feature branch
    subprocess.run(["git", "checkout", "-b", "feature"], check=True)

    # Make some changes for the tests to detect
    (repo_path / "app/ui/widget.py").write_text('def render(): return "Modified UI Widget"')
    (repo_path / "app/core/new_module.py").write_text('def new_function(): return "New Module"')
    (repo_path / "tests/core/test_new_module.py").write_text(
        'def test_new_module():\n'
        '    from app.core.new_module import new_function\n'
        '    assert new_function() == "New Module"'
    )

    # Commit the changes
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Modify widget and add new module"], check=True)

    return repo_path