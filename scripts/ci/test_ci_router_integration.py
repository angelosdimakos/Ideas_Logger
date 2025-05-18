#!/usr/bin/env python3
"""
CI Router Integration Tester
===========================
This script tests the integration of the CI Router with all adapters.

It simulates file changes using git stash/apply and validates that
the router correctly identifies changed files and runs the appropriate
test adapters.

Usage:
    python test_ci_router_integration.py --test-file scripts/refactor/parsers/docstring_parser.py
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Ensure the repo root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the integration tester."""
    parser = argparse.ArgumentParser(
        description="Test CI Router integration with adapters."
    )
    parser.add_argument(
        "--test-file",
        help="File to modify for testing",
        default="scripts/refactor/parsers/docstring_parser.py"
    )
    parser.add_argument(
        "--output-dir",
        default="artifacts/router_test",
        help="Directory for test output"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean up temporary files after testing"
    )
    parser.add_argument(
        "--no-stash",
        action="store_true",
        help="Don't use git stash (for testing without git)"
    )
    return parser.parse_args()


def backup_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Create a backup of the specified file.

    Args:
        file_path: Path to the file to back up

    Returns:
        Tuple containing success flag and backup path
    """
    try:
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)
        return True, backup_path
    except Exception as e:
        print(f"Error backing up file: {e}")
        return False, None


def restore_file(file_path: str, backup_path: str) -> bool:
    """
    Restore a file from its backup.

    Args:
        file_path: Path to the file to restore
        backup_path: Path to the backup file

    Returns:
        True if the restoration was successful, False otherwise
    """
    try:
        shutil.copy2(backup_path, file_path)
        os.remove(backup_path)
        return True
    except Exception as e:
        print(f"Error restoring file: {e}")
        return False


def modify_file(file_path: str) -> bool:
    """
    Make a simple modification to a file for testing.

    Args:
        file_path: Path to the file to modify

    Returns:
        True if the modification was successful, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add a simple comment at the end
        new_content = content + f"\n# CI Router test modification: {os.urandom(4).hex()}\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True
    except Exception as e:
        print(f"Error modifying file: {e}")
        return False


def stash_changes() -> bool:
    """
    Stash any uncommitted changes in the git repository.

    Returns:
        True if stashing was successful, False otherwise
    """
    try:
        subprocess.run(
            ["git", "stash", "push", "-m", "CI Router integration test"],
            check=True,
            capture_output=True
        )
        return True
    except Exception as e:
        print(f"Error stashing changes: {e}")
        return False


def apply_stash() -> bool:
    """
    Apply the most recent stash in the git repository.

    Returns:
        True if stash application was successful, False otherwise
    """
    try:
        subprocess.run(
            ["git", "stash", "pop"],
            check=True,
            capture_output=True
        )
        return True
    except Exception as e:
        print(f"Error applying stash: {e}")
        return False


