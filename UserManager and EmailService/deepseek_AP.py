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
        result = self.manager.create_user("user123", "valid@test.com")
        
        assert result is True
        self.mock_email.send_welcome.assert_called_once_with("valid@test.com")
        assert "user123" in self.manager.users

    def test_duplicate_user_id_handling(self):
        self.manager.create_user("dupe", "first@test.com")
        result = self.manager.create_user("dupe", "second@test.com")
        
        assert result is False
        self.mock_email.send_welcome.assert_called_once()

    def test_email_service_failure_propagation(self):
        self.mock_email.send_welcome.side_effect = ConnectionError("Service down")
        with pytest.raises(ConnectionError) as exc_info:
            self.manager.create_user("fail_user", "error@test.com")
        assert "Service down" in str(exc_info.value)
        assert "fail_user" in self.manager.users  # User added before failure

    def test_edge_case_empty_email(self):
        self.mock_email.send_welcome.return_value = True
        self.manager.create_user("empty_email", "")
        
        self.mock_email.send_welcome.assert_called_once_with("")

    def test_real_integration_flow(self):
        real_email = EmailService()
        real_manager = UserManager(real_email)
        
        real_manager.create_user("real_user", "real@test.com")
        assert real_email.get_sent_count() == 1
        assert real_email.sent_emails[0]["to"] == "real@test.com"