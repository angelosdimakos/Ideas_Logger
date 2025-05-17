from typing import Dict, List, Tuple
from pathlib import Path
from scripts.ai.llm_router import apply_persona


def build_contextual_prompt(
    query: str,
    top_offenders: List[Tuple[str, any, List[any], int, int, float]],
    summary_metrics: Dict[str, any],
    persona: str
) -> str:
    # Format top offenders with real values
    offender_summary = "\n".join([
        f"- `{fp}`: MyPy={len(errors)}, Lint={lint}, Cx={cx}, Coverage={cov * 100:.1f}%"
        for fp, _, errors, lint, cx, cov in top_offenders[:5]
    ])

    # Pretty-print overall metrics
    metrics_summary = "\n".join([
        f"- {key.replace('_', ' ').capitalize()}: {value}"
        for key, value in summary_metrics.items()
    ])

    prompt = f"""
You are an AI assistant helping engineers improve their Python codebase.

Here is a summary of the most risky files:
{offender_summary}

Overall metrics:
{metrics_summary}

Now answer the developer's question below using this context, showing your reasoning step by step:

Q: {query}
"""
    return apply_persona(prompt.strip(), persona)


def build_enhanced_contextual_prompt(
    query: str,
    top_offenders: List[Tuple[str, any, List[any], int, int, float]],
    summary_metrics: Dict[str, any],
    module_summaries: Dict[str, str],
    file_issues: Dict[str, Dict[str, List[any]]],
    file_recommendations: Dict[str, str],
    persona: str
) -> str:
    # Format top offenders with real values
    offender_summary = "\n".join([
        f"- `{fp}`: MyPy={len(errors)}, Lint={lint}, Cx={cx}, Coverage={cov * 100:.1f}%"
        for fp, _, errors, lint, cx, cov in top_offenders[:5]
    ])

    # Pretty-print overall metrics
    metrics_summary = "\n".join([
        f"- {key.replace('_', ' ').capitalize()}: {value}"
        for key, value in summary_metrics.items()
    ])

    # Build detailed module context for top offenders only
    relevant_files = [fp for fp, *_ in top_offenders[:5] if fp in module_summaries]
    module_context_entries = []
    for file_path in relevant_files:
        summary = module_summaries[file_path]
        issues = file_issues.get(file_path, {})
        mypy = ", ".join(str(e) for e in issues.get('mypy_errors', []))
        lint = ", ".join(str(i) for i in issues.get('lint_issues', []))
        rec = file_recommendations.get(file_path, 'No specific recommendation available')
        module_context_entries.append(
            f"## Module: {file_path}\n"
            f"**Summary**: {summary}\n"
            f"**Issues**:\n"
            f"- MyPy: {mypy or 'None'}\n"
            f"- Lint: {lint or 'None'}\n"
            f"**Recommendation**: {rec}"
        )
    module_context = "\n\n".join(module_context_entries)

    prompt = f"""
You are an AI assistant helping engineers improve their Python codebase.

Here is a summary of the most risky files:
{offender_summary}

Overall metrics:
{metrics_summary}

Detailed module information:
{module_context}

Now answer the developer's question below using this comprehensive context.
Provide specific, actionable recommendations for what to fix and how to fix it.
Show your reasoning step by step, and focus on concrete, practical advice rather than general suggestions.

Q: {query}
"""
    return apply_persona(prompt.strip(), persona)
