import pytest
from unittest.mock import Mock, patch
import logging
from DataValidator import DataValidator
from FormHandler import FormHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_validator():
    mock = Mock(spec=DataValidator)
    mock.validate_email.return_value = True
    mock.validate_password.return_value = True
    mock.error_messages = []
    return mock

@pytest.fixture
def real_validator():
    return DataValidator()

@pytest.fixture
def form_handler_with_mock(mock_validator):
    return FormHandler(mock_validator)

@pytest.fixture
def form_handler_with_real(real_validator):
    return FormHandler(real_validator)

class TestHappyPath:
    def test_successful_submission(self, form_handler_with_real):
        result = form_handler_with_real.submit_form("test@example.com", "validpass123")
        
        assert result["success"] == True
        assert form_handler_with_real.submitted_data == {
            "email": "test@example.com",
            "password": "validpass123"
        }

    def test_component_interaction(self, form_handler_with_mock, mock_validator):
        form_handler_with_mock.submit_form("test@example.com", "validpass123")
        
        mock_validator.validate_email.assert_called_once_with("test@example.com")
        mock_validator.validate_password.assert_called_once_with("validpass123")

class TestFailurePath:
    def test_validator_email_failure(self, form_handler_with_mock, mock_validator):
        mock_validator.validate_email.return_value = False
        mock_validator.error_messages = ["Invalid email format"]
        
        result = form_handler_with_mock.submit_form("invalid", "validpass123")
        
        assert result["success"] == False
        assert result["errors"] == ["Invalid email format"]
        assert form_handler_with_mock.submitted_data == {}

    def test_validator_password_failure(self, form_handler_with_mock, mock_validator):
        mock_validator.validate_email.return_value = True
        mock_validator.validate_password.return_value = False
        mock_validator.error_messages = ["Password must be at least 8 characters"]
        
        result = form_handler_with_mock.submit_form("test@example.com", "short")
        
        assert result["success"] == False
        assert result["errors"] == ["Password must be at least 8 characters"]
        assert form_handler_with_mock.submitted_data == {}

    def test_exception_handling(self, form_handler_with_mock, mock_validator):
        mock_validator.validate_email.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception) as exc_info:
            form_handler_with_mock.submit_form("test@example.com", "validpass123")
        
        assert str(exc_info.value) == "Unexpected error"

class TestEdgeCases:
    def test_empty_inputs(self, form_handler_with_real):
        result = form_handler_with_real.submit_form("", "")
        
        assert result["success"] == False
        assert "Invalid email format" in result["errors"]
        assert form_handler_with_real.submitted_data == {}

    def test_boundary_values(self, form_handler_with_real):
        # Test minimum valid password length
        result = form_handler_with_real.submit_form("test@example.com", "12345678")
        assert result["success"] == True

        # Test password just below minimum length
        result = form_handler_with_real.submit_form("test@example.com", "1234567")
        assert result["success"] == False

    def test_extremely_long_inputs(self, form_handler_with_real):
        long_email = "a" * 1000 + "@example.com"
        long_password = "p" * 10000
        
        result = form_handler_with_real.submit_form(long_email, long_password)
        assert result["success"] == True

class TestDataFlow:
    def test_error_message_reset(self, form_handler_with_real):
        # First submission with invalid email
        result1 = form_handler_with_real.submit_form("invalid", "validpass123")
        assert "Invalid email format" in result1["errors"]
        
        # Second submission with invalid password
        result2 = form_handler_with_real.submit_form("valid@example.com", "short")
        assert "Password must be at least 8 characters" in result2["errors"]
        assert "Invalid email format" not in result2["errors"]

    def test_submitted_data_consistency(self, form_handler_with_real):
        # Initial submission
        form_handler_with_real.submit_form("test1@example.com", "password123")
        assert form_handler_with_real.submitted_data["email"] == "test1@example.com"
        
        # Subsequent submission
        form_handler_with_real.submit_form("test2@example.com", "password456")
        assert form_handler_with_real.submitted_data["email"] == "test2@example.com"