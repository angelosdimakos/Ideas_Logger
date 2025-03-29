import os
import json
import zipfile
import pytest
from datetime import datetime
from utils.file_utils import (
    sanitize_filename,
    get_timestamp,
    safe_path,
    write_json,
    read_json,
    make_backup,
    zip_python_files
)

MOCK_DIR = "tests/mock_data"
MOCK_JSON_PATH = os.path.join(MOCK_DIR, "test_file.json")
MOCK_BACKUP_PATH = os.path.join(MOCK_DIR, "test_file_backup.json")
MOCK_ZIP_PATH = os.path.join(MOCK_DIR, "test_py_only.zip")

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    """
    Fixture for setting up and tearing down the test environment:
    - Creates the mock directory for testing.
    - Ensures cleanup of any mock files created during tests.
    """
    os.makedirs(MOCK_DIR, exist_ok=True)
    yield
    for f in [MOCK_JSON_PATH, MOCK_BACKUP_PATH, MOCK_ZIP_PATH]:
        if os.path.exists(f):
            os.remove(f)

def test_sanitize_filename():
    """
    Tests that the `sanitize_filename` function correctly cleans up a filename by:
    - Replacing illegal characters with underscores.
    - Removing special characters.
    - Ensuring the file extension is valid.
    """
    dirty = "this\\is<>illegal|file:name?.json"
    clean = sanitize_filename(dirty)
    assert clean == "thisisillegalfilename.json"

def test_get_timestamp_format():
    """
    Tests that the `get_timestamp` function returns a string in the format "%Y-%m-%d_%H-%M-%S".
    """
    ts = get_timestamp()
    datetime.strptime(ts, "%Y-%m-%d_%H-%M-%S")  # should not raise

def test_safe_path_creates_dirs():
    """
    Tests that the `safe_path` function creates any missing directories in the provided path.
    """
    path = safe_path("tests/mock_data/nested_dir/test.json")
    assert os.path.exists(os.path.dirname(path))

def test_write_and_read_json():
    """
    Tests the `write_json` and `read_json` functions by:
    - Writing a dictionary to a JSON file.
    - Reading the JSON file back into a dictionary.
    - Ensuring the written and read data are equivalent.
    """
    data = {"test": 123}
    write_json(MOCK_JSON_PATH, data)
    loaded = read_json(MOCK_JSON_PATH)
    assert loaded == data

def test_make_backup_creates_timestamped_copy():
    """
    Tests that the `make_backup` function creates a timestamped copy of the provided file.
    """
    data = {"backup": True}
    write_json(MOCK_JSON_PATH, data)
    backup_path = make_backup(MOCK_JSON_PATH)
    assert os.path.exists(backup_path)
    assert os.path.basename(backup_path).startswith("test_file_backup_")

def test_zip_python_files_excludes_unwanted_dirs():
    """
    Tests that the `zip_python_files` function excludes unwanted directories (e.g. venv, __pycache__) and only includes Python files.
    """
    zip_python_files(output_path=MOCK_ZIP_PATH, root_dir=".")
    assert os.path.exists(MOCK_ZIP_PATH)

    with zipfile.ZipFile(MOCK_ZIP_PATH, 'r') as zipf:
        files = zipf.namelist()
        assert all(f.endswith(".py") for f in files)
        assert all(".venv" not in f and "__pycache__" not in f for f in files)
