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
    Computes high-level summary metrics for the dashboard's Executive Summary.
    
    Aggregates unique test count, average strictness and severity, number of production files, overall coverage percentage, and percentage of missing documentation from the provided data.
    
    Args:
        merged_data: Data containing documentation and code structure information.
        strictness_data: Data containing coverage, strictness, and severity metrics.
    
    Returns:
        A dictionary with total unique tests, average strictness, average severity, production file count, overall coverage percentage, and missing documentation percentage.
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
    Identifies modules with the lowest coverage based on strictness data.
    
    Args:
        strictness_data: Dictionary containing module coverage information.
        top_n: Number of modules with the lowest coverage to return.
    
    Returns:
        A list of tuples, each containing a module name and its coverage value, sorted in ascending order by coverage.
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
    Calculates LOC-weighted coverage percentages for each module and returns the modules with the lowest coverage.
    
    Args:
        merged_data: Dictionary containing module data with coverage and complexity information.
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
    Calculates severity metrics for a file by combining linting errors, code complexity, and coverage.
    
    The severity score is computed as a weighted sum of mypy errors, pydocstyle lint issues, average code complexity, and coverage deficit. Returns a dictionary with file name, path, error counts, average complexity, average coverage percentage, and severity score.
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
    Builds a pandas DataFrame containing severity metrics for each file.
    
    Applies the provided severity computation function to every file in the merged data, sorts the resulting DataFrame by severity score in descending order, and resets the index.
    
    Args:
        merged_data: Dictionary mapping file paths to their associated data.
        compute_severity_fn: Function that computes severity metrics for a given file.
    
    Returns:
        A pandas DataFrame with severity metrics for all files, sorted by severity score.
    """
    rows: List[Dict[str, Any]] = []
    for fp, content in merged_data.items():
        rows.append(compute_severity_fn(fp, content))
    df = pd.DataFrame(rows)
    return df.sort_values("Severity Score", ascending=False).reset_index(drop=True)


def build_prod_to_tests_df(strictness_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Builds a DataFrame mapping production modules to their unique covering tests and related metrics.
    
    For each production module, deduplicates tests by name (keeping the highest severity per test), then computes the test count, average strictness, average severity, and a comma-separated list of unique test names. Returns a DataFrame sorted by test count in descending order.
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
    Buckets unique tests into Low, Medium, and High severity categories based on their highest observed severity.
    
    Deduplicates tests globally by test name, assigning each to a severity bucket: Low (≤0.3), Medium (≤0.7), or High (>0.7). Returns a dictionary with the count of tests in each bucket.
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