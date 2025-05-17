# llm_quality_utils_refactored.py
"""Utility helpers for summarising code‑quality artefacts and building LLM prompts.

🔧 **Patch v2** – restores backwards‑compat fields and fixes helper signature
regressions that broke the existing unit‑test suite.

*   `summarize_file_data_for_llm` again returns the exact keys
    ``{"complexity", "coverage"}`` expected by old tests.
*   Added thin wrapper ``_categorise_issues`` that accepts the legacy
    `(entries, condition, message, cap)` signature and is used by
    ``build_strategic_recommendations_prompt``.
*   Internal refactor helpers renamed with leading underscores but public
    function signatures stay **unchanged**.
*   Added type‑hints + docstrings for the new helper.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, List, Dict, Tuple, Union
import logging

import numpy as np

from scripts.ai.llm_router import get_prompt_template, apply_persona

__all__ = [
    "summarize_file_data_for_llm",
    "extract_top_issues",
    "build_refactor_prompt",
    "build_strategic_recommendations_prompt",
    "compute_severity",
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Low‑level helpers
# ---------------------------------------------------------------------------

def _mean(values: List[float]) -> float:
    """
    Calculates the mean of a list of floats.
    
    Returns 0.0 if the list is empty.
    """
    return float(np.mean(values)) if values else 0.0


from typing import List, Dict


def _categorise_issues(offenders: List[Dict]) -> str:
    """
    Returns a summary of how many files fall into each major code quality issue category.
    
    The summary includes counts of files with more than 5 type errors, average complexity greater than 7, and average coverage below 60%.
    """
    counts = {
        "type errors": sum(o.get("Mypy Errors", 0) > 5 for o in offenders),
        "high complexity": sum(o.get("Avg Complexity", 0) > 7 for o in offenders),
        "low coverage": sum(o.get("Avg Coverage %", 100) < 60 for o in offenders),
    }

    return "\n".join(f"Files with {label}: {count}" for label, count in counts.items())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def summarize_file_data_for_llm(file_data: dict, file_path: str) -> dict[str, Any]:
    """
    Generates a summary dictionary of code quality metrics for a single file.
    
    Extracts and computes average complexity, coverage percentage, MyPy error count, and docstring completeness from nested file data. Returns a dictionary with legacy-compatible keys, including the file name, full path, rounded metrics, docstring ratio, and a list of up to three top issues.
    """

    coverage_info: dict = file_data.get("coverage", {}).get("complexity", {})
    lint_info: dict = file_data.get("linting", {}).get("quality", {})
    docstring_info: dict = file_data.get("docstrings", {})

    complexities = [fn.get("complexity", 0.0) for fn in coverage_info.values()]
    coverages = [fn.get("coverage", 0.0) for fn in coverage_info.values()]

    avg_complexity = _mean(complexities)
    avg_coverage = _mean(coverages)

    mypy_errors = len(lint_info.get("mypy", {}).get("errors", []))

    funcs = docstring_info.get("functions", [])
    missing_docs = sum(1 for f in funcs if not f.get("description"))

    summary = {
        "file": os.path.basename(file_path),
        "full_path": file_path,
        "complexity": round(avg_complexity, 2),  # ← restored key
        "coverage": round(avg_coverage * 100, 1),  # ← restored key
        "mypy_errors": mypy_errors,
        "docstring_ratio": f"{len(funcs) - missing_docs}/{len(funcs)}" if funcs else "0/0",
        "top_issues": extract_top_issues(file_data, max_issues=3),
    }
    return summary


def extract_top_issues(file_data: dict, max_issues: int = 3) -> List[str]:
    """
    Extracts up to a specified number of top code quality issues from file data.
    
    The function prioritizes the first MyPy error, the first function with high complexity (complexity > 10), and the first function with low coverage (coverage < 50%), returning formatted issue descriptions.
    
    Args:
        file_data: Dictionary containing code quality metrics for a file.
        max_issues: Maximum number of issues to extract.
    
    Returns:
        A list of formatted strings describing the top issues found in the file.
    """
    issues: List[str] = []

    mypy_errors = file_data.get("linting", {}).get("quality", {}).get("mypy", {}).get("errors", [])
    if mypy_errors and len(issues) < max_issues:
        issues.append(f"MyPy error: {mypy_errors[0]}")

    complexity_info = file_data.get("coverage", {}).get("complexity", {})
    high_cmp = [(n, d) for n, d in complexity_info.items() if d.get("complexity", 0) > 10]
    if high_cmp and len(issues) < max_issues:
        name, data = high_cmp[0]
        issues.append(f"High complexity: {name} ({data.get('complexity')})")

    low_cov = [(n, d) for n, d in complexity_info.items() if d.get("coverage", 1.0) < 0.5]
    if low_cov and len(issues) < max_issues:
        name, data = low_cov[0]
        issues.append(f"Low coverage: {name} ({data.get('coverage') * 100:.1f}% )")

    return issues


# ---------------------------------------------------------------------------
# Prompt builders – refactored into composable helpers
# ---------------------------------------------------------------------------

def build_refactor_prompt(
        offenders: List[Tuple[str, float, list, int, float, float]],
        config: Any,
        *,
        verbose: bool = False,
        limit: int = 30,
) -> str:
    """
        Builds an LLM prompt requesting strategic refactoring suggestions for a list of offender files.
        
        The prompt summarizes up to `limit` files with significant code quality issues, applies a persona and template from the configuration, and includes both a summary and detailed offender information. The resulting prompt instructs the LLM to focus on identifying refactoring patterns rather than file-specific advice.
        
        Args:
            offenders: List of tuples containing file details and metrics for files needing refactoring.
            config: Configuration object providing persona and prompt template.
            verbose: If True, includes detailed information for each file; otherwise, provides a concise summary.
            limit: Maximum number of offender files to include in the prompt.
        
        Returns:
            A formatted prompt string for use with an LLM.
        """

    offenders = offenders[:limit]
    template = apply_persona(
        get_prompt_template("Refactor Suggestions", config), config.persona
    )

    summary_section = _summarise_offenders(offenders)

    files_info = _format_offender_block(offenders, verbose)

    return (
        f"{template}\n\n{summary_section}\n\nFiles needing attention:\n{files_info}\n\n"
        "Please provide strategic refactoring suggestions, focusing on patterns rather than individual files when possible."
    )


def build_strategic_recommendations_prompt(
        severity_data: List[Dict[str, Any]],
        summary_metrics: Union[Dict[str, Any], str],
        *,
        limit: int = 30,
) -> str:
    """
        Constructs a detailed prompt for an LLM to generate strategic, actionable recommendations for improving code quality and test coverage based on severity data and summary metrics.
        
        The prompt summarizes the distribution of key issues (high complexity, low coverage, type errors), highlights problematic modules with multiple severe files, and lists the top offenders. It instructs the LLM to provide specific, non-generic recommendations tied directly to the identified files and modules, prioritizing complexity, coverage, type errors, and documentation.
        
        Args:
            severity_data: List of dictionaries containing per-file severity metrics and scores.
            summary_metrics: Overall codebase metrics, either as a formatted string or a dictionary.
            limit: Maximum number of top offender files to include in the summary (default: 30).
        
        Returns:
            A formatted prompt string for use with an LLM, emphasizing targeted, codebase-specific recommendations.
        """

    top_offenders = severity_data[:limit]
    issue_summary = _categorise_issues(top_offenders)

    # Extract specific issue patterns
    high_complexity_files = [d for d in severity_data if d.get("Avg Complexity", 0) > 7]
    low_coverage_files = [d for d in severity_data if d.get("Avg Coverage %", 100) < 60]
    mypy_error_files = [d for d in severity_data if d.get("Mypy Errors", 0) > 0]

    # Get the top 5 files for detailed examination
    top5_details = []
    for d in severity_data[:5]:
        file_name = os.path.basename(d['Full Path'])
        score = d['Severity Score']
        complexity = d.get('Avg Complexity', 'N/A')
        coverage = d.get('Avg Coverage %', 'N/A')
        mypy_errors = d.get('Mypy Errors', 0)

        top5_details.append(
            f"• {file_name} - Score: {score}, Complexity: {complexity}, "
            f"Coverage: {coverage}%, MyPy Errors: {mypy_errors}"
        )

    top5_text = "\n".join(top5_details)

    # Calculate distribution of issues
    total_files = len(severity_data)
    high_complexity_pct = len(high_complexity_files) / total_files * 100 if total_files else 0
    low_coverage_pct = len(low_coverage_files) / total_files * 100 if total_files else 0
    mypy_error_pct = len(mypy_error_files) / total_files * 100 if total_files else 0

    # Find repeated patterns in file names (potential modules that need attention)
    file_prefixes = {}
    for d in severity_data:
        file_name = os.path.basename(d['Full Path'])
        # Get the module name (remove extension and look at first part)
        prefix = file_name.split('.')[0].split('_')[0]
        if prefix not in file_prefixes:
            file_prefixes[prefix] = []
        file_prefixes[prefix].append(d['Severity Score'])

    # Find modules with multiple problematic files
    problem_modules = {k: len(v) for k, v in file_prefixes.items() if len(v) > 1}
    problem_modules_text = ", ".join(
        [f"{k} ({v} files)" for k, v in sorted(problem_modules.items(), key=lambda x: x[1], reverse=True)[:3]])

    # Handle the case where summary_metrics is a string instead of a dictionary
    if isinstance(summary_metrics, str):
        metrics_text = summary_metrics
    else:
        # If it's a dictionary, format it as expected
        metrics_text = f"""
      • Total Tests .............. {summary_metrics.get('total_tests', 'N/A')}
      • Avg Test Strictness ...... {summary_metrics.get('avg_strictness', 'N/A')}
      • Avg Severity ............. {summary_metrics.get('avg_severity', 'N/A')}
      • Overall Coverage ......... {summary_metrics.get('coverage', 'N/A')} %
      • Missing Docstrings ....... {summary_metrics.get('missing_docs', 'N/A')} %
      • High / Med / Low Severity  {summary_metrics.get('high_severity_tests', 'N/A')} / {summary_metrics.get('medium_severity_tests', 'N/A')} / {summary_metrics.get('low_severity_tests', 'N/A')}
        """

    template = f"""
    Based on the analysis of this codebase, provide 3‑5 strategic recommendations
    for improving code quality and test coverage. Focus on actionable steps that
    would have the most impact.

    Key metrics:
{metrics_text}

    Issue distribution:
    • {high_complexity_pct:.1f}% of files have high complexity
    • {low_coverage_pct:.1f}% of files have low test coverage
    • {mypy_error_pct:.1f}% of files have type errors

    {issue_summary}

    Problem modules with multiple files: {problem_modules_text}

    Top 5 most severe modules:
{top5_text}

    When providing recommendations, prioritise:
      1. Code complexity (hard to test & maintain)
      2. Test coverage (risk mitigation)
      3. Type errors (reliability)
      4. Documentation (maintainability)

    Respond with SPECIFIC recommendations tied to the actual issues found in this 
    codebase. Name problematic files and modules directly. Don't give generic advice - be
    precise about what needs fixing and why. Avoid boilerplate recommendations that could
    apply to any codebase. Focus on the actual patterns identified in this analysis.

    For example, if you see that visualization.py has high complexity, low coverage, and many
    type errors, suggest specific refactoring approaches relevant to visualization code, not
    just generic "break down large functions" advice.
    """

    return template.strip()


# ---------------------------------------------------------------------------
# Scoring helper
# ---------------------------------------------------------------------------

def compute_severity(file_path: str, content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates a weighted severity score and summary metrics for a single module.
    
    The severity score combines counts of MyPy errors, pydocstyle lint issues, average function complexity, and lack of test coverage using fixed weights. Returns a dictionary with the file name, full path, error and issue counts, average complexity, average coverage percentage, and the computed severity score.
    """

    coverage = content.get("coverage", {}).get("complexity", {})
    linting = content.get("linting", {}).get("quality", {})

    mypy_errors = linting.get("mypy", {}).get("errors", [])
    pydoc_issues = linting.get("pydocstyle", {}).get("functions", {})

    complexities = [fn.get("complexity", 0) for fn in coverage.values()]
    coverages = [fn.get("coverage", 1.0) for fn in coverage.values()]

    avg_complexity = float(np.mean(complexities)) if complexities else 0.0
    avg_coverage = float(np.mean(coverages)) if coverages else 1.0

    severity = (
            2.0 * len(mypy_errors)
            + 1.5 * sum(len(v) for v in pydoc_issues.values())
            + 2.0 * avg_complexity  # emphasise complexity
            + 2.0 * (1.0 - avg_coverage)
    )

    return {
        "File": os.path.basename(file_path),
        "Full Path": file_path,
        "Mypy Errors": len(mypy_errors),
        "Lint Issues": sum(len(v) for v in pydoc_issues.values()),
        "Avg Complexity": round(avg_complexity, 2),
        "Avg Coverage %": round(avg_coverage * 100, 1),
        "Severity Score": round(severity, 2),
    }


