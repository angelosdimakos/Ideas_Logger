import os

def test_conftest_exists():
    assert os.path.exists("conftest.py"), "⚠️ conftest.py is missing. Something is deleting it!"
