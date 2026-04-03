from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ResetRequest(BaseModel):
    task: str = "easy"
    seed: Optional[int] = None

class StepRequest(BaseModel):
    action_type: str
    content: Optional[str] = None

class ResetResponse(BaseModel):
    observation: Dict[str, Any]
    done: bool = False
    info: Dict[str, Any] = {}

class StepResponse(BaseModel):
    observation: Dict[str, Any]
    reward: float
    done: bool
    info: Dict[str, Any] = {}

class StateResponse(BaseModel):
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
