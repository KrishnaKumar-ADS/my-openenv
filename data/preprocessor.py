from __future__ import annotations
import re, uuid
from datetime import datetime
from typing import List, Optional
import pandas as pd
from data.schema import TicketSchema

CATEGORY_KEYWORDS = {
    "billing":   ["bill", "charge", "payment", "invoice", "subscription", "fee", "price", "cost", "refund", "credit"],
    "technical": ["error", "bug", "crash", "broken", "not working", "issue", "problem", "fail", "down", "outage"],
    "refund":    ["refund", "return", "money back", "cancel", "reimburs", "chargeback"],
    "account":   ["login", "password", "account", "sign in", "access", "locked", "username", "email", "profile"],
    "general":   [],
}

SENTIMENT_KEYWORDS = {
    "angry":    ["furious", "outrageous", "unacceptable", "terrible", "worst", "disgusting", "angry", "hate"],
    "negative": ["frustrated", "disappointed", "unhappy", "bad", "upset", "annoyed", "poor"],
    "positive": ["great", "excellent", "love", "amazing", "fantastic", "happy", "wonderful", "good"],
    "neutral":  [],
}

PRIORITY_MAP = {
    ("angry", "technical"): "urgent",
    ("angry", "billing"):   "high",
    ("negative", "technical"): "high",
    ("negative", "billing"):   "medium",
}

class Preprocessor:
    def process_csv(self, csv_path: str) -> List[TicketSchema]:
        df = pd.read_csv(csv_path, low_memory=False)
        df = self._clean(df)
        tickets: List[TicketSchema] = []
        for _, row in df.iterrows():
            t = self._row_to_ticket(row)
            if t: tickets.append(t)
        return tickets

    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        text_col = self._detect_text_col(df)
        df = df.dropna(subset=[text_col])
        df = df.drop_duplicates(subset=[text_col])
        df[text_col] = df[text_col].str.strip()
        return df

    def _detect_text_col(self, df: pd.DataFrame) -> str:
        for col in ["text", "tweet", "message", "body", "content", "Text"]:
            if col in df.columns: return col
        return df.columns[0]

    def _row_to_ticket(self, row) -> Optional[TicketSchema]:
        text_col = next((c for c in ["text", "tweet", "message", "body", "Text"] if c in row.index), row.index[0])
        message = str(row[text_col]).strip()
        if len(message) < 10: return None
        category = self._infer_category(message)
        sentiment = self._infer_sentiment(message)
        priority = PRIORITY_MAP.get((sentiment, category), "medium")
        resolution = self._generate_resolution(category, sentiment)
        should_escalate = sentiment == "angry" and category == "technical"
        return TicketSchema(
            ticket_id=str(uuid.uuid4()), message=message, category=category, priority=priority,
            sentiment=sentiment, conversation_history=[], expected_resolution=resolution,
            should_escalate=should_escalate, noise_injected=False, difficulty="easy",
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

    def _infer_category(self, text: str) -> str:
        lower = text.lower()
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in lower for kw in keywords): return cat
        return "general"

    def _infer_sentiment(self, text: str) -> str:
        lower = text.lower()
        for sentiment, keywords in SENTIMENT_KEYWORDS.items():
            if any(kw in lower for kw in keywords): return sentiment
        return "neutral"

    def _generate_resolution(self, category: str, sentiment: str) -> str:
        templates = {
            "billing": "We apologize for the billing issue. Please allow 3-5 business days for the adjustment.",
            "technical": "We're sorry for the technical inconvenience. Our team is working on a fix. Please try clearing cache.",
            "refund": "We have processed your refund request. You should see the credit within 5-7 business days.",
            "account": "We have reset your account credentials. Please check your email for the reset link.",
            "general": "Thank you for reaching out. A specialist will follow up within 24 hours.",
        }
        return templates.get(category, templates["general"])
