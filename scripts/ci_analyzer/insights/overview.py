# scripts/ci_analyzer/insights/overview.py

from typing import Any, Dict, List


def generate_overview_insights(audit: Dict[str, Any]) -> List[str]:
    """
    Generate a summary of audit insights, including test coverage, code complexity, and quality metrics.

    Args:
        audit (Dict[str, Any]): Audit data for multiple files.

    Returns:
        List[str]: Formatted overview lines with key statistics and metrics.
    """

    total_files = len(audit)
    # Missing tests
    files_with_missing_tests = sum(1 for data in audit.values() if data.get("missing_tests"))
    total_missing_tests = sum(len(data.get("missing_tests", [])) for data in audit.values())

    # Complexity metrics
    comp_scores = [
        obj["complexity"]
        for data in audit.values()
        for obj in data.get("complexity", {}).values()
        if isinstance(obj, dict) and "complexity" in obj
    ]
    methods_high_complexity = sum(1 for s in comp_scores if s >= 10)

    # Files with high average complexity
    file_avg_complexities: List[float] = []
    for data in audit.values():
        scores = [
            obj["complexity"]
            for obj in data.get("complexity", {}).values()
            if isinstance(obj, dict) and "complexity" in obj
        ]
        if scores:
            file_avg_complexities.append(sum(scores) / len(scores))
    files_high_avg_complexity = sum(1 for avg in file_avg_complexities if avg >= 10)
    avg_complexity = (sum(comp_scores) / len(comp_scores)) if comp_scores else 0

    # Quality metrics
    total_flake8 = sum(
        len(d.get("quality", {}).get("flake8", {}).get("issues", [])) for d in audit.values()
    )
    files_needing_black = sum(
        1
        for d in audit.values()
        if d.get("quality", {}).get("black", {}).get("needs_formatting", False)
    )
    total_mypy = sum(
        len(d.get("quality", {}).get("mypy", {}).get("errors", [])) for d in audit.values()
    )
    total_pydoc = sum(
        len(d.get("quality", {}).get("pydocstyle", {}).get("issues", [])) for d in audit.values()
    )
    coverage_vals = [
        d.get("quality", {}).get("coverage", {}).get("percent", 0)
        for d in audit.values()
        if d.get("quality", {}).get("coverage")
    ]
    avg_coverage = (sum(coverage_vals) / len(coverage_vals)) if coverage_vals else 0

    # Testing metrics
    total_methods = sum(len(data.get("testing", {})) for data in audit.values())
    untested_methods = sum(
        1
        for data in audit.values()
        for v in data.get("testing", {}).values()
        if v.get("tested") is False
    )
    tested_methods = total_methods - untested_methods
    testing_coverage = (tested_methods / total_methods * 100) if total_methods else None

    # Diff metrics
    diff_files = [d.get("diff", {}) for d in audit.values() if d.get("diff")]
    total_changed = sum(d.get("changed", 0) for d in diff_files)
    total_covered = sum(d.get("covered", 0) for d in diff_files)
    diff_coverage = (total_covered / total_changed * 100) if total_changed else None

    parts: List[str] = ["### 🗒️ Overview\n"]
    parts.append(f"- **Total Files Audited:** `{total_files}`")
    parts.append(f"- **Files with Missing Tests:** `{files_with_missing_tests}`")
    parts.append(f"- **Total Missing Tests:** `{total_missing_tests}`")
    parts.append(f"- **Methods (Complexity ≥10):** `{methods_high_complexity}`")
    parts.append(f"- **Files with Avg Complexity ≥10:** `{files_high_avg_complexity}`")
    parts.append(f"- **Average Method Complexity:** `{avg_complexity:.1f}`")
    parts.append(f"- **Total Flake8 Issues:** `{total_flake8}`")
    parts.append(f"- **Files Needing Black Formatting:** `{files_needing_black}`")
    parts.append(f"- **Total MyPy Errors:** `{total_mypy}`")
    parts.append(f"- **Total Pydocstyle Issues:** `{total_pydoc}`")
    parts.append(f"- **Average Coverage %:** `{avg_coverage:.1f}%`")
    if total_methods:
        parts.append(f"- **Testing Coverage:** `{testing_coverage:.1f}%`")
    else:
        parts.append(f"- **Testing Coverage:** `N/A`")
    if total_changed:
        parts.append(f"- **Diff Coverage:** `{diff_coverage:.1f}%`")
    else:
        parts.append(f"- **Diff Coverage:** `N/A`")
    parts.append("")  # padding newline
    return parts
