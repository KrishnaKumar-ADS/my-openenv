from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    CLASSIFY = "classify_ticket"
    RESPOND  = "respond_to_customer"
    ESCALATE = "escalate_ticket"
    CLOSE    = "close_ticket"

class ActionModel(BaseModel):
    action_type: ActionType
    content: Optional[str] = None

    def action_key(self) -> str:
        """Stable string used for loop-detection in action_history."""
        content_snippet = (self.content or "")[:30].replace(" ", "_")
        return f"{self.action_type.value}:{content_snippet}"

class ObservationModel(BaseModel):
    ticket_text: str
    conversation_history: List[str] = Field(default_factory=list)
    last_agent_action: Optional[str] = None
    status: str = "open"
    step_count: int = 0
    ticket_id: str = ""
    priority: str = "medium"
    timestamp: str = ""
    available_actions: List[str] = Field(default_factory=list)
    sentiment_hint: str = "neutral"

class RewardModel(BaseModel):
    reward: float = 0.0
    components: Dict[str, float] = Field(default_factory=dict)

class StepResult(BaseModel):
    observation: ObservationModel
    reward: float
    done: bool
    info: Dict = Field(default_factory=dict)

class FullStateModel(BaseModel):
    ticket_id: str
    step_count: int
    status: str
    action_history: List[str]
    response_history: List[str]
    classification: Optional[str]
    true_category: str
    expected_resolution: str
    should_escalate: bool
    customer_satisfaction_score: float
    noise_injected: bool
    total_reward: float
    done: bool
