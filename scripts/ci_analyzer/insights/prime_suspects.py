# scripts/ci_analyzer/insights/prime_suspects.py

import re
from typing import Any, Dict, List, Tuple
from collections import Counter


def generate_prime_insights(audit: Dict[str, Any]) -> List[str]:
    """
    Identify the most frequent errors and highest complexity methods.
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
            pydoc_issues.append(msg)
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
