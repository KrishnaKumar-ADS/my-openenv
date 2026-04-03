from __future__ import annotations
import json
from pathlib import Path
from typing import List
from data.schema import TicketSchema

BASE_DIR = Path(__file__).resolve().parent
SEED_FILE   = BASE_DIR / "tickets" / "seed_tickets.jsonl"
EASY_FILE   = BASE_DIR / "tickets" / "processed" / "tickets_easy.jsonl"
MEDIUM_FILE = BASE_DIR / "tickets" / "processed" / "tickets_medium.jsonl"
HARD_FILE   = BASE_DIR / "tickets" / "processed" / "tickets_hard.jsonl"

TASK_FILE_MAP = {
    "easy":   EASY_FILE,
    "medium": MEDIUM_FILE,
    "hard":   HARD_FILE,
}

class DatasetLoader:
    def __init__(self, task: str = "easy"):
        self.task = task

    def load(self) -> List[TicketSchema]:
        target = TASK_FILE_MAP.get(self.task, EASY_FILE)
        path = target if target.exists() else SEED_FILE
        if not path.exists(): raise FileNotFoundError(f"Dataset not found at {path}. Run scripts/preprocess.py first.")

        tickets: List[TicketSchema] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    if path == SEED_FILE and data.get("difficulty") != self.task: continue
                    tickets.append(TicketSchema(**data))
        if not tickets and path == SEED_FILE:
            tickets = []
            with open(SEED_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line: tickets.append(TicketSchema(**json.loads(line)))
        return tickets
