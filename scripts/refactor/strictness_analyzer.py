#!/usr/bin/env python3
"""
Test Coverage Mapper
====================
This tool maps tests to production code based on merged coverage data and directory structure,
while also calculating test quality metrics and severity scores.

Author: Angelos Dimakos
Version: 1.1.1 (Patched with safety and consistency checks)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

from scripts.refactor.parsers.json_coverage_parser import parse_json_coverage

def scan_test_directory(tests_path: Path) -> List[Dict[str, Any]]:
    print("\U0001F50D Scanning test files and extracting functions...")
    test_results = []
    test_files = [tests_path] if tests_path.is_file() else list(tests_path.rglob("test_*.py"))

    for test_file in test_files:
        with open(test_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        funcs = extract_test_functions(test_file)
        for func in funcs:
            test_results.append(analyze_strictness(lines, func))
    return test_results

def extract_test_functions(filepath: Path) -> List[Dict[str, Any]]:
    import ast
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    return [
        {"name": node.name, "start": node.lineno, "end": getattr(node, "end_lineno", node.lineno), "path": str(filepath)}
        for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith("test")
    ]

def analyze_strictness(lines: List[str], func: Dict[str, Any]) -> Dict[str, Any]:
    segment = lines[func["start"] - 1: func["end"]]
    joined = "\n".join(segment)
    return {
        "name": func["name"],
        "file": func["path"],
        "start": func["start"],
        "end": func["end"],
        "asserts": sum(1 for line in segment if "assert" in line),
        "mocks": joined.count("mock") + joined.count("MagicMock"),
        "raises": joined.count("pytest.raises") + joined.count("self.assertRaises"),
        "branches": sum(1 for line in segment if any(kw in line for kw in ("if ", "for ", "while "))),
        "length": max(1, func["end"] - func["start"] + 1),
    }

def attach_coverage_from_merged_report(results: List[Dict[str, Any]], merged_data: Dict[str, Any]) -> None:
    coverage_data = merged_data.get("coverage", {})
    for result in results:
        test_file = Path(result["file"]).as_posix()
        prod_coverage = coverage_data.get(test_file, {})
        complexity_data = prod_coverage.get("complexity", {})

        covered_methods = []
        total_hits = 0
        total_lines = 0

        for cls, methods in complexity_data.items():
            coverage = methods.get("coverage", 0.0)
            hits = methods.get("hits", 0)
            lines = methods.get("lines", 0)

            covered_methods.append({
                "name": cls,
                "hits": hits,
                "lines": lines,
                "coverage": coverage,
                "covered_lines": methods.get("covered_lines", []),
                "missing_lines": methods.get("missing_lines", [])
            })
            total_hits += hits
            total_lines += lines

        result["covers_prod_methods"] = covered_methods
        result["coverage_hits"] = total_hits
        result["coverage_hit_ratio"] = round(total_hits / total_lines, 3) if total_lines else 0.0

        # Ensure consistent schema
        if "covers_prod_files" not in result:
            result["covers_prod_files"] = []

def compute_strictness_score(results: List[Dict[str, Any]]) -> None:
    for result in results:
        assert_count = result.get("asserts", 0)
        coverage_ratio = result.get("coverage_hit_ratio", 0.0)
        complexities = [m.get("complexity", 1) for m in result.get("covers_prod_methods", [])]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 1

        assertion_factor = min(1.0, assert_count / 5)
        complexity_factor = min(1.5, 1 + (avg_complexity / 15))
        strictness_score = round(assertion_factor * coverage_ratio * complexity_factor, 3)

        result["strictness_score"] = strictness_score
        result["strictness_grade"] = (
            "A" if strictness_score >= 1.0 else
            "B" if strictness_score >= 0.7 else
            "C" if strictness_score >= 0.4 else "D"
        )

def main(tests_dir: str, merged_report_path: str, output_path: Optional[str] = None) -> None:
    tests_path = Path(tests_dir)
    merged_report = Path(merged_report_path)

    if not tests_path.exists() or not merged_report.exists():
        print("❌ One or more input paths do not exist.")
        sys.exit(1)

    test_results = scan_test_directory(tests_path)
    print(f"Found {len(test_results)} test functions.")

    print("📖 Loading merged report...")
    merged_data = json.loads(merged_report.read_text(encoding="utf-8"))

    print("🔗 Attaching precomputed coverage data...")
    attach_coverage_from_merged_report(test_results, merged_data)

    print("📊 Computing strictness scores...")
    compute_strictness_score(test_results)

    report = {
        "summary": {
            "total_tests": len(test_results),
            "avg_strictness": round(
                sum(r.get("strictness_score", 0) for r in test_results) / max(len(test_results), 1), 2
            ),
            "total_prod_files_covered": len(
                set(file for r in test_results for file in r.get("covers_prod_files", []))
            ),
        },
        "test_to_prod_mapping": test_results
    }

    if output_path:
        out_path = Path(output_path)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"✅ Report written to {out_path}")
    else:
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map tests to production code using merged coverage data.")
    parser.add_argument("--tests", type=str, required=True, help="Path to test suite directory.")
    parser.add_argument("--merged_report", type=str, required=True, help="Path to merged JSON coverage report.")
    parser.add_argument("--output", type=str, help="Output report JSON path.")
    args = parser.parse_args()

    main(args.tests, args.merged_report, args.output)
