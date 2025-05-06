def risk_emoji(score: float) -> str:
    if score >= 90:
        return "🟢"
    elif score >= 70:
        return "🟡"
    else:
        return "🔴"

def render_bar(score: float, width: int = 20) -> str:
    filled = int((score / 100.0) * width)
    return "▓" * filled + "░" * (width - filled)
