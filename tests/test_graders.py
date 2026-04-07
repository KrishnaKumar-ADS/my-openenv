import pytest
from env.graders import EasyGrader, MediumGrader, HardGrader

def test_easy_exact_match(): assert EasyGrader().grade("billing", "billing", 1) == 1.0
def test_easy_wrong(): assert EasyGrader().grade("technical", "billing", 1) == 0.0
def test_medium_good_response():
    response = "I sincerely apologize for the billing discrepancy. Please allow 3-5 days for our team to review and issue a correction."
    expected = "Apologize and indicate resolution timeline for the billing issue."
    assert MediumGrader().grade(response, expected, 2) > 0.3
def test_hard_correct_close():
    responses = ["We are sorry. Our team is looking into this."]
    assert HardGrader().grade(responses, "Resolve the issue.", "close_ticket", False, 4) > 0.5
