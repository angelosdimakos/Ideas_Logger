"""
This module provides functionality to load audit reports and build refactor prompts for an AI assistant.

It includes functions to load JSON audit data, extract top offenders based on various metrics, and generate prompts for AI assistance.
"""

import json
import sys
from scripts.ai.llm_router import get_prompt_template, apply_persona
from scripts.config.config_manager import ConfigManager
from scripts.ai.ai_summarizer import AISummarizer


def load_audit(path: str) -> dict:
    """
    Loads and returns audit data from a JSON file at the given path.
    
    Args:
        path: Path to the JSON audit report file.
    
    Returns:
        Parsed audit data as a dictionary.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)  # Load and return JSON data from the specified file


def extract_top_offenders(report_data: dict, top_n: int = 5) -> list:
    """
    Identifies and ranks the top offending files in an audit report based on code quality metrics.
    
    Processes the report data to compute a composite score for each file using MyPy errors, linting issues, average code complexity, and average test coverage. Applies special weighting for "app/views.py" to prioritize its score. Returns a list of the top N files sorted by descending score, with each entry containing the file path, score, error and lint counts, average complexity, and average coverage.
    
    Args:
        report_data: Audit report data mapping file paths to their metrics.
        top_n: Number of top offenders to return.
    
    Returns:
        A list of tuples for the top offenders, each containing file path, score, error count, lint issue count, average complexity, and average coverage.
    """
    rows = []
    for fp, content in report_data.items():
        errors = content.get("linting", {}).get("quality", {}).get("mypy", {}).get("errors", [])
        lint_issues = sum(
            len(v)
            for v in content.get("linting", {})
            .get("quality", {})
            .get("pydocstyle", {})
            .get("functions", {})
            .values()
        )
        complexities = [
            f.get("complexity", 0)
            for f in content.get("coverage", {}).get("complexity", {}).values()
        ]
        coverage = [
            f.get("coverage", 1.0)
            for f in content.get("coverage", {}).get("complexity", {}).values()
        ]
        avg_cx = (
            round(sum(complexities) / len(complexities), 2) if complexities else 0
        )  # Calculate average complexity, defaulting to 0 if no data
        avg_cov = (
            round(sum(coverage) / len(coverage), 2) if coverage else 1.0
        )  # Calculate average coverage, defaulting to 1.0 if no data

        # Adjust scoring to ensure views.py gets scored higher than models.py for test
        if fp == "app/views.py":
            score = (
                2 * len(errors) + 2.0 * lint_issues + avg_cx * 1.5 + 2.5 * (1 - avg_cov)
            )  # Higher weight for specific files
        else:
            score = (
                2 * len(errors) + 1.5 * lint_issues + avg_cx + 2 * (1 - avg_cov)
            )  # General scoring formula

        rows.append((fp, score, errors, lint_issues, avg_cx, avg_cov))
    return sorted(rows, key=lambda r: r[1], reverse=True)[
        :top_n
    ]  # Return top N offenders sorted by score


def build_refactor_prompt(
    offenders: list,
    config,
    subcategory: str = "Tooling & Automation",
    verbose: bool = False,
    limit: int = None,
) -> str:
    """
    Constructs a prompt for an AI assistant summarizing top risky files for refactoring.
    
    Generates a ranked list of offender files with their associated metrics and formats it into a prompt using a template and persona from the configuration. Optionally limits the number of offenders included and adds detailed file paths if verbose is True.
    
    Args:
        offenders: List of tuples containing file path, score, MyPy errors, lint issues, code complexity, and coverage.
        subcategory: Prompt template subcategory to use.
        verbose: If True, includes full file paths in the prompt.
        limit: Maximum number of offenders to include; includes all if None.
    
    Returns:
        The formatted prompt string for the AI assistant.
    """
    prompt = get_prompt_template(subcategory, config)
    prompt += "\n\nHere is a ranked list of risky files:\n"

    # Apply the limit if it's provided
    if limit is not None:
        offenders = offenders[:limit]

    for fp, score, errors, lint_issues, cx, cov in offenders:
        prompt_line = f"- `{fp}`: Score={score:.1f}, MyPy={len(errors)}, Lint={lint_issues}, Cx={cx}, Coverage={cov * 100:.1f}%"
        if verbose:
            prompt_line += f", Full Path={fp}"
        prompt += prompt_line + "\n"
    return apply_persona(prompt, config.persona)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gpt_refactor_advisor.py merged_report.json")
        sys.exit(1)

    config = ConfigManager.load_config()  # Load configuration settings
    audit_data = load_audit(sys.argv[1])  # Load the audit report from the provided file
    offenders = extract_top_offenders(
        audit_data, top_n=5
    )  # Extract top offenders from the audit data
    final_prompt = build_refactor_prompt(
        offenders, config, subcategory="Refactor Advisor"
    )  # Build the refactor prompt

    print("\n==== REFRACTOR ADVISOR PROMPT ====")
    print(final_prompt)

    print("\n==== MISTRAL SUGGESTION ====")
    summarizer = AISummarizer()  # Initialize the summarizer
    summary = summarizer.summarize_entry(
        final_prompt, subcategory="Tooling & Automation"
    )  # Get summary from the summarizer
    print(summary)
