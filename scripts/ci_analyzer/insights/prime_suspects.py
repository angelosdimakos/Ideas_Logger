"""
prime_suspects.py

This module provides functionality to identify and summarize the most frequent code quality and complexity issues found in CI audit reports.

Core features include:
- Extracting and ranking the most common Flake8, Pydocstyle, and MyPy issues across all analyzed files.
- Identifying methods with the highest cyclomatic complexity.
- Formatting the top issues and complexity findings as Markdown strings for inclusion in CI reports and dashboards.

Intended for use in CI pipelines to help teams quickly pinpoint recurring code quality problems and complexity hotspots.
"""

# scripts/ci_analyzer/insights/prime_suspects.py

import re
from typing import Any, Dict, List, Tuple
from collections import Counter


def generate_prime_insights(audit: Dict[str, Any]) -> List[str]:
    """
    Analyzes audit data to extract and summarize the most frequent Flake8, Pydocstyle, and MyPy issues,
    as well as the highest complexity methods. Returns a formatted list of insight strings highlighting
    the top occurrences for each category.

    Args:
        audit (Dict[str, Any]): Dictionary containing code quality and complexity analysis results.

    Returns:
        List[str]: Formatted summary lines with the top issues and complexity findings.
    """
    flake8_codes: List[str] = []
    pydoc_issues: List[str] = []
    mypy_codes: List[str] = []
    comp_methods: List[Tuple[str, str, int]] = []

    for file_path, data in audit.items():
        # Flake8 codes
        for issue in data.get("quality", {}).get("flake8", {}).get("issues", []):
            code = issue.get("code")
            if code:
                flake8_codes.append(code)
        # Pydocstyle messages
        for msg in data.get("quality", {}).get("pydocstyle", {}).get("issues", []):
            key = msg if isinstance(msg, str) else str(msg)
            pydoc_issues.append(key)
        # MyPy error codes
        for err in data.get("quality", {}).get("mypy", {}).get("errors", []):
            match = re.search(r"\[([^\]]+)\]", err)
            if match:
                mypy_codes.append(match.group(1))
        # Complexity methods
        for method, obj in data.get("complexity", {}).items():
            if isinstance(obj, dict) and "complexity" in obj:
                comp_methods.append((file_path, method, obj["complexity"]))

    # Top occurrences
    top_flake8 = Counter(flake8_codes).most_common(3)
    top_pydoc = Counter(pydoc_issues).most_common(3)
    top_mypy = Counter(mypy_codes).most_common(3)
    top_complex = sorted(comp_methods, key=lambda t: -t[2])[:3]

    parts: List[str] = ["### 🎯 Prime Suspects\n"]
    if top_flake8:
        parts.append("- **Top Flake8 Errors:**")
        for code, count in top_flake8:
            parts.append(f"  - `{code}`: {count} occurrences")
    if top_pydoc:
        parts.append("- **Top Pydocstyle Issues:**")
        for msg, count in top_pydoc:
            parts.append(f"  - `{msg}`: {count} occurrences")
    if top_mypy:
        parts.append("- **Top MyPy Error Codes:**")
        for code, count in top_mypy:
            parts.append(f"  - `{code}`: {count} occurrences")
    if top_complex:
        parts.append("- **Highest Complexity Methods:**")
        for file_path, method, score in top_complex:
            parts.append(f"  - `{file_path}::{method}`: Complexity {score}")
    parts.append("")
    return parts
