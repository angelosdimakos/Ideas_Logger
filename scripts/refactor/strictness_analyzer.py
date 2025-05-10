#!/usr/bin/env python3
"""
Test Coverage Mapper
===================

This tool maps tests to production code based on coverage data and directory structure,
while also calculating test quality metrics and severity scores.

Usage:
    python test_coverage_mapper.py --source src/ --tests tests/ --coverage coverage.json --output mapping.json

Features:
- Maps test functions to the production code they cover
- Calculates test strictness and quality metrics
- Integrates complexity analysis for production code
- Produces a comprehensive report on test-to-code relationships

Author: Angelos Dimakos
Version: 1.1.0
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

# Import your existing modules
from scripts.refactor.parsers.json_coverage_parser import parse_json_coverage
from scripts.refactor.ast_extractor import extract_class_methods
from scripts.refactor.method_line_ranges import extract_method_line_ranges
from scripts.refactor.complexity.complexity_analyzer import calculate_function_complexity_map


def scan_test_directory(tests_path: Path) -> List[Dict[str, Any]]:
    print("🔍 Scanning test files and extracting functions...")
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
    """
    Extract test function names and line ranges from a Python test file.

    Args:
        filepath (Path): The path to the Python test file.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing test function names and their line ranges.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    import ast
    tree = ast.parse(source)
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            functions.append({"name": node.name, "start": start, "end": end, "path": str(filepath)})
    return functions


