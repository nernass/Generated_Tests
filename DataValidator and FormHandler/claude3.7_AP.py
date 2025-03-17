import pytest
from unittest.mock import Mock, patch, call
import sys
import os
from DataValidator import DataValidator
from FormHandler import FormHandler

# ================== FIXTURES ==================

@pytest.fixture
def validator():
    return DataValidator()

@pytest.fixture
def form_handler(validator):
    return FormHandler(validator)

@pytest.fixture
def mock_validator():
    mock = Mock(spec=DataValidator)
    # Default behavior for success path
    mock.validate_email.return_value = True
    mock.validate_password.return_value = True
    mock.error_messages = []
    return mock

@pytest.fixture
def form_handler_with_mock(mock_validator):
    return FormHandler(mock_validator)

# ================== SUCCESS PATH TESTS ==================

def test_successful_form_submission(form_handler):
    # Test end-to-end success flow
    result = form_handler.submit_form("valid@example.com", "password123")
    
    # Assertions
    assert result["success"] == True
    assert form_handler.submitted_data == {"email": "valid@example.com", "password": "password123"}

def test_successful_form_submission_with_mocks(form_handler_with_mock, mock_validator):
    # Test with mocks to verify component interactions
    result = form_handler_with_mock.submit_form("valid@example.com", "password123")
    
    # Verify interactions
    mock_validator.validate_email.assert_called_once_with("valid@example.com")
    mock_validator.validate_password.assert_called_once_with("password123")
    
    # Verify result
    assert result["success"] == True
    assert form_handler_with_mock.submitted_data == {"email": "valid@example.com", "password": "password123"}

# ================== FAILURE PATH TESTS ==================

def test_email_validation_failure(form_handler_with_mock, mock_validator):
    # Configure mock for failure
    mock_validator.validate_email.return_value = False
    mock_validator.error_messages = ["Invalid email format"]
    
    # Execute
    result = form_handler_with_mock.submit_form("invalid", "password123")
    
    # Verify
    assert result["success"] == False
    assert result["errors"] == ["Invalid email format"]
    mock_validator.validate_email.assert_called_once_with("invalid")
    # Password validation should not be called if email validation fails
    mock_validator.validate_password.assert_not_called()
    # Data should not be stored on validation failure
    assert form_handler_with_mock.submitted_data == {}

def test_password_validation_failure(form_handler_with_mock, mock_validator):
    # Configure mock for email success but password failure
    mock_validator.validate_email.return_value = True
    mock_validator.validate_password.return_value = False
    mock_validator.error_messages = ["Password must be at least 8 characters"]
    
    # Execute
    result = form_handler_with_mock.submit_form("valid@example.com", "short")
    
    # Verify
    assert result["success"] == False
    assert result["errors"] == ["Password must be at least 8 characters"]
    mock_validator.validate_email.assert_called_once_with("valid@example.com")
    mock_validator.validate_password.assert_called_once_with("short")
    assert form_handler_with_mock.submitted_data == {}

def test_validator_exception_handling(form_handler_with_mock, mock_validator):
    # Configure mock to throw exception
    mock_validator.validate_email.side_effect = Exception("Unexpected error")
    
    # Execute and verify exception propagation
    with pytest.raises(Exception) as exc_info:
        form_handler_with_mock.submit_form("valid@example.com", "password123")
    
    assert "Unexpected error" in str(exc_info.value)

# ================== EDGE CASE TESTS ==================

def test_empty_inputs(form_handler):
    result = form_handler.submit_form("", "")
    
    assert result["success"] == False
    assert "Invalid email format" in result["errors"]
    assert form_handler.submitted_data == {}

def test_boundary_password_length(form_handler):
    # Test exactly 8 characters (boundary value)
    result1 = form_handler.submit_form("valid@example.com", "12345678")
    assert result1["success"] == True
    
    # Test 7 characters (just below boundary)
    result2 = form_handler.submit_form("valid@example.com", "1234567")
    assert result2["success"] == False
    assert "Password must be at least 8 characters" in result2["errors"]

def test_extremely_long_inputs(form_handler):
    # Test with very long but valid inputs
    long_email = "a" * 1000 + "@example.com"
    long_password = "p" * 10000
    
    result = form_handler.submit_form(long_email, long_password)
    assert result["success"] == True
    assert form_handler.submitted_data["email"] == long_email
    assert form_handler.submitted_data["password"] == long_password

# ================== INTEGRATION FLOW TESTS ==================

def test_validation_error_message_reset(form_handler):
    # First submission - email error
    result1 = form_handler.submit_form("invalid", "password123")
    assert "Invalid email format" in result1["errors"]
    
    # Second submission - password error
    result2 = form_handler.submit_form("valid@example.com", "short")
    assert "Password must be at least 8 characters" in result2["errors"]
    # Previous error message should not persist
    assert "Invalid email format" not in result2["errors"]

def test_multiple_validation_errors(form_handler_with_mock, mock_validator):
    # Setup mock to simulate both validations failing with different errors
    mock_validator.validate_email.return_value = False
    mock_validator.validate_password.return_value = False
    
    # First simulate email validation failing
    mock_validator.error_messages = ["Invalid email format"]
    
    result = form_handler_with_mock.submit_form("invalid", "short")
    
    # Verify form handler stops at first validation failure
    assert result["success"] == False
    assert result["errors"] == ["Invalid email format"]
    mock_validator.validate_email.assert_called_once()
    mock_validator.validate_password.assert_not_called()