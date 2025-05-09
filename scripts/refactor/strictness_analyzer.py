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
Version: 1.0.0
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

# Import your existing modules
from scripts.refactor.parsers.json_coverage_parser import parse_json_coverage
from scripts.refactor.ast_extractor import extract_class_methods
from scripts.refactor.method_line_ranges import extract_method_line_ranges
from scripts.refactor.complexity.complexity_analyzer import calculate_function_complexity_map


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


def compute_strictness_score(
        asserts: int,
        raises: int,
        mocks: int,
        branches: int,
        length: int,
        hit_ratio: float,
) -> float:
    """
    Compute a weighted strictness score using heuristics and coverage hit ratio.

    Args:
        asserts (int): The number of assert statements.
        raises (int): The number of expected exceptions.
        mocks (int): The number of mock objects used.
        branches (int): The number of branches in the code.
        length (int): The length of the test function.
        hit_ratio (float): The coverage hit ratio.

    Returns:
        float: The computed strictness score.
    """
    structural_score = (asserts * 1.5 + raises + 0.3 * mocks + 0.5 * branches) / max(1, length)
    combined = 0.7 * structural_score + 0.3 * hit_ratio  # Weighted blend
    return round(combined, 2)


def attach_coverage_hits(results: List[Dict[str, Any]], coverage_data: Dict[str, Dict[str, Any]]) -> None:
    """
    Attach line hit counts and recompute score.

    Args:
        results (List[Dict[str, Any]]): The results of the test analysis.
        coverage_data (Dict[str, Dict[str, Any]]): The coverage data mapping.
    """
    for result in results:
        normalized_path = str(Path(result["file"]).resolve().as_posix())
        file_hits = coverage_data.get(normalized_path, {})
        # file_hits is a dict mapping function names to stats
        hits = sum(
            1
            for i in range(result["start"], result["end"] + 1)
            if any(
                i in meth_info.get("covered_lines", []) for meth_info in file_hits.values()
            )
        )
        length = result["length"]
        hit_ratio = hits / length if length else 0.0

        result["coverage_hits"] = hits
        result["hit_ratio"] = round(hit_ratio, 2)
        result["strictness_score"] = compute_strictness_score(
            result["asserts"],
            result["raises"],
            result["mocks"],
            result["branches"],
            length,
            hit_ratio,
        )


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
    Map test functions to production code they cover.

    Args:
        test_results (List[Dict[str, Any]]): The results of the test analysis.
        test_root (Path): The root directory of the test files.
        source_root (Path): The root directory of the production code.
        coverage_data (Dict[str, Dict[str, Any]]): The coverage data mapping.
    """
    # Build a cache of files mapped by coverage
    covered_files: Dict[str, Set[str]] = {}
    for path, methods in coverage_data.items():
        for method_name, method_info in methods.items():
            if not method_name.startswith("test_"):
                # This is likely a production method covered by tests
                for test_path in test_results:
                    test_file = Path(test_path["file"]).resolve().as_posix()
                    if test_file not in covered_files:
                        covered_files[test_file] = set()
                    covered_files[test_file].add(path)

    # Map each test to production code
    for result in test_results:
        test_path = Path(result["file"])

        # Get production paths from coverage data first
        test_file_path = test_path.resolve().as_posix()
        covered_prod_paths = covered_files.get(test_file_path, set())

        # If coverage data doesn't help, try directory structure mapping
        if not covered_prod_paths:
            prod_path = map_test_to_prod_path(test_path, test_root, source_root)
            if prod_path:
                covered_prod_paths = {prod_path.resolve().as_posix()}

        # Add production code info to test result
        result["covers_prod_files"] = list(covered_prod_paths)

        # Extract methods from each production file
        covered_methods = []
        method_complexity = {}
        for prod_file in covered_prod_paths:
            if not Path(prod_file).is_file():
                continue  # Skip directories, we can't calculate complexity on them
            try:
                methods = extract_method_line_ranges(prod_file)
                complexity = calculate_function_complexity_map(prod_file)

                # Add methods and complexity to results
                for method_name, line_range in methods.items():
                    covered_methods.append({
                        "name": method_name,
                        "file": prod_file,
                        "line_range": line_range,
                        "complexity": complexity.get(method_name, 1)
                    })
                    method_complexity[method_name] = complexity.get(method_name, 1)
            except Exception as e:
                print(f"Error processing production file {prod_file}: {e}")

        result["covers_prod_methods"] = covered_methods

        # Adjust test severity based on production code complexity
        if covered_methods:
            avg_complexity = sum(m["complexity"] for m in covered_methods) / len(covered_methods)
            result["prod_code_complexity"] = avg_complexity

            # Adjust severity score
            strictness = result.get("strictness_score", 0.5)
            complexity_factor = min(2.0, 1.0 + (avg_complexity / 10.0))
            result["severity_score"] = round(strictness * complexity_factor, 2)
        else:
            result["severity_score"] = result.get("strictness_score", 0.5)


def scan_test_directory(tests_path: Path) -> List[Dict[str, Any]]:
    """
    Scan test directory and extract test function information.

    Args:
        tests_path (Path): The path to the test directory.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing test function information.
    """
    print("🔍 Scanning test files and extracting functions...")
    test_results: List[Dict[str, Any]] = []
    for test_file in tests_path.rglob("test_*.py"):
        with open(test_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        funcs = extract_test_functions(test_file)
        for func in funcs:
            test_results.append(analyze_strictness(lines, func))
    return test_results


def main(
        tests_dir: str,
        source_dir: str,
        coverage_path: str,
        output_path: Optional[str] = None,
) -> None:
    """
    Main entry point for the script.

    Args:
        tests_dir (str): The directory containing test files.
        source_dir (str): The directory containing production code.
        coverage_path (str): The path to the coverage data file.
        output_path (Optional[str]): The path to the output file (if any).
    """
    tests_path = Path(tests_dir)
    source_path = Path(source_dir)
    coverage_json = Path(coverage_path)

    if not tests_path.exists():
        print(f"❌ Tests path does not exist: {tests_path}")
        sys.exit(1)
    if not source_path.exists():
        print(f"❌ Source path does not exist: {source_path}")
        sys.exit(1)
    if not coverage_json.exists():
        print(f"❌ Coverage file not found: {coverage_json}")
        sys.exit(1)

    # Scan tests and build results
    test_results = scan_test_directory(tests_path)
    print(f"Found {len(test_results)} test functions in {tests_path}")

    # Parse coverage per-file and per-function
    print("📈 Parsing coverage...")
    coverage_data: Dict[str, Dict[str, Dict]] = {}
    for test_result in test_results:
        test_file = Path(test_result["file"])
        method_ranges = {test_result["name"]: (test_result["start"], test_result["end"])}
        cov_for_file = parse_json_coverage(str(coverage_json), method_ranges, str(test_file))
        coverage_data.update(cov_for_file)

    # Attach coverage hits and compute strictness
    print("🔗 Attaching coverage hits and calculating strictness scores...")
    attach_coverage_hits(test_results, coverage_data)

    # Map tests to production code
    print("🗺️ Mapping tests to production code...")
    map_tests_to_prod_code(test_results, tests_path, source_path, coverage_data)

    # Generate report
    report = {
        "summary": {
            "total_tests": len(test_results),
            "avg_strictness": round(sum(r.get("strictness_score", 0) for r in test_results) / len(test_results),
                                    2) if test_results else 0,
            "avg_severity": round(sum(r.get("severity_score", 0) for r in test_results) / len(test_results),
                                  2) if test_results else 0,
            "total_prod_files_covered": len(set(file for r in test_results for file in r.get("covers_prod_files", []))),
        },
        "test_to_prod_mapping": test_results
    }

    # Output results
    if output_path:
        out_path = Path(output_path)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"✅ Test-to-production code mapping written to: {out_path}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map tests to production code with quality metrics.")
    parser.add_argument("--tests", type=str, required=True, help="Path to test suite directory.")
    parser.add_argument("--source", type=str, required=True, help="Path to source code directory.")
    parser.add_argument("--coverage", type=str, required=True, help="Path to JSON coverage report.")
    parser.add_argument("--output", type=str, help="Where to save the mapping report (JSON).")
    args = parser.parse_args()
    main(args.tests, args.source, args.coverage, args.output)