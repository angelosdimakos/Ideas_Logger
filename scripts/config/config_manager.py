import logging
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, ValidationError
from scripts.config.config_loader import load_config as load_raw_config

logger = logging.getLogger(__name__)

class AppConfig(BaseModel):
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
    _config: Optional[AppConfig] = None
    _config_timestamp: Optional[float] = None

    @classmethod
    def load_config(cls, config_path: str = "config/config.json", force_reload: bool = False) -> AppConfig:
        path = Path(config_path)

        if force_reload or cls._config is None or not path.exists() or path.stat().st_mtime > (cls._config_timestamp or 0):
            if not path.exists():
                logger.error("Configuration file missing: %s", config_path)
                raise FileNotFoundError(f"Configuration file not found: {config_path}")

            try:
                raw_config = load_raw_config(config_path)
                cls._config = AppConfig(**raw_config)
                cls._config_timestamp = path.stat().st_mtime
                logger.info("Configuration loaded from %s", config_path)
            except ValidationError as e:
                logger.error("Config validation error: %s", e, exc_info=True)
                raise ValueError("Config validation failed") from e
            except Exception as e:
                logger.error("Unexpected error loading configuration: %s", e, exc_info=True)
                raise
        else:
            logger.debug("Using cached configuration.")

        return cls._config

    @classmethod
    def get_value(cls, key: str, default: Any = None, force_reload: bool = False) -> Any:
        config = cls.load_config(force_reload=force_reload)
        return getattr(config, key, default)

    @classmethod
    def reset(cls):
        cls._config = None
        cls._config_timestamp = None
        logger.debug("Config cache reset.")

    @classmethod
    def validate_config_paths(cls):
        config = cls.load_config()
        critical_paths = [
            config.raw_log_path,
            config.correction_summaries_path,
            config.vector_store_dir,
        ]
        missing_dirs = [p for p in critical_paths if not Path(p).parent.exists()]
        for p in missing_dirs:
            logger.warning("Missing directory for config path: %s", p)
        return not missing_dirs  # Returns True if all directories exist