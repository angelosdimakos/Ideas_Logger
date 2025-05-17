import json
import gzip
import bz2
import lzma
import os
from pathlib import Path
from typing import Any, Dict, IO

_COMPRESSED_READERS: dict[str, callable[[str | os.PathLike], IO[bytes]]] = {
    ".gz": gzip.open,
    ".bz2": bz2.open,
    ".xz": lzma.open,
}


def load_json_any(path: str | os.PathLike) -> Dict[str, Any]:
    """
    Load .json or compressed .json.{gz,bz2,xz} transparently.
    Returns {} on missing file for caller-side resilience.
    """
    p = Path(path)
    if not p.exists():
        return {}

    reader = _COMPRESSED_READERS.get(p.suffix, open)  # fall back to plain open
    mode = "rt" if reader is open else "rt"  # text mode either way
    with reader(p, mode, encoding="utf-8") as f:
        return json.load(f)