def analyze_strictness(lines: List[str], func: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze basic strictness heuristics on a test function.

    Args:
        lines (List[str]): The lines of the test function.
        func (Dict[str, Any]): A dictionary containing the test function's metadata.

    Returns:
        Dict[str, Any]: A dictionary containing the analysis results.
    """
    segment = lines[func["start"] - 1: func["end"]]
    joined = "\n".join(segment)

    asserts = sum(1 for line in segment if "assert" in line)
    mocks = joined.count("mock") + joined.count("MagicMock")
    raises = joined.count("pytest.raises") + joined.count("self.assertRaises")
    branches = sum(1 for line in segment if any(kw in line for kw in ("if ", "for ", "while ")))

    length = max(1, func["end"] - func["start"] + 1)

    return {
        "name": func["name"],
        "file": func["path"],
        "start": func["start"],
        "end": func["end"],
        "asserts": asserts,
        "mocks": mocks,
        "raises": raises,
        "branches": branches,
        "length": length,
    }


def attach_coverage_hits(results: List[Dict[str, Any]], coverage_data: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Attaches coverage and hit data to each test result and associated production methods.
    Now correctly handles normalized paths and avoids overmatching.
    """
    normalized_coverage_data = {Path(k).as_posix(): v for k, v in coverage_data.items()}

    for result in results:
        raw_file_path = result.get("file", "")
        requested_path = str(Path(raw_file_path).as_posix())

        # Try exact path match first
        coverage_info = normalized_coverage_data.get(requested_path)

        # Fallback to best suffix match
        if not coverage_info:
            requested_parts = Path(requested_path).parts
            best_match = None
            best_len = 0

            for key in normalized_coverage_data:
                parts = Path(key).parts
                match_len = sum(1 for a, b in zip(reversed(parts), reversed(requested_parts)) if a == b)
                if match_len > best_len:
                    best_match = key
                    best_len = match_len

            if best_match:
                coverage_info = normalized_coverage_data[best_match]
                result["matched_coverage_path"] = best_match
            else:
                result["coverage_hit_ratio"] = 0.0
                result["coverage_hits"] = 0
                result["covers_prod_methods"] = []
                continue

        total_hits = 0
        total_lines = 0
        covered_methods = []

        for method, cov_stats in coverage_info.items():
            hits = cov_stats.get("hits", 0)
            lines = cov_stats.get("lines", 0)
            coverage = cov_stats.get("coverage", 0.0)

            covered_methods.append({
                "name": method,
                "hits": hits,
                "lines": lines,
                "coverage": coverage,
                "covered_lines": cov_stats.get("covered_lines", []),
                "missing_lines": cov_stats.get("missing_lines", [])
            })

            total_hits += hits
            total_lines += lines

        result["covers_prod_methods"] = covered_methods
        result["coverage_hits"] = total_hits
        result["coverage_hit_ratio"] = round(total_hits / total_lines, 3) if total_lines else 0.0

    return results


def compute_strictness_score(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Computes a strictness score for each test case based on:
    - Assertion count (asserts)
    - Code coverage (coverage_hit_ratio)
    - Method complexity (from covered methods)
    Returns results with 'strictness_score' and 'strictness_grade'.
    """

    for result in results:
        assert_count = result.get("asserts", 0)
        coverage_ratio = result.get("coverage_hit_ratio", 0.0)
        covered_methods = result.get("covers_prod_methods", [])

        complexities = [m.get("complexity", 1) for m in covered_methods]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 1

        assertion_factor = min(1.0, assert_count / 5)  # Cap at 5 asserts contributing fully
        coverage_factor = coverage_ratio  # Already between 0.0 and 1.0
        complexity_factor = min(1.5, 1 + (avg_complexity / 15))  # Mild boost for complex methods

        strictness_score = round(assertion_factor * coverage_factor * complexity_factor, 3)

        result["strictness_score"] = strictness_score

        # Assign grade
        if strictness_score >= 1.0:
            grade = "A"
        elif strictness_score >= 0.7:
            grade = "B"
        elif strictness_score >= 0.4:
            grade = "C"
        else:
            grade = "D"

        result["strictness_grade"] = grade

    return results



def map_test_to_prod_path(test_path: Path, test_root: Path, source_root: Path) -> Path:
    """
    Map a test file path to its corresponding production code path.

    Args:
        test_path (Path): The path to the test file.
        test_root (Path): The root directory of the test files.
        source_root (Path): The root directory of the production code.

    Returns:
        Path: The corresponding production code path.
    """
    try:
        # Get relative path from test root
        rel_path = test_path.relative_to(test_root)

        # Transform test filename to production filename
        # e.g., test_module.py -> module.py
        prod_filename = rel_path.name
        if prod_filename.startswith("test_"):
            prod_filename = prod_filename[5:]  # Remove 'test_' prefix

        # Construct production path
        prod_path = source_root / rel_path.parent / prod_filename

        # Check if the exact path exists
        if prod_path.exists():
            return prod_path

        # Try alternative naming conventions if exact path doesn't exist
        # For example, tests/dir/test_module.py might map to src/dir/module.py
        # or tests/test_dir/test_module.py might map to src/dir/module.py
        if not prod_path.exists() and "test_" in str(rel_path.parent):
            # Try removing "test_" from directory names
            modified_parent = Path(*[
                part[5:] if part.startswith("test_") else part
                for part in rel_path.parent.parts
            ])
            prod_path = source_root / modified_parent / prod_filename
            if prod_path.exists():
                return prod_path

        # Final fallback: look for any file with a matching base name
        base_name = prod_filename.split('.')[0]
        candidates = list(source_root.rglob(f"*{base_name}*"))
        if candidates:
            return candidates[0]

        return None
    except Exception as e:
        print(f"Error mapping test path {test_path}: {e}")
        return None


def map_tests_to_prod_code(
    test_results: List[Dict[str, Any]],
    test_root: Path,
    source_root: Path,
    coverage_data: Dict[str, Dict[str, Any]],
) -> None:
    """
    Maps test functions to the production code they cover, avoiding overmatching.
    Prioritizes coverage data over directory-based heuristics.
    """

    # Normalize coverage keys
    normalized_coverage = {Path(k).as_posix(): v for k, v in coverage_data.items()}

    for result in test_results:
        test_file_path = Path(result["file"]).as_posix()
        covered_prod_files: Set[str] = set()

        # 1. Try direct coverage match first
        coverage_info = normalized_coverage.get(test_file_path)

        if coverage_info:
            # Add files from coverage data only if methods were covered
            for method_name, method_data in coverage_info.items():
                if method_data.get("hits", 0) > 0:
                    covered_prod_files.add(test_file_path)
        else:
            # 2. Fallback to structural matching only if coverage failed
            rel_test_path = Path(result["file"]).relative_to(test_root)
            prod_candidate = source_root / rel_test_path.parent / rel_test_path.name.replace("test_", "")
            if prod_candidate.exists():
                covered_prod_files.add(prod_candidate.as_posix())

        # Assign discovered production files
        result["covers_prod_files"] = list(covered_prod_files)

        # Compute and attach production method complexity if any
        covered_methods = result.get("covers_prod_methods", [])
        if covered_methods:
            avg_complexity = sum(m.get("complexity", 1) for m in covered_methods) / len(covered_methods)
            result["prod_code_complexity"] = avg_complexity

            strictness = result.get("strictness_score", 0.5)
            complexity_factor = 1.0 + avg_complexity / 10.0
            result["severity_score"] = round(strictness * complexity_factor, 2)
        else:
            result["severity_score"] = result.get("strictness_score", 0.5)

def scan_test_directory(tests_path: Path) -> List[Dict[str, Any]]:
    """
    Scan test directory or single test file and extract test function information.

    Args:
        tests_path (Path): The path to the test directory or test file.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing test function information.
    """
    print("🔍 Scanning test files and extracting functions...")
    test_results: List[Dict[str, Any]] = []

    if tests_path.is_file() and tests_path.name.startswith("test_") and tests_path.suffix == ".py":
        test_files = [tests_path]
    else:
        test_files = list(tests_path.rglob("test_*.py"))

    for test_file in test_files:
        with open(test_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        funcs = extract_test_functions(test_file)
        for func in funcs:
            test_results.append(analyze_strictness(lines, func))

    return test_results



def main(tests_dir: str, source_dir: str, coverage_path: str, output_path: Optional[str] = None) -> None:
    tests_path = Path(tests_dir)
    source_path = Path(source_dir)
    coverage_json = Path(coverage_path)

    if not tests_path.exists() or not source_path.exists() or not coverage_json.exists():
        print("❌ One or more input paths do not exist.")
        sys.exit(1)

    test_results = scan_test_directory(tests_path)
    print(f"Found {len(test_results)} test functions.")

    print("📈 Parsing coverage for tests and production files...")
    coverage_data = {}
    for test_result in test_results:
        test_file = Path(test_result["file"])
        method_ranges = {test_result["name"]: (test_result["start"], test_result["end"])}
        cov_for_file = parse_json_coverage(str(coverage_json), method_ranges, str(test_file))
        coverage_data.update(cov_for_file)

    # Also parse coverage for production files directly
    for prod_file in source_path.rglob("*.py"):
        try:
            methods = extract_method_line_ranges(prod_file)
            cov_for_prod = parse_json_coverage(str(coverage_json), methods, str(prod_file))
            coverage_data.update(cov_for_prod)
        except Exception as e:
            print(f"⚠️ Failed to parse coverage for production file {prod_file}: {e}")

    print("🔗 Attaching coverage hits and calculating strictness scores...")
    attach_coverage_hits(test_results, coverage_data)
    test_results = compute_strictness_score(test_results)

    print("🗺️ Mapping tests to production code...")
    map_tests_to_prod_code(test_results, tests_path, source_path, coverage_data)

    report = {
        "summary": {
            "total_tests": len(test_results),
            "avg_strictness": round(sum(r.get("strictness_score", 0) for r in test_results) / max(len(test_results), 1), 2),
            "avg_severity": round(sum(r.get("severity_score", 0) for r in test_results) / max(len(test_results), 1), 2),
            "total_prod_files_covered": len(set(file for r in test_results for file in r.get("covers_prod_files", []))),
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
    parser = argparse.ArgumentParser(description="Map tests to production code with quality metrics.")
    parser.add_argument("--tests", type=str, required=True, help="Path to test suite directory.")
    parser.add_argument("--source", type=str, required=True, help="Path to source code directory.")
    parser.add_argument("--coverage", type=str, required=True, help="Path to JSON coverage report.")
    parser.add_argument("--output", type=str, help="Output report JSON path.")
    args = parser.parse_args()

    main(args.tests, args.source, args.coverage, args.output)