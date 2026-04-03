from __future__ import annotations

POSITIVE_SIGNALS = ["thank", "great", "perfect", "excellent", "appreciate", "helpful", "resolved", "fixed", "working", "wonderful"]
NEGATIVE_SIGNALS = ["still", "not working", "persist", "again", "frustrated", "unacceptable", "terrible", "still having", "doesn't work"]

def update_sentiment(current_score: float, agent_response: str) -> float:
    lower = agent_response.lower()
    positive_hits = sum(1 for s in POSITIVE_SIGNALS if s in lower)
    negative_hits = sum(1 for s in NEGATIVE_SIGNALS if s in lower)
    delta = (positive_hits * 0.08) - (negative_hits * 0.10)
    new_score = current_score + delta
    return round(min(max(new_score, 0.0), 1.0), 4)

def score_to_label(score: float) -> str:
    if score >= 0.75: return "positive"
    if score >= 0.50: return "neutral"
    if score >= 0.25: return "negative"
    return "angry"
