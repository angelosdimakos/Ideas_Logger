# strategy.py

from typing import List, Dict
from scripts.ai.ai_summarizer import AISummarizer
from scripts.ai import llm_optimization as optim
from scripts.ai.llm_router import apply_persona

def generate_strategy(
    severity_data: List[Dict],
    summary_metrics: Dict,
    limit: int,
    persona: str,
    summarizer: AISummarizer
) -> str:
    """
    Generate strategic recommendations using severity and metric data.

    Args:
        severity_data (List[Dict]): Computed severity info per file.
        summary_metrics (Dict): High-level code quality metrics.
        limit (int): Max number of files to include.
        persona (str): AI assistant persona.
        summarizer (AISummarizer): Summarization engine.

    Returns:
        str: Strategic AI recommendations
    """
    prompt = optim.build_strategic_recommendations_prompt(
        severity_data=severity_data,
        summary_metrics=summary_metrics,
        limit=limit
    )

    persona_prompt = apply_persona(prompt, persona)
    return summarizer.summarize_entry(persona_prompt, subcategory="Tooling & Automation")
