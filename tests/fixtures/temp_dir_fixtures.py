"""
Temporary Directory and Configuration Management Fixtures

This module provides fixtures for creating temporary directories and
managing configuration during testing.
"""
import json
import pytest
from pathlib import Path
from typing import Any


# ===========================
# 📁 TEMP DIR + CONFIG FIXTURES
# ===========================
@pytest.fixture(scope="function")
def temp_dir(tmp_path: Path) -> Path:
    """
    Creates a temporary directory for testing.

    Args:
        tmp_path (Path): The temporary path to create the directory.

    Returns:
        Path: The path to the created temporary directory.
    """
    paths = [tmp_path / "logs", tmp_path / "exports", tmp_path / "vector_store"]
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def temp_script_dir(temp_dir: Path) -> str:
    """
    Creates a temporary script directory for testing.

    Args:
        temp_dir (Path): The temporary directory for the script.

    Returns:
        str: The path to the created temporary script directory.
    """
    return str(temp_dir)  # Just returns the temp path as a string


@pytest.fixture
def temp_config_file(temp_dir: Path) -> Path:
    """
    Creates a temporary config file for testing.

    Args:
        temp_dir (Path): The temporary directory for the config file.

    Returns:
        Path: The path to the created temporary config file.
    """
    config = build_test_config(temp_dir)
    config_path = temp_dir / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path


# ===========================
# 🦢 TEST CONFIG PATCHER
# ===========================
@pytest.fixture(scope="function", autouse=True)
def patch_config_and_paths(monkeypatch: Any, temp_dir: Path, request) -> None:
    """
    Patches the configuration and paths for testing.

    Args:
        monkeypatch (Any): The monkeypatch object to use for patching.
        temp_dir (Path): The temporary directory for the configuration.
    """
    if "dont_patch_config" in request.keywords:
        return
    config = build_test_config(temp_dir)
    monkeypatch.setattr("scripts.config.config_loader.load_config", lambda config_path=None: config)
    monkeypatch.setattr(
        "scripts.config.config_loader.get_absolute_path", lambda rel: str(Path(rel).resolve())
    )


# ===========================
# 🛡 CONFIG GENERATOR
# ===========================
def build_test_config(temp_dir: Path) -> dict:
    """
    Builds a test configuration.

    Args:
        temp_dir (Path): The temporary directory for the configuration.

    Returns:
        dict: The test configuration.
    """

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
        "category_structure": {
            "Test": ["Subtest"],
            "SequentialTest": ["Flow"],
            "FallbackTest": ["Flow"],
            "IntegrationTest": ["Workflow"],
            "FAISS": ["Check"],
        },
        "prompts_by_subcategory": {
            "Subtest": "Test prompt",
            "Flow": "Summarize the flow of events.",
            "Workflow": "Summarize the integration workflow.",
            "Check": "Summarize log behavior for index check.",
        },
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