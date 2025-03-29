import json
from pathlib import Path
import logging
from pydantic import BaseModel, Field, Extra
from typing import List, Dict

logger = logging.getLogger(__name__)

class AppConfig(BaseModel):
    # ==== GENERAL SETTINGS ====
    mode: str
    use_gui: bool
    interface_theme: str
    batch_size: int
    autosave_interval: int
    log_level: str

    # ==== AI & LLM SETTINGS ====
    summarization: bool
    llm_provider: str
    llm_model: str
    openai_model: str
    api_keys: Dict[str, str]

    # ==== EMBEDDING & FAISS ====
    embedding_model: str
    faiss_top_k: int
    force_summary_tracker_rebuild: bool
    vector_store_dir: str
    faiss_index_path: str
    faiss_metadata_path: str

    # ==== LOGGING & EXPORT ====
    logs_dir: str
    export_dir: str
    correction_summaries_path: str
    raw_log_path: str
    raw_log_index_path: str
    raw_log_metadata_path: str
    log_format: str
    markdown_export: bool

    # ==== STRUCTURE SETTINGS ====
    default_tags: List[str]
    use_templates: bool
    persona: str

    # ==== CATEGORY STRUCTURE ====
    category_structure: Dict[str, List[str]]
    prompts_by_subcategory: Dict[str, str]

    # ==== TESTING SETTINGS ====
    test_mode: bool
    test_logs_dir: str
    test_vector_store_dir: str
    test_export_dir: str
    test_correction_summaries_path: str
    test_raw_log_path: str
    test_summary_tracker_path: str

    # ==== ADVANCED / FUTURE SETTINGS ====
    remote_sync: bool
    plugin_dir: str
    enable_debug_logging: bool
    strict_offline_mode: bool

    class Config:
        extra = Extra.ignore  # Ignore any extra keys (like comment keys)

class ConfigManager:
    _config: AppConfig = None

    @classmethod
    def load_config(cls, config_path: str = "config/config.json", force_reload: bool = False) -> AppConfig:
        """
        Load and validate the configuration from a JSON file.
        Caches the configuration for subsequent calls, unless force_reload is True.
        """
        if cls._config is None or force_reload:
            try:
                path = Path(config_path)
                if not path.exists():
                    logger.error("Configuration file not found: %s", config_path)
                    raise FileNotFoundError(f"Configuration file not found: {config_path}")
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cls._config = AppConfig(**data)
                logger.info("Configuration loaded and validated from %s", config_path)
            except Exception as e:
                logger.error("Error loading configuration: %s", e, exc_info=True)
                raise
        else:
            logger.debug("Using cached configuration")
        return cls._config

    @classmethod
    def get_value(cls, key: str, default=None, force_reload: bool = False):
        """
        Retrieve a configuration value from the loaded config.
        If the key does not exist, returns the provided default.
        Can force a reload if needed.
        """
        config = cls.load_config(force_reload=force_reload)
        return getattr(config, key, default)
