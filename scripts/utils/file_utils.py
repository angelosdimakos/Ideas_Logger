import os
import json
import datetime
import re
import logging
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)
DEFAULT_JSON_INDENT = 2
BACKUP_JSON_INDENT = 4

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
    Ensure the parent directory for a file path exists.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return path



def write_json(path, data):
    """
    Safely write a Python object to a JSON file.
    """
    try:
        safe_path(path)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=DEFAULT_JSON_INDENT, ensure_ascii=False)
        logger.debug(f"Wrote JSON to: {path}")
    except FileNotFoundError:
        logger.error("Target directory does not exist: %s", path, exc_info=True)
    except PermissionError:
        logger.error("Permission denied while writing JSON to %s", path, exc_info=True)
    except TypeError as e:
        logger.error("Data contains non-serializable values: %s", e, exc_info=True)
    except OSError as e:
        logger.error("OS-level failure while writing JSON: %s", e, exc_info=True)


def read_json(path):
    """
    Safely read and return a log JSON object from a file.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON from {path}: {e}")
        return {}


def safe_read_json(filepath: Path) -> dict:
    """
    Safely reads a config JSON file. Returns an empty dictionary if the file doesn't exist
    or there is an error reading the file.

    Args:
        filepath (Path): Path to the JSON file to be read.

    Returns:
        dict: The contents of the JSON file, or an empty dictionary if an error occurs.
    """
    try:
        if not filepath.exists():
            logger.warning(f"File '{filepath}' not found. Returning empty dictionary.")
            return {}

        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to read JSON from {filepath}: {e}")
        return {}


def make_backup(file_path: str) -> str:
    """
    Creates a timestamped backup of a given JSON file.

    The backup file is saved in the same directory with the format:
    <original_name>_backup_<timestamp>.json

    Args:
        file_path (str): Path to the original JSON file to back up.

    Returns:
        str: Path to the created backup file if successful, or None if the original file doesn't exist or an error occurs.
    """
    if not os.path.exists(file_path):
        return None

    base, ext = os.path.splitext(file_path)
    timestamp = get_timestamp()
    backup_path = f"{base}_backup_{timestamp}{ext}"

    try:
        data = read_json(file_path)
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=BACKUP_JSON_INDENT)
        return backup_path 
    except Exception as e:
        logger.warning(f"Error creating backup: {e}")
        return None
        

def zip_python_files(output_path: str, root_dir: str = ".", exclude_dirs=None):
    """
    Zips all .py files in the project directory and its subdirectories,
    excluding specified folders like `.venv` or `.git`.

    Args:
        output_path (str): Destination .zip file path.
        root_dir (str): Root directory to start from.
        exclude_dirs (list[str], optional): List of directory names to exclude.
    """
    exclude_dirs = set(exclude_dirs or [".venv", ".git", "__pycache__", "node_modules"])
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(root_dir):
            # Skip excluded directories
            if any(excl in foldername for excl in exclude_dirs):
                continue
            for filename in filenames:
                if filename.endswith(".py"):
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, root_dir)  # keep relative structure
                    zipf.write(file_path, arcname)

