#!/usr/bin/env python3
"""
Test Coverage Mapper (Final Version with Audit Integration)
Author: Angelos Dimakos
Version: 2.2.0

This tool maps tests to production code based on the refactor audit JSON file,
calculates strictness and severity metrics, and produces a detailed report.
Now with improved Pydantic model usage for coverage and line data.

Usage:
    python test_coverage_mapper.py --source src/ --tests tests/ --audit refactor_audit.json --output mapping.json
"""

import argparse
import json
import sys
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from functools import lru_cache
from pydantic import BaseModel, Field

from scripts.refactor.method_line_ranges import extract_method_line_ranges
from scripts.refactor.complexity.complexity_analyzer import calculate_function_complexity_map


class ComplexityMetrics(BaseModel):
    complexity: int
    coverage: float
    hits: int
    lines: int
    covered_lines: List[int]
    missing_lines: List[int]


class FileAudit(BaseModel):
    complexity: Dict[str, ComplexityMetrics] = Field(default_factory=dict)


class AuditReport(BaseModel):
    __root__: Dict[str, FileAudit]

    def get_file_metrics(self, filepath: str) -> Dict[str, ComplexityMetrics]:
        """Get the metrics for a specific file from the audit report"""
        audit = self.__root__.get(filepath, FileAudit())
        return audit.complexity

    def get_coverage_for_lines(self, filepath: str, start_line: int, end_line: int) -> Dict[str, Any]:
        """Get coverage metrics for a specific line range in a file"""
        metrics = self.get_file_metrics(filepath)

        if not metrics:
            return {
                "covered_lines": [],
                "missing_lines": list(range(start_line, end_line + 1)),
                "hits": 0,
                "total_lines": end_line - start_line + 1,
                "coverage_ratio": 0.0
            }

        # Combine all covered lines from all functions in the file
        all_covered_lines = []
        for metric in metrics.values():
            all_covered_lines.extend(metric.covered_lines)

        # Find which lines in the range are covered
        covered_in_range = [line for line in all_covered_lines if start_line <= line <= end_line]
        missing_in_range = [line for line in range(start_line, end_line + 1) if line not in covered_in_range]

        return {
            "covered_lines": covered_in_range,
            "missing_lines": missing_in_range,
            "hits": len(covered_in_range),
            "total_lines": end_line - start_line + 1,
            "coverage_ratio": len(covered_in_range) / (end_line - start_line + 1) if end_line >= start_line else 0.0
        }


