from __future__ import annotations
from typing import Any
from env.graders import EasyGrader

class TaskEasy:
    NAME = "easy"; MAX_STEPS = 3; DESCRIPTION = "Classify ticket."; SUCCESS_THRESHOLD = 0.5
    def __init__(self): self._grader = EasyGrader()
    def grade(self, predicted: str, true_label: str, step_count: int) -> float:
        return self._grader.grade(predicted, true_label, step_count)
    def is_success(self, score: float) -> bool: return score >= self.SUCCESS_THRESHOLD

def grade_easy(predicted: Any = "", true_label: Any = "", step_count: Any = 1, **_: Any) -> float:
    """Module-level grader entrypoint for manifest-based validators."""
    try:
        step = max(1, int(step_count))
    except (TypeError, ValueError):
        step = 1
    return TaskEasy().grade(str(predicted or "general"), str(true_label or predicted or "general"), step)


def grade(*args: Any, **kwargs: Any) -> float:
    """Compatibility alias for validators expecting tasks.task_easy:grade."""
    return grade_easy(*args, **kwargs)


def grader(*args: Any, **kwargs: Any) -> float:
    """Compatibility alias for validators expecting tasks.task_easy:grader."""
    return grade_easy(*args, **kwargs)
