import os
import numpy as np
from scripts.ai.llm_router import get_prompt_template, apply_persona

# 1. Create a new helper function to summarize file data before sending to LLM
def summarize_file_data_for_llm(file_data, file_path):
    """
    Condense file data to essential information for LLM processing.
    This helps reduce token usage when sending many files.
    """
    # Extract key metrics
    coverage_info = file_data.get("coverage", {}).get("complexity", {})
    lint_info = file_data.get("linting", {}).get("quality", {})
    docstring_info = file_data.get("docstrings", {})

    # Calculate summary metrics
    avg_complexity = np.mean([fn.get("complexity", 0) for fn in coverage_info.values()]) if coverage_info else 0
    avg_coverage = np.mean([fn.get("coverage", 0) for fn in coverage_info.values()]) if coverage_info else 0
    mypy_errors = len(lint_info.get("mypy", {}).get("errors", []))

    # Count docstring issues
    funcs = docstring_info.get("functions", [])
    missing_docs = sum(1 for func in funcs if not func.get("description"))
    total_funcs = len(funcs)

    # Create summary
    return {
        "file": os.path.basename(file_path),
        "full_path": file_path,
        "complexity": round(avg_complexity, 2),
        "coverage": round(avg_coverage * 100, 1),
        "mypy_errors": mypy_errors,
        "docstring_ratio": f"{total_funcs - missing_docs}/{total_funcs}",
        "top_issues": extract_top_issues(file_data, max_issues=3)  # Extract only top 3 issues
    }


def extract_top_issues(file_data, max_issues=3):
    """Extract the most important issues from a file."""
    issues = []

    # Get MyPy errors (limited sample)
    mypy_errors = file_data.get("linting", {}).get("quality", {}).get("mypy", {}).get("errors", [])
    if mypy_errors and len(issues) < max_issues:
        # Take just one representative error
        issues.append(f"MyPy error: {mypy_errors[0]}")

    # Check for high complexity functions
    complexity_info = file_data.get("coverage", {}).get("complexity", {})
    if complexity_info:
        high_complexity = [(name, data) for name, data in complexity_info.items()
                           if data.get("complexity", 0) > 10]
        if high_complexity and len(issues) < max_issues:
            name, data = high_complexity[0]
            issues.append(f"High complexity: {name} ({data.get('complexity', 0)})")

    # Check for coverage issues
    low_coverage = [(name, data) for name, data in complexity_info.items()
                    if data.get("coverage", 1.0) < 0.5]
    if low_coverage and len(issues) < max_issues:
        name, data = low_coverage[0]
        issues.append(f"Low coverage: {name} ({data.get('coverage', 0) * 100:.1f}%)")

    return issues


# 2. Modify the build_refactor_prompt function to handle more files efficiently
def build_refactor_prompt(offenders, config, verbose=False, limit=30):
    """
    Build a prompt for refactoring suggestions, optimized for handling many files.

    Args:
        offenders: List of (file_path, score, errors, lint_issues, complexity, coverage) tuples
        config: Configuration object
        verbose: Whether to include detailed info about each file
        limit: Maximum number of files to include
    """
    offenders = offenders[:limit]  # Limit to specified number

    if verbose:
        # Original detailed format
        files_info = "\n\n".join([
            f"File: {os.path.basename(fp)}\n"
            f"Severity Score: {score:.2f}\n"
            f"MyPy Errors: {len(errors)}\n"
            f"Lint Issues: {lint_issues}\n"
            f"Avg Complexity: {cx:.2f}\n"
            f"Coverage: {cov:.1f}%\n"
            f"Sample errors: {errors[:2]}"
            for fp, score, errors, lint_issues, cx, cov in offenders
        ])
    else:
        # Condensed format for many files
        files_info = "\n".join([
            f"- {os.path.basename(fp)}: Score {score:.2f}, {len(errors)} MyPy errors, {lint_issues} lint issues"
            for fp, score, errors, lint_issues, cx, cov in offenders
        ])

    # Group files by issue type for better organization
    high_complexity_files = [os.path.basename(fp) for fp, _, _, _, cx, _ in offenders if cx > 8]
    low_coverage_files = [os.path.basename(fp) for fp, _, _, _, _, cov in offenders if cov < 50]
    many_errors_files = [os.path.basename(fp) for fp, _, errors, _, _, _ in offenders if len(errors) > 5]

    summary_section = f"""
    Summary of issues:
    - {len(high_complexity_files)} files with high complexity: {', '.join(high_complexity_files[:5])}{'...' if len(high_complexity_files) > 5 else ''}
    - {len(low_coverage_files)} files with low coverage: {', '.join(low_coverage_files[:5])}{'...' if len(low_coverage_files) > 5 else ''}
    - {len(many_errors_files)} files with many type errors: {', '.join(many_errors_files[:5])}{'...' if len(many_errors_files) > 5 else ''}
    """

    template = get_prompt_template("Refactor Suggestions", config)
    final_prompt = apply_persona(template, config.persona)

    return f"{final_prompt}\n\n{summary_section}\n\nFiles needing attention:\n{files_info}\n\nPlease provide strategic refactoring suggestions, focusing on patterns rather than individual files when possible."


