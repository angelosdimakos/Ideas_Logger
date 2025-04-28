"""
Core Application Fixtures

This module provides fixtures for testing core application components like
the logger core, summary tracker, and indexers.
"""
import pytest
import numpy as np
from unittest.mock import MagicMock
from pathlib import Path
from typing import Any


# ===========================
# 🧠 CORE LOGGER FIXTURE
# ===========================
@pytest.fixture
def logger_core(temp_dir: Path) -> Any:
    """
    Creates a logger core for testing.

    Args:
        temp_dir (Path): The temporary directory for the logger core.

    Returns:
        Any: The logger core.
    """
    from scripts.core.core import ZephyrusLoggerCore

    return ZephyrusLoggerCore(script_dir=temp_dir)


# ===========================
# 🔀 STATE CLEANUP FIXTURES
# ===========================
@pytest.fixture
def clean_summary_tracker(logger_core: Any) -> None:
    """
    Cleans the summary tracker for testing.

    Args:
        logger_core (Any): The logger core to clean.
    """
    logger_core.summary_tracker.tracker_file.write_text("{}", encoding="utf-8")
    yield


@pytest.fixture(autouse=True)
def reset_config_manager() -> None:
    """
    Resets the configuration manager for testing.
    """
    from scripts.config.config_manager import ConfigManager

    ConfigManager.reset()
    yield
    ConfigManager.reset()


# ===========================
# 🧱 INDEXER AUTLOAD BLOCKERS
# ===========================
@pytest.fixture(autouse=True)
def stub_indexers(
    monkeypatch: Any, mock_raw_log_file: Any, mock_correction_summaries_file: Any, temp_dir: Path
) -> None:
    """
    Stubs indexers for testing.

    Args:
        monkeypatch (Any): The monkeypatch object to use for patching.
        mock_raw_log_file (Any): The mocked raw log file.
        mock_correction_summaries_file (Any): The mocked correction summaries file.
        temp_dir (Path): The temporary directory for the indexers.
    """

    class DummyEmbeddingModel:
        def encode(self, texts, convert_to_numpy=True):
            return np.array([[0.1] * 384 for _ in texts])

    def mock_init_summary(self, *args, **kwargs):
        self.paths = kwargs.get("paths") if "paths" in kwargs else kwargs.get("index_root")
        self.index = None
        self.metadata = []
        self.embedding_model = DummyEmbeddingModel()
        self.summaries_path = mock_correction_summaries_file
        self.index_path = temp_dir / "vector_store" / "summary_index.faiss"
        self.metadata_path = temp_dir / "vector_store" / "summary_metadata.pkl"

    def mock_init_raw(self, *args, **kwargs):
        self.paths = kwargs.get("paths") if "paths" in kwargs else kwargs.get("index_root")
        self.index = None
        self.metadata = []
        self.embedding_model = DummyEmbeddingModel()
        self.log_path = mock_raw_log_file
        self.index_path = temp_dir / "vector_store" / "raw_index.faiss"
        self.metadata_path = temp_dir / "vector_store" / "raw_metadata.pkl"

    monkeypatch.setattr(
        "scripts.indexers.summary_indexer.SummaryIndexer.__init__", mock_init_summary
    )
    monkeypatch.setattr("scripts.indexers.raw_log_indexer.RawLogIndexer.__init__", mock_init_raw)