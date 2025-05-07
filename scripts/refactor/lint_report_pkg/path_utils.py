"""
Path Utilities for Quality Audit Modules
===============================
This module provides common path helper functions used across quality and audit modules.

It includes functions for normalizing paths relative to the repository root.
"""

from pathlib import Path
import os

# Absolute path to the repository root (≈ directory that contains `scripts/`)
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def norm(p: str | os.PathLike) -> str:
    """
    Return a *repository-relative* normalized path.

    If the file lives outside the repo, fall back to “last-two components”
    to avoid collisions yet stay platform-agnostic.

    Args:
        p (str | os.PathLike): The path to normalize.

    Returns:
        str: The normalized repository-relative path.
    """
    p = Path(p).resolve()
    try:
        return str(p.relative_to(PROJECT_ROOT))
    except ValueError:  # outside repo – best-effort fallback
        return str(Path(*p.parts[-2:]))
