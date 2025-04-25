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
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

# JSON Keys
BATCH_KEY = "batch"
ORIGINAL_SUMMARY_KEY = "original_summary"
CORRECTED_SUMMARY_KEY = "corrected_summary"
CORRECTION_TIMESTAMP_KEY = "correction_timestamp"
CONTENT_KEY = "content"
TIMESTAMP_KEY = "timestamp"

# Summary Tracker
LOGGED_TOTAL = "logged_total"
SUMMARIZED_TOTAL = "summarized_total"

# Default config values
DEFAULT_BATCH_SIZE = 5
DEFAULT_AUTOSAVE_INTERVAL = 5
DEFAULT_LOG_LEVEL = "ERROR"

# Path defaults (can later be externalized)
SUMMARY_FILE_SUFFIX = "_summary.json"
MARKDOWN_EXTENSION = ".md"

# UI Defaults (optional - only if you want to centralize)
DEFAULT_THEME = "dark"
