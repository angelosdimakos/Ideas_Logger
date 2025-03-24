# tests/conftest.py

import pytest
from pathlib import Path
from unittest.mock import MagicMock

# Constants for testing using test-specific directories
MOCK_INDEX_PATH = "tests/mock_data/vector_store/test_index.faiss"
MOCK_METADATA_PATH = "tests/mock_data/vector_store/test_metadata.pkl"
MOCK_SUMMARIES_PATH = "tests/mock_data/logs/test_summaries.json"


# === OPTIONAL PATCH (No longer autouse) ===

@pytest.fixture
def mock_ai(monkeypatch):
    """
    Optional AI patch. Use in tests that don't require fallback simulation.
    """
    mock_ai = MagicMock()
    mock_ai.summarize_entries_bulk.return_value = "This is a mocked summary."
    mock_ai._fallback_summary.return_value = "Fallback summary used."
    monkeypatch.setattr("scripts.ai_summarizer.AISummarizer", lambda: mock_ai)


# === STATIC CONFIG PATCH (autouse is okay here) ===

@pytest.fixture(scope="function", autouse=True)
def patch_load_config(monkeypatch):
    test_config = {
        "batch_size": 5,
        "logs_dir": "tests/mock_data/logs",
        "export_dir": "tests/mock_data/exports",
        "correction_summaries_path": "tests/mock_data/logs/correction_summaries.json",
        "raw_log_path": "tests/mock_data/logs/zephyrus_log.json",
        "raw_log_index_path": "tests/mock_data/vector_store/raw_index.faiss",
        "raw_log_metadata_path": "tests/mock_data/vector_store/raw_metadata.pkl",
        "vector_store_dir": "tests/mock_data/vector_store",
        "faiss_index_path": "tests/mock_data/vector_store/summary_index.faiss",
        "faiss_metadata_path": "tests/mock_data/vector_store/summary_metadata.pkl",
        "force_summary_tracker_rebuild": True,
        "test_mode": True
    }
    monkeypatch.setattr("scripts.config_loader.load_config", lambda: test_config)


@pytest.fixture(scope="function", autouse=True)
def patch_get_absolute_path(monkeypatch, temp_dir):
    monkeypatch.setattr(
        "scripts.config_loader.get_absolute_path",
        lambda rel_path: str(temp_dir / rel_path)
    )


@pytest.fixture(scope="function")
def temp_dir(tmp_path):
    paths = [
        tmp_path / "logs",
        tmp_path / "exports",
        tmp_path / "vector_store"
    ]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture(scope="function")
def raw_log_path(temp_dir):
    return temp_dir / "tests/mock_data/logs/zephyrus_log.json"

@pytest.fixture(scope="function", autouse=True)
def patch_aisummarizer(monkeypatch):
    mock_ai = MagicMock()
    mock_ai.summarize_entries_bulk.return_value = "This is a mocked summary."
    mock_ai._fallback_summary.return_value = "Fallback summary used."
    monkeypatch.setattr("scripts.ai_summarizer.AISummarizer", lambda: mock_ai)

@pytest.fixture(scope="function")
def logger_core(temp_dir, monkeypatch):
    from scripts.core import ZephyrusLoggerCore
    from scripts import config_loader

    config = {
        "batch_size": 5,
        "logs_dir": str(temp_dir / "logs"),
        "export_dir": str(temp_dir / "exports"),
        "correction_summaries_path": str(temp_dir / "logs/correction_summaries.json"),
        "raw_log_path": str(temp_dir / "logs/zephyrus_log.json"),
        "force_summary_tracker_rebuild": True
    }

    monkeypatch.setattr(config_loader, "load_config", lambda: config)
    monkeypatch.setattr(config_loader, "get_absolute_path", lambda path: str(Path(path)))

    return ZephyrusLoggerCore(script_dir=temp_dir)