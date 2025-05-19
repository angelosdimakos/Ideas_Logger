# scripts/utils/test_router.py
"""
test_router.py

This module provides functionality for selective test execution based on which files have changed.
It supports both regular and GUI tests, integrating with the existing CI pipeline for Ideas_Logger.

Intended for use in CI workflows to optimize test execution time by only running tests
affected by code changes.
"""
import json
import os
import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Union, Optional, Tuple

# Import from your existing utilities
from scripts.utils.git_utils import get_added_modified_files, get_added_modified_py_files


def map_files_to_tests(changed_files: List[str], project_root: str = ".") -> Dict:
    """
    Maps source files to their corresponding test files based on project structure.

    Applies a set of rules to determine which test files correspond to the changed source files.
    Special files like configuration files can trigger running all tests.

    Args:
        changed_files (List[str]): List of changed file paths
        project_root (str): Root directory of the project. Defaults to current directory.

    Returns:
        Dict: Mapping of source files to test modules, or {"all": True} if all tests should run
    """
    test_mapping = {"regular": [], "gui": []}

    # Define mapping rules - customize these based on your project structure
    mapping_rules = [
        # Rule format: (source_pattern, test_pattern_template, test_type)
        (r"src/(\w+)/(.+)\.py$", "tests/test_{1}_{2}.py", "regular"),
        (r"app/ui/(.+)\.py$", "tests/ui/test_{1}.py", "gui"),
        (r"app/core/(.+)\.py$", "tests/core/test_{1}.py", "regular"),
        (r"lib/(\w+)\.py$", "tests/lib/test_{1}.py", "regular"),

        # Add rules for visualization modules
        (r"scripts/kg/modules/visualization\.py$", "tests/unit/kg/modules/test_visualization.py", "gui"),
        # Other KG module patterns
        (r"scripts/kg/modules/(.+)\.py$", "tests/unit/kg/modules/test_{1}.py", "regular"),

        # Add rules for utility files
        (r"scripts/utils/(.+)\.py$", "tests/unit/utils/test_{1}.py", "regular"),

        # Add rules for test files themselves
        (r"tests/(.+)/test_(.+)\.py$", "tests/{1}/test_{2}.py", "regular"),
        (r"tests/unit/kg/modules/test_(.+)\.py$", "tests/unit/kg/modules/test_{1}.py", "gui"),
    ]

    # If these files change, run all tests (e.g., config files, test fixtures)
    run_all_patterns = [
        r"pyproject\.toml$",
        r"setup\.py$",
        r"requirements\.txt$",
        r"pytest\.ini$",
        r"conftest\.py$",
        r"tests/fixtures/.+\.py$"
    ]

    # Check if any changed file requires running all tests
    for file in changed_files:
        for pattern in run_all_patterns:
            if re.match(pattern, file):
                print(f"Change in {file} requires running all tests")
                return {"all": True}

    # Map each file to its tests
    for file in changed_files:
        matched = False
        for source_pattern, test_template, test_type in mapping_rules:
            match = re.match(source_pattern, file)
            if match:
                # Replace placeholders in template with captured groups
                # {1} refers to first group, {2} to second, etc.
                test_file = test_template.format(*[""] + list(match.groups()))

                # For tests, we can either check file existence (for production)
                # or just map based on pattern (for testing)
                test_path = Path(project_root) / test_file

                # In integration tests, check existence; for unit tests, just do the mapping
                if test_path.exists() or 'test' in str(project_root):
                    # Get test module path like "tests.module.test_file"
                    test_module = str(test_file).replace("/", ".").replace("\\", ".").replace(".py", "")
                    if test_module not in test_mapping[test_type]:
                        test_mapping[test_type].append(test_module)
                    matched = True

        if not matched and file.endswith(".py"):
            print(f"No test mapping found for {file}")

    return test_mapping

