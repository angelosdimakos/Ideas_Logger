import subprocess
import json
from pathlib import Path
import pytest


# Create a temporary directory and files for testing the CLI end-to-end
@pytest.fixture
def cli_test_setup(tmp_path):
    # Create directories
    orig_dir = tmp_path / "original"
    orig_dir.mkdir()
    ref_dir = tmp_path / "refactored"
    ref_dir.mkdir()
    test_dir = tmp_path / "tests"
    test_dir.mkdir()

    # Create sample code files
    orig_content = """
class SampleClass:
    def method_a(self):
        return 42

    def method_to_remove(self):
        return "This will be removed"
"""

    ref_content = """
class SampleClass:
    def method_a(self):
        return 42

    def new_method(self):
        # Added complexity
        x = 0
        for i in range(10):
            x += i
        return x
"""

    # Create the files
    (orig_dir / "foo.py").write_text(orig_content, encoding="utf-8")
    (ref_dir / "foo.py").write_text(ref_content, encoding="utf-8")

    # Create a test file
    test_content = """
from refactored.foo import SampleClass

def test_method_a():
    assert SampleClass().method_a() == 42
"""
    (test_dir / "test_foo.py").write_text(test_content, encoding="utf-8")

    # Return the setup
    return {
        "original": orig_dir,
        "refactored": ref_dir,
        "tests": test_dir,
        "root": tmp_path
    }


def test_cli_end_to_end(cli_test_setup):
    # Find the CLI script
    cli_path = Path(__file__).parents[2] / "scripts" / "refactor" / "refactor_guard_cli.py"
    output_path = cli_test_setup["root"] / "audit_result.json"

    # Run the CLI directly as a subprocess to simulate actual usage
    cmd = [
        "python",
        str(cli_path),
        "--original", str(cli_test_setup["original"]),
        "--refactored", str(cli_test_setup["refactored"]),
        "--tests", str(cli_test_setup["tests"]),
        "--all",
        "--json",
        "--output", str(output_path)
    ]

    # Run the command
    try:
        result = subprocess.run(
            cmd,
            cwd=cli_test_setup["root"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        raise

    # Check if output file exists
    assert output_path.exists(), f"Output file {output_path} was not created"

    # Load and validate the JSON output
    with open(output_path, "r", encoding="utf-8") as f:
        audit = json.load(f)

    # Find the key containing 'foo.py'
    found = False
    for key in audit.keys():
        if "foo.py" in key or key == "foo.py":
            found = True
            # Further validate the content
            file_data = audit[key]

            # Check for method differences
            assert "method_diff" in file_data
            assert "SampleClass" in file_data["method_diff"]
            class_diff = file_data["method_diff"]["SampleClass"]

            # Check removed and added methods
            assert "method_to_remove" in class_diff["missing"]
            assert "new_method" in class_diff["added"]

            # Check for missing tests
            assert "missing_tests" in file_data
            missing_methods = [item["method"] for item in file_data["missing_tests"] if item["class"] == "SampleClass"]
            assert "new_method" in missing_methods

            # Check for complexity data
            assert "complexity" in file_data
            break

    assert found, f"Expected 'foo.py' in audit, got keys: {list(audit.keys())}"
