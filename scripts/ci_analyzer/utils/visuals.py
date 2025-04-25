"""
visuals.py

This module provides utility functions for rendering visual indicators of code quality and risk scores.

Core features include:
- Rendering a colored bar representation of a score (0–100) using emoji blocks.
- Returning an emoji that represents risk level based on a numeric score.

Intended for use in CI reports and dashboards to provide intuitive, visual feedback on code metrics.
"""

# scripts/ci_analyzer/utils/visuals.py


def render_bar(score: float, width: int = 10) -> str:
    """
    Render a visual bar for scores between 0–100.
    E.g. 🟩🟩🟩🟨⬜⬜⬜⬜⬜⬜
    """
    filled = round((score / 100) * width)
    bar = "🟩" * filled + "⬜" * (width - filled)
    return bar


def risk_emoji(score: float) -> str:
    """
    Return a risk emoji based on score.
    """
    if score >= 90:
        return "🟢"
    elif score >= 70:
        return "🟡"
    else:
        return "🔴"
