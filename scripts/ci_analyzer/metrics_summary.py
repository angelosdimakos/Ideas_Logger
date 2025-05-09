"""
This module provides functionality to generate summary metrics from code quality reports.

It includes functions to analyze report data and summarize key metrics related to methods, tests, complexity, docstrings, and linter issues.
"""


def generate_metrics_summary(report_data: dict) -> str:
    """
    Generate a summary of metrics from the provided report data.

    Args:
        report_data (dict): Dictionary containing report data for each file.

    Returns:
        str: A Markdown formatted string summarizing the metrics.
    """
    total_methods = 0
    missing_tests = 0
    high_complexity = 0
    missing_docstrings = 0
    linter_issues = 0

    for content in report_data.values():
        for m in content.get("coverage", {}).get("complexity", {}).values():
            total_methods += 1  # Count each method audited
            if m.get("coverage", 1.0) == 0:
                missing_tests += 1  # Increment count for methods with no tests
            if m.get("complexity", 0) >= 10:
                high_complexity += 1  # Increment count for methods with high complexity

        for func in content.get("docstrings", {}).get("functions", []):
            if not func.get("description") or not func.get("args") or not func.get("returns"):
                missing_docstrings += 1  # Count methods missing docstring components

        lint = content.get("linting", {}).get("quality", {})
        linter_issues += len(lint.get("mypy", {}).get("errors", []))  # Count MyPy errors
        linter_issues += sum(len(v) for v in lint.get("pydocstyle", {}).get("functions", {}).values())  # Count Pydocstyle issues

    return f"""## 📊 Summary Metrics

- Total methods audited: **{total_methods}**
- 🚫 Methods missing tests: **{missing_tests}**
- 🔺 High-complexity methods (≥10): **{high_complexity}**
- 📚 Methods missing docstrings: **{missing_docstrings}**
- 🧼 Linter issues detected: **{linter_issues}**

"""  # Return a formatted summary of the metrics
