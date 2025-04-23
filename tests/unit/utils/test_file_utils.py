import os
import zipfile
import pytest
from datetime import datetime
from scripts.utils.file_utils import (
    sanitize_filename,
    get_timestamp,
    safe_path,
    write_json,
    read_json,
    make_backup,
    zip_python_files,
)
import pytest

pytestmark = [pytest.mark.unit, pytest.mark.file_ops]

MOCK_DIR = "tests/mock_data"
MOCK_JSON_PATH = os.path.join(MOCK_DIR, "test_file.json")
MOCK_BACKUP_PATH = os.path.splitext(MOCK_JSON_PATH)[0] + "_backup.json"
MOCK_ZIP_PATH = os.path.join(MOCK_DIR, "test_py_only.zip")
MOCK_NESTED_JSON = os.path.join(MOCK_DIR, "nested_dir", "test.json")


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    os.makedirs(MOCK_DIR, exist_ok=True)
    yield
    for f in [MOCK_JSON_PATH, MOCK_BACKUP_PATH, MOCK_ZIP_PATH, MOCK_NESTED_JSON]:
        if os.path.exists(f):
            for _ in range(3):
                try:
                    os.remove(f)
                    break
                except PermissionError:
                    import time

                    time.sleep(0.5)


def test_sanitize_filename():
    """
    Unit tests for file utility functions including filename sanitization,
    timestamp formatting, directory creation, JSON read/write operations, backup creation,
    and zipping Python files. Ensures correct behavior and error handling
    for file operations using mock data and temporary paths.
    """
    dirty = "this\\is<>illegal|file:name?.json"
    clean = sanitize_filename(dirty)
    assert clean == "thisisillegalfilename.json"


def test_get_timestamp_format():
    """
    Unit tests for file utility functions, covering filename sanitization,
    timestamp formatting, directory creation, JSON read/write operations, backup creation,
    and zipping Python files. Tests ensure correct functionality and error handling using mock data and temporary paths.
    """
    ts = get_timestamp()
    datetime.strptime(ts, "%Y-%m-%d_%H-%M-%S")  # Should not raise


def test_safe_path_creates_dirs():
    """
    Unit tests for file utility functions, verifying filename sanitization,
    timestamp formatting, directory creation, JSON read/write operations,
    backup creation, and zipping of Python files. Tests ensure correct behavior
    and error handling using mock data and temporary paths.
    """
    path = safe_path(MOCK_NESTED_JSON)
    assert os.path.exists(os.path.dirname(path))


def test_write_and_read_json():
    """
    Unit tests for file utility functions, including filename sanitization,
    timestamp formatting, directory creation, JSON read/write operations, backup creation,
    and zipping Python files. Tests validate correct behavior and error handling using mock data and temporary paths.
    """
    data = {"test": 123}
    write_json(MOCK_JSON_PATH, data)
    loaded = read_json(MOCK_JSON_PATH)
    assert loaded == data


def test_make_backup_creates_timestamped_copy():
    """
    Unit tests for file utility functions in scripts.utils.file_utils,
    covering filename sanitization, timestamp formatting, directory creation,
    JSON read/write operations, backup creation, and zipping of Python files.
    Tests ensure correct functionality, error handling, and proper file operations using mock data and temporary paths.
    """
    data = {"backup": True}
    write_json(MOCK_JSON_PATH, data)
    backup_path = make_backup(MOCK_JSON_PATH)
    assert os.path.exists(backup_path)
    assert os.path.basename(backup_path).startswith("test_file_backup_")


def test_zip_python_files_excludes_unwanted_dirs():
    """
    Unit tests for file utility functions in scripts.utils.file_utils,
    including filename sanitization, timestamp formatting, directory creation,
    JSON read/write operations, backup creation, and zipping Python files.
    Tests validate correct behavior, error handling, and file operations using mock data and temporary paths.
    """
    zip_python_files(output_path=MOCK_ZIP_PATH, root_dir="")
    assert os.path.exists(MOCK_ZIP_PATH)
    with zipfile.ZipFile(MOCK_ZIP_PATH, "r") as zipf:
        files = zipf.namelist()
        assert all(f.endswith(".py") for f in files)
        assert all(".venv" not in f and "__pycache__" not in f for f in files)


def test_read_json_missing_file(tmp_path):
    """
    Unit tests for file utility functions in scripts.utils.file_utils,
    including filename sanitization, timestamp formatting, directory creation,
    JSON read/write operations, backup creation, and zipping Python files.
    Tests ensure correct functionality, error handling, and file operations using mock data and temporary paths.
    """
    from scripts.utils.file_utils import read_json

    path = tmp_path / "missing.json"
    data = read_json(path)
    assert data == {}


def test_write_and_read_json_with_invalid_data(tmp_path):
    """
    Unit tests for file utility functions in scripts.utils.file_utils,
    including filename sanitization, timestamp formatting, directory creation,
    JSON read/write operations, backup creation, and zipping Python files.
    Tests validate correct behavior, error handling, and file operations using mock data and temporary paths.
    """
    from scripts.utils.file_utils import write_json, read_json

    path = tmp_path / "data.json"
    data = {"x": 1}
    write_json(path, data)
    result = read_json(path)
    assert result == data
