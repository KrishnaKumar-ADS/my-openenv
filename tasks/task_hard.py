from __future__ import annotations
from typing import Any, List
from env.graders import HardGrader

class TaskHard:
    NAME = "hard"; MAX_STEPS = 10; DESCRIPTION = "Full resolution."; SUCCESS_THRESHOLD = 0.5
    def __init__(self): self._grader = HardGrader()
    def grade(self, responses: List[str], expected: str, final_action: str, should_escalate: bool, step_count: int) -> float:
        return self._grader.grade(responses, expected, final_action, should_escalate, step_count)
    def is_success(self, score: float) -> bool: return score >= self.SUCCESS_THRESHOLD

def grade_hard(
    responses: Any = None,
    expected: Any = "",
    final_action: Any = "close_ticket",
    should_escalate: Any = False,
    step_count: Any = 1,
    **_: Any,
) -> float:
    """Module-level grader entrypoint for manifest-based validators."""
    if responses is None:
        response_list: List[str] = []
    elif isinstance(responses, list):
        response_list = [str(item) for item in responses]
    else:
        response_list = [str(responses)]

    try:
        step = max(1, int(step_count))
    except (TypeError, ValueError):
        step = 1

    if isinstance(should_escalate, str):
        should_escalate_flag = should_escalate.strip().lower() in {"1", "true", "yes", "y"}
    else:
        should_escalate_flag = bool(should_escalate)

    return TaskHard().grade(
        response_list,
        str(expected or ""),
        str(final_action or "close_ticket"),
        should_escalate_flag,
        step,
    )


def grade(*args: Any, **kwargs: Any) -> float:
    """Compatibility alias for validators expecting tasks.task_hard:grade."""
    return grade_hard(*args, **kwargs)


def grader(*args: Any, **kwargs: Any) -> float:
    """Compatibility alias for validators expecting tasks.task_hard:grader."""
    return grade_hard(*args, **kwargs)
