"""
RefactorGuard: analyse refactors and (optionally) enrich the results with line‑coverage
information coming from a ``.coverage`` SQLite DB or a JSON export produced by Coverage.py.

Adds support for both `.coverage` and `coverage.json` formats. Automatically switches
parsers based on the extension.
"""

from __future__ import annotations

import argparse
import fnmatch
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.refactor.ast_extractor import compare_class_methods, extract_class_methods
from scripts.refactor.complexity.complexity_analyzer import (
    calculate_function_complexity_map,
)
from scripts.refactor.method_line_ranges import extract_method_line_ranges
from scripts.refactor.parsers.json_coverage_parser import parse_json_coverage

logger = logging.getLogger(__name__)


class AnalysisError(Exception):
    """Raised when an error occurs during analysis."""


class RefactorGuard:
    """Analyse / validate Python refactors."""

    def __init__(self, config: Optional[Dict[str, Any]] | None = None) -> None:
        self.config: Dict[str, Any] = config or {
            "max_complexity": 10,
            "ignore_files": [],
            "ignore_dirs": [],
            "coverage_path": ".coverage",
        }
        self.coverage_hits: Dict[str, Any] = {}

    def attach_coverage_hits(self, coverage_data: Dict[str, Dict[str, Any]]) -> None:
        flat = {}
        for file_methods in coverage_data.values():
            for method, stats in file_methods.items():
                flat[method] = stats
        self.coverage_hits = flat

    def analyze_tests(
        self, refactored_path: str, test_file_path: Optional[str] | None = None
    ) -> List[Dict[str, str]]:
        cov_path = self.config.get("coverage_path", ".coverage")
        abs_path = str(Path(refactored_path).resolve())
        force_fallback = self.config.get("force_fallback", False)

        if os.path.exists(cov_path) and not force_fallback:
            try:
                ranges = extract_method_line_ranges(refactored_path)
                parsed = parse_json_coverage(cov_path, ranges, filepath=refactored_path)

                if len(parsed) == 1:
                    covered = next(iter(parsed.values()))
                else:
                    covered = parsed.get(abs_path, {})

                zero_hit = {m for m, s in covered.items() if s.get("hits", 0) == 0}
                missing: List[Dict[str, str]] = []
                for cls in extract_class_methods(refactored_path):
                    for method in cls.methods:
                        if method in zero_hit:
                            missing.append({"class": cls.class_name, "method": method})
                return missing
            except Exception as exc:
                logger.warning("[Tests] Coverage‑based detection failed: %s", exc)

        # Fallback logic: assume all methods need tests
        fallback: List[Dict[str, str]] = []
        for cls in extract_class_methods(refactored_path):
            fallback.extend({"class": cls.class_name, "method": m} for m in cls.methods)
        return fallback

    def analyze_module(
        self,
        original_path: Optional[str],
        refactored_path: str,
        test_file_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "method_diff": {},
            "missing_tests": [],
            "complexity": {},
        }

        if (
            not original_path
            or not os.path.exists(original_path)
            or os.path.abspath(original_path) == os.path.abspath(refactored_path)
        ):
            orig_infos = {}
        else:
            orig_infos = {c.class_name: c for c in extract_class_methods(original_path)}

        ref_infos = {c.class_name: c for c in extract_class_methods(refactored_path)}

        for name, orig in orig_infos.items():
            if name in ref_infos:
                result["method_diff"][name] = compare_class_methods(orig, ref_infos[name])
            else:
                result["method_diff"][name] = {"missing": list(orig.methods), "added": []}

        for name, refc in ref_infos.items():
            if name not in orig_infos:
                result["method_diff"][name] = {"missing": [], "added": list(refc.methods)}

        result["missing_tests"] = self.analyze_tests(refactored_path, test_file_path)

        try:
            complexity_map = calculate_function_complexity_map(refactored_path)
        except Exception as e:
            raise AnalysisError(f"Failed complexity analysis: {e}")

        def _simple_name(qual: str) -> str:
            return qual.split(".")[-1]

        if self.coverage_hits:
            enriched: Dict[str, Any] = {}
            for qual, score in complexity_map.items():
                info = self.coverage_hits.get(qual, {})
                enriched[qual] = {
                    "complexity": score,
                    "coverage": info.get("coverage", "N/A"),
                    "hits": info.get("hits", "N/A"),
                    "lines": info.get("lines", "N/A"),
                    "covered_lines": info.get("covered_lines", []),
                    "missing_lines": info.get("missing_lines", []),
                }
            result["complexity"] = enriched
        else:
            result["complexity"] = {
                m: {
                    "complexity": sc,
                    "coverage": "N/A",
                    "hits": "N/A",
                    "lines": "N/A",
                }
                for m, sc in complexity_map.items()
            }

        return result

    def analyze_directory_recursive(
        self, original_dir: str, refactored_dir: str, test_dir: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        summary: Dict[str, Dict[str, Any]] = {}
        ignore_files = self.config.get("ignore_files", [])
        ignore_dirs = set(self.config.get("ignore_dirs", []))

        for root, dirs, files in os.walk(original_dir):
            rel_root = os.path.relpath(root, original_dir)
            for d in list(dirs):
                if d in ignore_dirs or fnmatch.fnmatch(os.path.join(rel_root, d), d):
                    dirs.remove(d)

            for fn in files:
                if not fn.endswith(".py"):
                    continue
                rel_path = os.path.relpath(os.path.join(root, fn), original_dir)
                if any(fnmatch.fnmatch(rel_path, pat) for pat in ignore_files):
                    continue

                orig = os.path.join(original_dir, rel_path)
                ref = os.path.join(refactored_dir, rel_path)
                if not os.path.exists(ref):
                    continue

                test_path = None
                if test_dir:
                    cand = os.path.join(test_dir, rel_path)
                    if os.path.exists(cand):
                        test_path = cand
                    else:
                        test_name = f"test_{os.path.basename(rel_path)}"
                        cand2 = os.path.join(test_dir, test_name)
                        if os.path.exists(cand2):
                            test_path = cand2

                summary[rel_path] = self.analyze_module(orig, ref, test_file_path=test_path)

        return summary


def print_human_readable(
    summary: Dict[str, Dict[str, Any]],
    guard: RefactorGuard,
    args: Optional[argparse.Namespace] = None,
) -> None:
    """Print a human-readable summary of the analysis results."""
    max_complexity = guard.config.get("max_complexity", 10)

    for filename, data in summary.items():
        print(f"\n📄 {filename}")

        if data.get("method_diff"):
            for cls, diff in data["method_diff"].items():
                if diff["missing"] or diff["added"]:
                    print(f"  📦 {cls}:")
                    if diff["missing"]:
                        print(f"    ❌ Missing: {', '.join(diff['missing'])}")
                    if diff["added"]:
                        print(f"    ✅ Added: {', '.join(diff['added'])}")

        if not args or not args.missing_tests:
            if data.get("complexity"):
                high_complexity = [
                    (name, info["complexity"])
                    for name, info in data["complexity"].items()
                    if info["complexity"] > max_complexity
                ]

                if high_complexity and (not args or args.complexity_warnings):
                    print("  🔍 High complexity methods:")
                    for name, score in high_complexity:
                        print(f"    ⚠️  {name}: {score}")

        if not args or not args.complexity_warnings:
            if data.get("missing_tests"):
                print("  🧪 Missing Tests:")
                for test in data["missing_tests"]:
                    print(f"    ❓ {test['class']}.{test['method']}")
