"""
Test Data and File Fixtures

This module provides fixtures for creating mock log files, sample data files,
and other test data used in testing.
"""
import json
import pytest
from pathlib import Path


@pytest.fixture
def mock_raw_log_file(temp_dir: Path) -> Path:
    """
    Mocks a raw log file for testing.

    Args:
        temp_dir (Path): The temporary directory for the mock file.

    Returns:
        Path: The path to the mock raw log file.
    """
    path = temp_dir / "logs" / "zephyrus_log.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    content = {
        "2024-01-01": {
            "Test": {
                "Subtest": [
                    {"timestamp": "2024-01-01 10:00:00", "content": "Test entry A"},
                    {"timestamp": "2024-01-01 10:01:00", "content": "Test entry B"},
                ]
            }
        }
    }
    path.write_text(json.dumps(content), encoding="utf-8")
    return path


@pytest.fixture
def sample_lint_file(tmp_path: Path) -> str:
    """
    Provides a sample lint file for testing.

    Args:
        tmp_path (Path): The temporary path to create the sample file.

    Returns:
        str: The path to the sample lint file.
    """
    file = tmp_path / "flake8.txt"
    file.write_text(
        "scripts/core/core.py:10:1: F401 unused import\nscripts/main.py:5:5: E225 missing whitespace"
    )
    return str(file)


@pytest.fixture
def sample_refactor_file(tmp_path: Path) -> str:
    """
    Provides a sample refactor file for testing.

    Args:
        tmp_path (Path): The temporary path to create the sample file.

    Returns:
        str: The path to the sample refactor file.
    """
    file = tmp_path / "refactor_audit.json"
    data = {
        "scripts/core/core.py": {"complexity": {"func_a": {"score": 5}, "func_b": {"score": 10}}},
        "scripts/gui/gui.py": {"complexity": {"gui_main": {"score": 7}}},
    }
    file.write_text(json.dumps(data), encoding="utf-8-sig")
    return str(file)


@pytest.fixture
def real_lint_artifact() -> str:
    """
    Provides a real lint artifact for testing.

    Returns:
        str: The real lint artifact.
    """
    return Path("tests/test_data/real_lint_output.txt").read_text()


@pytest.fixture
def mock_correction_summaries_file(temp_dir: Path) -> Path:
    """
    Mocks a correction summaries file for testing.

    Args:
        temp_dir (Path): The temporary directory for the mock file.

    Returns:
        Path: The path to the mock correction summaries file.
    """
    content = {
        "global": {
            "Test": {
                "Subtest": [
                    {"corrected_summary": "Test summary A"},
                    {"original_summary": "Test summary B"},
                ]
            }
        }
    }
    path = temp_dir / "logs" / "correction_summaries.json"
    path.write_text(json.dumps(content), encoding="utf-8")
    return path