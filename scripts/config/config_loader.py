import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Setup centralized logging immediately
logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """
    Configures centralized logging for the application.
    
    Sets the logging level to INFO, applies a standard log message format, and directs log output to the console.
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
    Loads a JSON configuration file from the specified path, returning its contents as a dictionary.
    
    If the file does not exist or cannot be read or parsed, returns an empty dictionary. Adjusts the logger level to DEBUG if "test_mode" is enabled in the configuration; otherwise, sets it to INFO.
    
    Args:
        config_path: Path to the configuration file. Defaults to CONFIG_FILE_PATH.
    
    Returns:
        A dictionary containing the configuration, or an empty dictionary if loading fails.
    """
    if not config_path.exists():  # Check if the config file exists
        logger.warning(
            f"Config file '{config_path}' not found. Using defaults."
        )  # Log warning if file not found
        return {}  # Return empty dictionary if file not found

    try:
        with config_path.open("r", encoding="utf-8") as f:  # Open the config file in read mode
            data = json.load(f)  # Load the config data from the file
        logger.debug(
            f"Successfully loaded config from '{config_path}'. Keys: {list(data.keys())}"
        )  # Log debug message
        logger.debug("Full config dump:\n" + json.dumps(data, indent=2))  # Log the full config dump

        if data.get("test_mode", False):  # Check if test mode is enabled
            logger.setLevel(logging.DEBUG)  # Set the logger level to DEBUG if test mode is enabled
            logger.debug("Test mode enabled: setting logger level to DEBUG.")  # Log debug message
        else:
            logger.setLevel(
                logging.INFO
            )  # Set the logger level to INFO if test mode is not enabled

        return data  # Return the loaded config data

    except json.JSONDecodeError as e:  # Catch JSON decode errors
        logger.error(
            f"Failed to parse config file '{config_path}': {e}. Using defaults."
        )  # Log error message
        return {}  # Return empty dictionary if JSON decode error occurs
    except OSError as e:  # Catch OS errors
        logger.error(
            f"I/O error while loading config file '{config_path}': {e}. Using defaults."
        )  # Log error message
        return {}  # Return empty dictionary if OS error occurs


def get_config_value(config: Dict[str, Any], key: str, default: Any) -> Any:
    """
    Retrieves a value from the configuration dictionary by key, returning a default if missing.
    
    If the key is not present in the config, logs a warning and returns the provided default value.
    """
    if key not in config:  # Check if the key is not in the config
        logger.warning(
            f"Missing key '{key}' in config. Using default value: {default}"
        )  # Log warning if key not found
        return default  # Return the default value if key not found
    return config[key]  # Return the config value if key found


def get_absolute_path(relative_path: str) -> Path:
    """
    Resolves an absolute path by joining the project root with a given relative path.
    
    Args:
        relative_path: A path relative to the project root directory.
    
    Returns:
        The absolute Path object corresponding to the provided relative path.
    
    Raises:
        ValueError: If the relative path is invalid or cannot be resolved.
    """
    try:
        return BASE_DIR / relative_path  # Build the absolute path
    except (TypeError, ValueError, OSError) as e:  # Catch exceptions
        logger.error(
            f"Failed to resolve absolute path for '{relative_path}': {e}"
        )  # Log error message
        raise  # Re-raise the exception


def is_test_mode(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Determines whether test mode is enabled in the configuration.
    
    If no configuration is provided, loads the configuration from the default location.
    
    Returns:
        True if 'test_mode' is set to True in the configuration; otherwise, False.
    """
    if config is None:  # Check if config is None
        config = load_config()  # Load the config if None
    return config.get("test_mode", False)  # Return True if test mode is enabled, False otherwise


def get_effective_config(config_path: Path = CONFIG_FILE_PATH) -> Dict[str, Any]:
    """
    Loads the configuration and overrides directory paths with test-safe equivalents if test mode is enabled.
    
    If 'test_mode' is set in the configuration, updates directory and file paths to use test-specific locations to prevent interference with production data.
    
    Args:
        config_path: Path to the configuration file. Defaults to CONFIG_FILE_PATH.
    
    Returns:
        The effective configuration dictionary, with test-safe paths if test mode is active.
    """
    config = load_config(config_path)  # Load the config
    try:
        if config.get("test_mode", False):  # Check if test mode is enabled
            logger.warning(
                "\u26a0\ufe0f Test mode is active. Overriding config paths with test equivalents."
            )  # Log warning if test mode is enabled

            config["logs_dir"] = Path(
                config.get("test_logs_dir", "tests/mock_data/logs")
            )  # Override logs dir
            config["vector_store_dir"] = Path(
                config.get("test_vector_store_dir", "tests/mock_data/vector_store")
            )  # Override vector store dir
            config["export_dir"] = Path(
                config.get("test_export_dir", "tests/mock_data/exports")
            )  # Override export dir

            config["raw_log_path"] = (
                config["logs_dir"] / "zephyrus_log.json"
            )  # Override raw log path
            config["correction_summaries_path"] = (
                config["logs_dir"] / "correction_summaries.json"
            )  # Override correction summaries path
            config["summary_tracker_path"] = (
                config["logs_dir"] / "summary_tracker.json"
            )  # Override summary tracker path
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
