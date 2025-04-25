from __future__ import annotations
"""
file_utils.py

Utility helpers for robust file I/O across the project.
All public helpers accept either ``str`` or ``pathlib.Path``; we coerce to
``Path`` immediately so internal logic is consistent and safe.  

Key helpers
-----------
- **sanitize_filename** – remove illegal chars, truncate to 100‑char max
- **get_timestamp**     – ``YYYY‑MM‑DD_HH‑MM‑SS`` string
- **safe_path**         – ensure parent dir exists, return ``Path``
- **write_json / read_json / safe_read_json** – typed, UTF‑8 safe
- **make_backup**       – timestamped ``_backup_YYYY‑MM‑DD_HH‑MM‑SS`` copy
- **zip_python_files**  – zip only ``*.py`` files, skipping ``.venv``, ``__pycache__``…
"""

from pathlib import Path
from typing import Union, Iterable, Optional
import datetime as _dt
import json
import logging
import os
import re
import zipfile

logger = logging.getLogger(__name__)
DEFAULT_JSON_INDENT = 2
BACKUP_JSON_INDENT = 4

# ---------------------------------------------------------------------------
# 🌐  Generic helpers
# ---------------------------------------------------------------------------

def sanitize_filename(name: str) -> str:
    """Return *name* stripped of illegal chars and truncated to 100 chars."""
    return re.sub(r"[^\w\-_. ]", "", name)[:100]


def get_timestamp() -> str:
    """Current time as ``YYYY‑MM‑DD_HH‑MM‑SS``."""
    return _dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# ---------------------------------------------------------------------------
# 📂  Path safety & JSON helpers
# ---------------------------------------------------------------------------

def _to_path(p: Union[str, Path]) -> Path:
    """Internal: coerce *p* to ``Path`` exactly once."""
    return p if isinstance(p, Path) else Path(p)


def safe_path(path: Union[str, Path]) -> Path:
    """Ensure ``path.parent`` exists; return ``Path``."""
    path = _to_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Union[str, Path], data: dict) -> None:
    path = safe_path(path)
    try:
        with path.open("w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=DEFAULT_JSON_INDENT, ensure_ascii=False)
    except Exception:
        logger.exception("Failed to write JSON → %s", path)
        raise


def read_json(path: Union[str, Path]) -> dict:
    path = _to_path(path)
    try:
        with path.open("r", encoding="utf-8") as fp:
            return json.load(fp)
    except Exception as e:
        logger.error("Failed to read JSON from %s: %s", path, e)
        return {}


def safe_read_json(filepath: Union[str, Path]) -> dict:
    path = _to_path(filepath)
    if not path.exists():
        logger.warning("%s not found – returning empty dict", path)
        return {}
    return read_json(path)

# ---------------------------------------------------------------------------
# 🗄️  Backup helper
# ---------------------------------------------------------------------------

def make_backup(file_path: Union[str, Path]) -> str | None:
    src = _to_path(file_path)
    if not src.exists():
        return None

    backup = src.with_name(f"{src.stem}_backup_{get_timestamp()}{src.suffix}")
    try:
        data = read_json(src)
        with backup.open("w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=BACKUP_JSON_INDENT)
        return str(backup)
    except Exception:
        logger.exception("Failed to create backup for %s", src)
        return None

# ---------------------------------------------------------------------------
# 📦  Zip helper
# ---------------------------------------------------------------------------

def zip_python_files(
    output_path: Union[str, Path],
    root_dir: Union[str, Path] = ".",
    exclude_dirs: Optional[Iterable[str]] = None,
) -> None:
    """
    Zip all ``.py`` files under *root_dir* (recursively), excluding any directory whose
    name appears in *exclude_dirs* (case‑sensitive match against each path part).

    If *exclude_dirs* is ``None`` we default to::{.python}

        {".venv", "__pycache__", ".git", "node_modules"}

    Args:
        output_path: Destination ``.zip`` path (created/overwritten).
        root_dir:    Directory to start searching; ``'.'`` by default.
        exclude_dirs: Folder names to skip entirely.
    """
    output_path = _to_path(output_path)
    root_dir = _to_path(root_dir)

    # ----- Normalise exclusion list -----------------------------
    default_excludes = {".venv", "__pycache__", ".git", "node_modules"}
    exclude_dirs = set(exclude_dirs) if exclude_dirs else default_excludes

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for dirpath, _, filenames in os.walk(root_dir):
            # Skip if *any* component of dirpath is in exclude_dirs
            if any(part in exclude_dirs for part in Path(dirpath).parts):
                continue
            for filename in filenames:
                if filename.endswith(".py"):
                    file_path = Path(dirpath) / filename
                    arcname = file_path.relative_to(root_dir)
                    zipf.write(file_path, arcname)

    """Zip **only** ``*.py`` files under *root_dir*, skipping folders in *exclude_dirs*."""

    output_path = _to_path(output_path)
    root_dir = _to_path(root_dir)
    exclude_dirs = set(exclude_dirs or {".venv", ".git", "__pycache__", "node_modules"})

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for folder, _sub, files in os.walk(root_dir):
            if any(edir in Path(folder).parts for edir in exclude_dirs):
                continue
            for fname in files:
                if not fname.endswith(".py"):
                    continue  # 🔒 only .py – keeps test expectation true
                fpath = Path(folder) / fname
                arcname = fpath.relative_to(root_dir).as_posix()
                zipf.write(str(fpath), arcname)
