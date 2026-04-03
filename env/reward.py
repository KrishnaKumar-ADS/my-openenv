from __future__ import annotations
from typing import Dict, List
from env.models import ActionType, ActionModel, RewardModel
from utils.similarity import cosine_similarity_tfidf

ADJACENT_CATEGORIES: Dict[str, List[str]] = {
    "billing":   ["refund", "account"],
    "refund":    ["billing", "account"],
    "technical": ["general"],
    "account":   ["billing", "refund"],
    "general":   ["technical"],
}

class RewardCalculator:
    WEIGHTS = {
        "classification":   0.20,
        "response_quality": 0.35,
        "resolution":       0.30,
        "escalation":       0.10,
        "efficiency":      -0.05,
        "loop":            -1.00,
    }
    MIN_RAW = -3.0
    MAX_RAW =  2.6

    def compute(self, action: ActionModel, env_state) -> RewardModel:
        components: Dict[str, float] = {}

        if action.action_type == ActionType.CLASSIFY:
            components["classification"] = self.classification_reward(
                action.content or "", env_state.ticket.category
            )
        elif action.action_type == ActionType.RESPOND:
            components["response_quality"] = self.response_quality_reward(
                action.content or "", env_state.ticket.expected_resolution
            )
        elif action.action_type in (ActionType.ESCALATE, ActionType.CLOSE):
            components["resolution"] = self.resolution_reward(
                action.action_type, env_state.ticket.should_escalate
            )
            components["escalation"] = self.escalation_reward(
                action.action_type == ActionType.ESCALATE,
                env_state.ticket.should_escalate,
            )

        components["efficiency"] = self.efficiency_penalty(env_state.step_count)
        components["loop"] = self.loop_penalty(
            env_state.action_history, action.action_key()
        )

        raw = sum(v * self.WEIGHTS.get(k, 1.0) for k, v in components.items())
        return RewardModel(reward=self.normalize(raw), components=components)

    def classification_reward(self, predicted: str, true_label: str) -> float:
        predicted = predicted.strip().lower()
        true_label = true_label.strip().lower()
        if predicted == true_label: return 0.5
        if predicted in ADJACENT_CATEGORIES.get(true_label, []): return 0.15
        return -0.3

    def response_quality_reward(self, response: str, expected: str) -> float:
        if not response or len(response.strip()) < 20: return -0.3
        if "[INSERT]" in response or "<TODO>" in response: return -0.5

        sim = cosine_similarity_tfidf(response, expected)
        if sim >= 0.7: score = 0.8
        elif sim >= 0.4: score = 0.3
        else: score = -0.1

        lower = response.lower()
        if any(w in lower for w in ("sorry", "apologize", "understand", "apologies")): score += 0.1
        if any(w in lower for w in ("please", "will", "can", "step", "contact", "follow")): score += 0.1
        return round(score, 4)

    def resolution_reward(self, action_type: ActionType, should_escalate: bool) -> float:
        correct_close    = (action_type == ActionType.CLOSE    and not should_escalate)
        correct_escalate = (action_type == ActionType.ESCALATE and should_escalate)
        return 1.0 if (correct_close or correct_escalate) else -1.0

    def escalation_reward(self, escalated: bool, should_escalate: bool) -> float:
        if escalated and should_escalate: return 0.3
        if escalated and not should_escalate: return -0.5
        return 0.0

    def efficiency_penalty(self, step_count: int) -> float:
        if step_count <= 3: return 0.0
        return -0.05 * (step_count - 3)

    def loop_penalty(self, action_history: List[str], current_key: str) -> float:
        return -1.0 if current_key in action_history else 0.0

    def normalize(self, raw: float) -> float:
        normalized = (raw - self.MIN_RAW) / (self.MAX_RAW - self.MIN_RAW)
        return round(min(max(normalized, 0.0), 1.0), 4)
