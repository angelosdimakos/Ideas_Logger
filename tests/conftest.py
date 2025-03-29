import pytest
import os
from pathlib import Path
from unittest.mock import MagicMock
import json
from unittest.mock import patch
# === TEST DIR CREATION ===
from ollama import Client


@pytest.fixture(autouse=True)
def mock_ollama():
    with patch.object(Client, "generate") as mock_generate, \
            patch.object(Client, "chat") as mock_chat:
        # Define mock responses
        mock_generate.return_value = {"response": "Mock summary"}
        mock_chat.return_value = {"message": {"content": "Mock fallback summary"}}

        yield mock_generate, mock_chat
@pytest.fixture(scope="function")
def temp_dir(tmp_path):
    paths = [tmp_path / "logs", tmp_path / "exports", tmp_path / "vector_store"]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
    return tmp_path

@pytest.fixture(scope="function")
def temp_config_file(temp_dir):
    config_path = temp_dir / "config.json"
    test_config = {
        "mode": "test",
        "use_gui": False,
        "interface_theme": "dark",
        "batch_size": 5,
        "autosave_interval": 10,
        "log_level": "DEBUG",
        "summarization": True,
        "llm_provider": "ollama",
        "llm_model": "mistral",
        "openai_model": "gpt-4",
        "api_keys": {"openai": "test-key"},
        "embedding_model": "all-MiniLM-L6-v2",
        "faiss_top_k": 5,
        "force_summary_tracker_rebuild": True,
        "vector_store_dir": str(temp_dir / "vector_store"),
        "faiss_index_path": str(temp_dir / "vector_store" / "index.faiss"),
        "faiss_metadata_path": str(temp_dir / "vector_store" / "metadata.pkl"),
        "logs_dir": str(temp_dir / "logs"),
        "export_dir": str(temp_dir / "exports"),
        "correction_summaries_path": str(temp_dir / "logs" / "corrections.json"),
        "raw_log_path": str(temp_dir / "logs" / "raw_log.json"),
        "raw_log_index_path": str(temp_dir / "vector_store" / "raw_index.faiss"),
        "raw_log_metadata_path": str(temp_dir / "vector_store" / "raw_metadata.pkl"),
        "log_format": "json",
        "markdown_export": True,
        "default_tags": ["test"],
        "use_templates": True,
        "persona": "test_persona",
        "category_structure": {"Test": ["Subtest"]},
        "prompts_by_subcategory": {"Subtest": "Test prompt"},
        "test_mode": True,
        "test_logs_dir": str(temp_dir / "logs"),
        "test_vector_store_dir": str(temp_dir / "vector_store"),
        "test_export_dir": str(temp_dir / "exports"),
        "test_correction_summaries_path": str(temp_dir / "logs" / "test_corrections.json"),
        "test_raw_log_path": str(temp_dir / "logs" / "test_raw_log.json"),
        "test_summary_tracker_path": str(temp_dir / "logs" / "test_summary_tracker.json"),
        "remote_sync": False,
        "plugin_dir": str(temp_dir / "plugins"),
        "enable_debug_logging": True,
        "strict_offline_mode": True
    }
    config_path.write_text(json.dumps(test_config), encoding="utf-8")
    return config_path

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

    monkeypatch.setattr("scripts.config.config_loader.load_config", lambda config_path=None: test_config)
    monkeypatch.setattr("scripts.config.config_loader.get_absolute_path", lambda rel: str(Path(rel)))

# === OPTIONAL AI MOCK ===

@pytest.fixture
def mock_ai(monkeypatch):
    mock_ai = MagicMock()
    mock_ai.summarize_entries_bulk.return_value = "This is a mocked summary."
    mock_ai._fallback_summary.return_value = "Fallback summary used."
    monkeypatch.setattr("scripts.ai.ai_summarizer.AISummarizer", lambda: mock_ai)

# === DEFAULT AI PATCH (AUTOUSE) ===

@pytest.fixture(scope="function", autouse=True)
def patch_aisummarizer(monkeypatch):
    mock_ai = MagicMock()
    mock_ai.summarize_entries_bulk.return_value = "This is a mocked summary."
    mock_ai._fallback_summary.return_value = "Fallback summary used."
    monkeypatch.setattr("scripts.ai.ai_summarizer.AISummarizer", lambda: mock_ai)

# === CORE OBJECT FIXTURE ===

@pytest.fixture(scope="function")
def logger_core(temp_dir):
    from scripts.core.core import ZephyrusLoggerCore
    return ZephyrusLoggerCore(script_dir=temp_dir)
