import os
import sys
import subprocess
import re
from datetime import datetime

# Enable importing git_utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.utils.git_utils import interactive_commit_flow


def get_current_branch():
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True
    )
    return result.stdout.strip()


def get_modified_files():
    result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
    return result.stdout.strip().splitlines()


def is_valid_branch_name(name):
    return bool(re.match(r"^[\w\-/]+$", name))  # Alphanumeric, underscore, dash, slash


def generate_suggested_branch_name():
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
        return  # <- to stop execution in test context

    print(f"⏳ Running: git checkout -b {new_branch}")
    try:
        subprocess.run(["git", "checkout", "-b", new_branch], check=True)
        print(f"🌱 Created and switched to: {new_branch}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        sys.exit(1)


if __name__ == "__main__":
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
