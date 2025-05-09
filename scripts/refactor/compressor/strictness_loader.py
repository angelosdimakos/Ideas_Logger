# scripts/refactor/compressor/strictness_loader.py
import json, gzip, pathlib
import pandas as pd
from typing import Any, Dict
from .strictness_squeezer import decompress_obj   # ← already defined

def _read(path: pathlib.Path) -> Dict[str, Any]:
    raw = path.read_bytes()
    if path.suffix == ".gz":          # let you gzip it later
        raw = gzip.decompress(raw)
    return json.loads(raw.decode())

def load(path: str | pathlib.Path) -> Dict[str, Any]:
    """Load *compressed* strictness JSON and return the original structure."""
    return decompress_obj(_read(pathlib.Path(path)))

# Optional helper -----------------------------------------------------------
def to_dataframe(path: str | pathlib.Path) -> pd.DataFrame:
    """Return a DataFrame with one row per test case (ready for Streamlit)."""
    blob = _read(pathlib.Path(path))
    files   = blob["files"]
    methods = blob["methods"]

    rows = []
    for t in blob["tests"]:
        (name, file_i, start, end,
         asserts, mocks, raises, branches, length,
         hits, ratio, strictness,
         prod_files, prod_methods,
         pcc, severity) = t
        rows.append({
            "name":          name,
            "test_file":     files[file_i],
            "loc":           end - start + 1,
            "asserts":       asserts,
            "mocks":         mocks,
            "branches":      branches,
            "strictness":    strictness,
            "severity":      severity or 0,
            "prod_files":    [files[i] for i in prod_files],
            "prod_methods":  [methods[i][0] for i in prod_methods],
        })
    return pd.DataFrame(rows)
