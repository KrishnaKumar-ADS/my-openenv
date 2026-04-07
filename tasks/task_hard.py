from __future__ import annotations
from typing import List
from env.graders import HardGrader

class TaskHard:
    NAME = "hard"; MAX_STEPS = 10; DESCRIPTION = "Full resolution."; SUCCESS_THRESHOLD = 0.5
    def __init__(self): self._grader = HardGrader()
    def grade(self, responses: List[str], expected: str, final_action: str, should_escalate: bool, step_count: int) -> float:
        return self._grader.grade(responses, expected, final_action, should_escalate, step_count)
    def is_success(self, score: float) -> bool: return score >= self.SUCCESS_THRESHOLD

def grade_hard(
    responses: List[str],
    expected: str,
    final_action: str,
    should_escalate: bool,
    step_count: int,
) -> float:
    """Module-level grader entrypoint for manifest-based validators."""
    return TaskHard().grade(
        responses, expected, final_action, should_escalate, step_count
    )
