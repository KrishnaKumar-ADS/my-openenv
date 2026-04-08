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


def test_grader_entrypoints_tolerate_generic_validator_inputs():
    manifest = _load_manifest()
    tasks = manifest.get("tasks", [])

    checked = 0
    sample_payload = {
        "prediction": "billing",
        "true_label": "billing",
        "response": "Thanks for reaching out. We can help with this issue.",
        "expected": "Thanks for reaching out. We can help with this issue.",
        "responses": ["Thanks for reaching out."],
        "final_action": "close_ticket",
        "should_escalate": False,
        "step_count": 1,
    }

    for task in tasks:
        if not isinstance(task, dict):
            continue
        grader_ep = task.get("grader")
        if not grader_ep:
            continue

        grader_fn = _resolve_entrypoint(grader_ep)

        score_no_args = float(grader_fn())
        score_dict_arg = float(grader_fn(sample_payload))
        score_noisy_args = float(grader_fn("x", "x", 1, "ignored", sample_payload))

        assert 0.0 <= score_no_args <= 1.0
        assert 0.0 <= score_dict_arg <= 1.0
        assert 0.0 <= score_noisy_args <= 1.0
        checked += 1

    assert checked >= 3
