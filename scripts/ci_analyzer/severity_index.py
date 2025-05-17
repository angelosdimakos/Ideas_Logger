"""
This module provides functionality to compute severity scores for code quality analysis.

It includes functions to compute individual severity scores for files and to create a severity index DataFrame from report data.
"""

import numpy as np
import pandas as pd


def compute_severity(file_path: str, content: dict) -> dict:
    """
    Compute the severity score for a given file based on its coverage and linting data.

    Args:
        file_path (str): The path of the file being analyzed.
        content (dict): The report data for the file, including coverage and linting information.

    Returns:
        dict: A dictionary containing the severity metrics for the file.
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
    Compute a severity index for all files in the report data.

    Args:
        report_data (dict): Dictionary containing report data for each file.

    Returns:
        pd.DataFrame: A DataFrame sorted by severity score.
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
