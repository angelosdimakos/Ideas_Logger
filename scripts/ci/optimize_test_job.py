# scripts/ci/optimize_test_job.py
"""
optimize_test_job.py

This script optimizes the GitHub Actions test job to run only necessary tests based on changed files.
It integrates with the existing Ideas_Logger CI workflow by dynamically generating test commands.

Usage:
  python scripts/ci/optimize_test_job.py --from-ref $GITHUB_BASE_REF --to-ref $GITHUB_SHA
"""
import os
import json
import sys
import argparse
from pathlib import Path

# Import the test router
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scripts.utils.test_router import update_github_workflow_test_job, get_added_modified_py_files


def create_optimized_workflow(from_ref, to_ref):
    """
    Create an optimized GitHub Actions workflow step for test execution.

    Args:
        from_ref (str): Git reference to compare from
        to_ref (str): Git reference to compare to

    Returns:
        str: GitHub Actions compatible workflow step
    """
    # Get CI configuration based on changed files
    config = update_github_workflow_test_job(from_ref, to_ref)

    # Create workflow step
    if config["run_all"]:
        # Run the full test command from your existing workflow
        return (
            "echo \"🧪 Running ALL tests with coverage...\"\n"
            "xvfb-run -a pytest -n auto -c pytest.ini \\\n"
            "  --cov=scripts --cov-config=.coveragerc \\\n"
            "  --cov-report=term --cov-report=html --cov-report=json\n"
            "echo \"✅ Coverage reports generated (.coverage, HTML, JSON)\""
        )

    # Run only necessary tests
    output = []
    output.append("echo \"🧪 Running TARGETED tests with coverage...\"")

    for i, command in enumerate(config.get("test_commands", [])):
        output.append(f"echo \"⚙️ Running test command {i + 1} of {len(config['test_commands'])}...\"")
        output.append(command)

    output.append("echo \"✅ Coverage reports generated (.coverage, HTML, JSON)\"")

    return "\n".join(output)


def generate_github_output(from_ref, to_ref, output_file=None):
    """Generate GitHub Actions output variables from the optimization results."""
    # Get changed files for better logging
    changed_files = get_added_modified_py_files(from_ref, to_ref)
    print(f"Changed Python files detected: {changed_files}")

    # Get CI configuration based on changed files
    config = update_github_workflow_test_job(from_ref, to_ref)

    # Generate a codecov flag name based on the changed files
    # This will be used to mark this coverage run in Codecov
    flag_base = "targeted" if changed_files else "full"
    codecov_flag = f"{flag_base}-{from_ref[:7]}-{to_ref[:7]}"
    codecov_flag = codecov_flag.replace("/", "-").replace("_", "-").lower()

    # Generate a comma-separated list of files to include in coverage
    # (the .coveragerc format is "file1.py,file2.py,...")
    include_pattern = ",".join([f"*{file}" for file in changed_files]) if changed_files else "*"

    # More detailed logging
    if config["run_all"]:
        print("Running ALL tests due to core file changes or configuration")
    else:
        test_commands = config.get("test_commands", [])
        if not test_commands:
            print("⚠️ No tests mapped to changed files")
        else:
            print(f"Running {len(test_commands)} test command(s):")
            for cmd in test_commands:
                print(f"  - {cmd}")

    # Format commands for GitHub
    if config["run_all"]:
        test_commands = [
            "xvfb-run -a pytest -n auto -c pytest.ini --cov=scripts --cov-config=.coveragerc --cov-report=term --cov-report=html --cov-report=json"]
    else:
        test_commands = config.get("test_commands", [])

    # Create output variables
    output_vars = {
        "run_all": str(config["run_all"]).lower(),
        "test_commands": json.dumps(test_commands),
        "has_regular": str(config.get("has_regular", False)).lower(),
        "has_gui": str(config.get("has_gui", False)).lower(),
        "command_count": str(len(test_commands)),
        "codecov_flag": codecov_flag,
        "coverage_include": include_pattern,
        "has_changed_files": str(bool(changed_files)).lower()
    }

    # Write to GitHub environment file
    if output_file:
        with open(output_file, "a") as f:
            for key, value in output_vars.items():
                f.write(f"{key}={value}\n")

    # Also print to console for debugging
    print("GitHub Actions outputs:")
    for key, value in output_vars.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize GitHub Actions test job")
    parser.add_argument("--from-ref", required=True, help="Git reference to compare from")
    parser.add_argument("--to-ref", required=True, help="Git reference to compare to")
    parser.add_argument("--github-output", help="Path to GitHub environment output file")
    parser.add_argument("--workflow-step", action="store_true",
                        help="Output GitHub Actions workflow step instead of environment variables")

    args = parser.parse_args()

    if args.workflow_step:
        # Output workflow step
        workflow_step = create_optimized_workflow(args.from_ref, args.to_ref)
        print(workflow_step)
    else:
        # Output GitHub environment variables
        generate_github_output(args.from_ref, args.to_ref, args.github_output)