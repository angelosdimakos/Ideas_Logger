"""
config_manager.py

This module provides centralized management of application configuration using a Pydantic-based model.

Core features include:
- Defining a comprehensive AppConfig model for all configurable application parameters.
- Loading, validating, and caching configuration from a JSON file.
- Utility methods for retrieving configuration values, resetting the config cache, and validating critical config paths.
- Integration with safe file reading utilities for resilience against missing or malformed config files.

Intended for use throughout the application to ensure consistent, validated configuration management.
"""

import logging
import json
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, ValidationError
from scripts.utils.file_utils import safe_read_json

logger = logging.getLogger(__name__)


class AppConfig(BaseModel):
    """
    Configuration model for application settings.

    Defines all configurable parameters for the application, including UI,
    logging, LLM and embedding model settings, file paths, test mode,
    and plugin management. Ignores any extra fields not explicitly defined.
    """

    mode: str
    use_gui: bool
    interface_theme: str
    batch_size: int
    autosave_interval: int
    log_level: str
    summarization: bool
    llm_provider: str
    llm_model: str
    openai_model: str
    api_keys: dict[str, str]
    embedding_model: str
    faiss_top_k: int
    force_summary_tracker_rebuild: bool
    vector_store_dir: str
    faiss_index_path: str
    faiss_metadata_path: str
    logs_dir: str
    export_dir: str
    correction_summaries_path: str
    raw_log_path: str
    raw_log_index_path: str
    raw_log_metadata_path: str
    log_format: str
    markdown_export: bool
    default_tags: list[str]
    use_templates: bool
    persona: str
    category_structure: dict[str, list[str]]
    prompts_by_subcategory: dict[str, str]
    test_mode: bool
    test_logs_dir: str
    test_vector_store_dir: str
    test_export_dir: str
    test_correction_summaries_path: str
    test_raw_log_path: str
    test_summary_tracker_path: str
    remote_sync: bool
    plugin_dir: str
    enable_debug_logging: bool
    strict_offline_mode: bool

    class Config:
        extra = "ignore"


class ConfigManager:
    """
    Manages application configuration loading, caching, and validation.

    Provides methods to load configuration from a JSON file using the AppConfig model,
    retrieve configuration values, reset the cached config, and validate critical config paths.
    Handles missing or invalid config files by returning default settings and logs relevant events.
    """

    _config: Optional[AppConfig] = None
    _config_timestamp: Optional[float] = None

    # Default values for standalone AppConfig
    _DEFAULTS = {
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
        "vector_store_dir": "test_vector_store_dir",
        "faiss_index_path": "test_faiss_index_path",
        "faiss_metadata_path": "test_faiss_metadata_path",
        "logs_dir": "test_logs_dir",
        "export_dir": "test_export_dir",
        "correction_summaries_path": "test_correction_summaries_path",
        "raw_log_path": "test_raw_log_path",
        "raw_log_index_path": "test_raw_log_index_path",
        "raw_log_metadata_path": "test_raw_log_metadata_path",
        "log_format": "json",
        "markdown_export": True,
        "default_tags": ["test"],
        "use_templates": True,
        "persona": "test_persona",
        "category_structure": {"Test": ["Subtest"]},
        "prompts_by_subcategory": {"Subtest": "Test prompt"},
        "test_mode": True,
        "test_logs_dir": "test_test_logs_dir",
        "test_vector_store_dir": "test_test_vector_store_dir",
        "test_export_dir": "test_test_export_dir",
        "test_correction_summaries_path": "test_test_correction_summaries_path",
        "test_raw_log_path": "test_test_raw_log_path",
        "test_summary_tracker_path": "test_test_summary_tracker_path",
        "remote_sync": False,
        "plugin_dir": "test_plugin_dir",
        "enable_debug_logging": True,
        "strict_offline_mode": True,
    }

    # Pre-instantiated default config for type-safety
    _DEFAULT_CONFIG: AppConfig = AppConfig.parse_obj(_DEFAULTS)

    @classmethod
    def _default_config(cls) -> AppConfig:
        """Return a fresh copy of the pre-instantiated default config."""
        return cls._DEFAULT_CONFIG.copy()

    @classmethod
    def load_config(
        cls, config_path: str = "config/config.json", force_reload: bool = False
    ) -> AppConfig:
        """
        Loads the application configuration from a JSON file, with optional cache refresh.

        If the config file is missing or invalid, returns a default AppConfig instance.
        Caches the loaded config and reloads if the file changes or force_reload is True.
        Logs relevant events and raises on validation errors.

        Args:
            config_path (str): Path to the configuration JSON file.
            force_reload (bool): If True, forces reloading the config from disk.

        Returns:
            AppConfig: The loaded or default application configuration.
        """
        path = Path(config_path)

        if (
            force_reload
            or cls._config is None
            or not path.exists()
            or path.stat().st_mtime > (cls._config_timestamp or 0)
        ):
            if not path.exists():
                logger.error("Configuration file missing: %s", config_path)
                return cls._default_config()

            try:
                raw_config = safe_read_json(path)
                try:
                    text = path.read_text(encoding="utf-8")
                    raw_config = json.loads(text)
                except json.JSONDecodeError as e:
                    logger.error("Failed to decode config JSON: %s", e)
                    raise ValueError("Config validation failed: malformed JSON") from e
                if not raw_config:
                    logger.warning("Config is empty—falling back to defaults.")
                    return cls._default_config()

                cls._config = AppConfig(**raw_config)
                cls._config_timestamp = path.stat().st_mtime
                logger.info("Configuration loaded from %s", config_path)
            except ValidationError as e:
                logger.error("Config validation error: %s", e, exc_info=True)
                raise ValueError("Config validation failed") from e
            except Exception:
                logger.error("Unexpected error loading configuration", exc_info=True)
                raise
        else:
            logger.debug("Using cached configuration.")

        return cls._config

    @classmethod
    def get_value(cls, key: str, default: Any = None, force_reload: bool = False) -> Any:
        """
        Retrieve a configuration value by key from the loaded AppConfig.

        Args:
            key (str): The configuration attribute to retrieve.
            default (Any, optional): Value to return if the key is not found. Defaults to None.
            force_reload (bool, optional): If True, reloads the config from disk. Defaults to False.

        Returns:
            Any: The value of the requested configuration key, or the default if not found.
        """
        config = cls.load_config(force_reload=force_reload)
        return getattr(config, key, default)

    @classmethod
    def reset(cls) -> None:
        """Reset the cached configuration and timestamp."""
        cls._config = None
        cls._config_timestamp = None
        logger.debug("Config cache reset.")

    @classmethod
    def validate_config_paths(cls) -> bool:
        """
        Validate that critical config paths have existing parent directories.

        Logs a warning for each missing directory. Returns True if all required directories exist, otherwise False.

        Returns:
            bool: True if all critical directories exist, False otherwise.
        """
        config = cls.load_config()
        critical = [
            config.raw_log_path,
            config.correction_summaries_path,
            config.vector_store_dir,
        ]
        missing = [p for p in critical if not Path(p).parent.exists()]
        for p in missing:
            logger.warning("Missing directory for config path: %s", p)
        return not missing
