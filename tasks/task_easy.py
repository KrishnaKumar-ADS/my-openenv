from __future__ import annotations
from typing import Any
from env.graders import EasyGrader

class TaskEasy:
    NAME = "easy"; MAX_STEPS = 3; DESCRIPTION = "Classify ticket."; SUCCESS_THRESHOLD = 0.5
    def __init__(self): self._grader = EasyGrader()
    def grade(self, predicted: str, true_label: str, step_count: int) -> float:
        return self._grader.grade(predicted, true_label, step_count)
    def is_success(self, score: float) -> bool: return score >= self.SUCCESS_THRESHOLD

def _coerce_label(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("predicted", "prediction", "category", "label", "content"):
            if value.get(key):
                return str(value[key])
    return str(value or "")


def grade_easy(*args: Any, **kwargs: Any) -> float:
    """Robust module-level grader entrypoint for manifest-based validators."""
    predicted: Any = kwargs.get("predicted", kwargs.get("prediction", kwargs.get("label", "")))
    true_label: Any = kwargs.get("true_label", kwargs.get("ground_truth", kwargs.get("expected", "")))
    step_count: Any = kwargs.get("step_count", kwargs.get("step", kwargs.get("steps", 1)))

    if len(args) >= 1 and predicted in ("", None):
        predicted = args[0]
    if len(args) >= 2 and true_label in ("", None):
        true_label = args[1]
    if len(args) >= 3 and step_count in ("", None, 1):
        step_count = args[2]

    if isinstance(predicted, dict):
        if true_label in ("", None):
            true_label = predicted.get("true_label") or predicted.get("expected") or predicted.get("ground_truth")
        if step_count in ("", None, 1):
            step_count = predicted.get("step_count") or predicted.get("step") or predicted.get("steps") or 1

    try:
        step = max(1, int(step_count))
    except (TypeError, ValueError):
        step = 1

    predicted_label = _coerce_label(predicted) or "general"
    true_label_str = _coerce_label(true_label) or predicted_label or "general"
    return TaskEasy().grade(predicted_label, true_label_str, step)


def grade(*args: Any, **kwargs: Any) -> float:
    """Compatibility alias for validators expecting tasks.task_easy:grade."""
    return grade_easy(*args, **kwargs)


def grader(*args: Any, **kwargs: Any) -> float:
    """Compatibility alias for validators expecting tasks.task_easy:grader."""
    return grade_easy(*args, **kwargs)
