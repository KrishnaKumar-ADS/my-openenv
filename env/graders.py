from __future__ import annotations
from utils.similarity import cosine_similarity_tfidf

class EasyGrader:
    ADJACENT: dict = {
        "billing":   ["refund", "account"],
        "refund":    ["billing", "account"],
        "technical": ["general"],
        "account":   ["billing", "refund"],
        "general":   ["technical"],
    }

    def grade(self, predicted: str, true_label: str, step_count: int) -> float:
        predicted = predicted.strip().lower()
        true_label = true_label.strip().lower()
        if predicted == true_label: base = 1.0
        elif predicted in self.ADJACENT.get(true_label, []): base = 0.3
        else: base = 0.0
        score = base - (step_count - 1) * 0.05
        return round(min(max(score, 0.0), 1.0), 4)

class MediumGrader:
    def grade(self, response: str, expected: str, step_count: int) -> float:
        if not response or len(response.strip()) < 20: return 0.0
        if "[INSERT]" in response or "<TODO>" in response: return 0.0
        sim = cosine_similarity_tfidf(response, expected)
        if sim >= 0.7: score = 0.8
        elif sim >= 0.4: score = 0.3
        else: score = 0.15
        lower = response.lower()
        if any(w in lower for w in ("sorry", "apologize", "understand", "apologies")): score += 0.1
        if any(w in lower for w in ("please", "will", "can", "step", "contact", "follow")): score += 0.1
        score = max(0.0, score - (step_count - 2) * 0.02)
        return round(min(score, 1.0), 4)

class HardGrader:
    def grade(
        self, responses: list[str], expected: str, final_action: str,
        should_escalate: bool, step_count: int
    ) -> float:
        if final_action == "close_ticket" and not should_escalate: resolution_score = 1.0
        elif final_action == "escalate_ticket" and should_escalate: resolution_score = 1.0
        elif final_action == "escalate_ticket" and not should_escalate: resolution_score = -0.5
        else: resolution_score = -1.0

        quality_scores = [cosine_similarity_tfidf(r, expected) for r in responses if r]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        if avg_quality >= 0.7: quality_reward = 0.8
        elif avg_quality >= 0.4: quality_reward = 0.3
        else: quality_reward = 0.0

        efficiency_bonus = 0.1 if step_count <= 5 else 0.0
        raw = (resolution_score * 0.50) + (quality_reward * 0.40) + efficiency_bonus
        return round(min(max(raw, 0.0), 1.0), 4)
