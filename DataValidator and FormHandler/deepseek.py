import pytest
from unittest.mock import MagicMock
from DataValidator import DataValidator
from FormHandler import FormHandler

class TestIntegrationFormHandler:
    def setup_method(self):
        self.mock_validator = MagicMock(spec=DataValidator)
        self.handler = FormHandler(self.mock_validator)

    def test_valid_form_submission(self):
        self.mock_validator.validate_email.return_value = True
        self.mock_validator.validate_password.return_value = True
        
        result = self.handler.submit_form("test@valid.com", "SecurePass123")
        
        assert result["success"] is True
        assert self.handler.submitted_data == {"email": "test@valid.com", "password": "SecurePass123"}

    def test_invalid_email_handling(self):
        self.mock_validator.validate_email.return_value = False
        self.mock_validator.error_messages = ["Invalid email format"]
        
        result = self.handler.submit_form("invalid-email", "Password123")
        
        assert result["success"] is False
        assert "Invalid email format" in result["errors"]

    def test_invalid_password_handling(self):
        self.mock_validator.validate_email.return_value = True
        self.mock_validator.validate_password.return_value = False
        self.mock_validator.error_messages = ["Password must be at least 8 characters"]
        
        result = self.handler.submit_form("valid@email.com", "short")
        
        assert result["success"] is False
        assert "Password must be at least 8 characters" in result["errors"]

    def test_validator_exception_propagation(self):
        self.mock_validator.validate_email.side_effect = Exception("Validation crash")
        
        with pytest.raises(Exception) as exc_info:
            self.handler.submit_form("test@error.com", "anypass")
        assert "Validation crash" in str(exc_info.value)

    def test_edge_case_empty_fields(self):
        self.mock_validator.validate_email.return_value = False
        self.mock_validator.error_messages = ["Invalid email format"]
        
        result = self.handler.submit_form("", "")
        assert "Invalid email format" in result["errors"]

    def test_real_integration_flow(self):
        real_validator = DataValidator()
        handler = FormHandler(real_validator)
        
        assert handler.submit_form("user@domain.com", "ValidPass123")["success"] is True
        assert handler.submit_form("bad-email", "short")["success"] is False