def run_ci_router(output_dir: str) -> Dict[str, Any]:
    """
    Run the CI Router.

    Args:
        output_dir: Directory for router output

    Returns:
        Router report data
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Run the router
    try:
        cmd = [
            "python",
            "scripts/ci/ci_router.py",
            "--base-branch", "HEAD~1",  # Compare with previous commit
            "--report-dir", output_dir,
            "--verbose"
        ]

        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        print(process.stdout)

        if process.returncode != 0:
            print(f"Error running CI Router: {process.stderr}")
            return {}

        # Read the router report
        report_path = os.path.join(output_dir, "router_summary.json")
        if not os.path.exists(report_path):
            print(f"Router report not found at {report_path}")
            return {}

        with open(report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error running CI Router: {e}")
        return {}


def run_adapter(adapter_name: str, output_dir: str, router_report: str) -> Dict[str, Any]:
    """
    Run a specific adapter.

    Args:
        adapter_name: Name of the adapter to run
        output_dir: Directory for adapter output
        router_report: Path to the router report

    Returns:
        Dictionary with adapter results
    """
    adapter_scripts = {
        "lint": "scripts/ci/adapters/lint_router.py",
        "test": "scripts/ci/adapters/test_router.py",
        "docstring": "scripts/ci/adapters/docstring_router.py",
        "refactor_guard": "scripts/ci/adapters/refactor_guard_router.py"
    }

    adapter_outputs = {
        "lint": os.path.join(output_dir, "lint_report.json"),
        "test": os.path.join(output_dir, "test_results.json"),
        "docstring": os.path.join(output_dir, "docstring_summary.json"),
        "refactor_guard": os.path.join(output_dir, "refactor_audit.json")
    }

    if adapter_name not in adapter_scripts:
        print(f"Unknown adapter: {adapter_name}")
        return {"status": "error", "error": "Unknown adapter"}

    script = adapter_scripts[adapter_name]
    output = adapter_outputs[adapter_name]

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output), exist_ok=True)

    try:
        # Build command based on adapter
        cmd = ["python", script, "--router-report", router_report]

        if adapter_name == "lint":
            cmd.extend(["--output", output])
        elif adapter_name == "test":
            cmd.extend(["--output", output, "--collect-only"])
        elif adapter_name == "docstring":
            cmd.extend(["--output", output])
        elif adapter_name == "refactor_guard":
            cmd.extend(["--output", output])

        # Run the adapter
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        print(f"--- {adapter_name} Adapter Output ---")
        print(process.stdout)

        if process.returncode != 0:
            print(f"Error running {adapter_name} adapter: {process.stderr}")
            return {"status": "error", "error": process.stderr}

        # Read the adapter output if it exists
        if os.path.exists(output):
            try:
                with open(output, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # If not JSON, return the file content
                with open(output, 'r', encoding='utf-8') as f:
                    return {"status": "success", "output": f.read()}

        return {"status": "success"}
    except Exception as e:
        print(f"Error running {adapter_name} adapter: {e}")
        return {"status": "error", "error": str(e)}


def validate_results(results: Dict[str, Any], modified_file: str) -> bool:
    """
    Validate that the router and adapters processed the modified file correctly.

    Args:
        results: Dictionary with test results
        modified_file: Path to the file that was modified

    Returns:
        True if validation passed, False otherwise
    """
    validation_passed = True
    relative_path = os.path.relpath(modified_file, _PROJECT_ROOT)

    # Check router results
    router_report = results.get("router", {})
    changed_files = router_report.get("changed_files", [])

    if not changed_files:
        print("❌ Router did not detect any changed files")
        validation_passed = False
    elif relative_path not in changed_files:
        print(f"❌ Router did not detect changes to {relative_path}")
        validation_passed = False
    else:
        print(f"✅ Router correctly detected changes to {relative_path}")

    # Check that the appropriate tasks were selected
    tasks_run = list(router_report.get("task_results", {}).keys())

    if not tasks_run:
        print("❌ Router did not select any tasks to run")
        validation_passed = False
    else:
        print(f"✅ Router selected tasks: {', '.join(tasks_run)}")

    # Check adapter results
    for adapter_name, adapter_results in results.items():
        if adapter_name == "router":
            continue

        if adapter_results.get("status") == "error":
            print(f"❌ {adapter_name} adapter failed: {adapter_results.get('error')}")
            validation_passed = False
        else:
            print(f"✅ {adapter_name} adapter ran successfully")

    return validation_passed


def main() -> int:
    """
    Main entry point for the integration tester.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()

    print(f"=== CI Router Integration Test ===")
    print(f"Test file: {args.test_file}")
    print(f"Output directory: {args.output_dir}")

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Backup the test file
    if not args.no_stash:
        print(f"Stashing current changes...")
        if not stash_changes():
            print("Failed to stash changes. Aborting.")
            return 1
    else:
        success, backup_path = backup_file(args.test_file)
        if not success:
            print("Failed to back up test file. Aborting.")
            return 1

    try:
        # Modify the test file
        print(f"Modifying test file...")
        if not modify_file(args.test_file):
            print("Failed to modify test file. Aborting.")
            return 1

        # Run the CI Router
        print(f"Running CI Router...")
        router_report = run_ci_router(args.output_dir)

        if not router_report:
            print("CI Router failed or produced no output. Aborting.")
            return 1

        # Run adapters
        results = {"router": router_report}

        for adapter in ["lint", "test", "docstring", "refactor_guard"]:
            print(f"Running {adapter} adapter...")
            router_report_path = os.path.join(args.output_dir, "router_summary.json")
            results[adapter] = run_adapter(adapter, args.output_dir, router_report_path)

        # Validate results
        print(f"\n=== Validation Results ===")
        validation_passed = validate_results(results, args.test_file)

        if validation_passed:
            print(f"\n✅ Integration test passed! All components are working correctly.")
        else:
            print(f"\n❌ Integration test failed. See errors above.")

        return 0 if validation_passed else 1
    finally:
        # Restore the test file
        print(f"Restoring test file...")
        if not args.no_stash:
            if not apply_stash():
                print("Failed to restore changes from stash.")
        else:
            if not restore_file(args.test_file, f"{args.test_file}.bak"):
                print("Failed to restore test file from backup.")

        # Clean up temporary files
        if args.clean:
            print(f"Cleaning up temporary files...")
            try:
                shutil.rmtree(args.output_dir)
            except Exception as e:
                print(f"Error cleaning up temporary files: {e}")


if __name__ == "__main__":
    sys.exit(main())