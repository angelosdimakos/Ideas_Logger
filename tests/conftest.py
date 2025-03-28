import pytest
import os
from pathlib import Path
from unittest.mock import MagicMock

# === TEST DIR CREATION ===

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

# === PATCHED CONFIG + EFFECTIVE CONFIG (AUTOUSE) ===

@pytest.fixture(scope="function", autouse=True)
def patch_config_and_paths(monkeypatch, temp_dir):
    test_config = {
        "batch_size": 5,
        "test_mode": True,
        "test_logs_dir": str(temp_dir / "logs"),
        "test_export_dir": str(temp_dir / "exports"),
        "test_vector_store_dir": str(temp_dir / "vector_store"),
        "logs_dir": str(temp_dir / "logs"),
        "export_dir": str(temp_dir / "exports"),
        "vector_store_dir": str(temp_dir / "vector_store"),
        "correction_summaries_path": str(temp_dir / "logs" / "correction_summaries.json"),
        "raw_log_path": str(temp_dir / "logs" / "zephyrus_log.json"),
        "raw_log_index_path": str(temp_dir / "vector_store" / "raw_index.faiss"),
        "raw_log_metadata_path": str(temp_dir / "vector_store" / "raw_metadata.pkl"),
        "faiss_index_path": str(temp_dir / "vector_store" / "summary_index.faiss"),
        "faiss_metadata_path": str(temp_dir / "vector_store" / "summary_metadata.pkl"),
        "force_summary_tracker_rebuild": True
    }

    # ✅ Patch config loader to return our controlled test config
    monkeypatch.setattr("scripts.config_loader.load_config", lambda config_path=None: test_config)

    # ✅ Patch absolute path resolution to temp dir
    monkeypatch.setattr("scripts.config_loader.get_absolute_path", lambda rel: str(Path(rel)))


# === OPTIONAL AI MOCK ===

@pytest.fixture
def mock_ai(monkeypatch):
    mock_ai = MagicMock()
    mock_ai.summarize_entries_bulk.return_value = "This is a mocked summary."
    mock_ai._fallback_summary.return_value = "Fallback summary used."
    monkeypatch.setattr("scripts.ai_summarizer.AISummarizer", lambda: mock_ai)

# === DEFAULT AI PATCH (AUTOUSE) ===

@pytest.fixture(scope="function", autouse=True)
def patch_aisummarizer(monkeypatch):
    mock_ai = MagicMock()
    mock_ai.summarize_entries_bulk.return_value = "This is a mocked summary."
    mock_ai._fallback_summary.return_value = "Fallback summary used."
    monkeypatch.setattr("scripts.ai_summarizer.AISummarizer", lambda: mock_ai)

# === CORE OBJECT FIXTURE ===

@pytest.fixture(scope="function")
def logger_core(temp_dir):
    from scripts.core import ZephyrusLoggerCore
    return ZephyrusLoggerCore(script_dir=temp_dir)
