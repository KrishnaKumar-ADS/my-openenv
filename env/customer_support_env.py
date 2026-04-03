from __future__ import annotations
import random
from typing import Optional
from data.loader import DatasetLoader
from data.schema import TicketSchema
from env.episode import EpisodeState, EpisodeLogic
from env.models import ActionModel, ActionType, ObservationModel, StepResult, FullStateModel
from env.reward import RewardCalculator
from utils.logger import get_logger
from utils.sentiment import update_sentiment

log = get_logger(__name__)

FOLLOWUP_TEMPLATES = [
    "Thank you for your response. However, I still have not received a solution. Can you please help further?",
    "I appreciate the reply but the issue persists. What should I do next?",
    "That didn't solve my problem. My issue is still ongoing.",
    "Could you please escalate this? It's been several days.",
    "I tried what you suggested but it didn't work. Please advise.",
]

class CustomerSupportEnv:
    def __init__(self, task: str = "easy", seed: Optional[int] = None):
        self.task = task
        self.seed = seed
        self._rng = random.Random(seed)
        self._loader = DatasetLoader(task=task)
        self._reward_calc = RewardCalculator()
        self._episode_logic = EpisodeLogic()
        self._state: Optional[EpisodeState] = None

    def reset(self, task: Optional[str] = None, seed: Optional[int] = None) -> ObservationModel:
        if task:
            self.task = task
            self._loader = DatasetLoader(task=task)
        if seed is not None:
            self.seed = seed
            self._rng = random.Random(seed)
        ticket = self._load_ticket()
        self._state = EpisodeState(ticket=ticket)
        log.info(f"[RESET] task={self.task} ticket_id={ticket.ticket_id}")
        return self._build_observation()

    def step(self, action: ActionModel) -> StepResult:
        if self._state is None:
            raise RuntimeError("Call reset() before step().")
        s = self._state
        s.step_count += 1
        reward_model = self._reward_calc.compute(action, s)
        s.total_reward += reward_model.reward
        s.action_history.append(action.action_key())
        new_status = self._episode_logic.transition(s, action.action_type.value)
        s.status = new_status
        if action.action_type == ActionType.RESPOND and action.content:
            s.response_history.append(action.content)
            s.conversation_history.append(f"Agent: {action.content}")
            s.customer_satisfaction_score = update_sentiment(s.customer_satisfaction_score, action.content)

        followup_injected = False
        if self._episode_logic.should_inject_followup(s):
            followup = self._inject_customer_followup()
            s.conversation_history.append(f"Customer: {followup}")
            s.ticket = s.ticket.model_copy(update={"message": followup})
            followup_injected = True

        s.done = self._episode_logic.is_done(s)
        obs = self._build_observation()
        info = {
            "reward_components": reward_model.components,
            "step_count": s.step_count,
            "last_action_error": None,
            "followup_injected": followup_injected,
        }
        log.debug(f"[STEP] step={s.step_count} action={action.action_key()} reward={reward_model.reward} done={s.done}")
        return StepResult(observation=obs, reward=reward_model.reward, done=s.done, info=info)

    def state(self) -> FullStateModel:
        if self._state is None: raise RuntimeError("Call reset() first.")
        s = self._state
        return FullStateModel(
            ticket_id=s.ticket.ticket_id, step_count=s.step_count, status=s.status,
            action_history=s.action_history, response_history=s.response_history,
            classification=s.classification, true_category=s.ticket.category,
            expected_resolution=s.ticket.expected_resolution, should_escalate=s.ticket.should_escalate,
            customer_satisfaction_score=s.customer_satisfaction_score,
            noise_injected=s.ticket.noise_injected, total_reward=s.total_reward, done=s.done,
        )

    def _load_ticket(self) -> TicketSchema:
        tickets = self._loader.load()
        if not tickets: raise RuntimeError("No tickets loaded. Run scripts/preprocess.py first.")
        return self._rng.choice(tickets)

    def _build_observation(self) -> ObservationModel:
        s = self._state
        sentiment = _score_to_label(s.customer_satisfaction_score)
        return ObservationModel(
            ticket_text=s.ticket.message, conversation_history=list(s.conversation_history),
            last_agent_action=s.action_history[-1] if s.action_history else None,
            status=s.status, step_count=s.step_count, ticket_id=s.ticket.ticket_id,
            priority=s.ticket.priority, timestamp=s.ticket.timestamp,
            available_actions=self._episode_logic.get_available_actions(s),
            sentiment_hint=sentiment,
        )

    def _inject_customer_followup(self) -> str:
        return self._rng.choice(FOLLOWUP_TEMPLATES)

def _score_to_label(score: float) -> str:
    if score >= 0.75: return "positive"
    if score >= 0.50: return "neutral"
    if score >= 0.25: return "negative"
    return "angry"
