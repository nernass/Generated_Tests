import pytest
from DataValidator import DataValidator
from FormHandler import FormHandler

@pytest.fixture
def form_setup():
    validator = DataValidator()
    form_handler = FormHandler(validator)
    return form_handler

def test_successful_form_submission(form_setup):
    result = form_setup.submit_form("test@example.com", "password123")
    assert result["success"] == True
    assert form_setup.submitted_data == {"email": "test@example.com", "password": "password123"}

def test_invalid_email_submission(form_setup):
    result = form_setup.submit_form("invalid_email", "password123")
    assert result["success"] == False
    assert "Invalid email format" in result["errors"]
    assert not form_setup.submitted_data

def test_invalid_password_submission(form_setup):
    result = form_setup.submit_form("test@example.com", "short")
    assert result["success"] == False
    assert "Password must be at least 8 characters" in result["errors"]
    assert not form_setup.submitted_data

def test_multiple_form_submissions(form_setup):
    # First submission - invalid
    result1 = form_setup.submit_form("invalid_email", "password123")
    assert result1["success"] == False
    
    # Second submission - valid
    result2 = form_setup.submit_form("test@example.com", "password123")
    assert result2["success"] == True

def test_empty_submissions(form_setup):
    result = form_setup.submit_form("", "")
    assert result["success"] == False
    assert len(result["errors"]) > 0