# 3. Enhancement for Strategic Recommendations to handle 30 files
def build_strategic_recommendations_prompt(severity_data, summary_metrics, limit=30):
    """Build a prompt for strategic recommendations that can handle many files."""
    top_offenders = severity_data[:limit]

    # Group files by issue type
    type_errors_files = []
    complexity_files = []
    coverage_files = []

    for s in top_offenders:
        file_name = os.path.basename(s['Full Path'])
        if s['Mypy Errors'] > 5:
            type_errors_files.append(file_name)
        if s['Avg Complexity'] > 7:
            complexity_files.append(file_name)
        if s['Avg Coverage %'] < 60:
            coverage_files.append(file_name)

    # Create a summary by issue category
    issue_summary = f"""
    Files with type errors: {len(type_errors_files)}
    Files with high complexity: {len(complexity_files)}
    Files with low coverage: {len(coverage_files)}
    """

    strategic_prompt = f"""
    Based on the analysis of this codebase, provide 3-5 strategic recommendations for improving code quality
    and test coverage. Focus on actionable steps that would have the most impact.  Pay close attention to code complexity, 
    as it is a key indicator of maintainability and long-term risk in our project.

    Key metrics:
    - Total Tests: {summary_metrics['total_tests']}
    - Average Test Strictness: {summary_metrics['avg_strictness']}
    - Average Severity: {summary_metrics['avg_severity']}
    - Overall Coverage: {summary_metrics['coverage']}%
    - Missing Docstrings: {summary_metrics['missing_docs']}%
    - High Severity Tests: {summary_metrics['high_severity_tests']}
    - Medium Severity Tests: {summary_metrics['medium_severity_tests']}
    - Low Severity Tests: {summary_metrics['low_severity_tests']}

    {issue_summary}

    Top 5 most severe issues:
    {', '.join([f"{os.path.basename(s['Full Path'])} (Score: {s['Severity Score']})" for s in severity_data[:5]])}

    When providing recommendations, consider the following factors and their relative importance:
    - Code Complexity: (High complexity makes code harder to understand, test, and maintain.  Prioritize refactoring complex modules.)
    - Test Coverage: (Low coverage indicates higher risk.  Improve coverage, especially for critical modules.)
    - Type Errors: (Fixing type errors improves code reliability.)
    - Documentation: (Good documentation is essential for maintainability.)

    Please provide strategic recommendations that would help improve the overall health of this codebase.
    Focus on patterns and systemic issues rather than individual files.  Prioritize recommendations that address the root 
    causes of high complexity.
    """

    return strategic_prompt


def compute_severity(file_path: str, content: dict) -> dict:
    """
    Compute severity metrics for a file based on its linting errors, mypy errors,
    code complexity, and test coverage.

    Args:
        file_path: Path to the file being analyzed
        content: Dictionary containing analysis data for the file

    Returns:
        Dictionary with severity metrics
    """
    coverage_data = content.get("coverage", {}).get("complexity", {})
    linting = content.get("linting", {}).get("quality", {})
    mypy_errors = linting.get("mypy", {}).get("errors", [])
    pydocstyle_issues = linting.get("pydocstyle", {}).get("functions", {})

    num_lint_issues = sum(len(v) for v in pydocstyle_issues.values())
    num_mypy_errors = len(mypy_errors)

    complexities = [fn.get("complexity", 0) for fn in coverage_data.values()]
    coverages = [fn.get("coverage", 1.0) for fn in coverage_data.values()]

    avg_complexity = np.mean(complexities) if complexities else 0
    avg_coverage = np.mean(coverages) if coverages else 1.0

    severity_score = (
            2.0 * num_mypy_errors +
            1.5 * num_lint_issues +
            2.0 * avg_complexity +  # Increased weight of complexity to 2.0
            2.0 * (1.0 - avg_coverage)
    )

    return {
        "File": os.path.basename(file_path),
        "Full Path": file_path,
        "Mypy Errors": num_mypy_errors,
        "Lint Issues": num_lint_issues,
        "Avg Complexity": round(avg_complexity, 2),
        "Avg Coverage %": round(avg_coverage * 100, 1),
        "Severity Score": round(severity_score, 2),
    }
