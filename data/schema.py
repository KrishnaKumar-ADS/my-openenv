from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class TicketSchema(BaseModel):
    ticket_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: str
    category: str
    priority: str
    sentiment: str
    conversation_history: List[str] = Field(default_factory=list)
    expected_resolution: str
    should_escalate: bool = False
    noise_injected: bool = False
    difficulty: str = "easy"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "abc-123",
                "message": "I have been charged twice.",
                "category": "billing",
                "priority": "high",
                "sentiment": "angry",
                "conversation_history": [],
                "expected_resolution": "Apologize and issue refund.",
                "should_escalate": False,
                "noise_injected": False,
                "difficulty": "easy",
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }
