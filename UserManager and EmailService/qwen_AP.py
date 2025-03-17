import pytest
from unittest.mock import MagicMock

class UserManager:
    def __init__(self, email_service):
        self.users = {}
        self.email_service = email_service

    def create_user(self, user_id, email):
        if user_id in self.users:
            return False
        self.users[user_id] = {"email": email}
        self.email_service.send_welcome(email)
        return True

class EmailService:
    def __init__(self):
        self.sent_emails = []

    def send_welcome(self, email):
        message = f"Welcome to our service!"
        self.sent_emails.append({"to": email, "message": message})
        return True

    def get_sent_count(self):
        return len(self.sent_emails)

@pytest.fixture
def email_service():
    return EmailService()

@pytest.fixture
def user_manager(email_service):
    return UserManager(email_service)

class TestIntegrationUserManagerAndEmailService:

    def test_success_path_create_user_and_send_welcome_email(self, user_manager, email_service):
        result = user_manager.create_user("user1", "user1@example.com")
        assert result == True
        assert user_manager.users["user1"]["email"] == "user1@example.com"
        assert email_service.get_sent_count() == 1
        assert email_service.sent_emails[0] == {"to": "user1@example.com", "message": "Welcome to our service!"}

    def test_partial_failure_email_service_fails_on_send_welcome(self, user_manager, email_service):
        email_service.send_welcome = MagicMock(side_effect=Exception("Email sending failed"))
        with pytest.raises(Exception) as excinfo:
            user_manager.create_user("user1", "user1@example.com")
        assert str(excinfo.value) == "Email sending failed"
        assert "user1" not in user_manager.users
        assert email_service.get_sent_count() == 0

    def test_edge_case_create_existing_user(self, user_manager, email_service):
        user_manager.create_user("user1", "user1@example.com")
        result = user_manager.create_user("user1", "user1@example.com")
        assert result == False
        assert email_service.get_sent_count() == 1

    def test_edge_case_create_user_with_empty_email(self, user_manager, email_service):
        result = user_manager.create_user("user1", "")
        assert result == True
        assert user_manager.users["user1"]["email"] == ""
        assert email_service.get_sent_count() == 1
        assert email_service.sent_emails[0] == {"to": "", "message": "Welcome to our service!"}

    def test_edge_case_create_user_with_invalid_email_format(self, user_manager, email_service):
        result = user_manager.create_user("user1", "invalid-email")
        assert result == True
        assert user_manager.users["user1"]["email"] == "invalid-email"
        assert email_service.get_sent_count() == 1
        assert email_service.sent_emails[0] == {"to": "invalid-email", "message": "Welcome to our service!"}