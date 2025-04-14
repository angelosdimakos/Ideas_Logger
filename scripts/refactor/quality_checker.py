import json
import subprocess
from pathlib import Path


BLACK_REPORT = "black.txt"
FLAKE8_REPORT = "flake8.json"
MYPY_REPORT = "mypy.txt"


# Utility to run a command and capture its output
def run_command(cmd, output_file):
    result = subprocess.run(cmd, capture_output=True, text=True)
    Path(output_file).write_text(result.stdout.strip())
    return result.returncode


def run_black():
    return run_command(["black", "--check", "scripts"], BLACK_REPORT)


def run_flake8():
    return run_command(["flake8", "--format=json", "scripts"], FLAKE8_REPORT)


def run_mypy():
    return run_command(["mypy", "--strict", "--no-color-output", "scripts"], MYPY_REPORT)


def merge_into_refactor_guard(audit_path="refactor_audit.json"):
    if not Path(audit_path).exists():
        print("❌ Missing refactor audit JSON!")
        return

    with open(audit_path, "r", encoding="utf-8-sig") as f:
        audit = json.load(f)

    # Add flake8 results
    if Path(FLAKE8_REPORT).exists():
        with open(FLAKE8_REPORT) as f:
            flake_data = json.load(f)
        for file, issues in flake_data.items():
            audit.setdefault(file, {})["flake8"] = issues

    # Add black (just flag per file)
    if Path(BLACK_REPORT).exists():
        black_lines = Path(BLACK_REPORT).read_text().splitlines()
        for line in black_lines:
            if "would reformat" in line:
                file = line.split(" ")[-1]
                audit.setdefault(file, {})["black"] = "needs formatting"

    # Add mypy output
    if Path(MYPY_REPORT).exists():
        for line in Path(MYPY_REPORT).read_text().splitlines():
            if ".py" in line and ": error:" in line:
                file = line.split(":")[0]
                audit.setdefault(file, {}).setdefault("mypy", []).append(line.strip())

    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)

    print("✅ RefactorGuard audit enriched with lint/type info!")


if __name__ == "__main__":
    run_black()
    run_flake8()
    run_mypy()
    merge_into_refactor_guard()
