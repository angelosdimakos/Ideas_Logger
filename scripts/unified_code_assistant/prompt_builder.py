# prompt_builder.py

from typing import Dict
from pathlib import Path
from scripts.ai.llm_router import apply_persona

def build_contextual_prompt(query: str, top_offenders: list, summary_metrics: Dict, persona: str) -> str:
    offender_summary = "\n".join([
        f"- `{fp}`: MyPy={{len(errors)}}, Lint={{lint}}, Cx={{cx}}, Coverage={{cov * 100:.1f}}%"
        for fp, _, errors, lint, cx, cov in top_offenders[:5]
    ])

    prompt = f"""
You are an AI assistant helping engineers improve their Python codebase.

Here is a summary of the most risky files:
{offender_summary}

Overall metrics:
{summary_metrics}

Now answer the developer's question below using this context, showing your reasoning step by step:

Q: {query}
"""
    return apply_persona(prompt.strip(), persona)

def build_enhanced_contextual_prompt(
    query: str,
    top_offenders: list,
    summary_metrics: Dict,
    module_summaries: Dict[str, str],
    file_issues: Dict[str, Dict],
    file_recommendations: Dict[str, str],
    persona: str
) -> str:

    offender_summary = "\n".join([
        f"- `{fp}`: MyPy={{len(errors)}}, Lint={{lint}}, Cx={{cx}}, Coverage={{cov * 100:.1f}}%"
        for fp, _, errors, lint, cx, cov in top_offenders[:5]
    ])

    module_context = "\n\n".join([
        f"## Module: {file_path}\n"
        f"**Summary**: {summary}\n"
        f"**Issues**:\n"
        f"- MyPy: {', '.join(str(e) for e in file_issues.get(file_path, {}).get('mypy_errors', []))[:200]}...\n"
        f"- Lint: {', '.join(str(i) for i in file_issues.get(file_path, {}).get('lint_issues', []))[:200]}...\n"
        f"**Recommendation**: {file_recommendations.get(file_path, 'No specific recommendation available')[:300]}..."
        for file_path, summary in module_summaries.items()
    ])

    prompt = f"""
You are an AI assistant helping engineers improve their Python codebase.

Here is a summary of the most risky files:
{offender_summary}

Overall metrics:
{summary_metrics}

Detailed module information:
{module_context}

Now answer the developer's question below using this comprehensive context.
Provide specific, actionable recommendations for what to fix and how to fix it.
Show your reasoning step by step, and focus on concrete, practical advice rather than general suggestions.

Q: {query}
"""
    return apply_persona(prompt.strip(), persona)
