from __future__ import annotations
import argparse
import os
import sys

import httpx
from fastapi import FastAPI, Query
from openai import OpenAI
from tasks.task_easy import grade_easy as grade_easy_logic
from tasks.task_hard import grade_hard as grade_hard_logic
from tasks.task_medium import grade_medium as grade_medium_logic
from utils.config import API_BASE_URL, MODEL_NAME, HF_TOKEN, TASK_NAME, CS_ENV_URL, CS_ENV_BENCHMARK, MAX_STEPS, TEMPERATURE, VALID_CATEGORIES
from utils.logger import log_start, log_step, log_end

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "no-key")
app = FastAPI(title="Customer Support Grader API")

CLASSIFY_SYSTEM = "You are a customer support ticket classifier. Output ONLY one of these labels: billing, technical, refund, account, general"
RESPOND_SYSTEM = "You are a professional support agent. Write a helpful reply (2-4 sentences). Acknowledge issue, provide next step. Do NOT use [INSERT] or <TODO>."
DECISION_SYSTEM = "Decide if ticket should be escalated or closed. Output EXACTLY one word: escalate OR close"


def _bounded_score(value: float) -> float:
    return round(min(max(float(value), 0.01), 0.99), 4)


@app.get("/grade/task_easy")
def grade_easy(
    predicted: str = Query("general"),
    true_label: str = Query("general"),
    step_count: int = Query(1, ge=1),
) -> dict[str, float]:
    score = _bounded_score(grade_easy_logic(predicted=predicted, true_label=true_label, step_count=step_count))
    return {"score": score, "reward": score}


@app.get("/grade/task_medium")
def grade_medium(
    response: str = Query("Thank you for reaching out. We are reviewing your request and will update you shortly."),
    expected: str = Query("Thank you for reaching out. We are reviewing your request and will update you shortly."),
    step_count: int = Query(1, ge=1),
) -> dict[str, float]:
    score = _bounded_score(grade_medium_logic(response=response, expected=expected, step_count=step_count))
    return {"score": score, "reward": score}


@app.get("/grade/task_hard")
def grade_hard(
    response: str = Query("I understand your concern and have started reviewing this ticket."),
    expected: str = Query("I understand your concern and have started reviewing this ticket."),
    final_action: str = Query("close_ticket"),
    should_escalate: bool = Query(False),
    step_count: int = Query(1, ge=1),
) -> dict[str, float]:
    score = _bounded_score(
        grade_hard_logic(
            responses=[response],
            expected=expected,
            final_action=final_action,
            should_escalate=should_escalate,
            step_count=step_count,
        )
    )
    return {"score": score, "reward": score}

def _call_llm(system: str, user: str) -> str:
    response = client.chat.completions.create(model=MODEL_NAME, temperature=TEMPERATURE, max_tokens=300, messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
    return response.choices[0].message.content.strip()

def classify(ticket_text: str) -> str:
    try:
        raw = _call_llm(CLASSIFY_SYSTEM, f"Classify:\n\n{ticket_text}").strip().lower().split()[0]
        return raw if raw in VALID_CATEGORIES else "general"
    except Exception: return "general"

def respond(ticket_text: str, category: str, history: list[str]) -> str:
    try:
        history_text = "\n".join(history[-6:]) if history else "None"
        user_prompt = f"Category: {category}\nHistory:\n{history_text}\n\nMessage:\n{ticket_text}"
        return _call_llm(RESPOND_SYSTEM, user_prompt)
    except Exception: return "I apologize for the inconvenience. Our team is looking into this."

def decide_close_or_escalate(ticket_text: str, history: list[str]) -> str:
    try:
        history_text = "\n".join(history[-8:]) if history else "None"
        raw = _call_llm(DECISION_SYSTEM, f"Ticket: {ticket_text}\n\nConversation:\n{history_text}\n\nEscalate or close?").lower()
        return "escalate_ticket" if "escalate" in raw else "close_ticket"
    except Exception: return "close_ticket"

def _post(url: str, payload: dict) -> dict:
    r = httpx.post(url, json=payload, timeout=60); r.raise_for_status(); return r.json()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run CustomerSupportEnv baseline inference")
    parser.add_argument(
        "--task",
        choices=["easy", "medium", "hard"],
        default=os.getenv("TASK_NAME", TASK_NAME),
        help="Task tier to run.",
    )
    return parser.parse_args()

def run_episode(task: str) -> None:
    rewards, step_num, history = [], 0, []
    success, score, category = False, 0.0, "general"
    model_slug = MODEL_NAME.split("/")[-1]
    log_start(task=task, env=CS_ENV_BENCHMARK, model=model_slug)
    try:
        reset_resp = _post(f"{CS_ENV_URL}/reset", {"task": task})
        obs, done = reset_resp["observation"], reset_resp.get("done", False)
        while not done and step_num < MAX_STEPS:
            ticket_text, conv_history = obs["ticket_text"], obs.get("conversation_history", [])
            available_actions = obs.get("available_actions", [])
            if "classify_ticket" in available_actions:
                category = classify(ticket_text); action = {"action_type": "classify_ticket", "content": category}
            elif "respond_to_customer" in available_actions and step_num < MAX_STEPS - 2:
                reply = respond(ticket_text, category, conv_history); action = {"action_type": "respond_to_customer", "content": reply}
                history.append(f"Agent: {reply[:60]}")
            else:
                decision = decide_close_or_escalate(ticket_text, conv_history); action = {"action_type": decision}
            
            step_resp = _post(f"{CS_ENV_URL}/step", action)
            obs, reward, done = step_resp["observation"], step_resp["reward"], step_resp["done"]
            step_error = step_resp.get("info", {}).get("last_action_error")
            step_num += 1; rewards.append(reward)
            
            action_log = action["action_type"]
            if action.get("content"): action_log += f":{action['content'][:30]}"
            log_step(step=step_num, action=action_log, reward=reward, done=done, error=step_error)
        score = round(sum(rewards) / len(rewards), 4) if rewards else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score >= 0.5
    except Exception as exc:
        print(f"[ERROR] Episode failed: {exc}", file=sys.stderr)
    finally:
        log_end(success=success, steps=step_num, score=score, rewards=rewards)

if __name__ == "__main__":
    args = _parse_args()
    run_episode(args.task)
