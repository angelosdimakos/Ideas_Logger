"""
logging_setup.py

This module provides centralized logging configuration for the application.

Core features include:
- Defining a `setup_logging` function to initialize the root logger with a specified log level.
- Clearing existing handlers and adding a console handler with a standardized log message format.
- Automatically configuring logging upon import for convenience and consistency across the application.

Intended for use as the standard logging setup to ensure uniform log formatting and log level management.
"""

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
    # Create a root logger
    logger = logging.getLogger()  # Get the root logger
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))  # Set the logging level

    # Clear any existing handlers
    if logger.hasHandlers():  # Check if there are existing handlers
        logger.handlers.clear()  # Clear existing handlers to avoid duplicate logs

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)  # Create a console handler for logging to stdout
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))  # Set the handler's log level
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")  # Define log message format
    console_handler.setFormatter(formatter)  # Set the formatter for the console handler
    logger.addHandler(console_handler)  # Add the console handler to the logger

# Run the setup on import for convenience
setup_logging()  # Automatically configure logging when the module is imported
