import pytest
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
        assert result == True
        assert email_service.get_sent_count() == 1
        assert email_service.sent_emails[0]["to"] == email
        assert email_service.sent_emails[0]["message"] == "Welcome to our service!"
        
    def test_create_duplicate_user_no_welcome_email(self, user_manager, email_service):
        # Arrange
        user_id = "user123"
        email = "test@example.com"
        user_manager.create_user(user_id, email)
        initial_email_count = email_service.get_sent_count()
        
        # Act
        result = user_manager.create_user(user_id, "another@example.com")
        
        # Assert
        assert result == False
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