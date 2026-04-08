from __future__ import annotations

from .task_easy import TaskEasy, grade_easy, grader as easy_grader
from .task_medium import TaskMedium, grade_medium, grader as medium_grader
from .task_hard import TaskHard, grade_hard, grader as hard_grader

TASK_GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard,
}

# Compatibility alias used by some validators.
GRADERS = TASK_GRADERS


def get_task_graders() -> dict[str, object]:
    """Return the canonical task->grader map used by submission validators."""
    return dict(TASK_GRADERS)


def get_graders() -> dict[str, object]:
    """Compatibility alias for validators expecting get_graders()."""
    return dict(TASK_GRADERS)


__all__ = [
    "TaskEasy",
    "TaskMedium",
    "TaskHard",
    "grade_easy",
    "grade_medium",
    "grade_hard",
    "easy_grader",
    "medium_grader",
    "hard_grader",
    "TASK_GRADERS",
    "GRADERS",
    "get_task_graders",
    "get_graders",
]

