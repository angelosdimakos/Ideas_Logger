"""
This module provides functionality to render visual representations of risk and scores for code quality analysis.

It includes functions to generate risk emojis and bar representations based on severity scores.
"""


def risk_emoji(score: float) -> str:
    """
    Return an emoji representing the risk level based on the severity score.

    Args:
        score (float): The severity score to evaluate.

    Returns:
        str: An emoji indicating the risk level (green, yellow, or red).
    """
    if score >= 90:
        return "🟢"  # Green emoji for low risk
    elif score >= 70:
        return "🟡"  # Yellow emoji for moderate risk
    else:
        return "🔴"  # Red emoji for high risk


def render_bar(score: float, width: int = 20) -> str:
    """
    Render a horizontal bar representation of the score.

    Args:
        score (float): The score to represent as a bar.
        width (int): The total width of the bar (default is 20).

    Returns:
        str: A string representing the filled and unfilled sections of the bar.
    """
    filled = int((score / 100.0) * width)  # Calculate how many sections of the bar should be filled
    return "▓" * filled + "░" * (width - filled)  # Return the filled and unfilled sections of the bar
