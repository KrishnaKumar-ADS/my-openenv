from __future__ import annotations
import threading
from typing import Dict, Optional
from env.customer_support_env import CustomerSupportEnv

class SessionManager:
    _instance: Optional["SessionManager"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "SessionManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._sessions: Dict[str, CustomerSupportEnv] = {}
                cls._instance._session_lock = threading.Lock()
        return cls._instance

    def get_or_create(self, session_id: str, task: str = "easy", seed: Optional[int] = None) -> CustomerSupportEnv:
        with self._session_lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = CustomerSupportEnv(task=task, seed=seed)
            return self._sessions[session_id]

    def create(self, session_id: str, task: str = "easy", seed: Optional[int] = None) -> CustomerSupportEnv:
        env = CustomerSupportEnv(task=task, seed=seed)
        with self._session_lock:
            self._sessions[session_id] = env
        return env

    def get(self, session_id: str) -> Optional[CustomerSupportEnv]:
        with self._session_lock: return self._sessions.get(session_id)

    def delete(self, session_id: str) -> None:
        with self._session_lock: self._sessions.pop(session_id, None)

session_manager = SessionManager()
