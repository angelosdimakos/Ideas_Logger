import json
import os
import logging
from pathlib import Path


def setup_logging():
    """
    Configures centralized logging with a default INFO level and a standard log format.
    Initializes a stream handler and logs a debug message to confirm setup.
    """
    # Default log level is INFO. This can be overridden later.
    level_str = "INFO"
    numeric_level = getattr(logging, level_str.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    # Log a debug message to confirm that logging is configured.
    logger = logging.getLogger(__name__)
    logger.debug("Centralized logging configured at level %s", level_str)


# Set up logging as early as possible.
setup_logging()

# Configure the module logger.
logger = logging.getLogger(__name__)

# Compute project base directory.
BASE_DIR = Path(__file__).resolve().parents[2]  # ← resolves to project root (Zephyrus root folder)
# Define the directory where configuration files are stored.
CONFIG_DIR = os.path.join(BASE_DIR, "config")
CONFIG_FILE_PATH = Path(__file__).resolve().parent / "config.json"

import json
import logging
import os

logger = logging.getLogger(__name__)

# Default config file path
CONFIG_FILE_PATH = "config/config.json"


def load_config(config_path=CONFIG_FILE_PATH):
    """
    Safely load the config file from the config folder.
    If it doesn't exist or has errors, return an empty dict.

    Args:
        config_path (str): The path to the config file. Defaults to CONFIG_FILE_PATH.

    Returns:
        dict: The loaded config dictionary.
    """
    if not os.path.exists(config_path):
        logger.warning(f"Config file '{config_path}' not found. Using defaults.")
        return {}

    try:
        # Attempt to read the config file
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(f"Successfully loaded config from '{config_path}'. Keys: {list(data.keys())}")
        logger.debug("Full config dump:\n" + json.dumps(data, indent=2))

        # Adjust logging level based on 'test_mode' value in the config
        if data.get("test_mode", False):
            logger.setLevel(logging.DEBUG)
            logger.debug("Test mode enabled: setting logger level to DEBUG.")
        else:
            logger.setLevel(logging.INFO)

        return data

    except json.JSONDecodeError as e:
        # If JSON is invalid, log an error and return an empty dict
        logger.error(f"Failed to parse config file '{config_path}': {e}. Using defaults.")
        return {}

    except OSError as e:
        # Handle I/O errors (file permission issues, etc.)
        logger.error(f"I/O error while loading config file '{config_path}': {e}. Using defaults.")
        return {}


def get_config_value(config, key, default):
    """
    Retrieve a configuration value by key.

    Args:
        config (dict): The configuration dictionary.
        key (str): The key of the value to retrieve.
        default (Any): The default value if key is not present.

    Returns:
        Any: The retrieved value, or the default if key is not present.

    Warning:
        Logs a warning if key is missing.
    """
    if key not in config:
        logger.warning(f"Missing key '{key}' in config. Using default value: {default}")
        return default
    return config[key]


def get_absolute_path(relative_path):
    """
    Build an absolute path from a project-root-relative path.

    Args:
        relative_path (str): The path relative to the project root.

    Returns:
        str: The absolute path, or None if the path can't be resolved.
    """
    try:
        return str(Path(BASE_DIR) / relative_path)
    except (TypeError, ValueError, OSError) as e:
        logger.error(f"Failed to resolve absolute path for '{relative_path}': {e}")
        return None


def is_test_mode(config=None):
    """
    Check if 'test_mode' is enabled in the configuration.

    This function verifies whether the application is running in test mode
    by checking the 'test_mode' flag in the provided configuration dictionary.

    Args:
        config (dict, optional): The configuration dictionary. If not provided,
                                 the configuration is loaded using `load_config()`.

    Returns:
        bool: True if 'test_mode' is enabled in the config, False otherwise.
    """
    if config is None:
        config = load_config()
        return config.get("test_mode", False)


def get_effective_config(config_path=CONFIG_FILE_PATH):
    """
    Loads the configuration from the specified path and overrides paths with test-safe ones if 'test_mode' is enabled.

    If 'test_mode' is enabled, the following configuration values are overridden:

        - 'logs_dir'
        - 'vector_store_dir'
        - 'export_dir'
        - 'raw_log_path'
        - 'correction_summaries_path'
        - 'summary_tracker_path'

    The overridden values are computed by joining the overridden directory paths with the original file names.
    """
    config = load_config(config_path)
    try:
        if config.get("test_mode", False):
            logger.warning("⚠️ Test mode is active. Overriding config paths with test equivalents.")

            config["logs_dir"] = config.get("test_logs_dir", "tests/mock_data/logs")
            config["vector_store_dir"] = config.get(
                "test_vector_store_dir", "tests/mock_data/vector_store"
            )
            config["export_dir"] = config.get("test_export_dir", "tests/mock_data/exports")

            # Override all path-specific keys using those dirs
            config["raw_log_path"] = str(Path(config["logs_dir"]) / "zephyrus_log.json")
            config["correction_summaries_path"] = str(
                Path(config["logs_dir"]) / "correction_summaries.json"
            )
            config["summary_tracker_path"] = str(Path(config["logs_dir"]) / "summary_tracker.json")
    except TypeError as e:
        logger.error("Invalid directory paths in test config override: %s", e)
    return config


# Example usage:
if __name__ == "__main__":
    config = load_config()
    batch_size = get_config_value(config, "batch_size", 5)
    summary_path = get_absolute_path(
        get_config_value(config, "correction_summaries_path", "logs/correction_summaries.json")
    )
    logger.info(f"Batch Size: {batch_size}")
    logger.info(f"Summary Path: {summary_path}")
