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

    mode: str  # Application mode (e.g., test, prod)
    use_gui: bool  # Whether to use the graphical user interface
    interface_theme: str  # Theme for the graphical user interface
    batch_size: int  # Batch size for processing data
    autosave_interval: int  # Interval for autosaving data
    log_level: str  # Logging level (e.g., DEBUG, INFO, WARNING, ERROR)
    summarization: bool  # Whether to enable summarization
    llm_provider: str  # Provider for the language model
    llm_model: str  # Model for the language model
    openai_model: str  # Model for OpenAI
    api_keys: dict[str, str]  # API keys for various services
    embedding_model: str  # Model for embeddings
    faiss_top_k: int  # Top k for Faiss
    force_summary_tracker_rebuild: bool  # Whether to force rebuild of summary tracker
    vector_store_dir: str  # Directory for vector store
    faiss_index_path: str  # Path to Faiss index
    faiss_metadata_path: str  # Path to Faiss metadata
    logs_dir: str  # Directory for logs
    export_dir: str  # Directory for exports
    correction_summaries_path: str  # Path to correction summaries
    raw_log_path: str  # Path to raw log
    raw_log_index_path: str  # Path to raw log index
    raw_log_metadata_path: str  # Path to raw log metadata
    log_format: str  # Format for logs
    markdown_export: bool  # Whether to export in Markdown format
    default_tags: list[str]  # Default tags for data
    use_templates: bool  # Whether to use templates
    persona: str  # Persona for the application
    category_structure: dict[str, list[str]]  # Structure for categories
    prompts_by_subcategory: dict[str, str]  # Prompts for subcategories
    test_mode: bool  # Whether to enable test mode
    test_logs_dir: str  # Directory for test logs
    test_vector_store_dir: str  # Directory for test vector store
    test_export_dir: str  # Directory for test exports
    test_correction_summaries_path: str  # Path to test correction summaries
    test_raw_log_path: str  # Path to test raw log
    test_summary_tracker_path: str  # Path to test summary tracker
    remote_sync: bool  # Whether to enable remote sync
    plugin_dir: str  # Directory for plugins
    enable_debug_logging: bool  # Whether to enable debug logging
    strict_offline_mode: bool  # Whether to enable strict offline mode

    class Config:
        extra = "ignore"  # Ignore extra fields not explicitly defined


class ConfigManager:
    """
    Manages application configuration loading, caching, and validation.

    Provides methods to load configuration from a JSON file using the AppConfig model,
    retrieve configuration values, reset the cached config, and validate critical config paths.
    Handles missing or invalid config files by returning default settings and logs relevant events.
    """

    _config: Optional[AppConfig] = None  # Cached configuration
    _config_timestamp: Optional[float] = None  # Timestamp for cached configuration

    # Default values for standalone AppConfig
    _DEFAULTS = {
        "mode": "test",  # Default mode
        "use_gui": False,  # Default GUI usage
        "interface_theme": "dark",  # Default interface theme
        "batch_size": 5,  # Default batch size
        "autosave_interval": 10,  # Default autosave interval
        "log_level": "DEBUG",  # Default logging level
        "summarization": True,  # Default summarization
        "llm_provider": "ollama",  # Default LLM provider
        "llm_model": "mistral",  # Default LLM model
        "openai_model": "gpt-4",  # Default OpenAI model
        "api_keys": {"openai": "test-key"},  # Default API keys
        "embedding_model": "all-MiniLM-L6-v2",  # Default embedding model
        "faiss_top_k": 5,  # Default Faiss top k
        "force_summary_tracker_rebuild": True,  # Default force rebuild of summary tracker
        "vector_store_dir": "test_vector_store_dir",  # Default vector store directory
        "faiss_index_path": "test_faiss_index_path",  # Default Faiss index path
        "faiss_metadata_path": "test_faiss_metadata_path",  # Default Faiss metadata path
        "logs_dir": "test_logs_dir",  # Default logs directory
        "export_dir": "test_export_dir",  # Default export directory
        "correction_summaries_path": "test_correction_summaries_path",  # Default correction summaries path
        "raw_log_path": "test_raw_log_path",  # Default raw log path
        "raw_log_index_path": "test_raw_log_index_path",  # Default raw log index path
        "raw_log_metadata_path": "test_raw_log_metadata_path",  # Default raw log metadata path
        "log_format": "json",  # Default log format
        "markdown_export": True,  # Default Markdown export
        "default_tags": ["test"],  # Default tags
        "use_templates": True,  # Default template usage
        "persona": "test_persona",  # Default persona
        "category_structure": {"Test": ["Subtest"]},  # Default category structure
        "prompts_by_subcategory": {"Subtest": "Test prompt"},  # Default prompts for subcategories
        "test_mode": True,  # Default test mode
        "test_logs_dir": "test_test_logs_dir",  # Default test logs directory
        "test_vector_store_dir": "test_test_vector_store_dir",  # Default test vector store directory
        "test_export_dir": "test_test_export_dir",  # Default test export directory
        "test_correction_summaries_path": "test_test_correction_summaries_path",  # Default test correction summaries path
        "test_raw_log_path": "test_test_raw_log_path",  # Default test raw log path
        "test_summary_tracker_path": "test_test_summary_tracker_path",  # Default test summary tracker path
        "remote_sync": False,  # Default remote sync
        "plugin_dir": "test_plugin_dir",  # Default plugin directory
        "enable_debug_logging": True,  # Default debug logging
        "strict_offline_mode": True,  # Default strict offline mode
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
