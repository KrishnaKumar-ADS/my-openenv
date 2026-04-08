from __future__ import annotations
import re, subprocess, sys, os
from pathlib import Path

START_PATTERN = re.compile(r"^\[START\] task=\w+ env=\S+ model=\S+$")
STEP_PATTERN  = re.compile(r"^\[STEP\] step=\d+ action=\S+ reward=[\d.]+ done=(true|false) error=\S+$")
END_PATTERN   = re.compile(r"^\[END\] success=(true|false) steps=\d+ score=[\d.]+ rewards=[\d.,]+$")

def test_inference_stdout_format():
    root = Path(__file__).resolve().parents[1]
    script = root / "inference.py"
    env = {**os.environ, "TASK_NAME": "easy", "CS_ENV_URL": "http://localhost:7860"}
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=120, env=env, cwd=str(root))
    lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
    start_lines = [l for l in lines if l.startswith("[START]")]
    end_lines   = [l for l in lines if l.startswith("[END]")]
    assert len(start_lines) >= 1, "Missing [START] line"
    assert len(end_lines) >= 1, "Missing [END] line"
    assert START_PATTERN.match(start_lines[0])
    assert END_PATTERN.match(end_lines[-1])
