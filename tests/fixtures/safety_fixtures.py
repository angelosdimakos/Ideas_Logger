"""
Test Safety and Integrity Safeguards

This module provides fixtures for ensuring test integrity, preventing writes
to production paths, and maintaining the safety of the test environment.
"""
import pytest
from pathlib import Path
from typing import Any


# ===========================
# 🐧 CONFTEST CANARY
# ===========================
@pytest.fixture(autouse=True, scope="session")
def watch_conftest_integrity() -> None:
    """
    Watches the integrity of the conftest.py file.
    """
    original_path = Path(__file__).parent.parent / "conftest.py"
    if not original_path.exists():
        raise RuntimeError("🔥 CRITICAL: conftest.py is missing before test session starts!")

    yield

    if not original_path.exists():
        raise RuntimeError("🛑 ALERT: conftest.py was deleted during test run!")


# ===========================
# 🫯 GUARDRAILS
# ===========================
@pytest.fixture(autouse=True)
def prevent_production_path_writes(monkeypatch: Any) -> None:
    """
    Prevents writes to production paths.

    Args:
        monkeypatch (Any): The monkeypatch object to use for patching.
    """
    original_open = open

    def guarded_open(file, mode="r", *args, **kwargs):
        file_path = str(file)
        if (
            "zephyrus_log.json" in file_path or "correction_summaries.json" in file_path
        ) and "test" not in file_path:
            raise PermissionError(f"❌ Blocked access to production file during test: {file_path}")
        return original_open(file, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", guarded_open)


SAFE_DIRS = {
    ".git",
    ".venv",
    ".pytest_cache",
    "htmlcov",
    "__pycache__",
    "site-packages",
    ".mypy_cache",
    ".vscode",
}
SAFE_EXTS = {
    ".py",
    ".pyc",
    ".pyo",
    ".ini",
    ".toml",
    ".md",
    ".zip",
    ".exe",
    ".html",
    ".json",
    ".coverage",
    ".coveragerc",
    ".txt",
    ".spec",
    ".log",
}


@pytest.fixture(scope="session", autouse=True)
def assert_all_output_in_temp(tmp_path_factory: Any) -> None:
    """
    Asserts all output is in the temporary directory.

    Args:
        tmp_path_factory (Any): The temporary path factory.
    """
    tmp_root = tmp_path_factory.getbasetemp().resolve()
    root_dir = Path(".").resolve()

    # Take a snapshot of the files BEFORE test run
    before = {p.resolve() for p in root_dir.rglob("*") if p.is_file()}

    yield  # let the tests run

    # Take a snapshot AFTER test run
    after = {p.resolve() for p in root_dir.rglob("*") if p.is_file()}
    new_files = after - before

    ALLOWED_OUTPUT = {
        "coverage.xml",
        ".coverage",
        ".coverage.*",  # xdist shards
    }
    ALLOWED_DIRS = {
        "htmlcov",
    }

    for path in new_files:
        relative = path.relative_to(root_dir)

        # ✅ Skip safe locations
        if (
            any(part in SAFE_DIRS for part in relative.parts)
            or path.suffix in SAFE_EXTS
            or tmp_root in path.parents
            or str(relative).startswith("tests/mock_data/")
            or relative.name.startswith(".coverage.")  # ✅ Ignore xdist coverage fragments
            or relative.name in ALLOWED_OUTPUT
            or relative.parts[0] in ALLOWED_DIRS
        ):
            continue

        raise AssertionError(f"🚨 Test output leaked outside tmp dir: {relative}")