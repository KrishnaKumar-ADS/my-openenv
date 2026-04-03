from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN", "")
TEMPERATURE  = float(os.getenv("TEMPERATURE", "0.3"))
TASK_NAME    = os.getenv("TASK_NAME", "easy")
CS_ENV_URL   = os.getenv("CS_ENV_URL", "http://localhost:7860")
CS_ENV_BENCHMARK = os.getenv("CS_ENV_BENCHMARK", "customer_support_env")
MAX_STEPS    = int(os.getenv("MAX_STEPS", "10"))

VALID_CATEGORIES = ["billing", "technical", "refund", "account", "general"]
VALID_PRIORITIES = ["low", "medium", "high", "urgent"]
VALID_SENTIMENTS = ["positive", "neutral", "negative", "angry"]
