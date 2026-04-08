from __future__ import annotations
from typing import Any
from env.graders import MediumGrader

class TaskMedium:
    NAME = "medium"; MAX_STEPS = 5; DESCRIPTION = "Generate response."; SUCCESS_THRESHOLD = 0.5
    def __init__(self): self._grader = MediumGrader()
    def grade(self, response: str, expected: str, step_count: int) -> float:
        return self._grader.grade(response, expected, step_count)
    def is_success(self, score: float) -> bool: return score >= self.SUCCESS_THRESHOLD

def _coerce_text(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("response", "content", "text", "output", "message"):
            if value.get(key):
                return str(value[key])
    return str(value or "")


def grade_medium(*args: Any, **kwargs: Any) -> float:
    """Robust module-level grader entrypoint for manifest-based validators."""
    response: Any = kwargs.get("response", kwargs.get("content", kwargs.get("text", "")))
    expected: Any = kwargs.get("expected", kwargs.get("target", kwargs.get("ground_truth", "")))
    step_count: Any = kwargs.get("step_count", kwargs.get("step", kwargs.get("steps", 1)))

    if len(args) >= 1 and response in ("", None):
        response = args[0]
    if len(args) >= 2 and expected in ("", None):
        expected = args[1]
    if len(args) >= 3 and step_count in ("", None, 1):
        step_count = args[2]

    if isinstance(response, dict):
        if expected in ("", None):
            expected = response.get("expected") or response.get("target") or response.get("ground_truth")
        if step_count in ("", None, 1):
            step_count = response.get("step_count") or response.get("step") or response.get("steps") or 1

    try:
        step = max(1, int(step_count))
    except (TypeError, ValueError):
        step = 1

    response_text = _coerce_text(response)
    expected_text = _coerce_text(expected) or response_text
    return TaskMedium().grade(response_text, expected_text, step)


def grade(*args: Any, **kwargs: Any) -> float:
    """Compatibility alias for validators expecting tasks.task_medium:grade."""
    return grade_medium(*args, **kwargs)


def grader(*args: Any, **kwargs: Any) -> float:
    """Compatibility alias for validators expecting tasks.task_medium:grader."""
    return grade_medium(*args, **kwargs)
