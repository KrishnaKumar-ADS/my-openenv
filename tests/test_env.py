import pytest
from env.customer_support_env import CustomerSupportEnv
from env.models import ActionModel, ActionType

@pytest.fixture
def env(): return CustomerSupportEnv(task="easy", seed=42)

def test_reset_returns_observation(env):
    obs = env.reset()
    assert obs.ticket_text and obs.status == "open" and obs.step_count == 0
    assert "classify_ticket" in obs.available_actions

def test_step_classify(env):
    env.reset()
    action = ActionModel(action_type=ActionType.CLASSIFY, content="billing")
    result = env.step(action)
    assert 0.0 <= result.reward <= 1.0 and result.observation.step_count == 1

def test_done_after_close(env):
    env.reset()
    env.step(ActionModel(action_type=ActionType.CLASSIFY, content="general"))
    env.step(ActionModel(action_type=ActionType.RESPOND, content="Thank you for reaching out. We will resolve this shortly."))
    result = env.step(ActionModel(action_type=ActionType.CLOSE))
    assert result.done is True
