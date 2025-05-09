"""strictness_squeezer.py
================================
Bespoke *loss‑less* compressor / decompressor for the
`strictness_mapping.json` report produced by the strictness‑analyser.

Changes (2025‑05‑09)
--------------------
* **Optional fields handled** – `prod_code_complexity` and
  `severity_score` are not guaranteed to be present in every test entry.
  They are now treated as optional (stored as `None` if absent and omitted
  on decompression when `None`).

CLI
---
```bash
python strictness_squeezer.py compress    <in.json> <out.json>
python strictness_squeezer.py decompress  <in.json> <out.json>
python strictness_squeezer.py selftest    <in.json>
```

Standard‑library‑only; no external deps.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Compressor
# ---------------------------------------------------------------------------

def _ensure_idx(item: Any, lst: List[Any], index: Dict[Any, int]) -> int:
    """Return existing index of *item* in *lst* or append and return new one."""
    try:
        return index[item]
    except KeyError:
        idx = len(lst)
        lst.append(item)
        index[item] = idx
        return idx


def compress_obj(src: Dict[str, Any]) -> Dict[str, Any]:
    """Return the compact representation of **strictness_mapping.json**."""

    files: List[str] = []
    file_idx: Dict[str, int] = {}

    methods: List[Tuple] = []
    method_idx: Dict[Tuple, int] = {}

    def _fid(path: str) -> int:
        return _ensure_idx(path, files, file_idx)

    def _mid(m: Dict[str, Any]) -> int:
        key = (m["name"], m["file"], tuple(m["line_range"]), m["complexity"])
        if key not in method_idx:
            method_idx[key] = len(methods)
            methods.append([m["name"], _fid(m["file"]), m["line_range"], m["complexity"]])
        return method_idx[key]

    tests: List[List[Any]] = []

    for t in src["test_to_prod_mapping"]:
        pcc = t.get("prod_code_complexity")
        sev = t.get("severity_score")
        tests.append([
            t["name"],
            _fid(t["file"]),
            t["start"],
            t["end"],
            t["asserts"],
            t["mocks"],
            t["raises"],
            t["branches"],
            t["length"],
            t["coverage_hits"],
            t["hit_ratio"],
            t["strictness_score"],
            [_fid(p) for p in t.get("covers_prod_files", [])],
            [_mid(m) for m in t.get("covers_prod_methods", [])],
            pcc,
            sev,
        ])

    compact = {
        "summary": src.get("summary", {}),  # passthrough unchanged
        "files": files,
        "methods": methods,
        "tests": tests,
    }
    return compact


# ---------------------------------------------------------------------------
# Decompressor
# ---------------------------------------------------------------------------

def decompress_obj(blob: Dict[str, Any]) -> Dict[str, Any]:
    files = blob["files"]
    methods = blob["methods"]

    def _method_from_id(i: int) -> Dict[str, Any]:
        name, file_i, line_range, complexity = methods[i]
        return {
            "name": name,
            "file": files[file_i],
            "line_range": line_range,
            "complexity": complexity,
        }

    test_objs: List[Dict[str, Any]] = []

    for row in blob["tests"]:
        (
            name,
            file_i,
            start,
            end,
            asserts,
            mocks,
            raises,
            branches,
            length,
            hits,
            ratio,
            strictness,
            prod_files,
            prod_methods,
            pcc,
            sev,
        ) = row

        obj = {
            "name": name,
            "file": files[file_i],
            "start": start,
            "end": end,
            "asserts": asserts,
            "mocks": mocks,
            "raises": raises,
            "branches": branches,
            "length": length,
            "coverage_hits": hits,
            "hit_ratio": ratio,
            "strictness_score": strictness,
            "covers_prod_files": [files[i] for i in prod_files],
            "covers_prod_methods": [_method_from_id(i) for i in prod_methods],
        }
        if pcc is not None:
            obj["prod_code_complexity"] = pcc
        if sev is not None:
            obj["severity_score"] = sev
        test_objs.append(obj)

    return {
        "summary": blob.get("summary", {}),
        "test_to_prod_mapping": test_objs,
    }


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------

def _cli() -> None:
    p = argparse.ArgumentParser(description="Compress or decompress strictness_mapping.json")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("compress", help="compress <in> <out>")
    c.add_argument("infile", type=Path)
    c.add_argument("outfile", type=Path)

    d = sub.add_parser("decompress", help="decompress <in> <out>")
    d.add_argument("infile", type=Path)
    d.add_argument("outfile", type=Path)

    t = sub.add_parser("selftest", help="self‑test round‑trip <in>")
    t.add_argument("infile", type=Path)

    args = p.parse_args()

    if args.cmd == "compress":
        original = json.loads(args.infile.read_text())
        compact = compress_obj(original)
        args.outfile.write_text(json.dumps(compact, separators=(",", ":")))

    elif args.cmd == "decompress":
        compact = json.loads(args.infile.read_text())
        restored = decompress_obj(compact)
        args.outfile.write_text(json.dumps(restored, indent=2))

    elif args.cmd == "selftest":
        original = json.loads(args.infile.read_text())
        roundtrip = decompress_obj(compress_obj(original))
        if original == roundtrip:
            print("✓ round‑trip OK")
            sys.exit(0)
        else:
            print("✗ round‑trip failed", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    _cli()
