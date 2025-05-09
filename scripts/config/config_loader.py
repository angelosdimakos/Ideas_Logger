import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Setup centralized logging immediately
logger = logging.getLogger(__name__)

def setup_logging() -> None:
    """
    Configure centralized logging.

    This function sets up the logging level, format, and handlers for the application.

    Returns:
        None

    Raises:
        None
    """
    level_str = "INFO"  # Set the logging level to INFO
    numeric_level = getattr(logging, level_str.upper(), logging.INFO)  # Convert level to numeric
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Set log format
        handlers=[logging.StreamHandler()],  # Log to console
    )
    logger.debug("Centralized logging configured at level %s", level_str)  # Log debug message

setup_logging()

# Base directory setup
BASE_DIR: Path = Path(__file__).resolve().parents[2]  # Get the base directory of the project
CONFIG_DIR: Path = BASE_DIR / "config"  # Define the config directory path
CONFIG_FILE_PATH: Path = CONFIG_DIR / "config.json"  # Define the path to the config file

def load_config(config_path: Path = CONFIG_FILE_PATH) -> Dict[str, Any]:
    """
    Safely load the configuration file from the specified path.

    If the config file does not exist or has errors, return an empty dictionary.

    Args:
        config_path (Optional[Path]): The path to the config file. If None, defaults to CONFIG_FILE_PATH.

    Returns:
        Dict[str, Any]: The loaded configuration dictionary, or an empty dictionary if loading fails.

    Raises:
        FileNotFoundError: If the configuration file cannot be found.
        JSONDecodeError: If the configuration file contains invalid JSON.
    """
    if not config_path.exists():  # Check if the config file exists
        logger.warning(f"Config file '{config_path}' not found. Using defaults.")  # Log warning if file not found
        return {}  # Return empty dictionary if file not found

    try:
        with config_path.open("r", encoding="utf-8") as f:  # Open the config file in read mode
            data = json.load(f)  # Load the config data from the file
        logger.debug(f"Successfully loaded config from '{config_path}'. Keys: {list(data.keys())}")  # Log debug message
        logger.debug("Full config dump:\n" + json.dumps(data, indent=2))  # Log the full config dump

        if data.get("test_mode", False):  # Check if test mode is enabled
            logger.setLevel(logging.DEBUG)  # Set the logger level to DEBUG if test mode is enabled
            logger.debug("Test mode enabled: setting logger level to DEBUG.")  # Log debug message
        else:
            logger.setLevel(logging.INFO)  # Set the logger level to INFO if test mode is not enabled

        return data  # Return the loaded config data

    except json.JSONDecodeError as e:  # Catch JSON decode errors
        logger.error(f"Failed to parse config file '{config_path}': {e}. Using defaults.")  # Log error message
        return {}  # Return empty dictionary if JSON decode error occurs
    except OSError as e:  # Catch OS errors
        logger.error(f"I/O error while loading config file '{config_path}': {e}. Using defaults.")  # Log error message
        return {}  # Return empty dictionary if OS error occurs


def get_config_value(config: Dict[str, Any], key: str, default: Any) -> Any:
    """
    Retrieve a configuration value by its key from the provided config dictionary.

    If the key is not found in the config, a warning is logged and the default value is returned.

    Args:
        config (Dict[str, Any]): The configuration dictionary.
        key (str): The key of the value to retrieve.
        default (Any): The default value to return if the key is not found.

    Returns:
        Any: The retrieved configuration value or the default value.

    Raises:
        KeyError: If the key is not found and no default is provided.
    """
    if key not in config:  # Check if the key is not in the config
        logger.warning(f"Missing key '{key}' in config. Using default value: {default}")  # Log warning if key not found
        return default  # Return the default value if key not found
    return config[key]  # Return the config value if key found


def get_absolute_path(relative_path: str) -> Path:
    """
    Build an absolute path from a project-root-relative path.

    Args:
        relative_path (str): The relative path to convert.

    Returns:
        Path: The absolute path derived from the project root.

    Raises:
        ValueError: If the relative path is invalid.
    """
    try:
        return BASE_DIR / relative_path  # Build the absolute path
    except (TypeError, ValueError, OSError) as e:  # Catch exceptions
        logger.error(f"Failed to resolve absolute path for '{relative_path}': {e}")  # Log error message
        raise  # Re-raise the exception


def is_test_mode(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Check if 'test_mode' is enabled in the configuration.

    Args:
        config (Optional[Dict[str, Any]]): The configuration dictionary. If None, defaults to loading the config.

    Returns:
        bool: True if 'test_mode' is enabled, False otherwise.

    Raises:
        RuntimeError: If the configuration cannot be loaded.
    """
    if config is None:  # Check if config is None
        config = load_config()  # Load the config if None
    return config.get("test_mode", False)  # Return True if test mode is enabled, False otherwise


def get_effective_config(config_path: Path = CONFIG_FILE_PATH) -> Dict[str, Any]:
    """
    Load the configuration from the specified path and override paths with test-safe ones if 'test_mode' is enabled.

    This function first attempts to load the configuration from the given path. If 'test_mode' is active, it modifies certain paths in the configuration to point to test-safe equivalents, ensuring that tests do not interfere with production data.

    Args:
        config_path (Optional[Path]): The path to the config file. If None, defaults to CONFIG_FILE_PATH.

    Returns:
        Dict[str, Any]: The effective configuration dictionary, with test-safe paths if applicable.

    Raises:
        FileNotFoundError: If the configuration file cannot be found.
        JSONDecodeError: If the configuration file contains invalid JSON.
    """
    config = load_config(config_path)  # Load the config
    try:
        if config.get("test_mode", False):  # Check if test mode is enabled
            logger.warning(
                "\u26a0\ufe0f Test mode is active. Overriding config paths with test equivalents."
            )  # Log warning if test mode is enabled

            config["logs_dir"] = Path(config.get("test_logs_dir", "tests/mock_data/logs"))  # Override logs dir
            config["vector_store_dir"] = Path(
                config.get("test_vector_store_dir", "tests/mock_data/vector_store")
            )  # Override vector store dir
            config["export_dir"] = Path(config.get("test_export_dir", "tests/mock_data/exports"))  # Override export dir

            config["raw_log_path"] = config["logs_dir"] / "zephyrus_log.json"  # Override raw log path
            config["correction_summaries_path"] = config["logs_dir"] / "correction_summaries.json"  # Override correction summaries path
            config["summary_tracker_path"] = config["logs_dir"] / "summary_tracker.json"  # Override summary tracker path
    except TypeError as e:  # Catch type errors
        logger.error("Invalid directory paths in test config override: %s", e)  # Log error message

    return config  # Return the effective config


if __name__ == "__main__":
    config = load_config()  # Load the config
    batch_size = get_config_value(config, "batch_size", 5)  # Get the batch size
    summary_path = get_absolute_path(
        get_config_value(config, "correction_summaries_path", "logs/correction_summaries.json")
    )  # Get the summary path
    logger.info(f"Batch Size: {batch_size}")  # Log the batch size
    logger.info(f"Summary Path: {summary_path}")  # Log the summary path