def run_targeted_tests(
        from_ref: str = "HEAD~1",
        to_ref: str = "HEAD",
        output_json: str = "coverage.json",
        py_only: bool = True,
        headless: bool = True,
        run_xvfb: bool = True,
        parallel: bool = True,
) -> bool:
    """
    Runs pytest with coverage for tests corresponding to changed files,
    supporting both regular and GUI tests.

    Identifies changed files using git_utils, maps them to test modules,
    and runs the relevant tests with appropriate configuration.

    Args:
        from_ref (str): Git reference to compare from. Defaults to 'HEAD~1'.
        to_ref (str): Git reference to compare to. Defaults to 'HEAD'.
        output_json (str): Path for the coverage JSON output. Defaults to 'coverage.json'.
        py_only (bool): Whether to filter for Python files only. Defaults to True.
        headless (bool): Whether to run in headless mode for GUI tests. Defaults to True.
        run_xvfb (bool): Whether to use xvfb for GUI tests (Linux only). Defaults to True.
        parallel (bool): Whether to run tests in parallel with pytest-xdist. Defaults to True.

    Returns:
        bool: True if all tests pass, False otherwise
    """
    # Get changed files (Python only or all files)
    if py_only:
        changed_files = get_added_modified_py_files(from_ref, to_ref)
    else:
        changed_files = get_added_modified_files(from_ref, to_ref)

    print(f"Found {len(changed_files)} changed files")

    # Save changed files to JSON for debugging/logging
    with open("changed_files.json", "w") as f:
        json.dump({"changed_files": changed_files}, f, indent=2)

    # Map files to tests
    test_mapping = map_files_to_tests(changed_files)

    # Save test mapping to JSON for debugging/logging
    with open("test_mapping.json", "w") as f:
        json.dump(test_mapping, f, indent=2)

    # Set environment variable for headless UI testing if needed
    if headless:
        os.environ["ZEPHYRUS_HEADLESS"] = "1"

    # Run tests with coverage
    regular_success = True
    gui_success = True

    # If we need to run all tests, run them with the appropriate commands
    if isinstance(test_mapping, dict) and test_mapping.get("all", False):
        print("Running ALL tests (including GUI tests)")
        cmd_prefix = ["xvfb-run", "-a"] if run_xvfb and sys.platform.startswith("linux") else []
        parallel_arg = ["-n", "auto"] if parallel else []

        full_cmd = cmd_prefix + [
            "pytest",
            *parallel_arg,
            "-c", "pytest.ini",
            f"--cov=scripts",
            "--cov-config=.coveragerc",
            f"--cov-report=term",
            f"--cov-report=html",
            f"--cov-report=json:{output_json}"
        ]

        try:
            result = subprocess.run(full_cmd, check=False)
            return result.returncode == 0
        except Exception as e:
            print(f"Error running tests: {e}")
            return False

    # Run regular tests if we have any
    if test_mapping.get("regular"):
        regular_success = _run_regular_tests(test_mapping["regular"], output_json, parallel)

    # Run GUI tests if we have any
    if test_mapping.get("gui"):
        gui_success = _run_gui_tests(test_mapping["gui"], output_json, run_xvfb, parallel)

    # Return True only if both test types pass
    return regular_success and gui_success


def _run_regular_tests(test_modules: List[str], output_json: str = "coverage.json", parallel: bool = True) -> bool:
    """
    Run regular (non-GUI) tests with pytest and coverage.

    Args:
        test_modules (List[str]): List of test modules to run
        output_json (str): Path for the coverage JSON output
        parallel (bool): Whether to run tests in parallel

    Returns:
        bool: True if tests pass, False otherwise
    """
    if not test_modules:
        print("No regular test modules to run")
        return True

    print(f"Running {len(test_modules)} regular test modules with coverage:")
    for module in test_modules:
        print(f"  - {module}")

    parallel_arg = ["-n", "auto"] if parallel else []

    cmd = [
              "pytest",
              *parallel_arg,
              "-c", "pytest.ini",
              f"--cov=scripts",
              "--cov-config=.coveragerc",
              f"--cov-report=term",
              f"--cov-report=json:{output_json}"
          ] + test_modules

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running regular tests: {e}")
        return False


def _run_gui_tests(
        test_modules: List[str],
        output_json: str = "coverage.json",
        run_xvfb: bool = True,
        parallel: bool = True
) -> bool:
    """
    Run GUI tests with pytest and coverage, using xvfb if on Linux.

    Args:
        test_modules (List[str]): List of test modules to run
        output_json (str): Path for the coverage JSON output
        run_xvfb (bool): Whether to use xvfb for GUI tests
        parallel (bool): Whether to run tests in parallel

    Returns:
        bool: True if tests pass, False otherwise
    """
    if not test_modules:
        print("No GUI test modules to run")
        return True

    print(f"Running {len(test_modules)} GUI test modules with coverage:")
    for module in test_modules:
        print(f"  - {module}")

    # Determine if we need xvfb (Linux) and parallel execution
    cmd_prefix = ["xvfb-run", "-a"] if run_xvfb and sys.platform.startswith("linux") else []
    parallel_arg = ["-n", "auto"] if parallel else []

    cmd = cmd_prefix + [
        "pytest",
        *parallel_arg,
        "-c", "pytest.ini",
        f"--cov=scripts",
        "--cov-config=.coveragerc",
        f"--cov-report=term",
        f"--cov-report=append",  # Append to existing coverage from regular tests
        f"--cov-report=json:{output_json}"
    ] + test_modules

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running GUI tests: {e}")
        return False


