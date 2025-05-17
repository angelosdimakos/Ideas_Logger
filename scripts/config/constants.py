"""
constants.py

This module defines global constants used throughout the Zephyrus Logger application.

Core features include:
- Timestamp and date formatting strings for consistent time representation.
- Standardized JSON keys for batch processing, summaries, and content tracking.
- Keys for summary tracking and logging statistics.
- Default configuration values for batch size, autosave interval, and log level.
- Default file suffixes and extensions for summary and markdown files.
- Centralized UI default settings, such as theme.

Intended to provide a single source of truth for application-wide constants, improving maintainability and consistency.
"""

# === Zephyrus Logger: Global Constants ===

# Timestamp formatting
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"  # Format for timestamps
DATE_FORMAT = "%Y-%m-%d"  # Format for dates

# JSON Keys
BATCH_KEY = "batch"  # Key for batch processing
ORIGINAL_SUMMARY_KEY = "original_summary"  # Key for original summary data
CORRECTED_SUMMARY_KEY = "corrected_summary"  # Key for corrected summary data
CORRECTION_TIMESTAMP_KEY = "correction_timestamp"  # Key for correction timestamp
CONTENT_KEY = "content"  # Key for content tracking
TIMESTAMP_KEY = "timestamp"  # Key for timestamps in JSON

# Summary Tracker
LOGGED_TOTAL = "logged_total"  # Key for total logged entries
SUMMARIZED_TOTAL = "summarized_total"  # Key for total summarized entries

# Default config values
DEFAULT_BATCH_SIZE = 5  # Default batch size for processing
DEFAULT_AUTOSAVE_INTERVAL = 5  # Default interval for autosaving
DEFAULT_LOG_LEVEL = "ERROR"  # Default logging level

# Path defaults (can later be externalized)
SUMMARY_FILE_SUFFIX = "_summary.json"  # Default suffix for summary files
MARKDOWN_EXTENSION = ".md"  # Default file extension for Markdown files

# UI Defaults (optional - only if you want to centralize)
DEFAULT_THEME = "dark"  # Default theme for the UI
