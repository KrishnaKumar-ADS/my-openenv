#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime
import json
import sys
import uuid
from pathlib import Path

# Ensure repo root is importable when script is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.augmentor import Augmentor
from data.loader import SEED_FILE
from data.schema import TicketSchema


def load_seed() -> list[TicketSchema]:
    if not SEED_FILE.exists():
        print(f"[WARN] Seed file not found at {SEED_FILE}. Generating minimal seed.")
        generated = _generate_minimal_seed()
        SEED_FILE.parent.mkdir(parents=True, exist_ok=True)
        _write_jsonl(generated, SEED_FILE)
        print(f"[INFO] Generated seed dataset at {SEED_FILE}.")
        return generated

    tickets: list[TicketSchema] = []
    with open(SEED_FILE, "r", encoding="utf-8") as file_obj:
        for line in file_obj:
            line = line.strip()
            if line:
                tickets.append(TicketSchema(**json.loads(line)))

    print(f"[INFO] Loaded {len(tickets)} tickets from seed.")
    return tickets


def _generate_minimal_seed() -> list[TicketSchema]:
    now = datetime.datetime.utcnow().isoformat() + "Z"
    samples = [
        (
            "I was charged twice for my subscription this month. Please fix this.",
            "billing",
            "high",
            "angry",
            False,
            "medium",
        ),
        (
            "My app keeps crashing every time I open it on iOS 17.",
            "technical",
            "high",
            "negative",
            True,
            "hard",
        ),
        (
            "I need a full refund for order #4521 as the product never arrived.",
            "refund",
            "medium",
            "negative",
            False,
            "medium",
        ),
        (
            "I can't log in. It says my account is locked.",
            "account",
            "medium",
            "negative",
            False,
            "easy",
        ),
        (
            "Can you tell me what plans you offer for small businesses?",
            "general",
            "low",
            "neutral",
            False,
            "easy",
        ),
        (
            "The payment page is broken and I cannot complete my purchase.",
            "technical",
            "urgent",
            "angry",
            True,
            "hard",
        ),
        (
            "My invoice shows the wrong amount. Please review.",
            "billing",
            "medium",
            "neutral",
            False,
            "easy",
        ),
        (
            "How do I cancel my subscription?",
            "general",
            "low",
            "neutral",
            False,
            "easy",
        ),
        (
            "I accidentally deleted my account. Can it be recovered?",
            "account",
            "high",
            "negative",
            False,
            "medium",
        ),
        (
            "Your service has been down for 6 hours. This is unacceptable.",
            "technical",
            "urgent",
            "angry",
            True,
            "hard",
        ),
    ]

    tickets: list[TicketSchema] = []
    for message, category, priority, sentiment, escalate, difficulty in samples:
        tickets.append(
            TicketSchema(
                ticket_id=str(uuid.uuid4()),
                message=message,
                category=category,
                priority=priority,
                sentiment=sentiment,
                conversation_history=[],
                expected_resolution=(
                    f"Resolved {category} issue: addressed customer concern "
                    "and provided next steps."
                ),
                should_escalate=escalate,
                noise_injected=False,
                difficulty=difficulty,
                timestamp=now,
            )
        )

    return tickets


def split_and_save(tickets: list[TicketSchema], output_dir: Path) -> None:
    augmentor = Augmentor(noise_rate=0.25, seed=42)
    tickets = augmentor.assign_difficulty(augmentor.augment(tickets))

    easy = [ticket for ticket in tickets if ticket.difficulty == "easy"]
    medium = [ticket for ticket in tickets if ticket.difficulty == "medium"]
    hard = [ticket for ticket in tickets if ticket.difficulty == "hard"]

    # Keep all task splits non-empty for deterministic test/runtime behavior.
    if not easy:
        easy = tickets[: max(1, len(tickets) // 3)]
    if not medium:
        medium = tickets[: max(1, len(tickets) // 3)]
    if not hard:
        hard = tickets[: max(1, len(tickets) // 3)]

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(easy, output_dir / "tickets_easy.jsonl")
    _write_jsonl(medium, output_dir / "tickets_medium.jsonl")
    _write_jsonl(hard, output_dir / "tickets_hard.jsonl")

    print(f"[INFO] Wrote {len(easy)} easy, {len(medium)} medium, {len(hard)} hard tickets.")


def _write_jsonl(tickets: list[TicketSchema], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as file_obj:
        for ticket in tickets:
            file_obj.write(ticket.model_dump_json() + "\n")
    print(f"[INFO] -> {path} ({len(tickets)} records)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess CustomerSupportEnv dataset")
    parser.add_argument("--source", choices=["seed", "kaggle"], default="seed")
    parser.add_argument("--output", default="data/tickets/processed")
    args = parser.parse_args()

    if args.source == "kaggle":
        csv_candidates = list(Path("data/tickets/raw").glob("*.csv"))
        if csv_candidates:
            from data.preprocessor import Preprocessor

            tickets = Preprocessor().process_csv(str(csv_candidates[0]))
            print(f"[INFO] Processed {len(tickets)} tickets from Kaggle CSV.")
        else:
            print("[WARN] No CSV found in data/tickets/raw/. Falling back to seed.")
            tickets = load_seed()
    else:
        tickets = load_seed()

    split_and_save(tickets, Path(args.output))


if __name__ == "__main__":
    main()
