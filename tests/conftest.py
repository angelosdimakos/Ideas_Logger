"""
conftest.py

This module contains configuration and fixtures for pytest testing.

It imports and makes available all fixtures from separate modules to keep
the testing infrastructure organized and maintainable.
"""

# Import all fixtures from the fixtures directory
from tests.fixtures.tkinter_fixtures import *
from tests.fixtures.ai_mock_fixtures import *
from tests.fixtures.test_data_fixtures import *
from tests.fixtures.temp_dir_fixtures import *
from tests.fixtures.core_fixtures import *
from tests.fixtures.safety_fixtures import *
from tests.fixtures.encoding_fixtures import *

# Any project-wide fixtures or pytest configuration would go here
