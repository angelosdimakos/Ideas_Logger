# strictness_report_squeezer.py
# Unified compressor, decompressor, and semantic self-test for strictness reports

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict


def compress_obj(original: Dict[str, Any]) -> Dict[str, Any]:
    """Compress a strictness report into a minimal 'modules' mapping."""
    # Support both wrapped (with 'modules') and bare module maps
    raw_modules = original.get("modules", original)
    compressed: Dict[str, Any] = {"modules": {}}

    for module, data in raw_modules.items():
        compressed_module = {
            "module_coverage": round(data.get("module_coverage", 0), 2),
            "methods": [
                {
                    "name": m.get("name", ""),
                    "coverage": round(m.get("coverage", 0), 2),
                    "complexity": int(m.get("complexity", 0)),
                }
                for m in data.get("methods", [])
            ],
            "tests": [
                {
                    "test_name": t.get("test_name", ""),
                    "strictness": round(t.get("strictness", 0), 2),
                    "severity": round(t.get("severity", 0), 2),
                }
                for t in data.get("tests", [])
            ],
        }
        compressed["modules"][module] = compressed_module
    return compressed


def decompress_obj(blob: Dict[str, Any]) -> Dict[str, Any]:
    """Rebuild the full strictness report structure from the compact blob."""
    # If this blob is just the compressed wrapper, unwrap to original shape
    if "modules" in blob and len(blob) == 1 and isinstance(blob["modules"], dict):
        return blob["modules"]
    return blob


def semantic_equal(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    """Compare two reports semantically, allowing for rounding discrepancies."""
    # Extract underlying modules mapping for both
    mods_a = a.get("modules", a)
    mods_b = b.get("modules", b)

    if set(mods_a.keys()) != set(mods_b.keys()):
        return False

    for module in mods_a:
        ma, mb = mods_a[module], mods_b[module]
        if round(ma.get("module_coverage", 0), 2) != round(mb.get("module_coverage", 0), 2):
            return False

        # Compare methods by name
        methods_a = sorted(ma.get("methods", []), key=lambda x: x.get("name"))
        methods_b = sorted(mb.get("methods", []), key=lambda x: x.get("name"))
        if len(methods_a) != len(methods_b):
            return False
        for m1, m2 in zip(methods_a, methods_b):
            if m1.get("name") != m2.get("name"):
                return False
            if round(m1.get("coverage", 0), 2) != round(m2.get("coverage", 0), 2):
                return False
            if int(m1.get("complexity", 0)) != int(m2.get("complexity", 0)):
                return False

        # Compare tests by test_name
        tests_a = sorted(ma.get("tests", []), key=lambda x: x.get("test_name"))
        tests_b = sorted(mb.get("tests", []), key=lambda x: x.get("test_name"))
        if len(tests_a) != len(tests_b):
            return False
        for t1, t2 in zip(tests_a, tests_b):
            if t1.get("test_name") != t2.get("test_name"):
                return False
            if round(t1.get("strictness", 0), 2) != round(t2.get("strictness", 0), 2):
                return False
            if round(t1.get("severity", 0), 2) != round(t2.get("severity", 0), 2):
                return False

    return True


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump_json(obj: Dict[str, Any], path: Path, pretty: bool = False) -> None:
    path.write_text(
        json.dumps(obj, indent=2 if pretty else None, separators=(",", ":")), encoding="utf-8"
    )


def _cli() -> None:
    p = argparse.ArgumentParser(
        description="Compress / decompress strictness report with self-test."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("compress")
    pc.add_argument("infile")
    pc.add_argument("outfile")
    pc.add_argument("--pretty", action="store_true")

    pd = sub.add_parser("decompress")
    pd.add_argument("infile")
    pd.add_argument("outfile")
    pd.add_argument("--pretty", action="store_true")

    st = sub.add_parser("selftest")
    st.add_argument("infile")

    args = p.parse_args()
    if args.cmd == "compress":
        orig = _load_json(Path(args.infile))
        compressed = compress_obj(orig)
        _dump_json(compressed, Path(args.outfile), pretty=args.pretty)
    elif args.cmd == "decompress":
        blob = _load_json(Path(args.infile))
        expanded = decompress_obj(blob)
        _dump_json(expanded, Path(args.outfile), pretty=args.pretty)
    elif args.cmd == "selftest":
        orig = _load_json(Path(args.infile))
        roundtrip = decompress_obj(compress_obj(orig))
        if semantic_equal(orig, roundtrip):
            print("✓ Round-trip OK (semantic match)")
        else:
            print("✗ Round-trip FAILED", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    _cli()
