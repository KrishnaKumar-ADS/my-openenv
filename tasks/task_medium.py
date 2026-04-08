from __future__ import annotations
from typing import Any
from env.graders import MediumGrader

class TaskMedium:
    NAME = "medium"; MAX_STEPS = 5; DESCRIPTION = "Generate response."; SUCCESS_THRESHOLD = 0.5
    def __init__(self): self._grader = MediumGrader()
    def grade(self, response: str, expected: str, step_count: int) -> float:
        return self._grader.grade(response, expected, step_count)
    def is_success(self, score: float) -> bool: return score >= self.SUCCESS_THRESHOLD

def grade_medium(response: Any = "", expected: Any = "", step_count: Any = 1, **_: Any) -> float:
    """Module-level grader entrypoint for manifest-based validators."""
    try:
        step = max(1, int(step_count))
    except (TypeError, ValueError):
        step = 1
    return TaskMedium().grade(str(response or ""), str(expected or response or ""), step)


def grade(*args: Any, **kwargs: Any) -> float:
    """Compatibility alias for validators expecting tasks.task_medium:grade."""
    return grade_medium(*args, **kwargs)


def grader(*args: Any, **kwargs: Any) -> float:
    """Compatibility alias for validators expecting tasks.task_medium:grader."""
    return grade_medium(*args, **kwargs)
