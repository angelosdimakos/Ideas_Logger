"""
This module provides functionality to generate detailed Markdown reports for top offenders in code quality analysis.

It includes functions to create drilldowns that summarize linting errors, complexity, coverage, and function descriptions for the top offenders.
"""


def generate_top_offender_drilldowns(severity_df, report_data: dict, top_n: int = 3) -> str:
    """
    Generate a Markdown section with drilldowns for the top N offenders.

    Args:
        severity_df: DataFrame containing severity information for files.
        report_data (dict): Dictionary containing report data for each file.
        top_n (int): Number of top offenders to include in the report.

    Returns:
        str: Markdown formatted string with detailed analysis of top offenders.
    """
    md = "\n## 🔎 Top Offenders: Detailed Analysis\n"
    top_files = severity_df.head(top_n)["File"].tolist()  # Get top N files based on severity

    for filepath in top_files:
        content = report_data.get(filepath, {})  # Retrieve report data for the file
        md += f"\n<details>\n<summary>🔍 `{filepath}`</summary>\n\n"

        # MyPy Errors
        mypy_errors = (
            content.get("linting", {}).get("quality", {}).get("mypy", {}).get("errors", [])
        )
        if mypy_errors:
            md += "\n**❗ MyPy Errors:**\n"
            for err in mypy_errors:
                md += f"- {err}\n"  # List each MyPy error

        # Pydocstyle Issues
        pydoc_issues = (
            content.get("linting", {}).get("quality", {}).get("pydocstyle", {}).get("functions", {})
        )
        if pydoc_issues:
            md += "\n**🧼 Pydocstyle Issues:**\n"
            for fn_name, issues in pydoc_issues.items():
                for issue in issues:
                    md += f"- `{fn_name}`: {issue['code']} — {issue['message']}\n"  # List each Pydocstyle issue

        # Complexity & Coverage
        complexity_data = content.get("coverage", {}).get("complexity", {})
        if complexity_data:
            md += "\n**📉 Complexity & Coverage Issues:**\n"
            for fn_name, meta in complexity_data.items():
                cx = meta.get("complexity", 0)  # Get complexity value
                cov = round(meta.get("coverage", 0.0) * 100, 1)  # Get coverage percentage
                if cx > 5 or cov < 50:  # Highlight functions with high complexity or low coverage
                    md += f"- `{fn_name}`: Complexity = {cx}, Coverage = {cov}%\n"

        # Function Docstrings
        func_docs = content.get("docstrings", {}).get("functions", [])
        if func_docs:
            md += "\n**📚 Function Descriptions:**\n"
            for fn in func_docs:
                name = fn.get("name")
                desc = fn.get("description", "No description.")
                args = fn.get("args", "*Not documented*")
                returns = fn.get("returns", "*Not documented*")
                md += f"- `{name}`: {desc}\n  - Args: {args}\n  - Returns: {returns}\n"

        md += "\n</details>\n"

    return md
