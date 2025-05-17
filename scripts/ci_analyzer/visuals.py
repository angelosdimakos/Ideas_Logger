"""
This module provides functionality to render visual representations of risk and scores for code quality analysis.

It includes functions to generate risk emojis and bar representations based on severity scores.
"""


def risk_emoji(score: float) -> str:
    """
    Returns an emoji indicating risk level based on the given severity score.
    
    A green emoji ("🟢") represents low risk for scores 90 and above, yellow ("🟡") indicates moderate risk for scores between 70 and 89, and red ("🔴") signifies high risk for scores below 70.
    """
    if score >= 90:
        return "🟢"  # Green emoji for low risk
    elif score >= 70:
        return "🟡"  # Yellow emoji for moderate risk
    else:
        return "🔴"  # Red emoji for high risk


def render_bar(score: float, width: int = 20) -> str:
    """
    Generates a horizontal bar visualizing a score as filled and unfilled segments.
    
    Args:
        score: The value to represent, expected in the range 0 to 100.
        width: Total number of segments in the bar (default is 20).
    
    Returns:
        A string with filled ("▓") and unfilled ("░") segments proportional to the score.
    """
    filled = int((score / 100.0) * width)  # Calculate how many sections of the bar should be filled
    return "▓" * filled + "░" * (
        width - filled
    )  # Return the filled and unfilled sections of the bar
