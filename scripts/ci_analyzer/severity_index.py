import numpy as np
import pandas as pd

def compute_severity(file_path: str, content: dict) -> dict:
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
        1.0 * avg_complexity +
        2.0 * (1.0 - avg_coverage)
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
    rows = [compute_severity(fp, content) for fp, content in report_data.items()]
    df = pd.DataFrame(rows)
    return df.sort_values(by="Severity Score", ascending=False).reset_index(drop=True)
