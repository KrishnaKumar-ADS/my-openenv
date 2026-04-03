from __future__ import annotations
import random, re
from typing import List
from data.schema import TicketSchema

TYPO_REPLACEMENTS = {
    "you": "u", "are": "r", "please": "plz", "thanks": "thx", "your": "ur",
    "cannot": "cant", "to": "2", "for": "4", "people": "ppl", "before": "b4", "great": "gr8",
}
INFORMAL_PHRASES = [" asap", " pls help", " need help now", " this is ridiculous", " sort this out"]
HARD_AMBIGUITY_SUFFIXES = [
    " I'm not sure who to contact about this.",
    " This might be a billing or technical problem.",
    " Please advise as I'm very confused.",
]

class Augmentor:
    def __init__(self, noise_rate: float = 0.25, seed: int = 42):
        self.noise_rate = noise_rate
        self._rng = random.Random(seed)

    def augment(self, tickets: List[TicketSchema]) -> List[TicketSchema]:
        return [self._augment_one(t) for t in tickets]

    def assign_difficulty(self, tickets: List[TicketSchema]) -> List[TicketSchema]:
        result = []
        for t in tickets:
            if t.noise_injected or len(t.message) < 40:
                t = t.model_copy(update={"difficulty": "easy"})
            elif t.sentiment in ("negative", "angry") and len(t.conversation_history) > 0:
                t = t.model_copy(update={"difficulty": "hard"})
            else:
                t = t.model_copy(update={"difficulty": "medium"})
            result.append(t)
        return result

    def _augment_one(self, ticket: TicketSchema) -> TicketSchema:
        if self._rng.random() >= self.noise_rate: return ticket
        message = ticket.message
        message = self._inject_typos(message)
        message = self._inject_informal(message)
        if ticket.difficulty == "hard": message = self._inject_ambiguity(message)
        return ticket.model_copy(update={"message": message, "noise_injected": True})

    def _inject_typos(self, text: str) -> str:
        for word, replacement in TYPO_REPLACEMENTS.items():
            if self._rng.random() < 0.4:
                text = re.sub(rf"\b{word}\b", replacement, text, flags=re.IGNORECASE)
        return text

    def _inject_informal(self, text: str) -> str:
        if self._rng.random() < 0.5: text += self._rng.choice(INFORMAL_PHRASES)
        return text

    def _inject_ambiguity(self, text: str) -> str:
        return text + self._rng.choice(HARD_AMBIGUITY_SUFFIXES)
