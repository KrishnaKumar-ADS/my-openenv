import pytest
from env.reward import RewardCalculator
from env.models import ActionModel, ActionType

@pytest.fixture
def calc(): return RewardCalculator()

def test_correct_classification(calc): assert calc.classification_reward("billing", "billing") == 0.5
def test_wrong_classification(calc): assert calc.classification_reward("technical", "billing") == -0.3
def test_adjacent_classification(calc): assert calc.classification_reward("refund", "billing") == 0.15

def test_good_response(calc):
    response = "I'm sorry to hear about this issue. Please contact our billing team at support@example.com and we will resolve it."
    expected = "Apologize and provide billing contact details."
    assert calc.response_quality_reward(response, expected) > 0.0

def test_short_response_penalized(calc): assert calc.response_quality_reward("ok", "Please resolve the billing issue.") <= 0.0
def test_correct_resolution_close(calc): assert calc.resolution_reward(ActionType.CLOSE, should_escalate=False) == 1.0
def test_wrong_resolution(calc): assert calc.resolution_reward(ActionType.ESCALATE, should_escalate=False) == -1.0
def test_normalize(calc): assert calc.normalize(-999) == 0.0 and calc.normalize(999) == 1.0
def test_loop_penalty(calc):
    assert calc.loop_penalty(["classify_ticket:billing"], "classify_ticket:billing") == -1.0
    assert calc.loop_penalty(["classify_ticket:billing"], "respond_to_customer:Hello") == 0.0
