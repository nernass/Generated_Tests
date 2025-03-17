import pytest
from unittest.mock import Mock, patch
from UserManager import UserManager
from EmailService import EmailService

class TestUserManagerEmailServiceIntegration:
    @pytest.fixture
    def mock_email_service(self):
        service = Mock(spec=EmailService)
        service.send_welcome.return_value = True
        service.get_sent_count.return_value = 0
        service.sent_emails = []
        return service

    @pytest.fixture
    def user_manager(self, mock_email_service):
        return UserManager(mock_email_service)

    def test_successful_user_creation(self, user_manager, mock_email_service):
        # Arrange
        user_id = "user123"
        email = "test@example.com"

        # Act
        result = user_manager.create_user(user_id, email)

        # Assert
        assert result is True
        mock_email_service.send_welcome.assert_called_once_with(email)
        assert user_id in user_manager.users
        assert user_manager.users[user_id]["email"] == email

    def test_email_service_failure(self, mock_email_service):
        # Arrange
        mock_email_service.send_welcome.return_value = False
        user_manager = UserManager(mock_email_service)
        user_id = "user123"
        email = "test@example.com"

        # Act
        result = user_manager.create_user(user_id, email)

        # Assert
        assert result is True  # User is still created even if email fails
        mock_email_service.send_welcome.assert_called_once_with(email)

    def test_duplicate_user_creation(self, user_manager, mock_email_service):
        # Arrange
        user_id = "user123"
        email1 = "test1@example.com"
        email2 = "test2@example.com"

        # Act
        first_result = user_manager.create_user(user_id, email1)
        second_result = user_manager.create_user(user_id, email2)

        # Assert
        assert first_result is True
        assert second_result is False
        mock_email_service.send_welcome.assert_called_once_with(email1)

    def test_edge_cases(self, user_manager, mock_email_service):
        # Empty strings
        assert user_manager.create_user("", "") is True
        mock_email_service.send_welcome.assert_called_with("")

        # Long inputs
        long_id = "a" * 1000
        long_email = "a" * 1000 + "@example.com"
        assert user_manager.create_user(long_id, long_email) is True
        mock_email_service.send_welcome.assert_called_with(long_email)

    def test_real_integration(self):
        # Real integration test without mocks
        email_service = EmailService()
        user_manager = UserManager(email_service)
        
        # Test full workflow
        user_id = "test_user"
        email = "real@example.com"
        
        result = user_manager.create_user(user_id, email)
        
        assert result is True
        assert email_service.get_sent_count() == 1
        assert email_service.sent_emails[0]["to"] == email
        assert email_service.sent_emails[0]["message"] == "Welcome to our service!"
        assert user_manager.users[user_id]["email"] == email