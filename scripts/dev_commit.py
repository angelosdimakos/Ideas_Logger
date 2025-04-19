import os
import sys
import subprocess
import re
from datetime import datetime

# Enable importing git_utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.utils.git_utils import interactive_commit_flow


def get_current_branch():
    """
    Returns the name of the current Git branch.

    Returns:
        str: The current branch name.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,  # <-- Add this line
    )

    return result.stdout.strip()


def get_modified_files():
    """
    Returns a list of files modified (but not yet committed) in the current Git working directory.

    Returns:
        list[str]: List of modified file paths.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip().splitlines()
    except subprocess.CalledProcessError:
        return []


def is_valid_branch_name(name):
    """
    Checks if the provided branch name is valid according to Git naming conventions.

    Args:
        name (str): The branch name to validate.

    Returns:
        bool: True if the branch name is valid, False otherwise.
    """
    return bool(re.match(r"^[\w\-/]+$", name))  # Alphanumeric, underscore, dash, slash


def generate_suggested_branch_name():
    """
    Generates a suggested branch name based on modified files and the current date.

    Returns:
        str: A suggested branch name in the format 'fix/<keywords>-<date>'.
    """
    files = get_modified_files()
    keywords = []

    for file in files:
        parts = file.replace("\\", "/").split("/")
        if len(parts) >= 2:
            keywords.append(parts[-2])  # e.g., "gui" from gui/gui.py
        else:
            keywords.append(parts[0].replace(".py", ""))

    keywords = list(set(keywords))[:2] or ["manual"]
    base = "-".join(keywords)
    date = datetime.now().strftime("%Y-%m-%d")
    return f"fix/{base}-{date}"


def switch_to_new_branch():
    """
    Prompts the user to create and switch to a new Git branch.
    Suggests a branch name based on modified files and validates user input.
    Exits the script if the branch name is invalid or if Git fails to create or push the branch.
    """
    try:
        suggested = generate_suggested_branch_name()
    except Exception as e:
        print(f"⚠️ Failed to generate suggested branch name: {e}")
        suggested = "feature/manual-" + datetime.now().strftime("%Y%m%d-%H%M")

    print(f"\n💡 Suggested branch: `{suggested}`")
    user_input = input(f"🔧 New branch name [{suggested}]: ").strip()
    new_branch = user_input or suggested

    if not is_valid_branch_name(new_branch):
        print(
            "❌ Invalid branch name. Use only letters, numbers, dashes, slashes, and underscores."
        )
        sys.exit(1)
        return

    print(f"⏳ Running: git checkout -b {new_branch}")
    try:
        subprocess.run(["git", "checkout", "-b", new_branch], check=True)
        print(f"🌱 Created and switched to: {new_branch}")

        # ✅ Automatically push the new branch
        print(f"📤 Pushing new branch to origin...")
        subprocess.run(["git", "push", "--set-upstream", "origin", new_branch], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        sys.exit(1)
        return


if __name__ == "__main__":
    """
    Main script logic:
    - Checks the current branch.
    - Prevents direct commits to 'main' or 'master'.
    - Prompts the user to create a new branch if necessary.
    - Initiates the interactive commit flow.
    """
    try:
        current_branch = get_current_branch()
        print(f"🌿 Current branch: {current_branch}")

        if current_branch in ["main", "master"]:
            print("🚫 Commits to main are blocked by law.")
            response = input("👉 Create a new branch? (y/n): ").strip().lower()
            if response == "y":
                switch_to_new_branch()
                current_branch = get_current_branch()
            else:
                print("❌ Commit aborted. Please branch responsibly.")
                sys.exit(1)

        # Safe to commit
        interactive_commit_flow(default_branch=current_branch)

    except KeyboardInterrupt:
        print("\n🚫 Commit canceled by user.")
