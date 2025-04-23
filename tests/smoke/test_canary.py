import os


def test_conftest_exists():
    """
    Test to ensure that the 'conftest.py' file exists in the current directory.

    Raises an assertion error if the file is missing.
    """
    assert os.path.exists("conftest.py"), "⚠️ conftest.py is missing. Something is deleting it!"
