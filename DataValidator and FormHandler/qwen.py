import pytest

class DataValidator:
    def __init__(self):
        self.error_messages = []
        
    def validate_email(self, email):
        self.error_messages = []
        if not email or '@' not in email:
            self.error_messages.append("Invalid email format")
            return False
        return True
        
    def validate_password(self, password):
        self.error_messages = []
        if not password or len(password) < 8:
            self.error_messages.append("Password must be at least 8 characters")
            return False
        return True

class FormHandler:
    def __init__(self, validator):
        self.validator = validator
        self.submitted_data = {}
        
    def submit_form(self, email, password):
        if not self.validator.validate_email(email):
            return {"success": False, "errors": self.validator.error_messages}
            
        if not self.validator.validate_password(password):
            return {"success": False, "errors": self.validator.error_messages}
            
        self.submitted_data = {"email": email, "password": password}
        return {"success": True}

@pytest.fixture
def data_validator():
    return DataValidator()

@pytest.fixture
def form_handler(data_validator):
    return FormHandler(data_validator)

class TestIntegrationDataValidatorAndFormHandler:

    def test_success_path_valid_email_and_password(self, form_handler, data_validator):
        result = form_handler.submit_form("user@example.com", "password123")
        assert result == {"success": True}
        assert form_handler.submitted_data == {"email": "user@example.com", "password": "password123"}

    def test_partial_failure_invalid_email(self, form_handler, data_validator):
        result = form_handler.submit_form("invalid-email", "password123")
        assert result == {"success": False, "errors": ["Invalid email format"]}
        assert form_handler.submitted_data == {}

    def test_partial_failure_invalid_password(self, form_handler, data_validator):
        result = form_handler.submit_form("user@example.com", "pass")
        assert result == {"success": False, "errors": ["Password must be at least 8 characters"]}
        assert form_handler.submitted_data == {}

    def test_partial_failure_both_invalid_email_and_password(self, form_handler, data_validator):
        result = form_handler.submit_form("invalid-email", "pass")
        assert result == {"success": False, "errors": ["Invalid email format", "Password must be at least 8 characters"]}
        assert form_handler.submitted_data == {}

    def test_edge_case_empty_email(self, form_handler, data_validator):
        result = form_handler.submit_form("", "password123")
        assert result == {"success": False, "errors": ["Invalid email format"]}
        assert form_handler.submitted_data == {}

    def test_edge_case_empty_password(self, form_handler, data_validator):
        result = form_handler.submit_form("user@example.com", "")
        assert result == {"success": False, "errors": ["Password must be at least 8 characters"]}
        assert form_handler.submitted_data == {}

    def test_edge_case_short_password(self, form_handler, data_validator):
        result = form_handler.submit_form("user@example.com", "short")
        assert result == {"success": False, "errors": ["Password must be at least 8 characters"]}
        assert form_handler.submitted_data == {}

    def test_edge_case_long_email(self, form_handler, data_validator):
        long_email = "a" * 100 + "@example.com"
        result = form_handler.submit_form(long_email, "password123")
        assert result == {"success": True}
        assert form_handler.submitted_data == {"email": long_email, "password": "password123"}

    def test_edge_case_long_password(self, form_handler, data_validator):
        long_password = "a" * 100
        result = form_handler.submit_form("user@example.com", long_password)
        assert result == {"success": True}
        assert form_handler.submitted_data == {"email": "user@example.com", "password": long_password}