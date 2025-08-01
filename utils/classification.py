# wholesale_lead_analyzer/utils/classification.py

def classify_lead(score: int) -> str:
    """Classify leads based on score."""
    if score >= 70:
        return "HOT"
    elif score >= 50:
        return "WARM"
    elif score >= 30:
        return "COLD"
    else:
        return "UNLIKELY"

def estimate_probability(score: int) -> str:
    """Estimate probability of being a motivated seller."""
    if score >= 70:
        return "High (70-90%)"
    elif score >= 50:
        return "Medium-High (50-70%)"
    elif score >= 30:
        return "Medium (30-50%)"
    else:
        return "Low (0-30%)"