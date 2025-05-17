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
    Generates a horizontal bar visualizing the score as filled and unfilled segments.
    
    The bar's length is determined by the width parameter, with the number of filled segments proportional to the score out of 100.
    
    Args:
        score: The value to visualize, where 100 fills the bar completely.
        width: Total number of segments in the bar (default is 20).
    
    Returns:
        A string composed of filled ("▓") and unfilled ("░") segments representing the score.
    """
    filled = int((score / 100.0) * width)  # Calculate how many sections of the bar should be filled
    return "▓" * filled + "░" * (
        width - filled
    )  # Return the filled and unfilled sections of the bar
