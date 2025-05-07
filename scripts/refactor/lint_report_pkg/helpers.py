"""
Helpers for Lint Report Package
===============================
This module provides utility functions shared by the quality-checker core and plugins.

It includes functions for running commands, printing safely, and reading report files.
"""

from __future__ import annotations

import subprocess
import os
from pathlib import Path
from typing import Sequence, Union


# ────────────────────────────────────────────────────────────────────────────────
# console convenience
# ────────────────────────────────────────────────────────────────────────────────
def safe_print(msg: str) -> None:
    """
    Print `msg` even on exotic console encodings (swallows UnicodeEncodeError).

    Args:
        msg (str): The message to print.
    """
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="ignore").decode())


# ────────────────────────────────────────────────────────────────────────────────
# generic subprocess helper
# ────────────────────────────────────────────────────────────────────────────────
def run_cmd(cmd: Sequence[str], output_file: Union[str, os.PathLike]) -> int:
    """
    Run *cmd*, write **combined stdout + stderr** to *output_file* (UTF-8),
    and return the subprocess' exit-code.

    Args:
        cmd (Sequence[str]): The command to run.
        output_file (Union[str, os.PathLike]): The file to write the output to.

    Returns:
        int: The exit code of the command.
    """
    proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", text=True, errors="replace")
    Path(output_file).write_text(
        ((proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")).strip(),
        encoding="utf-8",
    )
    return proc.returncode


# ────────────────────────────────────────────────────────────────────────────────
# file helpers
# ────────────────────────────────────────────────────────────────────────────────
def read_report(path: Path) -> str:
    """
    Return the textual contents of *path* (empty string if the file is missing),
    decoding as UTF-8 and falling back to “replace” for any bad bytes.

    Args:
        path (Path): The path to the report file.

    Returns:
        str: The contents of the report file.
    """
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
