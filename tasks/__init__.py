from __future__ import annotations

from .task_easy import TaskEasy, grade_easy, grader as easy_grader
from .task_medium import TaskMedium, grade_medium, grader as medium_grader
from .task_hard import TaskHard, grade_hard, grader as hard_grader

TASK_GRADERS = {
    "easy": easy_grader,
    "medium": medium_grader,
    "hard": hard_grader,
}


def get_task_graders() -> dict[str, object]:
    """Return the canonical task->grader map used by submission validators."""
    return dict(TASK_GRADERS)


__all__ = [
    "TaskEasy",
    "TaskMedium",
    "TaskHard",
    "grade_easy",
    "grade_medium",
    "grade_hard",
    "TASK_GRADERS",
    "get_task_graders",
]

