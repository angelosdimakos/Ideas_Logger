import json
import os
import logging
from pathlib import Path

def setup_logging():
    """
    Configures logging for the entire application.
    This function sets up a basic logging configuration that can be adjusted later based on config settings.
    """
    # Default log level is INFO. This can be overridden later.
    level_str = "INFO"
    numeric_level = getattr(logging, level_str.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    # Log a debug message to confirm that logging is configured.
    logger = logging.getLogger(__name__)
    logger.debug("Centralized logging configured at level %s", level_str)

# Set up logging as early as possible.
setup_logging()

# Configure the module logger.
logger = logging.getLogger(__name__)

# Compute project base directory.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Define the directory where configuration files are stored.
CONFIG_DIR = os.path.join(BASE_DIR, "config")
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, "config.json")

def load_config(config_path=CONFIG_FILE_PATH):
    """
    Safely load the config file from the config folder.
    If it doesn't exist or has errors, return an empty dict.
    """
    if not os.path.exists(config_path):
        logger.warning(f"Config file '{config_path}' not found. Using defaults.")
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"Successfully loaded config from '{config_path}'. Keys: {list(data.keys())}")
        logger.debug("Full config dump:\n" + json.dumps(data, indent=2))
        # After loading, adjust the logger level based on test_mode.
        if data.get("test_mode", False):
            logger.setLevel(logging.DEBUG)
            logger.debug("Test mode enabled: setting logger level to DEBUG.")
        else:
            logger.setLevel(logging.INFO)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse config file '{config_path}': {e}. Using defaults.")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error while loading config file '{config_path}': {e}. Using defaults.")
        return {}

def get_config_value(config, key, default):
    """
    Retrieve a configuration value by key.
    Logs a warning only if the key is missing.
    """
    if key not in config:
        logger.warning(f"Missing key '{key}' in config. Using default value: {default}")
        return default
    return config[key]

def get_absolute_path(relative_path):
    """
    Build an absolute path from a project-root-relative path.
    """
    try:
        return os.path.join(BASE_DIR, relative_path)
    except Exception as e:
        logger.error(f"Failed to resolve absolute path for '{relative_path}': {e}.")
        return None

def is_test_mode(config=None):
    """
    Returns True if 'test_mode' is enabled in the config, else False.
    """
    if config is None:
        config = load_config()
        return config.get("test_mode", False)

def get_effective_config(config_path=CONFIG_FILE_PATH):
    """
    Loads the config and overrides paths with test-safe ones if test_mode is enabled.
    """
    config = load_config(config_path)
    if config.get("test_mode", False):
        logger.warning("⚠️ Test mode is active. Overriding config paths with test equivalents.")

        config["logs_dir"] = config.get("test_logs_dir", "tests/mock_data/logs")
        config["vector_store_dir"] = config.get("test_vector_store_dir", "tests/mock_data/vector_store")
        config["export_dir"] = config.get("test_export_dir", "tests/mock_data/exports")

        # Override all path-specific keys using those dirs
        config["raw_log_path"] = str(Path(config["logs_dir"]) / "zephyrus_log.json")
        config["correction_summaries_path"] = str(Path(config["logs_dir"]) / "correction_summaries.json")
        config["summary_tracker_path"] = str(Path(config["logs_dir"]) / "summary_tracker.json")

    return config


# Example usage:
if __name__ == "__main__":
    config = load_config()
    batch_size = get_config_value(config, "batch_size", 5)
    summary_path = get_absolute_path(get_config_value(config, "correction_summaries_path", "logs/correction_summaries.json"))
    logger.info(f"Batch Size: {batch_size}")
    logger.info(f"Summary Path: {summary_path}")
