import os
from pathlib import Path


def test_conftest_exists():
    """
    Test to ensure that the 'conftest.py' file exists in the tests directory.

    Raises an assertion error if the file is missing.
    """
    tests_dir = Path(__file__).parent.parent  # Go up one level to the tests directory
    conftest_path = tests_dir / "conftest.py"

    assert conftest_path.exists(), f"⚠️ conftest.py is missing at {conftest_path}. Something is deleting it!"