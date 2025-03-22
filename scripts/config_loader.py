import json
import os
import logging

# Configure the module logger.
logger = logging.getLogger(__name__)
# Default log level is set to INFO for production.
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

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

# Example usage:
if __name__ == "__main__":
    config = load_config()
    batch_size = get_config_value(config, "batch_size", 5)
    summary_path = get_absolute_path(get_config_value(config, "correction_summaries_path", "logs/correction_summaries.json"))
    logger.info(f"Batch Size: {batch_size}")
    logger.info(f"Summary Path: {summary_path}")
