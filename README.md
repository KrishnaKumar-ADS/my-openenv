# CustomerSupportEnv

CustomerSupportEnv is an OpenEnv-style benchmark for evaluating AI agents on customer support ticket workflows.

The environment supports three task tiers:

1. Easy: ticket classification
2. Medium: response generation
3. Hard: multi-turn resolution with close/escalate decisions

## Features

1. FastAPI API with reset/step/state endpoints
2. Modular reward system and graders
3. Dataset preprocessing pipeline with seed fallback
4. Baseline inference runner with structured START/STEP/END logs
5. Unit and integration test coverage

## Repository Layout

1. `env/` environment logic, models, reward, graders
2. `data/` schemas, loaders, preprocessing, augmentation
3. `server/` API app and routes
4. `scripts/` dataset, preprocess, baseline, validation
5. `tests/` test suite

## Requirements

1. Python 3.11 recommended
2. Docker Desktop optional
3. Bash optional for shell scripts

## Quick Start (Windows PowerShell)

```bash
py -3.11 -m venv .venv311
./.venv311/Scripts/python.exe -m pip install --upgrade pip
./.venv311/Scripts/python.exe -m pip install -r requirements.txt
./.venv311/Scripts/python.exe -m pip install kaggle
./.venv311/Scripts/python.exe scripts/preprocess.py --source seed --output data/tickets/processed
./.venv311/Scripts/python.exe -m uvicorn server.app:app --host 127.0.0.1 --port 7860
```

In another terminal:

```bash
./.venv311/Scripts/python.exe -m pytest tests -v
./.venv311/Scripts/python.exe inference.py --task easy
./.venv311/Scripts/python.exe inference.py --task medium
./.venv311/Scripts/python.exe inference.py --task hard
```

## Process Guide

For a full from-scratch guide, see:

1. `process.md`

## Notes

1. Kaggle dataset download requires valid Kaggle credentials.
2. Docker validation requires Docker daemon running.
3. `script.py` at workspace root regenerates project files; run it only when intentionally scaffolding.