@lru_cache(maxsize=1)
def load_audit_report(audit_path: str) -> AuditReport:
    """Load the audit report from a JSON file and parse it into the Pydantic model"""
    with open(audit_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return AuditReport.parse_obj(data)


def extract_test_functions(filepath: Path) -> List[Dict[str, Any]]:
    """Extract test functions and methods from a Python file"""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    functions = []

    # Extract class methods and standalone test functions
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for method in node.body:
                if isinstance(method, ast.FunctionDef):
                    start = method.lineno
                    end = getattr(method, "end_lineno", start)
                    functions.append({
                        "name": f"{node.name}.{method.name}",
                        "start": start,
                        "end": end,
                        "path": str(filepath)
                    })
        elif isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            functions.append({"name": node.name, "start": start, "end": end, "path": str(filepath)})

    return functions


def analyze_strictness(lines: List[str], func: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the strictness of a test function based on its content"""
    segment = lines[func["start"] - 1: func["end"]]
    joined = "\n".join(segment)

    asserts = sum(1 for line in segment if "assert" in line)
    mocks = joined.count("mock") + joined.count("MagicMock")
    raises = joined.count("pytest.raises") + joined.count("self.assertRaises")

    # Count control flow branches
    branches = 0
    for line in segment:
        line = line.strip()
        if (line.startswith("if ") or " if " in line or
                line.startswith("for ") or " for " in line or
                line.startswith("while ") or " while " in line):
            branches += 1

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


def compute_strictness_score(asserts, raises, mocks, branches, length, hit_ratio) -> float:
    """Compute the strictness score based on various metrics"""
    structural_score = (asserts * 1.5 + raises + 0.3 * mocks + 0.5 * branches) / max(1, length)
    combined = 0.7 * structural_score + 0.3 * hit_ratio
    return round(combined, 2)


def attach_audit_hits(results: List[Dict[str, Any]], audit_model: AuditReport) -> None:
    """Attach coverage hits to test results using the audit model's direct coverage values"""
    for result in results:
        normalized_path = str(Path(result["file"]).resolve().as_posix())
        start_line = result["start"]
        end_line = result["end"]

        # Determine which audit entry applies
        file_path = None
        for fp in audit_model.__root__:
            if normalized_path == fp or Path(fp).name == Path(normalized_path).name:
                file_path = fp
                break

        # Attempt to read direct metrics
        coverage = 0.0
        hits = 0
        covered_lines = []
        missing_lines = list(range(start_line, end_line + 1))

        if file_path:
            metrics_map = audit_model.get_file_metrics(file_path)
            # use test name as key if present, else fallback to line-range compute
            metric = metrics_map.get(result["name"])
            if metric:
                # Use JSON's own coverage ratio and line lists
                coverage = metric.coverage
                hits = metric.hits
                covered_lines = metric.covered_lines
                missing_lines = metric.missing_lines
            else:
                # Fallback: compute from covered_lines arrays
                data = audit_model.get_coverage_for_lines(file_path, start_line, end_line)
                hits = data["hits"]
                covered_lines = data["covered_lines"]
                missing_lines = data["missing_lines"]
                coverage = data.get("coverage_ratio", 0.0)

        # Update result with direct coverage
        result.update({
            "coverage_hits": hits,
            "covered_lines": covered_lines,
            "missing_lines": missing_lines,
            "hit_ratio": round(coverage, 2),
            "strictness_score": compute_strictness_score(
                result["asserts"], result["raises"], result["mocks"], result["branches"], result["length"], coverage
            )
        })


def map_tests_to_prod_code(
    test_results: List[Dict[str, Any]], source_root: Path, audit_model: AuditReport
) -> None:
    """Map test functions to production code, using JSON coverage metrics for each method"""
    for result in test_results:
        covered_files: Set[str] = set()
        normalized_path = str(Path(result["file"]).resolve().as_posix())

        # ... (path selection logic unchanged)

        result["covers_prod_files"] = list(covered_files)
        covered_methods = []

        for prod_file in covered_files:
            try:
                methods = extract_method_line_ranges(prod_file)
                complexity_map = calculate_function_complexity_map(prod_file)
                metrics_map = audit_model.get_file_metrics(prod_file)

                for method_name, line_range in methods.items():
                    # Directly read JSON coverage if available
                    metric = metrics_map.get(method_name)
                    if metric:
                        cov_ratio = metric.coverage
                        cov_lines = metric.covered_lines
                        miss_lines = metric.missing_lines
                        hits = metric.hits
                    else:
                        # Fallback: compute via range
                        data = audit_model.get_coverage_for_lines(prod_file, line_range[0], line_range[1])
                        cov_ratio = data.get("coverage_ratio", 0.0)
                        cov_lines = data["covered_lines"]
                        miss_lines = data["missing_lines"]
                        hits = data["hits"]

                    covered_methods.append({
                        "name": method_name,
                        "file": prod_file,
                        "line_range": line_range,
                        "complexity": complexity_map.get(method_name, 1),
                        "coverage": round(cov_ratio, 2),
                        "covered_lines": cov_lines,
                        "missing_lines": miss_lines
                    })
            except Exception as e:
                print(f"Error processing production file {prod_file}: {e}")

        result["covers_prod_methods"] = covered_methods

        # Compute severity using direct coverage
        if covered_methods:
            avg_complexity = sum(m["complexity"] for m in covered_methods) / len(covered_methods)
            strictness = result.get("strictness_score", 0.5)
            complexity_factor = min(2.0, 1.0 + (avg_complexity / 10.0))
            result["severity_score"] = round(strictness * complexity_factor, 2)
        else:
            result["severity_score"] = result.get("strictness_score", 0.5)


def scan_test_directory(tests_path: Path) -> List[Dict[str, Any]]:
    """Scan a directory for test files and extract test functions"""
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


def main(tests_dir: str, source_dir: str, audit_path: str, output_path: Optional[str] = None) -> None:
    """Main function to run the test coverage mapping"""
    tests_path = Path(tests_dir)
    source_path = Path(source_dir)
    audit_json = Path(audit_path)

    if not tests_path.exists() or not source_path.exists() or not audit_json.exists():
        print("❌ Invalid path(s). Ensure tests, source, and audit files exist.")
        sys.exit(1)

    test_results = scan_test_directory(tests_path)
    print(f"📚 Found {len(test_results)} test functions.")

    print("📈 Loading audit report via Pydantic...")
    audit_model = load_audit_report(str(audit_json))

    print("🔗 Attaching audit hits and calculating strictness...")
    attach_audit_hits(test_results, audit_model)

    print("🗺️ Mapping tests to production code...")
    map_tests_to_prod_code(test_results, source_path, audit_model)

    # Calculate covered files and methods for the summary
    covered_files = set(f for r in test_results for f in r.get("covers_prod_files", []))
    covered_methods = sum(len(r.get("covers_prod_methods", [])) for r in test_results)

    report = {
        "summary": {
            "total_tests": len(test_results),
            "avg_strictness": round(
                sum(r.get("strictness_score", 0) for r in test_results) / len(test_results), 2
            ) if test_results else 0,
            "avg_severity": round(
                sum(r.get("severity_score", 0) for r in test_results) / len(test_results), 2
            ) if test_results else 0,
            "total_prod_files_covered": len(covered_files),
            "total_prod_methods_covered": covered_methods,
        },
        "test_analysis": test_results
    }

    if output_path:
        out_path = Path(output_path)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"✅ Report written to: {out_path}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map tests to production code with quality metrics.")
    parser.add_argument("--tests", required=True, help="Path to test suite directory.")
    parser.add_argument("--source", required=True, help="Path to source code directory.")
    parser.add_argument("--audit", required=True, help="Path to refactor audit JSON file.")
    parser.add_argument("--output", help="Where to save the mapping report (JSON).")
    args = parser.parse_args()

    main(args.tests, args.source, args.audit, args.output)