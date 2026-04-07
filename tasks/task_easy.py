from __future__ import annotations
from env.graders import EasyGrader

class TaskEasy:
    NAME = "easy"; MAX_STEPS = 3; DESCRIPTION = "Classify ticket."; SUCCESS_THRESHOLD = 0.5
    def __init__(self): self._grader = EasyGrader()
    def grade(self, predicted: str, true_label: str, step_count: int) -> float:
        return self._grader.grade(predicted, true_label, step_count)
    def is_success(self, score: float) -> bool: return score >= self.SUCCESS_THRESHOLD

def grade_easy(predicted: str, true_label: str, step_count: int) -> float:
    """Module-level grader entrypoint for manifest-based validators."""
    return TaskEasy().grade(predicted, true_label, step_count)
