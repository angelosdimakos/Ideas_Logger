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
    zip_python_files
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
                    import time; time.sleep(0.5)

def test_sanitize_filename():
    dirty = "this\\is<>illegal|file:name?.json"
    clean = sanitize_filename(dirty)
    assert clean == "thisisillegalfilename.json"

def test_get_timestamp_format():
    ts = get_timestamp()
    datetime.strptime(ts, "%Y-%m-%d_%H-%M-%S")  # Should not raise

def test_safe_path_creates_dirs():
    path = safe_path(MOCK_NESTED_JSON)
    assert os.path.exists(os.path.dirname(path))

def test_write_and_read_json():
    data = {"test": 123}
    write_json(MOCK_JSON_PATH, data)
    loaded = read_json(MOCK_JSON_PATH)
    assert loaded == data

def test_make_backup_creates_timestamped_copy():
    data = {"backup": True}
    write_json(MOCK_JSON_PATH, data)
    backup_path = make_backup(MOCK_JSON_PATH)
    assert os.path.exists(backup_path)
    assert os.path.basename(backup_path).startswith("test_file_backup_")

def test_zip_python_files_excludes_unwanted_dirs():
    zip_python_files(output_path=MOCK_ZIP_PATH, root_dir="")
    assert os.path.exists(MOCK_ZIP_PATH)
    with zipfile.ZipFile(MOCK_ZIP_PATH, 'r') as zipf:
        files = zipf.namelist()
        assert all(f.endswith(".py") for f in files)
        assert all(".venv" not in f and "__pycache__" not in f for f in files)
