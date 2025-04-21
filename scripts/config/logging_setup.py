import logging
import sys


def setup_logging(log_level="INFO"):
    """
    Sets up application-wide logging configuration.

    Initializes the root logger with the specified log level, clears existing handlers,
    and adds a console handler with a standard log message format.

    Args:
        log_level (str): Logging level as a string (e.g., "INFO", "DEBUG"). Defaults to "INFO".
    """
    """Configure logging for the application."""
    # Create a root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


# Run the setup on import for convenience
setup_logging()
