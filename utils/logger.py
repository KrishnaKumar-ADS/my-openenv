from __future__ import annotations
import logging, sys
from typing import List, Optional

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str] = None) -> None:
    action_slug = action[:30].replace(" ", "_")
    done_str  = "true" if done else "false"
    error_str = error if error else "null"
    print(f"[STEP] step={step} action={action_slug} reward={reward} done={done_str} error={error_str}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    success_str = "true" if success else "false"
    rewards_str = ",".join(str(r) for r in rewards) if rewards else "0.0"
    print(f"[END] success={success_str} steps={steps} score={score} rewards={rewards_str}", flush=True)
