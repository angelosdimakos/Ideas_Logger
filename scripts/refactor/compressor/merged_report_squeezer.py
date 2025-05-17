from __future__ import annotations

import argparse
import gzip
import json
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ----------------------------------------------------------------------------
# core helpers
# ----------------------------------------------------------------------------

DocTriple = Tuple[str | None, str | None, str | None]


def _get_or_add(triple: DocTriple, cache: Dict[DocTriple, int], table: List[List[Any]]) -> int:
    """Return ID for *triple*; create a new one if unseen."""
    if triple not in cache:
        cache[triple] = len(table)
        table.append(list(triple))  # store as list to save a few chars
    return cache[triple]


def _calc_percent(cov_blob: dict[str, Any]) -> float | None:
    """
    Return overall file-coverage percentage if the *complexity* section
    provides enough data, otherwise None.
    """
    comp = cov_blob.get("complexity")
    if not comp:
        return None

    total = covered = 0
    for stats in comp.values():
        lines = stats.get("lines", 0)
        total += lines
        cov = stats.get("covered_lines", 0)
        if isinstance(cov, list):
            covered += len(cov)
        else:
            covered += cov

    return round(100 * covered / total, 1) if total else None


# ----------------------------------------------------------------------------
# Compression
# ----------------------------------------------------------------------------


def compress_obj(original: Dict[str, Any], *, retain_keys: bool = False) -> Dict[str, Any]:
    """Return a *compact* structure with docstrings hoisted into a lookup table.

    Parameters
    ----------
    original
        The full‑fidelity merged_report dict loaded from JSON.
    retain_keys
        If True, keep verbose dict keys inside each docstring record instead of
        positional arrays.  (Adds ~2 kB gzipped – handy for debugging.)
    """
    doc_table: List[List[Any]] = []
    cache: Dict[DocTriple, int] = {}
    files_blob: Dict[str, Any] = {}

    for file_path, report in original.items():
        # -------------------------------------------------- docstrings block
        ds = report.get("docstrings", {})
        module_doc = ds.get("module_doc", {})
        module_id = (
            _get_or_add(
                (module_doc.get("description"), module_doc.get("args"), module_doc.get("returns")),
                cache,
                doc_table,
            )
            if module_doc
            else None
        )

        cls_arr: List[Tuple[str, int]] = []
        for cls in ds.get("classes", []):
            cls_arr.append(
                (
                    cls.get("name", ""),
                    _get_or_add(
                        (cls.get("description"), cls.get("args"), cls.get("returns")),
                        cache,
                        doc_table,
                    ),
                )
            )

        fn_arr: List[Tuple[str, int]] = []
        for fn in ds.get("functions", []):
            fn_arr.append(
                (
                    fn.get("name", ""),
                    _get_or_add(
                        (fn.get("description"), fn.get("args"), fn.get("returns")), cache, doc_table
                    ),
                )
            )

        doc_block = (
            {"m": module_id, "c": cls_arr, "f": fn_arr}
            if not retain_keys
            else {"module_doc": module_id, "classes": cls_arr, "functions": fn_arr}
        )

        # -------------------------------------------------- coverage block + percent calculation
        cov_blob: Dict[str, Any] = report.get("coverage", {})
        percent = _calc_percent(cov_blob)
        if percent is not None:
            # prepend 'p' key so percent is first
            cov_blob = {"p": percent, **cov_blob}

        # -------------------------------------------------- assemble new report
        files_blob[file_path] = {"d": doc_block, "cov": cov_blob, "lint": report.get("linting", {})}

    return {"doc": doc_table, "files": files_blob}


# ----------------------------------------------------------------------------
# Decompression
# ----------------------------------------------------------------------------


