"""
Module: scripts/dashboard/metrics.py
Extracts all data-transformation and metrics logic from the Streamlit app.
"""
import os
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Tuple
from collections import defaultdict

from dashboard.data_loader import weighted_coverage, is_excluded


def compute_executive_summary(
    merged_data: Dict[str, Any],
    strictness_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generates high-level summary metrics for the dashboard's Executive Summary.
    
    Aggregates unique test counts, average strictness and severity scores, number of production files, overall coverage percentage, and percentage of missing documentation from the provided data sources.
    
    Args:
        merged_data: Dictionary containing merged module data, including docstring information.
        strictness_data: Dictionary containing strictness and coverage metrics for modules.
    
    Returns:
        A dictionary with total unique tests, average strictness, average severity, production file count, overall coverage percentage, and percentage of missing documentation.
    """
    unique_tests = set()
    strictness_vals, severity_vals, coverage_vals = [], [], []

    modules = strictness_data.get("modules", strictness_data)
    for file_path, mod in modules.items():
        if is_excluded(file_path):
            continue
        coverage_vals.append(mod.get("module_coverage", 0.0))
        for test in mod.get("tests", []):
            name = test.get("test_name")
            if name:
                unique_tests.add(name)
            strictness_vals.append(test.get("strictness", 0.0))
            severity_vals.append(test.get("severity", 0.0))

    total_tests = len(unique_tests)
    avg_strictness = float(np.mean(strictness_vals)) if strictness_vals else 0.0
    avg_severity = float(np.mean(severity_vals)) if severity_vals else 0.0
    prod_files = len(modules)
    overall_coverage = float(np.mean(coverage_vals) * 100) if coverage_vals else 0.0

    # Docstring coverage stats
    doc_total = doc_missing = 0
    for rep in merged_data.values():
        doc = rep.get("docstrings", {})
        if doc.get("module_doc", {}).get("description") is None:
            doc_missing += 1
        classes = doc.get("classes", [])
        funcs = doc.get("functions", [])
        doc_total += 1 + len(classes) + len(funcs)
        doc_missing += sum(1 for cls in classes if not cls.get("description"))
        doc_missing += sum(1 for fn in funcs if not fn.get("description"))

    missing_doc_percent = round((doc_missing / doc_total) * 100, 2) if doc_total else 0.0

    return {
        "total_tests": total_tests,
        "avg_strictness": round(avg_strictness, 2),
        "avg_severity": round(avg_severity, 2),
        "prod_files": prod_files,
        "overall_coverage": round(overall_coverage, 2),
        "missing_doc_percent": missing_doc_percent,
    }


def get_low_coverage_modules(
    strictness_data: Dict[str, Any],
    top_n: int = 5
) -> List[Tuple[str, float]]:
    """
    Returns the modules with the lowest coverage percentages.
    
    Iterates over modules in the strictness data, excluding filtered files, and collects their coverage values. Returns a list of (module name, coverage) tuples for the modules with the lowest coverage, sorted in ascending order.
    
    Args:
        strictness_data: Dictionary containing module coverage information.
        top_n: Number of modules to return.
    
    Returns:
        A list of tuples, each containing a module name and its coverage percentage.
    """
    pairs: List[Tuple[str, float]] = []
    raw_modules = strictness_data.get("modules", strictness_data)
    for mod, data in raw_modules.items():
        if is_excluded(mod):
            continue
        pairs.append((mod, data.get("module_coverage", 0.0)))
    pairs.sort(key=lambda x: x[1])
    return pairs[:top_n]


def coverage_by_module(
    merged_data: Dict[str, Any],
    top_n: int = 10
) -> List[Tuple[str, float]]:
    """
    Calculates line-of-code weighted coverage for each module and returns the modules with the lowest coverage.
    
    Args:
        merged_data: Dictionary containing module data, including coverage and complexity information.
        top_n: Number of modules with the lowest coverage to return.
    
    Returns:
        A list of tuples containing the module name and its coverage percentage, sorted in ascending order by coverage.
    """
    covs: Dict[str, float] = {}
    for path, rep in merged_data.items():
        if is_excluded(path):
            continue
        comp = rep.get("coverage", {}).get("complexity", {})
        ratio = weighted_coverage(comp) if comp else 0.0
        if ratio > 0:
            covs[os.path.basename(path)] = round(ratio * 100, 2)

    sorted_cov = sorted(covs.items(), key=lambda x: x[1])
    return sorted_cov[:top_n]


def compute_severity(
    file_path: str,
    content: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculates a severity score for a file based on linting errors, code complexity, and coverage.
    
    The severity score combines the number of mypy errors, pydocstyle lint issues, average function complexity, and coverage ratio using weighted factors. Returns a dictionary summarizing the file's name, path, error counts, average complexity, average coverage percentage, and computed severity score.
    """
    linting = content.get("linting", {}).get("quality", {})
    mypy_errors = linting.get("mypy", {}).get("errors", [])
    pydoc = linting.get("pydocstyle", {}).get("functions", {})

    num_mypy = len(mypy_errors)
    num_pydoc = sum(len(v) for v in pydoc.values())

    comp = content.get("coverage", {}).get("complexity", {})
    complexities = [f.get("complexity", 0) for f in comp.values()]
    avg_comp = float(np.mean(complexities)) if complexities else 0.0

    avg_cov = weighted_coverage(comp) if comp else 1.0

    score = (
        2.0 * num_mypy +
        1.5 * num_pydoc +
        1.0 * avg_comp +
        2.0 * (1.0 - avg_cov)
    )

    return {
        "File": os.path.basename(file_path),
        "Full Path": file_path,
        "Mypy Errors": num_mypy,
        "Lint Issues": num_pydoc,
        "Avg Complexity": round(avg_comp, 2),
        "Avg Coverage %": round(avg_cov * 100, 1),
        "Severity Score": round(score, 2),
    }


def compute_severity_df(
    merged_data: Dict[str, Any],
    compute_severity_fn
) -> pd.DataFrame:
    """
    Builds a DataFrame summarizing severity metrics for all files.
    
    Applies the provided severity computation function to each file in the merged data and constructs a DataFrame from the results, sorted by severity score in descending order with the index reset.
    
    Args:
        merged_data: A dictionary mapping file paths to their associated data.
        compute_severity_fn: A function that computes severity metrics for a given file.
    
    Returns:
        A pandas DataFrame containing severity metrics for each file, sorted by severity score descending.
    """
    rows: List[Dict[str, Any]] = []
    for fp, content in merged_data.items():
        rows.append(compute_severity_fn(fp, content))
    df = pd.DataFrame(rows)
    return df.sort_values("Severity Score", ascending=False).reset_index(drop=True)


def build_prod_to_tests_df(strictness_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Creates a DataFrame mapping each production module to its unique covering tests and related metrics.
    
    Deduplicates tests by name within each module, retaining the highest severity and corresponding strictness for each test. Calculates the average strictness and severity across unique tests per module, and lists the names of all covering tests. The resulting DataFrame includes the production module name, test count, average strictness, average severity, and a comma-separated list of test names, sorted by test count in descending order.
    """
    rows: List[Dict[str, Any]] = []

    raw_modules = strictness_data.get("modules", strictness_data)
    for prod, info in raw_modules.items():
        tests = info.get("tests", [])
        if not tests:
            continue

        # Deduplicate tests per test_name within this module, keeping the highest severity/strictness seen.
        test_metrics = {}
        for t in tests:
            name = t.get("test_name", "")
            strictness = t.get("strictness", 0.0)
            severity = t.get("severity", 0.0)
            if name not in test_metrics or severity > test_metrics[name]["severity"]:
                test_metrics[name] = {"strictness": strictness, "severity": severity}

        unique_tests = list(test_metrics.keys())
        strictness_vals = [m["strictness"] for m in test_metrics.values()]
        severity_vals = [m["severity"] for m in test_metrics.values()]

        avg_str = np.mean(strictness_vals) if strictness_vals else 0.0
        avg_sev = np.mean(severity_vals) if severity_vals else 0.0

        rows.append({
            "Production Module": os.path.basename(prod),
            "Test Count": len(unique_tests),
            "Avg Strictness": round(avg_str, 2),
            "Avg Severity": round(avg_sev, 2),
            "Covering Tests": ", ".join(sorted(unique_tests))
        })

    df = pd.DataFrame(rows)
    return df.sort_values("Test Count", ascending=False).reset_index(drop=True)


def severity_distribution(strictness_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Categorizes tests into Low, Medium, and High severity buckets based on their highest observed severity.
    
    Deduplicates tests globally by test name, retaining only the highest severity for each test, and returns a count of tests in each severity category.
    """
    buckets = {"Low": 0, "Medium": 0, "High": 0}
    severity_thresholds = {"Low": 0.3, "Medium": 0.7}
    test_severities = defaultdict(float)  # Global deduplication

    # Deduplicate by test_name
    raw_modules = strictness_data.get("modules", strictness_data)
    for module in raw_modules.values():
        for t in module.get("tests", []):
            name = t.get("test_name", "unknown")
            sev = t.get("severity", 0.0)
            test_severities[name] = max(test_severities[name], sev)

    for sev in test_severities.values():
        if sev <= severity_thresholds["Low"]:
            buckets["Low"] += 1
        elif sev <= severity_thresholds["Medium"]:
            buckets["Medium"] += 1
        else:
            buckets["High"] += 1

    return buckets