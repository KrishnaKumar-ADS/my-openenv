from __future__ import annotations
from typing import Any, List
from env.graders import HardGrader

class TaskHard:
    NAME = "hard"; MAX_STEPS = 10; DESCRIPTION = "Full resolution."; SUCCESS_THRESHOLD = 0.5
    def __init__(self): self._grader = HardGrader()
    def grade(self, responses: List[str], expected: str, final_action: str, should_escalate: bool, step_count: int) -> float:
        return self._grader.grade(responses, expected, final_action, should_escalate, step_count)
    def is_success(self, score: float) -> bool: return score >= self.SUCCESS_THRESHOLD


def _coerce_response_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    if isinstance(value, dict):
        for key in ("responses", "response_history", "conversation_history"):
            seq = value.get(key)
            if isinstance(seq, list):
                return [str(item) for item in seq]
        single = value.get("response") or value.get("content") or value.get("text")
        return [str(single)] if single else []
    return [str(value)]


def grade_hard(
    *args: Any,
    **kwargs: Any,
) -> float:
    """Robust module-level grader entrypoint for manifest-based validators."""
    responses: Any = kwargs.get("responses", kwargs.get("response", None))
    expected: Any = kwargs.get("expected", kwargs.get("target", ""))
    final_action: Any = kwargs.get("final_action", kwargs.get("action_type", "close_ticket"))
    should_escalate: Any = kwargs.get("should_escalate", False)
    step_count: Any = kwargs.get("step_count", kwargs.get("step", kwargs.get("steps", 1)))

    if len(args) >= 1 and responses is None:
        responses = args[0]
    if len(args) >= 2 and expected in ("", None):
        expected = args[1]
    if len(args) >= 3 and final_action in ("", None, "close_ticket"):
        final_action = args[2]
    if len(args) >= 4 and should_escalate in ("", None, False):
        should_escalate = args[3]
    if len(args) >= 5 and step_count in ("", None, 1):
        step_count = args[4]

    if isinstance(responses, dict):
        payload = responses
        if expected in ("", None):
            expected = payload.get("expected") or payload.get("expected_resolution") or payload.get("target")
        if final_action in ("", None, "close_ticket"):
            final_action = payload.get("final_action") or payload.get("action_type") or payload.get("action") or "close_ticket"
        if should_escalate in ("", None, False):
            should_escalate = payload.get("should_escalate", False)
        if step_count in ("", None, 1):
            step_count = payload.get("step_count") or payload.get("step") or payload.get("steps") or 1

    try:
        step = max(1, int(step_count))
    except (TypeError, ValueError):
        step = 1

    if isinstance(should_escalate, str):
        should_escalate_flag = should_escalate.strip().lower() in {"1", "true", "yes", "y"}
    else:
        should_escalate_flag = bool(should_escalate)

    response_list = _coerce_response_list(responses)

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