def decompress_obj(blob: Dict[str, Any]) -> Dict[str, Any]:
    """Rebuild the full merged_report structure from the compact *blob*."""
    doc_table: List[List[Any]] = blob["doc"]

    def _expand(doc_id: int | None) -> Dict[str, Any]:
        if doc_id is None:
            return {"description": None, "args": None, "returns": None}
        descr, args, returns = doc_table[doc_id]
        return {"description": descr, "args": args, "returns": returns}

    rebuilt: Dict[str, Any] = {}
    for file_path, comp in blob["files"].items():
        dblock = comp["d"]
        module_doc = _expand(dblock.get("m"))
        classes = [{"name": name, **_expand(doc_id)} for name, doc_id in dblock.get("c", [])]
        functions = [{"name": name, **_expand(doc_id)} for name, doc_id in dblock.get("f", [])]

        cov_blob = comp.get("cov", {}).copy()
        cov_blob.pop("p", None)
        rebuilt[file_path] = {
            "docstrings": {"module_doc": module_doc, "classes": classes, "functions": functions},
            "coverage": cov_blob,
            "linting": comp.get("lint", {}),
        }

    return rebuilt


# ----------------------------------------------------------------------------
# File helpers (optional gzip)
# ----------------------------------------------------------------------------


def _load_json(path: Path) -> Dict[str, Any]:
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return json.loads(data.decode())


def _dump_json(
    obj: Dict[str, Any], path: Path, *, pretty: bool = False, gzip_level: int | None = None
) -> None:
    txt = json.dumps(obj, indent=2 if pretty else None, separators=(",", ":"))
    b = txt.encode()
    if gzip_level is not None:
        b = gzip.compress(b, compresslevel=gzip_level)
    path.write_bytes(b)


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------


def _cli() -> None:
    p = argparse.ArgumentParser(description="Compress / decompress merged_report.json")
    sub = p.add_subparsers(dest="cmd", required=True)

    # compress
    pc = sub.add_parser("compress")
    pc.add_argument("infile")
    pc.add_argument("outfile")
    pc.add_argument("--pretty", action="store_true", help="pretty‑print JSON (debug)")
    pc.add_argument(
        "--gzip", type=int, nargs="?", const=9, help="gzip level (default 9) → .gz suffix"
    )

    # decompress
    pd = sub.add_parser("decompress")
    pd.add_argument("infile")
    pd.add_argument("outfile")
    pd.add_argument("--pretty", action="store_true")

    # self‑test
    st = sub.add_parser("selftest")
    st.add_argument("infile")

    # percent viewer
    pv = sub.add_parser("percent", help="Show per-file coverage percentages from compressed report")
    pv.add_argument("infile")

    args = p.parse_args()
    cmd = args.cmd

    if cmd == "compress":
        orig = _load_json(Path(args.infile))
        compact = compress_obj(orig)
        _dump_json(compact, Path(args.outfile), pretty=args.pretty, gzip_level=args.gzip)

    elif cmd == "decompress":
        blob = _load_json(Path(args.infile))
        full = decompress_obj(blob)
        _dump_json(full, Path(args.outfile), pretty=args.pretty)

    elif cmd == "selftest":
        orig = _load_json(Path(args.infile))
        roundtrip = decompress_obj(compress_obj(orig))
        if orig == roundtrip:
            print("✓ round‑trip OK (loss‑less)")
        else:
            print("✗ round‑trip FAILED", file=sys.stderr)
            sys.exit(1)

    elif cmd == "percent":
        blob = _load_json(Path(args.infile))
        files = blob.get("files", {})
        if not files:
            print("No files found in compressed report.", file=sys.stderr)
            sys.exit(1)

        print(f"{'File':<50} {'Coverage (%)':>12}")
        print("-" * 65)
        for path, rep in files.items():
            short = os.path.basename(path)
            cov_blob = rep.get("cov", {})
            pct = cov_blob.get("p")
            if pct is None:
                pct = _calc_percent(cov_blob)
            pct_display = f"{pct:.1f}" if pct is not None else "—"
            print(f"{short:<50} {pct_display:>12}")


if __name__ == "__main__":
    _cli()