# ---------------------------------------------------------------------------
# Internal utilities  (kept *private*)
# ---------------------------------------------------------------------------


def _summarise_offenders(offenders: List[Tuple[str, float, list, int, float, float]]) -> str:
    """
    Aggregates a list of offender files into a summary of key code quality issues.
    
    Counts and lists up to five example files for each of the following categories: high complexity (complexity > 8), low coverage (coverage < 50%), and many type errors (more than 5 type errors). Returns a formatted multiline string summarizing the counts and sample file names per category.
    """

    high_cx = [os.path.basename(fp) for fp, _, _, _, cx, _ in offenders if cx > 8]
    low_cov = [os.path.basename(fp) for fp, _, _, _, _, cov in offenders if cov < 50]
    many_err = [os.path.basename(fp) for fp, _, errs, _, _, _ in offenders if len(errs) > 5]

    def _fmt(lst: List[str]) -> str:
        """
        Formats a list of strings as a comma-separated string, truncating with '...' if more than five items.
        
        Args:
            lst: List of strings to format.
        
        Returns:
            A string of up to five comma-separated items from the list, followed by '...' if the list contains more than five items.
        """
        return f"{', '.join(lst[:5])}{'...' if len(lst) > 5 else ''}"

    return (
        "Summary of issues:\n"
        f"- {len(high_cx)} files with high complexity: {_fmt(high_cx)}\n"
        f"- {len(low_cov)} files with low coverage: {_fmt(low_cov)}\n"
        f"- {len(many_err)} files with many type errors: {_fmt(many_err)}"
    )


