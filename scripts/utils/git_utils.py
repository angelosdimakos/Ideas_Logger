# scripts/utils/git_utils.py
"""
git_utils.py

This module provides utility functions for working with Git, including:

- Getting changed Python files compared to a specified branch.
- Running an interactive commit flow to create and push a new branch.

Intended for use in CI workflows and scripts to automate code quality and coverage reporting.
"""
import subprocess
from typing import List


def get_changed_files(base: str = "origin/main") -> List[str]:
    """
    Returns a list of changed Python files compared to the specified Git base branch.

    Runs 'git diff --name-only' to identify changed files and filters for those ending with '.py'.
    Handles compatibility with different Python versions and returns an empty list if the Git command fails.

    Args:
        base (str): The Git base branch or commit to compare against. Defaults to 'origin/main'.

    Returns:
        List[str]: A list of changed Python file paths.
    """
    cmd = ["git", "diff", "--name-only", base]
    try:
        # Try modern subprocess.run with text, encoding, errors
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=True,
        )
        output = result.stdout
    except subprocess.CalledProcessError:
        # Git returned non-zero exit code
        return []
    except TypeError:
        # Older Python: fallback to universal_newlines
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
            check=True,
        )
        output = result.stdout

    return [line for line in output.splitlines() if line.endswith(".py")]


def interactive_commit_flow(default_branch: str = "main") -> None:
    """
    Guides the user through an interactive Git commit and push process.

    Prompts the user to either push changes to the default branch or create and push to a new branch, handling all Git commands interactively.

    Args:
        default_branch (str): The branch to push to by default. Defaults to "main".

    Returns:
        None
    """
    import subprocess

    print("\n")
    print("Commit Assistant:")
    print(f"You're on branch: {get_current_branch()}")

    choice = (
        input(f"Push to [{default_branch}] or create a new branch? (main/new): ").strip().lower()
    )

    if choice == "main":
        subprocess.run(["git", "add", "."])
        msg = input("Commit message: ").strip()
        subprocess.run(["git", "commit", "-m", msg])
        subprocess.run(["git", "push", "origin", default_branch])
    else:
        new_branch = input("New branch name: ").strip()
        subprocess.run(["git", "checkout", "-b", new_branch])
        subprocess.run(["git", "add", "."])
        msg = input("Commit message: ").strip()
        subprocess.run(["git", "commit", "-m", msg])
        subprocess.run(["git", "push", "--set-upstream", "origin", new_branch])


def get_current_branch() -> str:
    """
    Returns the name of the current Git branch as a string.

    Executes a Git command to determine the active branch in the local repository.
    """
    import subprocess

    return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()

# Extended git_utils.py with new functionality while maintaining existing structure

def get_added_modified_files(from_ref: str = "HEAD~1", to_ref: str = "HEAD") -> List[str]:
    """
    Returns a list of files that were added or modified between two Git references.

    Uses 'git diff --diff-filter=AM --name-only' to identify only added and modified files,
    excluding deleted files. Provides robust error handling for cross-platform compatibility.

    Args:
        from_ref (str): The starting Git reference (commit, branch, tag). Defaults to 'HEAD~1'.
        to_ref (str): The ending Git reference (commit, branch, tag). Defaults to 'HEAD'.

    Returns:
        List[str]: A list of added and modified file paths.
    """
    cmd = ["git", "diff", "--diff-filter=AM", "--name-only", from_ref, to_ref]
    try:
        # Try modern subprocess.run with text, encoding, errors
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=True,
        )
        output = result.stdout
    except subprocess.CalledProcessError:
        # Git returned non-zero exit code
        return []
    except TypeError:
        # Older Python: fallback to universal_newlines
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
            check=True,
        )
        output = result.stdout

    return [line for line in output.splitlines() if line]


def get_added_modified_py_files(from_ref: str = "HEAD~1", to_ref: str = "HEAD") -> List[str]:
    """
    Returns a list of Python files that were added or modified between two Git references.

    Combines the functionality of git diff filtering with Python file filtering.
    Useful for targeting test execution to only modified Python code.

    Args:
        from_ref (str): The starting Git reference (commit, branch, tag). Defaults to 'HEAD~1'.
        to_ref (str): The ending Git reference (commit, branch, tag). Defaults to 'HEAD'.

    Returns:
        List[str]: A list of added and modified Python file paths.
    """
    files = get_added_modified_files(from_ref, to_ref)
    return [file for file in files if file.endswith(".py")]


def get_changed_files_as_dict(from_ref: str = "HEAD~1", to_ref: str = "HEAD") -> dict:
    """
    Returns a dictionary of changed files between two Git references.

    Formats the output as a structured dictionary suitable for JSON serialization,
    which is useful for CI pipelines and test routing.

    Args:
        from_ref (str): The starting Git reference (commit, branch, tag). Defaults to 'HEAD~1'.
        to_ref (str): The ending Git reference (commit, branch, tag). Defaults to 'HEAD'.

    Returns:
        dict: A dictionary with 'changed_files' key containing the list of changed files.
    """
    files = get_added_modified_files(from_ref, to_ref)
    return {"changed_files": files}