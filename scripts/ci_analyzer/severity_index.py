"""
This module provides functionality to compute severity scores for code quality analysis.

It includes functions to compute individual severity scores for files and to create a severity index DataFrame from report data.
"""

import numpy as np
import pandas as pd


def compute_severity(file_path: str, content: dict) -> dict:
    """
    Calculates a severity score for a file using its coverage and linting report data.
    
    The severity score is a weighted sum of MyPy errors, Pydocstyle lint issues, average function complexity, and coverage deficit. Returns a dictionary summarizing these metrics and the computed severity score.
    """
    coverage_data = content.get("coverage", {}).get(
        "complexity", {}
    )  # Get coverage complexity data
    linting = content.get("linting", {}).get("quality", {})  # Get linting quality data
    mypy_errors = linting.get("mypy", {}).get("errors", [])  # Get MyPy errors
    pydocstyle_issues = linting.get("pydocstyle", {}).get("functions", {})  # Get Pydocstyle issues

    num_lint_issues = sum(
        len(v) for v in pydocstyle_issues.values()
    )  # Count total Pydocstyle issues
    num_mypy_errors = len(mypy_errors)  # Count total MyPy errors

    complexities = [
        fn.get("complexity", 0) for fn in coverage_data.values()
    ]  # Get complexities of functions
    coverages = [
        fn.get("coverage", 1.0) for fn in coverage_data.values()
    ]  # Get coverage percentages of functions

    avg_complexity = np.mean(complexities) if complexities else 0  # Calculate average complexity
    avg_coverage = np.mean(coverages) if coverages else 1.0  # Calculate average coverage

    # Calculate the severity score based on weighted metrics
    severity_score = (
        2.0 * num_mypy_errors
        + 1.5 * num_lint_issues
        + 1.0 * avg_complexity
        + 2.0 * (1.0 - avg_coverage)
    )

    return {
        "File": file_path,
        "Mypy Errors": num_mypy_errors,
        "Lint Issues": num_lint_issues,
        "Avg Complexity": round(avg_complexity, 2),
        "Avg Coverage %": round(avg_coverage * 100, 1),
        "Severity Score": round(severity_score, 2),
    }


def compute_severity_index(report_data: dict) -> pd.DataFrame:
    """
    Aggregates severity scores for multiple files into a sorted DataFrame.
    
    Processes report data for each file, computes severity metrics, and returns a DataFrame sorted by severity score in descending order. If no data is provided, returns an empty DataFrame with predefined columns.
    
    Args:
        report_data: Mapping of file paths to their coverage and linting report data.
    
    Returns:
        A pandas DataFrame containing severity metrics for each file, sorted by severity score.
    """
    rows = [compute_severity(fp, content) for fp, content in report_data.items()]

    # Create DataFrame with appropriate columns if empty
    if not rows:
        return pd.DataFrame(
            columns=[
                "File",
                "Mypy Errors",
                "Lint Issues",
                "Avg Complexity",
                "Avg Coverage %",
                "Severity Score",
            ]
        )

    df = pd.DataFrame(rows)
    return df.sort_values(by="Severity Score", ascending=False).reset_index(drop=True)