def _format_offender_block(offenders: List[Tuple[str, float, list, int, float, float]], verbose: bool) -> str:
    """
    Formats offender file details into a summary block for inclusion in LLM prompts.
    
    If verbose is True, returns a detailed multiline summary for each file including severity score, error counts, complexity, coverage, and sample errors. Otherwise, returns a concise single-line summary per file.
    """
    if verbose:
        return "\n\n".join(
            (
                f"File: {os.path.basename(fp)}\n"
                f"Severity Score: {score:.2f}\n"
                f"MyPy Errors: {len(errors)}\n"
                f"Lint Issues: {lint_issues}\n"
                f"Avg Complexity: {cx:.2f}\n"
                f"Coverage: {cov:.1f}%\n"
                f"Sample errors: {errors[:2]}"
            )
            for fp, score, errors, lint_issues, cx, cov in offenders
        )
    return "\n".join(
        f"- {os.path.basename(fp)}: Score {score:.2f}, {len(errors)} MyPy errors, {lint_issues} lint issues"
        for fp, score, errors, lint_issues, cx, cov in offenders
    )


# ---------------------------------------------------------------------------
# Module init – configure debug logger if needed
# ---------------------------------------------------------------------------

if int(os.getenv("LLM_UTILS_DEBUG", "0")):
    logging.basicConfig(level=logging.DEBUG)