import pytest
from unittest.mock import MagicMock
from UserManager import UserManager
from EmailService import EmailService

class TestIntegrationUserManager:
    def setup_method(self):
        self.mock_email = MagicMock(spec=EmailService)
        self.manager = UserManager(self.mock_email)

    def test_successful_user_creation(self):
        self.mock_email.send_welcome.return_value = True
        result = self.manager.create_user("u1", "user@test.com")
        
        assert result is True
        self.mock_email.send_welcome.assert_called_once_with("user@test.com")
        assert "u1" in self.manager.users

    def test_duplicate_user_handling(self):
        self.manager.create_user("u2", "existing@test.com")
        result = self.manager.create_user("u2", "new@test.com")
        
        assert result is False
        assert self.mock_email.send_welcome.call_count == 1  # Only first call happened

    def test_email_failure_propagation(self):
        self.mock_email.send_welcome.side_effect = ConnectionError("SMTP down")
        with pytest.raises(ConnectionError) as exc_info:
            self.manager.create_user("u3", "error@test.com")
        assert "SMTP down" in str(exc_info.value)
        assert "u3" not in self.manager.users

    def test_real_email_integration(self):
        real_email = EmailService()
        real_manager = UserManager(real_email)
        
        real_manager.create_user("real1", "real@test.com")
        assert real_email.get_sent_count() == 1
        assert real_email.sent_emails[0]["to"] == "real@test.com"