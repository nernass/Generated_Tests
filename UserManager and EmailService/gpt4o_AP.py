import pytest
from unittest.mock import Mock, patch
from UserManager import UserManager
from EmailService import EmailService

class TestUserManagerEmailServiceIntegration:
    @pytest.fixture
    def email_service(self):
        return EmailService()
    
    @pytest.fixture
    def user_manager(self, email_service):
        return UserManager(email_service)
    
    def test_create_user_sends_welcome_email(self, user_manager, email_service):
        # Arrange
        user_id = "user123"
        email = "test@example.com"
        
        # Act
        result = user_manager.create_user(user_id, email)
        
        # Assert
        assert result is True
        assert email_service.get_sent_count() == 1
        assert email_service.sent_emails[0]["to"] == email
        assert email_service.sent_emails[0]["message"] == "Welcome to our service!"
    
    def test_create_duplicate_user_returns_false(self, user_manager):
        # Arrange
        user_id = "user123"
        email = "test@example.com"
        
        # Act
        first_result = user_manager.create_user(user_id, email)
        second_result = user_manager.create_user(user_id, "another@example.com")
        
        # Assert
        assert first_result is True
        assert second_result is False
    
    def test_create_duplicate_user_no_welcome_email(self, user_manager, email_service):
        # Arrange
        user_id = "user123"
        email = "test@example.com"
        user_manager.create_user(user_id, email)
        initial_email_count = email_service.get_sent_count()
        
        # Act
        user_manager.create_user(user_id, "another@example.com")
        
        # Assert
        assert email_service.get_sent_count() == initial_email_count
    
    def test_multiple_users_multiple_emails(self, user_manager, email_service):
        # Arrange
        users = [
            ("user1", "user1@example.com"),
            ("user2", "user2@example.com"),
            ("user3", "user3@example.com")
        ]
        
        # Act
        for user_id, email in users:
            user_manager.create_user(user_id, email)
        
        # Assert
        assert email_service.get_sent_count() == 3
        for i, (_, email) in enumerate(users):
            assert email_service.sent_emails[i]["to"] == email
    
    def test_email_content_verification(self, user_manager, email_service):
        # Arrange
        user_id = "user123"
        email = "test@example.com"
        
        # Act
        user_manager.create_user(user_id, email)
        
        # Assert
        sent_email = email_service.sent_emails[0]
        assert "Welcome" in sent_email["message"]
        assert sent_email["to"] == email
    
    def test_email_service_failure(self, user_manager):
        # Arrange
        user_id = "user123"
        email = "test@example.com"
        with patch.object(EmailService, 'send_welcome', return_value=False):
            email_service = EmailService()
            user_manager = UserManager(email_service)
        
            # Act
            result = user_manager.create_user(user_id, email)
        
            # Assert
            assert result is False
            assert email_service.get_sent_count() == 0
    
    def test_edge_case_empty_email(self, user_manager):
        # Arrange
        user_id = "user123"
        email = ""
        
        # Act
        result = user_manager.create_user(user_id, email)
        
        # Assert
        assert result is False
        assert user_id not in user_manager.users