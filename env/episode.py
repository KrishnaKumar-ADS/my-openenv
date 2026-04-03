from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from data.schema import TicketSchema

class EpisodeState(BaseModel):
    ticket: TicketSchema
    step_count: int = 0
    status: str = "open"
    action_history: List[str] = Field(default_factory=list)
    response_history: List[str] = Field(default_factory=list)
    conversation_history: List[str] = Field(default_factory=list)
    classification: Optional[str] = None
    customer_satisfaction_score: float = 0.5
    total_reward: float = 0.0
    done: bool = False

    class Config:
        arbitrary_types_allowed = True

class EpisodeLogic:
    MAX_STEPS = 10

    def is_done(self, state: EpisodeState) -> bool:
        return (
            state.status in ("resolved", "escalated")
            or state.step_count >= self.MAX_STEPS
        )

    def should_inject_followup(self, state: EpisodeState) -> bool:
        """Inject a customer follow-up after the first agent response in Hard tasks."""
        return (
            state.status == "responding"
            and len(state.response_history) == 1
            and state.ticket.difficulty == "hard"
        )

    def get_available_actions(self, state: EpisodeState) -> list[str]:
        if state.done: return []
        if state.status == "open": return ["classify_ticket"]
        if state.status == "classified": return ["respond_to_customer", "escalate_ticket"]
        if state.status == "responding": return ["respond_to_customer", "escalate_ticket", "close_ticket"]
        return []

    def transition(self, state: EpisodeState, action_type: str) -> str:
        """Return the new status after applying action_type."""
        if action_type == "classify_ticket": return "classified"
        if action_type == "respond_to_customer": return "responding"
        if action_type == "escalate_ticket": return "escalated"
        if action_type == "close_ticket": return "resolved"
        return state.status
