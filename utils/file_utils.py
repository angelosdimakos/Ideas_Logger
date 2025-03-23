import os
import json
import datetime
import re
import logging

logger = logging.getLogger(__name__)


def sanitize_filename(name):
    """
    Remove invalid characters and trim length for safe file naming.
    """
    return re.sub(r'[^\w\-_. ]', '', name)[:100]


def get_timestamp():
    """
    Return current timestamp string.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def safe_path(path):
    """
    Ensure directory exists before using file path.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def write_json(path, data):
    """
    Safely write a Python object to a JSON file.
    """
    try:
        safe_path(path)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.debug(f"Wrote JSON to: {path}")
    except Exception as e:
        logger.error(f"Failed to write JSON to {path}: {e}")


def read_json(path):
    """
    Safely read and return a JSON object from a file.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON from {path}: {e}")
        return {}


def make_backup(original_path):
    """
    Create a timestamped backup of the original file.
    """
    try:
        base, ext = os.path.splitext(original_path)
        backup_path = f"{base}_backup_{get_timestamp()}{ext}"
        if os.path.exists(original_path):
            os.rename(original_path, backup_path)
            logger.debug(f"Backed up {original_path} → {backup_path}")
    except Exception as e:
        logger.warning(f"Failed to create backup for {original_path}: {e}")
