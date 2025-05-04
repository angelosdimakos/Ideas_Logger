"""
helpers.py – tiny utilities shared by the quality-checker core & plugins.
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
    """Print `msg` even on exotic console encodings (swallows UnicodeEncodeError)."""
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
    """
    proc = subprocess.run(cmd, capture_output=True,
                                encoding="utf-8",
                                text=True,
                                errors="replace"
                          )
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
    """
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        with path.open("rb") as fh:
            return fh.read().decode("utf-8", errors="replace")
