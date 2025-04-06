import pytest
import os
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import tempfile
import numpy as np

# ===========================
# 🧪 OLLAMA AI MOCKING
# ===========================
@pytest.fixture(autouse=True)
def mock_ollama():
    with patch("ollama.generate") as mock_generate, patch("ollama.chat") as mock_chat:
        mock_generate.return_value = {"response": "Mock summary"}
        mock_chat.return_value = {"message": {"content": "Mock fallback summary"}}
        yield mock_generate, mock_chat


# ===========================
# 📁 TEMP DIR + CONFIG FIXTURES
# ===========================
@pytest.fixture(scope="function")
def temp_dir(tmp_path):
    paths = [tmp_path / "logs", tmp_path / "exports", tmp_path / "vector_store"]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture(scope="function")
def temp_config_file(temp_dir):
    config = build_test_config(temp_dir)
    config_path = temp_dir / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path


# ===========================
# 🧪 TEST CONFIG PATCHER
# ===========================
@pytest.fixture(scope="function", autouse=True)
def patch_config_and_paths(monkeypatch, temp_dir):
    config = build_test_config(temp_dir)
    monkeypatch.setattr("scripts.config.config_loader.load_config", lambda config_path=None: config)
    monkeypatch.setattr("scripts.config.config_loader.get_absolute_path", lambda rel: str(Path(rel).resolve()))


# ===========================
# 🔒 MOCKED AI SUMMARIZER
# ===========================
@pytest.fixture(scope="function", autouse=True)
def patch_aisummarizer(monkeypatch):
    mock_ai = MagicMock()
    mock_ai.summarize_entries_bulk.return_value = "This is a mocked summary."
    mock_ai._fallback_summary.return_value = "Fallback summary used."
    monkeypatch.setattr("scripts.ai.ai_summarizer.AISummarizer", lambda: mock_ai)


# ===========================
# 🧠 CORE LOGGER FIXTURE
# ===========================
@pytest.fixture(scope="function")
def logger_core(temp_dir):
    from scripts.core.core import ZephyrusLoggerCore
    return ZephyrusLoggerCore(script_dir=str(temp_dir))


# ===========================
# 🔁 STATE CLEANUP FIXTURES
# ===========================
@pytest.fixture
def clean_summary_tracker(logger_core):
    logger_core.summary_tracker_file.write_text("{}", encoding="utf-8")
    yield

@pytest.fixture(autouse=True)
def reset_config_manager():
    from scripts.config.config_manager import ConfigManager
    ConfigManager.reset()
    yield
    ConfigManager.reset()


# ===========================
# 🧠 MOCK TRANSFORMERS
# ===========================
@pytest.fixture(autouse=True)
def mock_sentence_transformer(monkeypatch):
    mock_model = MagicMock()
    mock_model.encode.side_effect = lambda texts, **kwargs: np.array([[0.1] * 384 for _ in texts])
    monkeypatch.setattr("scripts.indexers.base_indexer.SentenceTransformer", lambda *a, **kw: mock_model)


# ===========================
# 🧱 INDEXER AUTLOAD BLOCKERS
# ===========================
@pytest.fixture(autouse=True)
def disable_index_autoload(monkeypatch):
    monkeypatch.setattr("scripts.indexers.summary_indexer.SummaryIndexer.__init__", lambda self, paths, autoload=True: None)
    monkeypatch.setattr("scripts.indexers.raw_log_indexer.RawLogIndexer.__init__", lambda self, paths, autoload=True: None)


# ===========================
# 🛡 CONFIG GENERATOR
# ===========================
def build_test_config(temp_dir):
    def safe_path(p):
        return str(temp_dir / p)

    return {
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
        "log_format": "json",
        "markdown_export": True,
        "default_tags": ["test"],
        "use_templates": True,
        "persona": "test_persona",
        "category_structure": {"Test": ["Subtest"]},
        "prompts_by_subcategory": {"Subtest": "Test prompt"},
        "test_mode": True,
        "logs_dir": safe_path("logs"),
        "export_dir": safe_path("exports"),
        "vector_store_dir": safe_path("vector_store"),
        "correction_summaries_path": safe_path("logs/correction_summaries.json"),
        "raw_log_path": safe_path("logs/zephyrus_log.json"),
        "faiss_index_path": safe_path("vector_store/summary_index.faiss"),
        "faiss_metadata_path": safe_path("vector_store/summary_metadata.pkl"),
        "raw_log_index_path": safe_path("vector_store/raw_index.faiss"),
        "raw_log_metadata_path": safe_path("vector_store/raw_metadata.pkl"),
        "test_logs_dir": safe_path("logs"),
        "test_vector_store_dir": safe_path("vector_store"),
        "test_export_dir": safe_path("exports"),
        "test_correction_summaries_path": safe_path("logs/test_corrections.json"),
        "test_raw_log_path": safe_path("logs/test_raw_log.json"),
        "test_summary_tracker_path": safe_path("logs/test_summary_tracker.json"),
        "plugin_dir": safe_path("plugins"),
        "remote_sync": False,
        "enable_debug_logging": True,
        "strict_offline_mode": True,
    }


# ===========================
# 🐦 CONFTEXT CANARY
# ===========================
@pytest.fixture(autouse=True, scope="session")
def watch_conftest_integrity():
    original_path = Path(__file__)
    if not original_path.exists():
        raise RuntimeError("🔥 CRITICAL: conftest.py is missing before test session starts!")

    yield

    if not original_path.exists():
        raise RuntimeError("🛑 ALERT: conftest.py was deleted during test run!")


# ===========================
# 🧯 GUARDRAILS
# ===========================
@pytest.fixture(autouse=True)
def prevent_production_path_writes(monkeypatch):
    original_open = open

    def guarded_open(file, mode='r', *args, **kwargs):
        file_path = str(file)
        if ("zephyrus_log.json" in file_path or "correction_summaries.json" in file_path) and "test" not in file_path:
            raise PermissionError(f"❌ Blocked access to production file during test: {file_path}")
        return original_open(file, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", guarded_open)


@pytest.fixture(scope="session", autouse=True)
def assert_all_output_in_temp(tmp_path_factory):
    tmp_root = str(tmp_path_factory.getbasetemp())
    yield
    for root, dirs, files in os.walk("."):
        for name in files:
            fpath = os.path.join(root, name)
            if "test" in fpath.lower() and tmp_root not in fpath and "site-packages" not in fpath:
                raise AssertionError(f"🚨 Test output leaked outside tmp dir: {fpath}")

@pytest.fixture
def mock_raw_log_file(temp_dir):
    content = {
        "2024-01-01": {
            "Test": {
                "Subtest": [
                    {"timestamp": "2024-01-01 10:00:00", "content": "Test entry A"},
                    {"timestamp": "2024-01-01 10:01:00", "content": "Test entry B"}
                ]
            }
        }
    }
    path = temp_dir / "logs" / "zephyrus_log.json"
    path.write_text(json.dumps(content), encoding="utf-8")
    return path

@pytest.fixture
def mock_correction_summaries_file(temp_dir):
    content = {
        "global": {
            "Test": {
                "Subtest": ["Test summary A", "Test summary B"]
            }
        }
    }
    path = temp_dir / "logs" / "correction_summaries.json"
    path.write_text(json.dumps(content), encoding="utf-8")
    return path

