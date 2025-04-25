import pytest
import sys
from unittest import mock
from scripts.utils import zip_util

pytestmark = [pytest.mark.unit]


def test_zip_util_calls_zip_python_files(monkeypatch):
    """
    Tests that the main function in zip_util correctly parses command-line arguments
    and calls zip_python_files with the expected parameters, using monkeypatch to mock dependencies.
    """
    test_args = ["zip_util.py", "--output", "test.zip", "--root", ".", "--exclude", ".venv", ".git"]
    monkeypatch.setattr(sys, "argv", test_args)

    called = {}

    def mock_zip(output, root, exclude):
        called["output"] = output
        called["root"] = root
        called["exclude"] = exclude

    # 🔥 Patch where the function is used, not defined
    monkeypatch.setattr("scripts.utils.zip_util.zip_python_files", mock_zip)

    zip_util.main()

    assert called["output"] == "test.zip"
    assert called["root"] == "."
    assert ".venv" in called["exclude"]
