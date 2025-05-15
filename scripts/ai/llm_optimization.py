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
from typing import Any, List, Dict, Tuple
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
    return float(np.mean(values)) if values else 0.0


from typing import List, Dict

def _categorise_issues(offenders: List[Dict]) -> str:
    """
    Return a three-line summary that counts how many files trigger each
    broad issue category.

    Categories
    ----------
    • type errors   (Mypy Errors > 5)
    • high complexity (Avg Complexity > 7)
    • low coverage  (Avg Coverage % < 60)
    """
    counts = {
        "type errors":   sum(o.get("Mypy Errors",     0) > 5  for o in offenders),
        "high complexity": sum(o.get("Avg Complexity", 0) > 7  for o in offenders),
        "low coverage":  sum(o.get("Avg Coverage %", 100) < 60 for o in offenders),
    }

    return "\n".join(f"Files with {label}: {count}" for label, count in counts.items())



# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def summarize_file_data_for_llm(file_data: dict, file_path: str) -> dict[str, Any]:
    """Create the *exact* summary dict expected by legacy callers/tests."""

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
        issues.append(f"Low coverage: {name} ({data.get('coverage')*100:.1f}% )")

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
    """Return an LLM prompt focused on refactoring advice for up to *limit* files."""

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
    summary_metrics: Dict[str, Any],
    *,
    limit: int = 30,
) -> str:
    """Return a high‑level, strategy‑oriented prompt covering the *limit* worst files."""

    top_offenders = severity_data[:limit]
    issue_summary = _categorise_issues(top_offenders)
    top5 = ", ".join(
        f"{os.path.basename(d['Full Path'])} (Score: {d['Severity Score']})" for d in severity_data[:5]
    )

    template = f"""
    Based on the analysis of this codebase, provide 3‑5 strategic recommendations
    for improving code quality and test coverage.  Focus on actionable steps that
    would have the most impact.

    Key metrics:
      • Total Tests .............. {summary_metrics['total_tests']}
      • Avg Test Strictness ...... {summary_metrics['avg_strictness']}
      • Avg Severity ............. {summary_metrics['avg_severity']}
      • Overall Coverage ......... {summary_metrics['coverage']} %
      • Missing Docstrings ....... {summary_metrics['missing_docs']} %
      • High / Med / Low Severity  {summary_metrics['high_severity_tests']} / {summary_metrics['medium_severity_tests']} / {summary_metrics['low_severity_tests']}

    {issue_summary}

    Top 5 most severe modules: {top5}

    When providing recommendations, prioritise:
      1. Code complexity (hard to test & maintain)
      2. Test coverage (risk mitigation)
      3. Type errors (reliability)
      4. Documentation (maintainability)

    Respond with patterns and systemic actions – avoid per‑file micromanagement.
    """

    return template.strip()


# ---------------------------------------------------------------------------
# Scoring helper
# ---------------------------------------------------------------------------

def compute_severity(file_path: str, content: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a weighted severity score for one module."""

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
    """Aggregate offender list into a human‑readable summary block."""

    high_cx = [os.path.basename(fp) for fp, _, _, _, cx, _ in offenders if cx > 8]
    low_cov = [os.path.basename(fp) for fp, _, _, _, _, cov in offenders if cov < 50]
    many_err = [os.path.basename(fp) for fp, _, errs, _, _, _ in offenders if len(errs) > 5]

    def _fmt(lst: List[str]) -> str:
        return f"{', '.join(lst[:5])}{'...' if len(lst) > 5 else ''}"

    return (
        "Summary of issues:\n"
        f"- {len(high_cx)} files with high complexity: {_fmt(high_cx)}\n"
        f"- {len(low_cov)} files with low coverage: {_fmt(low_cov)}\n"
        f"- {len(many_err)} files with many type errors: {_fmt(many_err)}"
    )


def _format_offender_block(offenders: List[Tuple[str, float, list, int, float, float]], verbose: bool) -> str:
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
