import pytest
from unittest.mock import MagicMock
from DataValidator import DataValidator
from FormHandler import FormHandler

class TestIntegrationFormHandler:
    def setup_method(self):
        self.mock_validator = MagicMock(spec=DataValidator)
        self.handler = FormHandler(self.mock_validator)

    def test_valid_submission_flow(self):
        self.mock_validator.validate_email.return_value = True
        self.mock_validator.validate_password.return_value = True
        
        result = self.handler.submit_form("valid@test.com", "SecurePassword123")
        
        assert result["success"] is True
        self.mock_validator.validate_email.assert_called_once_with("valid@test.com")
        self.mock_validator.validate_password.assert_called_once_with("SecurePassword123")
        assert self.handler.submitted_data == {"email": "valid@test.com", "password": "SecurePassword123"}

    def test_email_validation_failure(self):
        self.mock_validator.validate_email.return_value = False
        self.mock_validator.error_messages = ["Invalid email format"]
        
        result = self.handler.submit_form("invalid-email", "GoodPass123")
        
        assert result["success"] is False
        assert "Invalid email format" in result["errors"]
        self.mock_validator.validate_password.assert_not_called()

    def test_password_validation_failure(self):
        self.mock_validator.validate_email.return_value = True
        self.mock_validator.validate_password.return_value = False
        self.mock_validator.error_messages = ["Password must be at least 8 characters"]
        
        result = self.handler.submit_form("good@email.com", "short")
        
        assert result["success"] is False
        assert "Password must be at least 8 characters" in result["errors"]

    def test_validator_exception_propagation(self):
        self.mock_validator.validate_email.side_effect = RuntimeError("Validation error")
        
        with pytest.raises(RuntimeError) as exc_info:
            self.handler.submit_form("test@error.com", "anypass")
        assert "Validation error" in str(exc_info.value)

    def test_edge_case_empty_inputs(self):
        self.mock_validator.validate_email.return_value = False
        self.mock_validator.error_messages = ["Invalid email format"]
        
        result = self.handler.submit_form("", "")
        assert "Invalid email format" in result["errors"]
        self.mock_validator.validate_email.assert_called_once_with("")

    def test_real_integration_with_validator(self):
        real_validator = DataValidator()
        handler = FormHandler(real_validator)
        
        assert handler.submit_form("user@domain.com", "ValidPass123")["success"] is True
        assert handler.submit_form("broken", "short")["success"] is False
        assert "Password must be at least 8 characters" in handler.submit_form("a@b.c", "short")["errors"]