# Function to integrate with your CI workflow
def update_github_workflow_test_job(
        from_ref: str = "HEAD~1",
        to_ref: str = "HEAD"
) -> Dict:
    """Analyzes changed files and generates CI configuration for targeted test execution."""
    # Get changed files
    changed_files = get_added_modified_py_files(from_ref, to_ref)

    # Check if any test files themselves were modified
    test_files = [file for file in changed_files if file.startswith("tests/") and "test_" in file]
    if test_files:
        print(f"Test files were changed: {test_files}")
        # If test files were modified, run those tests directly
        test_modules = []
        gui_test_modules = []

        for test_file in test_files:
            # Convert path to module format
            test_module = test_file.replace("/", ".").replace("\\", ".").replace(".py", "")

            # Check if it's a GUI test
            if "kg/modules" in test_file or "gui" in test_file:
                gui_test_modules.append(test_module)
            else:
                test_modules.append(test_module)

        commands = []
        if test_modules:
            module_args = " ".join(test_modules)
            commands.append(
                f"pytest -n auto -c pytest.ini "
                f"--cov=scripts --cov-config=.coveragerc "
                f"--cov-report=term --cov-report=html --cov-report=json {module_args}"
            )

        if gui_test_modules:
            module_args = " ".join(gui_test_modules)
            cov_report = "--cov-report=append" if test_modules else "--cov-report=html --cov-report=json"
            commands.append(
                f"xvfb-run -a pytest -n auto -c pytest.ini "
                f"--cov=scripts --cov-config=.coveragerc "
                f"--cov-report=term {cov_report} {module_args}"
            )

        return {
            "run_all": False,
            "test_commands": commands,
            "has_regular": bool(test_modules),
            "has_gui": bool(gui_test_modules)
        }

    # Map files to tests (original code continues here)
    test_mapping = map_files_to_tests(changed_files)

    # Generate CI configuration
    if isinstance(test_mapping, dict) and test_mapping.get("all", False):
        # Run all tests with default CI configuration
        return {
            "run_all": True,
            "test_command": "xvfb-run -a pytest -n auto -c pytest.ini " +
                            "--cov=scripts --cov-config=.coveragerc " +
                            "--cov-report=term --cov-report=html --cov-report=json"
        }

    # Prepare targeted test configuration
    has_regular = bool(test_mapping.get("regular", []))
    has_gui = bool(test_mapping.get("gui", []))

    commands = []

    if has_regular:
        regular_modules = " ".join(test_mapping.get("regular", []))
        commands.append(
            f"pytest -n auto -c pytest.ini " +
            f"--cov=scripts --cov-config=.coveragerc " +
            f"--cov-report=term --cov-report=html --cov-report=json {regular_modules}"
        )

    if has_gui:
        gui_modules = " ".join(test_mapping.get("gui", []))
        # For GUI tests, append to existing coverage
        commands.append(
            f"xvfb-run -a pytest -n auto -c pytest.ini " +
            f"--cov=scripts --cov-config=.coveragerc " +
            f"--cov-report=term --cov-report=append --cov-report=json {gui_modules}"
        )

    if not commands:
        # No tests to run, but we still need coverage report
        commands.append(
            "echo '⚠️ No tests mapped to changed files, generating empty coverage...'" +
            " && pytest --collect-only --cov=scripts --cov-report=json"
        )

    return {
        "run_all": False,
        "test_commands": commands,
        "has_regular": has_regular,
        "has_gui": has_gui
    }


if __name__ == "__main__":
    # Command line interface for the module
    import argparse

    parser = argparse.ArgumentParser(description="Run tests based on changed files")
    parser.add_argument("--from-ref", default="HEAD~1", help="Git reference to compare from")
    parser.add_argument("--to-ref", default="HEAD", help="Git reference to compare to")
    parser.add_argument("--output", default="coverage.json", help="Path for coverage JSON output")
    parser.add_argument("--py-only", action="store_true", help="Filter for Python files only")
    parser.add_argument("--no-headless", action="store_false", dest="headless",
                        help="Disable headless mode for GUI tests")
    parser.add_argument("--no-xvfb", action="store_false", dest="run_xvfb",
                        help="Disable xvfb for GUI tests")
    parser.add_argument("--no-parallel", action="store_false", dest="parallel",
                        help="Disable parallel test execution")
    parser.add_argument("--ci", action="store_true", help="Generate CI configuration")

    args = parser.parse_args()

    if args.ci:
        # Generate CI configuration
        config = update_github_workflow_test_job(args.from_ref, args.to_ref)
        print(json.dumps(config, indent=2))
        sys.exit(0)

    # Run tests
    success = run_targeted_tests(
        args.from_ref,
        args.to_ref,
        args.output,
        args.py_only,
        args.headless,
        args.run_xvfb,
        args.parallel
    )

    sys.exit(0 if success else 1)