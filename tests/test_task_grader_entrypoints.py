from __future__ import annotations

import importlib
from pathlib import Path

import yaml


def _load_manifest() -> dict:
    manifest_path = Path(__file__).resolve().parents[1] / "openenv.yaml"
    with manifest_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _resolve_entrypoint(entrypoint: str):
    module_name, symbol_name = entrypoint.split(":", 1)
    module = importlib.import_module(module_name)
    return getattr(module, symbol_name)


def test_manifest_has_at_least_three_tasks_with_graders():
    manifest = _load_manifest()
    tasks = manifest.get("tasks", [])
    tasks_with_graders = [t for t in tasks if isinstance(t, dict) and t.get("grader")]
    assert len(tasks_with_graders) >= 3


def test_each_task_grader_is_callable_and_bounded():
    manifest = _load_manifest()
    tasks = manifest.get("tasks", [])

    checked = 0
    for task in tasks:
        if not isinstance(task, dict):
            continue
        grader_ep = task.get("grader")
        if not grader_ep:
            continue

        grader_fn = _resolve_entrypoint(grader_ep)
        assert callable(grader_fn)

        score = float(grader_fn())
        assert 0.0 <= score <= 1.0
        checked += 1

    assert checked >= 3
