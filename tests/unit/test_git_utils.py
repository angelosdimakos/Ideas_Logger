from scripts.utils.git_utils import get_changed_files
from unittest.mock import patch

@patch("subprocess.run")
def test_get_changed_files_success(mock_run):
    mock_run.return_value.stdout = "scripts/foo.py\nscripts/bar.txt\n"
    result = get_changed_files()
    assert result == ["scripts/foo.py"]
