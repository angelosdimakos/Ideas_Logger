import os
import json
import subprocess
from pathlib import Path
import pytest


@pytest.fixture
def single_file_setup(tmp_path):
    # Create directories
    orig_dir = tmp_path / "original"
    orig_dir.mkdir()
    ref_dir = tmp_path / "refactored"
    ref_dir.mkdir()

    # Create sample code files
    orig_content = "class Foo:\n    def method(self):\n        return 42\n"
    ref_content = "class Foo:\n    def method(self):\n        return 99\n"

    orig_file = orig_dir / "foo.py"
    ref_file = ref_dir / "foo.py"

    orig_file.write_text(orig_content, encoding="utf-8")
    ref_file.write_text(ref_content, encoding="utf-8")

    return {"original": orig_file, "refactored": ref_file, "root": tmp_path}


def test_single_file_json(single_file_setup):
    # Find the CLI script
    cli_path = Path(__file__).parents[2] / "scripts" / "refactor" / "refactor_guard_cli.py"
    output_path = single_file_setup["root"] / "single_file_audit.json"

    # Run the CLI directly as a subprocess
    cmd = [
        "python",
        str(cli_path),
        "--original",
        str(single_file_setup["original"]),
        "--refactored",
        str(single_file_setup["refactored"]),
        "--json",
        "--output",
        str(output_path),
    ]

    # Run the command
    try:
        result = subprocess.run(
            cmd, cwd=single_file_setup["root"], capture_output=True, text=True, check=True
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
            # Validate the content
            file_data = audit[key]
            assert "method_diff" in file_data
            assert "complexity" in file_data
            assert "missing_tests" in file_data
            break

    assert found, f"Expected 'foo.py' in audit, got keys: {list(audit.keys())}"
