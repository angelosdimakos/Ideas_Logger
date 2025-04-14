# scripts/utils/git_utils.py
import subprocess


def get_changed_files(ref: str = "origin/main") -> list[str]:
    """Returns a list of changed Python files compared to a Git reference (default: origin/main)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", ref], capture_output=True, text=True, check=True
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip().endswith(".py")]
    except subprocess.CalledProcessError as e:
        print(f"❌ Git diff failed: {e}")
        return []


def interactive_commit_flow(default_branch="main"):
    import subprocess

    print("\n🧠 Commit Assistant:")
    print(f"You're on branch: {get_current_branch()}")

    choice = (
        input(f"👉 Push to [{default_branch}] or create a new branch? (main/new): ").strip().lower()
    )

    if choice == "main":
        subprocess.run(["git", "add", "."])
        msg = input("📝 Commit message: ").strip()
        subprocess.run(["git", "commit", "-m", msg])
        subprocess.run(["git", "push", "origin", default_branch])
    else:
        new_branch = input("🔧 New branch name: ").strip()
        subprocess.run(["git", "checkout", "-b", new_branch])
        subprocess.run(["git", "add", "."])
        msg = input("📝 Commit message: ").strip()
        subprocess.run(["git", "commit", "-m", msg])
        subprocess.run(["git", "push", "--set-upstream", "origin", new_branch])


def get_current_branch():
    import subprocess

    return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
