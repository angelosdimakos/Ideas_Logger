"""Automate testing for the refactored code and ensure functionality is preserved.

This module automates testing to ensure that changes during refactoring do not negatively impact existing functionality.

Integrates with: unittest, pytest, nose, Travis CI, CircleCI
"""

import subprocess
from typing import List[str]

def run_tests(test_suites: List[str], use_travis_ci: bool = False, use_circle_ci: bool = False) -> None:
    """Run the specified tests using the chosen testing framework.

    Args:
        test_suites (List[str]): The list of test suites to run.
        use_travis_ci (bool, optional): Run the tests using Travis CI. Defaults to False.
        use_circle_ci (bool, optional): Run the tests using CircleCI. Defaults to False.
    """
