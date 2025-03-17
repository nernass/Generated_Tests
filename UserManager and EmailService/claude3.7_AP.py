import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from UserManager import UserManager
from EmailService import EmailService

class TestUserManagerEmailServiceIntegration:
    @pytest.fixture
    def mock_email_service(self):
        mock_service = Mock(spec=EmailService)
        mock_service.send_welcome.return_value = True
        mock_service.get_sent_count.return_value = 0
        mock_service.sent_emails = []
        return mock_service
    
    @pytest.fixture
    def real_email_service(self):
        return EmailService()
    
    @pytest.fixture
    def user_manager_with_mock(self, mock_email_service):
        return UserManager(mock_email_service)
    
    @pytest.fixture
    def user_manager_with_real(self, real_email_service):
        return UserManager(real_email_service)
    
    # Success path: normal flow with both real components
    def test_end_to_end_success(self, user_manager_with_real, real_email_service):
        # Arrange
        user_id = "test_user1"
        email = "user1@example.com"
        
        # Act
        result = user_manager_with_real.create_user(user_id, email)
        
        # Assert
        assert result is True
        assert user_id in user_manager_with_real.users
        assert user_manager_with_real.users[user_id]["email"] == email
        assert real_email_service.get_sent_count() == 1
        assert real_email_service.sent_emails[0]["to"] == email
        assert real_email_service.sent_emails[0]["message"] == "Welcome to our service!"
    
    # Success path: using mocks to verify interactions
    def test_user_creation_calls_email_service(self, user_manager_with_mock, mock_email_service):
        # Arrange
        user_id = "test_user2"
        email = "user2@example.com"
        
        # Act
        result = user_manager_with_mock.create_user(user_id, email)
        
        # Assert
        assert result is True
        mock_email_service.send_welcome.assert_called_once_with(email)
    
    # Failure path: email service fails
    def test_email_service_failure(self):
        # Arrange
        mock_service = Mock(spec=EmailService)
        mock_service.send_welcome.return_value = False  # Simulate failure
        user_manager = UserManager(mock_service)
        
        user_id = "test_user3"
        email = "user3@example.com"
        
        # Act
        result = user_manager.create_user(user_id, email)
        
        # Assert
        assert result is True  # User still created even if email fails
        assert user_id in user_manager.users
        mock_service.send_welcome.assert_called_once_with(email)
    
    # Failure path: email service throws exception
    def test_email_service_exception(self):
        # Arrange
        mock_service = Mock(spec=EmailService)
        mock_service.send_welcome.side_effect = Exception("Email service down")
        user_manager = UserManager(mock_service)
        
        user_id = "test_user4"
        email = "user4@example.com"
        
        # Act & Assert
        with pytest.raises(Exception, match="Email service down"):
            user_manager.create_user(user_id, email)
    
    # Edge case: duplicate user
    def test_duplicate_user(self, user_manager_with_real, real_email_service):
        # Arrange
        user_id = "test_user5"
        email1 = "user5.a@example.com"
        email2 = "user5.b@example.com"
        
        # Act
        first_result = user_manager_with_real.create_user(user_id, email1)
        initial_email_count = real_email_service.get_sent_count()
        second_result = user_manager_with_real.create_user(user_id, email2)
        
        # Assert
        assert first_result is True
        assert second_result is False
        assert real_email_service.get_sent_count() == initial_email_count
        assert user_manager_with_real.users[user_id]["email"] == email1  # Original email unchanged
    
    # Edge case: empty values
    def test_empty_values(self, user_manager_with_real, real_email_service):
        # Arrange
        empty_user_id = ""
        empty_email = ""
        
        # Act
        result = user_manager_with_real.create_user(empty_user_id, empty_email)
        
        # Assert
        assert result is True
        assert empty_user_id in user_manager_with_real.users
        assert real_email_service.get_sent_count() == 1
        assert real_email_service.sent_emails[0]["to"] == empty_email
    
    # Edge case: very long values
    def test_long_values(self, user_manager_with_real, real_email_service):
        # Arrange
        long_user_id = "x" * 1000
        long_email = "y" * 500 + "@example.com"
        
        # Act
        result = user_manager_with_real.create_user(long_user_id, long_email)
        
        # Assert
        assert result is True
        assert long_user_id in user_manager_with_real.users
        assert user_manager_with_real.users[long_user_id]["email"] == long_email
        assert real_email_service.get_sent_count() == 1
        assert real_email_service.sent_emails[0]["to"] == long_email
    
    # Data flow accuracy: ensure email service receives correct email
    def test_data_flow_accuracy(self):
        # Arrange
        mock_service = MagicMock(spec=EmailService)
        user_manager = UserManager(mock_service)
        user_id = "test_user6"
        email = "user6@example.com"
        
        # Act
        user_manager.create_user(user_id, email)
        
        # Assert - capture what was passed to email service
        mock_service.send_welcome.assert_called_once_with(email)