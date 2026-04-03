from __future__ import annotations
from env.graders import MediumGrader

class TaskMedium:
    NAME = "medium"; MAX_STEPS = 5; DESCRIPTION = "Generate response."; SUCCESS_THRESHOLD = 0.5
    def __init__(self): self._grader = MediumGrader()
    def grade(self, response: str, expected: str, step_count: int) -> float:
        return self._grader.grade(response, expected, step_count)
    def is_success(self, score: float) -> bool: return score >= self.SUCCESS_THRESHOLD
